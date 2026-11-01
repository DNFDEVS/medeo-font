"""Print the CHANGELOG.md section of the version being released, for the GitHub release notes; exit 1 when the
section is missing or still says «unreleased».

Since 1.0.0 a section is headed by the npm version, «## 1.0.0 — <date>», as CHANGELOG.md says. Older sections
used the font version: npm 1.0.0-rc.4 was «## 1.000-rc4 — <date>» (as in release_version.py), and a package-only
release with a fourth number (1.0.0-rc.2.1) was «## npm 1.0.0-rc.2.1 — <date>»; both forms are still found.

Usage: python -I scripts/release_notes.py <package.json> <CHANGELOG.md>
"""
import json
import re
import sys

npm = json.load(open(sys.argv[1]))["version"]
m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)(?:-rc\.(\d+)(\.\d+)?)?", npm)
if not m:
    sys.exit(f"npm version {npm} is not X.Y.Z or X.Y.Z-rc.N[.M]")
major, minor, patch, rc, package_only = m.groups()
title = f"npm {npm}" if package_only else f"{major}.{int(minor) * 100 + int(patch):03d}" + (f"-rc{rc}" if rc else "")
text = open(sys.argv[2], encoding="utf-8").read()
# Since 1.0.0 the headings are the npm version («## 1.0.0 — <date>»); older sections used the font version.
for heading in (npm, title):
    section = re.search(rf"^## {re.escape(heading)} — ([^\n]+)\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if section:
        title = heading
        break
if not section:
    sys.exit(f"CHANGELOG.md has no section «## {npm} — <date>» or «## {title} — <date>»")
if section.group(1).strip() in ("unreleased", "not released yet"):
    sys.exit(f"CHANGELOG.md: {title} is still «unreleased»; give it the release date")
print(section.group(2).strip())
