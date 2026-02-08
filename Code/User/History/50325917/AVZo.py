import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QScrollArea)
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt

class WallpaperThumbnail(QLabel):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.setFixedSize(220, 130)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        # Style thumbnail dengan border rounded
        self.setStyleSheet("border: 2px solid #333; border-radius: 12px; background: #000;")
        
        pixmap = QPixmap(path)
        self.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                     Qt.TransformationMode.SmoothTransformation))
        self.setScaledContents(True)

    def mousePressEvent(self, event):
        # Efek transisi swww saat klik
        subprocess.run(["swww", "img", self.path, 
                        "--transition-type", "outer", 
                        "--transition-fps", "60", 
                        "--transition-step", "100"])
        # Feedback visual sederhana
        self.setStyleSheet("border: 3px solid #ce4433; border-radius: 12px;") 

class NobaraSwwwLauncher(QWidget):
    def __init__(self):
        super().__init__()
        # SET PATH DEFAULT DISINI
        self.default_path = "/home/xeeukanbara/Pictures/wallpapers/"
        
        # Validasi folder: jika tidak ada, gunakan folder Pictures user
        if not os.path.exists(self.default_path):
            self.default_path = os.path.expanduser("~/Pictures")
            
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Nobara Wallpaper Gallery')
        self.setFixedSize(950, 320)
        self.setStyleSheet("background-color: #11111b; color: #cdd6f4; font-family: 'Inter', sans-serif;")

        layout = QVBoxLayout()

        # Header Section
        header = QHBoxLayout()
        title_label = QLabel("✨ Wallpaper Collections")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #f5c2e7;")
        header.addWidget(title_label)
        
        header.addStretch()
        
        btn_folder = QPushButton("📁 Change Folder")
        btn_folder.clicked.connect(self.select_folder)
        btn_folder.setStyleSheet("""
            QPushButton { background: #313244; border: none; padding: 8px 15px; border-radius: 8px; }
            QPushButton:hover { background: #45475a; }
        """)
        header.addWidget(btn_folder)
        layout.addLayout(header)

        # Scroll Area Horizontal
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(200)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setStyleSheet("""
            QScrollArea { background-color: transparent; }
            QScrollBar:horizontal { height: 8px; background: #181825; border-radius: 4px; }
            QScrollBar::handle:horizontal { background: #ce4433; border-radius: 4px; }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { background: none; }
        """)

        self.container = QWidget()
        self.content_layout = QHBoxLayout(self.container)
        self.content_layout.setContentsMargins(15, 10, 15, 10)
        self.content_layout.setSpacing(20)
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        # Footer
        footer_text = f"Folder aktif: {self.default_path}"
        self.path_label = QLabel(footer_text)
        self.path_label.setStyleSheet("color: #6c7086; font-size: 10px;")
        layout.addWidget(self.path_label)

        self.setLayout(layout)
        
        # Load images
        self.load_wallpapers(self.default_path)
        
        # Pastikan daemon swww aktif
        subprocess.run(["swww-daemon"], stderr=subprocess.DEVNULL)

    def select_folder(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Pilih Folder")
        if new_dir:
            self.load_wallpapers(new_dir)
            self.path_label.setText(f"Folder aktif: {new_dir}")

    def load_wallpapers(self, path):
        # Bersihkan layout lama
        for i in reversed(range(self.content_layout.count())): 
            self.content_layout.itemAt(i).widget().setParent(None)

        try:
            valid_ext = ('.png', '.jpg', '.jpeg', '.webp', '.gif')
            files = [f for f in os.listdir(path) if f.lower().endswith(valid_ext)]
            files.sort() # Urutkan abjad

            for f in files:
                full_path = os.path.join(path, f)
                thumb = WallpaperThumbnail(full_path)
                self.content_layout.addWidget(thumb)
        except Exception as e:
            print(f"Error loading images: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraSwwwLauncher()
    window.show()
    sys.exit(app.exec())