"""Print the CHANGELOG.md section of the version being released, for the GitHub release notes; exit 1 when the
section is missing or still says «unreleased».

npm 1.0.0-rc.4 is the section «## 1.000-rc4 — <date>» (the font version, as in release_version.py); a package-only
release with a fourth number (1.0.0-rc.2.1) is the section «## npm 1.0.0-rc.2.1 — <date>».

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
section = re.search(rf"^## {re.escape(title)} — ([^\n]+)\n(.*?)(?=^## |\Z)", text, re.S | re.M)
if not section:
    sys.exit(f"CHANGELOG.md has no section «## {title} — <date>»")
if section.group(1).strip() == "unreleased":
    sys.exit(f"CHANGELOG.md: {title} is still «unreleased»; give it the release date")
print(section.group(2).strip())
