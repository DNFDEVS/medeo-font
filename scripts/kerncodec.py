"""Lossless re-encoding of a font's kerning lookup: glyph-pair records become classes plus exceptions.

Medeo Sans spaces accented and twin letters like their base letters, so most explicit glyph pairs repeat the pair of
their base letters; as classes plus exceptions the kerning takes about a third of the bytes, every pair value
unchanged.

recode_static(font) re-encodes the kerning of a static font, compiles the result and checks every glyph pair of the
kerning against the original values (scripts/static_instances.py, scripts/display_statics.py).

recode_variable(font, path) evaluates the kerning at every master (corner) of the design space, clusters the
per-master value tuples, and writes class and exception values as variation deltas appended to the font's own GDEF
item variation store (existing regions, mark and anchor variations are left as they were)
(scripts/variable_kerning.py).
"""
import collections
import io
import itertools

import numpy as np
from fontTools.otlLib import builder as B
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.varLib import builder as VB
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.varLib.models import VariationModel, normalizeValue


def _xadv(v):
    return (getattr(v, "XAdvance", 0) or 0) if v is not None else 0


def find_kern_lookup(font):
    """Index of the pair-positioning lookup that holds the bulk of the kerning (most pair records)."""
    gpos = font["GPOS"].table
    kern = [r for r in gpos.FeatureList.FeatureRecord if r.FeatureTag == "kern"]
    cand = sorted({i for r in kern for i in r.Feature.LookupListIndex})
    best, best_n = None, -1
    for i in cand:
        lk = gpos.LookupList.Lookup[i]
        subs = [(s.ExtSubTable if lk.LookupType == 9 else s) for s in lk.SubTable]
        if not subs or any(getattr(s, "LookupType", 2) != 2 and lk.LookupType == 9 for s in subs):
            continue
        if lk.LookupType not in (2, 9):
            continue
        n = 0
        for s in subs:
            n += sum(len(p.PairValueRecord) for p in s.PairSet) if s.Format == 1 else s.Class1Count * s.Class2Count
        if n > best_n:
            best, best_n = i, n
    if best is None:
        raise ValueError("no kern pair lookup")
    return best


class Kern:
    """Effective advance adjustment of one pair-positioning lookup: first matching subtable wins."""

    def __init__(self, font, lookup):
        self.font = font
        lk = font["GPOS"].table.LookupList.Lookup[lookup]
        subs = [(s.ExtSubTable if lk.LookupType == 9 else s) for s in lk.SubTable]
        self.subs = []
        for s in subs:
            if s.Format == 1:
                d = {}
                for g, ps in zip(s.Coverage.glyphs, s.PairSet):
                    d[g] = {r.SecondGlyph: _xadv(r.Value1) for r in ps.PairValueRecord}
                self.subs.append((1, d))
            else:
                self.subs.append((2, (set(s.Coverage.glyphs), dict(s.ClassDef1.classDefs), dict(s.ClassDef2.classDefs),
                                      s.Class1Record)))

    def universe(self):
        first, second = set(), set()
        for kind, d in self.subs:
            if kind == 1:
                first |= set(d)
                for r in d.values():
                    second.update(r)
            else:
                first |= d[0]
                second |= set(d[2])
        order = {g: i for i, g in enumerate(self.font.getGlyphOrder())}
        return sorted(first, key=order.get), sorted(second, key=order.get)

    def get(self, a, b):
        for kind, d in self.subs:
            if kind == 1:
                r = d.get(a)
                if r is not None and b in r:
                    return r[b]
            else:
                cov, c1, c2, recs = d
                if a in cov:
                    return _xadv(recs[c1.get(a, 0)].Class2Record[c2.get(b, 0)].Value1)
        return 0


