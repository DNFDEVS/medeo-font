![Medeo: open fonts for Latin and Cyrillic](https://prtner.ai/font/media/og.jpg)

# Medeo

Medeo is a free font family for Latin and Cyrillic by [DNF Studio](https://dnf.dev), made for [prtner.ai](https://prtner.ai). Version 1.0 is the first stable release. Try the fonts at [prtner.ai/font](https://prtner.ai/font).

- **Medeo Sans** for interfaces and text. Weight 100–900, optical size 14–32, upright and italic. Includes Medeo Sans Display for headings.
- **Medeo Serif** for text and headings. One style: Regular.
- **Medeo Mono** for code and aligned columns. Weight 100–900, upright and italic.
- **Medeo Mono Nerd Font**: Medeo Mono with the [Nerd Fonts](https://www.nerdfonts.com) 3.5.1 icons, for terminals, editors and shell themes. Family name `MedeoMono Nerd Font Mono`.
- **Medeo Pixel** for display text. Five pixel shapes: Square, Circle, Grid, Triangle, and Line.

Each family covers the alphabets of 759 languages in the Google Fonts language dataset. This count describes alphabet coverage, not a linguistic review. See [LANGUAGES.md](LANGUAGES.md).

Made by DNF Studio · [dnf.dev](https://dnf.dev) for [prtner.ai](https://prtner.ai).

## Sans and Sans Display

Medeo Sans is spaced for text. Medeo Sans Display has tighter spacing for headings and large type. The variable Sans font includes both through its optical-size axis, `opsz` 14–32. Browsers select the optical size automatically unless you override it.

The static fonts include separate Sans and Sans Display families. Choose Sans for body text and Display for headings.

## Install

For a website or Next.js project:

```sh
npm install medeo-font@1.0.0
```

For CSS and Next.js examples, see [the npm package documentation](packages/medeo-font/README.md).

For desktop use, download the fonts from [GitHub releases](https://github.com/DNFDEVS/medeo-font/releases) and install the TTF files you need. Each family comes in its own folder under `fonts/`. The license (OFL.txt) and this README are in the root of the repository and of the release ZIP; Medeo Mono Nerd Font also keeps the licenses of its icons in `fonts/MedeoMonoNerdFont/licenses/`. Install either the variable or the static fonts of a family, not both.

## Figures

Medeo Sans, Medeo Serif and Medeo Pixel use proportional figures by default. For prices, clocks, counters and aligned columns, enable tabular figures (`tnum`). In Pixel, all ten digits then have the same width in every shape. Medeo Mono is monospaced by default.

```css
.prices { font-variant-numeric: tabular-nums; }
```

## Zero and O, and other stylistic sets

In Medeo Sans the zero is an oval close to O; `ss09` gives a slashed zero to distinguish it from O. Medeo Mono
and Medeo Pixel slash the zero by default, and their `ss09` gives the plain one.

```css
.code, .table { font-feature-settings: "ss09"; } /* Medeo Sans: 0 distinct from O */
```

| Set | Medeo Sans | Medeo Serif | Medeo Mono | Medeo Pixel |
| --- | --- | --- | --- | --- |
| ss01 | a without a tail | a with a curved tail | a without a tail | a without a tail |
| ss02 | alternate a | — | alternate a | alternate a |
| ss03 | alternate l | — | alternate l | alternate l |
| ss04 | alternate R | alternate R | alternate R | alternate R |
| ss05 | alternate I | — | — | alternate I |
| ss06 | alternate G | — | alternate G | alternate G |
| ss07 | alternate arrows | — | alternate arrows | — |
| ss08 | rounded dots | — | rounded dots | — |
| ss09 | slashed zero | — | plain zero | plain zero |
| ss10 | alternate enclosing shapes | — | alternate enclosing shapes | — |
| ss11 | contextual brand styles | — | coding ligatures | — |
| ss12 | — | alternate k | — | — |
| ss13 | — | square dots | — | — |
| ss14 | — | triangle dots | — | — |
| ss15 | — | heart dots | — | — |
| ss16 | — | transitional round letters | — | — |
| ss17 | — | — | plain г | — |
| ss18 | — | — | plain т | — |

Medeo Serif's sets also switch the matching Cyrillic letters. Medeo Mono Nerd Font has the same sets as Medeo Mono.

## Outlines and print

For outlined lettering and print export, choose the static Sans, Sans Display, or Mono files. Their overlapping letter parts are merged. If you convert a variable font to paths, unite the paths before adding an outline stroke. Pixel keeps its individual pixel elements.

## Files

`fonts/` holds the ready-to-use fonts, one folder per family:

- `ttf/`: static TTFs.
- `variable/`: variable TTFs (Sans, Mono and Pixel).
- `webfonts/`: web fonts, WOFF2; Pixel uses WOFF. One file per style, and the same fonts split by script for CSS `unicode-range` (`MedeoSansVariable.latin.woff2`, `.latin-ext`, `.vietnamese`, `.cyrillic`, `.cyrillic-ext`, `.symbols`; all WOFF2), which the npm package's style sheets load.
- `MedeoMonoNerdFont/licenses/`: the licenses of the Nerd Fonts icons.

`sources/` holds the Glyphs sources and the build configuration, `scripts/` the build steps (see Build below), and `packages/medeo-font/` the npm package.

## Release notes

See [CHANGELOG.md](CHANGELOG.md) for changes in each release and [FONTLOG.txt](FONTLOG.txt) for font development details.

Release tags use the npm version: `v1.0.0`. The matching font version is `1.000`.

## Build

The fonts in `fonts/` are built from the Glyphs sources in `sources/`. You need Python 3.12 and `make`. The first
build creates a virtual environment, `venv/`, with the pinned tools of `requirements.txt` (gftools builder,
fontmake, glyphsLib, fontTools, ttfautohint) and `requirements-pixel.txt` (the newer gftools that Medeo Pixel
needs).

```sh
make build   # build every family from sources/ into out/build/fonts
make check   # build, then require the fonts in fonts/ to equal the fresh build
make fonts   # copy a fresh build into fonts/ (after make build) and rewrite the npm package's CSS
make test    # Font Bakery, googlefonts profile, on the variable fonts (its own environment, venv-test/)
```

What each family is built from:

- **Medeo Sans**: `MedeoSans.glyphspackage` and `MedeoSans-Italic.glyphspackage` with `config-MedeoSans.yaml`. Each static style is cut from the variable font at its weight, at optical size 14 for Sans (`scripts/static_instances.py`) and 32 for Sans Display (`scripts/display_statics.py`): overlaps are merged, other components stay components, and ttfautohint hints the result. The kerning is stored as classes plus exceptions in the static, variable and web fonts (`scripts/kerncodec.py`, `scripts/variable_kerning.py`).
- **Medeo Mono**: `MedeoMono.glyphspackage` and `MedeoMono-Italic.glyphspackage` with `config-MedeoMono.yaml`. The static styles are cut from the variable font in the same way (`scripts/static_instances.py`).
- **Medeo Pixel**: `MedeoPixel.glyphspackage` with `config-MedeoPixel.yaml`. The five static shapes are named as one family by `scripts/pixel_static_names.py`; the web font is WOFF.
- **Medeo Serif**: `MedeoSerif.glyphspackage` with `config-MedeoSerif.yaml`, one static TTF. Its TrueType hinting and the data a Glyphs source does not hold come from `MedeoSerif-truetype.json` (`scripts/truetype_data.py`).
- After the builder, the variable Sans and Mono fonts lose their TrueType hinting (`scripts/variable_unhinted.py`), the variable fonts get overlap flags (`scripts/variable_overlaps.py`), and the web fonts are written (`scripts/webfonts.py`) and split by script (`scripts/web_subsets.py`: Google Fonts' subsets, with the whole Kazakh alphabet in `cyrillic`; `make fonts` also rewrites the npm package's style sheets from them).
- **Medeo Mono Nerd Font** is not built by `make`. It is patched from the static Medeo Mono TTFs with the [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) 3.5.1 font-patcher (`--complete --mono --careful`); afterwards Medeo Mono's own glyphs get back their original advance widths, so combining marks stay zero-width, and the `meta` table is restored. `make check` lists these files but does not compare them.

Every pull request and every push to `main` runs `make check` and `make test` on GitHub Actions (`.github/workflows/ci.yaml`).

## License and credits

Medeo uses the [SIL Open Font License 1.1](OFL.txt). You can use it in personal and commercial projects.

Medeo is a Modified Version of [Geist](https://github.com/vercel/geist-font) by Vercel and Basement Studio, Copyright 2024–2026 The Geist Project Authors. Medeo Serif is based on Geist Serif by WORDMARK, Mark Davis and Andrés Briganti, The Geist Project Authors.

Medeo Sans also uses letters and spacing from [Inter](https://github.com/rsms/inter) by Rasmus Andersson, Copyright 2016 The Inter Project Authors.

The Cyrillic of Medeo Serif follows [PT Serif](https://www.paratype.com) by ParaType Ltd. (Alexandra Korolkova, Olga Umpeleva, Vladimir Yefimov) for Б Д Л Ф З and other forms, Copyright (c) 2010 ParaType Ltd., with Reserved Font Names "PT Sans", "PT Serif" and "ParaType". Its Ʊ ʊ Ʋ ʋ are modelled on [Noto Serif Display](https://notofonts.github.io), Copyright 2012 Google Inc.

All of these fonts use the same license. Attribution and font changes are recorded in [FONTLOG.txt](FONTLOG.txt).

Medeo Mono Nerd Font adds the icons of [Nerd Fonts](https://github.com/ryanoasis/nerd-fonts) by Ryan L McIntyre and the icon sets it collects: Codicons, Devicons, Font Awesome, Font Logos, Material Design Icons, Octicons, Pomicons, Powerline Symbols, Powerline Extra Symbols, Seti UI, Weather Icons and others. The icons keep their own licenses (OFL 1.1, MIT, CC BY 4.0, Apache 2.0 and others); their texts travel with the fonts in `licenses/`. Brand logos among the icons are trademarks of their owners.
