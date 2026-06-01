import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
from netmiko import ConnectHandler
from datetime import datetime
import os, re

# Predefined standard core VLAN requirements / 预设的硬性标准 VLAN 需求清单
DEFAULT_VLANS = [("10", "VLAN_DATOS"), ("20", "VLAN_VOICE"), ("50", "VLAN_SECURITY")]

def get_dev():
    """Constructs Netmiko connection arguments dictionary. / 构建 Netmiko 底层连接参数字典。"""
    return {
        'device_type': 'cisco_ios', 'host': entry_ip.get().strip(),
        'username': entry_user.get().strip(), 'password': entry_pass.get().strip(),
        'secret': entry_secret.get().strip(), 'port': 22, 'global_delay_factor': 2,
    }

def run_deploy():
    """Button 1: Provision configuration arrays and write to NVRAM. / 按钮 1：批量下发配置并强制保存至 NVRAM。"""
    try:
        net = ConnectHandler(**get_dev()); net.enable() # Login & elevate / 登录并提权
        host = entry_host.get().strip()
        net.send_config_set([f"hostname {host}"]) # Deploys hostname / 下发修改主机名
        net.set_base_prompt() # Sync Netmiko prompt engine / 关键点：同步提示符缓存防止卡死超时
        cmds = []
        for item in tree.get_children():
            v = tree.item(item)['values']
            cmds.extend([f"vlan {v[0]}", f"name {v[1]}", "exit"])
        net.send_config_set(cmds) # Deploys VLAN batch / 批量下发 VLAN 清单
        net.send_command("write memory") # Permanent flash / 强制持久化保存
        net.disconnect()
        messagebox.showinfo("Success", "Configuration successfully deployed and saved to NVRAM!")
    except Exception as e: messagebox.showerror("Error", str(e))

def run_backup():
    """Button 2: Standalone runner to fetch running-config and save locally. / 按钮 2：独立获取运行配置并本地备份。"""
    try:
        net = ConnectHandler(**get_dev()); net.enable()
        p = net.find_prompt().replace("#", "").replace(">", "").strip() # Capture hostname / 实时抓取真实名
        cfg = net.send_command("show running-config")
        net.disconnect()
        os.makedirs("backups", exist_ok=True)
        path = f"backups/backup_{p}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(path, "w", encoding="utf-8") as f: f.write(cfg) # Flat file archival / 归档为本地文本
        messagebox.showinfo("Success", f"Configuration successfully backed up to:\n{path}")
    except Exception as e: messagebox.showerror("Error", str(e))

def run_audit():
    """Button 3: Closed-loop regex audit for standard compliance check. / 按钮 3：闭环双轨正则审计，校验不一致偏差。"""
    try:
        net = ConnectHandler(**get_dev()); net.enable()
        act_h = net.find_prompt().replace("#", "").replace(">", "").strip()
        v_out = net.send_command("show vlan brief") # Captures active databases / 抓取实时状态
        net.disconnect()
        devs = [] # Discovered configuration deviations / 偏差收集器
        if act_h != entry_host.get().strip(): devs.append(f"• Hostname: Expected '{entry_host.get()}', Actual '{act_h}'")
        for item in tree.get_children():
            v = tree.item(item)['values']
            m = re.search(rf"^{v[0]}\s+(\S+)\s+active", v_out, re.MULTILINE) # Regular expression parsing / 正则过滤
            if not m: devs.append(f"• VLAN {v[0]}: Missing or Inactive")
            elif m.group(1) != str(v[1]): devs.append(f"• VLAN {v[0]} Name: Expected '{v[1]}', Actual '{m.group(1)}'")
        if devs: messagebox.showwarning("Audit Warning", "Non-Standard Configuration Found:\n\n" + "\n".join(devs))
        else: messagebox.showinfo("Audit Passed", "Perfect! Switch states are 100% compliant.")
    except Exception as e: messagebox.showerror("Error", str(e))

# ==================== High Condensed Graphical Interface Layout / 极致精简前端 UI 布局 ====================
root = tk.Tk(); root.title("Cisco Tool"); root.geometry("400x570")

f1 = tk.LabelFrame(root, text=" 1. Connectivity Parameters "); f1.pack(fill="x", padx=10, pady=4)
entry_ip = tk.Entry(f1); entry_ip.insert(0, "192.168.137.10"); entry_ip.pack(fill="x", padx=5, pady=2)
entry_user = tk.Entry(f1); entry_user.insert(0, "admin"); entry_user.pack(fill="x", padx=5, pady=2)
entry_pass = tk.Entry(f1, show="*"); entry_pass.pack(fill="x", padx=5, pady=2)
entry_secret = tk.Entry(f1, show="*"); entry_secret.pack(fill="x", padx=5, pady=2) # Enable secret field / 特权密码框

f2 = tk.LabelFrame(root, text=" 2. Desired Hostname "); f2.pack(fill="x", padx=10, pady=4)
entry_host = tk.Entry(f2); entry_host.insert(0, "AUTOMATED_SWITCH"); entry_host.pack(fill="x", padx=5, pady=2)

f3 = tk.LabelFrame(root, text=" 3. VLAN Profiles (Double-click grid to edit) "); f3.pack(fill="both", expand=True, padx=10, pady=4)
tree = ttk.Treeview(f3, columns=('id', 'name'), show='headings', height=4)
tree.heading('id', text='VLAN ID'); tree.heading('name', text='VLAN Name')
tree.column('id', width=80, anchor="center"); tree.pack(fill="both", expand=True)
for v in DEFAULT_VLANS: tree.insert('', tk.END, values=v)

def on_edit(e):
    """Triggers modifier loops upon double clicking target grids. / 双击任意表格单元格动态修改期望值。"""
    item = tree.selection()
    if item:
        col = int(tree.identify_column(e.x).replace('#', '')) - 1
        new = simpledialog.askstring("Edit Profile", "Enter new expected target value:")
        if new:
            vals = list(tree.item(item)['values']); vals[col] = new; tree.item(item, values=vals)
tree.bind("<Double-1>", on_edit)

# Operational execution actions mapped into discrete pipelines / 相互独立的功能控制按钮管道
tk.Button(root, text="🚀 1. Deploy Configuration & Save", font=("Arial", 10, "bold"), bg="#0284C7", fg="white", command=run_deploy, pady=3).pack(fill="x", padx=10, pady=2)
tk.Button(root, text="💾 2. Standalone History Backup", font=("Arial", 10, "bold"), bg="#8B5CF6", fg="white", command=run_backup, pady=3).pack(fill="x", padx=10, pady=2)
tk.Button(root, text="🔍 3. Compliance Verification (Audit)", font=("Arial", 10, "bold"), bg="#10B981", fg="white", command=run_independent_audit if 'run_independent_audit' in globals() else run_audit, pady=3).pack(fill="x", padx=10, pady=4)

root.mainloop()
