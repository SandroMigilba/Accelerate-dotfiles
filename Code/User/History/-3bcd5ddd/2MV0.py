from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint, QParallelAnimationGroup, QTimer
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
        self.border_color = "#00ffff"
        self._pixmap = None

    def set_image(self, pixmap, border_color):
        self.border_color = border_color
        self._pixmap = pixmap
        self.update()

    def paintEvent(self, event):
        if not self._pixmap:
            return
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
        # Path gambar
        self.path = "/home/xeeukanbara/Pictures/wallpapers/"
        if not os.path.exists(self.path):
            self.path = os.path.expanduser("~/Pictures")

        # List images
        self.images = sorted([os.path.join(self.path, f) for f in os.listdir(self.path)
                              if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))])
        self.pixmap_cache = {}
        self.preload_range = 3  # total preload = 7

        # Animation / hold state
        self.animating = False
        self.hold_direction = 0
        self.hold_interval_start = 350
        self.hold_interval_min = 90
        self.hold_interval = self.hold_interval_start
        self.hold_accel_step = 25
        self.inertia_steps = 0

        # Timer untuk hold
        self.hold_timer = QTimer(self)
        self.hold_timer.setInterval(self.hold_interval_start)
        self.hold_timer.timeout.connect(self._hold_slide)

        # Deteksi wallpaper aktif
        self.current_index = self.get_active_wallpaper_index()

        # UI
        self.initUI()

    def get_active_wallpaper_index(self):
        try:
            result = subprocess.check_output(["swww", "query"], text=True)
            for line in result.splitlines():
                if "image:" in line:
                    current_path = line.split("image:")[1].strip()
                    if current_path in self.images:
                        return self.images.index(current_path)
        except:
            pass
        return 0

    # -----------------------------------
    # UI
    # -----------------------------------
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
        self.name_label.setStyleSheet(
            "color: #cdd6f4; font-size: 16px; font-family: 'JetBrains Mono'; font-weight: bold; margin-top: 30px;"
        )

        self.main_layout.addLayout(self.carousel_layout)
        self.main_layout.addWidget(self.name_label)
        self.setLayout(self.main_layout)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.activateWindow()
        self.setFocus()

        self.update_display()

    # -----------------------------------
    # Preload / Cache
    # -----------------------------------
    def preload_images(self):
        total = len(self.images)
        for i in range(-self.preload_range, self.preload_range + 1):
            idx = (self.current_index + i) % total
            path = self.images[idx]
            for size in (self.size_side, self.size_center):
                key = (path, size)
                if key not in self.pixmap_cache:
                    pix = QPixmap(path)
                    self.pixmap_cache[key] = pix.scaled(
                        size,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation
                    )

    def prune_cache(self):
        keep = set()
        total = len(self.images)
        for i in range(-self.preload_range, self.preload_range + 1):
            idx = (self.current_index + i) % total
            for size in (self.size_side, self.size_center):
                keep.add((self.images[idx], size))

        for key in list(self.pixmap_cache.keys()):
            if key not in keep:
                del self.pixmap_cache[key]

    # -----------------------------------
    # Update display
    # -----------------------------------
    def update_display(self):
        if not self.images:
            return

        total = len(self.images)
        idx_c = self.current_index
        idx_l = (idx_c - 1) % total
        idx_r = (idx_c + 1) % total

        self.preload_images()

        pix_l = self.pixmap_cache[(self.images[idx_l], self.size_side)]
        pix_c = self.pixmap_cache[(self.images[idx_c], self.size_center)]
        pix_r = self.pixmap_cache[(self.images[idx_r], self.size_side)]

        self.slot_left.set_image(pix_l, "#313244")
        self.slot_center.set_image(pix_c, "#00ffff")
        self.slot_right.set_image(pix_r, "#313244")

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

    # -----------------------------------
    # Slide animation
    # -----------------------------------
    def slide_animation(self, direction):
        if self.animating:
            return

        self.animating = True
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
            anim.setEasingCurve(self._current_easing())
            anim.setStartValue(start_pos)
            anim.setEndValue(QPoint(start_pos.x() - offset, start_pos.y()))
            anim_group.addAnimation(anim)

        def on_finished():
            for widget, start_pos in widgets:
                widget.move(start_pos)

            if direction == 1:
                self.current_index = (self.current_index + 1) % len(self.images)
            else:
                self.current_index = (self.current_index - 1) % len(self.images)

            self.prune_cache()
            self.update_display()
            self.animating = False

        anim_group.finished.connect(on_finished)
        anim_group.start()

    # -----------------------------------
    # Hold / acceleration / inertia
    # -----------------------------------
    def _hold_slide(self):
        if self.animating:
            return

        self.slide_animation(self.hold_direction)

        # acceleration
        self.hold_interval = max(
            self.hold_interval_min,
            self.hold_interval - self.hold_accel_step
        )
        self.hold_timer.setInterval(self.hold_interval)

    def _current_easing(self):
        if self.hold_interval > 260:
            return QEasingCurve.Type.OutCubic
        elif self.hold_interval > 160:
            return QEasingCurve.Type.OutQuart
        else:
            return QEasingCurve.Type.OutQuint

    def _run_inertia(self):
        if self.inertia_steps <= 0:
            return
        if not self.animating:
            self.slide_animation(self.hold_direction)
            self.inertia_steps -= 1
            QTimer.singleShot(120, self._run_inertia)

    # -----------------------------------
    # Events
    # -----------------------------------
    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        if event.key() == Qt.Key.Key_Right:
            self.hold_direction = 1
            self.hold_interval = self.hold_interval_start
            self.slide_animation(1)
            self.hold_timer.start(self.hold_interval)
        elif event.key() == Qt.Key.Key_Left:
            self.hold_direction = -1
            self.hold_interval = self.hold_interval_start
            self.slide_animation(-1)
            self.hold_timer.start(self.hold_interval)
        elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            subprocess.run([
                "swww", "img",
                self.images[self.current_index],
                "--transition-type", "outer",
                "--transition-duration", "0.8"
            ])
            self.close()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()

    def keyReleaseEvent(self, event):
        if event.isAutoRepeat():
            return
        if event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right):
            self.hold_timer.stop()
            if self.hold_interval < 200:
                self.inertia_steps = 2
            elif self.hold_interval < 280:
                self.inertia_steps = 1
            else:
                self.inertia_steps = 0
            self.hold_interval = self.hold_interval_start
            self._run_inertia()

    def wheelEvent(self, event):
        delta = event.angleDelta().x() or event.angleDelta().y()
        if delta < 0:
            self.slide_animation(1)
        elif delta > 0:
            self.slide_animation(-1)
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraCarousel()
    geo = app.primaryScreen().geometry()
    window.move((geo.width() - window.width()) // 2, (geo.height() - window.height()) // 2)
    window.show()
    sys.exit(app.exec())
