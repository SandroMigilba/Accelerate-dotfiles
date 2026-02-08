import sys
import subprocess
import threading
import time
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
        # Warna biru untuk Connected, Abu-abu untuk Paired, Putih Transparan untuk New
        if self.device['connected']:
            bg = "rgba(0, 150, 255, 0.2)"
            border = "1px solid #0096ff"
        elif self.device['paired']:
            bg = "rgba(255, 255, 255, 0.1)"
            border = "none"
        else:
            bg = "rgba(255, 255, 255, 0.05)"
            border = "1px dashed rgba(255,255,255,0.2)"
            
        self.setStyleSheet(f"background-color: {bg}; border: {border}; border-radius: 10px; margin: 2px;")

        icon = "󰂱 " if self.device['connected'] else "󰂯 "
        pair_status = " (New)" if not self.device['paired'] else ""
        name_label = QLabel(f"{icon}{self.device['name']}{pair_status}")
        name_label.setStyleSheet("color: white; font-weight: bold; border: none; background: transparent;")
        
        # Logika Tombol
        if self.device['connected']:
            btn_text, btn_color = "Disconnect", "rgba(255, 50, 50, 0.3)"
        elif self.device['paired']:
            btn_text, btn_color = "Connect", "rgba(255, 255, 255, 0.1)"
        else:
            btn_text, btn_color = "Pair", "rgba(0, 255, 100, 0.2)"

        self.btn_action = QPushButton(btn_text)
        self.btn_action.setFixedWidth(85)
        self.btn_action.setStyleSheet(f"background-color: {btn_color}; border: none; font-size: 10px; padding: 5px; border-radius: 5px; color: white;")
        self.btn_action.clicked.connect(self.handle_action)

        layout.addWidget(name_label)
        layout.addStretch()
        layout.addWidget(self.btn_action)

    def handle_action(self):
        if not self.device['paired']:
            self.parent_gui.execute_bt_cmd("pair", self.device['mac'])
        else:
            action = "disconnect" if self.device['connected'] else "connect"
            self.parent_gui.execute_bt_cmd(action, self.device['mac'])

class GlassBT(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.signals.finished.connect(self.populate_list)
        self.is_scanning = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle('BT Manager Pro')
        self.setFixedSize(420, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout(self)
        
        # Header
        header = QHBoxLayout()
        self.title_label = QLabel(" Bluetooth Pro")
        self.title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 5px;")
        
        self.btn_power = QPushButton("ON")
        self.btn_power.setFixedSize(50, 25)
        self.btn_power.setStyleSheet("background: #00ff88; color: black; font-weight: bold; border-radius: 12px;")
        self.btn_power.clicked.connect(self.toggle_power)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background: rgba(255, 50, 50, 0.3); border-radius: 15px; border: none; color: white;")
        close_btn.clicked.connect(self.close)
        
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.btn_power)
        header.addWidget(close_btn)
        self.main_layout.addLayout(header)

        # Refresh Button
        self.scan_btn = QPushButton("Scan New Devices")
        self.scan_btn.clicked.connect(self.start_discovery)
        self.scan_btn.setStyleSheet("background: rgba(255,255,255,0.1); padding: 10px; font-weight: bold; border: 1px solid rgba(255,255,255,0.1);")
        self.main_layout.addWidget(self.scan_btn)

        # List Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.setStyleSheet("QWidget { background-color: rgba(15, 15, 15, 0.9); border-radius: 20px; color: white; }")
        self.refresh_devices()

    def toggle_power(self):
        current = self.btn_power.text()
        new_state = "off" if current == "ON" else "on"
        subprocess.run(["bluetoothctl", "power", new_state])
        self.btn_power.setText("ON" if new_state == "on" else "OFF")
        self.btn_power.setStyleSheet(f"background: {'#00ff88' if new_state == 'on' else '#ff4444'}; color: black; font-weight: bold; border-radius: 12px;")
        QTimer.singleShot(1000, self.refresh_devices)

    def start_discovery(self):
        if not self.is_scanning:
            self.is_scanning = True
            self.scan_btn.setText("🔍 Scanning... (10s)")
            self.scan_btn.setEnabled(False)
            # Jalankan scan di latar belakang
            subprocess.Popen(["bluetoothctl", "scan", "on"])
            QTimer.singleShot(10000, self.stop_discovery)
            QTimer.singleShot(2000, self.refresh_devices)

    def stop_discovery(self):
        subprocess.Popen(["bluetoothctl", "scan", "off"])
        self.is_scanning = False
        self.scan_btn.setText("Scan New Devices")
        self.scan_btn.setEnabled(True)
        self.refresh_devices()

    def refresh_devices(self):
        threading.Thread(target=self.fetch_data_thread, daemon=True).start()

    def fetch_data_thread(self):
        devices_dict = {}
        try:
            # 1. Ambil paired devices
            paired = subprocess.check_output(["bluetoothctl", "paired-devices"]).decode().splitlines()
            for line in paired:
                parts = line.split(' ', 2)
                if len(parts) >= 3:
                    mac, name = parts[1], parts[2]
                    devices_dict[mac] = {'mac': mac, 'name': name, 'paired': True, 'connected': False}

            # 2. Ambil semua perangkat yang terdeteksi saat ini (hasil scan)
            all_devs = subprocess.check_output(["bluetoothctl", "devices"]).decode().splitlines()
            for line in all_devs:
                parts = line.split(' ', 2)
                if len(parts) >= 3:
                    mac, name = parts[1], parts[2]
                    if mac not in devices_dict:
                        devices_dict[mac] = {'mac': mac, 'name': name, 'paired': False, 'connected': False}

            # 3. Cek koneksi untuk tiap MAC
            for mac in devices_dict:
                info = subprocess.check_output(["bluetoothctl", "info", mac]).decode()
                devices_dict[mac]['connected'] = "Connected: yes" in info

            # Sorting: Connected > Paired > New
            sorted_devs = sorted(devices_dict.values(), key=lambda x: (x['connected'], x['paired']), reverse=True)
            self.signals.finished.emit(sorted_devs)
        except:
            self.signals.finished.emit([])

    def populate_list(self, devices):
        for i in reversed(range(self.list_layout.count())):
            if self.list_layout.itemAt(i).widget(): self.list_layout.itemAt(i).widget().setParent(None)
        for dev in devices:
            self.list_layout.addWidget(BluetoothItem(dev, self))

    def execute_bt_cmd(self, action, mac):
        self.title_label.setText(f"🔄 {action.capitalize()}ing...")
        subprocess.Popen(["bluetoothctl", action, mac])
        QTimer.singleShot(4000, self.refresh_devices)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassBT()
    ex.show()
    sys.exit(app.exec())