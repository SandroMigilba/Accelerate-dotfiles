import sys
import subprocess
import threading
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QHBoxLayout, QScrollArea, QFrame)
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
        if self.device['connected']:
            bg, border = "rgba(0, 150, 255, 0.2)", "1px solid #0096ff"
        elif self.device['paired']:
            bg, border = "rgba(255, 255, 255, 0.1)", "none"
        else:
            bg, border = "rgba(255, 255, 255, 0.05)", "1px dashed rgba(255,255,255,0.2)"
            
        self.setStyleSheet(f"background-color: {bg}; border: {border}; border-radius: 10px; margin: 2px;")

        icon = "󰂱 " if self.device['connected'] else "󰂯 "
        name = self.device['name'] if self.device['name'] else "Unknown Device"
        name_label = QLabel(f"{icon}{name}")
        name_label.setStyleSheet("color: white; font-weight: bold; border: none; background: transparent;")
        
        if self.device['connected']:
            btn_text, btn_color = "Disconnect", "rgba(255, 50, 50, 0.3)"
        elif self.device['paired']:
            btn_text, btn_color = "Connect", "rgba(255, 255, 255, 0.1)"
        else:
            btn_text, btn_color = "Pair", "rgba(0, 255, 100, 0.2)"

        btn = QPushButton(btn_text)
        btn.setFixedWidth(85)
        btn.setStyleSheet(f"background-color: {btn_color}; border: none; font-size: 10px; padding: 5px; border-radius: 5px;")
        btn.clicked.connect(self.handle_action)

        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(btn)

    def handle_action(self):
        action = "pair" if not self.device['paired'] else ("disconnect" if self.device['connected'] else "connect")
        self.parent_gui.execute_bt_cmd(action, self.device['mac'])

class GlassBT(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.signals.finished.connect(self.populate_list)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('BT Manager Pro')
        self.setFixedSize(420, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.main_layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        self.title_label = QLabel(" Bluetooth Pro")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(close_btn)
        self.main_layout.addLayout(header)

        self.scan_btn = QPushButton("Refresh & Scan")
        self.scan_btn.clicked.connect(self.refresh_devices)
        self.main_layout.addWidget(self.scan_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.setStyleSheet("""
            QWidget { background-color: rgba(15, 15, 15, 0.9); border-radius: 20px; color: white; }
            QPushButton { background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; }
            QScrollArea { border: none; background: transparent; }
        """)
        self.refresh_devices()

    def refresh_devices(self):
        self.title_label.setText("🔄 Scanning...")
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def fetch_data(self):
        devs = {}
        try:
            # Pastikan Bluetooth ON
            subprocess.run(["bluetoothctl", "power", "on"], check=False)
            
            # Ambil paired devices
            paired_raw = subprocess.check_output(["bluetoothctl", "paired-devices"]).decode().splitlines()
            for line in paired_raw:
                p = line.split(' ', 2)
                if len(p) >= 3:
                    devs[p[1]] = {'mac': p[1], 'name': p[2], 'paired': True, 'connected': False}

            # Ambil all known devices
            all_raw = subprocess.check_output(["bluetoothctl", "devices"]).decode().splitlines()
            for line in all_raw:
                p = line.split(' ', 2)
                if len(p) >= 3 and p[1] not in devs:
                    devs[p[1]] = {'mac': p[1], 'name': p[2], 'paired': False, 'connected': False}

            # Update status connected
            for mac in devs:
                info = subprocess.check_output(["bluetoothctl", "info", mac]).decode()
                if "Connected: yes" in info:
                    devs[mac]['connected'] = True
            
            sorted_list = sorted(devs.values(), key=lambda x: (x['connected'], x['paired']), reverse=True)
            self.signals.finished.emit(sorted_list)
        except:
            self.signals.finished.emit([])

    def populate_list(self, devices):
        # Bersihkan layout dengan benar
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        for d in devices:
            self.list_layout.addWidget(BluetoothItem(d, self))
        self.title_label.setText(" Bluetooth Pro")

    def execute_bt_cmd(self, action, mac):
        subprocess.Popen(["bluetoothctl", action, mac])
        QTimer.singleShot(3000, self.refresh_devices)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassBT()
    ex.show()
    sys.exit(app.exec())