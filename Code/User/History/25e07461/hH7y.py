import sys
import subprocess
import threading
import os
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                             QLabel, QHBoxLayout, QScrollArea, QFrame, QLineEdit)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject

class WorkerSignals(QObject):
    finished = pyqtSignal(list)

class WifiItem(QFrame):
    def __init__(self, net, parent_gui):
        super().__init__()
        self.net = net
        self.parent_gui = parent_gui
        self.is_expanded = False
        self.init_item()

    def init_item(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)

        # Baris Utama
        self.row_header = QWidget()
        bg = "rgba(0, 255, 255, 0.2)" if self.net['active'] else "rgba(255, 255, 255, 0.05)"
        border = "1px solid #00f2ff" if self.net['active'] else "1px solid rgba(255,255,255,0.1)"
        self.setStyleSheet(f"background-color: {bg}; border: {border}; border-radius: 12px; margin: 2px;")

        h_layout = QHBoxLayout(self.row_header)
        sig = self.net['signal']
        color = "#50fa7b" if sig > 75 else "#f1fa8c" if sig > 50 else "#ff5555"

        icon = "󰖩 " if self.net['active'] else "󰖪 "
        self.label_info = QLabel(f"{icon}{self.net['ssid']} ({sig}%)")
        self.label_info.setStyleSheet(f"color: {color}; font-weight: bold; border: none; background: transparent;")
        
        btn_text = "Active" if self.net['active'] else "Connect"
        self.btn_expand = QPushButton(btn_text)
        self.btn_expand.setFixedWidth(80)
        self.btn_expand.setStyleSheet("background: rgba(255,255,255,0.1); border: none; font-size: 10px; font-weight: bold; padding: 5px;")
        self.btn_expand.clicked.connect(self.toggle_accordion)

        btn_del = QPushButton("🗑")
        btn_del.setFixedWidth(35)
        btn_del.setStyleSheet("background: rgba(255, 50, 50, 0.2); border: none; color: white;")
        btn_del.clicked.connect(lambda: self.parent_gui.delete_wifi(self.net['ssid']))

        h_layout.addWidget(self.label_info)
        h_layout.addStretch()
        h_layout.addWidget(self.btn_expand)
        h_layout.addWidget(btn_del)
        layout.addWidget(self.row_header)

        # Accordion Input Password
        self.input_container = QWidget()
        input_h = QHBoxLayout(self.input_container)
        input_h.setContentsMargins(10, 5, 10, 10)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password...")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet("background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); padding: 5px; color: white;")
        self.pass_input.returnPressed.connect(self.submit_connection)

        btn_submit = QPushButton("Join")
        btn_submit.setFixedWidth(60)
        btn_submit.setStyleSheet("background: #00f2ff; color: black; font-weight: bold; border-radius: 5px;")
        btn_submit.clicked.connect(self.submit_connection)

        input_h.addWidget(self.pass_input)
        input_h.addWidget(btn_submit)
        self.input_container.setVisible(False)
        layout.addWidget(self.input_container)

    def toggle_accordion(self):
        if self.net['active']: return
        self.is_expanded = not self.is_expanded
        self.input_container.setVisible(self.is_expanded)
        if self.is_expanded: self.pass_input.setFocus()

    def submit_connection(self):
        pwd = self.pass_input.text()
        if pwd: self.parent_gui.execute_connect(self.net['ssid'], pwd)

class GlassWifi(QWidget):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()
        self.signals.finished.connect(self.populate_list)
        self.initUI()
        
        # Auto-refresh 15 detik agar tetap ringan
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_devices)
        self.refresh_timer.start(15000)

    def initUI(self):
        self.setWindowTitle('Wi-Fi Manager Pro')
        self.setFixedSize(420, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.main_layout = QVBoxLayout(self)
        
        # Header (Sama seperti BT Manager)
        header = QHBoxLayout()
        self.icon_label = QLabel("📡")
        self.icon_label.setStyleSheet("color: #00f2ff; font-weight: bold; background: transparent; font-size: 16px;")
        
        self.title_label = QLabel("Wi-Fi Manager")
        self.title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; background: transparent;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("background: rgba(255, 50, 50, 0.2); border-radius: 15px; border: none; color: white;")
        close_btn.clicked.connect(self.close)
        
        header.addWidget(self.icon_label)
        header.addWidget(self.title_label)
        header.addStretch()
        header.addWidget(close_btn)
        self.main_layout.addLayout(header)

        # Scan Button
        self.scan_btn = QPushButton("🔍 Scan Networks")
        self.scan_btn.setStyleSheet("background: rgba(255,255,255,0.05); padding: 12px; border: 1px solid rgba(255,255,255,0.1); font-weight: bold;")
        self.scan_btn.clicked.connect(self.refresh_devices)
        self.main_layout.addWidget(self.scan_btn)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.list_layout = QVBoxLayout(self.scroll_content)
        self.list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll)

        self.setStyleSheet("QWidget { background-color: rgba(15, 15, 15, 0.9); border-radius: 20px; color: white; }")
        
        # Animasi Loading
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.animate_loading)
        self.frames = ["|", "/", "-", "\\"]
        self.frame_idx = 0

        self.refresh_devices()

    def animate_loading(self):
        self.frame_idx = (self.frame_idx + 1) % len(self.frames)
        self.icon_label.setText(self.frames[self.frame_idx])

    def refresh_devices(self):
        self.loading_timer.start(100)
        threading.Thread(target=self.fetch_data, daemon=True).start()

    def fetch_data(self):
        devs = []
        try:
            subprocess.run(["nmcli", "radio", "wifi", "on"], check=False)
            subprocess.run(["nmcli", "device", "wifi", "rescan"], check=False)
            out = subprocess.check_output(["nmcli", "-t", "-f", "ACTIVE,SSID,BARS,SIGNAL", "device", "wifi", "list"]).decode().splitlines()
            seen = set()
            for line in out:
                p = line.split(':')
                if len(p) >= 4 and p[1].strip() and p[1] not in seen:
                    devs.append({"active": p[0] == "yes", "ssid": p[1], "signal": int(p[3] if p[3].isdigit() else 0)})
                    seen.add(p[1])
            devs.sort(key=lambda x: (x['active'], x['signal']), reverse=True)
            self.signals.finished.emit(devs)
        except:
            self.signals.finished.emit([])

    def populate_list(self, networks):
        self.loading_timer.stop()
        self.icon_label.setText("📡")
        
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        for net in networks:
            self.list_layout.addWidget(WifiItem(net, self))

    def execute_connect(self, ssid, password):
        self.title_label.setText("Connecting...")
        subprocess.run(["nmcli", "connection", "delete", ssid], check=False)
        subprocess.Popen(["nmcli", "device", "wifi", "connect", ssid, "password", password])
        QTimer.singleShot(5000, self.refresh_devices)

    def delete_wifi(self, name):
        subprocess.run(["nmcli", "connection", "delete", name])
        self.refresh_devices()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GlassWifi()
    ex.show()
    sys.exit(app.exec())