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
        self.mac = device['mac']
        self.parent_gui = parent_gui
        self.init_item(device)

    def init_item(self, device):
        layout = QHBoxLayout(self)
        # Warna biru terang jika aktif
        bg = "rgba(0, 150, 255, 0.3)" if device['connected'] else "rgba(255, 255, 255, 0.05)"
        border = "1px solid #00f2ff" if device['connected'] else "1px solid rgba(255,255,255,0.1)"
        self.setStyleSheet(f"background-color: {bg}; border: {border}; border-radius: 12px; margin: 2px;")

        # Gunakan ikon teks biasa jika Nerd Fonts bermasalah
        icon = "● " if device['connected'] else "○ "
        self.label = QLabel(f"{icon}{device['name']}")
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
        action = "disconnect" if "Disconnect" in self.btn.text() else "connect"
        self.parent_gui.execute_bt_cmd(action, self.mac)

class GlassBT(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.signals.finished.connect(self.populate_list)
        self.initUI()
        
        # Auto-refresh 10 detik
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_devices)
        self.refresh_timer.start(10000)

    def initUI(self):
        self.setWindowTitle('BT Manager')
        self.setFixedSize(400, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.main_layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        # Ikon status sederhana (Bakal ganti-ganti pas loading)
        self.icon_label = QLabel("BT")
        self.icon_label.setStyleSheet("color: #00f2ff; font-weight: bold; background: transparent; font-size: 14px;")
        
        self.title_label = QLabel("Manager")
        self.title_label.setStyleSheet("color: white; font-weight: bold; background: transparent;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background: rgba(255, 50, 50, 0.4); border-radius: 15px; border: none; color: white;")
        close_btn.clicked.connect(self.close)
        
        header.addWidget(self.icon_label)
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(close_btn)
        self.main_layout.addLayout(header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.setStyleSheet("QWidget { background-color: rgba(15, 15, 15, 0.95); border-radius: 20px; color: white; }")
        
        # Animasi Loading Sederhana
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.animate_loading)
        self.frames = ["|", "/", "-", "\\"]
        self.frame_idx = 0

        self.refresh_devices()

    def animate_loading(self):
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        self.icon_label.setText(self.frames[self.frame_idx])

    def refresh_devices(self):
        self.loading_timer.start(100)
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def fetch_data(self):
        devs = {}
        try:
            # Ambil semua device yang terdaftar
            raw = subprocess.check_output(["bluetoothctl", "devices"]).decode().splitlines()
            for line in raw:
                p = line.split(' ', 2)
                if len(p) >= 3:
                    devs[p[1]] = {'mac': p[1], 'name': p[2], 'connected': False}

            # Ambil yang beneran Connected (Sangat Akurat)
            conn_raw = subprocess.check_output(["bluetoothctl", "devices", "Connected"]).decode().splitlines()
            for line in conn_raw:
                p = line.split(' ', 2)
                if len(p) >= 2 and p[1] in devs:
                    devs[p[1]]['connected'] = True

            sorted_list = sorted(devs.values(), key=lambda x: x['connected'], reverse=True)
            self.signals.finished.emit(sorted_list)
        except:
            self.signals.finished.emit([])

    def populate_list(self, devices):
        self.loading_timer.stop()
        self.icon_label.setText("BT")
        
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for d in devices:
            self.list_layout.addWidget(BluetoothItem(d, self))

    def execute_bt_cmd(self, action, mac):
        self.loading_timer.start(100)
        # Gunakan subprocess.run agar lebih pasti sampai ke bluetoothd
        subprocess.Popen(["bluetoothctl", action, mac], stdout=subprocess.DEVNULL)
        QTimer.singleShot(3000, self.refresh_devices)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassBT()
    ex.show()
    sys.exit(app.exec())