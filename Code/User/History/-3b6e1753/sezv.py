import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
import re

# Path config Waybar
CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class CyberWaybarEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Forge v1.0")
        self.root.geometry("1000x750")
        
        # Cyberdark / Nord-ish Color Palette
        self.bg_deep = "#0b0e14"         # Background utama (sangat gelap)
        self.card_bg = "#151921"         # Card background
        self.input_bg = "#1c232d"        # Input background
        self.accent_primary = "#1793d1"  # Arch Blue
        self.accent_secondary = "#bb9af7"# Purple highlight
        self.text_main = "#c0caf5"       # Font terang
        self.text_dim = "#565f89"        # Font redup
        self.danger = "#f7768e"          # Red alert
        self.success = "#9ece6a"         # Green

        self.root.configure(bg=self.bg_deep)
        self.load_config()
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Scrollbar bergaya minimalis Cyberpunk
        style.configure("Vertical.TScrollbar", 
                        gripcount=0, 
                        background=self.input_bg, 
                        troughcolor=self.bg_deep, 
                        borderwidth=0, 
                        arrowsize=1)

    def load_config(self):
        try:
            if not os.path.exists(CONFIG_PATH):
                self.config = {"group/apps": {"modules": []}}
                return
            with open(CONFIG_PATH, 'r') as f:
                content = f.read()
                # Bersihkan komentar C-style jika ada agar JSON valid
                content = re.sub(r"//.*", "", content)
                content = re.sub(r",\s*([\]}])", r"\1", content)
                self.config = json.loads(content)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca config: {e}")
            self.root.destroy()

    def create_widgets(self):
        # --- Header ---
        header = tk.Frame(self.root, bg=self.bg_deep, pady=30)
        header.pack(fill="x", padx=40)

        title_label = tk.Label(header, text="WAYBAR FORGE", 
                               font=("JetBrains Mono", 24, "bold"), 
                               fg=self.accent_primary, bg=self.bg_deep)
        title_label.pack(side="left")
        
        status_dot = tk.Label(header, text="● SYSTEM ACTIVE", 
                             font=("JetBrains Mono", 8), fg=self.success, bg=self.bg_deep)
        status_dot.pack(side="left", padx=20, pady=(10, 0))

        # --- Content Area ---
        container = tk.Frame(self.root, bg=self.bg_deep)
        container.pack(fill="both", expand=True, padx=40)

        self.canvas = tk.Canvas(container, bg=self.bg_deep, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_deep)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=880)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.refresh_app_list()

        # --- Bottom Toolbar ---
        footer = tk.Frame(self.root, bg=self.bg_deep, pady=25)
        footer.pack(fill="x", padx=40)

        self.create_btn(footer, "[+] ADD MODULE", self.accent_secondary, self.open_app_picker).pack(side="left", padx=5)
        self.create_btn(footer, "[!] APPLY CHANGES", self.accent_primary, self.save_config).pack(side="right", padx=5)

    def create_btn(self, parent, text, color, command):
        # Tombol dengan gaya terminal/blok
        btn = tk.Button(parent, text=text, command=command, bg=self.bg_deep, fg=color,
                        font=("JetBrains Mono", 10, "bold"), relief="flat", padx=20, pady=10,
                        activebackground=color, activeforeground=self.bg_deep, 
                        highlightthickness=1, highlightbackground=color, bd=1, cursor="hand2")
        
        # Hover effect
        btn.bind("<Enter>", lambda e: btn.configure(bg=color, fg=self.bg_deep))
        btn.bind("<Leave>", lambda e: btn.configure(bg=self.bg_deep, fg=color))
        return btn

    def refresh_app_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.entries = {}
        image_keys = [k for k in self.config.keys() if k.startswith("image#")]

        for key in image_keys:
            # Card
            card = tk.Frame(self.scrollable_frame, bg=self.card_bg, padx=15, pady=15, 
                            highlightthickness=1, highlightbackground=self.input_bg)
            card.pack(fill="x", pady=8)

            top_row = tk.Frame(card, bg=self.card_bg)
            top_row.pack(fill="x", mb=10)
            
            name = key.split("#")[-1].upper()
            tk.Label(top_row, text=f"> {name}", font=("JetBrains Mono", 11, "bold"), 
                     fg=self.accent_secondary, bg=self.card_bg).pack(side="left")

            tk.Button(top_row, text="TERMINATE", font=("JetBrains Mono", 8), 
                      bg=self.card_bg, fg=self.danger, relief="flat",
                      command=lambda k=key: self.delete_app(k), cursor="hand2").pack(side="right")

            # Input Fields
            input_container = tk.Frame(card, bg=self.card_bg)
            input_container.pack(fill="x", pady=(10, 0))

            # Icon Path
            tk.Label(input_container, text="PATH:", font=("JetBrains Mono", 8), 
                     fg=self.text_dim, bg=self.card_bg).grid(row=0, column=0, sticky="w")
            
            val_path = tk.StringVar(value=self.config[key].get("path", ""))
            e_path = tk.Entry(input_container, textvariable=val_path, bg=self.input_bg, fg=self.text_main, 
                              insertbackground=self.accent_primary, borderwidth=0, font=("JetBrains Mono", 9))
            e_path.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

            # Command
            tk.Label(input_container, text="EXEC:", font=("JetBrains Mono", 8), 
                     fg=self.text_dim, bg=self.card_bg).grid(row=1, column=0, sticky="w")

            val_action = tk.StringVar(value=self.config[key].get("on-click", ""))
            e_action = tk.Entry(input_container, textvariable=val_action, bg=self.input_bg, fg=self.accent_primary, 
                                insertbackground=self.accent_primary, borderwidth=0, font=("JetBrains Mono", 9))
            e_action.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

            input_container.columnconfigure(1, weight=1)
            self.entries[key] = (val_path, val_action)

    # --- Logika Operasional ---
    def open_app_picker(self):
        picker = tk.Toplevel(self.root)
        picker.title("Select Binary")
        picker.geometry("450x550")
        picker.configure(bg=self.bg_deep)
        
        tk.Label(picker, text="// APPS_DATABASE", font=("JetBrains Mono", 14, "bold"), 
                 bg=self.bg_deep, fg=self.accent_secondary, pady=20).pack()

        lb = tk.Listbox(picker, bg=self.card_bg, fg=self.text_main, borderwidth=0, 
                        highlightthickness=1, highlightbackground=self.accent_primary,
                        font=("JetBrains Mono", 9), selectbackground=self.accent_primary)
        lb.pack(fill="both", expand=True, padx=20)

        apps = self.get_installed_apps()
        for app in apps:
            lb.insert(tk.END, f" {app['name']}")

        def confirm():
            idx = lb.curselection()
            if idx:
                self.add_selected_app(apps[idx[0]])
                picker.destroy()

        self.create_btn(picker, "INITIALIZE MODULE", self.accent_primary, confirm).pack(fill="x", padx=20, pady=20)

    def get_installed_apps(self):
        apps = []
        paths = ['/usr/share/applications', os.path.expanduser('~/.local/share/applications')]
        for path in paths:
            if os.path.exists(path):
                for file in sorted(os.listdir(path)):
                    if file.endswith('.desktop'):
                        try:
                            with open(os.path.join(path, file), 'r') as f:
                                content = f.read()
                                name = re.search(r'^Name=(.*)', content, re.M)
                                exec_cmd = re.search(r'^Exec=([^%\n]*)', content, re.M)
                                if name and exec_cmd:
                                    apps.append({"name": name.group(1).strip(), "cmd": exec_cmd.group(1).strip()})
                        except: continue
        return apps

    def add_selected_app(self, app_info):
        img = filedialog.askopenfilename(title="Select Module Icon")
        if img:
            key = f"image#{app_info['name'].lower().replace(' ', '_')}"
            self.config[key] = {"path": img, "size": 24, "on-click": app_info['cmd'], "tooltip": True}
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
            # Restart waybar secara otomatis
            os.system("pkill waybar && waybar &")
            messagebox.showinfo("SUCCESS", "Neural Link Established: Config Applied.")
        except Exception as e:
            messagebox.showerror("SYSTEM ERROR", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    # Pastikan font JetBrains Mono terinstal di sistem Linux kamu, 
    # jika tidak, ia akan fallback ke font monospace standar.
    app = CyberWaybarEditor(root)
    root.mainloop()