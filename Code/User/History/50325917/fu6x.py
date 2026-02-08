import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QLabel, 
                             QVBoxLayout, QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QSize

class RoundedImage(QLabel):
    """Widget khusus agar gambar benar-benar membulat mengikuti border-radius"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.radius = 20
        self.border_width = 1
        self.border_color = "#313244"
        self._pixmap = None

    def set_image(self, path, size, border_color):
        self.border_color = border_color
        pix = QPixmap(path)
        self._pixmap = pix.scaled(size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                 Qt.TransformationMode.SmoothTransformation)
        self.update()

    def paintEvent(self, event):
        if not self._pixmap:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Path untuk membulatkan gambar
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        
        painter.setClipPath(path)
        # Gambar pixmap di tengah slot
        painter.drawPixmap(0, 0, self._pixmap)
        
        # Gambar border 1px
        painter.setClipping(False)
        painter.setPen(QColor(self.border_color))
        painter.drawRoundedRect(0, 0, self.width()-1, self.height()-1, self.radius, self.radius)

class NobaraCarousel(QWidget):
    def __init__(self):
        super().__init__()
        self.path = "/home/xeeukanbara/Pictures/wallpapers/"
        if not os.path.exists(self.path):
            self.path = os.path.expanduser("~/Pictures")

        self.images = sorted([os.path.join(self.path, f) for f in os.listdir(self.path) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))])
        self.current_index = 0
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(1450, 650)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.carousel_layout = QHBoxLayout()
        self.carousel_layout.setSpacing(60) 
        self.carousel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # DIMENSI: Tengah 10% lebih besar (440x248) vs Samping (400x225)
        self.size_side = QSize(400, 225)
        self.size_center = QSize(440, 248)

        self.slot_left = RoundedImage()
        self.slot_center = RoundedImage()
        self.slot_right = RoundedImage()

        self.slot_left.setFixedSize(self.size_side)
        self.slot_center.setFixedSize(self.size_center)
        self.slot_right.setFixedSize(self.size_side)

        self.carousel_layout.addWidget(self.slot_left)
        self.carousel_layout.addWidget(self.slot_center)
        self.carousel_layout.addWidget(self.slot_right)

        # Label Nama File (Bersih tanpa background)
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("""
            color: #cdd6f4; 
            font-size: 16px; 
            font-family: 'JetBrains Mono', sans-serif;
            font-weight: bold;
            margin-top: 30px;
        """)

        self.main_layout.addLayout(self.carousel_layout)
        self.main_layout.addWidget(self.name_label)
        self.setLayout(self.main_layout)
        self.update_display()

    def update_display(self):
        if not self.images: return
        total = len(self.images)
        idx_c = self.current_index
        idx_l = (idx_c - 1) % total
        idx_r = (idx_c + 1) % total

        # Render dengan Border 1px
        self.slot_left.set_image(self.images[idx_l], self.size_side, "#313244")
        self.slot_center.set_image(self.images[idx_c], self.size_center, "#f5c2e7")
        self.slot_right.set_image(self.images[idx_r], self.size_side, "#313244")

        # Efek fokus
        self.apply_effects()
        self.name_label.setText(os.path.basename(self.images[idx_c]))

    def apply_effects(self):
        # Shadow hanya untuk tengah
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setYOffset(10)
        self.slot_center.setGraphicsEffect(shadow)

        # Opacity untuk samping
        for slot in [self.slot_left, self.slot_right]:
            op = QGraphicsOpacityEffect()
            op.setOpacity(0.5)
            slot.setGraphicsEffect(op)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Right:
            self.current_index = (self.current_index + 1) % len(self.images)
            self.update_display()
        elif event.key() == Qt.Key.Key_Left:
            self.current_index = (self.current_index - 1) % len(self.images)
            self.update_display()
        elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            subprocess.run(["swww", "img", self.images[self.current_index], "--transition-type", "outer"])
        elif event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraCarousel()
    geo = app.primaryScreen().geometry()
    window.move((geo.width() - window.width()) // 2, (geo.height() - window.height()) // 2)
    window.show()
    sys.exit(app.exec())