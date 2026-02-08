import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFileDialog, QScrollArea)
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect

class WallpaperThumbnail(QLabel):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.setFixedSize(240, 135)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus) # Agar bisa menerima fokus keyboard
        self.setStyleSheet("border: 3px solid #313244; border-radius: 12px; background: #000;")
        
        pixmap = QPixmap(path)
        self.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                     Qt.TransformationMode.SmoothTransformation))
        self.setScaledContents(True)

    def focusInEvent(self, event):
        # Warna highlight saat dipilih pakai arrow
        self.setStyleSheet("border: 4px solid #f5c2e7; border-radius: 12px;")
        super().focusInEvent(event)
        # Scroll otomatis ke item yang dipilih
        self.parentWidget().parent().parent().ensureWidgetVisible(self)

    def focusOutEvent(self, event):
        # Kembali ke warna normal
        self.setStyleSheet("border: 3px solid #313244; border-radius: 12px;")
        super().focusOutEvent(event)

    def apply_wallpaper(self):
        subprocess.run(["swww", "img", self.path, "--transition-type", "grow", "--transition-fps", "60"])

class NobaraKeyboardGui(QWidget):
    def __init__(self):
        super().__init__()
        self.default_path = "/home/xeeukanbara/Pictures/wallpapers/"
        if not os.path.exists(self.default_path):
            self.default_path = os.path.expanduser("~/Pictures")
        
        self.thumbnails = []
        self.current_index = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Arrow Navigation Wallpaper')
        self.setFixedSize(1000, 320)
        self.setStyleSheet("background-color: #11111b; color: #cdd6f4;")

        layout = QVBoxLayout()
        
        title = QLabel("⌨️ Use Arrow Keys to Select • Press Enter to Apply")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #f5c2e7; margin: 10px;")
        layout.addWidget(title)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.container = QWidget()
        self.content_layout = QHBoxLayout(self.container)
        self.content_layout.setSpacing(20)
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        self.setLayout(layout)
        self.load_wallpapers(self.default_path)
        
        # Berikan fokus awal ke item pertama
        if self.thumbnails:
            self.thumbnails[0].setFocus()

    def load_wallpapers(self, path):
        for i in reversed(range(self.content_layout.count())): 
            self.content_layout.itemAt(i).widget().setParent(None)
        
        self.thumbnails = []
        try:
            files = sorted([f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))])
            for f in files:
                thumb = WallpaperThumbnail(os.path.join(path, f), self.container)
                self.content_layout.addWidget(thumb)
                self.thumbnails.append(thumb)
        except Exception as e:
            print(f"Error: {e}")

    def keyPressEvent(self, event):
        # Navigasi Arrow Kanan
        if event.key() == Qt.Key.Key_Right:
            self.current_index = (self.current_index + 1) % len(self.thumbnails)
            self.thumbnails[self.current_index].setFocus()
        
        # Navigasi Arrow Kiri
        elif event.key() == Qt.Key.Key_Left:
            self.current_index = (self.current_index - 1) % len(self.thumbnails)
            self.thumbnails[self.current_index].setFocus()
        
        # Tekan Enter untuk Apply
        elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.thumbnails[self.current_index].apply_wallpaper()
            
        # ESC untuk keluar
        elif event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraKeyboardGui()
    window.show()
    sys.exit(app.exec())