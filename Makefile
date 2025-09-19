# Cross-platform Makefile for IP Switcher

APP_NAME = ip_switcher
ICON_PNG = icon.png
ICON_ICNS = $(APP_NAME).icns
ICON_ICO = $(APP_NAME).ico
ICONSET_DIR = $(APP_NAME).iconset

# Detect OS and set variables accordingly
ifeq ($(OS),Windows_NT)
    SYSTEM := Windows
    PYTHON ?= python
    BINARY_EXT := .exe
    NUITKA_FLAGS := --windows-icon-from-ico=$(ICON_ICO)
    # Windows: Try to detect Tcl/Tk from Python installation
    TCL_PATH := $(shell $(PYTHON) -c "import tkinter, os; print(os.path.dirname(tkinter.__file__))" 2>/dev/null)
    ifeq (,$(TCL_PATH))
        $(error Could not find Tcl/Tk installation)
    endif
    NUITKA_FLAGS += --include-package=tkinter --include-package=_tkinter
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
        SYSTEM := macOS
        PYTHON ?= python3
        BINARY_EXT := .bin
        NUITKA_FLAGS := --macos-app-icon=$(ICON_ICNS)
        
        # macOS: Try multiple common Tcl/Tk locations
        TCL_PATHS := /opt/local/lib/tcl8.6 /usr/local/lib/tcl8.6 /opt/homebrew/lib/tcl8.6 /System/Library/Frameworks/Tcl.framework
        TK_PATHS := /opt/local/lib/tk8.6 /usr/local/lib/tk8.6 /opt/homebrew/lib/tk8.6 /System/Library/Frameworks/Tk.framework
        
        # Find first existing Tcl path
        TCL_PATH := $(firstword $(wildcard $(TCL_PATHS)))
        TK_PATH := $(firstword $(wildcard $(TK_PATHS)))
        
        ifneq (,$(TCL_PATH))
            NUITKA_FLAGS += --tcl-library-dir=$(TCL_PATH)
        endif
        ifneq (,$(TK_PATH))
            NUITKA_FLAGS += --tk-library-dir=$(TK_PATH)
        endif
        
        # If no paths found, try to get from Python
        ifeq (,$(TCL_PATH))
            TCL_PATH := $(shell $(PYTHON) -c "import tkinter.tcl; print(tkinter.tcl.__file__)" 2>/dev/null)
            ifneq (,$(TCL_PATH))
                NUITKA_FLAGS += --tcl-library-dir=$(dir $(TCL_PATH))
            endif
        endif
    endif
endif

all: check-deps icons build

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
	@rm -r $(ICONSET_DIR)

$(ICON_ICO): $(ICON_PNG)
	@echo "Generating .ico from icon.png..."
	@sips -s format microsoft-icon $< --out $@

icons:
ifeq ($(SYSTEM),macOS)
	@$(MAKE) $(ICON_ICNS)
else ifeq ($(SYSTEM),Windows)
	@$(MAKE) $(ICON_ICO)
endif

clean-xattrs:
ifeq ($(SYSTEM),macOS)
	@echo "Cleaning extended attributes and resource forks..."
	@find . -name "._*" -delete 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@find . -type f -exec xattr -c {} \; 2>/dev/null || true
endif

build: clean-xattrs
	@echo "Building standalone app with Nuitka for $(SYSTEM)..."
	@echo "Using Tcl/Tk paths: $(TCL_PATH) $(TK_PATH)"
	$(PYTHON) -m nuitka \
		--onefile \
		$(NUITKA_FLAGS) \
		--enable-plugin=tk-inter \
		--include-package=tkinter \
		--include-package=_tkinter \
		--assume-yes-for-downloads \
		ip_switcher.py


clean:
	rm -rf build dist *.dist *.build *.app __pycache__ $(APP_NAME).build
ifeq ($(SYSTEM),macOS)
	rm -rf $(APP_NAME).iconset
	find . -type f -name ".DS_Store" -delete
	find . -type f -exec xattr -c {} \; 2>/dev/null || true
endif
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

install:
ifeq ($(SYSTEM),macOS)
	mkdir -p /Applications/IP\ Switcher.app/Contents/MacOS/
	cp $(APP_NAME)$(BINARY_EXT) /Applications/IP\ Switcher.app/Contents/MacOS/
else ifeq ($(SYSTEM),Windows)
	@echo "Please copy $(APP_NAME)$(BINARY_EXT) to your desired location"
endif

check-deps:
	@echo "Checking dependencies..."
	@$(PYTHON) -c "import tkinter" 2>/dev/null || (echo "Error: tkinter not found. Please install Python with Tkinter support." && exit 1)
	@$(PYTHON) -c "import nuitka" 2>/dev/null || (echo "Error: nuitka not found. Please run: pip install nuitka" && exit 1)
	@echo "All dependencies found."

.PHONY: all icons build clean install check-deps clean-xattrs
