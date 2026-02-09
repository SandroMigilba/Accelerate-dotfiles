import sys, os, subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QLabel,
    QVBoxLayout, QGraphicsOpacityEffect
)
from PyQt6.QtGui import (
    QPixmap, QImage, QColor, QPainter, QPainterPath
)
from PyQt6.QtCore import (
    Qt, QSize, QPropertyAnimation,
    QParallelAnimationGroup, QThread, pyqtSignal
)

# ================= THREAD IMAGE LOADER =================
class ImageLoader(QThread):
    loaded = pyqtSignal(int, QImage, str, int)

    def __init__(self, index, path, size):
        super().__init__()
        self.index = index
        self.path = path
        self.size = size

    def run(self):
        img = QImage(self.path)
        if img.isNull():
            return

        scaled = img.scaled(
            self.size,
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        self.loaded.emit(self.index, scaled, self.path, self.size.width())


# ================= ROUNDED IMAGE =================
class RoundedImage(QLabel):
    def __init__(self, radius=20, parent=None):
        super().__init__(parent)
        self.radius = radius
        self.border_color = QColor(255, 255, 255, 40)
        self._pixmap = None

        eff = QGraphicsOpacityEffect(self)
        eff.setOpacity(1.0)
        self.setGraphicsEffect(eff)

    def set_image(self, pixmap, border_hex):
        self.border_color = QColor(border_hex)
        self._pixmap = pixmap
        self.update()

    def paintEvent(self, event):
        if not self._pixmap:
            return

        p = QPainter(self)
        p.setRenderHints(
            QPainter.RenderHint.Antialiasing |
            QPainter.RenderHint.SmoothPixmapTransform
        )

        rect = self.rect().toRectF()
        path = QPainterPath()
        path.addRoundedRect(rect, self.radius, self.radius)

        p.setClipPath(path)
        p.drawPixmap(self.rect(), self._pixmap)

        p.setClipping(False)
        p.setPen(self.border_color)
        p.drawRoundedRect(rect.adjusted(0, 0, -1, -1),
                          self.radius, self.radius)


# ================= MAIN UI =================
class NobaraCarousel(QWidget):
    def __init__(self):
        super().__init__()

        wp = os.path.expanduser("~/Pictures/wallpapers/")
        self.base_path = wp if os.path.exists(wp) else os.path.expanduser("~/Pictures")

        valid = ('.png', '.jpg', '.jpeg', '.webp')
        self.images = sorted(
            os.path.join(self.base_path, f)
            for f in os.listdir(self.base_path)
            if f.lower().endswith(valid)
        )

        self.cache = {}
        self._workers = set()
        self.animating = False
        self.current_index = self.get_active_wallpaper_index()

        self.initUI()
        self.update_display()

    def get_active_wallpaper_index(self):
        try:
            res = subprocess.check_output(["swww", "query"], text=True)
            path = res.split("image:")[-1].strip()
            return self.images.index(path) if path in self.images else 0
        except Exception:
            return 0

    def initUI(self):
        # --- UPDATE IDENTITAS WINDOW ---
        self.setWindowTitle("Choose Wallpaper") # Muncul di Title Bar/Waybar
        self.setObjectName("choose-wallpaper")  # Class Name (App ID) untuk Waybar
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(1400, 600)

        main = QVBoxLayout(self)
        main.setContentsMargins(0, 100, 0, 0)
        main.setSpacing(20)

        row = QHBoxLayout()
        row.setSpacing(30)

        self.sizes = [QSize(380, 210), QSize(480, 270), QSize(380, 210)]
        self.slots = [RoundedImage() for _ in range(3)]

        for s, size in zip(self.slots, self.sizes):
            s.setFixedSize(size)
            row.addWidget(s, alignment=Qt.AlignmentFlag.AlignCenter)

        self.name_label = QLabel(alignment=Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet(
            "color: rgba(255,255,255,0.8);"
            "font-size: 16px;"
            "font-family: 'JetBrains Mono';"
        )

        main.addLayout(row)
        main.addWidget(self.name_label)

    # ================= UPDATE DISPLAY =================
    def update_display(self):
        if not self.images:
            return

        total = len(self.images)
        indices = [(self.current_index + i) % total for i in (-1, 0, 1)]
        self.name_label.setText(os.path.basename(self.images[self.current_index]))

        for slot_idx, img_idx in enumerate(indices):
            path = self.images[img_idx]
            size = self.sizes[slot_idx]
            border = "#ffffff" if slot_idx == 1 else "#444444"
            key = (path, size.width())

            if key in self.cache:
                self.slots[slot_idx].set_image(self.cache[key], border)
                continue

            worker = ImageLoader(slot_idx, path, size)
            self._workers.add(worker)

            worker.loaded.connect(self.on_image_loaded)
            worker.finished.connect(lambda w=worker: self._workers.discard(w))
            worker.finished.connect(worker.deleteLater)
            worker.start()

    def on_image_loaded(self, slot_idx, image, path, width):
        pixmap = QPixmap.fromImage(image)
        self.cache[(path, width)] = pixmap

        border = "#ffffff" if slot_idx == 1 else "#444444"
        self.slots[slot_idx].set_image(pixmap, border)

        if len(self.cache) > 40:
            for _ in range(10):
                self.cache.pop(next(iter(self.cache)))

    # ================= ANIMATION =================
    def run_fade(self, direction):
        if self.animating:
            return
        self.animating = True

        out = QParallelAnimationGroup(self)
        for s in self.slots:
            a = QPropertyAnimation(s.graphicsEffect(), b"opacity")
            a.setDuration(120)
            a.setEndValue(0.2)
            out.addAnimation(a)

        def swap():
            self.current_index = (self.current_index + direction) % len(self.images)
            self.update_display()

            inn = QParallelAnimationGroup(self)
            for s in self.slots:
                a = QPropertyAnimation(s.graphicsEffect(), b"opacity")
                a.setDuration(150)
                a.setEndValue(1.0)
                inn.addAnimation(a)

            inn.finished.connect(lambda: setattr(self, "animating", False))
            inn.start()

        out.finished.connect(swap)
        out.start()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Right:
            self.run_fade(1)
        elif e.key() == Qt.Key.Key_Left:
            self.run_fade(-1)
        elif e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            subprocess.Popen([
                "swww", "img", self.images[self.current_index],
                "--transition-type", "grow",
                "--transition-fps", "60"
            ])
            self.close()
        elif e.key() == Qt.Key.Key_Escape:
            self.close()


# ================= ENTRY =================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # --- UPDATE METADATA APLIKASI ---
    app.setApplicationName("Choose Wallpaper")
    app.setDesktopFileName("choose-wallpaper") # Sesuai dengan nama file .desktop kamu
    
    w = NobaraCarousel()

    geo = w.frameGeometry()
    cp = app.primaryScreen().availableGeometry().center()
    geo.moveCenter(cp)
    w.move(geo.topLeft())

    w.show()
    sys.exit(app.exec())
