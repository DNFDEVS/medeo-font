"""Exit 1 if a Font Bakery JSON report has a FAIL, ERROR or FATAL outside the allowed list.

Allowed: the three ELSH checks Medeo Pixel shares with the Geist Pixel Google Fonts publishes (fvar instances and
STAT names Square, Circle, Grid, Triangle, Line that the axis registry does not list).

Usage: python -I scripts/fontbakery_gate.py report.json [...]
"""
import json
import re
import sys

ALLOWED = {
    ("MedeoPixel[ELSH].ttf", "googlefonts/STAT/axisregistry"),
    ("MedeoPixel[ELSH].ttf", "googlefonts/fvar_instances"),
    ("MedeoPixel[ELSH].ttf", "opentype/fvar/regular_coords_correct"),
}
bad = []
for path in sys.argv[1:]:
    for section in json.load(open(path))["sections"]:
        for check in section["checks"]:
            if check["result"] not in ("FAIL", "ERROR", "FATAL"):
                continue
            name = (check.get("filename") or "family").split("/")[-1]
            cid = re.sub(r"<FontBakeryCheck:(.*)>", r"\1", check["key"][1])
            if (name, cid) not in ALLOWED:
                bad.append(f"{check['result']} {cid} {name}")
print("\n".join(bad) or "Font Bakery: no FAIL outside the allowed list")
sys.exit(1 if bad else 0)
