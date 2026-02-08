import tkinter as tk
from tkinter import messagebox, ttk
import json, os, re
# Tambahkan library untuk mencari icon path
import glob

CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class WaybarListManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Manager - Nobara Hyprland")
        self.root.geometry("1100x680")
        self.root.configure(bg="#0b1220")

        self.bg = "#0b1220"
        self.row = "#121a2f"
        self.row_alt = "#0f172a"
        self.input = "#1a2440"
        self.text = "#e5e7eb"
        self.sub = "#94a3b8"
        self.blue = "#38bdf8"
        self.green = "#22c55e"
        self.red = "#fb7185"

        self.load_config()
        self.build_ui()

    def find_icon_path(self, icon_name):
        """Mencari path lengkap icon dari sistem"""
        if not icon_name:
            return ""
        if os.path.isabs(icon_name):
            return icon_name
        
        # Lokasi standar icon di Linux
        search_paths = [
            os.path.expanduser("~/.local/share/icons"),
            "/usr/share/icons/hicolor/scalable/apps",
            "/usr/share/icons/hicolor/48x48/apps",
            "/usr/share/pixmaps"
        ]
        
        # Tambahkan pencarian ke tema aktif (biasanya di Nobara)
        for path in search_paths:
            # Cari file yang namanya mirip dengan icon_name + ekstensi
            matches = glob.glob(f"{path}/{icon_name}.*")
            if matches:
                return matches[0]
        
        return "" # Kosong jika tidak ketemu

    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            self.config = {"group/apps": {"modules": []}}
            return
        try:
            with open(CONFIG_PATH, 'r') as f:
                raw = f.read()
                raw = re.sub(r"//.*", "", raw)
                raw = re.sub(r",\s*([\]}])", r"\1", raw)
                self.config = json.loads(raw)
        except:
            self.config = {"group/apps": {"modules": []}}

    def build_ui(self):
        tk.Label(self.root, text="Waybar Manager", font=("Inter", 26, "bold"),
                 bg=self.bg, fg=self.text, pady=20).pack()

        header = tk.Frame(self.root, bg=self.bg)
        header.pack(fill="x", padx=24)
        self.col(header, "APP", 0)
        self.col(header, "ICON PATH", 1)
        self.col(header, "COMMAND", 2)
        self.col(header, "", 3)

        body = tk.Frame(self.root, bg=self.bg)
        body.pack(fill="both", expand=True, padx=24, pady=(8, 0))

        self.canvas = tk.Canvas(body, bg=self.bg, highlightthickness=0)
        sb = ttk.Scrollbar(body, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.list = tk.Frame(self.canvas, bg=self.bg)
        self.canvas.create_window((0, 0), window=self.list, anchor="nw")
        self.list.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.refresh()

        footer = tk.Frame(self.root, bg=self.bg, pady=18)
        footer.pack(fill="x", padx=24)
        self.btn(footer, "+ Add App", self.blue, self.add_app).pack(side="left")
        self.btn(footer, "Apply Changes", self.green, self.save).pack(side="right")

    def col(self, parent, text, col):
        tk.Label(parent, text=text, font=("Inter", 9, "bold"), bg=self.bg, fg=self.sub).grid(row=0, column=col, sticky="w", padx=(8, 12))
        parent.grid_columnconfigure(col, weight=1)

    def btn(self, parent, text, color, cmd):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="#020617",
                         font=("Inter", 10, "bold"), relief="flat", padx=28, pady=12, cursor="hand2")

    def refresh(self):
        for w in self.list.winfo_children(): w.destroy()
        self.entries = {}
        keys = [k for k in self.config if k.startswith("image#")]

        for i, key in enumerate(keys):
            bg = self.row if i % 2 == 0 else self.row_alt
            row = tk.Frame(self.list, bg=bg, height=48)
            row.pack(fill="x", pady=2)
            row.pack_propagate(False)

            name = key.split("#")[1].replace("_", " ").title()
            tk.Label(row, text=name, bg=bg, fg=self.text, font=("Inter", 10, "bold"), width=18, anchor="w").grid(row=0, column=0, padx=8)

            p = tk.StringVar(value=self.config[key].get("path", ""))
            tk.Entry(row, textvariable=p, bg=self.input, fg=self.text, insertbackground=self.text, relief="flat").grid(row=0, column=1, sticky="ew", padx=6)

            a = tk.StringVar(value=self.config[key].get("on-click", ""))
            tk.Entry(row, textvariable=a, bg=self.input, fg=self.text, insertbackground=self.text, relief="flat").grid(row=0, column=2, sticky="ew", padx=6)

            tk.Button(row, text="✕", bg=bg, fg=self.red, relief="flat", command=lambda k=key: self.remove(k), cursor="hand2").grid(row=0, column=3, padx=10)

            row.grid_columnconfigure(1, weight=1)
            row.grid_columnconfigure(2, weight=1)
            self.entries[key] = (p, a)

    def add_app(self):
        apps = self.get_apps()
        win = tk.Toplevel(self.root)
        win.title("Pilih Aplikasi")
        win.geometry("450x600")
        win.configure(bg=self.bg)

        search_var = tk.StringVar()
        tk.Entry(win, textvariable=search_var, bg=self.input, fg=self.text, relief="flat").pack(fill="x", padx=16, pady=10)

        lb = tk.Listbox(win, bg=self.row, fg=self.text, selectbackground=self.blue, relief="flat", font=("Inter", 10))
        lb.pack(fill="both", expand=True, padx=16)

        def populate(filter_txt=""):
            lb.delete(0, "end")
            for a in apps:
                if filter_txt.lower() in a["name"].lower():
                    lb.insert("end", a["name"])

        search_var.trace_add("write", lambda *args: populate(search_var.get()))
        populate()

        def pick():
            if not lb.curselection(): return
            selected_name = lb.get(lb.curselection())
            app = next(item for item in apps if item["name"] == selected_name)
            
            # Ambil path icon otomatis
            icon_path = self.find_icon_path(app['icon_raw'])
            
            if icon_path:
                key = f"image#{app['name'].lower().replace(' ','_')}"
                self.config[key] = {
                    "path": icon_path,
                    "size": 24,
                    "on-click": app["cmd"].strip(),
                    "tooltip": True
                }
                if key not in self.config["group/apps"]["modules"]:
                    self.config["group/apps"]["modules"].append(key)
                win.destroy()
                self.refresh()
            else:
                messagebox.showwarning("Icon Not Found", f"Tidak bisa menemukan file gambar untuk icon: {app['icon_raw']}")

        self.btn(win, "Tambah ke Waybar", self.blue, pick).pack(pady=16)

    def get_apps(self):
        apps = []
        dirs = ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]
        for d in dirs:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.endswith(".desktop"):
                        try:
                            with open(os.path.join(d, f), errors="ignore") as file:
                                txt = file.read()
                                n = re.search(r"^Name=(.*)", txt, re.M)
                                e = re.search(r"^Exec=([^%\n]*)", txt, re.M)
                                i = re.search(r"^Icon=(.*)", txt, re.M)
                                if n and e:
                                    apps.append({
                                        "name": n.group(1), 
                                        "cmd": e.group(1),
                                        "icon_raw": i.group(1) if i else ""
                                    })
                        except: continue
        return sorted(apps, key=lambda x: x["name"])

    def remove(self, key):
        if key in self.config: del self.config[key]
        if key in self.config["group/apps"]["modules"]:
            self.config["group/apps"]["modules"].remove(key)
        self.refresh()

    def save(self):
        for k, (p, a) in self.entries.items():
            self.config[k]["path"] = p.get()
            self.config[k]["on-click"] = a.get()
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=4)
        
        # Reload waybar (Nobara/Hyprland)
        os.system("pkill waybar")
        os.system("waybar &")
        messagebox.showinfo("Success", "Waybar has been reloaded!")

if __name__ == "__main__":
    root = tk.Tk()
    WaybarListManager(root)
    root.mainloop()