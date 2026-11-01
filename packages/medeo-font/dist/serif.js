import localFont from "next/font/local";

// One static style: Regular.
export const MedeoSerif = localFont({
  src: "./fonts/medeo-serif/MedeoSerif-Regular.woff2",
  variable: "--font-medeo-serif",
  weight: "400",
  style: "normal",
  fallback: [
    "ui-serif",
    "Georgia",
    "Cambria",
    "Times New Roman",
    "Times",
    "serif",
  ],
});
