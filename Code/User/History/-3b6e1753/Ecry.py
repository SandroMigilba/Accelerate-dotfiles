import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import os
import re

# Sesuaikan path jika berbeda (Nobara biasanya di ~/.config/waybar/config)
CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class WaybarAppsEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Image Icon Editor")
        self.root.geometry("700x550")
        self.root.configure(bg="#1c2238")

        self.load_config()
        self.create_widgets()

    def load_config(self):
        try:
            if not os.path.exists(CONFIG_PATH):
                self.config = {}
                return
                
            with open(CONFIG_PATH, 'r') as f:
                content = f.read()
                # Bersihkan komentar // agar json.loads tidak error
                content = re.sub(r"//.*", "", content)
                content = re.sub(r",\s*([\]}])", r"\1", content)
                self.config = json.loads(content)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca config: {e}")
            self.root.destroy()

    def create_widgets(self):
        tk.Label(self.root, text="Waybar Image Shortcuts (Jelly Mode)", font=("JetBrainsMono Nerd Font", 14, "bold"), 
                 fg="#8be9fd", bg="#1c2238", pady=15).pack()

        self.main_frame = tk.Frame(self.root, bg="#1c2238")
        self.main_frame.pack(fill="both", expand=True, padx=20)

        self.refresh_app_list()

        btn_frame = tk.Frame(self.root, bg="#1c2238", pady=10)
        btn_frame.pack(fill="x", side="bottom")

        tk.Button(btn_frame, text="+ ADD IMAGE APP", command=self.add_app_gui, 
                  bg="#50fa7b", fg="#1c2238", font=("bold"), width=20).pack(side="left", padx=20, pady=10)
        
        tk.Button(btn_frame, text="SAVE & RELOAD", command=self.save_config, 
                  bg="#8be9fd", fg="#1c2238", font=("bold"), width=20).pack(side="right", padx=20, pady=10)

    def refresh_app_list(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.entries = {}
        # Cari module yang bertipe image
        image_keys = [k for k in self.config.keys() if k.startswith("image")]

        for key in image_keys:
            row = tk.Frame(self.main_frame, bg="#2d3758", pady=5, padx=10)
            row.pack(fill="x", pady=2)

            name = key.split("#")[-1] if "#" in key else "Image"
            tk.Label(row, text=name[:10], fg="#8be9fd", bg="#2d3758", width=10, anchor="w", font=("bold")).pack(side="left")

            val_path = tk.StringVar(value=self.config[key].get("path", ""))
            tk.Entry(row, textvariable=val_path, bg="#1c2238", fg="white", width=30).pack(side="left", padx=5)
            
            tk.Button(row, text="📁", command=lambda v=val_path: self.browse_image(v)).pack(side="left")

            val_action = tk.StringVar(value=self.config[key].get("on-click", ""))
            tk.Entry(row, textvariable=val_action, bg="#1c2238", fg="#f1fa8c", width=15).pack(side="left", padx=5)

            tk.Button(row, text="󰆴", fg="#ff5555", bg="#2d3758", borderwidth=0, 
                      command=lambda k=key: self.delete_app(k)).pack(side="right")

            self.entries[key] = (val_path, val_action)

    def browse_image(self, var):
        filename = filedialog.askopenfilename(title="Pilih Icon", 
                                            filetypes=[("Images", "*.png *.svg *.jpg *.jpeg")])
        if filename:
            var.set(filename)

    def add_app_gui(self):
        name = simpledialog.askstring("Input", "Nama Aplikasi (misal: discord):")
        if not name: return
        
        img_path = filedialog.askopenfilename(title="Pilih Gambar", 
                                            filetypes=[("Images", "*.png *.svg *.jpg")])
        if img_path:
            key = f"image#{name.lower()}"
            # Ukuran 20-24 biasanya pas untuk font 14px
            self.config[key] = {
                "path": img_path,
                "size": 22, 
                "on-click": name.lower(),
                "tooltip": False
            }
            
            # Masukkan ke dalam grup #apps sesuai CSS kamu
            if "group/apps" in self.config:
                if key not in self.config["group/apps"]["modules"]:
                    self.config["group/apps"]["modules"].append(key)
            else:
                # Jika group/apps belum ada, masukkan ke modules-left sebagai cadangan
                if "modules-left" in self.config:
                    self.config["modules-left"].append(key)
            
            self.refresh_app_list()

    def delete_app(self, key):
        if messagebox.askyesno("Hapus", f"Hapus {key}?"):
            if key in self.config: del self.config[key]
            # Bersihkan dari semua kemungkinan lokasi modul
            for section in ["modules-left", "modules-center", "modules-right"]:
                if section in self.config and key in self.config[section]:
                    self.config[section].remove(key)
            if "group/apps" in self.config and key in self.config["group/apps"]["modules"]:
                self.config["group/apps"]["modules"].remove(key)
            self.refresh_app_list()

    def save_config(self):
        for key, (val_path, val_action) in self.entries.items():
            self.config[key]["path"] = val_path.get()
            self.config[key]["on-click"] = val_action.get()

        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            # Restart Waybar untuk melihat perubahan
            os.system("pkill waybar && waybar &")
            messagebox.showinfo("Sukses", "Waybar Updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WaybarAppsEditor(root)
    root.mainloop()