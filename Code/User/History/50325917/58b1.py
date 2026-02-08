import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt, QSize

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
        # Window Setup: Frameless & Translucent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(1200, 550)

        # Layout Utama
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Container Carousel
        self.carousel_layout = QHBoxLayout()
        self.carousel_layout.setSpacing(50)
        self.carousel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Inisialisasi Slot
        self.slot_left = QLabel()
        self.slot_center = QLabel()
        self.slot_right = QLabel()

        # Konfigurasi Dimensi & Shadow
        self.setup_slot(self.slot_left, 320, 180, False)
        self.setup_slot(self.slot_center, 640, 360, True) # Center lebih besar
        self.setup_slot(self.slot_right, 320, 180, False)

        self.carousel_layout.addWidget(self.slot_left)
        self.carousel_layout.addWidget(self.slot_center)
        self.carousel_layout.addWidget(self.slot_right)

        # Label Nama File (Style Floating)
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("""
            color: #cdd6f4; 
            font-size: 18px; 
            font-family: 'JetBrains Mono', sans-serif;
            font-weight: bold;
            padding: 10px;
        """)

        self.main_layout.addLayout(self.carousel_layout)
        self.main_layout.addWidget(self.name_label)
        self.setLayout(self.main_layout)

        self.update_display()

    def setup_slot(self, label, w, h, is_center):
        label.setFixedSize(w, h)
        label.setScaledContents(True)
        
        # Tambahkan efek bayangan (Drop Shadow)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25 if is_center else 15)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 180))
        label.setGraphicsEffect(shadow)

    def render_image(self, label, path, is_center):
        pixmap = QPixmap(path)
        # Style Border: Pink untuk center, Abu-abu gelap untuk samping
        border_color = "#f5c2e7" if is_center else "#313244"
        opacity = "1.0" if is_center else "0.4" # Gambar samping dibuat agak pudar
        
        label.setStyleSheet(f"""
            border: 4px solid {border_color}; 
            border-radius: 20px; 
            background-color: #000;
            opacity: {opacity};
        """)
        
        label.setPixmap(pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                     Qt.TransformationMode.SmoothTransformation))

    def update_display(self):
        if not self.images: return
        
        total = len(self.images)
        idx_c = self.current_index
        idx_l = (idx_c - 1) % total
        idx_r = (idx_c + 1) % total

        self.render_image(self.slot_left, self.images[idx_l], False)
        self.render_image(self.slot_center, self.images[idx_c], True)
        self.render_image(self.slot_right, self.images[idx_r], False)

        # Format nama file agar tidak terlalu panjang
        filename = os.path.basename(self.images[idx_c])
        self.name_label.setText(filename if len(filename) < 40 else filename[:37] + "...")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Right:
            self.current_index = (self.current_index + 1) % len(self.images)
            self.update_display()
        elif event.key() == Qt.Key.Key_Left:
            self.current_index = (self.current_index - 1) % len(self.images)
            self.update_display()
        elif event.key() in [Qt.Key.Key_Return, Qt.Key.Key_Enter]:
            self.apply_wallpaper()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()

    def apply_wallpaper(self):
        # Menggunakan transisi 'outer' agar terlihat meledak dari tengah
        subprocess.run([
            "swww", "img", self.images[self.current_index],
            "--transition-type", "outer",
            "--transition-pos", "0.5,0.5",
            "--transition-step", "90",
            "--transition-duration", "1.5"
        ])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraCarousel()
    # Memposisikan window tepat di tengah layar
    screen = app.primaryScreen().geometry()
    window.move((screen.width() - window.width()) // 2, (screen.height() - window.height()) // 2)
    window.show()
    sys.exit(app.exec())