#!/opt/local/bin/python3.11

import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# Initial IP presets (modifiable in UI)
presets = {
    "Alouette": ["192.168.1.149", "255.255.255.0", "192.168.1.1"],
    "DHCP": None,
    "Backup 1": ["10.0.0.100", "255.255.255.0", "10.0.0.1"],
    "Backup 2": ["172.16.0.50", "255.255.0.0", "172.16.0.1"]
}

def run_with_privileges(command):
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

def apply_settings(name, ip_entry, mask_entry, router_entry):
    port_name, _ = get_active_interface()
    if not port_name:
        messagebox.showerror("Error", "No active network interface found.")
        return

    if name.lower() == "dhcp":
        cmd = f'networksetup -setdhcp "{port_name}"'
    else:
        ip = ip_entry.get()
        mask = mask_entry.get()
        router = router_entry.get()
        presets[name] = [ip, mask, router]
        cmd = f'networksetup -setmanual "{port_name}" {ip} {mask} {router}'

    run_with_privileges(cmd)
    messagebox.showinfo("Success", f"{port_name} set to '{name}' profile.")

# GUI setup
root = tk.Tk()
root.title("macOS IP Preset Selector")

interface_name, _ = get_active_interface()
if interface_name:
    root.title(f"IP Presets - Interface: {interface_name}")

notebook = ttk.Notebook(root)
notebook.pack(padx=10, pady=10, fill='both', expand=True)

for name, values in presets.items():
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

        tk.Button(frame, text="Apply Preset", command=lambda n=name, i=ip_entry, m=mask_entry, r=router_entry: apply_settings(n, i, m, r)).pack(pady=10)

root.mainloop()
