"""Compare the OpenType layout of two fonts by what a shaper does with it.

Two compilations of the same features can lay GSUB and GPOS out differently (lookup order and numbering, subtable
formats, extension lookups, kerning split into lookups by script, an extra script record) and still shape every text
the same way. compare() reduces each table to that behaviour and lists every difference:

  - language systems: every script and language of either font; a script that a font lacks falls back to DFLT and a
    language to the script's default, as in shapers;
  - GSUB, per language system: the lookups of each feature in the order they run, each lookup by its content (rules
    expanded per first glyph, nested lookups by content, lookup flags and mark filtering sets by their glyphs);
  - GPOS kerning (pair lookups): the summed adjustment of every glyph pair, separately for lookups that skip marks
    and for those that do not;
  - GPOS mark, mkmk: the final offset of every mark on every base or mark (the last lookup that applies wins), with
    the lookup flags and mark filtering set it was attached under;
  - stylistic set names, GDEF glyph classes and mark attachment classes. A glyph that is a base glyph in one font
    and unclassified in the other is a note, not a difference, while no lookup ignores base glyphs: both are
    non-marks to every lookup.

A lookup type not listed here is reported as a difference rather than skipped, so an unknown table never passes.
"""
from collections import defaultdict

import numpy as np

VALUE_FIELDS = ("XPlacement", "YPlacement", "XAdvance", "YAdvance")


def _unwrap(lookup, extension):
    subs = []
    for st in lookup.SubTable:
        if lookup.LookupType == extension:
            subs.append((st.ExtensionLookupType, st.ExtSubTable))
        else:
            subs.append((lookup.LookupType, st))
    types = {t for t, _ in subs}
    return (types.pop() if len(types) == 1 else None), [s for _, s in subs]


