import sys
import os
import subprocess
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QScrollArea
from PyQt6.QtCore import Qt, QTimer

class GlassWifi(QWidget):
    def __init__(self):
        super().__init__()
        self.active_ssid = ""
        self.initUI()
        
        # Timer untuk auto-refresh setiap 10 detik
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.start_scan_thread)
        self.timer.start(10000)

    def initUI(self):
        self.setWindowTitle('Wifi Switcher Pro')
        self.setFixedSize(400, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout()
        
        # Header
        header = QHBoxLayout()
        self.status = QLabel("🌐 Network Manager")
        self.status.setStyleSheet("color: white; font-size: 16px; font-weight: bold; padding: 5px;")
        close = QPushButton("✕")
        close.setFixedSize(30, 30)
        close.setStyleSheet("background: rgba(255, 50, 50, 0.3); border-radius: 15px; color: white;")
        close.clicked.connect(self.close)
        header.addWidget(self.status)
        header.addStretch()
        header.addWidget(close)
        self.main_layout.addLayout(header)

        # Scroll Area untuk List
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.setStyleSheet("""
            QWidget { background-color: rgba(15, 15, 15, 0.7); border-radius: 20px; color: white; }
            QScrollArea { border: none; background: transparent; }
            #activeWifi { background-color: rgba(0, 255, 255, 0.15); border: 1px solid cyan; border-radius: 10px; }
            #normalWifi { background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; }
        """)

        self.setLayout(self.main_layout)
        self.start_scan_thread()

    def start_scan_thread(self):
        threading.Thread(target=self.get_data, daemon=True).start()

    def get_data(self):
        try:
            # Ambil SSID yang sedang aktif saat ini
            active = subprocess.check_output(["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"]).decode().splitlines()
            for line in active:
                if line.startswith("yes"):
                    self.active_ssid = line.split(":")[1]

            # Ambil semua list wifi
            cmd = ["nmcli", "-t", "-f", "SSID,BARS,SIGNAL", "dev", "wifi", "list"]
            output = subprocess.check_output(cmd).decode().splitlines()
            
            networks = []
            seen = set()
            for line in output:
                p = line.split(':')
                if len(p) >= 3 and p[0] and p[0] not in seen:
                    networks.append({"ssid": p[0], "bars": p[1], "sig": int(p[2])})
                    seen.add(p[0])
            
            QTimer.singleShot(0, lambda: self.render_list(networks))
        except: pass

    def render_list(self, networks):
        for i in reversed(range(self.list_layout.count())):
            w = self.list_layout.itemAt(i).widget()
            if w: w.setParent(None)

        for net in networks:
            is_active = net['ssid'] == self.active_ssid
            row_widget = QWidget()
            row_widget.setObjectName("activeWifi" if is_active else "normalWifi")
            
            row = QHBoxLayout(row_widget)
            color = "#00ff88" if net['sig'] > 70 else "#ffcc00" if net['sig'] > 40 else "#ff4444"
            
            prefix = "⭐ " if is_active else ""
            label = QLabel(f"<b>{prefix}{net['ssid']}</b><br><small style='color:{color}'>{net['sig']}% {net['bars']}</small>")
            
            btn_text = "Connected" if is_active else "Switch"
            btn = QPushButton(btn_text)
            btn.setFixedWidth(85)
            btn.setEnabled(not is_active) # Matikan tombol jika sudah tersambung
            btn.setStyleSheet(f"color: {color}; border: 1px solid {color}; padding: 5px; font-size: 10px;")
            btn.clicked.connect(lambda ch, s=net['ssid']: self.switch_wifi(s))

            row.addWidget(label)
            row.addStretch()
            row.addWidget(btn)
            self.list_layout.addWidget(row_widget)

    def switch_wifi(self, ssid):
        self.status.setText(f"🔄 Switching to {ssid}...")
        # Perintah pindah wifi
        os.system(f'alacritty -e nmcli device wifi connect "{ssid}" --ask &')
        # Beri jeda sedikit lalu refresh
        QTimer.singleShot(5000, self.start_scan_thread)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassWifi()
    ex.show()
    sys.exit(app.exec())