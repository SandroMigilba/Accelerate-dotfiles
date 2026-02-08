import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, 
                             QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPainterPath
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup, pyqtProperty

class RoundedImage(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.radius = 20
        self.border_color = "#313244"
        self._pixmap = None
        self._current_path = ""

    # Property khusus untuk animasi resize agar smooth
    @pyqtProperty(QSize)
    def widgetSize(self):
        return self.size()

    @widgetSize.setter
    def widgetSize(self, size):
        self.setFixedSize(size)
        if self._current_path:
            self.update_pixmap(size)

    def set_image(self, path, size, border_color):
        self._current_path = path
        self.border_color = border_color
        self.setFixedSize(size)
        self.update_pixmap(size)

    def update_pixmap(self, size):
        if not self._current_path: return
        pix = QPixmap(self._current_path)
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

        # Konfigurasi Ukuran
        self.size_side = QSize(400, 225)
        self.size_center = QSize(500, 281) # Lebih besar di tengah
        
        mid_x, mid_y = self.width() // 2, self.height() // 2
        spacing = 480 

        # Daftar Posisi Target (Titik Tengah)
        self.targets = [
            {"pos": QPoint(mid_x - spacing*2 - self.size_side.width()//2, mid_y - self.size_side.height()//2), "size": self.size_side, "op": 0.0},
            {"pos": QPoint(mid_x - spacing - self.size_side.width()//2, mid_y - self.size_side.height()//2), "size": self.size_side, "op": 0.5},
            {"pos": QPoint(mid_x - self.size_center.width()//2, mid_y - self.size_center.height()//2), "size": self.size_center, "op": 1.0},
            {"pos": QPoint(mid_x + spacing - self.size_side.width()//2, mid_y - self.size_side.height()//2), "size": self.size_side, "op": 0.5},
            {"pos": QPoint(mid_x + spacing*2 - self.size_side.width()//2, mid_y - self.size_side.height()//2), "size": self.size_side, "op": 0.0}
        ]

        # Inisialisasi 5 Slot
        self.slots = [RoundedImage(self) for _ in range(5)]
        
        self.name_label = QLabel(self)
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setFixedWidth(self.width())
        self.name_label.move(0, self.height() - 100)
        self.name_label.setStyleSheet("color: #cdd6f4; font-size: 22px; font-family: 'JetBrains Mono'; font-weight: bold;")

        self.setup_initial_state()

    def setup_initial_state(self):
        total = len(self.images)
        for i in range(5):
            idx = (self.current_index + (i - 2)) % total
            color = "#00ffff" if i == 2 else "#313244"
            self.slots[i].set_image(self.images[idx], self.targets[i]["size"], color)
            self.slots[i].move(self.targets[i]["pos"])
            
            op = QGraphicsOpacityEffect(self.slots[i])
            op.setOpacity(self.targets[i]["op"])
            self.slots[i].setGraphicsEffect(op)
            
            if i == 2: self.apply_shadow(self.slots[i])
        
        self.name_label.setText(os.path.basename(self.images[self.current_index]))

    def apply_shadow(self, widget):
        shadow = QGraphicsDropShadowEffect(widget)
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 255, 255, 120))
        widget.setGraphicsEffect(shadow)

    def animate_slide(self, direction):
        if self.is_animating: return
        self.is_animating = True
        
        self.group = QParallelAnimationGroup()
        duration = 450
        easing = QEasingCurve.Type.OutExpo # Animasi lebih "snappy"

        # Tentukan indeks baru
        if direction == "right":
            self.current_index = (self.current_index + 1) % len(self.images)
            slot_indices = [1, 2, 3, 4, 0] # Geser ke kiri
        else:
            self.current_index = (self.current_index - 1) % len(self.images)
            slot_indices = [4, 0, 1, 2, 3] # Geser ke kanan

        for i in range(5):
            slot = self.slots[i]
            target_idx = slot_indices[i]
            target_data = self.targets[target_idx]

            # Animasi Posisi
            pos_anim = QPropertyAnimation(slot, b"pos")
            pos_anim.setDuration(duration)
            pos_anim.setEndValue(target_data["pos"])
            pos_anim.setEasingCurve(easing)
            
            # Animasi Ukuran (menggunakan property widgetSize yang dibuat di atas)
            size_anim = QPropertyAnimation(slot, b"widgetSize")
            size_anim.setDuration(duration)
            size_anim.setEndValue(target_data["size"])
            size_anim.setEasingCurve(easing)

            self.group.addAnimation(pos_anim)
            self.group.addAnimation(size_anim)

            # Border update di tengah animasi
            slot.border_color = "#00ffff" if target_idx == 2 else "#313244"

        self.group.finished.connect(self.on_animation_finished)
        self.group.start()
        self.name_label.setText(os.path.basename(self.images[self.current_index]))

    def on_animation_finished(self):
        # Menyusun ulang list slots agar sesuai dengan posisi fisiknya sekarang
        # Ini penting agar siklus berikutnya tetap konsisten
        new_slots = [None] * 5
        for slot in self.slots:
            # Cari slot ini sekarang ada di posisi target mana
            for i in range(5):
                if slot.pos() == self.targets[i]["pos"]:
                    new_slots[i] = slot
        
        self.slots = new_slots
        
        # Update konten untuk slot yang baru masuk (indeks 0 dan 4)
        total = len(self.images)
        self.slots[0].set_image(self.images[(self.current_index - 2) % total], self.size_side, "#313244")
        self.slots[4].set_image(self.images[(self.current_index + 2) % total], self.size_side, "#313244")
        
        # Refresh Opacity dan Shadow
        for i in range(5):
            op = QGraphicsOpacityEffect(self.slots[i])
            op.setOpacity(self.targets[i]["op"])
            self.slots[i].setGraphicsEffect(op)
            if i == 2: self.apply_shadow(self.slots[i])

        self.is_animating = False

    def keyPressEvent(self, event):
        if self.is_animating: return
        if event.key() == Qt.Key.Key_Right: self.animate_slide("right")
        elif event.key() == Qt.Key.Key_Left: self.animate_slide("left")
        elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            subprocess.run(["swww", "img", self.images[self.current_index], "--transition-type", "outer"])
            self.close()
        elif event.key() == Qt.Key.Key_Escape: self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraCarousel()
    geo = app.primaryScreen().geometry()
    window.move((geo.width() - window.width()) // 2, (geo.height() - window.height()) // 2)
    window.show()
    sys.exit(app.exec())