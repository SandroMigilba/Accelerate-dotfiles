import tkinter as tk
from tkinter import messagebox, ttk
import json, os, re, glob

CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class WaybarListManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Manager - Minimalist")
        self.root.geometry("1100x720")
        self.root.configure(bg="#0b1220")

        # Palette
        self.bg = "#0b1220"
        self.row = "#121a2f"
        self.row_alt = "#0f172a"
        self.input_bg = "#121a2f" # Sama dengan row agar menyatu
        self.accent = "#38bdf8"   # Warna border bawah (biru)
        self.text = "#e5e7eb"
        self.sub = "#94a3b8"
        self.blue = "#38bdf8"
        self.green = "#22c55e"
        self.red = "#fb7185"

        self.load_config()
        self.build_ui()

    # ---------- UI Helper: Underlined Entry ----------
    def underlined_entry(self, parent, variable, bg_color):
        """ Membuat input dengan hanya border bawah """
        container = tk.Frame(parent, bg=self.accent) # Frame luar sebagai warna border
        entry = tk.Entry(
            container, 
            textvariable=variable,
            bg=bg_color, 
            fg=self.text,
            insertbackground=self.text,
            relief="flat",
            font=("Inter", 10),
            highlightthickness=0
        )
        entry.pack(fill="x", pady=(0, 1)) # pady 1 pixel di bawah untuk memunculkan warna accent
        return container

    def find_icon_path(self, icon_name):
        if not icon_name: return ""
        if os.path.isabs(icon_name): return icon_name
        
        search_paths = [
            os.path.expanduser("~/.local/share/icons"),
            "/usr/share/icons/hicolor/scalable/apps",
            "/usr/share/icons/hicolor/48x48/apps",
            "/usr/share/pixmaps",
            "/usr/share/icons/Adwaita/48x48/apps"
        ]
        
        for path in search_paths:
            matches = glob.glob(f"{path}/{icon_name}.*")
            if matches: return matches[0]
        return ""

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
        # Header
        tk.Label(self.root, text="Waybar Manager", font=("Inter", 28, "bold"),
                 bg=self.bg, fg=self.text, pady=30).pack()

        header = tk.Frame(self.root, bg=self.bg)
        header.pack(fill="x", padx=40)
        self.col(header, "APPLICATION NAME", 0)
        self.col(header, "ICON SYSTEM PATH", 1)
        self.col(header, "EXEC COMMAND", 2)
        self.col(header, "", 3)

        # Body with Scroll
        body = tk.Frame(self.root, bg=self.bg)
        body.pack(fill="both", expand=True, padx=30, pady=(10, 0))

        self.canvas = tk.Canvas(body, bg=self.bg, highlightthickness=0)
        sb = ttk.Scrollbar(body, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.list = tk.Frame(self.canvas, bg=self.bg)
        self.canvas.create_window((0, 0), window=self.list, anchor="nw", width=1020)
        self.list.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.refresh()

        # Footer
        footer = tk.Frame(self.root, bg=self.bg, pady=25)
        footer.pack(fill="x", padx=40)
        self.btn(footer, "+ ADD NEW APP", self.blue, self.add_app).pack(side="left")
        self.btn(footer, "SAVE & RELOAD", self.green, self.save).pack(side="right")

    def col(self, parent, text, col):
        tk.Label(parent, text=text, font=("Inter", 8, "bold"), bg=self.bg, fg=self.sub).grid(row=0, column=col, sticky="w", padx=15)
        parent.grid_columnconfigure(col, weight=1)

    def btn(self, parent, text, color, cmd):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="#020617",
                         font=("Inter", 9, "bold"), relief="flat", padx=25, pady=10, cursor="hand2")

    def refresh(self):
        for w in self.list.winfo_children(): w.destroy()
        self.entries = {}
        keys = [k for k in self.config if k.startswith("image#")]

        for i, key in enumerate(keys):
            row_color = self.row if i % 2 == 0 else self.row_alt
            row = tk.Frame(self.list, bg=row_color, height=60)
            row.pack(fill="x", pady=1)
            row.pack_propagate(False)

            name = key.split("#")[1].replace("_", " ").upper()
            tk.Label(row, text=name, bg=row_color, fg=self.text, font=("Inter", 9, "bold"), width=20, anchor="w").grid(row=0, column=0, padx=20)

            # Underlined Inputs
            path_var = tk.StringVar(value=self.config[key].get("path", ""))
            self.underlined_entry(row, path_var, row_color).grid(row=0, column=1, sticky="ew", padx=15)

            cmd_var = tk.StringVar(value=self.config[key].get("on-click", ""))
            self.underlined_entry(row, cmd_var, row_color).grid(row=0, column=2, sticky="ew", padx=15)

            tk.Button(row, text="✕", bg=row_color, fg=self.red, relief="flat", 
                      command=lambda k=key: self.remove(k), font=("Inter", 12), cursor="hand2").grid(row=0, column=3, padx=20)

            row.grid_columnconfigure(1, weight=1)
            row.grid_columnconfigure(2, weight=1)
            self.entries[key] = (path_var, cmd_var)

    def add_app(self):
        apps = self.get_apps()
        win = tk.Toplevel(self.root)
        win.title("Search Application")
        win.geometry("450x600")
        win.configure(bg=self.bg)
        win.transient(self.root)

        search_var = tk.StringVar()
        # Search juga pakai underline
        search_frame = self.underlined_entry(win, search_var, self.bg)
        search_frame.pack(fill="x", padx=30, pady=20)

        lb = tk.Listbox(win, bg=self.row, fg=self.text, selectbackground=self.accent, 
                        relief="flat", font=("Inter", 10), borderwidth=0, highlightthickness=0)
        lb.pack(fill="both", expand=True, padx=30)

        def populate(filter_txt=""):
            lb.delete(0, "end")
            for a in apps:
                if filter_txt.lower() in a["name"].lower():
                    lb.insert("end", f"  {a['name']}")

        search_var.trace_add("write", lambda *args: populate(search_var.get()))
        populate()

        def pick():
            if not lb.curselection(): return
            sel_text = lb.get(lb.curselection()).strip()
            app = next(item for item in apps if item["name"] == sel_text)
            icon_path = self.find_icon_path(app['icon_raw'])
            
            if icon_path:
                key = f"image#{app['name'].lower().replace(' ','_')}"
                self.config[key] = {"path": icon_path, "size": 24, "on-click": app["cmd"].strip(), "tooltip": True}
                if key not in self.config["group/apps"]["modules"]:
                    self.config["group/apps"]["modules"].append(key)
                win.destroy()
                self.refresh()
            else:
                messagebox.showwarning("Icon Error", "System icon file not found.")

        self.btn(win, "ADD TO WAYBAR", self.accent, pick).pack(pady=25)

    def get_apps(self):
        apps = []
        dirs = ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]
        for d in dirs:
            if not os.path.exists(d): continue
            for f in os.listdir(d):
                if f.endswith(".desktop"):
                    try:
                        with open(os.path.join(d, f), errors="ignore") as file:
                            t = file.read()
                            n = re.search(r"^Name=(.*)", t, re.M)
                            e = re.search(r"^Exec=([^%\n]*)", t, re.M)
                            i = re.search(r"^Icon=(.*)", t, re.M)
                            if n and e:
                                apps.append({"name": n.group(1), "cmd": e.group(1), "icon_raw": i.group(1) if i else ""})
                    except: continue
        return sorted(apps, key=lambda x: x["name"])

    def remove(self, key):
        if key in self.config: del self.config[key]
        if key in self.config["group/apps"]["modules"]: self.config["group/apps"]["modules"].remove(key)
        self.refresh()

    def save(self):
        for k, (p, a) in self.entries.items():
            self.config[k]["path"] = p.get()
            self.config[k]["on-click"] = a.get()
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=4)
        os.system("pkill waybar && waybar &")
        messagebox.showinfo("Success", "Configuration Applied!")

if __name__ == "__main__":
    root = tk.Tk()
    WaybarListManager(root)
    root.mainloop()