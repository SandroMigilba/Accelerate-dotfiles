import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QHBoxLayout, QLabel, 
                             QVBoxLayout, QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QVariantAnimation

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
        # Menggunakan lebar/tinggi widget sebenarnya untuk scaling agar halus
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
        
        # Gambar pixmap di tengah
        x = (self.width() - self._pixmap.width()) // 2
        y = (self.height() - self._pixmap.height()) // 2
        painter.drawPixmap(x, y, self._pixmap)
        
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
        
        self.current_index = self.get_active_wallpaper_index()
        self.is_animating = False # Lock untuk mencegah spam key
        self.initUI()

    def get_active_wallpaper_index(self):
        try:
            result = subprocess.check_output(["swww", "query"], text=True)
            for line in result.splitlines():
                if "image:" in line:
                    current_path = line.split("image:")[1].strip()
                    if current_path in self.images:
                        return self.images.index(current_path)
        except: pass
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

        for slot in [self.slot_left, self.slot_center, self.slot_right]:
            slot.setFixedSize(self.size_side)

        self.carousel_layout.addWidget(self.slot_left)
        self.carousel_layout.addWidget(self.slot_center)
        self.carousel_layout.addWidget(self.slot_right)

        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("color: #cdd6f4; font-size: 18px; font-family: 'JetBrains Mono'; font-weight: bold; margin-top: 30px;")

        self.main_layout.addLayout(self.carousel_layout)
        self.main_layout.addWidget(self.name_label)
        self.setLayout(self.main_layout)
        
        # Inisialisasi animasi
        self.animation = QVariantAnimation(self)
        self.animation.setDuration(300) # Durasi slide (ms)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.animation.valueChanged.connect(self.animate_transition)
        self.animation.finished.connect(self.finish_animation)

        self.update_display()

    def update_display(self):
        total = len(self.images)
        idx_c = self.current_index
        idx_l = (idx_c - 1) % total
        idx_r = (idx_c + 1) % total

        self.slot_left.set_image(self.images[idx_l], self.size_side, "#313244")
        self.slot_center.set_image(self.images[idx_c], self.size_center, "#00ffff")
        self.slot_right.set_image(self.images[idx_r], self.size_side, "#313244")
        
        self.slot_center.setFixedSize(self.size_center)
        self.apply_effects(1.0) # Reset effects
        self.name_label.setText(os.path.basename(self.images[idx_c]))

    def apply_effects(self, progress):
        # Progress 1.0 berarti center sedang fokus penuh
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 255, 255, int(100 * progress)))
        shadow.setYOffset(5)
        self.slot_center.setGraphicsEffect(shadow)

        for slot in [self.slot_left, self.slot_right]:
            op = QGraphicsOpacityEffect()
            op.setOpacity(0.5 + (0.5 * (1 - progress)))
            slot.setGraphicsEffect(op)

    def start_slide_animation(self, direction):
        if self.is_animating: return
        self.is_animating = True
        self.direction = direction # 1 untuk kanan, -1 untuk kiri
        
        # Animasi dari 0 ke 1
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

    def animate_transition(self, value):
        # Efek visual sederhana saat bergeser: sedikit mengubah opacity/skala
        # Untuk slide yang benar-benar bergerak posisi, kita bisa memanipulasi margin/spacing
        offset = value * 20 * self.direction
        self.carousel_layout.setContentsMargins(int(-offset), 0, int(offset), 0)
        self.apply_effects(1.0 - value)

    def finish_animation(self):
        self.current_index = (self.current_index + self.direction) % len(self.images)
        self.carousel_layout.setContentsMargins(0, 0, 0, 0)
        self.update_display()
        self.is_animating = False

    def keyPressEvent(self, event):
        if self.is_animating: return
        
        if event.key() == Qt.Key.Key_Right:
            self.start_slide_animation(1)
        elif event.key() == Qt.Key.Key_Left:
            self.start_slide_animation(-1)
        elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            subprocess.run(["swww", "img", self.images[self.current_index], "--transition-type", "outer"])
            self.close()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraCarousel()
    geo = app.primaryScreen().geometry()
    window.move((geo.width() - window.width()) // 2, (geo.height() - window.height()) // 2)
    window.show()
    sys.exit(app.exec())