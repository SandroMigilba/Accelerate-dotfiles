import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json, os, re

CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class BubbleWaybarManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Bubble Manager")
        self.root.geometry("1000x720")
        self.root.configure(bg="#f2f2f7")

        # Consistent Bubble Palette
        self.bg = "#f2f2f7"
        self.card = "#ffffff"
        self.input = "#f1f1f4"
        self.text = "#111111"
        self.sub = "#6e6e73"
        self.blue = "#5ac8fa"
        self.green = "#34c759"
        self.red = "#ff3b30"
        self.shadow = "#d1d1d6"

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
            text="Waybar Bubble Manager",
            font=("Inter", 28, "bold"),
            bg=self.bg,
            fg=self.text,
            pady=24
        ).pack()

        tk.Label(
            self.root,
            text="Clean bubble editor for Hyprland",
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
        self.canvas.create_window((0,0), window=self.list, anchor="nw")
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
            parent, text=text, command=cmd,
            bg=color, fg="white",
            font=("Inter", 10, "bold"),
            relief="flat", padx=32, pady=14,
            cursor="hand2"
        )

    # ---------- Cards ----------
    def refresh(self):
        for w in self.list.winfo_children():
            w.destroy()

        self.entries = {}
        keys = [k for k in self.config if k.startswith("image#")]

        for key in keys:
            c = tk.Canvas(self.list, height=170, bg=self.bg, highlightthickness=0)
            c.pack(fill="x", pady=12)

            self.rrect(c, 6, 6, 920, 164, 28, fill=self.shadow, outline="")
            self.rrect(c, 0, 0, 914, 158, 28, fill=self.card, outline="")

            card = tk.Frame(c, bg=self.card)
            c.create_window((24, 20), window=card, anchor="nw", width=860)

            # Title row
            head = tk.Frame(card, bg=self.card)
            head.pack(fill="x")

            name = key.split("#")[1].replace("_", " ").title()
            tk.Label(
                head, text=name,
                font=("Inter", 13, "bold"),
                bg=self.card, fg=self.text
            ).pack(side="left")

            tk.Button(
                head, text="Remove",
                fg=self.red, bg=self.card,
                relief="flat",
                command=lambda k=key: self.remove(k)
            ).pack(side="right")

            # Icon Path
            tk.Label(
                card, text="ICON PATH",
                font=("Inter", 8, "bold"),
                bg=self.card, fg=self.sub
            ).pack(anchor="w", pady=(14, 4))

            p = tk.StringVar(value=self.config[key].get("path", ""))
            tk.Entry(
                card, textvariable=p,
                bg=self.input, relief="flat"
            ).pack(fill="x", ipady=9)

            # Command
            tk.Label(
                card, text="COMMAND",
                font=("Inter", 8, "bold"),
                bg=self.card, fg=self.sub
            ).pack(anchor="w", pady=(14, 4))

            a = tk.StringVar(value=self.config[key].get("on-click", ""))
            tk.Entry(
                card, textvariable=a,
                bg=self.input, relief="flat"
            ).pack(fill="x", ipady=9)

            self.entries[key] = (p, a)

    # ---------- Logic ----------
    def add_app(self):
        apps = self.get_apps()
        win = tk.Toplevel(self.root)
        win.title("Select App")
        win.geometry("420x560")
        win.configure(bg=self.bg)

        lb = tk.Listbox(win, font=("Inter", 10))
        lb.pack(fill="both", expand=True, padx=20, pady=20)

        for a in apps:
            lb.insert("end", a["name"])

        def pick():
            if not lb.curselection(): return
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
                        txt = open(os.path.join(d,f), errors="ignore").read()
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
        for k,(p,a) in self.entries.items():
            self.config[k]["path"] = p.get()
            self.config[k]["on-click"] = a.get()
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=4)
        os.system("pkill waybar; waybar &")
        messagebox.showinfo("Done", "Waybar reloaded")

# ---------- Run ----------
if __name__ == "__main__":
    root = tk.Tk()
    BubbleWaybarManager(root)
    root.mainloop()
