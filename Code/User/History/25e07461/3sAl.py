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

    def initUI(self):
        self.setWindowTitle('Wifi Manager Glass Pro')
        self.setFixedSize(400, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout()
        
        # Header Row
        header_row = QHBoxLayout()
        self.status_label = QLabel("📡 Wi-Fi Scanner")
        self.status_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding: 10px;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(35, 35)
        close_btn.setStyleSheet("""
            QPushButton { background-color: rgba(255, 80, 80, 0.3); border-radius: 17px; color: white; border: none; }
            QPushButton:hover { background-color: rgba(255, 50, 50, 0.7); }
        """)
        close_btn.clicked.connect(self.close)
        
        header_row.addWidget(self.status_label)
        header_row.addStretch()
        header_row.addWidget(close_btn)
        self.main_layout.addLayout(header_row)

        # Refresh Button dengan Animasi Style
        self.scan_btn = QPushButton("Refresh Networks")
        self.scan_btn.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(0, 201, 255, 0.4), stop:1 rgba(146, 254, 157, 0.4));
                border: 1px solid rgba(255,255,255,0.2);
                font-weight: bold;
                padding: 12px;
                margin-bottom: 10px;
            }
            QPushButton:pressed { background-color: rgba(255, 255, 255, 0.2); }
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
            QWidget { background-color: rgba(15, 15, 15, 0.5); border-radius: 20px; color: white; font-family: 'Segoe UI', sans-serif; }
            QScrollArea { border: none; background: transparent; }
            #wifiRow { background-color: rgba(255, 255, 255, 0.05); border-radius: 10px; margin: 2px; }
            #wifiRow:hover { background-color: rgba(255, 255, 255, 0.12); }
        """)

        self.setLayout(self.main_layout)
        self.start_scan_thread()

    def start_scan_thread(self):
        """Menjalankan scan di thread terpisah agar GUI tidak beku/freeze"""
        self.status_label.setText("🔄 Scanning...")
        self.scan_btn.setEnabled(False)
        threading.Thread(target=self.refresh_list, daemon=True).start()

    def get_wifi_data(self):
        try:
            cmd = ["nmcli", "-t", "-f", "SSID,BARS,SIGNAL", "device", "wifi", "list"]
            output = subprocess.check_output(cmd).decode().splitlines()
            
            wifi_list = []
            seen_ssids = set()
            for line in output:
                parts = line.split(':')
                if len(parts) >= 3 and parts[0] and parts[0] not in seen_ssids:
                    wifi_list.append({
                        "ssid": parts[0],
                        "bars": parts[1].strip(),
                        "signal": int(parts[2])
                    })
                    seen_ssids.add(parts[0])
            return sorted(wifi_list, key=lambda x: x['signal'], reverse=True)
        except: return []

    def refresh_list(self):
        networks = self.get_wifi_data()
        
        # Menggunakan QTimer untuk update UI dari thread berbeda (Thread Safety)
        QTimer.singleShot(0, lambda: self.update_ui(networks))

    def update_ui(self, networks):
        # Bersihkan list lama
        for i in reversed(range(self.list_layout.count())): 
            widget = self.list_layout.itemAt(i).widget()
            if widget: widget.setParent(None)

        for net in networks:
            row_widget = QWidget()
            row_widget.setObjectName("wifiRow")
            row = QHBoxLayout(row_widget)
            
            # Logika Warna Sinyal
            if net['signal'] > 75: color = "#00ff88"   # Cyber Green
            elif net['signal'] > 50: color = "#ffff00" # Neon Yellow
            else: color = "#ff4444"                   # Soft Red

            # Label Nama & Sinyal
            info_label = QLabel(f"{net['ssid']}\n<span style='color:{color}; font-size:10px;'>{net['bars']} {net['signal']}%</span>")
            info_label.setStyleSheet("background: transparent; border: none;")
            
            btn_conn = QPushButton("Connect")
            btn_conn.setFixedWidth(80)
            btn_conn.setStyleSheet(f"color: {color}; border: 1px solid {color}; background: transparent;")
            btn_conn.clicked.connect(lambda ch, n=net['ssid']: self.connect_wifi(n))
            
            btn_del = QPushButton("🗑")
            btn_del.setFixedWidth(40)
            btn_del.setStyleSheet("background-color: rgba(255, 50, 50, 0.1); border: none;")
            btn_del.clicked.connect(lambda ch, n=net['ssid']: self.delete_wifi(n))

            row.addWidget(info_label)
            row.addStretch()
            row.addWidget(btn_conn)
            row.addWidget(btn_del)
            
            self.list_layout.addWidget(row_widget)

        self.status_label.setText("📡 Wi-Fi Scanner")
        self.scan_btn.setEnabled(True)

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