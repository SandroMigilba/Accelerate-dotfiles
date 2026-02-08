import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
import re

# Path config Waybar
CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class TahoeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Manager")
        self.root.geometry("1000x700")
        
        # macOS Tahoe Color Palette Refined
        self.bg_color = "#121212"        # Darker Background
        self.card_color = "#1e1e1e"      # Card Surface
        self.input_bg = "#2d2d2d"        # Input Background
        self.accent_blue = "#007aff"     # macOS Blue
        self.accent_green = "#34c759"    # macOS Green
        self.text_main = "#ffffff"
        self.text_dim = "#8e8e93"        # iOS Gray
        self.danger = "#ff453a"          # macOS Red

        self.root.configure(bg=self.bg_color)
        self.load_config()
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        # Minimalist Scrollbar
        style.configure("Vertical.TScrollbar", 
                        gripcount=0, 
                        background=self.card_color, 
                        troughcolor=self.bg_color, 
                        borderwidth=0, 
                        arrowsize=1)

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
            messagebox.showerror("Error", f"Gagal membaca config: {e}")
            self.root.destroy()

    def create_widgets(self):
        # --- Sidebar / Header ---
        header = tk.Frame(self.root, bg=self.bg_color, pady=30)
        header.pack(fill="x", padx=50)

        title_label = tk.Label(header, text="Waybar Manager", 
                               font=("Inter", 28, "bold"), 
                               fg=self.text_main, bg=self.bg_color)
        title_label.pack(side="left")
        
        subtitle = tk.Label(self.root, text="Customize your workspace modules and icons", 
                            font=("Inter", 10), fg=self.text_dim, bg=self.bg_color)
        subtitle.pack(anchor="w", padx=50, pady=(0, 20))

        # --- Main Content Area ---
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill="both", expand=True, padx=50)

        self.canvas = tk.Canvas(container, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        # Frame inside canvas
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=880)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.refresh_app_list()

        # --- Bottom Action Bar ---
        footer = tk.Frame(self.root, bg=self.bg_color, pady=30)
        footer.pack(fill="x", padx=50)

        # Custom Buttons with Hover Effects
        self.create_button(footer, "+ Add Application", self.accent_blue, self.open_app_picker).pack(side="left", padx=5)
        self.create_button(footer, "Apply Changes", self.accent_green, self.save_config).pack(side="right", padx=5)

    def create_button(self, parent, text, color, command):
        btn = tk.Button(parent, text=text, command=command, bg=color, fg="white",
                        font=("Inter", 10, "bold"), relief="flat", padx=25, pady=12,
                        activebackground=color, cursor="hand2", bd=0)
        btn.bind("<Enter>", lambda e: btn.configure(background=self.lighten_color(color)))
        btn.bind("<Leave>", lambda e: btn.configure(background=color))
        return btn

    def lighten_color(self, hex_color):
        # Sederhana: buat warna sedikit lebih terang saat hover
        return hex_color # Bisa dikembangkan dengan kalkulasi RGB

    def refresh_app_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.entries = {}
        image_keys = [k for k in self.config.keys() if k.startswith("image#")]

        if not image_keys:
            tk.Label(self.scrollable_frame, text="No applications added yet.", 
                     font=("Inter", 11), fg=self.text_dim, bg=self.bg_color).pack(pady=40)

        for key in image_keys:
            # Card Container
            card = tk.Frame(self.scrollable_frame, bg=self.card_color, padx=20, pady=20)
            card.pack(fill="x", pady=10)

            # Header inside Card
            title_frame = tk.Frame(card, bg=self.card_color)
            title_frame.pack(fill="x")
            
            name = key.split("#")[-1].replace("_", " ").title()
            tk.Label(title_frame, text=name, font=("Inter", 12, "bold"), 
                     fg=self.text_main, bg=self.card_color).pack(side="left")

            # Delete Button
            del_btn = tk.Button(title_frame, text="Remove", font=("Inter", 9, "bold"), 
                                bg=self.card_color, fg=self.danger, relief="flat",
                                command=lambda k=key: self.delete_app(k), cursor="hand2", bd=0)
            del_btn.pack(side="right")

            # Separator
            tk.Frame(card, bg=self.input_bg, height=1).pack(fill="x", pady=15)

            # Inputs Row
            edit_frame = tk.Frame(card, bg=self.card_color)
            edit_frame.pack(fill="x")

            # Icon Path Group
            path_grp = tk.Frame(edit_frame, bg=self.card_color)
            path_grp.pack(side="left", fill="x", expand=True, padx=(0, 10))
            tk.Label(path_grp, text="ICON PATH", font=("Inter", 7, "bold"), fg=self.text_dim, bg=self.card_color).pack(anchor="w")
            
            val_path = tk.StringVar(value=self.config[key].get("path", ""))
            e_path = tk.Entry(path_grp, textvariable=val_path, bg=self.input_bg, fg="white", 
                              insertbackground="white", borderwidth=0, font=("Inter", 10))
            e_path.pack(fill="x", pady=(5, 0), ipady=8, padx=2)

            # Command Group
            cmd_grp = tk.Frame(edit_frame, bg=self.card_color)
            cmd_grp.pack(side="left", fill="x", expand=True, padx=(10, 0))
            tk.Label(cmd_grp, text="EXECUTE COMMAND", font=("Inter", 7, "bold"), fg=self.text_dim, bg=self.card_color).pack(anchor="w")

            val_action = tk.StringVar(value=self.config[key].get("on-click", ""))
            e_action = tk.Entry(cmd_grp, textvariable=val_action, bg=self.input_bg, fg=self.accent_blue, 
                                insertbackground="white", borderwidth=0, font=("Inter", 10, "bold"))
            e_action.pack(fill="x", pady=(5, 0), ipady=8, padx=2)

            self.entries[key] = (val_path, val_action)

    # ... (Keep existing logic methods: open_app_picker, get_installed_apps, add_selected_app, delete_app, save_config)
    # Paste logic methods here...
    def open_app_picker(self):
        picker = tk.Toplevel(self.root)
        picker.title("Select App")
        picker.geometry("400x600")
        picker.configure(bg=self.bg_color)
        picker.transient(self.root)
        picker.grab_set()

        tk.Label(picker, text="Apps Library", font=("Inter", 18, "bold"), 
                 bg=self.bg_color, fg="white", pady=25).pack()

        lb = tk.Listbox(picker, bg=self.card_color, fg="white", borderwidth=0, 
                        highlightthickness=0, font=("Inter", 10), selectbackground=self.accent_blue,
                        padx=10, pady=10)
        lb.pack(fill="both", expand=True, padx=30)

        apps = self.get_installed_apps()
        for app in apps:
            lb.insert(tk.END, f"{app['name']}")

        def confirm():
            idx = lb.curselection()
            if idx:
                selected = apps[idx[0]]
                picker.destroy()
                self.add_selected_app(selected)

        self.create_button(picker, "Select App", self.accent_blue, confirm).pack(fill="x", padx=30, pady=30)

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
        img = filedialog.askopenfilename(title="Select Icon", filetypes=[("Images", "*.png *.svg *.jpg")])
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
            messagebox.showinfo("Success", "Configuration Applied!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = TahoeEditor(root)
    root.mainloop()