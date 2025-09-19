#!/opt/local/bin/python3.11

import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import json
import platform
import sys
from datetime import datetime


# File to persist presets
PRESETS_FILE = 'presets.json'

# Load presets from file (ordered list format)
def load_presets():
    try:
        with open(PRESETS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return [
            ["Alouette", ["192.168.1.149", "255.255.255.0", "192.168.1.1"]],
            ["DHCP", None],
            ["TLM", ["192.168.1.10", "255.255.255.0", "192.168.1.1"]],
            ["Backup 2", ["172.16.0.50", "255.255.0.0", "172.16.0.1"]]
        ]

# Save presets to file
def save_presets():
    with open(PRESETS_FILE, 'w') as file:
        json.dump(presets, file, indent=2)

# Presets stored as list of [name, values]
presets = load_presets()

import ctypes
import os

def run_with_privileges(command):
    system = platform.system()
    if system == "Darwin":
        escaped_command = command.replace('"', '\\"')
        script = f'do shell script "{escaped_command}" with administrator privileges'
        try:
            subprocess.run(["osascript", "-e", script], check=True)
        except subprocess.CalledProcessError:
            messagebox.showerror("Permission Denied", f"Command failed or was cancelled:\n{command}")
            sys.exit(1)
    elif system == "Windows":
        try:
            params = f'/c {command}'
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", "cmd.exe", params, None, 0
            )
        except Exception as e:
            messagebox.showerror("Permission Denied", f"Command failed or was cancelled:\n{command}")
            sys.exit(1)




def list_all_interfaces():
    system = platform.system()
    interfaces = []
    try:
        if system == "Darwin":
            output = subprocess.check_output(["networksetup", "-listallhardwareports"], text=True)
            blocks = output.strip().split("\n\n")
            for block in blocks:
                lines = block.splitlines()
                port = device = None
                for line in lines:
                    if line.startswith("Hardware Port:"):
                        port = line.split(":")[1].strip()
                    elif line.startswith("Device:"):
                        device = line.split(":")[1].strip()
                if port and device:
                    interfaces.append((port, device))
        elif system == "Windows":
            output = subprocess.check_output(["netsh", "interface", "show", "interface"], text=True)
            for line in output.splitlines()[3:]:  # skip header
                parts = line.strip().split()
                if len(parts) >= 4:
                    name = " ".join(parts[3:])
                    interfaces.append((name, name))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to list interfaces: {e}")
    return interfaces


def get_active_interface():
    for port, device in list_all_interfaces():
        try:
            ip_output = subprocess.check_output(["ipconfig", "getifaddr", device], text=True).strip()
            if ip_output:
                return port, device
        except subprocess.CalledProcessError:
            continue
    return None, None

def get_current_network_config():
    """Get the current network configuration for the selected interface"""
    selected_interface = interface_var.get()
    if not selected_interface:
        return {"error": "No interface selected"}

    config = {
        "interface": selected_interface,
        "ip": "Not configured",
        "netmask": "Not configured",
        "router": "Not configured",
        "dhcp": "Unknown"
    }

    system = platform.system()

    try:
        if system == "Darwin":
            # Get IP address
            try:
                # Find the device name for the selected interface
                device = None
                for port, dev in list_all_interfaces():
                    if port == selected_interface:
                        device = dev
                        break

                if device:
                    ip_output = subprocess.check_output(["ipconfig", "getifaddr", device], text=True).strip()
                    config["ip"] = ip_output

                    # Get detailed interface info
                    ifconfig_output = subprocess.check_output(["ifconfig", device], text=True)
                    for line in ifconfig_output.splitlines():
                        line = line.strip()
                        if "inet " in line and "127.0.0.1" not in line:
                            parts = line.split()
                            for i, part in enumerate(parts):
                                if part == "netmask" and i + 1 < len(parts):
                                    # Convert hex netmask to dotted decimal
                                    hex_mask = parts[i + 1]
                                    if hex_mask.startswith("0x"):
                                        mask_int = int(hex_mask, 16)
                                        config["netmask"] = f"{(mask_int >> 24) & 255}.{(mask_int >> 16) & 255}.{(mask_int >> 8) & 255}.{mask_int & 255}"

                    # Get router/gateway
                    try:
                        route_output = subprocess.check_output(["route", "get", "default"], text=True)
                        for line in route_output.splitlines():
                            if "gateway:" in line:
                                config["router"] = line.split("gateway:")[1].strip()
                    except subprocess.CalledProcessError:
                        pass

                    # Check if DHCP is enabled
                    try:
                        dhcp_output = subprocess.check_output(["networksetup", "-getinfo", selected_interface], text=True)
                        if "DHCP Configuration" in dhcp_output:
                            config["dhcp"] = "Enabled"
                        elif "Manual Configuration" in dhcp_output:
                            config["dhcp"] = "Disabled (Static)"
                    except subprocess.CalledProcessError:
                        pass

            except subprocess.CalledProcessError:
                pass

        elif system == "Windows":
            try:
                # Get interface configuration
                netsh_output = subprocess.check_output(
                    ["netsh", "interface", "ip", "show", "config", f'name="{selected_interface}"'],
                    text=True
                )

                for line in netsh_output.splitlines():
                    line = line.strip()
                    if "IP Address:" in line:
                        config["ip"] = line.split("IP Address:")[1].strip()
                    elif "Subnet Prefix:" in line:
                        # Extract subnet mask from prefix notation
                        prefix = line.split("Subnet Prefix:")[1].strip()
                        if "/" in prefix:
                            config["netmask"] = prefix.split("/")[1].strip()
                    elif "Default Gateway:" in line:
                        config["router"] = line.split("Default Gateway:")[1].strip()
                    elif "DHCP enabled:" in line:
                        dhcp_status = line.split("DHCP enabled:")[1].strip()
                        config["dhcp"] = "Enabled" if dhcp_status.lower() == "yes" else "Disabled"

            except subprocess.CalledProcessError:
                pass

    except Exception as e:
        config["error"] = f"Failed to get network config: {str(e)}"

    return config

