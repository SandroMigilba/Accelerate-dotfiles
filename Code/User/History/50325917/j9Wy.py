import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QScrollArea, QFrame)
from PyQt6.QtGui import QPixmap, QCursor, QIcon
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

class WallpaperThumbnail(QLabel):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.setFixedSize(240, 135)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setStyleSheet("border: 2px solid #313244; border-radius: 10px; background: #000;")
        
        pixmap = QPixmap(path)
        self.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                     Qt.TransformationMode.SmoothTransformation))
        self.setScaledContents(True)

    def mousePressEvent(self, event):
        subprocess.run(["swww", "img", self.path, "--transition-type", "wipe", "--transition-fps", "60"])
        self.setStyleSheet("border: 3px solid #f5c2e7; border-radius: 10px;")

class NobaraArrowGui(QWidget):
    def __init__(self):
        super().__init__()
        self.default_path = "/home/xeeukanbara/Pictures/wallpapers/"
        if not os.path.exists(self.default_path):
            self.default_path = os.path.expanduser("~/Pictures")
            
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Nobara Wallpaper Gallery')
        self.setFixedSize(1000, 350)
        self.setStyleSheet("background-color: #1e1e2e; color: #cdd6f4;")

        main_layout = QVBoxLayout()

        # Title
        title = QLabel("✨ Wallpaper Gallery")
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-left: 10px; color: #f5c2e7;")
        main_layout.addWidget(title)

        # Container Utama (Tombol L + Scroll + Tombol R)
        browser_layout = QHBoxLayout()

        # Tombol Kiri
        self.btn_left = QPushButton("❮")
        self.btn_left.setFixedSize(40, 135)
        self.btn_left.clicked.connect(self.scroll_left)
        self.btn_left.setStyleSheet(self.arrow_style())
        browser_layout.addWidget(self.btn_left)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedHeight(180)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) # Sembunyikan Scrollbar
        
        self.container = QWidget()
        self.content_layout = QHBoxLayout(self.container)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.content_layout.setSpacing(15)
        
        self.scroll.setWidget(self.container)
        browser_layout.addWidget(self.scroll)

        # Tombol Kanan
        self.btn_right = QPushButton("❯")
        self.btn_right.setFixedSize(40, 135)
        self.btn_right.clicked.connect(self.scroll_right)
        self.btn_right.setStyleSheet(self.arrow_style())
        browser_layout.addWidget(self.btn_right)

        main_layout.addLayout(browser_layout)

        # Path info & Folder button
        footer = QHBoxLayout()
        self.path_label = QLabel(f"Source: {self.default_path}")
        self.path_label.setStyleSheet("color: #6c7086; font-size: 11px; margin-left: 50px;")
        footer.addWidget(self.path_label)
        
        btn_folder = QPushButton("Change Folder")
        btn_folder.clicked.connect(self.select_folder)
        btn_folder.setStyleSheet("background: #313244; padding: 5px; border-radius: 5px; font-size: 10px;")
        footer.addStretch()
        footer.addWidget(btn_folder)
        footer.addSpacing(50)
        
        main_layout.addLayout(footer)
        self.setLayout(main_layout)

        self.load_wallpapers(self.default_path)
        subprocess.run(["swww-daemon"], stderr=subprocess.DEVNULL)

    def arrow_style(self):
        return """
            QPushButton { 
                background-color: rgba(49, 50, 68, 0.5); 
                color: white; 
                font-size: 24px; 
                border-radius: 10px; 
                border: none;
            }
            QPushButton:hover { background-color: #f5c2e7; color: #1e1e2e; }
        """

    def scroll_left(self):
        current = self.scroll.horizontalScrollBar().value()
        self.scroll.horizontalScrollBar().setValue(current - 500)

    def scroll_right(self):
        current = self.scroll.horizontalScrollBar().value()
        self.scroll.horizontalScrollBar().setValue(current + 500)

    def select_folder(self):
        new_dir = QFileDialog.getExistingDirectory(self, "Select Folder")
        if new_dir:
            self.load_wallpapers(new_dir)
            self.path_label.setText(f"Source: {new_dir}")

    def load_wallpapers(self, path):
        for i in reversed(range(self.content_layout.count())): 
            self.content_layout.itemAt(i).widget().setParent(None)
        try:
            files = sorted([f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))])
            for f in files:
                thumb = WallpaperThumbnail(os.path.join(path, f))
                self.content_layout.addWidget(thumb)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraArrowGui()
    window.show()
    sys.exit(app.exec())