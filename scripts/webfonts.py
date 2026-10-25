"""Write the web fonts next to the variable TTFs: fonts/<Family>/webfonts/<Family>Variable[-Italic].woff2.

Medeo Pixel gets WOFF 1.0 instead: its outlines are thousands of identical pixel components, Brotli packs the
5 MB TTF so well that browsers' OTS rejects the woff2 («Implausible compression ratio», Chrome, 2026-10-22).

Usage: python -I scripts/webfonts.py fonts
"""
import pathlib
import sys

from fontTools.ttLib import TTFont

root = pathlib.Path(sys.argv[1])
for ttf in sorted(root.glob("*/variable/*.ttf")):
    family = ttf.parent.parent.name  # MedeoSans, MedeoMono, MedeoPixel
    style = "-Italic" if "Italic" in ttf.name else ""
    flavor = "woff" if family == "MedeoPixel" else "woff2"
    dest = ttf.parent.parent / "webfonts" / f"{family}Variable{style}.{flavor}"
    dest.parent.mkdir(exist_ok=True)
    font = TTFont(ttf, recalcTimestamp=False)
    font.flavor = flavor
    font.save(dest)
    print(dest)
