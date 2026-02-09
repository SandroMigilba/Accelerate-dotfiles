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
        self.mac = device['mac']
        self.parent_gui = parent_gui
        self.init_item(device)

    def init_item(self, device):
        layout = QHBoxLayout(self)
        # Warna biru terang jika aktif
        bg = "rgba(0, 150, 255, 0.2)" if device['connected'] else "rgba(255, 255, 255, 0.05)"
        border = "1px solid #00f2ff" if device['connected'] else "1px solid rgba(255,255,255,0.1)"
        self.setStyleSheet(f"background-color: {bg}; border: {border}; border-radius: 12px; margin: 2px;")

        # Tampilkan nama perangkat (potong jika terlalu panjang)
        name = device['name'] if device['name'] else "Unknown Device"
        self.label = QLabel(name)
        self.label.setStyleSheet("color: white; font-weight: bold; border: none; background: transparent;")
        
        btn_text = "Disconnect" if device['connected'] else "Connect"
        btn_style = "background: #ff5555;" if device['connected'] else "background: #0096ff;"
        
        self.btn = QPushButton(btn_text)
        self.btn.setFixedWidth(85)
        self.btn.setStyleSheet(f"{btn_style} border: none; font-size: 10px; padding: 6px; border-radius: 6px; font-weight: bold; color: white;")
        self.btn.clicked.connect(self.main_action)

        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.btn)

    def main_action(self):
        self.parent_gui.loading_timer.start(100)
        action = "disconnect" if "Disconnect" in self.btn.text() else "connect"
        self.parent_gui.execute_bt_cmd(action, self.mac)

class GlassBT(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.signals.finished.connect(self.populate_list)
        
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.animate_loading)
        self.frames = ["|", "/", "-", "\\"]
        self.frame_idx = 0
        
        self.initUI()
        
        # Auto-refresh setiap 20 detik agar tidak membebani scan
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_devices)
        self.refresh_timer.start(20000)

    def initUI(self):
        self.setFixedSize(400, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.main_layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        self.icon_label = QLabel("BT")
        self.icon_label.setFixedWidth(25)
        self.icon_label.setStyleSheet("color: #00f2ff; font-weight: bold; background: transparent; font-size: 14px;")
        
        self.title_label = QLabel("Bluetooth Manager")
        self.title_label.setStyleSheet("color: white; font-weight: bold; background: transparent;")
        
        self.reload_btn = QPushButton("↻")
        self.reload_btn.setFixedSize(30, 30)
        self.reload_btn.setStyleSheet("""
            QPushButton { background: rgba(255,255,255,0.1); border-radius: 15px; color: white; border: none; font-size: 16px; }
            QPushButton:hover { background: rgba(255,255,255,0.2); }
        """)
        self.reload_btn.clicked.connect(self.refresh_devices)

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background: rgba(255, 50, 50, 0.4); border-radius: 15px; border: none; color: white;")
        close_btn.clicked.connect(self.close)
        
        header.addWidget(self.icon_label)
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(self.reload_btn)
        header.addWidget(close_btn)
        self.main_layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.setStyleSheet("QWidget { background-color: rgba(15, 15, 15, 0.95); border-radius: 20px; color: white; }")
        
        self.refresh_devices()

    def animate_loading(self):
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        self.icon_label.setText(self.frames[self.frame_idx])
        self.reload_btn.setText(self.frames[self.frame_idx])

    def refresh_devices(self):
        if not self.loading_timer.isActive():
            self.loading_timer.start(100)
        self.reload_btn.setEnabled(False)
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def fetch_data(self):
        devs = {}
        try:
            # Pastikan bluetooth tidak terblokir
            subprocess.run(["rfkill", "unblock", "bluetooth"], stdout=subprocess.DEVNULL)
            # Nyalakan power
            subprocess.run(["bluetoothctl", "power", "on"], stdout=subprocess.DEVNULL)
            # Scan singkat untuk memperbarui cache perangkat di sekitar
            scan_proc = subprocess.Popen(["bluetoothctl", "scan", "on"], stdout=subprocess.DEVNULL)
            time.sleep(1.5) # Beri waktu sejenak untuk menemukan perangkat
            subprocess.run(["bluetoothctl", "scan", "off"], stdout=subprocess.DEVNULL)

            # Ambil semua device
            raw = subprocess.check_output(["bluetoothctl", "devices"]).decode().splitlines()
            for line in raw:
                p = line.split(' ', 2)
                if len(p) >= 3:
                    mac = p[1]
                    name = p[2]
                    devs[mac] = {'mac': mac, 'name': name, 'connected': False}

            # Ambil device yang terkoneksi
            conn_raw = subprocess.check_output(["bluetoothctl", "devices", "Connected"]).decode().splitlines()
            for line in conn_raw:
                p = line.split(' ', 2)
                if len(p) >= 2 and p[1] in devs:
                    devs[p[1]]['connected'] = True

            sorted_list = sorted(devs.values(), key=lambda x: (x['connected'], x['name']), reverse=True)
            self.signals.finished.emit(sorted_list)
        except Exception as e:
            print(f"BT Error: {e}")
            self.signals.finished.emit([])

    def populate_list(self, devices):
        self.loading_timer.stop()
        self.icon_label.setText("BT")
        self.reload_btn.setText("↻")
        self.reload_btn.setEnabled(True)
        
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        if not devices:
            no_dev = QLabel("No devices found")
            no_dev.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_dev.setStyleSheet("color: gray; margin-top: 20px;")
            self.list_layout.addWidget(no_dev)
        else:
            for d in devices:
                self.list_layout.addWidget(BluetoothItem(d, self))

    def execute_bt_cmd(self, action, mac):
        # Jalankan perintah connect/disconnect
        subprocess.Popen(["bluetoothctl", action, mac], stdout=subprocess.DEVNULL)
        # Tunggu agak lama baru refresh agar status di sistem sudah update
        QTimer.singleShot(4000, self.refresh_devices)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassBT()
    ex.show()
    sys.exit(app.exec())
