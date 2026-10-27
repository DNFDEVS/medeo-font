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

For CSS and Next.js examples, see [the npm package documentation](packages/medeo-font/README.md).

For desktop use, download the ZIP from [GitHub releases](https://github.com/DNFDEVS/medeo-font/releases) and install the TTF files you need. The ZIP includes variable fonts and static Sans, Sans Display, Mono, and Pixel styles.

## Figures

Medeo Pixel uses proportional figures by default. For clocks, counters, and aligned columns, enable tabular figures. All ten digits then have the same width in every Pixel shape.

```css
.counter { font-variant-numeric: tabular-nums; }
```

## Outlines and print

For outlined lettering and print export, choose the static Sans, Sans Display, or Mono files. Their overlapping letter parts are merged. If you convert a variable font to paths, unite the paths before adding an outline stroke. Pixel keeps its individual pixel elements.

## Zero and O, and other stylistic sets

In Medeo Sans the zero is an oval close to O; `ss09` gives a slashed zero to distinguish it from O. Medeo Mono
and Medeo Pixel slash the zero by default, and their `ss09` gives the plain one.

```css
.code, .table { font-feature-settings: "ss09"; } /* Medeo Sans: 0 distinct from O */
```

| Set | Medeo Sans | Medeo Mono | Medeo Pixel |
| --- | --- | --- | --- |
| ss01 | a without a tail | a without a tail | a without a tail |
| ss02 | alternate a | alternate a | alternate a |
| ss03 | alternate l | alternate l | alternate l |
| ss04 | alternate R | alternate R | alternate R |
| ss05 | alternate I | — | alternate I |
| ss06 | alternate G | alternate G | alternate G |
| ss07 | alternate arrows | alternate arrows | — |
| ss08 | rounded dots | rounded dots | — |
| ss09 | slashed zero | plain zero | plain zero |
| ss10 | alternate enclosing shapes | alternate enclosing shapes | — |
| ss11 | contextual brand styles | coding ligatures | — |

## Release notes

See [CHANGELOG.md](CHANGELOG.md) for changes in each release and [FONTLOG.txt](FONTLOG.txt) for font development details.

## Build

Use Python 3.12.

```sh
make build   # build fonts from sources
make test    # run the Font Bakery profile
make check   # compare a fresh build with the committed fonts
```

Release tags use the npm version, such as `v1.0.0-rc.4.1`. The matching font version is `1.000-rc4`.

## Files

- `sources/`: Glyphs sources and build configuration.
- `fonts/`: static and variable TTFs, plus WOFF2 web fonts. Pixel uses WOFF.
- `packages/medeo-font/`: CSS and Next.js exports for npm.

## License and credits

Medeo uses the [SIL Open Font License 1.1](OFL.txt). You can use it in personal and commercial projects.

Medeo is a Modified Version of [Geist](https://github.com/vercel/geist-font) by Vercel and Basement Studio, Copyright 2024 and 2026 The Geist Project Authors. Medeo Sans also uses letters and spacing from [Inter](https://github.com/rsms/inter) by Rasmus Andersson, Copyright 2016 The Inter Project Authors. Both use the same license. Attribution and font changes are recorded in [FONTLOG.txt](FONTLOG.txt).
