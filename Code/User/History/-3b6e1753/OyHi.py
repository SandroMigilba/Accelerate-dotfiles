import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import os
import re

CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class WaybarAppsEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Smart Launcher")
        self.root.geometry("850x600")
        self.root.configure(bg="#1c2238")

        self.load_config()
        self.create_widgets()

    def get_installed_apps(self):
        """Membaca semua file .desktop untuk mendapatkan daftar aplikasi"""
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
                                    apps.append({
                                        "name": name.group(1).strip(),
                                        "cmd": exec_cmd.group(1).strip()
                                    })
                        except:
                            continue
        return sorted(apps, key=lambda x: x['name'].lower())

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
        tk.Label(self.root, text="󰀻 Waybar System App Picker", font=("JetBrainsMono Nerd Font", 16, "bold"), 
                 fg="#8be9fd", bg="#1c2238", pady=20).pack()

        self.canvas = tk.Canvas(self.root, bg="#1c2238", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.main_frame = tk.Frame(self.canvas, bg="#1c2238")

        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.canvas.pack(side="left", fill="both", expand=True, padx=20)
        self.scrollbar.pack(side="right", fill="y")

        self.refresh_app_list()

        btn_frame = tk.Frame(self.root, bg="#1c2238", pady=20)
        btn_frame.pack(fill="x", side="bottom")

        tk.Button(btn_frame, text="󰐕 SELECT FROM SYSTEM", command=self.open_app_picker, 
                  bg="#50fa7b", fg="#282a36", font=("bold", 10), padx=20, pady=8).pack(side="left", padx=30)
        
        tk.Button(btn_frame, text="󰔟 SAVE & RELOAD", command=self.save_config, 
                  bg="#8be9fd", fg="#282a36", font=("bold", 10), padx=20, pady=8).pack(side="right", padx=30)

    def refresh_app_list(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        self.entries = {}
        image_keys = [k for k in self.config.keys() if k.startswith("image#")]
        for key in image_keys:
            row = tk.Frame(self.main_frame, bg="#2d3758", pady=10, padx=15)
            row.pack(fill="x", pady=5)
            name = key.split("#")[-1].upper()
            tk.Label(row, text=name, fg="#ff79c6", bg="#2d3758", width=12, anchor="w", font=("bold", 10)).pack(side="left")
            val_path = tk.StringVar(value=self.config[key].get("path", ""))
            tk.Entry(row, textvariable=val_path, bg="#1c2238", fg="#f8f8f2", width=25).pack(side="left", padx=5)
            val_action = tk.StringVar(value=self.config[key].get("on-click", ""))
            tk.Entry(row, textvariable=val_action, bg="#1c2238", fg="#f1fa8c", width=15).pack(side="left", padx=5)
            tk.Button(row, text="󰆴", fg="#ff5555", bg="#2d3758", bd=0, command=lambda k=key: self.delete_app(k)).pack(side="right")
            self.entries[key] = (val_path, val_action)

    def open_app_picker(self):
        picker = tk.Toplevel(self.root)
        picker.title("Select Application")
        picker.geometry("400x500")
        picker.configure(bg="#282a36")

        tk.Label(picker, text="Pilih Aplikasi:", fg="#8be9fd", bg="#282a36", pady=10).pack()
        
        listbox = tk.Listbox(picker, bg="#1c2238", fg="white", font=("JetBrainsMono Nerd Font", 10))
        listbox.pack(fill="both", expand=True, padx=10, pady=10)
        
        apps = self.get_installed_apps()
        for app in apps:
            listbox.insert(tk.END, app['name'])

        def on_select():
            idx = listbox.curselection()
            if idx:
                selected_app = apps[idx[0]]
                picker.destroy()
                self.add_selected_app(selected_app)

        tk.Button(picker, text="CHOOSE ICON", command=on_select, bg="#50fa7b").pack(pady=10)

    def add_selected_app(self, app_info):
        img = filedialog.askopenfilename(title=f"Pilih Icon untuk {app_info['name']}", 
                                         filetypes=[("Images", "*.png *.svg *.jpg")])
        if img:
            key = f"image#{app_info['name'].lower().replace(' ', '_')}"
            self.config[key] = {
                "path": img,
                "size": 22, 
                "on-click": app_info['cmd'],
                "tooltip": True
            }
            if "group/apps" in self.config:
                if key not in self.config["group/apps"]["modules"]:
                    self.config["group/apps"]["modules"].append(key)
            self.refresh_app_list()

    def delete_app(self, key):
        if key in self.config: del self.config[key]
        if "group/apps" in self.config and key in self.config["group/apps"]["modules"]:
            self.config["group/apps"]["modules"].remove(key)
        self.refresh_app_list()

    def save_config(self):
        for key, (path, action) in self.entries.items():
            self.config[key]["path"] = path.get()
            self.config[key]["on-click"] = action.get()
        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.config, f, indent=4)
            os.system("pkill waybar && waybar &")
            messagebox.showinfo("Sukses", "Waybar Updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal simpan: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WaybarAppsEditor(root)
    root.mainloop()