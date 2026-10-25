"""Exit 1 unless the tag, the npm version and the version inside every font agree.

npm 1.0.0 is font 1.000, 1.0.1 is 1.001, 1.1.0 is 1.100; npm 1.0.0-rc.2 is font 1.000-rc2. A fourth number
(1.0.0-rc.2.1) is a package-only release: the fonts keep 1.000-rc2.

Usage: python -I scripts/release_version.py <tag> <package.json> <fonts dir>
"""
import json
import pathlib
import re
import sys

from fontTools.ttLib import TTFont

tag, package, fonts = sys.argv[1], sys.argv[2], pathlib.Path(sys.argv[3])
npm = json.load(open(package))["version"]
m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-rc\.(\d+)(?:\.\d+)?)?", npm)
if not m:
    sys.exit(f"npm version {npm} is not X.Y.Z or X.Y.Z-rc.N[.M]")
major, minor, patch, rc = m.groups()
expected = f"Version {major}.{int(minor) * 100 + int(patch):03d}" + (f"-rc{rc}" if rc else "")
bad = [] if tag == f"v{npm}" else [f"tag {tag} is not v{npm}"]
for ttf in sorted(fonts.glob("*/variable/*.ttf")):
    got = TTFont(ttf, lazy=True)["name"].getDebugName(5)
    if got != expected:
        bad.append(f"{ttf.name}: {got}, expected {expected}")
print("\n".join(bad) or f"{tag}: npm {npm}, fonts {expected}")
sys.exit(1 if bad else 0)
