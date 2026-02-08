import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import os
import re

CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class WaybarAppsEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Image Launcher Editor")
        self.root.geometry("750x550")
        self.root.configure(bg="#1c2238")

        self.load_config()
        self.create_widgets()

    def load_config(self):
        try:
            if not os.path.exists(CONFIG_PATH):
                self.config = {"modules-left": [], "group/apps": {"modules": []}}
                return
                
            with open(CONFIG_PATH, 'r') as f:
                content = f.read()
                # Bersihkan komentar JSONC agar tidak error
                content = re.sub(r"//.*", "", content)
                content = re.sub(r",\s*([\]}])", r"\1", content)
                self.config = json.loads(content)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca config: {e}")
            self.root.destroy()

    def create_widgets(self):
        header = tk.Frame(self.root, bg="#1c2238")
        header.pack(fill="x")
        
        tk.Label(header, text=" Waybar Dynamic Launcher", font=("JetBrainsMono Nerd Font", 14, "bold"), 
                 fg="#8be9fd", bg="#1c2238", pady=15).pack()

        # Label informasi kolom
        info_frame = tk.Frame(self.root, bg="#1c2238")
        info_frame.pack(fill="x", padx=25)
        tk.Label(info_frame, text="App Name", fg="#6272a4", bg="#1c2238", width=12, anchor="w").pack(side="left")
        tk.Label(info_frame, text="Icon Path", fg="#6272a4", bg="#1c2238", width=35, anchor="w").pack(side="left")
        tk.Label(info_frame, text="Command (On-Click)", fg="#6272a4", bg="#1c2238").pack(side="left", padx=10)

        self.main_frame = tk.Frame(self.root, bg="#1c2238")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=5)

        self.refresh_app_list()

        btn_frame = tk.Frame(self.root, bg="#1c2238", pady=15)
        btn_frame.pack(fill="x", side="bottom")

        tk.Button(btn_frame, text="󰐕 ADD NEW APP", command=self.add_app_gui, 
                  bg="#50fa7b", fg="#1c2238", font=("bold"), width=18).pack(side="left", padx=20)
        
        tk.Button(btn_frame, text="󰔟 SAVE & RELOAD", command=self.save_config, 
                  bg="#8be9fd", fg="#1c2238", font=("bold"), width=18).pack(side="right", padx=20)

    def refresh_app_list(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.entries = {}
        image_keys = [k for k in self.config.keys() if k.startswith("image#")]

        for key in image_keys:
            row = tk.Frame(self.main_frame, bg="#2d3758", pady=8, padx=10)
            row.pack(fill="x", pady=2)

            name = key.split("#")[-1]
            tk.Label(row, text=name.upper(), fg="#ff79c6", bg="#2d3758", width=10, anchor="w", font=("bold", 9)).pack(side="left")

            val_path = tk.StringVar(value=self.config[key].get("path", ""))
            tk.Entry(row, textvariable=val_path, bg="#1c2238", fg="white", width=30, borderwidth=0).pack(side="left", padx=5)
            tk.Button(row, text="󰉋", command=lambda v=val_path: self.browse_image(v), bg="#44475a", fg="white", bd=0).pack(side="left")

            val_action = tk.StringVar(value=self.config[key].get("on-click", ""))
            tk.Entry(row, textvariable=val_action, bg="#1c2238", fg="#f1fa8c", width=20, borderwidth=0).pack(side="left", padx=10)

            tk.Button(row, text="󰆴", fg="#ff5555", bg="#2d3758", borderwidth=0, font=("bold", 12),
                      command=lambda k=key: self.delete_app(k)).pack(side="right")

            self.entries[key] = (val_path, val_action)

    def browse_image(self, var):
        f = filedialog.askopenfilename(filetypes=[("Images", "*.png *.svg *.jpg *.jpeg")])
        if f: var.set(f)

    def add_app_gui(self):
        name = simpledialog.askstring("Launcher", "Nama Aplikasi (cth: Firefox):")
        if not name: return
        
        img = filedialog.askopenfilename(title="Pilih Icon", filetypes=[("Images", "*.png *.svg")])
        if img:
            key = f"image#{name.lower()}"
            self.config[key] = {
                "path": img,
                "size": 22, 
                "on-click": name.lower(),
                "tooltip": True
            }
            
            # Otomatis masukkan ke grup apps agar sesuai CSS Jelly kamu
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
            messagebox.showinfo("Sukses", "Waybar Launcher Aktif!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal simpan: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WaybarAppsEditor(root)
    root.mainloop()