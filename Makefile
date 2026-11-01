FAMILIES = MedeoSans MedeoMono MedeoPixel MedeoSerif
NOT_BUILT = MedeoMonoNerdFont
# Medeo Serif's committed fonts were compiled by other tools than this build: its layout tables are compared by
# what a shaper does with them (scripts/same_fonts.py --layout-by-effect), every other table byte for byte.
BY_EFFECT = MedeoSerif
BUILD = out/build/fonts
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
	@echo "make build    builds the fonts from sources/ into out/build/fonts (gftools builder, then the steps below)"
	@echo "make check    checks that the fonts in fonts/ equal a fresh build (scripts/same_fonts.py)"
	@echo "make fonts    copies a fresh build into fonts/ (after make build) and rewrites the npm package CSS"
	@echo "make test     runs Font Bakery (googlefonts profile) on the variable fonts"
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

# The builder configs in sources/ write to out/build/fonts. The static TTFs of Medeo Sans, Sans Display and Mono are
# cut from the variable fonts as the builder writes them, before the later steps rewrite the variable fonts: the
# builder's statics give each style its names and flags (scripts/static_instances.py, scripts/display_statics.py).
# Medeo Sans keeps its kerning as classes plus exceptions in every static, variable and web font (scripts/kerncodec.py).
build: $(VENV)/touchfile
	rm -rf $(BUILD)
	cd sources && $(BIN) gftools builder config-MedeoSans.yaml
	$(VENV)/bin/python -I scripts/display_statics.py $(BUILD)/MedeoSans
	cd sources && $(BIN) gftools builder config-MedeoMono.yaml
	$(VENV)/bin/python -I scripts/static_instances.py $(BUILD)
	cd sources && $(BIN_PIXEL) gftools builder config-MedeoPixel.yaml
	$(VENV)/bin/python -I scripts/pixel_static_names.py $(BUILD)/MedeoPixel/ttf
	cd sources && $(BIN) gftools builder config-MedeoSerif.yaml
	$(VENV)/bin/python -I scripts/truetype_data.py sources/MedeoSerif-truetype.json $(BUILD)/MedeoSerif/ttf/*.ttf
	$(VENV)/bin/python -I scripts/variable_unhinted.py $(BUILD)
	$(VENV)/bin/python -I scripts/variable_overlaps.py $(BUILD)
	$(VENV)/bin/python -I scripts/variable_kerning.py $(BUILD)
	$(VENV)/bin/python -I scripts/webfonts.py $(BUILD)
	$(VENV)/bin/python -I scripts/web_subsets.py $(BUILD)

# Only the variable fonts: they are what Google Fonts takes, and it cuts its own statics from them. The static TTFs
# are instances of the same sources, built by the same builder with gftools fix. Medeo Serif has no variable font:
# its one static TTF is checked.
test: $(VENV_TEST)/touchfile
	mkdir -p out
	for f in $(FAMILIES); do \
		files=$$(ls fonts/$$f/variable/*.ttf 2>/dev/null || ls fonts/$$f/ttf/*.ttf); \
		$(VENV_TEST)/bin/fontbakery check-googlefonts -l WARN --succinct -F --json out/fontbakery-$$f.json $$files; \
	done; \
	$(VENV_TEST)/bin/python -I scripts/fontbakery_gate.py out/fontbakery-*.json
	$(VENV_TEST)/bin/python -I scripts/languages.py --check

# Medeo Mono Nerd Font is not built from sources/: it is listed, not compared.
check: build
	$(VENV)/bin/python -I scripts/same_fonts.py fonts $(BUILD) --not-built $(NOT_BUILT) --layout-by-effect $(BY_EFFECT)

fonts: $(BUILD)
	for f in $(FAMILIES); do mkdir -p fonts/$$f && cp -R $(BUILD)/$$f/. fonts/$$f/; done
	$(VENV)/bin/python -I scripts/web_subsets.py fonts --css packages/medeo-font/dist --css-only

languages: $(VENV_TEST)/touchfile
	$(VENV_TEST)/bin/python -I scripts/languages.py

package:
	cd packages/medeo-font && npm pack

.PHONY: help build test check fonts languages package
