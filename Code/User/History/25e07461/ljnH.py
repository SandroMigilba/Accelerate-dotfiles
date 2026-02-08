import sys
import os
import subprocess
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QScrollArea
from PyQt6.QtCore import Qt, QTimer

class GlassWifi(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # Pengaturan Auto-Refresh (Setiap 10000 ms = 10 detik)
        self.auto_refresh_timer = QTimer(self)
        self.auto_refresh_timer.timeout.connect(self.start_scan_thread)
        self.auto_refresh_timer.start(10000)

    def initUI(self):
        self.setWindowTitle('Wifi Manager Auto-Sync')
        self.setFixedSize(400, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout()
        
        # Header
        header_row = QHBoxLayout()
        self.status_label = QLabel("📡 Wi-Fi Scanner")
        self.status_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding: 10px;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton { background-color: rgba(255, 80, 80, 0.2); border-radius: 15px; color: white; border: none; }
            QPushButton:hover { background-color: rgba(255, 50, 50, 0.6); }
        """)
        close_btn.clicked.connect(self.close)
        
        header_row.addWidget(self.status_label)
        header_row.addStretch()
        header_row.addWidget(close_btn)
        self.main_layout.addLayout(header_row)

        # Refresh Button (Manual)
        self.scan_btn = QPushButton("Manual Refresh")
        self.scan_btn.setStyleSheet("""
            QPushButton { 
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255,255,255,0.1);
                font-weight: bold;
                padding: 10px;
                margin-bottom: 5px;
            }
            QPushButton:hover { background: rgba(255, 255, 255, 0.15); }
        """)
        self.scan_btn.clicked.connect(self.start_scan_thread)
        self.main_layout.addWidget(self.scan_btn)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        # Main Style
        self.setStyleSheet("""
            QWidget { background-color: rgba(10, 10, 10, 0.6); border-radius: 15px; color: white; font-family: 'Inter', sans-serif; }
            QScrollArea { border: none; background: transparent; }
            #wifiRow { background-color: rgba(255, 255, 255, 0.03); border-radius: 10px; padding: 5px; }
            #wifiRow:hover { background-color: rgba(255, 255, 255, 0.08); }
        """)

        self.setLayout(self.main_layout)
        self.start_scan_thread()

    def start_scan_thread(self):
        self.status_label.setText("🔄 Updating...")
        threading.Thread(target=self.run_nmcli_scan, daemon=True).start()

    def run_nmcli_scan(self):
        try:
            # Mengambil data wifi
            cmd = ["nmcli", "-t", "-f", "SSID,BARS,SIGNAL", "device", "wifi", "list"]
            output = subprocess.check_output(cmd).decode().splitlines()
            
            networks = []
            seen = set()
            for line in output:
                p = line.split(':')
                if len(p) >= 3 and p[0] and p[0] not in seen:
                    networks.append({"ssid": p[0], "bars": p[1], "signal": int(p[2])})
                    seen.add(p[0])
            
            networks = sorted(networks, key=lambda x: x['signal'], reverse=True)
            QTimer.singleShot(0, lambda: self.update_ui(networks))
        except:
            pass

    def update_ui(self, networks):
        # Hapus list lama hanya jika jumlah data berubah atau ada perubahan nama
        # Untuk kesederhanaan, kita bersihkan dan gambar ulang
        for i in reversed(range(self.list_layout.count())): 
            w = self.list_layout.itemAt(i).widget()
            if w: w.setParent(None)

        for net in networks:
            row_widget = QWidget()
            row_widget.setObjectName("wifiRow")
            row = QHBoxLayout(row_widget)
            
            # Warna Sinyal
            color = "#00ff88" if net['signal'] > 75 else "#ffff00" if net['signal'] > 50 else "#ff4444"

            info = QLabel(f"<b>{net['ssid']}</b><br><small style='color:{color}'>{net['bars']} {net['signal']}%</small>")
            
            btn_conn = QPushButton("Connect")
            btn_conn.setFixedWidth(70)
            btn_conn.setStyleSheet(f"color: {color}; border: 1px solid {color}; font-size: 10px;")
            btn_conn.clicked.connect(lambda ch, n=net['ssid']: self.connect_wifi(n))
            
            btn_del = QPushButton("🗑")
            btn_del.setFixedWidth(35)
            btn_del.setStyleSheet("background: rgba(255, 50, 50, 0.1); border: none;")
            btn_del.clicked.connect(lambda ch, n=net['ssid']: self.delete_wifi(n))

            row.addWidget(info)
            row.addStretch()
            row.addWidget(btn_conn)
            row.addWidget(btn_del)
            self.list_layout.addWidget(row_widget)

        self.status_label.setText("📡 Wi-Fi Scanner")

    def connect_wifi(self, name):
        os.system(f'alacritty -e nmcli device wifi connect "{name}" --ask &')

    def delete_wifi(self, name):
        subprocess.run(["nmcli", "connection", "delete", name])
        self.start_scan_thread()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassWifi()
    ex.show()
    sys.exit(app.exec())