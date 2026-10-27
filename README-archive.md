![Medeo: open fonts for Latin and Cyrillic](https://prtner.ai/font/media/og.jpg)

# Medeo.RC4

Medeo is a free font family for Latin and Cyrillic by [DNF](https://dnf.dev), made for [prtner.ai](https://prtner.ai). RC4 is a release candidate. Try the fonts at [prtner.ai/font](https://prtner.ai/font).

- **Medeo Sans** for interfaces and text. Weight 100–900, upright and italic.
- **Medeo Mono** for code and aligned columns. Weight 100–900, upright and italic.
- **Medeo Pixel** for display text. Five pixel shapes: Square, Circle, Grid, Triangle, and Line.

Each family covers the alphabets of 759 languages in the Google Fonts language dataset. This count describes alphabet coverage, not a linguistic review. See [LANGUAGES.md](LANGUAGES.md).

## Sans and Sans Display

Medeo Sans is spaced for text. Medeo Sans Display has tighter spacing for headings and large type. The variable Sans font includes both through its optical-size axis, `opsz` 14–32. Browsers select the optical size automatically unless you override it.

The desktop archive also includes separate static Sans and Sans Display families. Choose Sans for body text and Display for headings.

## Install

For a website or Next.js project:

```sh
npm install medeo-font@1.0.0-rc.4.1
```

For CSS and Next.js examples, see the [npm package documentation](https://www.npmjs.com/package/medeo-font).

For desktop use, open and install the TTF files you need. Each family's folder contains:

- `variable/`: a font with adjustable weight, optical size, or pixel shape.
- `ttf/`: individual styles for apps that need static fonts.
- `webfonts/`: browser font files.

Medeo Sans Display static fonts are in `fonts/MedeoSans/ttf/` alongside Sans.

## Figures

Medeo Pixel uses proportional figures by default. For clocks, counters, and aligned columns, enable tabular figures. All ten digits then have the same width in every Pixel shape.

```css
.counter { font-variant-numeric: tabular-nums; }
```

Sans has a plain zero by default and a slashed zero with `ss09`. Mono and Pixel have a slashed zero by default and a plain zero with `ss09`.

## Outlines and print

For outlined lettering and print export, choose the static Sans, Sans Display, or Mono files. Their overlapping letter parts are merged. If you convert a variable font to paths, unite the paths before adding an outline stroke. Pixel keeps its individual pixel elements.

## What changed in RC4

RC4 expands language coverage, corrects letterforms and spacing, adds small-size alignment to the Sans and Mono variable fonts, and includes static desktop fonts. See [CHANGELOG.md](CHANGELOG.md) for the release notes.

## License and credits

Medeo uses the [SIL Open Font License 1.1](OFL.txt). You can use it in personal and commercial projects.

Medeo is a Modified Version of [Geist](https://github.com/vercel/geist-font) by Vercel and Basement Studio, Copyright 2024 and 2026 The Geist Project Authors. Medeo Sans also uses letters and spacing from [Inter](https://github.com/rsms/inter) by Rasmus Andersson, Copyright 2016 The Inter Project Authors. Both use the same license. Attribution and font changes are recorded in [FONTLOG.txt](FONTLOG.txt).

Source files and build instructions: [Medeo repository](https://github.com/DNFDEVS/medeo-font).
