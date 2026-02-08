import tkinter as tk
from tkinter import messagebox
import json
import os

# Sesuaikan path ke file config waybar kamu
CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class WaybarAppsEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Apps Editor")
        self.root.geometry("500x400")
        self.root.configure(bg="#1c2238") # Warna senada dengan style waybar kamu

        self.load_config()
        self.create_widgets()

    def load_config(self):
        try:
            with open(CONFIG_PATH, 'r') as f:
                # Membersihkan komentar // jika ada agar json.loads bekerja
                lines = [line for line in f if not line.strip().startswith("//")]
                self.config = json.loads("".join(lines))
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membaca config: {e}")
            self.root.destroy()

    def create_widgets(self):
        title_label = tk.Label(self.root, text="Edit Icons & Actions", font=("JetBrainsMono Nerd Font", 14, "bold"), 
                               fg="#8be9fd", bg="#1c2238", pady=10)
        title_label.pack()

        self.entries = {}
        
        # Daftar module apps yang ada di config
        # Sesuaikan key ini dengan nama di file config json kamu
        app_keys = ["custom/browser", "custom/terminal", "custom/files", "custom/editor", "custom/spotify"]

        for key in app_keys:
            if key in self.config:
                frame = tk.Frame(self.root, bg="#1c2238", pady=5)
                frame.pack(fill="x", padx=20)

                lbl = tk.Label(frame, text=key.split('/')[-1].capitalize(), fg="white", bg="#1c2238", width=10, anchor="w")
                lbl.pack(side="left")

                # Entry untuk Icon (format)
                val_icon = tk.StringVar(value=self.config[key].get("format", ""))
                ent_icon = tk.Entry(frame, textvariable=val_icon, width=10, bg="#2d3758", fg="white", borderwidth=0)
                ent_icon.pack(side="left", padx=5)

                # Entry untuk Action (on-click)
                val_action = tk.StringVar(value=self.config[key].get("on-click", ""))
                ent_action = tk.Entry(frame, textvariable=val_action, bg="#2d3758", fg="white", borderwidth=0)
                ent_action.pack(side="left", fill="x", expand=True)

                self.entries[key] = (val_icon, val_action)

        btn_save = tk.Button(self.root, text="SAVE & RELOAD", command=self.save_config, 
                             bg="#8be9fd", fg="#1c2238", font=("bold"), pady=10)
        btn_save.pack(side="bottom", fill="x", padx=20, pady=20)

    def save_config(self):
        for key, (val_icon, val_action) in self.entries.items():
            self.config[key]["format"] = val_icon.get()
            self.config[key]["on-click"] = val_action.get()

        try:
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            # Perintah untuk restart Waybar otomatis
            os.system("pkill waybar && waybar &")
            messagebox.showinfo("Sukses", "Konfigurasi disimpan dan Waybar direload!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WaybarAppsEditor(root)
    root.mainloop()