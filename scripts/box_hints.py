"""Medeo Mono: let the box-drawing strokes and blocks reach the line of consoles that size it by the Windows metrics.

The solid glyphs of U+2500-259F (strokes, corners, blocks) end on the standard line, the hhea ascent and descent: the
line of macOS, Linux, the browsers and Windows Terminal, where stacked rows join without a gap. A console that uses the
GDI sizes its line by usWinAscent and usWinDescent instead, rounded to whole pixels, and that line is taller, so a gap
shows between the rows.

This step appends a short run of instructions to the program of each such glyph: put the points at the top and the
bottom end of the glyph on the console's line, usWinAscent and usWinDescent at the current size, rounded to whole
pixels as the console rounds them. The run is guarded by GETINFO: it only runs in a rasterizer that does not report
ClearType sub-pixel positioning. The Windows GDI never positions glyphs at sub-pixel offsets; DirectWrite's natural
modes and the default interpreter of FreeType (version 40) report it and keep the standard line, as do unhinted
outlines (macOS, the web fonts, the variable fonts).

The instructions go after the ttfautohint program, which is kept as it is. That program leaves the zone pointers on the
twilight zone and may leave a rounding state other than the default, so the run first sets round-to-grid and points the
zones at the glyph.

The dashed lines, the diagonals and the shades are patterns tuned to the standard line and are left alone.
Only the static TTFs are touched; the variable fonts ship without hinting.

Usage: python -I scripts/box_hints.py out/build/fonts/MedeoMono/ttf
"""
import sys
from pathlib import Path

from fontTools.ttLib import TTFont

RTG, SZPS, PUSHB1, PUSHW1 = 0x18, 0x16, 0xB0, 0xB8
SVTCA_Y, SVTCA_X, MPPEM, MUL, DIV, ROUND, NEG, SCFS = 0x00, 0x01, 0x4B, 0x63, 0x62, 0x68, 0x65, 0x48
GETINFO, NOT, IF, EIF = 0x88, 0x5C, 0x58, 0x59
SUBPIXEL_POSITIONED_SELECTOR = 1024
FIRST, LAST = 0x2500, 0x259F
# patterns tuned to the standard line are left alone: the dashed lines, the diagonals and the shades
SKIP = set(range(0x2504, 0x250C)) | set(range(0x254C, 0x2550)) | {0x2571, 0x2572, 0x2573} | {0x2591, 0x2592, 0x2593}


def push_word(value):
    assert 0 < value < 0x8000
    return [PUSHW1, value >> 8, value & 0xFF]


def pixels(units):
    """Leaves size * units / 1000 pixels on the stack, in 26.6 fixed point, without losing precision:
    size * (units * 16) / 64 is an exact integer, and that * 64 / 250 is size * units * 64 / 1000."""
    return [MPPEM] + push_word(units * 16) + [MUL] + push_word(250) + [DIV]


def tail_for(tops, bottoms, win_ascent, win_descent):
    """if the rasterizer does not position glyphs at sub-pixels: round to grid; zone pointers to the glyph zone; y axis;
    each end point to the console's line; back to the x axis."""
    assert max(tops + bottoms) < 256
    code = push_word(SUBPIXEL_POSITIONED_SELECTOR) + [GETINFO, NOT, IF, RTG, PUSHB1, 1, SZPS, SVTCA_Y]
    for point in tops:
        code += [PUSHB1, point] + pixels(win_ascent) + [ROUND, SCFS]
    for point in bottoms:
        code += [PUSHB1, point] + pixels(win_descent) + [ROUND, NEG, SCFS]
    return bytes(code + [SVTCA_X, EIF])


def run(path):
    font = TTFont(path)
    cmap, glyf, os2, hhea = font.getBestCmap(), font["glyf"], font["OS/2"], font["hhea"]
    done, longest = 0, 0
    for cp in range(FIRST, LAST + 1):
        if cp in SKIP:
            continue
        name = cmap.get(cp)
        if name is None or name not in glyf.glyphs:
            continue
        glyph = glyf[name]
        if glyph.isComposite() or glyph.numberOfContours <= 0:
            continue
        ys = [y for _, y in glyph.coordinates]
        top, bottom = max(ys), min(ys)
        tops = [i for i, y in enumerate(ys) if y == top] if top >= hhea.ascent else []
        bottoms = [i for i, y in enumerate(ys) if y == bottom] if bottom <= hhea.descent else []
        if not tops and not bottoms:
            continue
        old = glyph.program.getBytecode()
        tail = tail_for(tops, bottoms, os2.usWinAscent, os2.usWinDescent)
        if old.endswith(tail):                      # already done
            continue
        glyph.program.fromBytecode(old + tail)
        done += 1
        longest = max(longest, len(old) + len(tail))
    maxp = font["maxp"]
    maxp.maxSizeOfInstructions = max(maxp.maxSizeOfInstructions, longest)
    maxp.maxStackElements = max(maxp.maxStackElements, 8)
    font.save(path)
    return done


def main(directory):
    paths = sorted(Path(directory).glob("*.ttf"))
    if not paths:
        sys.exit(f"no TTF in {directory}")
    for path in paths:
        print(f"{path.name}: {run(path)} glyphs")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
