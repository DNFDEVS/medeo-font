"""Static Medeo Sans and Medeo Mono: every static TTF is the matching weight cut from the variable font.

The builder makes one static per named instance with fontmake, which decomposes every composite glyph. This step
replaces each of them with the same weight cut from the variable font of the same build (Medeo Sans at opsz 14, the
text size and the default of its optical size axis):

- overlaps are removed by fontTools, which decomposes only the composite glyphs whose components overlap; every other
  composite glyph stays a composite, as in the variable font. The glyphs are tested once more after the cut has
  rounded its coordinates: components that only touched, or the two sides of a thin stroke, can overlap by a unit
  then, and such glyphs are merged again;
- names, weight class, style flags and the head dates of the builder's static are kept, and every stylistic set points
  to the name ID with the same text;
- the advance widths are the builder's: at weights between the masters the variable font rounds a few of them one
  unit the other way (the outlines stay as cut; a difference of more than one unit stops the step);
- Medeo Sans' kerning is stored as classes plus exceptions (scripts/kerncodec.py); every glyph pair is checked against
  the kerning of the cut font before it is written;
- the font is hinted with ttfautohint, as the builder hints its statics.

The cut must keep the builder's static as it was in everything a user or an app reads: the same characters, glyph
names, advance widths, names, OS/2 table and vertical metrics. The step stops on any difference.

Medeo Sans Display is cut the same way at opsz 32 (scripts/display_statics.py).

Usage: python -I scripts/static_instances.py out/build/fonts
"""
import io
import os
import sys
from multiprocessing import Pool
from pathlib import Path

import pathops
import ttfautohint
from fontTools.ttLib import TTFont
from fontTools.ttLib.removeOverlaps import removeOverlaps
from fontTools.varLib.instancer import OverlapMode, instantiateVariableFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kerncodec import recode_static  # noqa: E402

FAMILIES = {
    # family: (glob of the builder's statics, roman and italic variable font, axes besides wght, recode kerning)
    "MedeoSans": ("MedeoSans-*.ttf", ("MedeoSans[opsz,wght].ttf", "MedeoSans-Italic[opsz,wght].ttf"), {"opsz": 14}, True),
    "MedeoMono": ("MedeoMono-*.ttf", ("MedeoMono[wght].ttf", "MedeoMono-Italic[wght].ttf"), {}, False),
}
HHEA = ("ascent", "descent", "lineGap", "advanceWidthMax", "caretSlopeRise", "caretSlopeRun", "caretOffset")


def feature_params(font):
    return [r.Feature.FeatureParams for r in font["GSUB"].table.FeatureList.FeatureRecord
            if getattr(r.Feature.FeatureParams, "UINameID", None) is not None]


def self_overlapping(font):
    """Simple glyphs whose contours overlap: their signed areas add up to more than the area they fill."""
    glyphs = font.getGlyphSet()
    found = []
    for name in font.getGlyphOrder():
        if font["glyf"][name].numberOfContours <= 0:
            continue
        path = pathops.Path()
        glyphs[name].draw(path.getPen())
        filled = pathops.Path(path)
        filled.simplify(fix_winding=True)
        area = lambda p: abs(sum(c.area if c.clockwise else -c.area for c in p.contours))
        if area(path) - area(filled) > 1:
            found.append(name)
    return found


