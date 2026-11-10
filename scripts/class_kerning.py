"""Medeo Sans: one kerning table for all scripts, stored as classes, in every variable and static font.

Letters that behave alike share a class whatever their script, so the table stays small enough that one web font
per style holds every alphabet and kerning works across all of them. The classes and values are in
sources/MedeoSans-kerning.json and sources/MedeoSans-Italic-kerning.json. Marks, anchors and every other table
stay as they were.

Usage: python -I scripts/class_kerning.py out/build/fonts
"""
import io
import json
import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot
from fontTools.ttLib.tables.otBase import ValueRecord
from fontTools.varLib.builder import buildVarData
from fontTools.varLib.models import supportScalar

ROOT = Path(__file__).resolve().parent.parent
PEAKS = [(0, 1), (-1, 0), (1, 0), (-1, 1), (1, 1)]  # (wght, opsz) of the five deltas in each row


def regions(store, fvar):
    tags = [a.axisTag for a in fvar.axes]
    found = []
    for wght, opsz in PEAKS:
        want = {"wght": wght, "opsz": opsz}
        for i, r in enumerate(store.VarRegionList.Region):
            if all(x.PeakCoord == want[t] and x.StartCoord == min(want[t], 0) and x.EndCoord == max(want[t], 0)
                   for t, x in zip(tags, r.VarRegionAxis)):
                found.append(i)
                break
        else:
            raise SystemExit(f"no variation region at wght {wght}, opsz {opsz}")
    return found


def scalars(weight, opsz):
    loc = {"wght": (weight - 400) / (500 if weight > 400 else 300), "opsz": (opsz - 14) / 18}
    return [supportScalar(loc, {"wght": (min(w, 0), w, max(w, 0)), "opsz": (min(o, 0), o, max(o, 0))})
            for w, o in PEAKS]


def apply(font, data, row_value):
    gpos = font["GPOS"].table
    order = set(font.getGlyphOrder())
    missing = (set(data["first"]) | set(data["second"])) - order
    if missing:
        raise SystemExit(f"kerning names glyphs the font does not have: {sorted(missing)[:8]}")
    s = ot.PairPos()
    s.Format, s.ValueFormat2 = 2, 0
    s.Coverage = ot.Coverage()
    s.Coverage.glyphs = sorted(data["first"], key=font.getGlyphID)
    s.ClassDef1, s.ClassDef2 = ot.ClassDef(), ot.ClassDef()
    s.ClassDef1.classDefs = {g: c for g, c in data["first"].items() if c}
    s.ClassDef2.classDefs = {g: c + 1 for g, c in data["second"].items()}
    cells = data["cells"]
    s.Class1Count, s.Class2Count = len(cells), len(cells[0]) + 1
    s.Class1Record = []
    for line in cells:
        rec = ot.Class1Record()
        rec.Class2Record = []
        for c2 in [0] + line:
            cell = ot.Class2Record()
            cell.Value1, cell.Value2 = row_value(c2), None
            rec.Class2Record.append(cell)
        s.Class1Record.append(rec)
    kern = sorted({i for r in gpos.FeatureList.FeatureRecord if r.FeatureTag == "kern"
                   for i in r.Feature.LookupListIndex})
    for n, i in enumerate(kern):
        lk = gpos.LookupList.Lookup[i]
        lk.LookupType = 2
        lk.SubTable = [s] if n == 0 else []
        lk.SubTableCount = len(lk.SubTable)
    for r in gpos.FeatureList.FeatureRecord:
        if r.FeatureTag == "kern":
            r.Feature.LookupListIndex = kern[:1]
            r.Feature.LookupCount = 1
    return s


def variable(font, data):
    gdef = font["GDEF"].table
    gpos = font["GPOS"].table
    store = gdef.VarStore
    major = len(store.VarData)
    rows = data["rows"]
    moving = {i: m for m, i in enumerate(i for i, r in enumerate(rows) if any(r[1:]))}

    def value(i):
        v = ValueRecord()
        v.XAdvance = rows[i][0]
        if i in moving:
            d = ot.Device()
            d.StartSize, d.EndSize, d.DeltaFormat = major, moving[i], 0x8000
            v.XAdvDevice = d
        return v

    s = apply(font, data, value)
    s.ValueFormat1 = 0x44
    store.VarData.append(buildVarData(regions(store, font["fvar"]), [rows[i][1:] for i in moving], optimize=False))
    store.VarDataCount = len(store.VarData)
    used = set()
    gpos.collect_device_varidxes(used)
    gdef.collect_device_varidxes(used)
    for mapping in (store.subset_varidxes(used), store.optimize()):
        gpos.remap_device_varidxes(mapping)
        gdef.remap_device_varidxes(mapping)


def static(font, data, opsz):
    sc = scalars(font["OS/2"].usWeightClass, opsz)
    rows = data["rows"]

    def value(i):
        v = ValueRecord()
        v.XAdvance = round(rows[i][0] + sum(a * b for a, b in zip(sc, rows[i][1:])))
        return v

    apply(font, data, value).ValueFormat1 = 0x04


def save(font, path):
    buf = io.BytesIO()
    font.save(buf)
    path.write_bytes(buf.getvalue())


def main():
    build = Path(sys.argv[1])
    source = {False: json.load(open(ROOT / "sources/MedeoSans-kerning.json")),
              True: json.load(open(ROOT / "sources/MedeoSans-Italic-kerning.json"))}
    fonts = sorted(build.glob("MedeoSans/variable/*.ttf"))
    if len(fonts) != 2:
        raise SystemExit(f"expected two Medeo Sans variable fonts, found {len(fonts)}")
    for path in fonts:
        font = TTFont(path)
        variable(font, source["Italic" in path.name])
        save(font, path)
        print(path.name, flush=True)
    for path in sorted(build.glob("MedeoSans/ttf/*.ttf")):
        font = TTFont(path)
        static(font, source["Italic" in path.name], 32 if "Display" in path.name else 14)
        save(font, path)
    print("statics done", flush=True)


if __name__ == "__main__":
    main()
