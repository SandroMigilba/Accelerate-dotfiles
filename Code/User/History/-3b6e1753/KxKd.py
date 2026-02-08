import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
import re

# Path config Waybar
CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class ModernMinimalistEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Manager")
        self.root.geometry("850x700")
        
        # Modern Minimalist Palette (Neutral Dark)
        self.bg_color = "#121212"        # Base background
        self.surface = "#1e1e1e"         # Surface for cards
        self.accent = "#ffffff"          # High contrast for primary actions
        self.text_main = "#f5f5f7"       # Soft white
        self.text_dim = "#86868b"        # Muted gray for labels
        self.border_color = "#333333"    # Subtle dividers
        self.danger = "#ff453a"          # Minimalist red

        self.root.configure(bg=self.bg_color)
        self.load_config()
        self.create_widgets()

    def load_config(self):
        try:
            if not os.path.exists(CONFIG_PATH):
                self.config = {"group/apps": {"modules": []}}
                return
            with open(CONFIG_PATH, 'r') as f:
                content = f.read()
                content = re.sub(r"//.*", "", content)
                content = re.sub(r",\s*([\]}])", r"\1", content)
                self.config = json.loads(content)
        except Exception as e:
            messagebox.showerror("Error", f"Config error: {e}")
            self.root.destroy()

    def create_widgets(self):
        # --- Header ---
        header = tk.Frame(self.root, bg=self.bg_color, pady=40)
        header.pack(fill="x", padx=50)

        tk.Label(header, text="Waybar Launcher", font=("Inter", 22, "bold"), 
                 fg=self.text_main, bg=self.bg_color).pack(side="left")

        # --- Content Area (Scrollable) ---
        self.container = tk.Frame(self.root, bg=self.bg_color)
        self.container.pack(fill="both", expand=True, padx=50)

        self.canvas = tk.Canvas(self.container, bg=self.bg_color, highlightthickness=0)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)
        
        # Scrollbar minimalis
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=750)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)

        self.refresh_app_list()

        # --- Footer ---
        footer = tk.Frame(self.root, bg=self.bg_color, pady=40)
        footer.pack(fill="x", padx=50)

        # Buttons (Modern Flat Design)
        self.btn_add = tk.Button(footer, text="+ Add App", command=self.open_app_picker, 
                                 bg=self.surface, fg=self.text_main, font=("Inter", 10, "medium"),
                                 relief="flat", padx=25, pady=10, cursor="hand2",
                                 activebackground=self.border_color, activeforeground=self.text_main)
        self.btn_add.pack(side="left")

        self.btn_save = tk.Button(footer, text="Apply Changes", command=self.save_config, 
                                  bg=self.accent, fg=self.bg_color, font=("Inter", 10, "bold"),
                                  relief="flat", padx=25, pady=10, cursor="hand2",
                                  activebackground=self.text_dim)
        self.btn_save.pack(side="right")

    def refresh_app_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.entries = {}
        image_keys = [k for k in self.config.keys() if k.startswith("image#")]

        for key in image_keys:
            # Row Container (Minimalist List Style)
            row = tk.Frame(self.scrollable_frame, bg=self.bg_color, pady=20)
            row.pack(fill="x")
            
            # Hairline Divider
            tk.Frame(self.scrollable_frame, bg=self.border_color, height=1).pack(fill="x")

            # App Label
            name = key.split("#")[-1].replace("_", " ").upper()
            tk.Label(row, text=name, font=("Inter", 9, "bold"), fg=self.text_main, 
                     bg=self.bg_color, width=15, anchor="w").pack(side="left")

            # Path & Command Inputs
            input_container = tk.Frame(row, bg=self.bg_color)
            input_container.pack(side="left", fill="x", expand=True, padx=20)

            val_path = tk.StringVar(value=self.config[key].get("path", ""))
            e_path = tk.Entry(input_container, textvariable=val_path, bg=self.surface, fg=self.text_dim, 
                              insertbackground=self.accent, borderwidth=0, font=("Inter", 9), width=30)
            e_path.pack(side="left", padx=5, ipady=4)
            
            val_action = tk.StringVar(value=self.config[key].get("on-click", ""))
            e_action = tk.Entry(input_container, textvariable=val_action, bg=self.surface, fg=self.accent, 
                                insertbackground=self.accent, borderwidth=0, font=("Inter", 9, "bold"), width=20)
            e_action.pack(side="left", padx=5, ipady=4)

            # Minimal Delete Button
            tk.Button(row, text="Remove", font=("Inter", 8), bg=self.bg_color, fg=self.danger,
                      relief="flat", bd=0, command=lambda k=key: self.delete_app(k), cursor="hand2").pack(side="right")

            self.entries[key] = (val_path, val_action)

    def open_app_picker(self):
        picker = tk.Toplevel(self.root)
        picker.title("Select Application")
        picker.geometry("400x550")
        picker.configure(bg=self.bg_color)
        
        tk.Label(picker, text="Installed Apps", font=("Inter", 14, "bold"), 
                 bg=self.bg_color, fg=self.text_main, pady=30).pack()

        lb = tk.Listbox(picker, bg=self.surface, fg=self.text_main, borderwidth=0, 
                        highlightthickness=0, font=("Inter", 10), selectbackground=self.border_color)
        lb.pack(fill="both", expand=True, padx=40)

        apps = self.get_installed_apps()
        for app in apps:
            lb.insert(tk.END, f" {app['name']}")

        def confirm():
            idx = lb.curselection()
            if idx:
                selected = apps[idx[0]]
                picker.destroy()
                self.add_selected_app(selected)

        tk.Button(picker, text="Continue", command=confirm, bg=self.accent, 
                  fg=self.bg_color, relief="flat", font=("Inter", 10, "bold"), pady=12).pack(fill="x", padx=40, pady=30)

    def get_installed_apps(self):
        apps = []
        paths = ['/usr/share/applications', os.path.expanduser('~/.local/share/applications')]
        for path in paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.endswith('.desktop'):
                        try:
                            with open(os.path.join(path, file), 'r') as f:
                                content = f.read()
                                name = re.search(r'^Name=(.*)', content, re.M)
                                exec_cmd = re.search(r'^Exec=([^%\n]*)', content, re.M)
                                if name and exec_cmd:
                                    apps.append({"name": name.group(1).strip(), "cmd": exec_cmd.group(1).strip()})
                        except: continue
        return sorted(apps, key=lambda x: x['name'].lower())

    def add_selected_app(self, app_info):
        img = filedialog.askopenfilename(filetypes=[("Icons", "*.png *.svg *.jpg")])
        if img:
            key = f"image#{app_info['name'].lower().replace(' ', '_')}"
            self.config[key] = {"path": img, "size": 22, "on-click": app_info['cmd'], "tooltip": True}
            if "group/apps" in self.config:
                if key not in self.config["group/apps"]["modules"]:
                    self.config["group/apps"]["modules"].append(key)
            self.refresh_app_list()

    def delete_app(self, key):
        if key in self.config: del self.config[key]
        if "group/apps" in self.config:
            try: self.config["group/apps"]["modules"].remove(key)
            except: pass
        self.refresh_app_list()

    def save_config(self):
        for key, (p, a) in self.entries.items():
            self.config[key]["path"] = p.get()
            self.config[key]["on-click"] = a.get()
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.config, f, indent=4)
            os.system("pkill waybar && waybar &")
            messagebox.showinfo("Success", "Configuration applied.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernMinimalistEditor(root)
    root.mainloop()