class Layout:
    def __init__(self, font, tag):
        self.font = font
        self.tag = tag
        self.order = font.getGlyphOrder()
        self.index = {n: i for i, n in enumerate(self.order)}
        self.table = font[tag].table if tag in font else None
        gdef = font["GDEF"].table if "GDEF" in font else None
        self.classes = dict(gdef.GlyphClassDef.classDefs) if gdef and gdef.GlyphClassDef else {}
        self.attach = dict(gdef.MarkAttachClassDef.classDefs) if gdef and gdef.MarkAttachClassDef else {}
        self.sets = ([frozenset(c.glyphs) for c in gdef.MarkGlyphSetsDef.Coverage]
                     if gdef and getattr(gdef, "MarkGlyphSetsDef", None) else [])
        self.marks = np.array([self.classes.get(n) == 3 for n in self.order])
        self._canon = {}

    # language systems ------------------------------------------------------------------------------------------
    def systems(self):
        out = {}
        if self.table is None:
            return out
        for sr in self.table.ScriptList.ScriptRecord:
            if sr.Script.DefaultLangSys is not None:
                out[(sr.ScriptTag, "dflt")] = sr.Script.DefaultLangSys
            for lr in sr.Script.LangSysRecord:
                out[(sr.ScriptTag, lr.LangSysTag.strip())] = lr.LangSys
        return out

    def features(self, script, lang):
        """{feature tag: sorted lookup indices} of the language system a shaper picks for script and language."""
        systems = self.systems()
        scripts = {s for s, _ in systems}
        if script not in scripts:
            script = "DFLT"
        ls = systems.get((script, lang)) or systems.get((script, "dflt"))
        if ls is None:
            return {}
        recs = self.table.FeatureList.FeatureRecord
        idx = list(ls.FeatureIndex)
        if ls.ReqFeatureIndex != 0xFFFF:
            idx.append(ls.ReqFeatureIndex)
        out = defaultdict(set)
        for fi in idx:
            out[recs[fi].FeatureTag] |= set(recs[fi].Feature.LookupListIndex)
        return {t: tuple(sorted(v)) for t, v in out.items()}

    def feature_params(self):
        out = {}
        if self.table is None:
            return out
        name = self.font["name"] if "name" in self.font else None
        for r in self.table.FeatureList.FeatureRecord:
            p = r.Feature.FeatureParams
            if p is None:
                continue
            if hasattr(p, "UINameID"):
                out[r.FeatureTag] = ("name", name.getDebugName(p.UINameID) if name else None)
            else:
                out[r.FeatureTag] = ("params", type(p).__name__)
        return out

    # lookup content ---------------------------------------------------------------------------------------------
    def flags(self, lookup):
        f = lookup.LookupFlag
        fs = self.sets[lookup.MarkFilteringSet] if f & 0x10 else None
        at = None
        if f & 0xFF00:
            at = frozenset(g for g, c in self.attach.items() if c == f >> 8)
        return (f & 0x0F, fs, at)

    def glyph_set(self, classdef, c):
        if c == 0:
            return frozenset(g for g in self.order if g not in classdef)
        return frozenset(g for g, k in classdef.items() if k == c)

    def canon(self, li):
        """Content of a GSUB lookup (or any lookup not reduced elsewhere), independent of its index."""
        if li in self._canon:
            return self._canon[li]
        self._canon[li] = ("cycle", li)
        lookup = self.table.LookupList.Lookup[li]
        ext = 7 if self.tag == "GSUB" else 9
        kind, subs = _unwrap(lookup, ext)
        if self.tag == "GSUB" and kind in (1, 2, 3):
            m = {}
            for st in subs:
                src = st.mapping if kind in (1, 2) else st.alternates
                for g, v in src.items():
                    m.setdefault(g, tuple(v) if isinstance(v, list) else v)
            body = tuple(sorted(m.items()))
        elif self.tag == "GSUB" and kind == 4:
            m = defaultdict(list)
            for st in subs:
                for first, ligs in st.ligatures.items():
                    m[first] += [(tuple(l.Component), l.LigGlyph) for l in ligs]
            body = tuple(sorted((k, tuple(v)) for k, v in m.items()))
        elif kind in ((5, 6) if self.tag == "GSUB" else (7, 8)):
            body = self.context_rules(subs, kind in (6, 8))
        else:
            body = ("unsupported", self.tag, lookup.LookupType, li)
        result = (kind, self.flags(lookup), body)
        self._canon[li] = result
        return result

    def context_rules(self, subs, chained):
        """Rules per first input glyph, in the order a shaper tries them."""
        per_glyph = defaultdict(list)
        recname = "SubstLookupRecord" if self.tag == "GSUB" else "PosLookupRecord"
        for st in subs:
            fmt = st.Format
            rules = []      # (first glyphs, backtrack, input rest, lookahead, records)
            if fmt == 1:
                cov = st.Coverage.glyphs
                sets = st.ChainSubRuleSet if self.tag == "GSUB" and chained else (
                    st.SubRuleSet if self.tag == "GSUB" else (st.ChainPosRuleSet if chained else st.PosRuleSet))
                for g, rs in zip(cov, sets):
                    if rs is None:
                        continue
                    rlist = (rs.ChainSubRule if self.tag == "GSUB" and chained else
                             rs.SubRule if self.tag == "GSUB" else rs.ChainPosRule if chained else rs.PosRule)
                    for r in rlist:
                        rules.append(([g], tuple(frozenset([x]) for x in getattr(r, "Backtrack", [])),
                                      tuple(frozenset([x]) for x in r.Input),
                                      tuple(frozenset([x]) for x in getattr(r, "LookAhead", [])),
                                      getattr(r, recname)))
            elif fmt == 2:
                cov = set(st.Coverage.glyphs)
                if chained:
                    bcd, icd, lcd = (st.BacktrackClassDef.classDefs, st.InputClassDef.classDefs,
                                     st.LookAheadClassDef.classDefs)
                else:
                    bcd = lcd = {}
                    icd = st.ClassDef.classDefs
                sets = (st.ChainSubClassSet if chained else st.SubClassSet) if self.tag == "GSUB" else (
                    st.ChainPosClassSet if chained else st.PosClassSet)
                for c, rs in enumerate(sets):
                    if rs is None:
                        continue
                    firsts = sorted(cov & self.glyph_set(icd, c), key=self.index.get)
                    rlist = (rs.ChainSubClassRule if chained else rs.SubClassRule) if self.tag == "GSUB" else (
                        rs.ChainPosClassRule if chained else rs.PosClassRule)
                    for r in rlist:
                        rules.append((firsts, tuple(self.glyph_set(bcd, x) for x in getattr(r, "Backtrack", [])),
                                      tuple(self.glyph_set(icd, x) for x in r.Input),
                                      tuple(self.glyph_set(lcd, x) for x in getattr(r, "LookAhead", [])),
                                      getattr(r, recname)))
            elif fmt == 3:
                inp = st.InputCoverage if chained else st.Coverage
                rules.append((inp[0].glyphs,
                              tuple(frozenset(c.glyphs) for c in getattr(st, "BacktrackCoverage", [])),
                              tuple(frozenset(c.glyphs) for c in inp[1:]),
                              tuple(frozenset(c.glyphs) for c in getattr(st, "LookAheadCoverage", [])),
                              getattr(st, recname)))
            for firsts, bt, rest, la, recs in rules:
                nested = tuple((r.SequenceIndex, self.canon(r.LookupListIndex)) for r in recs)
                for g in firsts:
                    per_glyph[g].append((bt, rest, la, nested))
        return tuple(sorted((g, tuple(v)) for g, v in per_glyph.items()))

    # GPOS --------------------------------------------------------------------------------------------------------
    def pairs(self, indices):
        """Summed pair adjustments of the pair lookups among `indices`: {(skips marks, field): N×N matrix}."""
        N = len(self.order)
        out = {}
        for li in indices:
            lookup = self.table.LookupList.Lookup[li]
            kind, subs = _unwrap(lookup, 9)
            if kind != 2:
                continue
            f, fs, at = self.flags(lookup)
            if fs is not None or at is not None or f & 0x6:
                out[("unsupported pair flags", li)] = None
                continue
            skip = bool(f & 0x8)
            claimed = np.zeros((N, N), dtype=bool)
            vals = defaultdict(lambda: np.zeros((N, N), dtype=np.int32))
            for st in subs:
                fields = [(1, k) for k in VALUE_FIELDS if st.ValueFormat1 & (1 << VALUE_FIELDS.index(k))]
                fields += [(2, k) for k in VALUE_FIELDS if st.ValueFormat2 & (1 << VALUE_FIELDS.index(k))]
                if st.Format == 1:
                    for g1, ps in zip(st.Coverage.glyphs, st.PairSet):
                        i = self.index[g1]
                        for r in ps.PairValueRecord:
                            j = self.index[r.SecondGlyph]
                            if claimed[i, j]:
                                continue
                            claimed[i, j] = True
                            for side, k in fields:
                                v = getattr(r, f"Value{side}", None)
                                vals[(side, k)][i, j] = getattr(v, k, 0) or 0 if v is not None else 0
                else:
                    c2 = np.zeros(N, dtype=np.int64)
                    for g, c in st.ClassDef2.classDefs.items():
                        c2[self.index[g]] = c
                    tables = {}
                    for side, k in fields:
                        tables[(side, k)] = np.array(
                            [[(getattr(getattr(r, f"Value{side}", None), k, 0) or 0) for r in rec.Class2Record]
                             for rec in st.Class1Record], dtype=np.int32)
                    cd1 = st.ClassDef1.classDefs
                    for g in st.Coverage.glyphs:
                        i = self.index[g]
                        free = ~claimed[i]
                        for key, t in tables.items():
                            vals[key][i, free] = t[cd1.get(g, 0)][c2][free]
                        claimed[i, :] = True
            for key, m in vals.items():
                if skip:
                    m[self.marks, :] = 0
                    m[:, self.marks] = 0
                full = (skip,) + key
                out[full] = m if full not in out else out[full] + m
        return {k: v for k, v in out.items() if v is None or np.any(v)}

    def attachments(self, indices):
        """Final offset of every attached mark: {(kind, base or mark1, mark): (dx, dy, flags)}."""
        out = {}
        for li in sorted(indices):
            lookup = self.table.LookupList.Lookup[li]
            kind, subs = _unwrap(lookup, 9)
            if kind not in (4, 5, 6):
                continue
            fl = self.flags(lookup)
            for st in subs:
                if kind == 4:
                    marks = list(zip(st.MarkCoverage.glyphs, st.MarkArray.MarkRecord))
                    for b, br in zip(st.BaseCoverage.glyphs, st.BaseArray.BaseRecord):
                        for m, mr in marks:
                            a = br.BaseAnchor[mr.Class]
                            if a is not None:
                                out[("base", b, m)] = (a.XCoordinate - mr.MarkAnchor.XCoordinate,
                                                       a.YCoordinate - mr.MarkAnchor.YCoordinate, fl)
                elif kind == 6:
                    marks = list(zip(st.Mark1Coverage.glyphs, st.Mark1Array.MarkRecord))
                    for b, br in zip(st.Mark2Coverage.glyphs, st.Mark2Array.Mark2Record):
                        for m, mr in marks:
                            a = br.Mark2Anchor[mr.Class]
                            if a is not None:
                                out[("mark", b, m)] = (a.XCoordinate - mr.MarkAnchor.XCoordinate,
                                                       a.YCoordinate - mr.MarkAnchor.YCoordinate, fl)
                else:
                    marks = list(zip(st.MarkCoverage.glyphs, st.MarkArray.MarkRecord))
                    for b, lr in zip(st.LigatureCoverage.glyphs, st.LigatureArray.LigatureAttach):
                        for ci, comp in enumerate(lr.ComponentRecord):
                            for m, mr in marks:
                                a = comp.LigatureAnchor[mr.Class]
                                if a is not None:
                                    out[("ligature", b, ci, m)] = (
                                        a.XCoordinate - mr.MarkAnchor.XCoordinate,
                                        a.YCoordinate - mr.MarkAnchor.YCoordinate, fl)
        return out

    def others(self, indices):
        out = []
        for li in sorted(indices):
            kind, _ = _unwrap(self.table.LookupList.Lookup[li], 9)
            if kind not in (2, 4, 5, 6):
                out.append(self.canon(li))
        return tuple(out)