def cluster(E, cexc=4.0, rounds=3):
    """Greedy lossless merge of identical-ish rows and columns of the id matrix E.

    A row (or column) joins a larger one when the bytes saved (one row of class cells) exceed the bytes of the
    exceptions it then needs.  Returns (class of every row, class of every column, class matrix of ids).
    """
    E = np.asarray(E, dtype=np.int64)
    rowU, invL = np.unique(E, axis=0, return_inverse=True)
    colU, invR = np.unique(E.T, axis=0, return_inverse=True)
    invL, invR = invL.ravel(), invR.ravel()
    rowrep = [int(np.where(invL == i)[0][0]) for i in range(rowU.shape[0])]
    colrep = [int(np.where(invR == j)[0][0]) for j in range(colU.shape[0])]
    M = E[np.ix_(rowrep, colrep)]
    wL = np.bincount(invL).astype(np.float64)
    wR = np.bincount(invR).astype(np.float64)
    clL, clR = invL.copy(), invR.copy()

    def merge(M, wA, wB, cl):
        n = M.shape[0]
        alive = list(range(n))
        wA = wA.copy()
        members = {i: [i] for i in range(n)}
        saved = M.shape[1] * 2.0
        while len(alive) > 1:
            idx = np.array(alive)
            X = M[idx]
            k = len(idx)
            D = np.empty((k, k))
            for a in range(k):
                D[a] = ((X != X[a]) * wB).sum(axis=1)
            w = wA[idx]
            gain = saved - np.minimum(w[:, None], w[None, :]) * D * cexc
            np.fill_diagonal(gain, -1e18)
            a, b = np.unravel_index(np.argmax(gain), gain.shape)
            if gain[a, b] <= 0:
                break
            i, j = int(idx[a]), int(idx[b])
            if wA[i] > wA[j]:
                i, j = j, i
            wA[j] += wA[i]
            wA[i] = 0
            for m in members[i]:
                cl[cl == m] = j
            members[j] += members[i]
            alive.remove(i)
        keep = np.array(alive)
        remap = {int(k): n_ for n_, k in enumerate(keep)}
        return M[keep], wA[keep], np.array([remap[int(c)] for c in cl])

    for _ in range(rounds):
        before = M.shape
        M, wL, clL = merge(M, wL, wR, clL)
        Mt, wR, clR = merge(M.T, wR, wL, clR)
        M = Mt.T
        if M.shape == before:
            break
    return clL, clR, M


def build_matrix(K, tuples_of):
    """Id matrix of per-pair value tuples.  tuples_of(a, b) -> tuple of values (one per master)."""
    L, R = K[0].universe()
    for k in K[1:]:
        l2, r2 = k.universe()
        L = sorted(set(L) | set(l2), key=K[0].font.getGlyphOrder().index)
        R = sorted(set(R) | set(r2), key=K[0].font.getGlyphOrder().index)
    ids, E = {}, []
    for a in L:
        E.append([ids.setdefault(tuples_of(a, b), len(ids)) for b in R])
    T = [None] * len(ids)
    for t, i in ids.items():
        T[i] = t
    return L, R, E, T


def build_subtables(font, L, R, E, T, clL, clR, M, make_vr):
    gmap = font.getReverseGlyphMap()
    Lc, Rc = collections.defaultdict(list), collections.defaultdict(list)
    for g, c in zip(L, clL):
        Lc[int(c)].append(g)
    for g, c in zip(R, clR):
        Rc[int(c)].append(g)
    exc = {}
    for i, a in enumerate(L):
        row, mrow = E[i], M[clL[i]]
        for j, b in enumerate(R):
            if row[j] != mrow[clR[j]]:
                exc[(a, b)] = make_vr(row[j])
    sub1 = B.buildPairPosGlyphs({k: (v, None) for k, v in exc.items()}, gmap) if exc else []
    cp = {}
    for ci, gs in Lc.items():
        for cj, hs in Rc.items():
            i = M[ci][cj]
            if any(T[i]):
                cp[(tuple(sorted(gs, key=gmap.get)), tuple(sorted(hs, key=gmap.get)))] = (make_vr(i), None)
    sub2 = B.buildPairPosClassesSubtable(cp, gmap)
    return sub1 + [sub2], len(exc), (len(Lc), len(Rc))


def _install(font, lookup, subtables):
    lk = font["GPOS"].table.LookupList.Lookup[lookup]
    lk.SubTable = subtables
    lk.SubTableCount = len(subtables)
    lk.LookupType = 2


