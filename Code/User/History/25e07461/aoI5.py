import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt

class GlassWifi(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Wifi Manager')
        self.setFixedSize(350, 450)
        
        # Membuat jendela tanpa border/frame agar terlihat bersih
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QVBoxLayout()
        
        # Header
        header = QLabel("Wi-Fi Manager")
        header.setStyleSheet("color: white; font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Ambil daftar koneksi
        conns = subprocess.check_output(["nmcli", "-g", "NAME", "connection", "show"]).decode().splitlines()

        for name in conns[:6]: # Limit 6 koneksi biar rapi
            row = QHBoxLayout()
            
            btn_conn = QPushButton(name)
            btn_conn.clicked.connect(lambda ch, n=name: self.connect_wifi(n))
            
            btn_del = QPushButton("Delete")
            btn_del.setObjectName("delBtn")
            btn_del.clicked.connect(lambda ch, n=name: self.delete_wifi(n))

            row.addWidget(btn_conn)
            row.addWidget(btn_del)
            layout.addLayout(row)

            # Style QSS (Glassmorphism Style)
            self.setStyleSheet("""
                QWidget {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 15px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                }
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.15);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    padding: 8px;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.3);
                }
                #delBtn {
                    background-color: rgba(255, 50, 50, 0.2);
                    max-width: 60px;
                }
            """)

        self.setLayout(layout)

    def connect_wifi(self, name):
        os.system(f'alacritty -e nmcli device wifi connect "{name}" --ask &')

    def delete_wifi(self, name):
        subprocess.run(["nmcli", "connection", "delete", name])
        self.close() # Refresh manual dengan buka ulang

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassWifi()
    ex.show()
    sys.exit(app.exec())