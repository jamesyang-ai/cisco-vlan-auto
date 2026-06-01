import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from netmiko import ConnectHandler
from datetime import datetime
import os, re

# Predefined standard core VLAN requirements / 预设的硬性标准 VLAN 需求清单
DEFAULT_VLANS = [("10", "VLAN_DATOS"), ("20", "VLAN_VOICE"), ("50", "VLAN_SECURITY")]

def get_config():
    """Extracts target hostname and target VLAN list from the GUI fields. / 从 GUI 提取主机名和 VLAN 列表。"""
    host = entry_host.get().strip()
    vlans = {}
    for item in tree.get_children():
        v = tree.item(item)['values']
        if str(v[0]).strip():
            vlans[str(v[0]).strip()] = str(v[1]).strip()
    return host, vlans

def get_dev():
    """Constructs Netmiko connection arguments dictionary. / 构建 Netmiko 底层连接参数字典。"""
    return {
        'device_type': 'cisco_ios', 'host': entry_ip.get().strip(),
        'username': entry_user.get().strip(), 'password': entry_pass.get().strip(),
        'secret': entry_secret.get().strip(), 'port': 22, 'global_delay_factor': 2,
    }

def run_deploy():
    """Button 1: Provision configuration arrays and write to NVRAM. / 按钮 1：批量下发配置并保存至 NVRAM。"""
    try:
        net = ConnectHandler(**get_dev()); net.enable()
        host = entry_host.get().strip()
        net.send_config_set([f"hostname {host}"])
        net.set_base_prompt() # Sync Netmiko prompt engine / 同步提示符缓存防止卡死超时
        tgt_host, exp_vlans = get_config()
        cmds = []
        for vid, vname in exp_vlans.items():
            cmds.extend([f"vlan {vid}", f"name {vname}", "exit"])
        net.send_config_set(cmds)
        net.send_command("write memory")
        net.disconnect()
        messagebox.showinfo("Success", "Configuration successfully deployed and saved to NVRAM!")
    except Exception as e: messagebox.showerror("Error", str(e))

def run_backup():
    """Button 2: Standalone runner to fetch running-config and save locally. / 按钮 2：独立获取运行配置并本地备份。"""
    try:
        net = ConnectHandler(**get_dev()); net.enable()
        p = net.find_prompt().replace("#", "").replace(">", "").strip()
        cfg = net.send_command("show running-config")
        net.disconnect()
        os.makedirs("backups", exist_ok=True)
        path = f"backups/backup_{p}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(path, "w", encoding="utf-8") as f: f.write(cfg)
        messagebox.showinfo("Success", f"Configuration successfully backed up to:\n{path}")
    except Exception as e: messagebox.showerror("Error", str(e))

def run_audit():
    """Button 3: Closed-loop regex audit for standard compliance check. / 按钮 3：闭环双轨正则审计，校验不一致偏差。"""
    try:
        net = ConnectHandler(**get_dev()); net.enable()
        act_h = net.find_prompt().replace("#", "").replace(">", "").strip()
        v_out = net.send_command("show vlan brief")
        net.disconnect()
        tgt_host, exp_vlans = get_config()
        devs = []
        if act_h != tgt_host: devs.append(f"• Hostname: Expected '{tgt_host}', Actual '{act_h}'")
        for vid, vname in exp_vlans.items():
            m = re.search(rf"^{vid}\s+(\S+)\s+active", v_out, re.MULTILINE)
            if not m: devs.append(f"• VLAN {vid}: Missing or Inactive")
            elif m.group(1) != vname: devs.append(f"• VLAN {vid} Name: Expected '{vname}', Actual '{m.group(1)}'")
        if devs: messagebox.showwarning("Audit Warning", "Non-Standard Configuration Found:\n\n" + "\n".join(devs))
        else: messagebox.showinfo("Audit Passed", "Perfect! Switch states are 100% compliant.")
    except Exception as e: messagebox.showerror("Error", str(e))

