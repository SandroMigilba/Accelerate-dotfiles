import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QHBoxLayout, QScrollArea, QLineEdit, QFrame)
from PyQt6.QtCore import Qt, QTimer

class WifiItem(QFrame):
    """Widget custom untuk setiap baris Wi-Fi dengan efek accordion"""
    def __init__(self, net, parent_gui):
        super().__init__()
        self.net = net
        self.parent_gui = parent_gui
        self.is_expanded = False
        self.init_item()

    def init_item(self):
        self.main_vbox = QVBoxLayout(self)
        self.main_vbox.setContentsMargins(5, 5, 5, 5)
        self.main_vbox.setSpacing(0)

        # Container Utama (Baris yang selalu terlihat)
        self.row_header = QWidget()
        bg_color = "rgba(0, 255, 255, 0.15)" if self.net['active'] else "rgba(255, 255, 255, 0.05)"
        self.setStyleSheet(f"background-color: {bg_color}; border-radius: 12px;")
        
        header_layout = QHBoxLayout(self.row_header)
        color = "#50fa7b" if self.net['signal'] > 75 else "#f1fa8c" if self.net['signal'] > 50 else "#ff5555"

        status_icon = "✧ " if self.net['active'] else ""
        self.label_info = QLabel(f"{status_icon}{self.net['ssid']} ({self.net['signal']}%)")
        self.label_info.setStyleSheet(f"color: {color}; font-weight: bold; background: transparent;")
        
        self.btn_expand = QPushButton("Connect" if not self.net['active'] else "Active")
        self.btn_expand.setFixedWidth(80)
        self.btn_expand.setStyleSheet("background-color: rgba(255, 255, 255, 0.1); border: none; font-size: 10px;")
        self.btn_expand.clicked.connect(self.toggle_accordion)

        self.btn_del = QPushButton("🗑")
        self.btn_del.setFixedWidth(35)
        self.btn_del.setStyleSheet("background-color: rgba(255, 50, 50, 0.2); border: none;")
        self.btn_del.clicked.connect(lambda: self.parent_gui.delete_wifi(self.net['ssid']))

        header_layout.addWidget(self.label_info)
        header_layout.addStretch()
        header_layout.addWidget(self.btn_expand)
        header_layout.addWidget(self.btn_del)
        
        self.main_vbox.addWidget(self.row_header)

        # Container Accordion (Tersembunyi di awal)
        self.input_container = QWidget()
        self.input_layout = QHBoxLayout(self.input_container)
        self.input_layout.setContentsMargins(10, 5, 10, 10)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password...")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet("background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); padding: 5px;")

        self.btn_submit = QPushButton("enter")
        self.btn_submit.setFixedWidth(60)
        self.btn_submit.setStyleSheet("background-color: #50fa7b; color: black; font-weight: bold;")
        self.btn_submit.clicked.connect(self.submit_connection)

        self.input_layout.addWidget(self.pass_input)
        self.input_layout.addWidget(self.btn_submit)
        
        self.input_container.setVisible(False)
        self.main_vbox.addWidget(self.input_container)

    def toggle_accordion(self):
        if self.net['active']: return
        self.is_expanded = not self.is_expanded
        self.input_container.setVisible(self.is_expanded)
        if self.is_expanded:
            self.pass_input.setFocus()

    def submit_connection(self):
        pwd = self.pass_input.text()
        if pwd:
            self.parent_gui.execute_connect(self.net['ssid'], pwd)

class GlassWifi(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Wifi Manager Accordion')
        self.setFixedSize(400, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.main_layout = QVBoxLayout(self)
        
        header_row = QHBoxLayout()
        self.header_label = QLabel("📡 Wi-Fi Switcher")
        self.header_label.setStyleSheet("color: white; font-size: 20px; font-weight: bold; padding: 10px;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(35, 35)
        close_btn.setStyleSheet("background-color: rgba(255, 80, 80, 0.4); border-radius: 17px; color: white; border: none;")
        close_btn.clicked.connect(self.close)
        
        header_row.addWidget(self.header_label)
        header_row.addStretch()
        header_row.addWidget(close_btn)
        self.main_layout.addLayout(header_row)

        self.scan_btn = QPushButton("Refresh & Scan")
        self.scan_btn.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(72, 198, 239, 0.5), stop:1 rgba(111, 134, 214, 0.5)); font-weight: bold; padding: 12px;")
        self.scan_btn.clicked.connect(self.refresh_list)
        self.main_layout.addWidget(self.scan_btn)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.setStyleSheet("""
            QWidget { background-color: rgba(15, 15, 15, 0.85); border-radius: 20px; color: white; }
            QScrollArea { border: none; background: transparent; }
        """)

        self.refresh_list()

    def get_wifi_data(self):
        try:
            subprocess.run(["nmcli", "radio", "wifi", "on"], check=False)
            subprocess.run(["nmcli", "device", "wifi", "rescan"], check=False)
            cmd = ["nmcli", "-t", "-f", "ACTIVE,SSID,BARS,SIGNAL", "device", "wifi", "list"]
            output = subprocess.check_output(cmd).decode().splitlines()
            
            wifi_list = []
            seen = set()
            for line in output:
                p = line.split(':')
                if len(p) >= 4 and p[1].strip() and p[1] not in seen:
                    wifi_list.append({"active": p[0] == "yes", "ssid": p[1], "bars": p[2], "signal": int(p[3] if p[3].isdigit() else 0)})
                    seen.add(p[1])
            return sorted(wifi_list, key=lambda x: x['signal'], reverse=True)
        except: return []

    def refresh_list(self):
        self.header_label.setText("🔄 Scanning...")
        QApplication.processEvents()
        for i in reversed(range(self.list_layout.count())): 
            self.list_layout.itemAt(i).widget().setParent(None)

        networks = self.get_wifi_data()
        for net in networks:
            item = WifiItem(net, self)
            self.list_layout.addWidget(item)
        self.header_label.setText("📡 Wi-Fi Switcher")

    def execute_connect(self, ssid, password):
        self.header_label.setText(f"Connecting...")
        QApplication.processEvents()
        subprocess.run(["nmcli", "connection", "delete", ssid], check=False)
        subprocess.Popen(["nmcli", "device", "wifi", "connect", ssid, "password", password])
        QTimer.singleShot(6000, self.refresh_list)

    def delete_wifi(self, name):
        subprocess.run(["nmcli", "connection", "delete", name])
        self.refresh_list()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassWifi()
    ex.show()
    sys.exit(app.exec())