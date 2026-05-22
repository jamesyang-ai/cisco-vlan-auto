import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from netmiko import ConnectHandler
from datetime import datetime
import os, re

# Default assignment constraints
DEFAULT_VLANS = [
    {"id": "10", "name": "VLAN_DATOS"},
    {"id": "20", "name": "VLAN_VOICE"},
    {"id": "50", "name": "VLAN_SECURITY"}
]

def get_config():
    host = entry_host.get().strip()
    vlans = {}
    for item in tree.get_children():
        v = tree.item(item)['values']
        if str(v[0]).strip():
            vlans[str(v[0]).strip()] = str(v[1]).strip()
    return host, vlans

def get_dev():
    return {
        'device_type': 'cisco_ios',
        'host': entry_ip.get().strip(),
        'username': entry_user.get().strip(),
        'password': entry_pass.get().strip(),
        'secret': entry_secret.get().strip(),
        'port': 22,
        'global_delay_factor': 2,
    }

def run_deploy_config():
    ip = entry_ip.get().strip()
    tgt_host, exp_vlans = get_config()
    if not ip or not entry_user.get() or not entry_pass.get():
        messagebox.showerror("Error", "Missing IP, Username or Password!")
        return
    if not tgt_host:
        messagebox.showerror("Error", "Hostname cannot be empty!")
        return
    status_label.config(text="Deploying configuration...", fg="blue")
    root.update()
    try:
        net = ConnectHandler(**get_dev())
        net.enable()
        net.send_config_set([f"hostname {tgt_host}"])
        net.set_base_prompt()
        cmds = []
        for vid, vname in exp_vlans.items():
            cmds.extend([f"vlan {vid}", f"name {vname}", "exit"])
        net.send_config_set(cmds)
        net.send_command("write memory")
        net.disconnect()
        status_label.config(text="✓ Deployed successfully!", fg="green")
        messagebox.showinfo("Success", "Configuration saved to NVRAM!")
    except Exception as e:
        status_label.config(text="Deployment failed!", fg="red")
        messagebox.showerror("Error", str(e))

def run_independent_backup():
    if not entry_ip.get().strip():
        messagebox.showerror("Error", "Missing Switch IP!")
        return
    status_label.config(text="Backing up running-config...", fg="purple")
    root.update()
    try:
        net = ConnectHandler(**get_dev())
        net.enable()
        prompt = net.find_prompt().replace("#", "").replace(">", "").strip()
        cfg = net.send_command("show running-config")
        net.disconnect()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("backups", exist_ok=True)
        path = os.path.join("backups", f"backup_{prompt}_{ts}.txt")
        with open(path, "w", encoding="utf-8") as f:
            f.write(cfg)
        status_label.config(text="✓ Backup completed!", fg="green")
        messagebox.showinfo("Success", f"Saved to: {path}")
    except Exception as e:
        status_label.config(text="Backup failed!", fg="red")
        messagebox.showerror("Error", str(e))

def run_independent_audit():
    tgt_host, exp_vlans = get_config()
    if not entry_ip.get().strip():
        messagebox.showerror("Error", "Missing Switch IP!")
        return
    status_label.config(text="Auditing device compliance...", fg="#D97706")
    root.update()
    try:
        net = ConnectHandler(**get_dev())
        net.enable()
        act_host = net.find_prompt().replace("#", "").replace(">", "").strip()
        vlan_out = net.send_command("show vlan brief")
        net.disconnect()
        devs = []
        if act_host != tgt_host:
            devs.append(f"• Hostname: Expected '{tgt_host}', Actual '{act_host}'")
        for vid, vname in exp_vlans.items():
            match = re.search(rf"^{vid}\s+(\S+)\s+active", vlan_out, re.MULTILINE)
            if not match:
                devs.append(f"• VLAN {vid}: Missing or Inactive")
            elif match.group(1) != vname:
                devs.append(f"• VLAN {vid} Name: Expected '{vname}', Actual '{match.group(1)}'")
        if devs:
            status_label.config(text="⚠️ Non-Standard Configuration!", fg="red")
            messagebox.showwarning("Audit Warning", "Non-Standard Configuration Found:\n\n" + "\n".join(devs))
        else:
            status_label.config(text="✓ 100% Fully Compliant!", fg="green")
            messagebox.showinfo("Audit Passed", "Perfect! All checks are 100% compliant.")
    except Exception as e:
        status_label.config(text="Audit interrupted!", fg="red")
        messagebox.showerror("Error", str(e))

# --- Tkinter GUI Layout ---
root = tk.Tk()
root.title("Cisco Automation & Audit System")
root.geometry("520(x)680".replace("(x)", "x"))

f_conn = tk.LabelFrame(root, text=" 1. Connectivity (EVE-NG) ", padx=10, pady=5)
f_conn.pack(fill="x", padx=15, pady=5)
labels = ["Switch IP:", "Username:", "Password:", "Enable Secret (Opt):"]
entries = []
for i, l in enumerate(labels):
    tk.Label(f_conn, text=l).grid(row=i, column=0, sticky="w")
    e = tk.Entry(f_conn, show="*" if "Pass" in l or "Secret" in l else "")
    e.grid(row=i, column=1, pady=2, sticky="we")
    entries.append(e)
entry_ip, entry_user, entry_pass, entry_secret = entries
entry_ip.insert(0, "192.168.137.10")
entry_user.insert(0, "admin")

f_glob = tk.LabelFrame(root, text=" 2. Hostname ", padx=10, pady=5)
f_glob.pack(fill="x", padx=15, pady=5)
tk.Label(f_glob, text="Target Hostname:").grid(row=0, column=0, sticky="w")
entry_host = tk.Entry(f_glob)
entry_host.insert(0, "AUTOMATED_SWITCH")
entry_host.grid(row=0, column=1, pady=2, sticky="we")

f_vlan = tk.LabelFrame(root, text=" 3. VLAN Profile (Double-click cell to edit) ", padx=10, pady=5)
f_vlan.pack(fill="both", expand=True, padx=15, pady=5)
tree = ttk.Treeview(f_vlan, columns=('id', 'name'), show='headings', height=4)
tree.heading('id', text='VLAN ID')
tree.heading('name', text='VLAN Name')
tree.column('id', width=100, anchor="center")
tree.pack(fill="both", expand=True)
for v in DEFAULT_VLANS:
    tree.insert('', tk.END, values=(v["id"], v["name"]))

def on_edit(event):
    item = tree.selection()
    if not item: return
    col = int(tree.identify_column(event.x).replace('#', '')) - 1
    old = tree.item(item)['values'][col]
    new = simpledialog.askstring("Edit Profile", "Enter new value:", initialvalue=old)
    if new is not None:
        v = list(tree.item(item)['values'])
        v[col] = new
        tree.item(item, values=v)
tree.bind("<Double-1>", on_edit)

status_label = tk.Label(root, text="Ready...", fg="gray", font=("Arial", 10, "italic"))
status_label.pack(pady=3)

tk.Button(root, text="🚀 1. Deploy & Save NVRAM", font=("Arial", 11, "bold"), bg="#0284C7", fg="white", command=run_deploy_config, pady=4).pack(fill="x", padx=15, pady=2)
tk.Button(root, text="💾 2. Independent Backup", font=("Arial", 11, "bold"), bg="#8B5CF6", fg="white", command=run_independent_backup, pady=4).pack(fill="x", padx=15, pady=2)
tk.Button(root, text="🔍 3. Compliance Verification (Audit)", font=("Arial", 11, "bold"), bg="#10B981", fg="white", command=run_independent_audit, pady=4).pack(fill="x", padx=15, pady=4)

root.mainloop()
