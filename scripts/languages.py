"""Lists the languages each Medeo family supports, from the built fonts and the Google Fonts language data.

A language is listed when every base letter and every mark of its alphabet in gflanguages is in the cmap of every
style of the family, upright and italic (the dotted circle that gflanguages writes before a mark is a placeholder,
not a requirement), and every letter-and-mark cluster of the alphabet (written in braces, like {ɛ́}) shapes with
its marks attached: at the sampled weights, optical sizes and Pixel shapes, a mark above overlaps the letter
or the preceding upper mark horizontally and sits above its ink. A mark below sits under the letter;
an attached-below mark may join it. Nothing is .notdef, and no ink
is cut off by the clipping lines (winAscent, winDescent). Clusters are shaped with the language's tag, so its
localized forms (Dutch IJ, Serbian, Romanian) are the ones checked. Historical languages are left
out. Writes LANGUAGES.md and packages/medeo-font/dist/languages.json; with --check, exits 1 when either
file differs from what the fonts give.

Usage: python -I scripts/languages.py [--check]
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

import gflanguages
import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
# a family supports a language only when every style of it does (upright and italic)
FAMILIES = {
    "Medeo Sans": ["fonts/MedeoSans/variable/MedeoSans[opsz,wght].ttf",
                   "fonts/MedeoSans/variable/MedeoSans-Italic[opsz,wght].ttf"],
    "Medeo Mono": ["fonts/MedeoMono/variable/MedeoMono[wght].ttf",
                   "fonts/MedeoMono/variable/MedeoMono-Italic[wght].ttf"],
    "Medeo Pixel": ["fonts/MedeoPixel/variable/MedeoPixel[ELSH].ttf"],
}
SCRIPTS = {"Latn": "Latin", "Cyrl": "Cyrillic"}
LOCATIONS = {  # the ends of the axes where marks sit highest, widest and tightest
    "Medeo Sans": [{"wght": w, "opsz": o} for w in (100, 400, 900) for o in (14, 32)],
    "Medeo Mono": [{"wght": w} for w in (100, 400, 900)],
    "Medeo Pixel": [{"ELSH": shape} for shape in (0, 1, 20, 40, 60, 80)],
}
SLACK = 0.01  # em: how far a mark may reach into the ink it sits on before it counts as a collision


class Style:
    """One font file shaped with HarfBuzz at a design location, with the ink box of every glyph."""

    def __init__(self, path, location):
        self.font = TTFont(path)
        self.upm = self.font["head"].unitsPerEm
        self.order = self.font.getGlyphOrder()
        self.glyphs = self.font.getGlyphSet(location=location or None)
        self.hb = hb.Font(hb.Face(hb.Blob.from_file_path(str(path))))
        if location:
            self.hb.set_variations(location)
        self.mark_classes = {name: unicodedata.combining(chr(cp))
                             for cp, name in self.font.getBestCmap().items()
                             if unicodedata.combining(chr(cp))}
        self.boxes = {}
        os2 = self.font["OS/2"]
        self.clip = (-os2.usWinDescent, os2.usWinAscent)  # ink outside these lines is cut off on Windows
        gdef = self.font["GDEF"].table.GlyphClassDef if "GDEF" in self.font else None
        self.marks = {g for g, c in (gdef.classDefs.items() if gdef else []) if c == 3}

    def box(self, name):
        if name not in self.boxes:
            pen = BoundsPen(self.glyphs)
            self.glyphs[name].draw(pen)
            self.boxes[name] = pen.bounds
        return self.boxes[name]

    def cluster_ok(self, text, language=None):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        if language:  # locl lookups (Dutch IJ, Turkish i, Romanian ș…) run as they do in the language's text
            buf.language = language
        buf.cluster_level = hb.BufferClusterLevel.MONOTONE_CHARACTERS  # one cluster per character, so marks are known
        hb.shape(self.hb, buf)
        names = [self.order[i.codepoint] for i in buf.glyph_infos]
        if ".notdef" in names:
            return False
        slack = SLACK * self.upm
        x = 0
        base = None
        above = None
        for info, pos, name in zip(buf.glyph_infos, buf.glyph_positions, names):
            b = self.box(name)
            x0 = x + pos.x_offset
            x += pos.x_advance
            if not b:
                continue
            box = (b[0] + x0, b[1] + pos.y_offset, b[2] + x0, b[3] + pos.y_offset)
            if box[1] < self.clip[0] - slack or box[3] > self.clip[1] + slack:
                return False  # a stack that rises above the ascent line (or under the descent) is clipped
            cls = unicodedata.combining(text[info.cluster]) if info.cluster < len(text) else 0
            # HarfBuzz can merge a mark into a precomposed letter's cluster.
            cls = self.mark_classes.get(name, cls)
            if (cls == 0 and name not in self.marks) or base is None:  # a letter (a digraph like íj́ has two)
                base, above = box, box
                continue
            if cls == 0:  # a mark split off a precomposed letter by ccmp: above or below by where it stands
                cls = 230 if box[1] + box[3] > base[1] + base[3] else 220
            support = above if cls >= 230 else base
            if box[2] < support[0] - slack or box[0] > support[2] + slack:
                return False  # detached from the letter or the preceding upper mark
            if cls >= 230:  # above: over the letter's ink and over the previous mark
                if box[1] < above[3] - slack:
                    return False
                above = box
            elif cls == 202:  # attached below: the join may overlap, the body must stay below
                # A descender can extend below the attachment at the baseline.
                if (box[1] + box[3]) / 2 > max(base[1], 0) + slack:
                    return False
            elif cls == 220 and box[3] > base[1] + slack:  # below
                return False
        return True


def needed(exemplars):
    chars = set("".join((exemplars.base + " " + exemplars.marks).split())) - set("{}◌")
    return {c for c in chars if not unicodedata.category(c).startswith("Z")}


def clusters(exemplars):
    return [c for c in re.findall(r"\{([^}]+)\}", exemplars.base) if any(unicodedata.combining(ch) for ch in c)]


def supported():
    languages = gflanguages.LoadLanguages()
    cmaps = {family: set.intersection(*(set(TTFont(ROOT / p).getBestCmap()) for p in paths))
             for family, paths in FAMILIES.items()}
    styles = {family: [Style(ROOT / p, loc) for p in paths for loc in LOCATIONS[family]]
              for family, paths in FAMILIES.items()}
    shaped = {}

    def shapes(family, cluster, language):
        if (family, cluster, language) not in shaped:
            shaped[family, cluster, language] = all(style.cluster_ok(cluster, language) for style in styles[family])
        return shaped[family, cluster, language]

    rows = []
    for lid, lang in sorted(languages.items()):
        if lang.historical or lang.script not in SCRIPTS or not lang.exemplar_chars.base:
            continue
        need = needed(lang.exemplar_chars)
        families = [f for f, cmap in cmaps.items() if all(ord(c) in cmap for c in need)
                    and all(shapes(f, c, lang.language) for c in clusters(lang.exemplar_chars))]
        if families:
            rows.append({"id": lid, "name": lang.name, "autonym": lang.autonym, "script": SCRIPTS[lang.script],
                         "families": families})
    return rows


def markdown(rows):
    def count(family, script=None):
        return sum(1 for r in rows if family in r["families"] and (script is None or r["script"] == script))

    out = ["# Languages", ""]
    for family in FAMILIES:
        out.append(f"- **{family}**: {count(family)} languages, {count(family, 'Latin')} in Latin and "
                   f"{count(family, 'Cyrillic')} in Cyrillic.")
    out += ["", "A language is listed when the letters and marks in its alphabet in Google Fonts language data "
            f"(gflanguages {gflanguages.__version__}) are covered by every style in a family. "
            "Letter-and-mark clusters are also checked when shaped. This is a coverage check against that dataset, "
            "not a linguistic review. A dash in the Autonym column means the name is unavailable in the dataset.", ""]
    for script in ("Cyrillic", "Latin"):
        out += [f"## {script}", "", "| Language | Autonym | Sans | Mono | Pixel |", "| --- | --- | :-: | :-: | :-: |"]
        for r in sorted((r for r in rows if r["script"] == script), key=lambda r: r["name"]):
            marks = " | ".join("✓" if f in r["families"] else "—" for f in FAMILIES)
            out.append(f"| {r['name']} | {r['autonym'] or '—'} | {marks} |")
        out.append("")
    return "\n".join(out)


def main():
    rows = supported()
    files = {
        ROOT / "LANGUAGES.md": markdown(rows),
        ROOT / "packages/medeo-font/dist/languages.json": json.dumps(rows, ensure_ascii=False, indent=1) + "\n",
    }
    if "--check" in sys.argv:
        stale = [p.relative_to(ROOT) for p, text in files.items() if not p.exists() or p.read_text() != text]
        print("\n".join(f"{p} differs from the fonts; run scripts/languages.py" for p in stale) or "languages: up to date")
        sys.exit(1 if stale else 0)
    for path, text in files.items():
        path.write_text(text)
    print("\n".join(markdown(rows).split("\n")[2:5]))


if __name__ == "__main__":
    main()
