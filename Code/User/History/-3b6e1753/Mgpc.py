import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
import json
import os
import re

# Path config Waybar Nobara/Hyprland
CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class WaybarAppsEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Dynamic Image Launcher")
        self.root.geometry("800x600")
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
                content = re.sub(r"//.*", "", content)
                content = re.sub(r",\s*([\]}])", r"\1", content)
                self.config = json.loads(content)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca config: {e}")
            self.root.destroy()

    def create_widgets(self):
        header = tk.Frame(self.root, bg="#1c2238")
        header.pack(fill="x")
        
        tk.Label(header, text="󰀻 Waybar App Launcher Editor", font=("JetBrainsMono Nerd Font", 16, "bold"), 
                 fg="#8be9fd", bg="#1c2238", pady=20).pack()

        # Frame untuk List Aplikasi
        self.canvas = tk.Canvas(self.root, bg="#1c2238", highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.main_frame = tk.Frame(self.canvas, bg="#1c2238")

        self.main_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True, padx=20)
        self.scrollbar.pack(side="right", fill="y")

        self.refresh_app_list()

        # Footer
        btn_frame = tk.Frame(self.root, bg="#1c2238", pady=20)
        btn_frame.pack(fill="x", side="bottom")

        tk.Button(btn_frame, text="󰐕 ADD NEW APP", command=self.add_app_gui, 
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

            # Path Gambar
            val_path = tk.StringVar(value=self.config[key].get("path", ""))
            tk.Entry(row, textvariable=val_path, bg="#1c2238", fg="#f8f8f2", width=25, borderwidth=0).pack(side="left", padx=5)
            tk.Button(row, text="󰉋", command=lambda v=val_path: self.browse_image(v), bg="#44475a", fg="white", bd=0).pack(side="left")

            # Kolom Perintah Aplikasi (On-Click)
            tk.Label(row, text=" Run:", fg="#f1fa8c", bg="#2d3758").pack(side="left", padx=5)
            val_action = tk.StringVar(value=self.config[key].get("on-click", ""))
            tk.Entry(row, textvariable=val_action, bg="#1c2238", fg="#f1fa8c", width=15, borderwidth=0).pack(side="left", padx=5)

            # Tombol Hapus
            tk.Button(row, text="󰆴", fg="#ff5555", bg="#2d3758", borderwidth=0, font=("bold", 12),
                      command=lambda k=key: self.delete_app(k)).pack(side="right")

            self.entries[key] = (val_path, val_action)

    def browse_image(self, var):
        f = filedialog.askopenfilename(filetypes=[("Images", "*.png *.svg *.jpg")])
        if f: var.set(f)

    def add_app_gui(self):
        name = simpledialog.askstring("Input", "Nama Aplikasi (cth: Spotify):")
        if not name: return
        
        command = simpledialog.askstring("Input", f"Perintah untuk membuka {name}\n(cth: spotify, kitty, thunar):")
        if not command: return

        img = filedialog.askopenfilename(title="Pilih Icon", filetypes=[("Images", "*.png *.svg")])
        if img:
            key = f"image#{name.lower()}"
            self.config[key] = {
                "path": img,
                "size": 22, 
                "on-click": command,
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
            messagebox.showinfo("Sukses", "Waybar Updated! Ikon siap diklik.")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal simpan: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WaybarAppsEditor(root)
    root.mainloop()