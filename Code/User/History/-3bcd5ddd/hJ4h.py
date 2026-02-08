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
        # Menghapus setScaledContents(True) dan menggunakan paintEvent custom 
        # agar scaling gambar mengikuti ukuran widget dengan kualitas tinggi
        self._pixmap = None

    def set_image(self, path, border_color):
        self.border_color = border_color
        self._pixmap = QPixmap(path)
        self.update()

    def paintEvent(self, event):
        if not self._pixmap: return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothTransformation)
        
        # Clip area rounded
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), self.radius, self.radius)
        painter.setClipPath(path)
        
        # Gambar pixmap mengikuti ukuran widget saat ini (dinamis)
        painter.drawPixmap(0, 0, self.width(), self.height(), self._pixmap)
        
        # Gambar Border
        painter.setClipping(False)
        pen_width = 4 if self.border_color == "#00ffff" else 2
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
        
        # UKURAN TARGET
        self.size_side = QSize(400, 225)
        self.size_center = QSize(580, 326) # Jauh lebih besar
        
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
        self.setFixedSize(1450, 750)

        mid_x, mid_y = self.width() // 2, self.height() // 2
        spacing = 480 

        # POSISI TARGET (Dihitung berdasarkan center point agar simetris)
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
        self.name_label.setStyleSheet("color: white; font-size: 24px; font-family: 'JetBrains Mono'; font-weight: bold;")
        self.name_label.setGeometry(0, 600, 1450, 50)

        self.refresh_ui()

    def refresh_ui(self):
        total = len(self.images)
        for i in range(5):
            idx = (self.current_index + (i - 2)) % total
            is_center = (i == 2)
            
            size = self.size_center if is_center else self.size_side
            color = "#00ffff" if is_center else "#313244"
            
            self.slots[i].set_image(self.images[idx], color)
            self.slots[i].setFixedSize(size)
            self.slots[i].move(self.pos_targets[i])
            
            op = QGraphicsOpacityEffect(self.slots[i])
            op.setOpacity(0.0 if (i==0 or i==4) else (1.0 if is_center else 0.5))
            self.slots[i].setGraphicsEffect(op)

        self.name_label.setText(os.path.basename(self.images[self.current_index]))

    def animate(self, direction):
        if self.is_animating: return
        self.is_animating = True
        
        self.anim_group = QParallelAnimationGroup()
        duration = 500 # Sedikit lebih lama agar transisi zoom terlihat jelas
        curve = QEasingCurve.Type.OutQuart

        # Logika pergeseran list widget
        if direction == "right":
            self.current_index = (self.current_index + 1) % len(self.images)
            self.slots.append(self.slots.pop(0))
        else:
            self.current_index = (self.current_index - 1) % len(self.images)
            self.slots.insert(0, self.slots.pop())

        for i in range(5):
            slot = self.slots[i]
            is_center = (i == 2)
            target_size = self.size_center if is_center else self.size_side
            target_pos = self.pos_targets[i]

            # 1. Animasi Posisi
            pos_anim = QPropertyAnimation(slot, b"pos")
            pos_anim.setDuration(duration)
            pos_anim.setEndValue(target_pos)
            pos_anim.setEasingCurve(curve)
            
            # 2. Animasi Ukuran (Zooming effect)
            size_anim = QPropertyAnimation(slot, b"size")
            size_anim.setDuration(duration)
            size_anim.setEndValue(target_size)
            size_anim.setEasingCurve(curve)

            self.anim_group.addAnimation(pos_anim)
            self.anim_group.addAnimation(size_anim)
            
            # Update border dan opacity secara instan agar mengikuti aliran
            slot.border_color = "#00ffff" if is_center else "#313244"
            op = QGraphicsOpacityEffect(slot)
            op.setOpacity(0.0 if (i==0 or i==4) else (1.0 if is_center else 0.5))
            slot.setGraphicsEffect(op)

        self.anim_group.finished.connect(self.on_finished)
        self.anim_group.start()
        self.name_label.setText(os.path.basename(self.images[self.current_index]))

    def on_finished(self):
        total = len(self.images)
        # Update gambar pada slot buffer yang baru berotasi
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