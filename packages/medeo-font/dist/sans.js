import localFont from "next/font/local";

export const MedeoSans = localFont({
  src: [
    {
      path: "./fonts/medeo-sans/MedeoSansVariable.woff2",
      weight: "100 900",
      style: "normal",
    },
    {
      path: "./fonts/medeo-sans/MedeoSansVariable-Italic.woff2",
      weight: "100 900",
      style: "italic",
    },
  ],
  variable: "--font-medeo-sans",
  fallback: [
    "ui-sans-serif",
    "system-ui",
    "-apple-system",
    "BlinkMacSystemFont",
    "Segoe UI",
    "Roboto",
    "Helvetica Neue",
    "Arial",
    "sans-serif",
    "Apple Color Emoji",
    "Segoe UI Emoji",
    "Segoe UI Symbol",
    "Noto Color Emoji",
  ],
});
