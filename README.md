------------------------------
## 🌐 Cisco Network Automation & Compliance Audit System - User Guide
Deploying, backing up, and auditing Cisco switches using main.py and managing version control via sync_to_github.py. 
------------------------------
## Prerequisites
Before running the scripts, ensure your local environment and simulation topology meet the following enterprise netdevops specifications: 
## 1. Python Dependencies Installation
Install the industry-standard Netmiko library via your terminal: 

pip install netmiko

## 2. EVE-NG Network Bridge

* Connect the Cisco Switch's management port (e.g., Ethernet0/0) to Management(Cloud0) in EVE-NG. 
* Ensure your local PC can successfully ping the switch IP (Default: 192.168.43.101). 

## 3. Cisco Switch Initial Setup
The switch must have SSH enabled and a privilege password configured. Paste the following bootstrap commands onto your switch CLI: 

enable
configure terminal
vtp mode transparent
interface Ethernet0/0
no switchport
ip address 192.168.43.101 255.255.255.0
no shutdown
exit
username admin privilege 15 secret cisco
#enable secret cisco
crypto key generate rsa label SSH_KEY modulus 1024
line vty 0 4
login local
transport input ssh
end
write memory

------------------------------
## Step-by-Step Operations
Run the main application by executing python main.py in your terminal to launch the graphical user interface. 
## Step 1: Input Device Parameters & Edit VLAN Target Profile

   1. Fill Connectivity Fields: Verify the Switch IP, Username, Password, and Enable Secret match your current hardware configurations. 
   2. Define Hostname: Input your target hostname inside Section 2 (Default: AUTOMATED_SWITCH). 
   3. Modify VLAN Grid (Optional): Double-click any cell inside the Section 3 VLAN table to dynamically alter the expected VLAN ID or VLAN Name via the pop-up modal. 

## Step 2: Deploy Configuration & Persist States (Button 1)

   1. Click the blue button: 1. Deploy Configuration & Save. 
   2. Backend Execution Check: The script automatically logs into the switch via SSH, elevates its privilege level using the secret parameter, renames the hostname, provisions VLAN 10, 20, and 50, and automatically triggers write memory to prevent volatile configuration data from wiping upon power-offs. (p. 4)
   3. Success Output: Wait for the green status label to display ✓ Deployed successfully! and check the success message dialog. 

## Step 3: Standalone Disaster Recovery Configuration Export (Button 2)

   1. Click the purple button: 2. Standalone History Backup. 
   2. Backend Execution Check: The script establishes a new standalone session to query the current operational prompt, issues show running-config, downloads the raw config payload, and creates a local timestamped recovery log. (p. 4)
   3. File Output Verification: Open your project root directory. You will find a newly created folder named backups/ containing an enterprise-ready backup file matching the following naming convention: backup_[Actual_Hostname]_[YYYYMMDD_HHMMSS].txt. (p. 4)

## Step 4: Closed-Loop Dual-Track Compliance Audit (Button 3)
This standalone action queries live hardware parameters via text regex processing to parse out hidden non-standard anomalies. 

* Scenario A: Passing the Audit (100% Compliant)
1. Click the green button: 3. Compliance Verification (Audit). 
   2. The regex scanner verifies that both the live prompt matching group and the show vlan brief column layouts align perfectly with the target profile. A green window will pop up stating: "Perfect! All checks are 100% compliant." (p. 5)
* Scenario B: Catching Deviations (Non-Standard Alert)
1. Simulate a Change: Double-click VLAN_DATOS in the table grid, and intentionally rename it to VLAN_ERROR_TEST inside your GUI, but DO NOT click the deploy button. (p. 5)
   2. Trigger Audit: Directly click the green 3. Compliance Verification (Audit) button. 
   3. Warning Alert Interface: The Python background engine captures that the live state database on the switch is still storing the old configuration. The interface status label will immediately shift to red flashing Non-Standard Configuration!, and an engineering warning prompt will pop up on your screen explicitly listing the non-compliant parameters: VLAN 10 Name: Expected 'VLAN_ERROR_TEST', Actual 'VLAN_DATOS'. (p. 5)

------------------------------
## One-Click Infrastructure Synchronization (GitHub)
To fulfill the assignment requirement regarding "regularly committing meaningful code with descriptive messages", use the dedicated Git client module.

   1. Launch Sync Module: Run the companion Git sync client in your terminal: 
   
   python sync_to_github.py
   
   2. Execute Sync Trigger: Click the dark button: Synchronize Project and Backups to GitHub. 
   3. Provide Descriptive Commit Log: A prompt modal will overlay on your screen. Enter an explicit, professional change description tracking your network architecture adjustments (e.g., feat: deploy standard data voice and security vlans on switch 10 and export local config backups). 
   4. Automated Pipeline: The subprocess script blocks will sequentially run git add ., bake in your text parameter logs into a local commit block, pull upstream branches via --rebase to automatically secure conflict boundaries, and securely deploy your entire project codebase (including newly generated switch local historical txt text files) up to your public GitHub repository. 
   5. Verify on Web: Refresh your GitHub page. Your main tree file layout will display your dynamic descriptions, and the backups/ tracking folder will be completely archived and visualized under public version control history. 

------------------------------
------------------------------
## 🇨🇳 Part 2: 中文版本## Cisco 网络自动化配置与合规审计系统 - 操作指南
基于 main.py 和 sync_to_github.py 提供完整的思科交换机配置下发、独立灾备文件导出、双轨合规性审计以及 GitHub 一键版本同步的操作指南。 
------------------------------
## 环境准备
在运行脚本之前，请确保您的本地宿主机和 EVE-NG 仿真环境满足以下生产环境规范： 
## 1. Python 依赖库安装
打开终端（CMD/Git Bash），运行以下命令安装网络自动化核心通信库： 

