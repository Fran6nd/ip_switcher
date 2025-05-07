# IP Switcher Pro

## Overview

IP Switcher Pro is a macOS application that allows you to easily switch between different IP address configurations (DHCP or Static) for your network interface. You can use predefined presets or manually switch between IP configurations with a simple GUI.

## Features

- Switch between DHCP and Static IP addresses.
- Choose from a list of predefined static IP configurations.
- Simple and easy-to-use GUI with macOS app bundle.
- Automatically handles network interface detection.

## Requirements

- macOS 10.14 or higher.
- The application is bundled as a macOS `.app`, which is standalone and does not require installation.

## Download the macOS Binary

You can download the latest version of IP Switcher Pro for macOS from the following link:

[Download IP Switcher Pro](./dist/ip_switcher.zip)

## Installation and Usage

1. **Download** the `.zip` file.
2. **Unzip** the downloaded file. This will extract the `ip_switcher.app` bundle.
3. **Move** the `ip_switcher.app` to your `Applications` folder for easy access (optional).
4. **Double-click** the `ip_switcher.app` to launch the application.

## How to Use

1. Upon launching the app, it will automatically detect your active network interface.
2. From the GUI, select a preset configuration (either DHCP or a Static IP preset).
3. Click **Apply** to switch the network settings for your active interface.

## Troubleshooting

- If you encounter any issues or errors, please check the `nuitka-crash-report.xml` for debugging information.
- If the application fails to detect your network interface, ensure your network is properly configured.

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- This project uses [Nuitka](https://nuitka.net/) to compile the Python script into a standalone macOS application.
- [Tkinter](https://wiki.python.org/moin/TkInter) is used for the GUI.
- Thanks to everyone contributing to the development of this tool!

## Contact

For support or contributions, please open an issue or contact the repository owner.

---

Thank you for using **IP Switcher Pro**!
