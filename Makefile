FAMILIES = MedeoSans MedeoMono MedeoPixel
PYTHON ?= python3
VENV ?= venv
# Medeo Sans and Mono build with gftools 0.9.99 and the pinned tools of requirements.txt. Medeo Pixel's virtual
# master needs gftools 0.10.4, which needs protobuf 6, so Pixel gets requirements-pixel.txt in front of the venv.
# These are the versions that built the committed fonts.
PIXEL = $(VENV)/gftools-pixel
# gftools builder runs fontmake and the other tools from PATH; Pixel's static styles are cut with the
# gftools-gen-static script of the gftools-pixel target, which comes after the venv on PATH
BIN = PATH="$(abspath $(VENV))/bin:$$PATH"
BIN_PIXEL = PATH="$(abspath $(VENV))/bin:$(abspath $(PIXEL))/bin:$$PATH" PYTHONPATH="$(abspath $(PIXEL))"
# Font Bakery pins protobuf<4 and gftools needs protobuf>=6, so the checks get their own environment.
# requirements-test.txt is the full lock of requirements-test.in for Linux (uv pip compile --python-platform
# x86_64-manylinux_2_28): pip's resolver could not solve fontbakery[googlefonts] on its own in CI.
VENV_TEST ?= venv-test

help:
	@echo "make build    builds fonts/ from sources/ (gftools builder: variable and static TTFs, then the web fonts)"
	@echo "make test     runs Font Bakery (googlefonts profile) on the variable fonts"
	@echo "make check    checks that the committed fonts equal a fresh build"
	@echo "make package  copies the web fonts and static TTFs into packages/medeo-font and packs it"
	@echo "make languages  writes LANGUAGES.md and the package's languages.json from the built fonts"

$(VENV)/touchfile: requirements.txt requirements-pixel.txt
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -q --upgrade pip
	$(VENV)/bin/pip install -q --no-deps "gftools==0.9.99"
	$(VENV)/bin/pip install -q --prefer-binary -r requirements.txt
	$(VENV)/bin/pip install -q --no-deps --target $(PIXEL) -r requirements-pixel.txt
	touch $@

$(VENV_TEST)/touchfile: requirements-test.txt
	$(PYTHON) -m venv $(VENV_TEST)
	$(VENV_TEST)/bin/pip install -q --upgrade pip
	$(VENV_TEST)/bin/pip install -q --no-deps -r requirements-test.txt
	touch $@

build: $(VENV)/touchfile
	rm -rf fonts
	cd sources && $(BIN) gftools builder config-MedeoSans.yaml
	$(VENV)/bin/python -I scripts/display_statics.py fonts/MedeoSans
	cd sources && $(BIN) gftools builder config-MedeoMono.yaml
	cd sources && $(BIN_PIXEL) gftools builder config-MedeoPixel.yaml
	$(VENV)/bin/python -I scripts/pixel_static_names.py fonts/MedeoPixel/ttf
	$(VENV)/bin/python -I scripts/variable_hinting.py fonts
	$(VENV)/bin/python -I scripts/variable_overlaps.py fonts
	$(VENV)/bin/python -I scripts/webfonts.py fonts

# Only the variable fonts: they are what Google Fonts takes, and it cuts its own statics from them. The static TTFs
# are instances of the same sources, built by the same builder with gftools fix.
test: $(VENV_TEST)/touchfile
	mkdir -p out
	for f in $(FAMILIES); do \
		$(VENV_TEST)/bin/fontbakery check-googlefonts -l WARN --succinct -F --json out/fontbakery-$$f.json fonts/$$f/variable/*.ttf; \
	done; \
	$(VENV_TEST)/bin/python -I scripts/fontbakery_gate.py out/fontbakery-*.json
	$(VENV_TEST)/bin/python -I scripts/languages.py --check

check: $(VENV)/touchfile
	rm -rf out/committed && mkdir -p out && cp -R fonts out/committed
	$(MAKE) build
	# the committed files go back in place either way: a release packs those bytes, not the fresh build's timestamps
	$(VENV)/bin/python -I scripts/same_fonts.py out/committed fonts || { rm -rf out/fresh && mv fonts out/fresh && cp -R out/committed fonts; echo "fresh build kept in out/fresh"; exit 1; }
	rm -rf fonts && mv out/committed fonts

languages: $(VENV_TEST)/touchfile
	$(VENV_TEST)/bin/python -I scripts/languages.py

package:
	cd packages/medeo-font && npm pack

.PHONY: help build test check languages package
