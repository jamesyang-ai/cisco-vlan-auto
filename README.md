# Cisco Switch VLAN & Hostname Automation Tool

This is a Cisco switch configuration automation and compliance auditing system developed based on Python, Tkinter, and Netmiko. The project supports closed-loop interactions with real or virtual Cisco devices within a VMware Workstation + EVE-NG simulation environment.

## Core Features
1. **Graphical User Interface (GUI)**: Developed using Tkinter, supporting dynamic adjustments to hostnames and VLAN lists (editable via double-clicking cells).
2. **Decoupled Multi-Behavior Control**:
   - **Configuration Deployment**: Automatically elevates privileges, deploys hostname changes and bulk VLANs, and persists changes to NVRAM (`write memory`).
   - **Independent Backup**: One-click remote retrieval of the `running-config`, automatically generating a secure local backup file named with the format `[Hostname]_[Timestamp]`.
   - **Closed-Loop Compliance Verification**: Dedicated independent audit button. It recaptures the full status of the device and utilizes regular expressions for dual-track comparison. If inconsistencies are found, the GUI proactively triggers a warning pop-up reading **"Non-standard configuration detected"**.

## Quick Start
```bash
# 1. Clone the public repository
git clone <Your-GitHub-Repository-URL>
cd cisco-vlan-automation

# 2. Install core Netmiko dependency
pip install netmiko

# 3. Run the main program
python main.py
```
