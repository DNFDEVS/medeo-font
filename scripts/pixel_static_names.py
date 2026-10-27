"""Names the static Medeo Pixel styles as one family: «Medeo Pixel» with the styles Square, Circle, Grid, Triangle
and Line (typographic family and subfamily, name IDs 16 and 17), so apps that read them list one family with five
styles. Apps that only read name IDs 1 and 2 keep one family per style, as for any family with more than four
styles.

Usage: python -I scripts/pixel_static_names.py fonts/MedeoPixel/ttf
"""
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

FAMILY = "Medeo Pixel"


def rename(path):
    style = path.stem.split("-", 1)[1]
    font = TTFont(path, recalcTimestamp=False)
    name = font["name"]
    old_ps = name.getDebugName(6)
    ps = f"MedeoPixel-{style}"
    unique = (name.getDebugName(3) or "").replace(old_ps, ps)
    for record_id, value in ((1, f"{FAMILY} {style}"), (2, "Regular"), (3, unique), (4, f"{FAMILY} {style}"),
                             (6, ps), (16, FAMILY), (17, style)):
        name.setName(value, record_id, 3, 1, 0x409)
    name.removeNames(platformID=1)
    font.save(path)


def main():
    for path in sorted(Path(sys.argv[1]).glob("MedeoPixel-*.ttf")):
        rename(path)


if __name__ == "__main__":
    main()
