# IP Switcher

[![Build Status](https://github.com/Fran6nd/ip_switcher/actions/workflows/build.yml/badge.svg)](https://github.com/Fran6nd/ip_switcher/actions/workflows/build.yml)
[![Latest Release](https://img.shields.io/github/v/release/Fran6nd/ip_switcher)](https://github.com/Fran6nd/ip_switcher/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/Fran6nd/ip_switcher/total)](https://github.com/Fran6nd/ip_switcher/releases)

## Quick Download

🚀 **Get the latest builds directly from CI:**

| Platform | Architecture | Download Link |
|----------|-------------|---------------|
| **Windows** | x86_64 | [⬇️ Latest Windows Build](https://github.com/Fran6nd/ip_switcher/actions/workflows/build.yml?query=is%3Asuccess+branch%3Amain) |
| **macOS** | Intel (x86_64) | [⬇️ Latest macOS Intel Build](https://github.com/Fran6nd/ip_switcher/actions/workflows/build.yml?query=is%3Asuccess+branch%3Amain) |
| **macOS** | Apple Silicon (ARM64) | [⬇️ Latest macOS ARM Build](https://github.com/Fran6nd/ip_switcher/actions/workflows/build.yml?query=is%3Asuccess+branch%3Amain) |

> **Note**: Click on the latest successful build, then scroll down to "Artifacts" section to download the builds.

## Overview

IP Switcher is a cross-platform application that allows you to easily switch between different IP address configurations (DHCP or Static) for your network interface. You can use predefined presets or manually switch between IP configurations with a simple GUI. The application is available for:
- Windows (x86_64 and ARM64)
- macOS (Intel and Apple Silicon)

## Features

- Switch between DHCP and Static IP addresses.
- Choose from a list of predefined static IP configurations.
- Simple and easy-to-use GUI with macOS app bundle.
- Automatically handles network interface detection.

## Requirements

- macOS 10.14 or higher.
- The application is bundled as a macOS `.app` and a Windows `.exe`, which are standalone and does not require installation.

## Download and Installation

### Option 1: Stable Releases
Download the latest stable version from the [📦 Releases](https://github.com/Fran6nd/ip_switcher/releases/latest) page:

- **Windows**: `ip_switcher-windows-x86_64.exe`
- **macOS Intel**: `ip_switcher-macos-x86_64.tar.gz`
- **macOS Apple Silicon**: `ip_switcher-macos-arm64.tar.gz`

### Option 2: Latest CI Builds
Get the most recent builds from GitHub Actions:

1. Go to [🔄 Actions](https://github.com/Fran6nd/ip_switcher/actions/workflows/build.yml)
2. Click on the latest successful build (green checkmark)
3. Scroll down to **Artifacts** section
4. Download the appropriate build for your platform

### Installation

#### Windows
1. Download the `.exe` file for your system
2. Move it to your desired location (e.g., `Program Files` or Desktop)
3. Double-click to run (no installation required)

#### macOS
1. Download the appropriate `.tar.gz` file for your Mac
2. Extract the archive: `tar -xzf ip_switcher-macos-*.tar.gz`
3. Move the `.app` bundle to Applications: `mv ip_switcher.app /Applications/`
4. Launch from Launchpad or Applications folder

## Building from Source

### Prerequisites
- Python 3.10 or higher
- pip (Python package installer)

### Build Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/Fran6nd/ip_switcher.git
   cd ip_switcher
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install nuitka
   ```

3. Build the application:
   ```bash
   make
   ```

The build process will automatically detect your operating system and create the appropriate binary.

## How to Use

1. Upon launching the app, it will automatically detect your active network interface.
2. From the GUI, select a preset configuration (either DHCP or a Static IP preset).
3. Click **Apply** to switch the network settings for your active interface.
