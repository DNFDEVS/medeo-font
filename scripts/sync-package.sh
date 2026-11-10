#!/bin/sh
# Copies the release web fonts and the licence into the npm package before `npm pack` / `npm publish`,
# so the package never carries a second copy of the binaries in Git.
# One web font per style. Files are copied over the old ones.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
pkg="$root/packages/medeo-font"
out="$pkg/dist/fonts"
mkdir -p "$out/medeo-sans" "$out/medeo-mono" "$out/medeo-pixel" "$out/medeo-serif"
cp "$root"/fonts/MedeoSans/webfonts/MedeoSansVariable*.woff2 "$out/medeo-sans/"
cp "$root"/fonts/MedeoMono/webfonts/MedeoMonoVariable*.woff2 "$out/medeo-mono/"
cp "$root"/fonts/MedeoPixel/webfonts/MedeoPixelVariable*.woff* "$out/medeo-pixel/"
cp "$root"/fonts/MedeoSerif/webfonts/MedeoSerif-Regular*.woff2 "$out/medeo-serif/"
cp "$root/OFL.txt" "$pkg/LICENSE.txt"