def recode_static(font):
    """Replace the kerning lookup of a static font; every pair value is checked afterwards. Returns a stats dict."""
    li = find_kern_lookup(font)
    K = Kern(font, li)
    L, R = K.universe()
    for a in L:                          # glyphs outside R must be unkerned, or the class-0 column would be lost
        assert K.get(a, ".none.") == 0, a
    L, R, E, T = build_matrix([K], lambda a, b: (K.get(a, b),))
    clL, clR, M = cluster(E)

    def vr(i):
        r = ot.ValueRecord()
        r.XAdvance = int(T[i][0])
        return r

    subs, nexc, ncls = build_subtables(font, L, R, E, T, clL, clR, M, vr)
    old = font["GPOS"].table.LookupList.Lookup[li]
    snapshot = (old.SubTable, old.SubTableCount, old.LookupType)
    _install(font, li, subs)
    # compile and reload to check exactly what will be written
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    chk = TTFont(buf)
    K2 = Kern(chk, li)
    bad = sum(1 for i, a in enumerate(L) for j, b in enumerate(R) if K2.get(a, b) != T[E[i][j]][0])
    if bad:
        _install(font, li, snapshot[0])
        raise AssertionError(f"{bad} kerning pairs differ")
    return dict(lookup=li, classes=ncls, exceptions=nexc, pairs=len(L) * len(R))


def recode_variable(font, path_in, work_tmp=None):
    """Variable font: per-master tuple clustering; values written as deltas appended to the GDEF variation store."""
    li = find_kern_lookup(font)
    axes = font["fvar"].axes
    tags = [a.axisTag for a in axes]
    values = [sorted({a.minValue, a.defaultValue, a.maxValue}) for a in axes]
    masters = list(itertools.product(*values))
    default = tuple(a.defaultValue for a in axes)
    assert default in masters
    norm = [dict((a.axisTag, normalizeValue(v, (a.minValue, a.defaultValue, a.maxValue))) for a, v in zip(axes, m))
            for m in masters]
    model = VariationModel(norm, axisOrder=tags)
    Ks = []
    for m in masters:
        inst = instantiateVariableFont(TTFont(path_in), dict(zip(tags, m)), inplace=False)
        Ks.append(Kern(inst, li))
    for k in Ks:  # the instance keeps the glyph order of the VF
        k.font = font
    L, R, E, T = build_matrix(Ks, lambda a, b: tuple(k.get(a, b) for k in Ks))
    for k in Ks:                         # glyphs outside R must be unkerned, or the class-0 column would be lost
        for a in L:
            assert k.get(a, ".none.") == 0, a
    clL, clR, M = cluster(E)
    # deltas for every distinct tuple
    gpos_vs = font["GDEF"].table.VarStore
    regions = gpos_vs.VarRegionList.Region
    rkey = lambda r: tuple((a.StartCoord, a.PeakCoord, a.EndCoord) for a in r.VarRegionAxis)
    have = {rkey(r): i for i, r in enumerate(regions)}
    ridx = []
    for sup in model.supports[1:]:
        t = tuple(tuple(sup.get(tag, (0.0, 0.0, 0.0))) for tag in tags)
        if t not in have:
            regions.append(VB.buildVarRegion(sup, tags))
            have[t] = len(regions) - 1
        ridx.append(have[t])
    gpos_vs.VarRegionList.RegionCount = len(regions)
    order_default = masters.index(default)
    rows, rowof = [], {}
    for i, t in enumerate(T):
        d = model.getDeltas(list(t))
        if any(round(x) for x in d[1:]):
            rowof[i] = len(rows)
            rows.append([int(round(x)) for x in d[1:]])
    vd = VB.buildVarData(ridx, rows, optimize=True)
    outer = gpos_vs.VarDataCount
    gpos_vs.VarData.append(vd)
    gpos_vs.VarDataCount += 1
    devs = {}

    def vr(i):
        r = ot.ValueRecord()
        d = model.getDeltas(list(T[i]))
        r.XAdvance = int(round(d[0]))
        if i in rowof:
            dv = devs.get(i)
            if dv is None:
                dv = ot.Device()
                dv.DeltaFormat = 0x8000
                dv.StartSize, dv.EndSize = outer, rowof[i]
                devs[i] = dv
            r.XAdvDevice = dv
        return r

    subs, nexc, ncls = build_subtables(font, L, R, E, T, clL, clR, M, vr)
    _install(font, li, subs)
    # drop the variation rows that only the old kerning records used, as the subsetter does (renumbers all references)
    from fontTools.subset import _pruneGDEF
    _pruneGDEF(font)
    return dict(lookup=li, classes=ncls, exceptions=nexc, distinct_values=len(T), var_rows=len(rows),
                masters=len(masters), pairs=len(L) * len(R))
