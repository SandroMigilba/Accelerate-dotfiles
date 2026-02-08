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
        self.mac = device['mac']
        self.parent_gui = parent_gui
        self.init_item(device)

    def init_item(self, device):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Background warna berdasarkan status
        bg = "rgba(0, 150, 255, 0.25)" if device['connected'] else "rgba(255, 255, 255, 0.05)"
        border = "1px solid #0096ff" if device['connected'] else "1px solid rgba(255,255,255,0.1)"
        self.setStyleSheet(f"background-color: {bg}; border: {border}; border-radius: 12px; margin: 2px;")

        icon = "󰂱 " if device['connected'] else "󰂯 "
        self.label = QLabel(f"{icon}{device['name']}")
        self.label.setStyleSheet("color: white; font-weight: bold; border: none; background: transparent;")
        
        # Tombol Aksi
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
        # Tombol connect/disconnect sederhana
        action = "disconnect" if "Disconnect" in self.btn.text() else "connect"
        self.parent_gui.execute_bt_cmd(action, self.mac)

class GlassBT(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.signals.finished.connect(self.populate_list)
        self.initUI()
        
        # Timer Auto-Refresh setiap 10 detik (Ringan)
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
        self.title_label = QLabel(" Bluetooth")
        self.title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background: rgba(255, 50, 50, 0.2); border-radius: 15px; border: none; color: white;")
        close_btn.clicked.connect(self.close)
        
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
        self.refresh_devices()

    def refresh_devices(self):
        # Jalankan di background agar tidak lag
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def fetch_data(self):
        devs = {}
        try:
            # 1. Ambil list semua devices yang tersimpan/terdeteksi
            # Menggunakan 'devices' dan 'paired-devices' untuk memastikan tidak ada yang hilang
            for cmd in ["paired-devices", "devices"]:
                out = subprocess.check_output(["bluetoothctl", cmd]).decode().splitlines()
                for line in out:
                    p = line.split(' ', 2)
                    if len(p) >= 3:
                        devs[p[1]] = {'mac': p[1], 'name': p[2], 'connected': False}

            # 2. Ambil yang sedang Connected (Metode paling ringan)
            conn_out = subprocess.check_output(["bluetoothctl", "devices", "Connected"]).decode().splitlines()
            for line in conn_out:
                p = line.split(' ', 2)
                if len(p) >= 2 and p[1] in devs:
                    devs[p[1]]['connected'] = True

            # Sort: Perangkat aktif selalu di paling atas
            sorted_list = sorted(devs.values(), key=lambda x: x['connected'], reverse=True)
            self.signals.finished.emit(sorted_list)
        except:
            self.signals.finished.emit([])

    def populate_list(self, devices):
        # Bersihkan list lama secara efisien
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Tambahkan item ke daftar
        for d in devices:
            self.list_layout.addWidget(BluetoothItem(d, self))

    def execute_bt_cmd(self, action, mac):
        # Eksekusi instan & refresh cepat
        subprocess.Popen(["bluetoothctl", action, mac], stdout=subprocess.DEVNULL)
        QTimer.singleShot(2000, self.refresh_devices)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassBT()
    ex.show()
    sys.exit(app.exec())