import sys
import os
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt

class LogoutMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Setup Window
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.showFullScreen()

        # Layout Utama
        main_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)

        # Daftar Tombol (Nama, Perintah)
        buttons = [
            ("󰌾\nLock", "hyprlock"),
            ("󰔣\nLogout", "hyprctl dispatch exit"),
            ("󰜉\nReboot", "systemctl reboot"),
            ("󰐥\nPower", "systemctl poweroff")
        ]

        for text, cmd in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(150, 150)
            btn.clicked.connect(lambda checked, c=cmd: self.run_cmd(c))
            button_layout.addWidget(btn)

        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        container = QWidget()
        container.setLayout(main_layout)
        container.setObjectName("container")
        
        final_layout = QVBoxLayout(self)
        final_layout.addWidget(container)

        # Styling (Dark Navy & Blue Accent)
        self.setStyleSheet("""
            #container {
                background-color: rgba(11, 18, 32, 0.9);
            }
            QPushButton {
                background-color: #121a2f;
                color: #e5e7eb;
                font-size: 20px;
                font-family: 'JetBrainsMono Nerd Font';
                border: 2px solid #38bdf8;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #38bdf8;
                color: #0b1220;
            }
        """)

    def run_cmd(self, cmd):
        os.system(cmd)
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = LogoutMenu()
    sys.exit(app.exec())