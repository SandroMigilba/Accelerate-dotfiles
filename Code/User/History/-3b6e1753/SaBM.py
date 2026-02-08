def add_app(self):
        name = simpledialog.askstring("New App", "Masukkan nama aplikasi (misal: shotcut):")
        if name:
            key = f"custom/{name.lower()}"
            if key in self.config:
                messagebox.showwarning("Peringatan", "Aplikasi sudah ada!")
                return
            
            # DEFAULT UNTUK GAMBAR PNG:
            # Kita kosongkan "format" agar bisa diisi background-image via CSS
            # Atau isi dengan spasi agar modulnya tetap 'render' di Waybar
            self.config[key] = {
                "format": " ", 
                "on-click": name.lower(), 
                "tooltip-format": name.capitalize()
            }
            
            # Tambahkan ke list modul di group/apps
            if "group/apps" in self.config:
                if "modules" in self.config["group/apps"]:
                    self.config["group/apps"]["modules"].append(key)
            
            self.refresh_app_list()
            messagebox.showinfo("Info", f"Jangan lupa tambahkan CSS untuk #{key.replace('/', '-')} agar gambar PNG muncul!")

    def save_config(self):
        # Update data dari entry ke config object
        for key, (val_icon, val_action) in self.entries.items():
            self.config[key]["format"] = val_icon.get()
            self.config[key]["on-click"] = val_action.get()

        try:
            # Nobara/Hyprland terkadang sensitif dengan format JSON
            with open(CONFIG_PATH, 'w') as f:
                json.dump(self.config, f, indent=4)
            
            # Reload Waybar
            os.system("pkill waybar")
            os.system("waybar &") # Jalankan background
            messagebox.showinfo("Sukses", "Config disimpan & Waybar di-reload!")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menyimpan: {e}")