# ==================== Graphical Interface Layout (Fixed Grid System) ====================
root = tk.Tk(); root.title("Cisco Tool"); root.geometry("520x760")

# 1. Connectivity Parameters Section (Using standard grid for exact labels alignment)
f1 = tk.LabelFrame(root, text=" 1. Connectivity Parameters (EVE-NG Bridge) ", padx=10, pady=5)
f1.pack(fill="x", padx=15, pady=5)

tk.Label(f1, text="Switch IP Address:").grid(row=0, column=0, sticky="w", pady=2)
entry_ip = tk.Entry(f1); entry_ip.insert(0, "192.168.137.10")
entry_ip.grid(row=0, column=1, sticky="we", padx=5, pady=2)

tk.Label(f1, text="SSH Username:").grid(row=1, column=0, sticky="w", pady=2)
entry_user = tk.Entry(f1); entry_user.insert(0, "admin")
entry_user.grid(row=1, column=1, sticky="we", padx=5, pady=2)

tk.Label(f1, text="SSH Password:").grid(row=2, column=0, sticky="w", pady=2)
entry_pass = tk.Entry(f1, show="*")
entry_pass.grid(row=2, column=1, sticky="we", padx=5, pady=2)

tk.Label(f1, text="Enable Secret (Optional):").grid(row=3, column=0, sticky="w", pady=2)
entry_secret = tk.Entry(f1, show="*")
entry_secret.grid(row=3, column=1, sticky="we", padx=5, pady=2)
f1.columnconfigure(1, weight=1) # Makes entry inputs horizontally auto-resizable

# 2. Hostname Settings Section
f2 = tk.LabelFrame(root, text=" 2. Hostname Settings ", padx=10, pady=5)
f2.pack(fill="x", padx=15, pady=5)
tk.Label(f2, text="Desired Hostname:").grid(row=0, column=0, sticky="w", pady=2)
entry_host = tk.Entry(f2); entry_host.insert(0, "AUTOMATED_SWITCH")
entry_host.grid(row=0, column=1, sticky="we", padx=5, pady=2)
f2.columnconfigure(1, weight=1)

# 3. VLAN Profile Grid Section
f3 = tk.LabelFrame(root, text=" 3. VLAN Profiles (Double-click cell to edit) ", padx=10, pady=5)
f3.pack(fill="both", expand=True, padx=15, pady=5)
tree = ttk.Treeview(f3, columns=('id', 'name'), show='headings', height=4)
tree.heading('id', text='VLAN ID'); tree.heading('name', text='VLAN Name')
tree.column('id', width=100, anchor="center")
tree.pack(fill="both", expand=True)
for v in DEFAULT_VLANS: tree.insert('', tk.END, values=v)

def on_edit(e):
    item = tree.selection()
    if item:
        col = int(tree.identify_column(e.x).replace('#', '')) - 1
        old = tree.item(item)['values'][col]
        new = simpledialog.askstring("Edit Profile", "Enter new expected target value:", initialvalue=old)
        if new:
            vals = list(tree.item(item)['values']); vals[col] = new; tree.item(item, values=vals)
tree.bind("<Double-1>", on_edit)

status_label = tk.Label(root, text="System ready, waiting for actions...", fg="gray", font=("Arial", 9, "italic"))
status_label.pack(pady=3)

# 4. Pipelines Operational Control Buttons
tk.Button(root, text="🚀 1. Deploy Configuration & Save", font=("Arial", 11, "bold"), bg="#0284C7", fg="white", command=run_deploy, pady=4).pack(fill="x", padx=15, pady=2)
tk.Button(root, text="💾 2. Standalone History Backup", font=("Arial", 11, "bold"), bg="#8B5CF6", fg="white", command=run_backup, pady=4).pack(fill="x", padx=15, pady=2)
tk.Button(root, text="🔍 3. Compliance Verification (Audit)", font=("Arial", 11, "bold"), bg="#10B981", fg="white", command=run_audit, pady=4).pack(fill="x", padx=15, pady=4)

root.mainloop()
