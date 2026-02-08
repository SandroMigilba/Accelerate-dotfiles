import sys
import subprocess
import threading
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QHBoxLayout, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QTimer

class BluetoothItem(QFrame):
    def __init__(self, device, parent_gui):
        super().__init__()
        self.device = device # Format: {'mac': '...', 'name': '...', 'connected': bool}
        self.parent_gui = parent_gui
        self.init_item()

    def init_item(self):
        layout = QHBoxLayout(self)
        bg_color = "rgba(0, 150, 255, 0.15)" if self.device['connected'] else "rgba(255, 255, 255, 0.05)"
        self.setStyleSheet(f"background-color: {bg_color}; border-radius: 10px; margin: 2px;")

        name_label = QLabel(f"{'󰂱 ' if self.device['connected'] else '󰂯 '}{self.device['name']}")
        name_label.setStyleSheet("color: white; font-weight: bold; background: transparent;")
        
        btn_text = "Disconnect" if self.device['connected'] else "Connect"
        self.btn_action = QPushButton(btn_text)
        self.btn_action.setFixedWidth(85)
        self.btn_action.setStyleSheet("background-color: rgba(255,255,255,0.1); border: none; font-size: 10px; padding: 5px;")
        self.btn_action.clicked.connect(self.handle_action)

        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(self.btn_action)

    def handle_action(self):
        action = "disconnect" if self.device['connected'] else "connect"
        self.parent_gui.execute_bt_cmd(action, self.device['mac'])

class GlassBT(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('BT Manager')
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        title = QLabel(" Bluetooth Manager")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 10px;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        # Scan Button
        self.scan_btn = QPushButton("Refresh Devices")
        self.scan_btn.clicked.connect(self.refresh_devices)
        self.scan_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 120, 255, 0.5), stop:1 rgba(0, 255, 255, 0.5)); padding: 10px; font-weight: bold;")
        layout.addWidget(self.scan_btn)

        # List Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

        self.setStyleSheet("""
            QWidget { background-color: rgba(15, 15, 15, 0.85); border-radius: 15px; color: white; }
            QPushButton { border-radius: 8px; }
            QScrollArea { border: none; background: transparent; }
        """)

        self.refresh_devices()

    def get_devices(self):
        devices = []
        try:
            # Mengambil list paired devices
            out = subprocess.check_output(["bluetoothctl", "devices"]).decode().splitlines()
            # Mengambil list connected devices
            conn_out = subprocess.check_output(["bluetoothctl", "info"]).decode()
            
            for line in out:
                parts = line.split(' ', 2)
                if len(parts) == 3:
                    mac, name = parts[1], parts[2]
                    is_connected = mac in conn_out
                    devices.append({'mac': mac, 'name': name, 'connected': is_connected})
        except: pass
        return devices

    def refresh_devices(self):
        for i in reversed(range(self.list_layout.count())): 
            self.list_layout.itemAt(i).widget().setParent(None)
        
        for dev in self.get_devices():
            self.list_layout.addWidget(BluetoothItem(dev, self))

    def execute_bt_cmd(self, action, mac):
        subprocess.Popen(["bluetoothctl", action, mac])
        QTimer.singleShot(3000, self.refresh_devices)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassBT()
    ex.show()
    sys.exit(app.exec())