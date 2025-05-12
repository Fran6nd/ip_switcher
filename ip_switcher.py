#!/opt/local/bin/python3.11

import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import json
import platform
import sys


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

def update_tabs():
    for tab in notebook.tabs():
        notebook.forget(tab)
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

# Create tabs based on presets
for name, values in presets:
    create_tab(name, values)

root.mainloop()
