import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QHBoxLayout, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QTimer

class BluetoothItem(QFrame):
    def __init__(self, device, parent_gui):
        super().__init__()
        self.device = device
        self.parent_gui = parent_gui
        self.init_item()

    def init_item(self):
        layout = QHBoxLayout(self)
        # Warna biru transparan untuk perangkat yang tersambung
        bg_color = "rgba(0, 150, 255, 0.2)" if self.device['connected'] else "rgba(255, 255, 255, 0.05)"
        border = "1px solid #0096ff" if self.device['connected'] else "none"
        self.setStyleSheet(f"background-color: {bg_color}; border: {border}; border-radius: 10px; margin: 2px;")

        icon = "󰂱 " if self.device['connected'] else "󰂯 "
        name_label = QLabel(f"{icon}{self.device['name']}")
        name_label.setStyleSheet("color: white; font-weight: bold; border: none; background: transparent;")
        
        btn_text = "Disconnect" if self.device['connected'] else "Connect"
        self.btn_action = QPushButton(btn_text)
        self.btn_action.setFixedWidth(85)
        # Style tombol dinamis
        btn_style = "background-color: rgba(255, 50, 50, 0.3);" if self.device['connected'] else "background-color: rgba(255, 255, 255, 0.1);"
        self.btn_action.setStyleSheet(f"{btn_style} border: none; font-size: 10px; padding: 5px; border-radius: 5px; color: white;")
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
        
        header = QHBoxLayout()
        title = QLabel(" Bluetooth Manager")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 10px;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background: rgba(255, 50, 50, 0.3); border-radius: 15px; border: none; color: white;")
        close_btn.clicked.connect(self.close)
        header.addWidget(title)
        header.addStretch()
        header.addWidget(close_btn)
        layout.addLayout(header)

        self.scan_btn = QPushButton("Refresh Devices")
        self.scan_btn.clicked.connect(self.refresh_devices)
        self.scan_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 120, 255, 0.5), stop:1 rgba(0, 255, 255, 0.5));
                padding: 10px; font-weight: bold; border: none;
            }
            QPushButton:hover { background: rgba(0, 255, 255, 0.6); }
        """)
        layout.addWidget(self.scan_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

        self.setStyleSheet("QWidget { background-color: rgba(15, 15, 15, 0.85); border-radius: 15px; color: white; }")
        self.refresh_devices()

    def get_devices(self):
        devices = []
        try:
            # Ambil semua perangkat yang sudah di-pair
            raw_devices = subprocess.check_output(["bluetoothctl", "paired-devices"]).decode().splitlines()
            
            for line in raw_devices:
                parts = line.split(' ', 2)
                if len(parts) >= 3:
                    mac = parts[1]
                    name = parts[2]
                    
                    # Cek status koneksi secara spesifik untuk tiap MAC
                    info = subprocess.check_output(["bluetoothctl", "info", mac]).decode()
                    is_connected = "Connected: yes" in info
                    
                    devices.append({'mac': mac, 'name': name, 'connected': is_connected})
            
            # Urutkan: Connected di paling atas
            return sorted(devices, key=lambda x: x['connected'], reverse=True)
        except Exception as e:
            print(f"Error: {e}")
            return []

    def refresh_devices(self):
        # Bersihkan list
        for i in reversed(range(self.list_layout.count())): 
            widget = self.list_layout.itemAt(i).widget()
            if widget: widget.setParent(None)
        
        # Render ulang
        for dev in self.get_devices():
            self.list_layout.addWidget(BluetoothItem(dev, self))

    def execute_bt_cmd(self, action, mac):
        # Gunakan subprocess.run agar kita bisa menunggu proses selesai sebelum refresh
        subprocess.Popen(["bluetoothctl", action, mac])
        # Beri jeda 2 detik agar hardware sempat merespon sebelum UI di-refresh
        QTimer.singleShot(2000, self.refresh_list_after_action)

    def refresh_list_after_action(self):
        self.refresh_devices()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassBT()
    ex.show()
    sys.exit(app.exec())