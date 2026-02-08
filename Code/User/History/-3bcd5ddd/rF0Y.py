from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup

import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QLabel, 
                             QVBoxLayout, QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QSize

class RoundedImage(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.radius = 20
        self.border_width = 1
        self.border_color = "#00ffff"
        self._pixmap = None

    def set_image(self, path, size, border_color):
        self.border_color = border_color
        pix = QPixmap(path)
        self._pixmap = pix.scaled(size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                 Qt.TransformationMode.SmoothTransformation)
        self.update()

    def paintEvent(self, event):
        if not self._pixmap: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, self._pixmap)
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
        
        # Deteksi wallpaper aktif
        self.current_index = self.get_active_wallpaper_index()
        self.initUI()

    def get_active_wallpaper_index(self):
        try:
            # Query swww untuk mendapatkan path wallpaper saat ini
            result = subprocess.check_output(["swww", "query"], text=True)
            for line in result.splitlines():
                if "image:" in line:
                    current_path = line.split("image:")[1].strip()
                    if current_path in self.images:
                        return self.images.index(current_path)
        except:
            pass
        return 0

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(1450, 650)

        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.carousel_layout = QHBoxLayout()
        self.carousel_layout.setSpacing(60) 
        self.carousel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("color: #cdd6f4; font-size: 16px; font-family: 'JetBrains Mono'; font-weight: bold; margin-top: 30px;")

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

        self.slot_left.set_image(self.images[idx_l], self.size_side, "#313244")
        self.slot_center.set_image(self.images[idx_c], self.size_center, "#00ffff")
        self.slot_right.set_image(self.images[idx_r], self.size_side, "#313244")

        self.apply_effects()
        self.name_label.setText(os.path.basename(self.images[idx_c]))

    def apply_effects(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setYOffset(10)
        self.slot_center.setGraphicsEffect(shadow)

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
            self.close() # Menutup window setelah pilih wallpaper
        elif event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraCarousel()
    geo = app.primaryScreen().geometry()
    window.move((geo.width() - window.width()) // 2, (geo.height() - window.height()) // 2)
    window.show()
    sys.exit(app.exec())

def slide_animation(self, direction):
    """
    direction = 1  -> kanan
    direction = -1 -> kiri
    """
    anim_group = QParallelAnimationGroup(self)

    offset = 500 * direction

    widgets = [
        (self.slot_left, self.slot_left.pos()),
        (self.slot_center, self.slot_center.pos()),
        (self.slot_right, self.slot_right.pos())
    ]

    for widget, start_pos in widgets:
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(300)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.setStartValue(start_pos)
        anim.setEndValue(QPoint(start_pos.x() - offset, start_pos.y()))
        anim_group.addAnimation(anim)

    def on_finished():
        # reset posisi widget
        for widget, start_pos in widgets:
            widget.move(start_pos)

        # update index setelah animasi
        if direction == 1:
            self.current_index = (self.current_index + 1) % len(self.images)
        else:
            self.current_index = (self.current_index - 1) % len(self.images)

        self.update_display()

    anim_group.finished.connect(on_finished)
    anim_group.start()
