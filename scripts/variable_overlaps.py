"""Mark variable outlines for rasterizers that require overlap flags."""

import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import setMacOverlapFlags


def main():
    paths = sorted(Path(sys.argv[1]).glob("*/variable/*.ttf"))
    if not paths:
        raise SystemExit("No variable TTF files found")
    for path in paths:
        font = TTFont(path, recalcTimestamp=False)
        setMacOverlapFlags(font["glyf"])
        font.save(path)
        print(path.name)


if __name__ == "__main__":
    main()
