import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json, os, re

CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class DarkNavyWaybarManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Manager")
        self.root.geometry("1000x720")
        self.root.configure(bg="#0b1220")

        # 🎨 Dark Navy Palette
        self.bg = "#0b1220"
        self.card = "#121a2f"
        self.input = "#1a2440"
        self.text = "#e5e7eb"
        self.sub = "#94a3b8"
        self.blue = "#38bdf8"
        self.green = "#22c55e"
        self.red = "#fb7185"
        self.shadow = "#020617"

        self.load_config()
        self.build_ui()

    # ---------- Rounded Rectangle ----------
    def rrect(self, c, x1, y1, x2, y2, r, **kw):
        p = [
            x1+r,y1, x2-r,y1, x2,y1, x2,y1+r,
            x2,y2-r, x2,y2, x2-r,y2, x1+r,y2,
            x1,y2, x1,y2-r, x1,y1+r, x1,y1
        ]
        return c.create_polygon(p, smooth=True, **kw)

    # ---------- Config ----------
    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            self.config = {"group/apps": {"modules": []}}
            return
        raw = open(CONFIG_PATH).read()
        raw = re.sub(r"//.*", "", raw)
        raw = re.sub(r",\s*([\]}])", r"\1", raw)
        self.config = json.loads(raw)

    # ---------- UI ----------
    def build_ui(self):
        # Header
        tk.Label(
            self.root,
            text="Waybar Manager",
            font=("Inter", 28, "bold"),
            bg=self.bg,
            fg=self.text,
            pady=24
        ).pack()

        tk.Label(
            self.root,
            text="Dark Navy Bubble UI · Hyprland",
            font=("Inter", 11),
            bg=self.bg,
            fg=self.sub
        ).pack(pady=(0, 20))

        # Body
        body = tk.Frame(self.root, bg=self.bg)
        body.pack(fill="both", expand=True, padx=40)

        self.canvas = tk.Canvas(body, bg=self.bg, highlightthickness=0)
        sb = ttk.Scrollbar(body, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.list = tk.Frame(self.canvas, bg=self.bg)
        self.canvas.create_window((0, 0), window=self.list, anchor="nw")
        self.list.bind("<Configure>", lambda e:
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.refresh()

        # Footer
        footer = tk.Frame(self.root, bg=self.bg, pady=24)
        footer.pack(fill="x", padx=40)

        self.btn(footer, "+ Add App", self.blue, self.add_app).pack(side="left")
        self.btn(footer, "Apply", self.green, self.save).pack(side="right")

    # ---------- Button ----------
    def btn(self, parent, text, color, cmd):
        return tk.Button(
            parent,
            text=text,
            command=cmd,
            bg=color,
            fg="#020617",
            font=("Inter", 10, "bold"),
            relief="flat",
            padx=32,
            pady=14,
            cursor="hand2",
            activebackground=color
        )

    # ---------- Cards ----------
    def refresh(self):
        for w in self.list.winfo_children():
            w.destroy()

        self.entries = {}
        keys = [k for k in self.config if k.startswith("image#")]

        for key in keys:
            c = tk.Canvas(self.list, height=176, bg=self.bg, highlightthickness=0)
            c.pack(fill="x", pady=12)

            self.rrect(c, 6, 6, 920, 170, 30, fill=self.shadow, outline="")
            self.rrect(c, 0, 0, 914, 164, 30, fill=self.card, outline="")

            card = tk.Frame(c, bg=self.card)
            c.create_window((24, 22), window=card, anchor="nw", width=860)

            # Header row (aligned)
            head = tk.Frame(card, bg=self.card)
            head.pack(fill="x")

            name = key.split("#")[1].replace("_", " ").title()
            tk.Label(
                head,
                text=name,
                font=("Inter", 13, "bold"),
                bg=self.card,
                fg=self.text
            ).pack(side="left")

            tk.Button(
                head,
                text="Remove",
                fg=self.red,
                bg=self.card,
                relief="flat",
                command=lambda k=key: self.remove(k),
                cursor="hand2"
            ).pack(side="right")

            # Grid layout (SEJAJAR)
            grid = tk.Frame(card, bg=self.card)
            grid.pack(fill="x", pady=(18, 0))

            # Icon Path
            tk.Label(
                grid, text="ICON PATH",
                font=("Inter", 8, "bold"),
                bg=self.card, fg=self.sub
            ).grid(row=0, column=0, sticky="w")

            p = tk.StringVar(value=self.config[key].get("path", ""))
            tk.Entry(
                grid, textvariable=p,
                bg=self.input, fg=self.text,
                insertbackground=self.text,
                relief="flat"
            ).grid(row=1, column=0, sticky="ew", pady=(6, 0))

            # Command
            tk.Label(
                grid, text="COMMAND",
                font=("Inter", 8, "bold"),
                bg=self.card, fg=self.sub
            ).grid(row=0, column=1, sticky="w", padx=(20, 0))

            a = tk.StringVar(value=self.config[key].get("on-click", ""))
            tk.Entry(
                grid, textvariable=a,
                bg=self.input, fg=self.text,
                insertbackground=self.text,
                relief="flat"
            ).grid(row=1, column=1, sticky="ew", padx=(20, 0), pady=(6, 0))

            grid.columnconfigure(0, weight=1)
            grid.columnconfigure(1, weight=1)

            self.entries[key] = (p, a)

    # ---------- Logic ----------
    def add_app(self):
        apps = self.get_apps()
        win = tk.Toplevel(self.root)
        win.title("Select App")
        win.geometry("420x560")
        win.configure(bg=self.bg)

        lb = tk.Listbox(
            win, bg=self.card, fg=self.text,
            selectbackground=self.blue,
            relief="flat"
        )
        lb.pack(fill="both", expand=True, padx=20, pady=20)

        for a in apps:
            lb.insert("end", a["name"])

        def pick():
            if not lb.curselection():
                return
            app = apps[lb.curselection()[0]]
            icon = filedialog.askopenfilename(
                filetypes=[("Images", "*.png *.svg *.jpg")]
            )
            if icon:
                key = f"image#{app['name'].lower().replace(' ','_')}"
                self.config[key] = {
                    "path": icon,
                    "size": 22,
                    "on-click": app["cmd"],
                    "tooltip": True
                }
                self.config["group/apps"]["modules"].append(key)
                win.destroy()
                self.refresh()

        self.btn(win, "Add", self.blue, pick).pack(pady=20)

    def get_apps(self):
        apps = []
        for d in ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]:
            if os.path.exists(d):
                for f in os.listdir(d):
                    if f.endswith(".desktop"):
                        txt = open(os.path.join(d, f), errors="ignore").read()
                        n = re.search(r"^Name=(.*)", txt, re.M)
                        e = re.search(r"^Exec=([^%\n]*)", txt, re.M)
                        if n and e:
                            apps.append({"name": n.group(1), "cmd": e.group(1)})
        return sorted(apps, key=lambda x: x["name"])

    def remove(self, key):
        del self.config[key]
        self.config["group/apps"]["modules"].remove(key)
        self.refresh()

    def save(self):
        for k, (p, a) in self.entries.items():
            self.config[k]["path"] = p.get()
            self.config[k]["on-click"] = a.get()
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=4)
        os.system("pkill waybar; waybar &")
        messagebox.showinfo("Done", "Waybar reloaded")

# ---------- Run ----------
if __name__ == "__main__":
    root = tk.Tk()
    DarkNavyWaybarManager(root)
    root.mainloop()
