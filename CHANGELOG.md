# Changelog

What changes for people who use Medeo, release by release. Headings are npm versions; the fonts inside carry the matching font version, such as `1.0.0` → `1.000`. RC4.5 and RC4.6 are steps between npm versions, named as on [prtner.ai/font](https://prtner.ai/font). Supported languages are in [LANGUAGES.md](LANGUAGES.md); how the fonts are made, glyph by glyph, is in [FONTLOG.txt](FONTLOG.txt).

## 1.0.0 — 2026-11-01

Fonts `1.000`. The first stable release; it follows RC4.6.

### Medeo Serif — new family

- A serif for text and headings. One style: Regular.
- Latin is Geist Serif, as drawn, with the same spacing and kerning.
- New Cyrillic, built from Geist Serif's own strokes and serifs.
- Б Д Л Ф З follow PT Serif by ParaType.
- К к Ж ж join the arm and leg with a short bar, as in Medeo Sans and PT Serif.
- Cyrillic sets as tightly as Geist's Latin: pairs around о and others closed up; serifs never touch.
- Serif tips of the Cyrillic lowercase are as thin as the Latin ones.
- Cyrillic ро, сс, ТА are spaced exactly as Latin po, cc, TA.
- Loose Cyrillic pairs closed up (од, об, ёр, ос and others); nothing opens up.
- Fixed ǐ (one mark), a smoother б, straight stems in h ħ ђ.
- Ӄ ӄ: the leg bends into a round hook that reaches the full descender, as in PT Serif.
- Ҕ ҕ redrawn as in PT Serif and Medeo Sans: a bowl under the bar of Г г runs down into a hook; ҕ no longer reads like ŋ.
- The tail of Ҙ ҙ hangs cleanly from the bowl.
- Smooth joins in З з Ӟ ӟ Ɛ ɛ Ӡ ӡ Ҩ ҩ Ҽ ҽ Ҿ ҿ.
- Covers 759 languages, like Sans and Mono.
- Includes the Cyrillic of smaller languages and African Latin letters.
- Currency signs: ₸ ₽ ₴ ₼ ₾ ₺ ₿ and the Belarusian ruble (U+20C5).
- Also № ¢ £ ^.
- Spaces, hyphens and zero-width characters as in Sans.
- Stylistic sets use Medeo's numbers: ss01 a, ss04 R, ss12 k, ss13–ss15 dot shapes, ss16 round letters.
- Stylistic sets switch Cyrillic too.
- No bold or italic yet.

### Medeo Sans

- л Л drawn after Inter: the left leg is as heavy as the stems in every weight; љ Љ ԓ Ԓ follow.
- б drawn after Inter: a larger, more open bowl, close to о.
- Kerning: ку ко ка кс set like ky ko ka kc, and every ж pair like the к pair (жу as ку); он но по like on no; од as in Inter.
- Longer descenders: p, q, y, g, р, у, ф reach Inter's depth.
- Deeper tails on ц, д, щ and similar lowercase letters.
- Hooks of ҕ ҧ ӄ Ӄ Ԓ reach the full descender.
- Ҕ and Ҧ hang lower and no longer read like Б.
- Thinner crossbar of Ө in heavy weights.
- New signs: ₿ ✓ ✔ ★.
- New Belarusian ruble sign (U+20C5).
- New soft hyphen, non-breaking hyphen and zero-width characters.
- More room after Ҕ, Ҧ and italic ӄ in heavy weights.

### Medeo Mono

- New г with a foot serif and spur, like Mono's r; also ѓ ґ ӷ.
- New т with beaks and a foot serif, in the same style; also ҭ.
- The earlier г and т stay available: ss17 "Plain г", ss18 "Plain т".
- More even Cyrillic texture, also with tight tracking: м щ ю are narrower, к ц ь л я and several capitals are re-centred in their cells.
- Longer descenders, at the same depths as Sans.
- Thinner crossbar of Ө in heavy weights.
- New Belarusian ruble sign (U+20C5).
- Stylistic sets also switch the Cyrillic а ӑ ӓ, like a ă ä: ss01 and ss02 upright, ss02 italic.

### Medeo Mono Nerd Font — new set

- Medeo Mono with Nerd Fonts icons, for terminals and prompts.
- Family name `MedeoMono Nerd Font Mono`, 18 styles.
- Every icon fits one cell.
- The icon licences come with the fonts.

### Medeo Pixel

- New Belarusian ruble sign (U+20C5).
- Redrawn ₽: its two crossbars no longer merge.
- Fixed я: its right stem is straight and its leg joins the bowl cleanly.
- Stylistic sets also switch the Cyrillic а ӑ ӓ (ss01, ss02) and І Ї Ӏ (ss05), like the Latin a ă ä and I Ï.

### All families

- Variable fonts ship without hinting, like Inter and Geist; static fonts keep their hinting for Windows apps.
- The fonts now declare Latin and Cyrillic support correctly.
- Medeo Sans Display static fonts show the right names for their stylistic sets.
- Smaller files: the static fonts of Sans, Sans Display and Mono take about 40–60% of their former size and the Sans variable fonts about two thirds, with the same letters, spacing and kerning.

### Licence and docs

- OFL.txt credits ParaType and Google for Medeo Serif.
- README explains tabular figures for prices and columns.

## RC4.6 — 2026-11-01

Fonts `1.000-rc4`, as in 1.0.0-rc.4.1; no new npm version.

- Medeo on a CDN: the style sheets and web fonts of 1.0.0-rc.4.1 at `https://prtner.ai/font/cdn/1.0.0-rc.4.1/`, served by Cloudflare. Files at a version path never change.

## RC4.5 — 2026-10-31

- Medeo Serif 1.0 released on its own on GitHub (tag `medeo-serif-1.0.0`), ahead of the full 1.0.

## 1.0.0-rc.4.1 — 2026-10-28

Fonts `1.000-rc4`. Tag `v1.0.0-rc.4` has the same changes; 1.0.0-rc.4.1 aligns the static fonts with the release build.

### All families

- Cover the alphabets of 759 languages in Google Fonts language data. See [LANGUAGES.md](LANGUAGES.md).
- New letters and combining marks for those languages.
- Pinyin.
- Serbian and Macedonian italic forms.
- Corrected Kazakh and other letterforms.
- Better accents, zero options, currency signs and feature combinations.

### Medeo Sans and Medeo Mono

- Corrected descender joins.
- Small-size pixel alignment in the variable fonts, upright and italic.
- New static desktop fonts: Sans, Sans Display and Mono, 18 styles each.
- Static fonts have merged outlines for print and outline strokes.

### Medeo Sans

- Revised kerning for text and display sizes.
- Latin and Cyrillic letters of the same shape are spaced alike.

### Medeo Pixel

- Tabular figures for clocks, counters and aligned columns.
- Proportional figures stay the default.
- қ uses the Cyrillic к body in all five shapes.
- New static fonts: five pixel shapes.

## 1.0.0-rc.3 — 2026-10-25

Fonts `1.000-rc3`.

### Medeo Pixel

- Loads in Safari and every iPhone browser.
- Its pixels are components of one glyph again.
- The font is 0.4 MB instead of 5.4 MB.

### Medeo Sans and Medeo Mono

- Version number only.

## 1.0.0-rc.2 — 2026-10-25

Fonts `1.000-rc2`. npm 1.0.0-rc.2.1 has the same fonts.

### Medeo Sans

- The optical size axis is built from the sources.

### Medeo Pixel

- New Ђ Љ Њ Ћ Џ Җ and their lowercase.
- Serbian, Bosnian and Turkmen Cyrillic are fully covered.

### Project

- DNF Studio holds the copyright.
- The font moved to this repository.
- npm `medeo-font` is published from here.

## 1.0.0-rc.1 — 2026-10-25

Fonts `1.000-rc1`.

- The first public release candidate: Medeo Sans, Medeo Mono and Medeo Pixel.
- One version for all three families.
- npm package `medeo-font`, CSS from a CDN and a ZIP with the TTF files.
