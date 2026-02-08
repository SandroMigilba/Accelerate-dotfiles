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
        self.setWindowTitle('Wifi Manager')
        self.setFixedSize(380, 550)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout()
        
        # Header & Close Button
        header_row = QHBoxLayout()
        header = QLabel("Wi-Fi Manager")
        header.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.clicked.connect(self.close)
        header_row.addWidget(header)
        header_row.addWidget(close_btn)
        self.main_layout.addLayout(header_row)

        # Tombol Scan
        self.scan_btn = QPushButton("Scan Available Wi-Fi")
        self.scan_btn.clicked.connect(self.refresh_list)
        self.main_layout.addWidget(self.scan_btn)

        # Area List Wi-Fi (Scrollable)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.setStyleSheet("""
            QWidget { background-color: rgba(30, 30, 30, 0.3); border-radius: 15px; color: white; }
            QPushButton { background-color: rgba(255, 255, 255, 0.1); border: 1px solid rgba(255, 255, 255, 0.1); padding: 8px; border-radius: 8px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 0.2); }
            QScrollArea { border: none; background: transparent; }
        """)

        self.setLayout(self.main_layout)
        self.refresh_list()

    def get_wifi_list(self):
        # Mendeteksi Wi-Fi di sekitar (Scanning)
        try:
            output = subprocess.check_output(["nmcli", "-t", "-f", "SSID", "device", "wifi", "list"]).decode().splitlines()
            return sorted(list(set([line for line in output if line]))) # Hapus duplikat & urutkan
        except:
            return []

    def refresh_list(self):
        # Bersihkan list lama
        for i in reversed(range(self.list_layout.count())): 
            self.list_layout.itemAt(i).widget().setParent(None)

        # Isi list baru
        networks = self.get_wifi_list()
        for name in networks:
            row = QHBoxLayout()
            btn_conn = QPushButton(name)
            btn_conn.clicked.connect(lambda ch, n=name: self.connect_wifi(n))
            
            btn_del = QPushButton("Forget")
            btn_del.setStyleSheet("background-color: rgba(255, 50, 50, 0.2); max-width: 60px;")
            btn_del.clicked.connect(lambda ch, n=name: self.delete_wifi(n))

            row.addWidget(btn_conn)
            row.addWidget(btn_del)
            temp_widget = QWidget()
            temp_widget.setLayout(row)
            self.list_layout.addWidget(temp_widget)

    def connect_wifi(self, name):
        # Menghubungkan Wi-Fi via terminal untuk input password
        os.system(f'alacritty -e nmcli device wifi connect "{name}" --ask &')

    def delete_wifi(self, name):
        # Melupakan/menghapus profil Wi-Fi
        subprocess.run(["nmcli", "connection", "delete", name])
        self.refresh_list()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassWifi()
    ex.show()
    sys.exit(app.exec())