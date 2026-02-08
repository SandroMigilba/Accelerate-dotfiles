import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QScrollArea, QFrame)
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt, QSize

class WallpaperThumbnail(QLabel):
    """Widget khusus untuk setiap thumbnail gambar"""
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.setFixedSize(200, 120)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("border: 2px solid #333; border-radius: 10px; background: #000;")
        
        pixmap = QPixmap(path)
        self.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                     Qt.TransformationMode.SmoothTransformation))
        self.setScaledContents(True)

    def mousePressEvent(self, event):
        # Langsung ganti wallpaper saat thumbnail diklik
        subprocess.run(["swww", "img", self.path, "--transition-type", "grow", "--transition-pos", "top"])
        self.setStyleSheet("border: 3px solid #ce4433; border-radius: 10px;") # Highlight merah Nobara

class NobaraHorizontalGui(QWidget):
    def __init__(self):
        super().__init__()
        self.wallpaper_dir = os.path.expanduser("~/Pictures")
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Nobara SWWW Horizontal Picker')
        self.setFixedSize(900, 300)
        self.setStyleSheet("background-color: #1a1b26; color: white;")

        layout = QVBoxLayout()

        # Header
        header = QHBoxLayout()
        header.addWidget(QLabel("📂 Wallpaper Gallery"))
        
        btn_folder = QPushButton("Change Folder")
        btn_folder.clicked.connect(self.load_folder)
        btn_folder.setStyleSheet("background: #333; padding: 5px 15px; border-radius: 5px;")
        header.addStretch()
        header.addWidget(btn_folder)
        layout.addLayout(header)

        # Scroll Area Setup
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(180)
        self.scroll.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:horizontal { height: 10px; background: #222; border-radius: 5px; }
            QScrollBar::handle:horizontal { background: #ce4433; border-radius: 5px; }
        """)

        # Container untuk foto-foto
        self.container = QWidget()
        self.content_layout = QHBoxLayout(self.container)
        self.content_layout.setSpacing(15)
        self.content_layout.setContentsMargins(10, 10, 10, 10)
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        # Footer info
        self.footer = QLabel("Click a thumbnail to apply instantly")
        self.footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.footer.setStyleSheet("color: #777; font-size: 11px;")
        layout.addWidget(self.footer)

        self.setLayout(layout)
        
        # Load default folder
        self.refresh_thumbnails(self.wallpaper_dir)
        subprocess.run(["swww-daemon"], stderr=subprocess.DEVNULL)

    def load_folder(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Wallpaper Folder")
        if directory:
            self.wallpaper_dir = directory
            self.refresh_thumbnails(directory)

    def refresh_thumbnails(self, path):
        # Hapus widget lama
        for i in reversed(range(self.content_layout.count())): 
            self.content_layout.itemAt(i).widget().setParent(None)

        # List files
        try:
            files = [f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))]
            for f in files:
                full_path = os.path.join(path, f)
                thumb = WallpaperThumbnail(full_path)
                self.content_layout.addWidget(thumb)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraHorizontalGui()
    window.show()
    sys.exit(app.exec())