def _gsub_effect(lay, feats):
    """Lookups of the language system in the order they run, each with the features that call it."""
    by_lookup = defaultdict(set)
    for tag, idx in feats.items():
        for li in idx:
            by_lookup[li].add(tag)
    return [(lay.canon(li), frozenset(tags)) for li, tags in sorted(by_lookup.items())]


def _diff_gsub(a, b):
    ea, eb = _gsub_effect(*a), _gsub_effect(*b)
    if ea == eb:
        return []
    problems = []
    ta = defaultdict(list)
    tb = defaultdict(list)
    for c, tags in ea:
        for t in tags:
            ta[t].append(c)
    for c, tags in eb:
        for t in tags:
            tb[t].append(c)
    for t in sorted(set(ta) | set(tb)):
        if ta[t] != tb[t]:
            problems.append(f"GSUB {{where}} {t}: lookups differ")
    if not problems:
        problems.append("GSUB {where}: same lookups per feature, different order across features")
    return problems


def _diff_gpos(a, b, cache):
    (la, fa), (lb, fb) = a, b
    problems = []
    for t in sorted(set(fa) | set(fb)):
        ka, kb = fa.get(t, ()), fb.get(t, ())
        key = (t, ka, kb)
        if key in cache:
            problems += cache[key]
            continue
        found = []
        pa, pb = la.pairs(ka), lb.pairs(kb)
        for k in sorted(set(pa) | set(pb), key=str):
            x, y = pa.get(k), pb.get(k)
            if x is None or y is None or not np.array_equal(x, y):
                if x is None or y is None:
                    found.append(f"GPOS {{where}} {t}: pair adjustments {k} only in one font")
                else:
                    d = np.argwhere(x != y)
                    eg = ", ".join(f"{la.order[i]} {la.order[j]} {x[i, j]}→{y[i, j]}" for i, j in d[:5])
                    found.append(f"GPOS {{where}} {t}: {len(d)} pairs differ {k}: {eg}")
        aa, ab = la.attachments(ka), lb.attachments(kb)
        if aa != ab:
            keys = sorted((set(aa) | set(ab)), key=str)
            bad = [k for k in keys if aa.get(k) != ab.get(k)]
            found.append(f"GPOS {{where}} {t}: {len(bad)} mark attachments differ: "
                         + ", ".join(f"{k[1:]} {aa.get(k, (None,))[:2]}→{ab.get(k, (None,))[:2]}" for k in bad[:5]))
        if la.others(ka) != lb.others(kb):
            found.append(f"GPOS {{where}} {t}: other lookups differ")
        cache[key] = found
        problems += found
    return problems


