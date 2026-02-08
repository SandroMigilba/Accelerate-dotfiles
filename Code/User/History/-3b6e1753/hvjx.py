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
        self.root.title("Waybar Manager — macOS Tahoe Style")
        self.root.geometry("900x650")
        
        # macOS Tahoe Color Palette
        self.bg_color = "#1e1e1e"        # Deep Dark
        self.card_color = "#2a2a2a"      # Lighter surface
        self.accent_blue = "#007aff"     # macOS Blue
        self.accent_green = "#28cd41"    # macOS Green
        self.text_main = "#ffffff"
        self.text_dim = "#a0a0a0"
        self.danger = "#ff3b30"          # macOS Red

        self.root.configure(bg=self.bg_color)
        self.load_config()
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        # Customizing Scrollbar agar lebih minimalis
        style.configure("Vertical.TScrollbar", gripcount=0, background=self.card_color, 
                        troughcolor=self.bg_color, borderwidth=0, arrowsize=1)

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
        # --- Sidebar / Header Area ---
        header = tk.Frame(self.root, bg=self.bg_color, pady=20)
        header.pack(fill="x", padx=40)

        title_label = tk.Label(header, text="Waybar Apps", font=("SF Pro Display", 24, "bold"), 
                               fg=self.text_main, bg=self.bg_color)
        title_label.pack(side="left")

        # --- Main Content (Scrollable) ---
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill="both", expand=True, padx=40)

        self.canvas = tk.Canvas(container, bg=self.bg_color, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.bg_color)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=800)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.refresh_app_list()

        # --- Bottom Bar (Floating Action) ---
        bottom_bar = tk.Frame(self.root, bg=self.bg_color, pady=30)
        bottom_bar.pack(fill="x", padx=40)

        # macOS Styled Buttons
        add_btn = tk.Button(bottom_bar, text="+ Add Application", command=self.open_app_picker, 
                            bg=self.accent_blue, fg="white", font=("SF Pro Text", 10, "bold"),
                            relief="flat", padx=20, pady=10, activebackground="#005ecb", cursor="hand2")
        add_btn.pack(side="left")

        save_btn = tk.Button(bottom_bar, text="Apply Changes", command=self.save_config, 
                             bg=self.accent_green, fg="white", font=("SF Pro Text", 10, "bold"),
                             relief="flat", padx=20, pady=10, activebackground="#1eb035", cursor="hand2")
        save_btn.pack(side="right")

    def refresh_app_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.entries = {}
        image_keys = [k for k in self.config.keys() if k.startswith("image#")]

        for key in image_keys:
            # Tahoe "Card" Style
            card = tk.Frame(self.scrollable_frame, bg=self.card_color, padx=15, pady=15)
            card.pack(fill="x", pady=8)

            # Row 1: App Info
            name = key.split("#")[-1].replace("_", " ").title()
            tk.Label(card, text=name, font=("SF Pro Text", 11, "bold"), 
                     fg=self.text_main, bg=self.card_color).grid(row=0, column=0, sticky="w")

            # Row 2: Inputs
            input_frame = tk.Frame(card, bg=self.card_color)
            input_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))

            # Icon Path Entry
            tk.Label(input_frame, text="Icon Path", font=("SF Pro Text", 8), fg=self.text_dim, bg=self.card_color).pack(side="left")
            val_path = tk.StringVar(value=self.config[key].get("path", ""))
            e_path = tk.Entry(input_frame, textvariable=val_path, bg=self.bg_color, fg="white", 
                              insertbackground="white", borderwidth=0, font=("SF Pro Text", 9))
            e_path.pack(side="left", padx=10, ipady=4)
            
            # Action Entry
            tk.Label(input_frame, text="Command", font=("SF Pro Text", 8), fg=self.text_dim, bg=self.card_color).pack(side="left", padx=(10,0))
            val_action = tk.StringVar(value=self.config[key].get("on-click", ""))
            e_action = tk.Entry(input_frame, textvariable=val_action, bg=self.bg_color, fg=self.accent_blue, 
                                insertbackground="white", borderwidth=0, font=("SF Pro Text", 9, "bold"))
            e_action.pack(side="left", padx=10, ipady=4)

            # Delete Button (Top Right of card)
            del_btn = tk.Button(card, text="✕", font=("bold", 10), bg=self.card_color, fg=self.danger,
                                relief="flat", bd=0, command=lambda k=key: self.delete_app(k), cursor="hand2")
            del_btn.place(relx=0.98, rely=0.1, anchor="ne")

            self.entries[key] = (val_path, val_action)

    def open_app_picker(self):
        # Styled Picker Window
        picker = tk.Toplevel(self.root)
        picker.title("Select App")
        picker.geometry("400x550")
        picker.configure(bg=self.bg_color)
        picker.transient(self.root)
        picker.grab_set()

        tk.Label(picker, text="Applications", font=("SF Pro Text", 16, "bold"), 
                 bg=self.bg_color, fg="white", pady=20).pack()

        list_frame = tk.Frame(picker, bg=self.bg_color)
        list_frame.pack(fill="both", expand=True, padx=20)

        lb = tk.Listbox(list_frame, bg=self.card_color, fg="white", borderwidth=0, 
                        highlightthickness=0, font=("SF Pro Text", 10), selectbackground=self.accent_blue)
        lb.pack(side="left", fill="both", expand=True)

        apps = self.get_installed_apps()
        for app in apps:
            lb.insert(tk.END, f"  {app['name']}")

        def confirm():
            idx = lb.curselection()
            if idx:
                selected = apps[idx[0]]
                picker.destroy()
                self.add_selected_app(selected)

        tk.Button(picker, text="Select & Choose Icon", command=confirm, bg=self.accent_blue, 
                  fg="white", relief="flat", pady=10).pack(fill="x", padx=20, pady=20)

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
        img = filedialog.askopenfilename(title="Select PNG Icon", filetypes=[("Images", "*.png *.svg *.jpg")])
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
            messagebox.showinfo("Success", "Waybar has been updated successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    # Menghilangkan dekorasi window standar jika ingin benar-benar Tahoe (opsional)
    # root.overrideredirect(True) 
    app = TahoeEditor(root)
    root.mainloop()