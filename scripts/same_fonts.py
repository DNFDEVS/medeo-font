"""Exit 1 unless two font folders hold the same fonts, table by table.

The release publishes what the repository holds, so the committed fonts/ must equal a fresh build from sources/.
Only head.modified and head.checkSumAdjustment may differ (build time).

Usage: python -I scripts/same_fonts.py <committed fonts dir> <fresh fonts dir>
"""
import pathlib
import sys

from fontTools.ttLib import TTFont

a, b = (pathlib.Path(p) for p in sys.argv[1:3])
names = sorted(p.relative_to(a) for p in a.glob("*/*/*") if p.suffix in (".ttf", ".woff", ".woff2"))
fresh = sorted(p.relative_to(b) for p in b.glob("*/*/*") if p.suffix in (".ttf", ".woff", ".woff2"))
bad = []
if names != fresh:
    bad.append(f"file lists differ: only committed {sorted(set(names) - set(fresh))}, only fresh {sorted(set(fresh) - set(names))}")
for rel in sorted(set(names) & set(fresh)):
    fa, fb = TTFont(a / rel, lazy=True), TTFont(b / rel, lazy=True)
    for f in (fa, fb):
        f["head"].modified = 0
        f["head"].checkSumAdjustment = 0
    tags = sorted((set(fa.keys()) | set(fb.keys())) - {"GlyphOrder"})
    # head is loaded above, so getTableData compiles it with the zeroed fields; other tables compare raw
    diff = [t for t in tags if t not in fa or t not in fb or fa.getTableData(t) != fb.getTableData(t)]
    if diff:
        bad.append(f"{rel}: tables differ {diff}")
print("\n".join(bad) or f"{len(names)} fonts equal")
sys.exit(1 if bad else 0)
