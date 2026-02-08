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
        self.radius = 25
        self.border_color = "#313244"
        self.full_pixmap = None

    def set_image(self, path, border_color):
        self.border_color = border_color
        self.full_pixmap = QPixmap(path)
        self.update()

    def paintEvent(self, event):
        if not self.full_pixmap: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothTransformation)
        
        # Clip area rounded agar gambar tidak keluar border
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.setClipPath(path)
        
        # Render gambar mengikuti ukuran widget (GPU Scaling)
        painter.drawPixmap(self.rect(), self.full_pixmap)
        
        # Gambar Border
        painter.setClipping(False)
        is_focus = (self.border_color == "#00ffff")
        pen_width = 4 if is_focus else 2
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
        
        # KONFIGURASI UKURAN (Tengah dibuat dominan)
        self.size_side = QSize(380, 214)
        self.size_center = QSize(580, 326) 
        
        self.initUI()

    def get_active_wallpaper_index(self):
        try:
            result = subprocess.check_output(["swww", "query"], text=True)
            for line in result.splitlines():
                if "image:" in line:
                    p = line.split("image:")[1].strip()
                    if p in self.images: return self.images.index(p)
        except: pass
        return 0

    def initUI(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(1450, 700)

        mid_x, mid_y = self.width() // 2, self.height() // 2
        spacing = 460 

        # POSISI TARGET: Dihitung agar semua sejajar di garis tengah horizontal
        self.pos_targets = [
            QPoint(mid_x - spacing*2 - self.size_side.width()//2, mid_y - self.size_side.height()//2), 
            QPoint(mid_x - spacing - self.size_side.width()//2, mid_y - self.size_side.height()//2),   
            QPoint(mid_x - self.size_center.width()//2, mid_y - self.size_center.height()//2),         
            QPoint(mid_x + spacing - self.size_side.width()//2, mid_y - self.size_side.height()//2),   
            QPoint(mid_x + spacing*2 - self.size_side.width()//2, mid_y - self.size_side.height()//2)  
        ]

        self.slots = [RoundedImage(self) for _ in range(5)]
        
        self.name_label = QLabel(self)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("color: white; font-size: 22px; font-family: 'JetBrains Mono'; font-weight: bold;")
        self.name_label.setGeometry(0, 620, 1450, 50)

        self.refresh_ui()

    def refresh_ui(self):
        total = len(self.images)
        for i in range(5):
            idx = (self.current_index + (i - 2)) % total
            is_c = (i == 2)
            self.slots[i].set_image(self.images[idx], "#00ffff" if is_c else "#313244")
            self.slots[i].setFixedSize(self.size_center if is_c else self.size_side)
            self.slots[i].move(self.pos_targets[i])
            
            op = QGraphicsOpacityEffect(self.slots[i])
            op.setOpacity(0.0 if (i==0 or i==4) else (1.0 if is_c else 0.4))
            self.slots[i].setGraphicsEffect(op)

        self.name_label.setText(os.path.basename(self.images[self.current_index]))

    def animate(self, direction):
        if self.is_animating: return
        self.is_animating = True
        
        group = QParallelAnimationGroup(self)
        duration = 450
        curve = QEasingCurve.Type.OutQuart # Transisi premium dan halus

        if direction == "right":
            self.current_index = (self.current_index + 1) % len(self.images)
            self.slots.append(self.slots.pop(0))
        else:
            self.current_index = (self.current_index - 1) % len(self.images)
            self.slots.insert(0, self.slots.pop())

        for i in range(5):
            slot = self.slots[i]
            is_c = (i == 2)
            
            # Animasi Posisi
            pos_anim = QPropertyAnimation(slot, b"pos")
            pos_anim.setDuration(duration)
            pos_anim.setEndValue(self.pos_targets[i])
            pos_anim.setEasingCurve(curve)
            
            # Animasi Ukuran (Dynamic Zooming)
            size_anim = QPropertyAnimation(slot, b"size")
            size_anim.setDuration(duration)
            size_anim.setEndValue(self.size_center if is_c else self.size_side)
            size_anim.setEasingCurve(curve)

            group.addAnimation(pos_anim)
            group.addAnimation(size_anim)
            
            # Update visual (Opacity & Border)
            slot.border_color = "#00ffff" if is_c else "#313244"
            op = QGraphicsOpacityEffect(slot)
            op.setOpacity(0.0 if (i==0 or i==4) else (1.0 if is_c else 0.4))
            slot.setGraphicsEffect(op)

        group.finished.connect(self.on_finished)
        group.start()
        self.name_label.setText(os.path.basename(self.images[self.current_index]))

    def on_finished(self):
        total = len(self.images)
        # Update konten slot yang baru berotasi dari belakang layar
        self.slots[0].set_image(self.images[(self.current_index - 2) % total], "#313244")
        self.slots[4].set_image(self.images[(self.current_index + 2) % total], "#313244")
        self.is_animating = False

    def keyPressEvent(self, event):
        if self.is_animating: return
        if event.key() == Qt.Key.Key_Right: self.animate("right")
        elif event.key() == Qt.Key.Key_Left: self.animate("left")
        elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            subprocess.run(["swww", "img", self.images[self.current_index], "--transition-type", "grow"])
            self.close()
        elif event.key() == Qt.Key.Key_Escape: self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraCarousel()
    screen = app.primaryScreen().geometry()
    window.move((screen.width() - window.width()) // 2, (screen.height() - window.height()) // 2)
    window.show()
    sys.exit(app.exec())