import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QScrollArea)
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt

class WallpaperThumbnail(QLabel):
    def __init__(self, path, parent=None):
        super().__init__(parent)
        self.path = path
        self.setFixedSize(260, 146)  # Aspect ratio 16:9 yang pas
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus) # Fokus dikontrol oleh parent
        
        # Desain default (Border gelap)
        self.default_style = "border: 4px solid #313244; border-radius: 15px; background: #000;"
        self.select_style = "border: 4px solid #f5c2e7; border-radius: 15px; background: #000;"
        self.setStyleSheet(self.default_style)
        
        pixmap = QPixmap(path)
        self.setPixmap(pixmap.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                     Qt.TransformationMode.SmoothTransformation))
        self.setScaledContents(True)

    def set_active(self, is_active):
        if is_active:
            self.setStyleSheet(self.select_style)
        else:
            self.setStyleSheet(self.default_style)

class NobaraStepGui(QWidget):
    def __init__(self):
        super().__init__()
        self.default_path = "/home/xeeukanbara/Pictures/wallpapers/"
        
        # Fallback jika folder tidak ditemukan
        if not os.path.exists(self.default_path):
            self.default_path = os.path.expanduser("~/Pictures")
            
        self.thumbnails = []
        self.current_index = 0
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Hyprland Wallpaper Selector')
        self.setFixedSize(1000, 300)
        # Efek Window Transparan/Gelap Khas Hyprland
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: #11111b; color: #cdd6f4; border-radius: 20px;")

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Header info
        self.info_label = QLabel("Pilih Wallpaper: [Arrow Keys] | Set: [Enter]")
        self.info_label.setStyleSheet("font-size: 14px; color: #a6adc8; font-weight: bold;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        # Scroll Area
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setStyleSheet("background: transparent;")
        
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.content_layout = QHBoxLayout(self.container)
        self.content_layout.setSpacing(25)
        
        self.scroll.setWidget(self.container)
        layout.addWidget(self.scroll)

        self.setLayout(layout)
        self.load_wallpapers()
        
        # Tandai item pertama sebagai aktif secara visual
        if self.thumbnails:
            self.thumbnails[self.current_index].set_active(True)

    def load_wallpapers(self):
        try:
            files = sorted([f for f in os.listdir(self.default_path) 
                           if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))])
            for f in files:
                thumb = WallpaperThumbnail(os.path.join(self.default_path, f), self.container)
                self.content_layout.addWidget(thumb)
                self.thumbnails.append(thumb)
        except Exception as e:
            print(f"Error: {e}")

    def keyPressEvent(self, event):
        if not self.thumbnails:
            return

        # Simpan index lama untuk mematikan highlight
        old_index = self.current_index

        if event.key() == Qt.Key.Key_Right:
            self.current_index = (self.current_index + 1) % len(self.thumbnails)
        elif event.key() == Qt.Key.Key_Left:
            self.current_index = (self.current_index - 1) % len(self.thumbnails)
        elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.apply_wallpaper()
            return
        elif event.key() == Qt.Key.Key_Escape:
            self.close()

        # Update visual highlight
        self.thumbnails[old_index].set_active(False)
        self.thumbnails[self.current_index].set_active(True)
        
        # Scroll otomatis ke item baru (One-by-one scroll)
        self.scroll.ensureWidgetVisible(self.thumbnails[self.current_index], 300, 0)

    def apply_wallpaper(self):
        target = self.thumbnails[self.current_index]
        # Transisi SWWW
        subprocess.run([
            "swww", "img", target.path, 
            "--transition-type", "grow", 
            "--transition-duration", "1.5",
            "--transition-fps", "60"
        ])
        # Opsional: Tutup setelah memilih
        # self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraStepGui()
    window.show()
    sys.exit(app.exec())