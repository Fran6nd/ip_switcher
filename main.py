#!/opt/local/bin/python3.11

import subprocess
import tkinter as tk
from tkinter import messagebox

# Your static IP presets: name -> [IP, Subnet Mask, Router]
presets = {
    "Alouette": ["192.168.1.149", "255.255.255.0", "192.168.1.1"],
    "DHCP": None
}

def run_with_privileges(command):
    """
    Runs a shell command with macOS admin rights using osascript
    """
    escaped_command = command.replace('"', '\\"')
    script = f'do shell script "{escaped_command}" with administrator privileges'
    try:
        subprocess.run(["osascript", "-e", script], check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Permission Denied", f"Command failed or was cancelled:\n{command}")
        exit(1)

def get_active_interface():
    try:
        output = subprocess.check_output(["networksetup", "-listallhardwareports"], text=True)
        blocks = output.strip().split("\n\n")
        for block in blocks:
            lines = block.splitlines()
            if len(lines) < 3:
                continue
            name_line = next((l for l in lines if l.startswith("Device: ")), None)
            port_line = next((l for l in lines if l.startswith("Hardware Port: ")), None)
            if name_line and port_line:
                device = name_line.split(":")[1].strip()
                port_name = port_line.split(":")[1].strip()
                try:
                    ip_output = subprocess.check_output(["ipconfig", "getifaddr", device], text=True).strip()
                    if ip_output:
                        return port_name, device
                except subprocess.CalledProcessError:
                    continue
    except Exception as e:
        messagebox.showerror("Error", f"Failed to detect active interface: {e}")
    return None, None

def apply_preset():
    try:
        selected = listbox.get(listbox.curselection())
    except tk.TclError:
        messagebox.showwarning("No Selection", "Please select a preset.")
        return

    port_name, _ = get_active_interface()
    if not port_name:
        messagebox.showerror("Error", "No active network interface found.")
        return

    if presets[selected] is None:
        cmd = f'networksetup -setdhcp "{port_name}"'
    else:
        ip, subnet, router = presets[selected]
        cmd = f'networksetup -setmanual "{port_name}" {ip} {subnet} {router}'

    run_with_privileges(cmd)
    messagebox.showinfo("Success", f"{port_name} set to '{selected}' profile.")

# GUI Setup
root = tk.Tk()

interface_name, device = get_active_interface()
title = f"macOS IP Preset Selector"
if interface_name:
    title += f" - Interface: {interface_name}"
root.title(title)

tk.Label(root, text="Select an IP preset:").pack(pady=5)

listbox = tk.Listbox(root, height=len(presets), exportselection=False)
for preset in presets.keys():
    listbox.insert(tk.END, preset)
listbox.pack(padx=10, pady=10)

apply_btn = tk.Button(root, text="Apply Preset", command=apply_preset)
apply_btn.pack(pady=10)

# Start GUI
root.mainloop()
