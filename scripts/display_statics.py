"""Static Medeo Sans Display: for every text static of Medeo Sans (opsz 14, built from the sources), the same weight cut
from the variable font at opsz 32, the display end of the optical size axis. Names and style flags come from the
text static, with the family «Medeo Sans Display»; overlaps are removed and the font is hinted with ttfautohint as
the text statics are.

Usage: python -I scripts/display_statics.py fonts/MedeoSans
"""
import io
import sys
from pathlib import Path

import ttfautohint
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import OverlapMode, instantiateVariableFont

FAMILY, DISPLAY = "Medeo Sans", "Medeo Sans Display"
OPSZ = 32


def cut(text_static, variable, out):
    text = TTFont(text_static)
    weight = text["OS/2"].usWeightClass
    font = instantiateVariableFont(TTFont(variable), {"wght": weight, "opsz": OPSZ}, overlap=OverlapMode.REMOVE)
    for table in ("STAT", "MVAR", "HVAR", "avar"):
        if table in font:
            del font[table]
    name = font["name"]
    name.names = []
    for record in text["name"].names:
        value = record.toUnicode()
        if record.nameID in (1, 3, 4, 16, 18):
            value = value.replace(FAMILY, DISPLAY)
        if record.nameID in (3, 6):
            value = value.replace("MedeoSans-", "MedeoSansDisplay-")
        name.setName(value, record.nameID, record.platformID, record.platEncID, record.langID)
    for field in ("usWeightClass", "fsSelection"):
        setattr(font["OS/2"], field, getattr(text["OS/2"], field))
    font["head"].macStyle = text["head"].macStyle
    font["head"].created = text["head"].created
    font["head"].modified = text["head"].modified
    raw = io.BytesIO()
    font.save(raw)
    hinted = ttfautohint.ttfautohint(in_buffer=raw.getvalue())
    hinted_font = TTFont(io.BytesIO(hinted), recalcTimestamp=False)
    hinted_font["head"].modified = text["head"].modified
    hinted_font.save(out)


def main():
    root = Path(sys.argv[1])
    variables = {False: root / "variable" / "MedeoSans[opsz,wght].ttf",
                 True: root / "variable" / "MedeoSans-Italic[opsz,wght].ttf"}
    for text_static in sorted((root / "ttf").glob("MedeoSans-*.ttf")):
        italic = bool(TTFont(text_static)["OS/2"].fsSelection & 1)
        out = text_static.with_name(text_static.name.replace("MedeoSans-", "MedeoSansDisplay-"))
        cut(text_static, variables[italic], out)


if __name__ == "__main__":
    main()
