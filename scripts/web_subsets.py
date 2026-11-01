"""Split the Medeo web fonts by script for CSS unicode-range, so a browser downloads only the files whose
characters occur on the page.

The subsets are cut from the full web fonts that scripts/webfonts.py writes (fonts/<Family>/webfonts/), so they keep
whatever those carry: every axis, every layout feature, the names, Medeo Sans' kerning classes, Medeo Pixel's `prep`.
One file per subset and style:

    <name>.<subset>.woff2    e.g. MedeoSansVariable.cyrillic.woff2, MedeoSansVariable-Italic.latin.woff2

The subsets are the ones the Google Fonts CSS API and Fontsource serve, with Google's unicode-range for each:

    latin, latin-ext, vietnamese, cyrillic, cyrillic-ext

with one change: `cyrillic` also holds the Kazakh letters that Google puts in `cyrillic-ext` (Ғ Қ Ң Ү Һ Ә Ө and
their lowercase), so a Kazakh word comes from one file and keeps its kerning; `cyrillic-ext` holds no character of
`cyrillic`.

and a last file, `symbols`, with every other character of the font (Greek letters used as symbols, arrows,
mathematical and technical signs, box drawing, ...), so the files together hold every character of the full font.

Each file keeps every glyph the layout features reach from its characters, so stylistic sets, localized forms,
fractions and kerning work inside it. A browser shapes each file on its own: kerning and contextual features do not
act between two characters that come from different files, and a combining mark is placed on its letter only when
both are in the same file. Every text subset therefore also carries all of the font's combining marks, as Google
already does for some of them (U+0301 in cyrillic, U+0300-0309 in vietnamese).

Medeo Pixel's subsets are WOFF2 too: its full web font stays WOFF 1.0 only under the file name the npm package has
always loaded (see scripts/webfonts.py).

With --css DIR the package style sheets are written as well: for every DIR/<family>-full.css (one @font-face per
full file), DIR/<family>.css gets one @font-face per subset file with the same descriptors and a unicode-range,
followed by the rest of the full style sheet unchanged.

Usage:
    python -I scripts/web_subsets.py fonts                     # subsets next to the full web fonts
    python -I scripts/web_subsets.py fonts --out packages/medeo-font/dist/fonts --css packages/medeo-font/dist
"""
import argparse
import pathlib
import re

from fontTools import subset as ftsubset
from fontTools.ttLib import TTFont

# The Google Fonts CSS API's unicode-range per subset, in the order its style sheets declare them. Where ranges
# overlap, a browser tries the face declared last first, so latin wins over latin-ext and latin-ext over vietnamese.
SUBSETS = [
    ("cyrillic-ext", "U+0460-052F, U+1C80-1C8A, U+20B4, U+2DE0-2DFF, U+A640-A69F, U+FE2E-FE2F"),
    ("cyrillic", "U+0301, U+0400-045F, U+0490-0491, U+04B0-04B1, U+2116"),
    ("vietnamese", "U+0102-0103, U+0110-0111, U+0128-0129, U+0168-0169, U+01A0-01A1, U+01AF-01B0, U+0300-0301, "
                   "U+0303-0304, U+0308-0309, U+0323, U+0329, U+1EA0-1EF9, U+20AB"),
    ("latin-ext", "U+0100-02BA, U+02BD-02C5, U+02C7-02CC, U+02CE-02D7, U+02DD-02FF, U+0304, U+0308, U+0329, "
                  "U+1D00-1DBF, U+1E00-1E9F, U+1EF2-1EFF, U+2020, U+20A0-20AB, U+20AD-20C4, U+2113, U+2C60-2C7F, "
                  "U+A720-A7FF"),
    ("latin", "U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, "
              "U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD"),
]
# The Kazakh alphabet (gflanguages kk_Cyrl, base and index exemplars) minus Google's cyrillic: Ғ ғ Қ қ Ң ң Ү ү Һ һ
# Ә ә Ө ө. Its other letters (А-Я, Ё, І, Ұ) and its marks are in Google's cyrillic already.
KAZAKH = "U+0492-0493, U+049A-049B, U+04A2-04A3, U+04AE-04AF, U+04BA-04BB, U+04D8-04D9, U+04E8-04E9"
REST = "symbols"
# Combining marks: Combining Diacritical Marks, its Extended and Supplement blocks, Combining Half Marks.
MARKS = "U+0300-036F, U+1AB0-1AFF, U+1DC0-1DFF, U+FE20-FE2F"

FAMILIES = {"MedeoSans": "medeo-sans", "MedeoMono": "medeo-mono", "MedeoPixel": "medeo-pixel",
            "MedeoSerif": "medeo-serif"}


def parse(ranges):
    cps = set()
    for part in ranges.split(","):
        part = part.strip().removeprefix("U+")
        lo, _, hi = part.partition("-")
        cps.update(range(int(lo, 16), int(hi or lo, 16) + 1))
    return cps


