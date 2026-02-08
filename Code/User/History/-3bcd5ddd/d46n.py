import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, 
                             QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup

class RoundedImage(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.radius = 20
        self.border_color = "#313244"
        self.setScaledContents(True) # Optimasi hardware scaling

    def set_image(self, path, size, border_color):
        self.border_color = border_color
        pix = QPixmap(path)
        # Gunakan ukuran center sebagai basis agar tidak pecah saat membesar
        scaled_pix = pix.scaled(QSize(500, 281), Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                 Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(scaled_pix)
        self.setFixedSize(size)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Gambar Rounded Border
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.setPen(QColor(self.border_color))
        painter.drawRoundedRect(0, 0, self.width()-1, self.height()-1, self.radius, self.radius)

class NobaraCarousel(QWidget):
    def __init__(self):
        super().__init__()
        # Path detection
        self.path = "/home/xeeukanbara/Pictures/wallpapers/"
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
                    path = line.split("image:")[1].strip()
                    if path in self.images: return self.images.index(path)
        except: pass
        return 0

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(1450, 650)

        # Definisi Ukuran & Posisi Target
        self.size_side = QSize(400, 225)
        self.size_center = QSize(480, 270)
        
        mid_x, mid_y = self.width() // 2, self.height() // 2
        spacing = 450 # Jarak antar gambar

        self.pos_targets = [
            QPoint(mid_x - spacing*2 - 200, mid_y - 112), # Buffer Kiri (Hidden)
            QPoint(mid_x - spacing - 200, mid_y - 112),   # Slot Kiri
            QPoint(mid_x - 240, mid_y - 135),             # Slot Tengah
            QPoint(mid_x + spacing - 200, mid_y - 112),   # Slot Kanan
            QPoint(mid_x + spacing*2 - 200, mid_y - 112)  # Buffer Kanan (Hidden)
        ]

        # Inisialisasi 5 Slot (3 terlihat, 2 sebagai buffer transisi)
        self.slots = [RoundedImage(self) for _ in range(5)]
        
        self.name_label = QLabel(self)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("color: #cdd6f4; font-size: 20px; font-family: 'JetBrains Mono'; font-weight: bold;")
        self.name_label.setGeometry(0, 550, 1450, 50)

        self.refresh_content()

    def refresh_content(self):
        total = len(self.images)
        for i in range(5):
            idx = (self.current_index + (i - 2)) % total
            size = self.size_center if i == 2 else self.size_side
            color = "#00ffff" if i == 2 else "#313244"
            
            self.slots[i].set_image(self.images[idx], size, color)
            self.slots[i].move(self.pos_targets[i])
            
            # Atur Opacity: Buffer 0.0, Samping 0.6, Tengah 1.0
            op = QGraphicsOpacityEffect(self.slots[i])
            op.setOpacity(0.0 if (i==0 or i==4) else (1.0 if i==2 else 0.6))
            self.slots[i].setGraphicsEffect(op)

        self.name_label.setText(os.path.basename(self.images[self.current_index]))

    def animate_slide(self, direction):
        if self.is_animating: return
        self.is_animating = True
        
        self.anim_group = QParallelAnimationGroup()
        duration = 380 # Durasi optimal untuk kehalusan
        curve = QEasingCurve.Type.OutQuart # Gerakan premium (cepat lalu melambat halus)

        if direction == "right":
            self.current_index = (self.current_index + 1) % len(self.images)
            self.slots.append(self.slots.pop(0)) # Putar slot
        else:
            self.current_index = (self.current_index - 1) % len(self.images)
            self.slots.insert(0, self.slots.pop())

        for i in range(5):
            slot = self.slots[i]
            
            # 1. Animasi Posisi
            pos_anim = QPropertyAnimation(slot, b"pos")
            pos_anim.setDuration(duration)
            pos_anim.setEndValue(self.pos_targets[i])
            pos_anim.setEasingCurve(curve)
            
            # 2. Animasi Ukuran
            size_anim = QPropertyAnimation(slot, b"size")
            size_anim.setDuration(duration)
            size_anim.setEndValue(self.size_center if i == 2 else self.size_side)
            size_anim.setEasingCurve(curve)

            self.anim_group.addAnimation(pos_anim)
            self.anim_group.addAnimation(size_anim)
            
            # Update Visual (Border & Opacity)
            slot.border_color = "#00ffff" if i == 2 else "#313244"
            op = QGraphicsOpacityEffect(slot)
            op.setOpacity(0.0 if (i==0 or i==4) else (1.0 if i==2 else 0.6))
            slot.setGraphicsEffect(op)

        self.anim_group.finished.connect(self.on_anim_finished)
        self.anim_group.start()
        self.name_label.setText(os.path.basename(self.images[self.current_index]))

    def on_anim_finished(self):
        # Update konten gambar pada slot buffer yang baru masuk
        total = len(self.images)
        self.slots[0].set_image(self.images[(self.current_index - 2) % total], self.size_side, "#313244")
        self.slots[4].set_image(self.images[(self.current_index + 2) % total], self.size_side, "#313244")
        self.is_animating = False

    def keyPressEvent(self, event):
        if self.is_animating: return
        
        if event.key() == Qt.Key.Key_Right:
            self.animate_slide("right")
        elif event.key() == Qt.Key.Key_Left:
            self.animate_slide("left")
        elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            subprocess.run(["swww", "img", self.images[self.current_index], "--transition-type", "grow"])
            self.close()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraCarousel()
    screen = app.primaryScreen().geometry()
    window.move((screen.width() - window.width()) // 2, (screen.height() - window.height()) // 2)
    window.show()
    sys.exit(app.exec())