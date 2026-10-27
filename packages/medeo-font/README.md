![Medeo: open fonts for Latin and Cyrillic](https://prtner.ai/font/media/og.jpg)

# Medeo.RC4

Medeo is a free font family for Latin and Cyrillic by [DNF](https://dnf.dev), made for [prtner.ai](https://prtner.ai). RC4 is a release candidate. Try the fonts at [prtner.ai/font](https://prtner.ai/font).

Medeo Sans is a sans-serif for interfaces and running text. It has two axes, weight (100–900) and optical size (`opsz`, 14–32); browsers set the optical size from the font size automatically.

Medeo Mono is the monospaced companion to Medeo Sans, for code and for tables where figures must line up.

Medeo Pixel is a display face built on a pixel grid.

Each family covers the alphabets of 759 languages in the Google Fonts language dataset. This count describes alphabet coverage, not a linguistic review. See the [full list and coverage criteria](https://github.com/DNFDEVS/medeo-font/blob/main/LANGUAGES.md), or use `medeo-font/languages.json`.

## Installation

```sh
npm install medeo-font@1.0.0-rc.4
```

## Using with Next.js

`MedeoSans` is exported from `medeo-font/sans`, `MedeoMono` from `medeo-font/mono` and `MedeoPixel` from `medeo-font/pixel`. All are `NextFontWithVariable` instances. Importing from `medeo-font` itself loads all three; use the paths above to load only the fonts you use. Requires Next.js 13.2 or newer. You can learn more by [reading the `next/font` docs](https://nextjs.org/docs/app/building-your-application/optimizing/fonts).

| Export       | CSS variable          | Files                                              |
| ------------ | --------------------- | -------------------------------------------------- |
| `MedeoSans`  | `--font-medeo-sans`   | variable, weight 100–900, upright and italic       |
| `MedeoMono`  | `--font-medeo-mono`   | variable, weight 100–900, upright and italic       |
| `MedeoPixel` | `--font-medeo-pixel`  | one variable file, upright, weight 400; dot shape on the `ELSH` axis |

### App Router

In `app/layout.js`:

```jsx
import { MedeoSans } from "medeo-font/sans";

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={MedeoSans.className}>
      <body>{children}</body>
    </html>
  );
}
```

### Pages Router

In `pages/_app.js`:

```jsx
import { MedeoSans } from "medeo-font/sans";

export default function MyApp({ Component, pageProps }) {
  return (
    <main className={MedeoSans.className}>
      <Component {...pageProps} />
    </main>
  );
}
```

On Next.js older than 15, add `transpilePackages: ["medeo-font"]` to `next.config.js`.

### Medeo Pixel shapes

The dot shape is the `ELSH` axis (0–100). The font names five positions on it:

| Shape    | `font-variation-settings` | Class                  |
| -------- | ------------------------- | ---------------------- |
| Square   | `"ELSH" 1`                | `medeo-pixel-square`   |
| Circle   | `"ELSH" 20`               | `medeo-pixel-circle`   |
| Grid     | `"ELSH" 40`               | `medeo-pixel-grid`     |
| Triangle | `"ELSH" 60`               | `medeo-pixel-triangle` |
| Line     | `"ELSH" 80`               | `medeo-pixel-line`     |

The classes come with `medeo-font/pixel.css`, for use without Next.js (see [Using without Next.js](#using-without-nextjs)). With `next/font`, don't import it; set the axis directly:

```jsx
import { MedeoPixel } from "medeo-font/pixel";

export function Score() {
  return (
    <p className={MedeoPixel.className} style={{ fontVariationSettings: '"ELSH" 20' }}>
      Final 3:2
    </p>
  );
}
```

### With Tailwind CSS

In `app/layout.js`:

```jsx
import { MedeoSans } from "medeo-font/sans";
import { MedeoMono } from "medeo-font/mono";
import { MedeoPixel } from "medeo-font/pixel";

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className={`${MedeoSans.variable} ${MedeoMono.variable} ${MedeoPixel.variable}`}
    >
      <body>{children}</body>
    </html>
  );
}
```

Map the variables to Tailwind's font families as below, then use the `font-sans`, `font-mono` and `font-pixel` classes.

#### Tailwind CSS V4

In `tailwind.css`:

```css
@theme {
  --font-sans: var(--font-medeo-sans);
  --font-mono: var(--font-medeo-mono);
  --font-pixel: var(--font-medeo-pixel);
}
```

#### Tailwind CSS V3

In `tailwind.config.js`:

```javascript
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ["var(--font-medeo-sans)"],
        mono: ["var(--font-medeo-mono)"],
        pixel: ["var(--font-medeo-pixel)"],
      },
    },
  },
};
```

## Using without Next.js

The package ships plain CSS with `@font-face` rules and the same CSS variables. With Vite, Astro, Remix, SvelteKit or any bundler that resolves CSS from `node_modules`:

```js
import "medeo-font/medeo.css"; // all three; or medeo-font/sans.css, mono.css, pixel.css
```

```css
body {
  font-family: var(--font-medeo-sans);
}
code {
  font-family: var(--font-medeo-mono);
}
.score {
  font-family: var(--font-medeo-pixel);
}
```

```html
<p class="score medeo-pixel-circle">Final 3:2</p>
```

Without a bundler, from a CDN that mirrors npm:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/medeo-font@1.0.0-rc.4/dist/medeo.css" />
```

The font files are under `medeo-font/fonts/*`. Medeo Pixel ships as WOFF, the others as WOFF2. Desktop TTF files are in the archive on [prtner.ai/font](https://prtner.ai/font) and in every [GitHub release](https://github.com/DNFDEVS/medeo-font/releases).

## Tabular figures

Medeo Pixel uses proportional figures by default. For clocks, counters and aligned columns, enable tabular figures (`tnum`): all ten digits then have the same advance width in every Pixel shape, including the plain-zero alternate.

```css
.counter { font-variant-numeric: tabular-nums; }
```

## Outlines and print

For outlined lettering and print export, choose the static Sans, Sans Display, or Mono files from the desktop archive. Their overlapping letter parts are merged. If you convert a variable font to paths, unite the paths before adding an outline stroke. Pixel keeps its individual pixel elements.

## Sans and Sans Display

Medeo Sans is spaced for text. Sans Display has tighter spacing for headings and large type. The variable Sans font includes both through `opsz` 14–32, so a separate web font is not needed. Browsers select the optical size automatically unless you override it. The desktop archive includes separate static Sans and Sans Display families.

Start with the default letter spacing. The optical-size axis already adjusts the spacing for the chosen text size.

## License

Medeo is licensed under the [SIL Open Font License 1.1](LICENSE.txt). It is based on [Geist](https://vercel.com/font) by Vercel and Basement Studio (Copyright 2024 and 2026 The Geist Project Authors) and [Inter](https://rsms.me/inter) by Rasmus Andersson (Copyright 2016 The Inter Project Authors), both under the same license.
