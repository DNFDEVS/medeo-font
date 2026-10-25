FAMILIES = MedeoSans MedeoMono MedeoPixel
PYTHON ?= python3
VENV ?= venv
# Medeo Sans and Mono build with gftools 0.9.99 and the pinned tools of requirements.txt. Medeo Pixel's virtual
# master needs gftools 0.10.4, which needs protobuf 6, so Pixel gets requirements-pixel.txt in front of the venv.
# These are the versions that built the committed fonts.
PIXEL = $(VENV)/gftools-pixel
# gftools builder runs fontmake and the other tools from PATH
BIN = PATH="$(abspath $(VENV))/bin:$$PATH"
# Font Bakery pins protobuf<4 and gftools needs protobuf>=6, so the checks get their own environment.
# requirements-test.txt is the full lock of requirements-test.in for Linux (uv pip compile --python-platform
# x86_64-manylinux_2_28): pip's resolver could not solve fontbakery[googlefonts] on its own in CI.
VENV_TEST ?= venv-test

help:
	@echo "make build    builds fonts/ from sources/ (gftools builder, then the web fonts)"
	@echo "make test     runs Font Bakery (googlefonts profile) on the built fonts"
	@echo "make check    checks that the committed fonts equal a fresh build"
	@echo "make package  copies the web fonts into packages/medeo-font and packs it"

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
	cd sources && $(BIN) gftools builder config-MedeoMono.yaml
	cd sources && $(BIN) PYTHONPATH="$(abspath $(PIXEL))" gftools builder config-MedeoPixel.yaml
	$(VENV)/bin/python -I scripts/webfonts.py fonts

test: $(VENV_TEST)/touchfile
	mkdir -p out
	for f in $(FAMILIES); do \
		$(VENV_TEST)/bin/fontbakery check-googlefonts -l WARN --succinct -F --json out/fontbakery-$$f.json fonts/$$f/variable/*.ttf; \
	done; \
	$(VENV_TEST)/bin/python -I scripts/fontbakery_gate.py out/fontbakery-*.json

check: $(VENV)/touchfile
	rm -rf out/committed && mkdir -p out && cp -R fonts out/committed
	$(MAKE) build
	# the committed files go back in place either way: a release packs those bytes, not the fresh build's timestamps
	$(VENV)/bin/python -I scripts/same_fonts.py out/committed fonts || { rm -rf out/fresh && mv fonts out/fresh && cp -R out/committed fonts; echo "fresh build kept in out/fresh"; exit 1; }
	rm -rf fonts && mv out/committed fonts

package:
	cd packages/medeo-font && npm pack

.PHONY: help build test check package
