import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, 
                             QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, QRect

class RoundedImage(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.radius = 20
        self.border_color = "#313244"
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
        self.path = os.path.expanduser("~/Pictures/wallpapers/")
        if not os.path.exists(self.path):
            self.path = os.path.expanduser("~/Pictures")

        self.images = sorted([os.path.join(self.path, f) for f in os.listdir(self.path) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))])
        
        self.current_index = self.get_active_wallpaper_index()
        self.is_animating = False
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

        # Definisi Ukuran dan Posisi
        self.size_side = QSize(400, 225)
        self.size_center = QSize(440, 248)
        
        mid_x = self.width() // 2
        mid_y = self.height() // 2
        spacing = 460 

        # Posisi Target
        self.pos_left = QPoint(mid_x - spacing - self.size_side.width()//2, mid_y - self.size_side.height()//2)
        self.pos_center = QPoint(mid_x - self.size_center.width()//2, mid_y - self.size_center.height()//2)
        self.pos_right = QPoint(mid_x + spacing - self.size_side.width()//2, mid_y - self.size_side.height()//2)
        
        # Posisi Hidden (untuk animasi masuk/keluar)
        self.pos_far_left = QPoint(self.pos_left.x() - spacing, self.pos_left.y())
        self.pos_far_right = QPoint(self.pos_right.x() + spacing, self.pos_right.y())

        # Membuat 5 Slot untuk transisi seamless
        self.slots = [RoundedImage(self) for _ in range(5)]
        for s in self.slots: s.hide()

        self.name_label = QLabel(self)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setFixedWidth(self.width())
        self.name_label.move(0, self.pos_center.y() + self.size_center.height() + 40)
        self.name_label.setStyleSheet("color: #cdd6f4; font-size: 20px; font-family: 'JetBrains Mono'; font-weight: bold;")

        self.update_slots_content()

    def update_slots_content(self):
        total = len(self.images)
        indices = [
            (self.current_index - 2) % total,
            (self.current_index - 1) % total,
            self.current_index,
            (self.current_index + 1) % total,
            (self.current_index + 2) % total
        ]
        
        positions = [self.pos_far_left, self.pos_left, self.pos_center, self.pos_right, self.pos_far_right]
        sizes = [self.size_side, self.size_side, self.size_center, self.size_side, self.size_side]

        for i in range(5):
            slot = self.slots[i]
            color = "#00ffff" if i == 2 else "#313244"
            slot.set_image(self.images[indices[i]], sizes[i], color)
            slot.setFixedSize(sizes[i])
            slot.move(positions[i])
            slot.show()
            
            # Opacity
            op = QGraphicsOpacityEffect(slot)
            op.setOpacity(1.0 if i == 2 else 0.5)
            slot.setGraphicsEffect(op)
            
            # Shadow hanya untuk tengah
            if i == 2:
                shadow = QGraphicsDropShadowEffect(slot)
                shadow.setBlurRadius(30)
                shadow.setColor(QColor(0, 255, 255, 150))
                slot.setGraphicsEffect(shadow)
        
        self.name_label.setText(os.path.basename(self.images[self.current_index]))

    def animate_slide(self, direction):
        if self.is_animating: return
        self.is_animating = True
        
        duration = 400
        easing = QEasingCurve.Type.OutCubic
        self.anims = []

        # Tentukan urutan pergeseran
        if direction == "right": # Klik Panah Kanan -> Gambar geser ke Kiri
            targets = [None, self.pos_far_left, self.pos_left, self.pos_center, self.pos_right]
            self.current_index = (self.current_index + 1) % len(self.images)
        else: # Klik Panah Kiri -> Gambar geser ke Kanan
            targets = [self.pos_left, self.pos_center, self.pos_right, self.pos_far_right, None]
            self.current_index = (self.current_index - 1) % len(self.images)

        for i in range(5):
            if targets[i] is None:
                self.slots[i].hide()
                continue
            
            anim = QPropertyAnimation(self.slots[i], b"pos")
            anim.setDuration(duration)
            anim.setStartValue(self.slots[i].pos())
            anim.setEndValue(targets[i])
            anim.setEasingCurve(easing)
            self.anims.append(anim)
            anim.start()

        # Timer untuk update konten setelah animasi selesai
        self.anims[0].finished.connect(self.on_animation_finished)

    def on_animation_finished(self):
        self.update_slots_content()
        self.is_animating = False

    def keyPressEvent(self, event):
        if self.is_animating: return
        
        if event.key() == Qt.Key.Key_Right:
            self.animate_slide("right")
        elif event.key() == Qt.Key.Key_Left:
            self.animate_slide("left")
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