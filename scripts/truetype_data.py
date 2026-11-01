"""Write the TrueType data that a Glyphs source does not hold into a built TTF.

sources/<Family>-truetype.json holds the hinting of the font (the fpgm, prep and cvt tables and the maxp limits that
go with them), the instructions of each hinted glyph, the component flags of each composite glyph and
OS/2.xAvgCharWidth. The build writes the outlines from the Glyphs source; this step adds the rest.

A glyph gets its instructions only while its outline is the one they were made for. The stored id is the glyph hash
that ufo2ft uses for the same purpose (points, components and advance width, fontTools HashPointPen); a glyph whose
outline has changed keeps no instructions and is listed. Component flags are written where the glyph still has the
same components.

Usage: python -I scripts/truetype_data.py sources/MedeoSerif-truetype.json out/build/fonts/MedeoSerif/ttf/*.ttf
"""
import array
import json
import sys
from functools import partial

from fontTools.misc.fixedTools import floatToFixedToFloat
from fontTools.pens.hashPointPen import HashPointPen
from fontTools.pens.roundingPen import RoundingPointPen
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import ttProgram

# the component flags a source decides; the others follow from the compiled data
COMPONENT_FLAGS = 0x0004 | 0x0200 | 0x0400 | 0x0800 | 0x1000   # round to grid, use my metrics, overlap, offsets


def glyph_hash(font, name):
    glyf = font["glyf"]
    hp = HashPointPen(font["hmtx"][name][0], font.getGlyphSet())
    glyf[name].drawPoints(RoundingPointPen(hp, transformRoundFunc=partial(floatToFixedToFloat, precisionBits=14)),
                          glyf)
    return hp.hash


def program(lines):
    p = ttProgram.Program()
    p.fromAssembly(lines)
    return p


def apply(data, path):
    font = TTFont(path)
    glyf = font["glyf"]
    for tag, key in (("fpgm", "fontProgram"), ("prep", "controlValueProgram")):
        font[tag] = newTable(tag)
        font[tag].program = program(data[key])
    font["cvt "] = newTable("cvt ")
    font["cvt "].values = array.array("h", data["controlValue"])
    for key, value in data["maxp"].items():
        setattr(font["maxp"], key, value)
    for key, value in data["OS/2"].items():
        setattr(font["OS/2"], key, value)
    stale, changed = [], []
    for name, entry in data["glyphs"].items():
        if name not in glyf:
            stale.append(name)
            continue
        g = glyf[name]
        if "assembly" in entry:
            if glyph_hash(font, name) == entry["id"]:
                g.program = program(entry["assembly"])
            else:
                stale.append(name)
        if "componentFlags" in entry:
            if g.isComposite() and len(g.components) == len(entry["componentFlags"]):
                for c, flags in zip(g.components, entry["componentFlags"]):
                    c.flags = (c.flags & ~COMPONENT_FLAGS) | (flags & COMPONENT_FLAGS)
            else:
                changed.append(name)
    font.save(path)
    if stale:
        print(f"{path}: no instructions for {len(stale)} changed glyphs: {' '.join(stale)}")
    if changed:
        print(f"{path}: component flags not applied to {len(changed)} changed glyphs: {' '.join(changed)}")


def main():
    with open(sys.argv[1], encoding="utf-8") as f:
        data = json.load(f)
    for path in sys.argv[2:]:
        apply(data, path)


if __name__ == "__main__":
    main()
