"""Write the web fonts: fonts/<Family>/webfonts/<Family>Variable[-Italic].woff2 from the variable TTFs.

Every character, every layout feature and every axis stays; TrueType hinting, glyph names, names other than the
basic ones and unused data go. Medeo Sans' kerning is already stored as classes plus exceptions in its variable fonts
(scripts/variable_kerning.py). The `meta` table (design and supported scripts) is kept.

Medeo Serif has one static style and no variable font: fonts/MedeoSerif/webfonts/MedeoSerif-Regular.woff2 is made
from its TTF the same way.

Medeo Pixel gets WOFF 1.0 of the whole variable font instead, under the file name the npm package has always loaded.
Up to 1.000-rc2 its pixels were decomposed and the 5 MB TTF compressed so well that OTS rejected the woff2 and WebKit
both files; since rc3 they are components and either format would load.

Usage: python -I scripts/webfonts.py fonts
"""
import pathlib
import sys

from fontTools import subset
from fontTools.ttLib import TTFont


def web_subset(font, dest):
    opts = subset.Options()
    opts.layout_features = ["*"]
    opts.layout_scripts = ["*"]
    opts.hinting = False
    opts.notdef_outline = True
    opts.name_IDs = [0, 1, 2, 3, 4, 5, 6, 13, 14, 16, 17, 25]
    opts.name_languages = [0x409]
    opts.glyph_names = False
    opts.legacy_kern = False
    opts.drop_tables += ["DSIG"]
    opts.no_subset_tables += ["meta"]
    opts.flavor = "woff2"
    opts.with_zopfli = False
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=sorted(font.getBestCmap()))
    sub.subset(font)
    font.flavor = "woff2"
    font.save(dest)


def main():
    root = pathlib.Path(sys.argv[1])
    for ttf in sorted(root.glob("*/variable/*.ttf")):
        family = ttf.parent.parent.name  # MedeoSans, MedeoMono, MedeoPixel
        style = "-Italic" if "Italic" in ttf.name else ""
        flavor = "woff" if family == "MedeoPixel" else "woff2"
        dest = ttf.parent.parent / "webfonts" / f"{family}Variable{style}.{flavor}"
        dest.parent.mkdir(exist_ok=True)
        if family == "MedeoPixel":
            font = TTFont(ttf, recalcTimestamp=False)
            font.flavor = flavor
            font.save(dest)
        else:
            web_subset(TTFont(ttf), dest)
        print(dest)
    for ttf in sorted(root.glob("MedeoSerif/ttf/*.ttf")):
        dest = ttf.parent.parent / "webfonts" / f"{ttf.stem}.woff2"
        dest.parent.mkdir(exist_ok=True)
        web_subset(TTFont(ttf), dest)
        print(dest)


if __name__ == "__main__":
    main()
