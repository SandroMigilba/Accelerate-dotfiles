import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt

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
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Window diperlebar sedikit untuk ruang spacing yang lebih baik
        self.setFixedSize(1300, 600)

        # Layout Utama
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Container Carousel dengan SPACING ANTAR GAMBAR
        self.carousel_layout = QHBoxLayout()
        self.carousel_layout.setSpacing(60) # <-- ATUR JARAK ANTAR GAMBAR DI SINI (Default: 60)
        self.carousel_layout.setContentsMargins(50, 0, 50, 0) # Margin kanan-kiri jendela
        self.carousel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Inisialisasi Slot
        self.slot_left = QLabel()
        self.slot_center = QLabel()
        self.slot_right = QLabel()

        # Konfigurasi Dimensi
        self.setup_slot(self.slot_left, 300, 168, False)
        self.setup_slot(self.slot_center, 640, 360, True) 
        self.setup_slot(self.slot_right, 300, 168, False)

        self.carousel_layout.addWidget(self.slot_left)
        self.carousel_layout.addWidget(self.slot_center)
        self.carousel_layout.addWidget(self.slot_right)

        # Label Nama File
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("""
            color: #cdd6f4; 
            font-size: 18px; 
            font-family: 'JetBrains Mono', 'Sans';
            font-weight: bold;
            margin-top: 20px;
        """)

        self.main_layout.addLayout(self.carousel_layout)
        self.main_layout.addWidget(self.name_label)
        self.setLayout(self.main_layout)

        self.update_display()

    def setup_slot(self, label, w, h, is_center):
        label.setFixedSize(w, h)
        label.setScaledContents(True)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30 if is_center else 15)
        shadow.setXOffset(0)
        shadow.setYOffset(12)
        shadow.setColor(QColor(0, 0, 0, 150))
        label.setGraphicsEffect(shadow)

    def render_image(self, label, path, is_center):
        pixmap = QPixmap(path)
        border_color = "#f5c2e7" if is_center else "#313244"
        # Gambar samping dibuat lebih gelap agar fokus ke tengah
        opacity = "1.0" if is_center else "0.5"
        
        label.setStyleSheet(f"""
            border: { '5px' if is_center else '2px' } solid {border_color}; 
            border-radius: 24px; 
            background-color: #000;
        """)
        
        # Memberikan efek visual pudar pada gambar samping melalui style
        if not is_center:
            label.setGraphicsEffect(self.get_opacity_effect(0.5))
        else:
            label.setGraphicsEffect(self.get_shadow_effect(30))

        label.setPixmap(pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                     Qt.TransformationMode.SmoothTransformation))

    def get_opacity_effect(self, opacity):
        from PyQt6.QtWidgets import QGraphicsOpacityEffect
        effect = QGraphicsOpacityEffect()
        effect.setOpacity(opacity)
        return effect

    def get_shadow_effect(self, radius):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(radius)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(QColor(0, 0, 0, 180))
        return shadow

    def update_display(self):
        if not self.images: return
        total = len(self.images)
        idx_c = self.current_index
        idx_l = (idx_c - 1) % total
        idx_r = (idx_c + 1) % total

        self.render_image(self.slot_left, self.images[idx_l], False)
        self.render_image(self.slot_center, self.images[idx_c], True)
        self.render_image(self.slot_right, self.images[idx_r], False)

        self.name_label.setText(os.path.basename(self.images[idx_c]))

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
        subprocess.run([
            "swww", "img", self.images[self.current_index],
            "--transition-type", "outer",
            "--transition-pos", "0.5,0.5",
            "--transition-duration", "1.2"
        ])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraCarousel()
    # Posisikan window di tengah
    geo = app.primaryScreen().geometry()
    window.move((geo.width() - window.width()) // 2, (geo.height() - window.height()) // 2)
    window.show()
    sys.exit(app.exec())