#!/bin/sh
# Copies the release web fonts and the licence into the npm package before `npm pack` / `npm publish`,
# so the package never carries a second copy of the binaries in Git.
# The package CSS loads the fonts split by script (scripts/web_subsets.py). When fonts/ holds those files they are
# copied with the full ones; otherwise they are cut here from the full web fonts. Files are copied over the old ones.
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
pkg="$root/packages/medeo-font"
out="$pkg/dist/fonts"
python=${PYTHON:-"$root/venv/bin/python"}
mkdir -p "$out/medeo-sans" "$out/medeo-mono" "$out/medeo-pixel" "$out/medeo-serif"
cp "$root"/fonts/MedeoSans/webfonts/MedeoSansVariable*.woff2 "$out/medeo-sans/"
cp "$root"/fonts/MedeoMono/webfonts/MedeoMonoVariable*.woff2 "$out/medeo-mono/"
cp "$root"/fonts/MedeoPixel/webfonts/MedeoPixelVariable*.woff* "$out/medeo-pixel/"
cp "$root"/fonts/MedeoSerif/webfonts/MedeoSerif-Regular*.woff2 "$out/medeo-serif/"
if [ ! -e "$root/fonts/MedeoSans/webfonts/MedeoSansVariable.latin.woff2" ]; then
  "$python" -I "$root/scripts/web_subsets.py" "$root/fonts" --out "$out"
fi
cp "$root/OFL.txt" "$pkg/LICENSE.txt"
