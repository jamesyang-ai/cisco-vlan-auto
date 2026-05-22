import tkinter as tk
from tkinter import messagebox, simpledialog
import subprocess

def run_git_push():
    status_label.config(text="Synchronizing with GitHub remote repository...", fg="#2563EB")
    root.update()
    try:
        # Prompt user to input a custom descriptive commit message via UI
        commit_msg = simpledialog.askstring(
            "Git Commit Log", 
            "Enter descriptive change log (Required by Assignment):", 
            initialvalue="chore: routine network profile and backup tracking update"
        )
        
        # If user cancels or inputs an empty string, abort migration loop
        if not commit_msg:
            status_label.config(text="Git synchronization cancelled.", fg="gray")
            return

        # Execute standard industrial Git staging pipeline
        subprocess.run(["git", "add", "."], check=True, shell=True)
        subprocess.run(["git", "commit", "-m", commit_msg], check=True, shell=True)
        
        # Pull latest origin changes first to automatically mitigate upstream conflicts
        subprocess.run(["git", "pull", "origin", "main", "--rebase"], check=True, shell=True)
        subprocess.run(["git", "push", "origin", "main"], check=True, shell=True)

        status_label.config(text="✓ GitHub Repository successfully synchronized!", fg="green")
        messagebox.showinfo("Git Push Success", "All local scripts, documentation, and switch configuration backups have been successfully committed and pushed to your remote GitHub repository!")
    except Exception as e:
        status_label.config(text="Git synchronization failed!", fg="red")
        messagebox.showerror("Git Error", f"Failed to push to GitHub. Please verify your local Git credentials or network tunnel connectivity.\n\nDetails: {str(e)}")

# --- Tkinter GUI Layout for Dedicated Git Sync Client ---
root = tk.Tk()
root.title("Infrastructure as Code (IaC) GitHub Synchronizer")
root.geometry("450x180")

# Header Information
tk.Label(root, text="Network Automation Code Tracking Tool", font=("Arial", 11, "bold")).pack(pady=10)
tk.Label(root, text="Click below to track and sync local configurations to GitHub remote repository.", fg="gray").pack(pady=2)

status_label = tk.Label(root, text="Ready to track infrastructure variations...", fg="gray", font=("Arial", 9, "italic"))
status_label.pack(pady=8)

# Core GitHub Push Operational Button
btn_push = tk.Button(
    root, 
    text="🐙 Synchronize Project and Backups to GitHub", 
    font=("Arial", 10, "bold"), 
    bg="#24292E", 
    fg="white", 
    command=run_git_push, 
    pady=6
)
btn_push.pack(fill="x", padx=25, pady=5)

root.mainloop()
