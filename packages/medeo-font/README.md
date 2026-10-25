![Medeo: open fonts for Latin and Cyrillic](https://prtner.ai/font/media/og.jpg)

# Medeo Sans, Medeo Mono & Medeo Pixel

**RC1** — the first public release candidate.

Medeo is an open font family for Latin and Cyrillic. Made by DNF studio · [dnf.dev](https://dnf.dev) for [prtner.ai](https://prtner.ai). Specimen, tester and downloads: [prtner.ai/font](https://prtner.ai/font).

Medeo Sans is a sans-serif for interfaces and running text. It has two axes, weight (100–900) and optical size (`opsz`, 14–32); browsers set the optical size from the font size automatically.

Medeo Mono is the monospaced companion to Medeo Sans, for code and for tables where figures must line up.

Medeo Pixel is a display face built on a pixel grid.

Languages: English, Cyrillic (Russian), Kazakh (Cyrillic and the 2021 Latin), Ukrainian, Uzbek (Latin and Cyrillic), Kyrgyz, Tajik, Turkmen, Azerbaijani and Turkish.

### Installation

```sh
npm install medeo-font
```

### Using with Next.js

`MedeoSans` is exported from `medeo-font/sans`, `MedeoMono` from `medeo-font/mono` and `MedeoPixel` from `medeo-font/pixel`. All are `NextFontWithVariable` instances. Importing from `medeo-font` itself loads all three; use the paths above to load only the fonts you use. Requires Next.js 13.2 or newer. You can learn more by [reading the `next/font` docs](https://nextjs.org/docs/app/building-your-application/optimizing/fonts).

| Export       | CSS variable          | Files                                              |
| ------------ | --------------------- | -------------------------------------------------- |
| `MedeoSans`  | `--font-medeo-sans`   | variable, weight 100–900, upright and italic       |
| `MedeoMono`  | `--font-medeo-mono`   | variable, weight 100–900, upright and italic       |
| `MedeoPixel` | `--font-medeo-pixel`  | one variable file, upright, weight 400; dot shape on the `ELSH` axis |

#### App Router

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

#### Pages Router

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

#### Medeo Pixel shapes

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

#### With Tailwind CSS

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

##### Tailwind CSS V4

In `tailwind.css`:

```css
@theme {
  --font-sans: var(--font-medeo-sans);
  --font-mono: var(--font-medeo-mono);
  --font-pixel: var(--font-medeo-pixel);
}
```

##### Tailwind CSS V3

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

### Using without Next.js

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
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/medeo-font@1.0.0-rc.1.2/dist/medeo.css" />
```

The font files are under `medeo-font/fonts/*`. Medeo Pixel ships as WOFF, the others as WOFF2. Desktop TTF files are in the archive on [prtner.ai/font](https://prtner.ai/font).

### Spacing

The x-height is 75% of the cap height. In Medeo Sans, the optical-size axis tightens the spacing at display sizes on its own. Use `letter-spacing: -0.01em` to `-0.03em` for headlines and `0` for body text.

### License

Medeo is licensed under the [SIL Open Font License 1.1](LICENSE.txt). It is based on [Geist](https://vercel.com/font) by Vercel and Basement Studio (Copyright 2024 The Geist Project Authors) and [Inter](https://rsms.me/inter) by Rasmus Andersson (Copyright 2016 The Inter Project Authors), both under the same license.