def apply_settings(name, ip_entry, mask_entry, router_entry):
    selected_interface = interface_var.get()
    if not selected_interface:
        messagebox.showerror("Error", "No valid network interface selected.")
        return

    system = platform.system()
    if name.lower() == "dhcp":
        if system == "Darwin":
            cmd = f'networksetup -setdhcp "{selected_interface}"'
        elif system == "Windows":
            cmd = f'netsh interface ip set address "{selected_interface}" dhcp'
    else:
        ip = ip_entry.get()
        mask = mask_entry.get()
        router = router_entry.get()
        for preset in presets:
            if preset[0] == name:
                preset[1] = [ip, mask, router]
        if system == "Darwin":
            cmd = f'networksetup -setmanual "{selected_interface}" {ip} {mask} {router}'
        elif system == "Windows":
            cmd = f'netsh interface ip set address "{selected_interface}" static {ip} {mask} {router}'

    run_with_privileges(cmd)
    save_presets()
    messagebox.showinfo("Success", f"{selected_interface} set to '{name}' profile.")


def rename_preset(old_name, new_name):
    if not new_name or old_name == new_name:
        return
    if any(p[0] == new_name for p in presets):
        messagebox.showerror("Error", f"A preset named '{new_name}' already exists.")
        return
    for preset in presets:
        if preset[0] == old_name:
            preset[0] = new_name
            break
    save_presets()
    update_tabs()

def create_current_config_tab():
    """Create the readonly tab showing current network configuration"""
    global config_tab_frame

    frame = ttk.Frame(notebook)

    # Get current config for display
    config = get_current_network_config()

    # Display fields using same layout as preset tabs
    tk.Label(frame, text="IP Address:").pack()
    ip_display = tk.Entry(frame, state='readonly')
    ip_display.pack()

    tk.Label(frame, text="Subnet Mask:").pack()
    mask_display = tk.Entry(frame, state='readonly')
    mask_display.pack()

    tk.Label(frame, text="Router:").pack()
    router_display = tk.Entry(frame, state='readonly')
    router_display.pack()

    tk.Label(frame, text="DHCP Status:").pack()
    dhcp_display = tk.Entry(frame, state='readonly')
    dhcp_display.pack()

    tk.Label(frame, text="Interface:").pack()
    interface_display = tk.Entry(frame, state='readonly')
    interface_display.pack()

    # Store references to entry widgets for refresh functionality
    frame.ip_display = ip_display
    frame.mask_display = mask_display
    frame.router_display = router_display
    frame.dhcp_display = dhcp_display
    frame.interface_display = interface_display
    config_tab_frame = frame

    # Refresh button (same style as Apply Preset button)
    refresh_btn = tk.Button(frame, text="🔄 Refresh Configuration",
                           command=lambda: refresh_config_display_entries(frame))
    refresh_btn.pack(pady=10)

    # Initial load of config
    refresh_config_display_entries(frame)

    return frame

