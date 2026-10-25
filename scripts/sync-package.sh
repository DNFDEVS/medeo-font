#!/bin/sh
# Copies the release web fonts and the licence into the npm package before `npm pack` / `npm publish`,
# so the package never carries a second copy of the binaries in Git.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
pkg="$root/packages/medeo-font"
out="$pkg/dist/fonts"
rm -rf "$out"
mkdir -p "$out/medeo-sans" "$out/medeo-mono" "$out/medeo-pixel"
cp "$root/fonts/MedeoSans/webfonts/MedeoSansVariable.woff2" \
   "$root/fonts/MedeoSans/webfonts/MedeoSansVariable-Italic.woff2" "$out/medeo-sans/"
cp "$root/fonts/MedeoMono/webfonts/MedeoMonoVariable.woff2" \
   "$root/fonts/MedeoMono/webfonts/MedeoMonoVariable-Italic.woff2" "$out/medeo-mono/"
cp "$root/fonts/MedeoPixel/webfonts/MedeoPixelVariable.woff" "$out/medeo-pixel/"
cp "$root/OFL.txt" "$pkg/LICENSE.txt"
