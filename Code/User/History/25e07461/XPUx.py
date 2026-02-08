import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QScrollArea
from PyQt6.QtCore import Qt

class GlassWifi(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Wifi Manager Colorized')
        self.setFixedSize(400, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout()
        
        # Header transparan
        header_row = QHBoxLayout()
        header = QLabel("📡 Wi-Fi Scanner")
        header.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding: 10px;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(35, 35)
        close_btn.setStyleSheet("""
            QPushButton { background-color: rgba(255, 80, 80, 0.4); border-radius: 17px; color: white; }
            QPushButton:hover { background-color: rgba(255, 50, 50, 0.8); }
        """)
        close_btn.clicked.connect(self.close)
        
        header_row.addWidget(header)
        header_row.addStretch()
        header_row.addWidget(close_btn)
        self.main_layout.addLayout(header_row)

        # Tombol Scan dengan gradient
        self.scan_btn = QPushButton("Refresh Networks")
        self.scan_btn.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(72, 198, 239, 0.5), stop:1 rgba(111, 134, 214, 0.5));
                border: 1px solid rgba(255,255,255,0.2);
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        self.scan_btn.clicked.connect(self.refresh_list)
        self.main_layout.addWidget(self.scan_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.setStyleSheet("""
            QWidget { background-color: rgba(20, 20, 20, 0.4); border-radius: 20px; color: white; }
            QPushButton { background-color: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.15); padding: 10px; border-radius: 10px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.25); }
            QScrollArea { border: none; background: transparent; }
        """)

        self.setLayout(self.main_layout)
        self.refresh_list()

    def get_wifi_data(self):
        """Mendeteksi SSID dan Signal Strength"""
        try:
            # Mengambil SSID dan Bar (Signal)
            cmd = ["nmcli", "-t", "-f", "SSID,BARS,SIGNAL", "device", "wifi", "list"]
            output = subprocess.check_output(cmd).decode().splitlines()
            
            wifi_list = []
            seen_ssids = set()
            for line in output:
                parts = line.split(':')
                if len(parts) >= 3 and parts[0] and parts[0] not in seen_ssids:
                    wifi_list.append({
                        "ssid": parts[0],
                        "bars": parts[1],
                        "signal": int(parts[2])
                    })
                    seen_ssids.add(parts[0])
            return sorted(wifi_list, key=lambda x: x['signal'], reverse=True)
        except Exception as e:
            print(f"Error scan: {e}")
            return []

    def refresh_list(self):
        # Hapus list lama
        for i in reversed(range(self.list_layout.count())): 
            widget = self.list_layout.itemAt(i).widget()
            if widget: widget.setParent(None)

        networks = self.get_wifi_data()
        for net in networks:
            row = QHBoxLayout()
            
            # Tentukan warna berdasarkan sinyal
            if net['signal'] > 75: color = "#50fa7b" # Hijau
            elif net['signal'] > 50: color = "#f1fa8c" # Kuning
            else: color = "#ff5555" # Merah

            btn_text = f"{net['ssid']} ({net['signal']}%) {net['bars']}"
            btn_conn = QPushButton(btn_text)
            btn_conn.setStyleSheet(f"text-align: left; color: {color};")
            btn_conn.clicked.connect(lambda ch, n=net['ssid']: self.connect_wifi(n))
            
            btn_del = QPushButton("🗑")
            btn_del.setFixedWidth(45)
            btn_del.setStyleSheet("background-color: rgba(255, 50, 50, 0.15);")
            btn_del.clicked.connect(lambda ch, n=net['ssid']: self.delete_wifi(n))

            row.addWidget(btn_conn)
            row.addWidget(btn_del)
            
            container = QWidget()
            container.setLayout(row)
            self.list_layout.addWidget(container)

    def connect_wifi(self, name):
        os.system(f'alacritty -e nmcli device wifi connect "{name}" --ask &')

    def delete_wifi(self, name):
        subprocess.run(["nmcli", "connection", "delete", name])
        self.refresh_list()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassWifi()
    ex.show()
    sys.exit(app.exec())