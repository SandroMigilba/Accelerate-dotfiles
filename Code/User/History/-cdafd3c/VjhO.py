import sys
import subprocess
import threading
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QHBoxLayout, QScrollArea, QFrame, QMenu)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

class WorkerSignals(QObject):
    finished = pyqtSignal(list)

class BluetoothItem(QFrame):
    def __init__(self, device, parent_gui):
        super().__init__()
        self.device = device
        self.parent_gui = parent_gui
        self.init_item()

    def init_item(self):
        layout = QHBoxLayout(self)
        # Style berdasarkan status
        if self.device['connected']:
            bg, border = "rgba(0, 150, 255, 0.25)", "1px solid #0096ff"
        elif self.device['paired']:
            bg, border = "rgba(255, 255, 255, 0.1)", "1px solid rgba(255,255,255,0.1)"
        else:
            bg, border = "rgba(255, 255, 255, 0.03)", "1px dashed rgba(255,255,255,0.1)"
            
        self.setStyleSheet(f"background-color: {bg}; border: {border}; border-radius: 12px; margin: 2px;")

        # Info Perangkat
        icon = "󰂱 " if self.device['connected'] else "󰂯 "
        name = self.device['name'] if self.device['name'] else "Unknown"
        self.label = QLabel(f"{icon}{name}")
        self.label.setStyleSheet("color: white; font-weight: bold; border: none; background: transparent;")
        
        # Tombol Aksi Utama
        if self.device['connected']:
            btn_text, btn_style = "Disconnect", "background: rgba(255, 50, 50, 0.4);"
        elif self.device['paired']:
            btn_text, btn_style = "Connect", "background: rgba(0, 150, 255, 0.4);"
        else:
            btn_text, btn_style = "Pair", "background: rgba(80, 250, 123, 0.4); color: black;"

        self.btn = QPushButton(btn_text)
        self.btn.setFixedWidth(85)
        self.btn.setStyleSheet(f"{btn_style} border: none; font-size: 10px; padding: 6px; border-radius: 6px; font-weight: bold;")
        self.btn.clicked.connect(self.main_action)

        # Tombol Menu (Titik Tiga) untuk fungsi tambahan (Trust/Remove)
        self.btn_menu = QPushButton("")
        self.btn_menu.setFixedWidth(30)
        self.btn_menu.setStyleSheet("background: transparent; border: none; color: gray;")
        self.btn_menu.clicked.connect(self.show_context_menu)

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.btn)
        layout.addWidget(self.btn_menu)

    def main_action(self):
        if not self.device['paired']:
            self.parent_gui.execute_bt_cmd("pair", self.device['mac'])
        else:
            action = "disconnect" if self.device['connected'] else "connect"
            self.parent_gui.execute_bt_cmd(action, self.device['mac'])

    def show_context_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("background-color: #222; color: white; border: 1px solid #444;")
        
        trust_act = menu.addAction("Trust Device" if not self.device['trusted'] else "Untrust Device")
        remove_act = menu.addAction("Remove/Unpair")
        
        action = menu.exec(self.btn_menu.mapToGlobal(self.btn_menu.rect().bottomLeft()))
        
        if action == trust_act:
            cmd = "trust" if not self.device['trusted'] else "untrust"
            self.parent_gui.execute_bt_cmd(cmd, self.device['mac'])
        elif action == remove_act:
            self.parent_gui.execute_bt_cmd("remove", self.device['mac'])

class GlassBT(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.signals.finished.connect(self.populate_list)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Bluetooth Manager Pro')
        self.setFixedSize(420, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.main_layout = QVBoxLayout(self)
        
        # Header dengan Power Toggle
        header = QHBoxLayout()
        self.title_label = QLabel(" Bluetooth")
        self.title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        
        self.pwr_btn = QPushButton("ON")
        self.pwr_btn.setFixedSize(50, 25)
        self.update_pwr_btn_style(True)
        self.pwr_btn.clicked.connect(self.toggle_power)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background: rgba(255, 50, 50, 0.2); border-radius: 15px; border: none;")
        close_btn.clicked.connect(self.close)
        
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.pwr_btn)
        header.addWidget(close_btn)
        self.main_layout.addLayout(header)

        # Scan Button
        self.scan_btn = QPushButton("🔍 Scan for Devices")
        self.scan_btn.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.05); padding: 12px; border: 1px solid rgba(255,255,255,0.1); font-weight: bold; }
            QPushButton:hover { background: rgba(255,255,255,0.15); }
        """)
        self.scan_btn.clicked.connect(self.start_scan)
        self.main_layout.addWidget(self.scan_btn)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.setStyleSheet("""
            QWidget { background-color: rgba(15, 15, 15, 0.9); border-radius: 20px; color: white; }
            QScrollArea { border: none; background: transparent; }
        """)
        self.refresh_devices()

    def update_pwr_btn_style(self, is_on):
        color = "#50fa7b" if is_on else "#ff5555"
        self.pwr_btn.setText("ON" if is_on else "OFF")
        self.pwr_btn.setStyleSheet(f"background: {color}; color: black; border-radius: 12px; font-weight: bold;")

    def toggle_power(self):
        new_state = "on" if self.pwr_btn.text() == "OFF" else "off"
        subprocess.run(["bluetoothctl", "power", new_state], check=False)
        self.update_pwr_btn_style(new_state == "on")
        QTimer.singleShot(1000, self.refresh_devices)

    def start_scan(self):
        self.scan_btn.setText("Searching...")
        subprocess.Popen(["bluetoothctl", "scan", "on"])
        QTimer.singleShot(10000, lambda: subprocess.Popen(["bluetoothctl", "scan", "off"]))
        self.refresh_devices()

    def refresh_devices(self):
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def fetch_data(self):
        devs = {}
        try:
            # Menggabungkan Paired dan Visible Devices
            for cmd in ["paired-devices", "devices"]:
                out = subprocess.check_output(["bluetoothctl", cmd]).decode().splitlines()
                for line in out:
                    p = line.split(' ', 2)
                    if len(p) >= 3:
                        devs[p[1]] = {'mac': p[1], 'name': p[2], 'paired': False, 'connected': False, 'trusted': False}

            for mac in devs:
                info = subprocess.check_output(["bluetoothctl", "info", mac]).decode()
                devs[mac]['paired'] = "Paired: yes" in info
                devs[mac]['connected'] = "Connected: yes" in info
                devs[mac]['trusted'] = "Trusted: yes" in info
            
            # Sort: Connected > Paired > New
            sorted_list = sorted(devs.values(), key=lambda x: (x['connected'], x['paired']), reverse=True)
            self.signals.finished.emit(sorted_list)
        except: self.signals.finished.emit([])

    def populate_list(self, devices):
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for d in devices:
            self.list_layout.addWidget(BluetoothItem(d, self))
        self.scan_btn.setText("🔍 Scan for Devices")

    def execute_bt_cmd(self, action, mac):
        self.title_label.setText("🔄 Processing...")
        # Perintah Trust sangat penting agar auto-reconnect jalan
        subprocess.run(["bluetoothctl", action, mac], check=False)
        QTimer.singleShot(2000, self.refresh_devices)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassBT()
    ex.show()
    sys.exit(app.exec())