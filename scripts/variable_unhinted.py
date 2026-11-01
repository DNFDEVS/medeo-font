"""Variable Medeo Sans and Medeo Mono without TrueType hinting, as the Google Fonts guide recommends for variable
fonts; the static TTFs keep ttfautohint for Windows apps.

For every variable font of Medeo Sans and Medeo Mono: overlap flags for rasterizers that require them, an explicit
advance width map in HVAR, no instructions or hinting tables (the fontTools subsetter drops them and keeps every
glyph, feature, name and variation), and the gasp table (smooth at all sizes) and prep program (dropout control)
that `gftools fix-nonhinting` writes for unhinted fonts.

Usage: python -I scripts/variable_unhinted.py <fonts dir>
"""
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables import otTables, ttProgram
from fontTools.varLib.instancer import setMacOverlapFlags


def unhinted(path):
    font = TTFont(path)
    order = font.getGlyphOrder()
    for tag in font.keys():
        if tag != "GlyphOrder":
            font[tag]  # decompile under the build's glyph order
    if "HVAR" in font and font["HVAR"].table.AdvWidthMap is None:
        widths = otTables.VarIdxMap()
        widths.mapping = {name: i for i, name in enumerate(order)}
        font["HVAR"].table.AdvWidthMap = widths
    setMacOverlapFlags(font["glyf"])
    font["head"].flags |= 1 << 3
    opts = subset.Options()
    opts.hinting = False
    opts.layout_features = ["*"]
    opts.layout_scripts = ["*"]
    opts.name_IDs = ["*"]
    opts.name_languages = ["*"]
    opts.name_legacy = True
    opts.glyph_names = True
    opts.legacy_kern = True
    opts.notdef_glyph = True
    opts.notdef_outline = True
    opts.recalc_bounds = False
    opts.recalc_timestamp = False
    opts.prune_unicode_ranges = False
    opts.prune_codepage_ranges = False
    opts.passthrough_tables = True
    opts.drop_tables = ["fpgm", "prep", "cvt ", "cvar", "hdmx", "LTSH", "VDMX", "DSIG"]
    sub = subset.Subsetter(opts)
    sub.populate(glyphs=order)
    sub.subset(font)
    assert font.getGlyphOrder() == order, "the subsetter changed the glyph order"
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 15}
    prep = newTable("prep")
    prep.program = ttProgram.Program()
    prep.program.fromAssembly(["PUSHW[]", "511", "SCANCTRL[]", "PUSHB[]", "4", "SCANTYPE[]"])
    font["gasp"], font["prep"] = gasp, prep
    font.save(path)
    print(path.name)


def main():
    root = Path(sys.argv[1])
    paths = sorted(root.glob("MedeoSans/variable/*.ttf")) + sorted(root.glob("MedeoMono/variable/*.ttf"))
    if len(paths) != 4:
        raise SystemExit(f"expected four Sans and Mono variable fonts, found {len(paths)}")
    for path in paths:
        unhinted(path)


if __name__ == "__main__":
    main()
