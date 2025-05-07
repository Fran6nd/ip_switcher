# Makefile to build a macOS standalone app using Nuitka and icon.png

APP_NAME = ip_switcher
PYTHON = /opt/local/bin/python3.11
ICON_PNG = icon.png
ICON_ICNS = $(APP_NAME).icns
ICONSET_DIR = $(APP_NAME).iconset

all: build

$(ICON_ICNS): $(ICON_PNG)
	@echo "Generating .icns from icon.png..."
	@mkdir -p $(ICONSET_DIR)
	@sips -z 16 16     $< --out $(ICONSET_DIR)/icon_16x16.png
	@sips -z 32 32     $< --out $(ICONSET_DIR)/icon_16x16@2x.png
	@sips -z 32 32     $< --out $(ICONSET_DIR)/icon_32x32.png
	@sips -z 64 64     $< --out $(ICONSET_DIR)/icon_32x32@2x.png
	@sips -z 128 128   $< --out $(ICONSET_DIR)/icon_128x128.png
	@sips -z 256 256   $< --out $(ICONSET_DIR)/icon_128x128@2x.png
	@sips -z 256 256   $< --out $(ICONSET_DIR)/icon_256x256.png
	@sips -z 512 512   $< --out $(ICONSET_DIR)/icon_256x256@2x.png
	@sips -z 512 512   $< --out $(ICONSET_DIR)/icon_512x512.png
	@cp $< $(ICONSET_DIR)/icon_512x512@2x.png
	@iconutil -c icns $(ICONSET_DIR)
	@if [ -e $(APP_NAME).icns ]; then \
		echo "Icon already in place."; \
	else \
		mv $(APP_NAME).icns .; \
	fi

	@rm -r $(ICONSET_DIR)

build: $(ICON_ICNS)
	@echo "Building standalone app with Nuitka..."
	$(PYTHON) -m nuitka \
		--standalone \
		--macos-app-name=$(APP_NAME) \
		--macos-create-app-bundle \
		--macos-app-icon=$(ICON_ICNS) \
		--output-dir=dist \
		--follow-imports \
		--enable-plugin=tk-inter \
		--tcl-library-dir=/opt/local/lib/tcl8.6 \
		--tk-library-dir=/opt/local/lib/tk8.6 \
		ip_switcher.py


clean:
	rm -rf build dist *.dist *.build *.app __pycache__ $(APP_NAME).build $(APP_NAME).icns $(APP_NAME).iconset

.PHONY: all build clean
