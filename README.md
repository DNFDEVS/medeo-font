![Medeo: open fonts for Latin and Cyrillic](https://prtner.ai/font/media/og.jpg)

# Medeo

Medeo is an open type family for Latin and Cyrillic by [DNF](https://dnf.dev), made first for
[prtner.ai](https://prtner.ai). Specimen, tester and downloads: [prtner.ai/font](https://prtner.ai/font).

- **Medeo Sans** — a sans-serif for interfaces and running text. Axes: weight 100–900 and optical size 14–32
  (browsers set the optical size from the font size). Upright and italic.
- **Medeo Mono** — the monospaced companion, for code and for tables where figures line up. Weight 100–900,
  upright and italic.
- **Medeo Pixel** — a display face on a pixel grid. One axis, `ELSH`, sets the dot shape: Square, Circle, Grid,
  Triangle, Line.

Languages: English, Russian, Kazakh (Cyrillic and the 2021 Latin), Ukrainian, Uzbek (Latin and Cyrillic), Kyrgyz,
Tajik, Turkmen, Azerbaijani and Turkish.

## Use

- **npm:** `npm install medeo-font`. Exports for `next/font` and plain CSS: see
  [packages/medeo-font](packages/medeo-font/README.md).
- **CDN:** `<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/medeo-font@VERSION/dist/medeo.css">`
- **Desktop:** the ZIP of every [release](https://github.com/DNFDEVS/medeo-font/releases) holds the TTF files.

## Build

```sh
make build   # fonts/ from sources/ with gftools builder, then the web fonts
make test    # Font Bakery, googlefonts profile
make check   # the committed fonts equal a fresh build
```

Python 3.12. Releases are built by CI from a tag (`vX.Y.Z`): the npm version `1.0.0` is font version 1.000,
`1.0.1` is 1.001, and `1.0.0-rc.2` is 1.000-rc2.

## Layout

- `sources/` — the Glyphs sources and gftools configs: the only source of the fonts.
- `fonts/` — the built fonts: `variable/` TTF, `webfonts/` WOFF2 (Medeo Pixel: WOFF).
- `packages/medeo-font/` — the npm package.

## License and credits

Medeo is licensed under the [SIL Open Font License 1.1](OFL.txt). It is a Modified Version of
[Geist](https://github.com/vercel/geist-font) by Vercel and Basement Studio (Copyright 2024 The Geist Project
Authors), and Medeo Sans takes letters and spacing from [Inter](https://github.com/rsms/inter) by Rasmus Andersson
(Copyright 2016 The Inter Project Authors), both under the same license. What comes from where is in
[FONTLOG.txt](FONTLOG.txt); the authors are in [AUTHORS.txt](AUTHORS.txt).
