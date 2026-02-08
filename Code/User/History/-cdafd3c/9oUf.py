import sys
import subprocess
import threading
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QHBoxLayout, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QPropertyAnimation, QRect

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
        bg = "rgba(0, 150, 255, 0.25)" if device['connected'] else "rgba(255, 255, 255, 0.05)"
        border = "1px solid #0096ff" if device['connected'] else "1px solid rgba(255,255,255,0.1)"
        self.setStyleSheet(f"background-color: {bg}; border: {border}; border-radius: 12px; margin: 2px;")

        icon = "󰂱 " if device['connected'] else "󰂯 "
        self.label = QLabel(f"{icon}{device['name']}")
        self.label.setStyleSheet("color: white; font-weight: bold; border: none; background: transparent;")
        
        btn_text = "Disconnect" if device['connected'] else "Connect"
        btn_style = "background: rgba(255, 50, 50, 0.4);" if device['connected'] else "background: rgba(0, 150, 255, 0.4);"
        
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
        
        # Timer Auto-Refresh 10s
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_devices)
        self.refresh_timer.start(10000)

    def initUI(self):
        self.setWindowTitle('BT Pro')
        self.setFixedSize(400, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.main_layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        # Label Ikon yang akan berputar
        self.icon_label = QLabel("󰂯")
        self.icon_label.setStyleSheet("color: #0096ff; font-size: 20px; font-weight: bold; background: transparent;")
        
        self.title_label = QLabel("Bluetooth Manager")
        self.title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background: rgba(255, 50, 50, 0.2); border-radius: 15px; border: none; color: white;")
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

        self.setStyleSheet("QWidget { background-color: rgba(15, 15, 15, 0.9); border-radius: 20px; color: white; }")
        
        # Inisialisasi animasi putar (rotasi teks tidak didukung langsung, jadi kita pakai efek transisi teks)
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.animate_icon)
        self.frame_idx = 0
        self.frames = ["󰂯", "󱐋", "󰂰", "󱐌"] # Variasi ikon loading

        self.refresh_devices()

    def animate_icon(self):
        # Mengganti-ganti ikon dengan cepat untuk efek animasi loading
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        self.icon_label.setText(self.frames[self.frame_idx])

    def refresh_devices(self):
        self.loading_timer.start(100) # Mulai animasi (100ms per frame)
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def fetch_data(self):
        devs = {}
        try:
            for cmd in ["paired-devices", "devices"]:
                out = subprocess.check_output(["bluetoothctl", cmd]).decode().splitlines()
                for line in out:
                    p = line.split(' ', 2)
                    if len(p) >= 3:
                        devs[p[1]] = {'mac': p[1], 'name': p[2], 'connected': False}

            conn_out = subprocess.check_output(["bluetoothctl", "devices", "Connected"]).decode().splitlines()
            for line in conn_out:
                p = line.split(' ', 2)
                if len(p) >= 2 and p[1] in devs:
                    devs[p[1]]['connected'] = True

            sorted_list = sorted(devs.values(), key=lambda x: x['connected'], reverse=True)
            self.signals.finished.emit(sorted_list)
        except:
            self.signals.finished.emit([])

    def populate_list(self, devices):
        self.loading_timer.stop() # Berhenti animasi
        self.icon_label.setText("󰂯") # Kembalikan ke ikon semula
        
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        for d in devices:
            self.list_layout.addWidget(BluetoothItem(d, self))

    def execute_bt_cmd(self, action, mac):
        self.loading_timer.start(100)
        subprocess.Popen(["bluetoothctl", action, mac], stdout=subprocess.DEVNULL)
        QTimer.singleShot(2000, self.refresh_devices)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassBT()
    ex.show()
    sys.exit(app.exec())