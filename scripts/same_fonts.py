"""Exit 1 unless two font folders hold the same fonts.

The release publishes what the repository holds, so the committed fonts/ must equal a fresh build from sources/.

Every table must be byte-identical (head.modified and head.checkSumAdjustment, the build time, are ignored), with one
exception: the outlines of static TTFs. Their outlines are interpolated, overlap-merged and rounded by fontTools and
skia-pathops, whose floating point differs between platforms (macOS arm64 and Linux x86-64 give different results
for a few glyphs per font with the same pinned tools). In a static TTF a glyph whose bytes differ still counts as the
same when
  - it has the same contours with every point within 1 unit, in any contour order and from any start point, or
  - its filled area differs from the committed one by at most 0.1 % (at least 100 square units), which covers a
    redundant point on a straight segment;
its instructions are then not compared (ttfautohint follows the points). The `loca` offsets follow `glyf`, and
`post` is compared by its fields and glyph names rather than by the order of its name strings. Every glyph accepted
this way is listed, so platform noise stays visible. Variable fonts and web fonts are compared byte for byte.

Families named with --layout-by-effect have their layout tables (GDEF, GSUB, GPOS) compared by what a shaper does
with them (scripts/layout_effect.py) instead of byte for byte: the same substitutions per script, language and feature
in the same order, the same adjustment for every glyph pair, the same offset for every mark. Every other table of
those fonts is still compared byte for byte. This is for a family whose committed fonts were compiled by other tools
than the build, so the lookups are numbered and packed differently.

Families that the build does not make are named with --not-built; their files are listed and not compared. Any other
family that exists on one side only fails the check.

Usage: python -I scripts/same_fonts.py <committed fonts dir> <fresh fonts dir> [--not-built Family ...]
       [--layout-by-effect Family ...]
"""
import argparse
import pathlib
import sys

import pathops
from fontTools.ttLib import TTFont

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import layout_effect  # noqa: E402

LAYOUT = ("GDEF", "GSUB", "GPOS")

POINT_TOLERANCE = 1
AREA_SHARE, AREA_MIN = 0.001, 100


def contours(font, name):
    glyf = font["glyf"]
    coords, ends, flags = glyf[name].getCoordinates(glyf)
    out, start = [], 0
    for end in ends:
        out.append([(*coords[i], flags[i] & 1) for i in range(start, end + 1)])
        start = end + 1
    return out


def close(a, b):
    """Same points within the tolerance, from some start point of b."""
    if len(a) != len(b):
        return False
    n = len(b)
    return any(all(p[2] == q[2] and abs(p[0] - q[0]) <= POINT_TOLERANCE and abs(p[1] - q[1]) <= POINT_TOLERANCE
                   for p, q in zip(a, b[r:] + b[:r])) for r in range(n))


def same_points(fa, fb, name):
    a, b = contours(fa, name), contours(fb, name)
    if len(a) != len(b):
        return False
    left = list(b)
    for ca in a:
        match = next((cb for cb in left if close(ca, cb)), None)
        if match is None:
            return False
        left.remove(match)
    return True


def area_path(font, name):
    path = pathops.Path()
    font.getGlyphSet()[name].draw(path.getPen())
    return path


def same_area(fa, fb, name):
    a, b = area_path(fa, name), area_path(fb, name)
    xor = pathops.op(a, b, pathops.PathOp.XOR)
    return abs(xor.area) <= max(AREA_MIN, AREA_SHARE * abs(a.area))


def glyph_bytes(font, name):
    return font["glyf"][name].compile(font["glyf"])


def compare_static_glyphs(fa, fb):
    """Problems and the glyphs accepted within the tolerance."""
    if fa.getGlyphOrder() != fb.getGlyphOrder():
        return ["glyph order differs"], []
    bad, near = [], []
    for name in fa.getGlyphOrder():
        if glyph_bytes(fa, name) == glyph_bytes(fb, name):
            continue
        ga, gb = fa["glyf"][name], fb["glyf"][name]
        if ga.isComposite() or gb.isComposite() or not ga.numberOfContours or not gb.numberOfContours:
            bad.append(name)
        elif same_points(fa, fb, name) or same_area(fa, fb, name):
            near.append(name)
        else:
            bad.append(name)
    return ([f"glyphs differ: {' '.join(bad[:20])}{' …' if len(bad) > 20 else ''} ({len(bad)})"] if bad else []), near


def same_post(fa, fb):
    a, b = fa["post"], fb["post"]
    fields = ("formatType", "italicAngle", "underlinePosition", "underlineThickness", "isFixedPitch",
              "minMemType42", "maxMemType42", "minMemType1", "maxMemType1")
    return all(getattr(a, f) == getattr(b, f) for f in fields) and fa.getGlyphOrder() == fb.getGlyphOrder()


def compare(path_a, path_b, by_effect=False):
    fa, fb = TTFont(path_a, lazy=True), TTFont(path_b, lazy=True)
    for f in (fa, fb):
        f["head"].modified = 0
        f["head"].checkSumAdjustment = 0
    tags = sorted((set(fa.keys()) | set(fb.keys())) - {"GlyphOrder"})
    diff = [t for t in tags if t not in fa or t not in fb or fa.getTableData(t) != fb.getTableData(t)]
    static = "fvar" not in fa and "glyf" in fa and path_a.suffix == ".ttf"
    problems, near = [], []
    if static and "glyf" in diff:
        problems, near = compare_static_glyphs(fa, fb)
        diff = [t for t in diff if t not in ("glyf", "loca")]
    if static and "post" in diff and same_post(fa, fb):
        diff.remove("post")
    layout_notes = []
    if by_effect and any(t in diff for t in LAYOUT):
        diff = [t for t in diff if t not in LAYOUT]
        layout_problems, layout_notes = layout_effect.compare(fa, fb)
        problems += layout_problems
        layout_notes.append("layout compared by effect" + (", same" if not layout_problems else ""))
    if diff:
        problems.insert(0, f"tables differ {diff}")
    return problems, near, layout_notes


def fonts_in(root):
    return {p.relative_to(root) for p in root.glob("*/*/*") if p.suffix in (".ttf", ".woff", ".woff2")}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("committed", type=pathlib.Path)
    ap.add_argument("fresh", type=pathlib.Path)
    ap.add_argument("--not-built", nargs="*", default=[], metavar="FAMILY")
    ap.add_argument("--layout-by-effect", nargs="*", default=[], metavar="FAMILY")
    a = ap.parse_args()
    committed, fresh = fonts_in(a.committed), fonts_in(a.fresh)
    skipped = {p for p in committed if p.parts[0] in a.not_built}
    committed -= skipped
    bad, notes = [], []
    if committed != fresh:
        bad.append(f"file lists differ: only committed {sorted(map(str, committed - fresh))}, "
                   f"only fresh {sorted(map(str, fresh - committed))}")
    for rel in sorted(committed & fresh):
        problems, near, layout_notes = compare(a.committed / rel, a.fresh / rel, rel.parts[0] in a.layout_by_effect)
        bad += [f"{rel}: {p}" for p in problems]
        if near:
            notes.append(f"{rel}: {len(near)} glyphs within the outline tolerance: {' '.join(near[:12])}"
                         + (" …" if len(near) > 12 else ""))
        notes += [f"{rel}: {n}" for n in layout_notes]
    for family in a.not_built:
        files = sorted(p for p in skipped if p.parts[0] == family)
        notes.append(f"{family}: not built from sources, {len(files)} files not compared")
    print("\n".join(notes + bad))
    print(f"{len(bad)} problems" if bad else f"{len(committed & fresh)} fonts equal")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
