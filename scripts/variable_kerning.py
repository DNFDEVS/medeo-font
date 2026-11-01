"""Variable Medeo Sans: the kerning lookup stored as classes plus exceptions (scripts/kerncodec.py).

The kerning is evaluated at every master of the design space; its values become class and exception values with
variation deltas in the font's own variation store. Marks, anchors and every other table stay as they were. The
web fonts are made from these files (scripts/webfonts.py).

Usage: python -I scripts/variable_kerning.py out/build/fonts
"""
import io
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kerncodec import recode_variable  # noqa: E402


def main():
    paths = sorted(Path(sys.argv[1]).glob("MedeoSans/variable/*.ttf"))
    if len(paths) != 2:
        raise SystemExit(f"expected two Medeo Sans variable fonts, found {len(paths)}")
    for path in paths:
        font = TTFont(path)
        stats = recode_variable(font, str(path))
        buf = io.BytesIO()
        font.save(buf)
        path.write_bytes(buf.getvalue())
        print(path.name, stats, flush=True)


if __name__ == "__main__":
    main()
