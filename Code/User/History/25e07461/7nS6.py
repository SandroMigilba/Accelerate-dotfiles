import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QScrollArea
from PyQt6.QtCore import Qt, QTimer

class GlassWifi(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # Setup Timer untuk Auto-Refresh (10 detik)
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_list)
        self.timer.start(10000) 

    def initUI(self):
        self.setWindowTitle('Wifi Manager Pro')
        self.setFixedSize(400, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout()
        
        # Header
        header_row = QHBoxLayout()
        self.header_label = QLabel("📡 Wi-Fi Scanner")
        self.header_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding: 10px;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(35, 35)
        close_btn.setStyleSheet("""
            QPushButton { background-color: rgba(255, 80, 80, 0.4); border-radius: 17px; color: white; border: none; }
            QPushButton:hover { background-color: rgba(255, 50, 50, 0.8); }
        """)
        close_btn.clicked.connect(self.close)
        
        header_row.addWidget(self.header_label)
        header_row.addStretch()
        header_row.addWidget(close_btn)
        self.main_layout.addLayout(header_row)

        # Tombol Scan
        self.scan_btn = QPushButton("Refresh Networks")
        self.scan_btn.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(72, 198, 239, 0.5), stop:1 rgba(111, 134, 214, 0.5));
                border: 1px solid rgba(255,255,255,0.2);
                font-weight: bold; padding: 10px; margin-bottom: 5px;
            }
        """)
        self.scan_btn.clicked.connect(self.refresh_list)
        self.main_layout.addWidget(self.scan_btn)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.setStyleSheet("""
            QWidget { background-color: rgba(15, 15, 15, 0.6); border-radius: 20px; color: white; }
            QPushButton { background-color: rgba(255, 255, 255, 0.1); border-radius: 10px; color: white; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
            QScrollArea { border: none; background: transparent; }
        """)

        self.setLayout(self.main_layout)
        self.refresh_list()

    def get_wifi_data(self):
        try:
            # Paksa rescan agar data tidak "basi"
            subprocess.run(["nmcli", "device", "wifi", "rescan"], check=False)
            cmd = ["nmcli", "-t", "-f", "ACTIVE,SSID,BARS,SIGNAL", "device", "wifi", "list"]
            output = subprocess.check_output(cmd).decode().splitlines()
            
            wifi_list = []
            seen_ssids = set()
            for line in output:
                parts = line.split(':')
                # Format: ACTIVE:SSID:BARS:SIGNAL
                if len(parts) >= 4 and parts[1] and parts[1] not in seen_ssids:
                    wifi_list.append({
                        "active": parts[0] == "yes",
                        "ssid": parts[1],
                        "bars": parts[2],
                        "signal": int(parts[3] if parts[3].isdigit() else 0)
                    })
                    seen_ssids.add(parts[1])
            return sorted(wifi_list, key=lambda x: x['signal'], reverse=True)
        except Exception as e:
            print(f"Error: {e}")
            return []

    def refresh_list(self):
        self.header_label.setText("🔄 Scanning...")
        QApplication.processEvents() # Paksa UI update kata "Scanning"

        # Hapus list lama
        for i in reversed(range(self.list_layout.count())): 
            widget = self.list_layout.itemAt(i).widget()
            if widget: widget.setParent(None)

        networks = self.get_wifi_data()
        for net in networks:
            row_container = QWidget()
            # Style berbeda untuk wifi yang sedang aktif
            bg_color = "rgba(0, 255, 255, 0.15)" if net['active'] else "rgba(255, 255, 255, 0.05)"
            border = "1px solid cyan" if net['active'] else "none"
            row_container.setStyleSheet(f"background-color: {bg_color}; border: {border}; border-radius: 10px;")
            
            row = QHBoxLayout(row_container)
            
            # Warna Sinyal
            if net['signal'] > 75: color = "#50fa7b"
            elif net['signal'] > 50: color = "#f1fa8c"
            else: color = "#ff5555"

            prefix = "⭐ " if net['active'] else ""
            btn_text = f"{prefix}{net['ssid']} ({net['signal']}%)"
            
            btn_conn = QPushButton(btn_text)
            btn_conn.setStyleSheet(f"text-align: left; color: {color}; border: none; padding: 10px; background: transparent;")
            btn_conn.clicked.connect(lambda ch, n=net['ssid']: self.connect_wifi(n))
            
            btn_del = QPushButton("🗑")
            btn_del.setFixedWidth(40)
            btn_del.setStyleSheet("background-color: rgba(255, 50, 50, 0.2); border: none; padding: 5px;")
            btn_del.clicked.connect(lambda ch, n=net['ssid']: self.delete_wifi(n))

            row.addWidget(btn_conn)
            row.addStretch()
            row.addWidget(btn_del)
            self.list_layout.addWidget(row_container)

        self.header_label.setText("📡 Wi-Fi Scanner")

    def connect_wifi(self, name):
        self.header_label.setText(f"Connecting to {name}...")
        os.system(f'alacritty -e nmcli device wifi connect "{name}" --ask &')

    def delete_wifi(self, name):
        subprocess.run(["nmcli", "connection", "delete", name])
        self.refresh_list()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassWifi()
    ex.show()
    sys.exit(app.exec())