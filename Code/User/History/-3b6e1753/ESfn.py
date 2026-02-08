import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import re

# Path config Waybar
CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class WaybarAppsEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Apps Editor")
        self.root.geometry("600x500")
        self.root.configure(bg="#1c2238")

        self.load_config()
        self.create_widgets()

    def load_config(self):
        try:
            if not os.path.exists(CONFIG_PATH):
                raise FileNotFoundError("File config tidak ditemukan!")
                
            with open(CONFIG_PATH, 'r') as f:
                content = f.read()
                # Bersihkan komentar //
                content = re.sub(r"//.*", "", content)
                # Bersihkan trailing commas (koma di akhir objek sebelum })
                content = re.sub(r",\s*([\]}])", r"\1", content)
                
                self.config = json.loads(content)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca config: {e}")
            self.root.destroy()

    def create_widgets(self):
        # Header
        tk.Label(self.root, text="Waybar App Shortcuts Manager", font=("JetBrainsMono Nerd Font", 14, "bold"), 
                 fg="#8be9fd", bg="#1c2238", pady=15).pack()

        # Container Scrollable (Jika aplikasi banyak)
        self.main_frame = tk.Frame(self.root, bg="#1c2238")
        self.main_frame.pack(fill="both", expand=True, padx=20)

        self.refresh_app_list()

        # Footer Buttons
        btn_frame = tk.Frame(self.root, bg="#1c2238", pady=10)
        btn_frame.pack(fill="x", side="bottom")

        tk.Button(btn_frame, text="+ ADD NEW APP", command=self.add_app, 
                  bg="#50fa7b", fg="#1c2238", font=("bold"), width=15).pack(side="left", padx=20, pady=10)
        
        tk.Button(btn_frame, text="SAVE & RELOAD", command=self.save_config, 
                  bg="#8be9fd", fg="#1c2238", font=("bold"), width=15).pack(side="right", padx=20, pady=10)

    def refresh_app_list(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.entries = {}
        # Mencari semua module 'custom/...' yang ada di config
        app_keys = [k for k in self.config.keys() if k.startswith("custom/") and k != "custom/close"]

        for key in app_keys:
            row = tk.Frame(self.main_frame, bg="#2d3758", pady=5, padx=10, highlightthickness=1, highlightbackground="#1c2238")
            row.pack(fill="x", pady=2)

            name = key.replace("custom/", "").capitalize()
            tk.Label(row, text=name, fg="#8be9fd", bg="#2d3758", width=10, anchor="w", font=("bold")).pack(side="left")

            # Icon Entry
            val_icon = tk.StringVar(value=self.config[key].get("format", ""))
            tk.Entry(row, textvariable=val_icon, width=5, bg="#1c2238", fg="white", borderwidth=0, insertbackground="white").pack(side="left", padx=5)

            # Action Entry
            val_action = tk.StringVar(value=self.config[key].get("on-click", ""))
            tk.Entry(row, textvariable=val_action, bg="#1c2238", fg="white", borderwidth=0, insertbackground="white").pack(side="left", fill="x", expand=True, padx=5)

            # Delete Button
            tk.Button(row, text="󰆴", fg="#ff5555", bg="#2d3758", borderwidth=0, command=lambda k=key: self.delete_app(k)).pack(side="right")

            self.entries[key] = (val_icon, val_action)

    def add_app(self):
        name = simpledialog.askstring("New App", "Masukkan nama aplikasi (misal: discord):")
        if name:
            key = f"custom/{name.lower()}"
            if key in self.config:
                messagebox.showwarning("Peringatan", "Aplikasi sudah ada!")
                return
            
            # Tambahkan ke internal config
            self.config[key] = {"format": "󰍜", "on-click": name.lower(), "tooltip": False}
            
            # Tambahkan ke list modul di group/apps jika ada
            if "group/apps" in self.config:
                self.config["group/apps"]["modules"].append(key)
            
            self.refresh_app_list()

    def delete_app(self, key):
        if messagebox.askyesno("Hapus", f"Hapus {key}?"):
            del self.config[key]
            if "group/apps" in self.config:
                self.config["group/apps"]["modules"].remove(key)
            self.refresh_app_list()

    def save_config(self):
        # Update data dari entry ke config object
        for key, (val_icon, val_action) in self.entries.items():
            self.config[key]["format"] = val_icon.get()
            self.config[key]["on-click"] = val_action.get()

        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            os.system("pkill waybar && waybar &")
            messagebox.showinfo("Sukses", "Waybar Updated!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WaybarAppsEditor(root)
    root.mainloop()