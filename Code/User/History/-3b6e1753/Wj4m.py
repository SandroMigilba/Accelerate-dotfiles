import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
import re

# Path config Waybar
CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class ModernEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Configuration Tool")
        self.root.geometry("950x700")
        
        # --- Industrial Dark Palette ---
        self.bg_main = "#0f0f0f"         # Deep Black
        self.bg_card = "#1a1a1a"         # Dark Gray Card
        self.bg_input = "#242424"        # Input Field
        self.accent_color = "#f0f0f0"    # Pure White for primary actions
        self.text_primary = "#e0e0e0"    # Off-white text
        self.text_secondary = "#666666"  # Muted gray text
        self.danger = "#b3261e"          # Industrial Red

        self.root.configure(bg=self.bg_main)
        self.load_config()
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        # Minimalist Scrollbar (Dark)
        style.configure("Vertical.TScrollbar", 
                        gripcount=0, 
                        background="#333", 
                        troughcolor=self.bg_main, 
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
            messagebox.showerror("System Error", f"Failed to parse config: {e}")
            self.root.destroy()

    def create_widgets(self):
        # --- Header ---
        header = tk.Frame(self.root, bg=self.bg_main, pady=40)
        header.pack(fill="x", padx=60)

        title_label = tk.Label(header, text="WAYBAR MODULES", 
                               font=("Helvetica", 20, "bold"), 
                               fg=self.text_primary, bg=self.bg_main, letterspacing=2)
        title_label.pack(side="left")

        # --- Content Area ---
        container = tk.Frame(self.root, bg=self.bg_main)
        container.pack(fill="both", expand=True, padx=60)

        self.canvas = tk.Canvas(container, bg=self.bg_main, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_main)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=830)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.refresh_app_list()

        # --- Footer Actions ---
        footer = tk.Frame(self.root, bg=self.bg_main, pady=40)
        footer.pack(fill="x", padx=60)

        # Flat Industrial Buttons
        self.create_btn(footer, "ADD MODULE", "#333333", self.text_primary, self.open_app_picker).pack(side="left", padx=5)
        self.create_btn(footer, "SAVE & RELOAD", self.accent_color, "#000000", self.save_config).pack(side="right", padx=5)

    def create_btn(self, parent, text, bg, fg, command):
        btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                        font=("Helvetica", 9, "bold"), relief="flat", padx=30, pady=12,
                        activebackground=fg, activeforeground=bg, cursor="hand2", bd=0)
        return btn

    def refresh_app_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.entries = {}
        image_keys = [k for k in self.config.keys() if k.startswith("image#")]

        for key in image_keys:
            # Module Card
            card = tk.Frame(self.scrollable_frame, bg=self.bg_card, padx=25, pady=20)
            card.pack(fill="x", pady=5)

            # Left side: Module Name
            name = key.split("#")[-1].replace("_", " ").upper()
            tk.Label(card, text=name, font=("Helvetica", 10, "bold"), 
                     fg=self.text_primary, bg=self.bg_card).grid(row=0, column=0, sticky="w")

            # Inputs
            input_container = tk.Frame(card, bg=self.bg_card)
            input_container.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(15, 0))

            # Path Field
            tk.Label(input_container, text="PATH", font=("Helvetica", 7), fg=self.text_secondary, bg=self.bg_card).pack(anchor="w")
            v_path = tk.StringVar(value=self.config[key].get("path", ""))
            e_path = tk.Entry(input_container, textvariable=v_path, bg=self.bg_input, fg="white", 
                              insertbackground="white", borderwidth=0, font=("Monospace", 9))
            e_path.pack(fill="x", pady=(2, 10), ipady=6)
            
            # Command Field
            tk.Label(input_container, text="EXEC", font=("Helvetica", 7), fg=self.text_secondary, bg=self.bg_card).pack(anchor="w")
            v_cmd = tk.StringVar(value=self.config[key].get("on-click", ""))
            e_cmd = tk.Entry(input_container, textvariable=v_cmd, bg=self.bg_input, fg=self.text_primary, 
                             insertbackground="white", borderwidth=0, font=("Monospace", 9))
            e_cmd.pack(fill="x", pady=(2, 0), ipady=6)

            # Simple Remove Button
            del_btn = tk.Button(card, text="REMOVE", font=("Helvetica", 7, "bold"), bg=self.bg_card, 
                                fg=self.danger, relief="flat", bd=0, command=lambda k=key: self.delete_app(k))
            del_btn.place(relx=1.0, rely=0, anchor="ne")

            self.entries[key] = (v_path, v_cmd)

    # --- Logic Methods ---
    def open_app_picker(self):
        picker = tk.Toplevel(self.root)
        picker.title("Select Application")
        picker.geometry("400x550")
        picker.configure(bg=self.bg_main)
        picker.transient(self.root)
        picker.grab_set()

        tk.Label(picker, text="SYSTEM APPLICATIONS", font=("Helvetica", 12, "bold"), 
                 bg=self.bg_main, fg=self.text_primary, pady=30).pack()

        lb = tk.Listbox(picker, bg=self.bg_card, fg=self.text_primary, borderwidth=0, 
                        highlightthickness=1, highlightbackground=self.bg_input,
                        font=("Helvetica", 9), selectbackground="#444")
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

        self.create_btn(picker, "SELECT", self.accent_color, "#000000", confirm).pack(fill="x", padx=40, pady=30)

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
            messagebox.showinfo("Success", "Configuration applied to system.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernEditor(root)
    root.mainloop()