pip install netmiko

## 2. EVE-NG 网络桥接

* 将 EVE-NG 中思科交换机的管理接口（例如 Ethernet0/0）连线到 Management(Cloud0)。 
* 确保您的真实电脑可以成功 ping 通交换机的管理 IP（代码默认值：192.168.43.101）。 

## 3. 思科交换机基础初始化
交换机必须开启 SSH 并配置特权模式密码。请在交换机命令行中刷入以下基础配置： 

enable
configure terminal
vtp mode transparent
interface Ethernet0/0
no switchport
ip address 192.168.43.101 255.255.255.0
no shutdown
exit
username admin privilege 15 secret cisco
#enable secret cisco
crypto key generate rsa label SSH_KEY modulus 1024
line vty 0 4
login local
transport input ssh
end
write memory

------------------------------
## 核心功能分步操作说明
在终端输入 python main.py 唤醒主图形化控制台。 
## 步骤 1：填充设备连接参数与动态调整 VLAN 期望值

   1. 输入连接参数：在区域 1 对应的表单中，输入交换机的管理 IP、SSH 用户名、普通密码以及进入特权模式所需的 Enable Secret（特权密码）。 
   2. 定义主机名：在区域 2 中输入您期望变更的目标主机名（默认值：AUTOMATED_SWITCH）。 
   3. 修改 VLAN 列表（可选交互）：在区域 3 的 VLAN 列表中，双击任意单元格，可以在弹出的模态输入框中动态修改您期望配置的 VLAN 号或 VLAN 名称。 

## 步骤 2：下发批量配置与网络状态持久化（测试蓝色按钮 1）

   1. 点击蓝色按钮：点击界面下方的第一个蓝色按钮 1. Deploy Configuration & Save。 
   2. 底层逻辑印证：脚本会通过 SSH 登入交换机，利用特权密码自动执行提权命令，下发主机名变更并批量创建命名对应的 VLAN，最后在后台强制执行 write memory 将内存配置刷入 NVRAM。 
   3. 成功状态输出：等待底部状态栏显示绿色成功字样 ✓ Deployed successfully!，并在弹出的成功对话框中点击确定。

## 步骤 3：独立一键灾备配置归档（测试紫色按钮 2）

   1. 点击紫色按钮：点击界面下方的第二个紫色按钮 2. Standalone History Backup。 
   2. 底层逻辑印证：脚本将启动独立的通信会话，长途抓取交换机当前的物理运行配置文件（running-config）。 
   3. 文件产出比对：打开您电脑上的项目根目录，会发现自动生成了一个 backups 文件夹，里面已经妥善存储了类似于 backup_AUTOMATED_SWITCH_20260602_002400.txt 的纯文本无损配置文件。 

## 步骤 4：闭环双轨合规性深度审计验证（测试绿色按钮 3）
该功能为独立的合规性自检程序，通过拉取设备全量快照，利用正则表达式进行严格的“所需配置 vs 实际运行状态”双轨双重校验。 

* 情景 A：通过合规性审查（100% Compliant）
1. 直接点击第三个绿色按钮 3. Compliance Verification (Audit)。 
   2. 正则扫描器核对设备提示符和 VLAN 状态无误后，前端将直接弹出绿色的合规通过告知窗口（提示："Perfect! All checks are 100% compliant."）。 
* 情景 B：捕获非标准配置偏差（非标拦截报警）
1. 人为模拟变更：在界面表格中双击 VLAN_DATOS，将其名称故意篡改修改为 VLAN_ERROR_TEST，但绝对不要点击下发配置按钮。 
   2. 启动审计：直接越级点击第三个绿色按钮 3. Compliance Verification (Audit) 启动验证。 
   3. 偏差拦截报警：Python 后台正则引擎在比对交换机真实回显时，会敏锐发现交换机端依旧保留的是老名称。界面状态标签会瞬间变红（显示闪烁的 Non-Standard Configuration!），并向前端抛出一个醒目的黄色警告强阻断窗口，精准指出：VLAN 10 Name: Expected 'VLAN_ERROR_TEST', Actual 'VLAN_DATOS'（发现非标准配置不一致偏差）。 

------------------------------
## GitHub 一键版本控制与备份上传
为了完美履行作业中关于“定期向仓库提交有意义的代码并附带详细描述性消息”的指标要求，请使用专用的独立 Git 协同控制客户端。 

   1. 启动独立同步程序：在项目根目录下，执行以下命令唤醒独立的 IaC 版本同步工具： 
   
   python sync_to_github.py
   
   2. 触发一键远程同步：点击界面上黑色的项目同步按钮 Synchronize Project and Backups to GitHub。 
   3. 输入详细的版本变更日志：前端将自动弹出一个文本交互框。请输入一条极具专业语义的英文版本迭代日志，例如：feat: deploy standard data voice and security vlans on switch 10 and export local config backups 并点击确定。 
   4. 底层自动化流水线：脚本将通过进程链全自动在后台执行 git add .（包含新生成的交换机历史配置文件）、打包你输入的日志执行 git commit、利用 pull --rebase 规避上游冲突，并一键安全推送到公共 GitHub。 
   5. GitHub 远端确认：刷新您的 GitHub 仓库主页。即可看到整洁的文件目录、全新的提交历史（Commit History），以及连带上传上来的交换机历史灾备文本（backups/ 文件夹）。 

------------------------------


