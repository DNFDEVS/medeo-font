"""Static Medeo Sans Display: for every text static of Medeo Sans, the same weight cut from the variable font at opsz 32,
the display end of the optical size axis. Names, stylistic set names and style flags come from the text static, with
the family «Medeo Sans Display»; overlaps are removed, the kerning is stored as classes plus exceptions and the font
is hinted with ttfautohint, as the text statics are (scripts/static_instances.py).

Usage: python -I scripts/display_statics.py fonts/MedeoSans
"""
import os
import sys
from multiprocessing import Pool
from pathlib import Path

from fontTools.ttLib import TTFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from static_instances import cut_static  # noqa: E402

FAMILY, DISPLAY = "Medeo Sans", "Medeo Sans Display"
OPSZ = 32
RENAME = ((FAMILY, DISPLAY, (1, 3, 4, 16, 18)), ("MedeoSans-", "MedeoSansDisplay-", (3, 6)))


def cut(args):
    text_static, variable, out = args
    text = TTFont(text_static)
    location = {"wght": text["OS/2"].usWeightClass, "opsz": OPSZ}
    font, stats = cut_static(variable, text, location, kern=True, rename=RENAME)
    font.save(out)
    return Path(out).name, stats


def main():
    root = Path(sys.argv[1])
    variables = {False: root / "variable" / "MedeoSans[opsz,wght].ttf",
                 True: root / "variable" / "MedeoSans-Italic[opsz,wght].ttf"}
    jobs = []
    for text_static in sorted((root / "ttf").glob("MedeoSans-*.ttf")):
        italic = bool(TTFont(text_static)["OS/2"].fsSelection & 1)
        out = text_static.with_name(text_static.name.replace("MedeoSans-", "MedeoSansDisplay-"))
        jobs.append((str(text_static), str(variables[italic]), str(out)))
    with Pool(min(8, os.cpu_count() or 1)) as pool:
        for name, stats in pool.imap_unordered(cut, jobs):
            print(name, stats, flush=True)


if __name__ == "__main__":
    main()
