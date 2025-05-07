#!/opt/local/bin/python3.11

import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

presets = {
    "Alouette": ["192.168.1.149", "255.255.255.0", "192.168.1.1"],
    "DHCP": None,
    "Backup 1": ["10.0.0.100", "255.255.255.0", "10.0.0.1"],
    "Backup 2": ["172.16.0.50", "255.255.0.0", "172.16.0.1"]
}

last_config = {}  # interface -> (None for DHCP, or [IP, Mask, Router])

def run_with_privileges(command):
    escaped_command = command.replace('"', '\\"')
    script = f'do shell script "{escaped_command}" with administrator privileges'
    try:
        subprocess.run(["osascript", "-e", script], check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Permission Denied", f"Command failed or was cancelled:\n{command}")
        exit(1)

def list_all_interfaces():
    interfaces = []
    try:
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

def get_current_config(interface):
    try:
        output = subprocess.check_output(["networksetup", "-getinfo", interface], text=True)
        lines = output.splitlines()
        ip = subnet = router = None
        using_dhcp = False
        for line in lines:
            if "DHCP Configuration" in line or "DHCP" in line:
                using_dhcp = True
            elif line.startswith("IP address:"):
                ip = line.split(":")[1].strip()
            elif line.startswith("Subnet mask:"):
                subnet = line.split(":")[1].strip()
            elif line.startswith("Router:"):
                router = line.split(":")[1].strip()
        return None if using_dhcp else [ip, subnet, router]
    except Exception as e:
        print(f"Warning: Failed to get current config for {interface}: {e}")
        return None

def apply_settings(old_name, name_entry, ip_entry, mask_entry, router_entry, tab_index, revert_btn):
    new_name = name_entry.get().strip()
    if not new_name:
        messagebox.showerror("Error", "Preset name cannot be empty.")
        return

    selected_interface = interface_var.get()
    matching = next((d for p, d in interfaces if p == selected_interface), None)
    if not matching:
        messagebox.showerror("Error", "No valid network interface selected.")
        return

    # Store current config before changing
    prev = get_current_config(selected_interface)
    last_config[selected_interface] = prev
    revert_btn["state"] = tk.NORMAL

    if new_name.lower() == "dhcp":
        cmd = f'networksetup -setdhcp "{selected_interface}"'
        presets[new_name] = None
    else:
        ip = ip_entry.get()
        mask = mask_entry.get()
        router = router_entry.get()
        presets[new_name] = [ip, mask, router]
        cmd = f'networksetup -setmanual "{selected_interface}" {ip} {mask} {router}'

    if new_name != old_name:
        presets.pop(old_name)
        notebook.tab(tab_index, text=new_name)

    run_with_privileges(cmd)
    messagebox.showinfo("Success", f"{selected_interface} set to '{new_name}' profile.")

def revert_settings(interface):
    prev = last_config.get(interface)
    if prev is None:
        cmd = f'networksetup -setdhcp "{interface}"'
    else:
        ip, mask, router = prev
        cmd = f'networksetup -setmanual "{interface}" {ip} {mask} {router}'
    run_with_privileges(cmd)
    messagebox.showinfo("Reverted", f"{interface} has been reverted to the previous configuration.")

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

tab_refs = {}

for i, (name, values) in enumerate(presets.items()):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=name)
    tab_refs[name] = frame

    name_var = tk.StringVar(value=name)

    tk.Label(frame, text="Preset Name:").pack()
    name_entry = tk.Entry(frame, textvariable=name_var)
    name_entry.pack()

    revert_btn = tk.Button(frame, text="Revert", state=tk.DISABLED,
                           command=lambda iface=interface_var.get(): revert_settings(iface))
    revert_btn.pack(pady=(5, 5))

    if values is None:
        tk.Label(frame, text="DHCP mode - no fields to edit.", font=("Arial", 10)).pack(pady=20)
        tk.Button(
            frame, text="Apply DHCP",
            command=lambda n=name, ne=name_entry, i=i, rb=revert_btn:
                apply_settings(n, ne, None, None, None, i, rb)
        ).pack(pady=10)
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

        tk.Button(
            frame, text="Apply Preset",
            command=lambda n=name, ne=name_entry, ip=ip_entry, m=mask_entry, r=router_entry, i=i, rb=revert_btn:
                apply_settings(n, ne, ip, m, r, i, rb)
        ).pack(pady=10)

root.mainloop()