def cut_static(variable, donor, location, kern, rename=None, advances=False):
    """The static at `location` of `variable`, named and flagged as `donor`; returns the hinted font and its stats.

    rename: (old, new, name IDs) applied to the names, for a family cut under another name.
    advances: take the donor's advance widths (each at most one unit from the cut's)."""
    font = instantiateVariableFont(TTFont(variable), location, overlap=OverlapMode.REMOVE)
    rounded = io.BytesIO()
    font.save(rounded)
    font = TTFont(io.BytesIO(rounded.getvalue()))
    glyf = font["glyf"]
    composites = [g for g in font.getGlyphOrder() if glyf[g].isComposite()]
    removeOverlaps(font, composites + self_overlapping(font))
    stats = {"composites": sum(glyf[g].isComposite() for g in composites)}
    if advances:
        moved = []
        for glyph, (width, lsb) in font["hmtx"].metrics.items():
            want = donor["hmtx"][glyph][0]
            if want != width:
                if abs(want - width) > 1:
                    raise SystemExit(f"{glyph}: advance {width} in the variable font, {want} in the builder's static")
                font["hmtx"][glyph] = (want, lsb)
                moved.append(glyph)
        stats["advances"] = len(moved)
    for table in ("STAT", "MVAR", "HVAR", "avar"):
        if table in font:
            del font[table]
    name = font["name"]
    # the stylistic set names keep their text: each set points to the name ID the donor uses for that text
    labels = {r.toUnicode(): r.nameID for r in donor["name"].names if r.nameID >= 256 and r.platformID == 3}
    for param in {id(p): p for p in feature_params(font)}.values():
        param.UINameID = labels[name.getDebugName(param.UINameID)]
    name.names = []
    for record in donor["name"].names:
        value = record.toUnicode()
        for old, new, ids in rename or ():
            if record.nameID in ids:
                value = value.replace(old, new)
        name.setName(value, record.nameID, record.platformID, record.platEncID, record.langID)
    for field in ("usWeightClass", "fsSelection"):
        setattr(font["OS/2"], field, getattr(donor["OS/2"], field))
    for field in ("macStyle", "created", "modified"):
        setattr(font["head"], field, getattr(donor["head"], field))
    if kern:
        stats.update(recode_static(font))
    raw = io.BytesIO()
    font.save(raw)
    hinted = TTFont(io.BytesIO(ttfautohint.ttfautohint(in_buffer=raw.getvalue())), recalcTimestamp=False)
    hinted["head"].modified = donor["head"].modified
    hinted["head"].flags |= 1 << 3  # integer ppem, as in every hinted Medeo static
    # ttfautohint writes its version into name ID 5 with duplicate strings; fontTools writes the table again with
    # shared strings, as gftools fix does for the builder's statics
    hinted["name"]  # a loaded table is compiled again on save
    return hinted, stats


def same_as_donor(font, donor):
    """What a user or an app reads must not change: the problems, if any."""
    problems = []
    if font.getGlyphOrder() != donor.getGlyphOrder():
        problems.append("glyph names")
    if font.getBestCmap() != donor.getBestCmap():
        problems.append("cmap")
    if any(font["hmtx"][g][0] != donor["hmtx"][g][0] for g in donor.getGlyphOrder()):
        problems.append("advance widths")
    if font["OS/2"].compile(font) != donor["OS/2"].compile(donor):
        problems.append("OS/2")
    if any(getattr(font["hhea"], f) != getattr(donor["hhea"], f) for f in HHEA):
        problems.append("hhea")
    names = lambda f: sorted((r.nameID, r.platformID, r.platEncID, r.langID, r.toUnicode()) for r in f["name"].names)
    if names(font) != names(donor):
        problems.append("name")
    if font["post"].italicAngle != donor["post"].italicAngle or font["post"].isFixedPitch != donor["post"].isFixedPitch:
        problems.append("post")
    if font["meta"].data != donor["meta"].data:
        problems.append("meta")
    return problems


def job(args):
    static, variable, location, kern = args
    donor = TTFont(static)
    font, stats = cut_static(variable, donor, location, kern, advances=True)
    buf = io.BytesIO()
    font.save(buf)
    problems = same_as_donor(TTFont(io.BytesIO(buf.getvalue())), donor)
    if problems:
        return static, problems, stats
    Path(static).write_bytes(buf.getvalue())
    return static, [], stats


def main():
    root = Path(sys.argv[1])
    jobs = []
    for family, (pattern, variables, axes, kern) in FAMILIES.items():
        statics = sorted(p for p in (root / family / "ttf").glob(pattern) if "Display" not in p.name)
        if len(statics) != 18:
            raise SystemExit(f"{family}: expected 18 statics from the builder, found {len(statics)}")
        for static in statics:
            italic = bool(TTFont(static)["OS/2"].fsSelection & 1)
            location = {"wght": TTFont(static)["OS/2"].usWeightClass, **axes}
            jobs.append((str(static), str(root / family / "variable" / variables[italic]), location, kern))
    failed = 0
    with Pool(min(8, os.cpu_count() or 1)) as pool:
        for static, problems, stats in pool.imap_unordered(job, jobs):
            print(Path(static).name, "differs from the builder's static: " + ", ".join(problems) if problems else stats,
                  flush=True)
            failed += bool(problems)
    if failed:
        raise SystemExit(f"{failed} statics differ from the builder's statics")


if __name__ == "__main__":
    main()