def refresh_config_display_entries(frame):
    """Refresh the configuration display in entry widgets"""
    config = get_current_network_config()

    # Update each entry widget
    if hasattr(frame, 'ip_display'):
        frame.ip_display.config(state='normal')
        frame.ip_display.delete(0, tk.END)
        frame.ip_display.insert(0, config.get('ip', 'Not configured'))
        frame.ip_display.config(state='readonly')

    if hasattr(frame, 'mask_display'):
        frame.mask_display.config(state='normal')
        frame.mask_display.delete(0, tk.END)
        frame.mask_display.insert(0, config.get('netmask', 'Not configured'))
        frame.mask_display.config(state='readonly')

    if hasattr(frame, 'router_display'):
        frame.router_display.config(state='normal')
        frame.router_display.delete(0, tk.END)
        frame.router_display.insert(0, config.get('router', 'Not configured'))
        frame.router_display.config(state='readonly')

    if hasattr(frame, 'dhcp_display'):
        frame.dhcp_display.config(state='normal')
        frame.dhcp_display.delete(0, tk.END)
        frame.dhcp_display.insert(0, config.get('dhcp', 'Unknown'))
        frame.dhcp_display.config(state='readonly')

    if hasattr(frame, 'interface_display'):
        frame.interface_display.config(state='normal')
        frame.interface_display.delete(0, tk.END)
        frame.interface_display.insert(0, config.get('interface', 'No interface selected'))
        frame.interface_display.config(state='readonly')

def update_tabs():
    for tab in notebook.tabs():
        notebook.forget(tab)

    # Add the current config tab first
    config_frame = create_current_config_tab()
    notebook.add(config_frame, text="Current Config")

    # Add preset tabs
    for name, values in presets:
        create_tab(name, values)

def create_tab(name, values):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=name)

    if values is None:
        tk.Label(frame, text="DHCP mode - no fields to edit.", font=("Arial", 10)).pack(pady=20)
        tk.Button(frame, text="Apply DHCP", command=lambda n=name: apply_settings(n, None, None, None)).pack(pady=10)
    else:
        ip_var = tk.StringVar(value=values[0])
        mask_var = tk.StringVar(value=values[1])
        router_var = tk.StringVar(value=values[2])

        tk.Label(frame, text="IP Address:").pack()
        ip_entry = tk.Entry(frame, textvariable=ip_var)
        ip_entry.pack()

        tk.Label(frame, text="Subnet Mask:").pack()
        mask_entry = tk.Entry(frame, textvariable=mask_var)
        mask_entry.pack()

        tk.Label(frame, text="Router:").pack()
        router_entry = tk.Entry(frame, textvariable=router_var)
        router_entry.pack()

        tk.Label(frame, text="Rename Preset:").pack()
        rename_var = tk.StringVar(value=name)
        rename_entry = tk.Entry(frame, textvariable=rename_var)
        rename_entry.pack(pady=5)

        # Rename on losing focus
        rename_entry.bind("<FocusOut>", lambda e, old=name, entry=rename_entry: rename_preset(old, entry.get()))

        apply_btn = tk.Button(frame, text="Apply Preset", command=lambda n=name, i=ip_entry, m=mask_entry, r=router_entry: apply_settings(n, i, m, r))
        apply_btn.pack(pady=10)

# GUI setup
root = tk.Tk()
root.title("macOS IP Preset Selector")

interfaces = list_all_interfaces()
active_port, _ = get_active_interface()
interface_names = [p for p, d in interfaces]

tk.Label(root, text="Select Network Interface:").pack(pady=5)
interface_var = tk.StringVar(value=active_port if active_port else interface_names[0])
interface_menu = ttk.Combobox(root, textvariable=interface_var, values=interface_names, state="readonly")
interface_menu.pack(pady=5)

notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, fill='both', expand=True)

# Global variable to store config tab reference
config_tab_frame = None

def on_tab_changed(event):
    """Handle tab selection change"""
    global config_tab_frame
    selected_tab = event.widget.select()
    tab_text = event.widget.tab(selected_tab, "text")

    # If the current config tab is selected, refresh it
    if tab_text == "📊 Current Config" and config_tab_frame:
        refresh_config_display_entries(config_tab_frame)

# Bind tab change event
notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

# Create tabs based on presets (this will create the config tab first)
update_tabs()

root.mainloop()
