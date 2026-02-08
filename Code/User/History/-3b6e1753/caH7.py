import tkinter as tk
from tkinter import messagebox, ttk
import json, os, re, glob

CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class WaybarManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar Manager - Centered Design")
        self.root.geometry("1150x780")
        self.root.configure(bg="#0b1220")

        self.colors = {
            "bg": "#0b1220",
            "row": "#121a2f",
            "row_alt": "#0f172a",
            "accent": "#38bdf8",
            "text": "#e5e7eb",
            "sub": "#64748b",
            "green": "#10b981",
            "red": "#f43f5e"
        }

        self.load_config()
        self.setup_styles()
        self.build_main_layout()
        self.refresh_list()

    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            self.config = {"group/apps": {"modules": []}}
            return
        try:
            with open(CONFIG_PATH, 'r') as f:
                content = f.read()
                content = re.sub(r"//.*", "", content)
                content = re.sub(r",\s*([\]}])", r"\1", content)
                self.config = json.loads(content)
        except:
            self.config = {"group/apps": {"modules": []}}

    def find_icon(self, icon_name):
        if not icon_name: return ""
        paths = ["/usr/share/icons/hicolor/scalable/apps", "/usr/share/icons/hicolor/48x48/apps", "/usr/share/pixmaps"]
        for p in paths:
            match = glob.glob(f"{p}/{icon_name}.*")
            if match: return match[0]
        return ""

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar", background=self.colors["row"], troughcolor=self.colors["bg"])

    def create_underlined_input(self, parent, var, bg_color):
        container = tk.Frame(parent, bg=bg_color)
        # justify="center" membuat teks di dalam input berada di tengah
        entry = tk.Entry(container, textvariable=var, bg=bg_color, fg=self.colors["text"],
                         insertbackground=self.colors["text"], relief="flat", 
                         font=("Inter", 10), highlightthickness=0, justify="center")
        entry.pack(fill="x", side="top")
        line = tk.Frame(container, bg=self.colors["accent"], height=1)
        line.pack(fill="x", side="bottom")
        return container

    def build_main_layout(self):
        # Header - Centered
        header_frame = tk.Frame(self.root, bg=self.colors["bg"], pady=40)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="WAYBAR CONFIGURATOR", font=("Inter", 26, "bold"),
                 bg=self.colors["bg"], fg=self.colors["text"]).pack()
        tk.Label(header_frame, text="All system icons and paths are centered for better visibility", 
                 font=("Inter", 10), bg=self.colors["bg"], fg=self.colors["sub"]).pack()

        # Table Header - Centered Labels
        table_head = tk.Frame(self.root, bg=self.colors["bg"], padx=45)
        table_head.pack(fill="x")
        
        cols = [("APPLICATION", 2), ("ICON SYSTEM PATH", 4), ("COMMAND LINE", 3), ("ACTION", 1)]
        for i, (name, weight) in enumerate(cols):
            # anchor="center" dan justify="center" untuk merapikan judul
            lbl = tk.Label(table_head, text=name, font=("Inter", 8, "bold"), 
                           bg=self.colors["bg"], fg=self.colors["sub"], anchor="center")
            lbl.grid(row=0, column=i, sticky="ew", padx=10)
            table_head.grid_columnconfigure(i, weight=weight)

        # Scrollable Area
        container = tk.Frame(self.root, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=40, pady=10)

        self.canvas = tk.Canvas(container, bg=self.colors["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=self.colors["bg"])

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((525, 0), window=self.scroll_frame, anchor="n", width=1050)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Footer Actions - Centered Buttons
        footer = tk.Frame(self.root, bg=self.colors["bg"], pady=40)
        footer.pack(fill="x")
        
        btn_container = tk.Frame(footer, bg=self.colors["bg"])
        btn_container.pack(expand=True) # Container tengah

        self.create_btn(btn_container, "+ ADD APPLICATION", self.colors["accent"], self.add_app_dialog).pack(side="left", padx=10)
        self.create_btn(btn_container, "APPLY & RESTART", self.colors["green"], self.save_and_reload).pack(side="left", padx=10)

    def create_btn(self, parent, text, color, cmd):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="#020617",
                         font=("Inter", 9, "bold"), relief="flat", padx=30, pady=12, cursor="hand2")

    def refresh_list(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        self.input_map = {}
        app_keys = [k for k in self.config if k.startswith("image#")]

        for i, key in enumerate(app_keys):
            row_bg = self.colors["row"] if i % 2 == 0 else self.colors["row_alt"]
            f = tk.Frame(self.scroll_frame, bg=row_bg, pady=20, padx=15)
            f.pack(fill="x", pady=2)

            name = key.split("#")[1].replace("_", " ").upper()
            tk.Label(f, text=name, bg=row_bg, fg=self.colors["text"], 
                     font=("Inter", 9, "bold"), width=20, anchor="center").grid(row=0, column=0, sticky="ew")

            p_var = tk.StringVar(value=self.config[key].get("path", ""))
            self.create_underlined_input(f, p_var, row_bg).grid(row=0, column=1, sticky="ew", padx=30)

            c_var = tk.StringVar(value=self.config[key].get("on-click", ""))
            self.create_underlined_input(f, c_var, row_bg).grid(row=0, column=2, sticky="ew", padx=30)

            tk.Button(f, text="✕", bg=row_bg, fg=self.colors["red"], relief="flat",
                      font=("Inter", 11, "bold"), command=lambda k=key: self.delete_item(k)).grid(row=0, column=3, sticky="ew")

            f.grid_columnconfigure(0, weight=2)
            f.grid_columnconfigure(1, weight=4)
            f.grid_columnconfigure(2, weight=3)
            f.grid_columnconfigure(3, weight=1)
            self.input_map[key] = (p_var, c_var)

    def add_app_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Select App")
        dialog.geometry("500x650")
        dialog.configure(bg=self.colors["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        # Centered Search Header
        tk.Label(dialog, text="SEARCH APPLICATION", font=("Inter", 10, "bold"), 
                 bg=self.colors["bg"], fg=self.colors["accent"]).pack(pady=(30, 0))
        
        search_var = tk.StringVar()
        self.create_underlined_input(dialog, search_var, self.colors["bg"]).pack(fill="x", padx=60, pady=20)

        lb = tk.Listbox(dialog, bg=self.colors["row"], fg=self.colors["text"], 
                        selectbackground=self.colors["accent"], relief="flat", 
                        font=("Inter", 10), borderwidth=0, highlightthickness=0, justify="center")
        lb.pack(fill="both", expand=True, padx=60)

        apps = self.get_system_apps()
        def update_lb(*args):
            lb.delete(0, "end")
            search = search_var.get().lower()
            for a in apps:
                if search in a["name"].lower(): lb.insert("end", a["name"])
        
        search_var.trace_add("write", update_lb)
        update_lb()

        def on_select():
            if not lb.curselection(): return
            sel_name = lb.get(lb.curselection()).strip()
            app_data = next(a for a in apps if a["name"] == sel_name)
            icon_path = self.find_icon(app_data['icon_id'])
            
            key = f"image#{app_data['name'].lower().replace(' ', '_')}"
            self.config[key] = {"path": icon_path if icon_path else "", "size": 24, "on-click": app_data["exec"].strip(), "tooltip": True}
            if key not in self.config["group/apps"]["modules"]: self.config["group/apps"]["modules"].append(key)
            dialog.destroy()
            self.refresh_list()

        footer_btn = tk.Frame(dialog, bg=self.colors["bg"], pady=30)
        footer_btn.pack(fill="x")
        self.create_btn(footer_btn, "CONFIRM", self.colors["accent"], on_select).pack(expand=True)

    def get_system_apps(self):
        found = []
        for path in ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]:
            if not os.path.exists(path): continue
            for f in os.listdir(path):
                if f.endswith(".desktop"):
                    try:
                        with open(os.path.join(path, f), 'r') as file:
                            content = file.read()
                            name = re.search(r"^Name=(.*)", content, re.M)
                            exe = re.search(r"^Exec=([^%\n]*)", content, re.M)
                            ico = re.search(r"^Icon=(.*)", content, re.M)
                            if name and exe: found.append({"name": name.group(1), "exec": exe.group(1), "icon_id": ico.group(1) if ico else ""})
                    except: continue
        return sorted(found, key=lambda x: x["name"])

    def delete_item(self, key):
        if key in self.config: del self.config[key]
        if key in self.config["group/apps"]["modules"]: self.config["group/apps"]["modules"].remove(key)
        self.refresh_list()

    def save_and_reload(self):
        for key, (path_v, exec_v) in self.input_map.items():
            self.config[key]["path"] = path_v.get()
            self.config[key]["on-click"] = exec_v.get()
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=4)
        os.system("pkill waybar && waybar &")
        messagebox.showinfo("Success", "Configuration applied!")

if __name__ == "__main__":
    root = tk.Tk()
    app = WaybarManager(root)
    root.mainloop()