def compact(cps):
    out, run = [], None
    for cp in sorted(cps):
        if run and cp == run[1] + 1:
            run[1] = cp
        else:
            run = [cp, cp]
            out.append(run)
    return ", ".join(f"U+{a:04X}" if a == b else f"U+{a:04X}-{b:04X}" for a, b in out)


def subset_ranges():
    """[(subset, its characters)] in CSS order: Google's ranges, the Kazakh letters moved into cyrillic."""
    ranges = {name: parse(r) for name, r in SUBSETS}
    ranges["cyrillic"] |= parse(KAZAKH)
    ranges["cyrillic-ext"] -= ranges["cyrillic"]
    return [(name, ranges[name]) for name, _ in SUBSETS]


def plan(cmap):
    """[(subset, characters in its file, its unicode-range)], in CSS order; the files cover the cmap exactly."""
    marks = cmap & parse(MARKS)
    out, covered = [], set()
    for name, ranges in subset_ranges():
        own = cmap & ranges
        if not own - marks:
            continue
        cps = own | marks
        covered |= cps
        out.append((name, cps, compact(ranges | marks)))
    rest = cmap - covered
    if rest:
        out.insert(0, (REST, rest, compact(rest)))
    return out


def sources(root):
    """(full web font, its name without extension, its package folder) for every family."""
    for family, folder in FAMILIES.items():
        for web in sorted((root / family / "webfonts").glob(f"{family}*")):
            if web.suffix in (".woff2", ".woff") and "." not in web.stem:
                yield web, web.stem, folder


def cut(web, dest, unicodes):
    """Write the characters `unicodes` of the web font `web` to `dest` as WOFF2, with every layout feature and
    script, every glyph those features reach, and every table the full web font keeps."""
    opts = ftsubset.Options()
    opts.layout_features = ["*"]
    opts.layout_scripts = ["*"]
    opts.hinting = True
    opts.notdef_outline = True
    opts.name_IDs = ["*"]
    opts.name_languages = ["*"]
    opts.glyph_names = False
    opts.legacy_kern = True
    opts.no_subset_tables += ["meta"]
    opts.flavor = "woff2"
    font = TTFont(web, recalcTimestamp=False)
    sub = ftsubset.Subsetter(opts)
    sub.populate(unicodes=sorted(unicodes))
    sub.subset(font)
    font.flavor = "woff2"
    font.save(dest)


def write_fonts(root, out=None):
    for web, name, folder in sources(root):
        cmap = set(TTFont(web).getBestCmap())
        dest_dir = web.parent if out is None else out / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
        for subset, cps, _ in plan(cmap):
            dest = dest_dir / f"{name}.{subset}.woff2"
            cut(web, dest, cps)
            print(dest)


FACE = re.compile(r"@font-face\s*\{(.*?)\}", re.S)
SRC = re.compile(r'src:\s*url\("\./fonts/([^/"]+)/([^"]+?)\.(woff2?)"\)\s*format\("[^"]+"\);')


def write_css(root, dist):
    ranges = {}
    for web, name, _ in sources(root):
        cmap = set(TTFont(web).getBestCmap())
        ranges[name] = [(subset, f"{name}.{subset}.woff2", declared) for subset, _, declared in plan(cmap)]
    for full in sorted(dist.glob("*-full.css")):
        css = full.read_text()
        faces = list(FACE.finditer(css))
        if not faces:
            continue
        out = [f"/* Generated by scripts/web_subsets.py from {full.name}: one @font-face per script, so a browser\n"
               f"   downloads only the files for the characters a page uses. {full.name} loads one file per style. */\n"]
        for face in faces:
            body = face.group(1)
            m = SRC.search(body)
            folder, name = m.group(1), m.group(2)
            for subset, file, declared in ranges[name]:
                src = f'src: url("./fonts/{folder}/{file}") format("woff2");'
                block = SRC.sub(lambda _: src, body).rstrip()
                out.append(f"/* {subset} */\n@font-face {{{block}\n  unicode-range: {declared};\n}}\n")
        out.append(css[faces[-1].end():].lstrip("\n"))
        dest = dist / full.name.replace("-full.css", ".css")
        dest.write_text("".join(out))
        print(dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, metavar="DIR",
                    help="write the subsets to DIR/<package folder>/ instead of next to the full web fonts")
    ap.add_argument("--css", type=pathlib.Path, metavar="DIR", help="also write the style sheets in DIR")
    ap.add_argument("--css-only", action="store_true", help="write the style sheets only")
    a = ap.parse_args()
    if not a.css_only:
        write_fonts(a.root, a.out)
    if a.css:
        write_css(a.root, a.css)


if __name__ == "__main__":
    main()