def _ignores_bases(font):
    for tag in ("GSUB", "GPOS"):
        if tag in font and any(lk.LookupFlag & 0x2 for lk in font[tag].table.LookupList.Lookup):
            return True
    return False


def compare(font_a, font_b):
    """(problems, notes): differences in shaping, and differences a shaper does not see."""
    problems, notes = [], []
    ga, gb = Layout(font_a, "GDEF"), Layout(font_b, "GDEF")
    if ga.classes != gb.classes:
        names = sorted({g for g, _ in set(ga.classes.items()) ^ set(gb.classes.items())})
        text = ", ".join(f"{g} {ga.classes.get(g, 0)}→{gb.classes.get(g, 0)}" for g in names[:10])
        # base (1) and unclassified (0) differ only for lookups that ignore base glyphs
        if all({ga.classes.get(g, 0), gb.classes.get(g, 0)} == {0, 1} for g in names) and not (
                _ignores_bases(font_a) or _ignores_bases(font_b)):
            notes.append(f"GDEF base/unclassified, no lookup ignores base glyphs: {text}")
        else:
            problems.append(f"GDEF glyph classes differ: {text}")
    if ga.attach != gb.attach:
        problems.append("GDEF mark attachment classes differ")
    for tag in ("GSUB", "GPOS"):
        la, lb = Layout(font_a, tag), Layout(font_b, tag)
        if (la.table is None) != (lb.table is None):
            problems.append(f"{tag} only in one font")
            continue
        if la.table is None:
            continue
        for t in (la, lb):
            if getattr(t.table, "FeatureVariations", None) is not None:
                problems.append(f"{tag}: feature variations are not compared")
        if la.feature_params() != lb.feature_params():
            problems.append(f"{tag} feature parameters (stylistic set names) differ")
        systems = sorted(set(la.systems()) | set(lb.systems()))
        cache, seen = {}, {}
        for script, lang in systems:
            fa, fb = la.features(script, lang), lb.features(script, lang)
            key = (tuple(sorted(fa.items())), tuple(sorted(fb.items())))
            if key not in seen:
                if set(fa) != set(fb):
                    seen[key] = [f"{tag} {{where}}: features {sorted(fa)} vs {sorted(fb)}"]
                elif tag == "GSUB":
                    seen[key] = _diff_gsub((la, fa), (lb, fb))
                else:
                    seen[key] = _diff_gpos((la, fa), (lb, fb), cache)
            problems += [p.replace("{where}", f"{script}/{lang}") for p in seen[key]]
    return problems, notes
