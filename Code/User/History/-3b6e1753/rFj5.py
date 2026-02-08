import tkinter as tk
from tkinter import messagebox, ttk
import json, os, re, glob

# Path konfigurasi Waybar
CONFIG_PATH = os.path.expanduser("~/.config/waybar/config")

class WaybarManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Waybar App Manager")
        self.root.geometry("1150x750")
        self.root.configure(bg="#0b1220")

        # --- Palette & Theme ---
        self.colors = {
            "bg": "#0b1220",
            "row": "#121a2f",
            "row_alt": "#0f172a",
            "accent": "#38bdf8",  # Biru Nobara
            "text": "#e5e7eb",
            "sub": "#64748b",
            "green": "#10b981",
            "red": "#f43f5e"
        }

        self.load_config()
        self.setup_styles()
        self.build_main_layout()
        self.refresh_list()

    # ---------- Core Logic ----------
    def load_config(self):
        if not os.path.exists(CONFIG_PATH):
            self.config = {"group/apps": {"modules": []}}
            return
        try:
            with open(CONFIG_PATH, 'r') as f:
                content = f.read()
                content = re.sub(r"//.*", "", content) # Hapus comment //
                content = re.sub(r",\s*([\]}])", r"\1", content) # Fix trailing commas
                self.config = json.loads(content)
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = {"group/apps": {"modules": []}}

    def find_icon(self, icon_name):
        if not icon_name: return ""
        if os.path.isabs(icon_name): return icon_name
        
        paths = [
            os.path.expanduser("~/.local/share/icons"),
            "/usr/share/icons/hicolor/scalable/apps",
            "/usr/share/icons/hicolor/48x48/apps",
            "/usr/share/pixmaps"
        ]
        for p in paths:
            match = glob.glob(f"{p}/{icon_name}.*")
            if match: return match[0]
        return ""

    # ---------- UI Components ----------
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar", 
                        background=self.colors["row"], 
                        troughcolor=self.colors["bg"], 
                        bordercolor=self.colors["bg"], 
                        arrowcolor=self.colors["accent"])

    def create_underlined_input(self, parent, var, bg_color):
        container = tk.Frame(parent, bg=bg_color)
        entry = tk.Entry(container, textvariable=var, bg=bg_color, fg=self.colors["text"],
                         insertbackground=self.colors["text"], relief="flat", 
                         font=("Inter", 10), highlightthickness=0)
        entry.pack(fill="x", side="top", pady=(0, 0))
        
        # Garis bawah (Underline)
        line = tk.Frame(container, bg=self.colors["accent"], height=1)
        line.pack(fill="x", side="bottom")
        return container

    def build_main_layout(self):
        # Header Section
        header_frame = tk.Frame(self.root, bg=self.colors["bg"], pady=30)
        header_frame.pack(fill="x")
        
        tk.Label(header_frame, text="WAYBAR CONFIGURATOR", font=("Inter", 24, "bold"),
                 bg=self.colors["bg"], fg=self.colors["text"]).pack()
        tk.Label(header_frame, text="Manage your portable OS application shortcuts", 
                 font=("Inter", 10), bg=self.colors["bg"], fg=self.colors["sub"]).pack()

        # Table Header
        table_head = tk.Frame(self.root, bg=self.colors["bg"], padx=45)
        table_head.pack(fill="x")
        
        cols = [("APPLICATION", 0.2), ("ICON PATH", 0.4), ("EXECUTION COMMAND", 0.3), ("", 0.1)]
        for i, (name, weight) in enumerate(cols):
            lbl = tk.Label(table_head, text=name, font=("Inter", 8, "bold"), 
                           bg=self.colors["bg"], fg=self.colors["sub"])
            lbl.grid(row=0, column=i, sticky="w", padx=10)
            table_head.grid_columnconfigure(i, weight=int(weight*10))

        # Content Area with Scroll
        container = tk.Frame(self.root, bg=self.colors["bg"])
        container.pack(fill="both", expand=True, padx=40, pady=10)

        self.canvas = tk.Canvas(container, bg=self.colors["bg"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=self.colors["bg"])

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=1050)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Footer Action Bar
        footer = tk.Frame(self.root, bg=self.colors["bg"], pady=30, padx=50)
        footer.pack(fill="x")

        self.create_btn(footer, "+ ADD APPLICATION", self.colors["accent"], self.add_app_dialog).pack(side="left")
        self.create_btn(footer, "APPLY & RESTART", self.colors["green"], self.save_and_reload).pack(side="right")

    def create_btn(self, parent, text, color, cmd):
        return tk.Button(parent, text=text, command=cmd, bg=color, fg="#020617",
                         font=("Inter", 9, "bold"), relief="flat", padx=25, pady=12, cursor="hand2")

    # ---------- Interaction ----------
    def refresh_list(self):
        for w in self.scroll_frame.winfo_children(): w.destroy()
        self.input_map = {}
        
        app_keys = [k for k in self.config if k.startswith("image#")]

        for i, key in enumerate(app_keys):
            row_bg = self.colors["row"] if i % 2 == 0 else self.colors["row_alt"]
            f = tk.Frame(self.scroll_frame, bg=row_bg, pady=15, padx=15)
            f.pack(fill="x", pady=2)

            name = key.split("#")[1].replace("_", " ").upper()
            tk.Label(f, text=name, bg=row_bg, fg=self.colors["text"], 
                     font=("Inter", 9, "bold"), width=22, anchor="w").grid(row=0, column=0)

            p_var = tk.StringVar(value=self.config[key].get("path", ""))
            self.create_underlined_input(f, p_var, row_bg).grid(row=0, column=1, sticky="ew", padx=20)

            c_var = tk.StringVar(value=self.config[key].get("on-click", ""))
            self.create_underlined_input(f, c_var, row_bg).grid(row=0, column=2, sticky="ew", padx=20)

            tk.Button(f, text="", bg=row_bg, fg=self.colors["red"], relief="flat",
                      font=("Inter", 12), command=lambda k=key: self.delete_item(k)).grid(row=0, column=3, padx=10)

            f.grid_columnconfigure(1, weight=4)
            f.grid_columnconfigure(2, weight=3)
            self.input_map[key] = (p_var, c_var)

    def add_app_dialog(self):
        # Dialog pencarian aplikasi
        dialog = tk.Toplevel(self.root)
        dialog.title("Select App")
        dialog.geometry("500x650")
        dialog.configure(bg=self.colors["bg"])
        dialog.transient(self.root)
        dialog.grab_set()

        search_var = tk.StringVar()
        self.create_underlined_input(dialog, search_var, self.colors["bg"]).pack(fill="x", padx=40, pady=30)

        lb = tk.Listbox(dialog, bg=self.colors["row"], fg=self.colors["text"], 
                        selectbackground=self.colors["accent"], relief="flat", 
                        font=("Inter", 10), borderwidth=0, highlightthickness=0)
        lb.pack(fill="both", expand=True, padx=40)

        apps = self.get_system_apps()
        
        def update_lb(*args):
            lb.delete(0, "end")
            search = search_var.get().lower()
            for a in apps:
                if search in a["name"].lower():
                    lb.insert("end", f"  {a['name']}")

        search_var.trace_add("write", update_lb)
        update_lb()

        def on_select():
            if not lb.curselection(): return
            selected_name = lb.get(lb.curselection()).strip()
            app_data = next(a for a in apps if a["name"] == selected_name)
            
            icon_path = self.find_icon(app_data['icon_id'])
            if not icon_path:
                messagebox.showwarning("Icon Warning", f"Could not find icon for {selected_name}")
                return

            key = f"image#{app_data['name'].lower().replace(' ', '_')}"
            self.config[key] = {
                "path": icon_path,
                "size": 24,
                "on-click": app_data["exec"].strip(),
                "tooltip": True
            }
            if key not in self.config["group/apps"]["modules"]:
                self.config["group/apps"]["modules"].append(key)
            
            dialog.destroy()
            self.refresh_list()

        self.create_btn(dialog, "CONFIRM SELECTION", self.colors["accent"], on_select).pack(pady=30)

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
                            if name and exe:
                                found.append({
                                    "name": name.group(1),
                                    "exec": exe.group(1),
                                    "icon_id": ico.group(1) if ico else ""
                                })
                    except: continue
        return sorted(found, key=lambda x: x["name"])

    def delete_item(self, key):
        if key in self.config: del self.config[key]
        if key in self.config["group/apps"]["modules"]:
            self.config["group/apps"]["modules"].remove(key)
        self.refresh_list()

    def save_and_reload(self):
        for key, (path_v, exec_v) in self.input_map.items():
            self.config[key]["path"] = path_v.get()
            self.config[key]["on-click"] = exec_v.get()
        
        try:
            with open(CONFIG_PATH, "w") as f:
                json.dump(self.config, f, indent=4)
            os.system("pkill waybar && waybar &")
            messagebox.showinfo("Success", "Waybar configuration updated and reloaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WaybarManager(root)
    root.mainloop()