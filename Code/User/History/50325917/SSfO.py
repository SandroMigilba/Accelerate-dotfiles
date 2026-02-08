import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QListWidget, QLabel, QFileDialog)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class NobaraSwww(QWidget):
    def __init__(self):
        super().__init__()
        self.wallpaper_dir = os.path.expanduser("~/Pictures")
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Nobara Wallpaper Selector (SWWW)')
        self.resize(700, 450)

        main_layout = QHBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()

        # Daftar File (Kiri)
        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self.show_preview)
        left_layout.addWidget(QLabel("Daftar Gambar:"))
        left_layout.addWidget(self.list_widget)

        # Tombol Folder
        btn_folder = QPushButton("Pilih Folder")
        btn_folder.clicked.connect(self.load_folder)
        left_layout.addWidget(btn_folder)

        # Preview & Tombol Set (Kanan)
        self.preview_label = QLabel("Pilih gambar untuk preview")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setFixedSize(350, 200)
        self.preview_label.setStyleSheet("border: 1px solid #555; background: #222;")
        
        right_layout.addWidget(self.preview_label)
        
        btn_apply = QPushButton("Terapkan Wallpaper")
        btn_apply.setFixedHeight(50)
        btn_apply.setStyleSheet("background-color: #ce4433; color: white; font-weight: bold; border-radius: 5px;")
        btn_apply.clicked.connect(self.apply_wallpaper)
        right_layout.addWidget(btn_apply)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 1)
        self.setLayout(main_layout)

        # Jalankan Daemon SWWW secara otomatis
        subprocess.run(["swww-daemon"], stderr=subprocess.DEVNULL)

    def load_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Pilih Folder Wallpaper")
        if directory:
            self.wallpaper_dir = directory
            self.list_widget.clear()
            files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))]
            self.list_widget.addItems(files)

    def show_preview(self, index):
        if index >= 0:
            filename = self.list_widget.item(index).text()
            filepath = os.path.join(self.wallpaper_dir, filename)
            pixmap = QPixmap(filepath)
            self.preview_label.setPixmap(pixmap.scaled(self.preview_label.size(), 
                                        Qt.AspectRatioMode.KeepAspectRatio, 
                                        Qt.TransformationMode.SmoothTransformation))

    def apply_wallpaper(self):
        item = self.list_widget.currentItem()
        if item:
            path = os.path.join(self.wallpaper_dir, item.text())
            # Menggunakan efek transisi khas Nobara/Hyprland
            subprocess.run(["swww", "img", path, "--transition-type", "wipe", "--transition-angle", "30", "--transition-step", "90"])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraSwww()
    window.show()
    sys.exit(app.exec())