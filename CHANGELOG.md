# Changelog

What changes for people who use Medeo, release by release. Font versions map to npm versions as `1.000-rc4` → `1.0.0-rc.4.1`. The languages each family supports are listed in [LANGUAGES.md](LANGUAGES.md); how the fonts are made, and what changed in their glyphs, features and spacing, is in [FONTLOG.txt](FONTLOG.txt).

## npm 1.0.0-rc.4.1 — 2026-10-28

Font version: 1.000-rc4.

- Expanded Latin and Cyrillic coverage: all three families cover the alphabets of 759 languages in Google Fonts language data. Added letters, combining marks, Pinyin and localized Serbian and Macedonian italics. See [LANGUAGES.md](LANGUAGES.md).
- Revised Sans kerning for text and display sizes, with consistent spacing for Latin and Cyrillic letters that share the same shapes.
- Corrected Kazakh and other letterforms, including the descender joins in Sans and Mono and the Cyrillic body of Pixel қ in all five shapes.
- Added small-size pixel alignment to variable Sans and Mono, upright and italic.
- Added tabular figures to Pixel for clocks, counters and aligned columns; proportional figures remain the default.
- Added static desktop fonts: Sans, Sans Display and Mono in 18 styles each, plus five Pixel shapes. Static Sans and Mono have merged outlines for print and outline strokes.
- Improved accents, zero options, currency signs and feature combinations across the families.

## 1.000-rc3 — 2026-10-25
- Medeo Pixel loads in Safari and every iPhone browser: its pixels are components of one glyph again, and the font is 0.4 MB instead of 5.4 MB.

## 1.000-rc2 — 2026-10-25
- The optical size axis is built from the sources.
- Medeo Pixel: Ђ Љ Њ Ћ Џ Җ and their lowercase; Serbian, Bosnian and Turkmen Cyrillic are fully covered.
- DNF holds the copyright; the font moved to this repository, and npm `medeo-font` is published from here.

## 1.000-rc1 — 2026-10-25
- The first public release candidate: Medeo Sans, Medeo Mono and Medeo Pixel, one version for all three. npm package `medeo-font`, CSS from a CDN and a ZIP with the TTF files.
