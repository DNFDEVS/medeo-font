import localFont from "next/font/local";

export const MedeoMono = localFont({
  src: [
    {
      path: "./fonts/medeo-mono/MedeoMonoVariable.woff2",
      weight: "100 900",
      style: "normal",
    },
    {
      path: "./fonts/medeo-mono/MedeoMonoVariable-Italic.woff2",
      weight: "100 900",
      style: "italic",
    },
  ],
  variable: "--font-medeo-mono",
  adjustFontFallback: false,
  fallback: [
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
});
