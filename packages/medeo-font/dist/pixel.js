import localFont from "next/font/local";

// One variable file: the dot shape is the ELSH axis, chosen with
// font-variation-settings (see the README), not a separate font.
export const MedeoPixel = localFont({
  src: "./fonts/medeo-pixel/MedeoPixelVariable.woff",
  variable: "--font-medeo-pixel",
  weight: "400",
  fallback: [
    "Medeo Mono",
    "ui-monospace",
    "SFMono-Regular",
    "Roboto Mono",
    "Menlo",
    "Monaco",
    "Liberation Mono",
    "DejaVu Sans Mono",
    "Courier New",
    "monospace",
  ],
  adjustFontFallback: false,
});
