import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QVBoxLayout, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt

class NobaraCarousel(QWidget):
    def __init__(self):
        super().__init__()
        # Path folder wallpaper Anda
        self.path = "/home/xeeukanbara/Pictures/wallpapers/"
        
        if not os.path.exists(self.path):
            self.path = os.path.expanduser("~/Pictures")

        self.images = sorted([os.path.join(self.path, f) for f in os.listdir(self.path) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))])
        
        self.current_index = 0
        self.initUI()

    def initUI(self):
        # Window setup khas Hyprland (Floating & Center)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Lebar ditingkatkan agar spacing antar gambar besar terasa lega
        self.setFixedSize(1450, 650)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Carousel Container
        self.carousel_layout = QHBoxLayout()
        self.carousel_layout.setSpacing(50) # Jarak antar gambar
        self.carousel_layout.setContentsMargins(20, 0, 20, 0)
        self.carousel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Inisialisasi Slot Gambar
        self.slot_left = QLabel()
        self.slot_center = QLabel()
        self.slot_right = QLabel()

        # DIMENSI: Center hanya 5% lebih besar dari samping
        # Samping: 410x230 | Tengah: 430x242 (Selisih ~5%)
        self.w_side, self.h_side = 410, 230
        self.w_center, self.h_center = 430, 242 

        self.setup_slot(self.slot_left, self.w_side, self.h_side)
        self.setup_slot(self.slot_center, self.w_center, self.h_center) 
        self.setup_slot(self.slot_right, self.w_side, self.h_side)

        self.carousel_layout.addWidget(self.slot_left)
        self.carousel_layout.addWidget(self.slot_center)
        self.carousel_layout.addWidget(self.slot_right)

        # Label Nama File di bawah
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("""
            color: #cdd6f4; 
            font-size: 16px; 
            font-family: 'JetBrains Mono', sans-serif;
            font-weight: bold;
            margin-top: 40px;
            background-color: rgba(17, 17, 27, 0.8);
            padding: 8px 20px;
            border-radius: 10px;
        """)

        self.main_layout.addLayout(self.carousel_layout)
        self.main_layout.addWidget(self.name_label)
        self.setLayout(self.main_layout)

        self.update_display()

    def setup_slot(self, label, w, h):
        label.setFixedSize(w, h)
        label.setScaledContents(True)

    def render_image(self, label, path, is_center):
        pixmap = QPixmap(path)
        border_color = "#f5c2e7" if is_center else "#313244"
        border_width = "4px" if is_center else "2px"
        
        # Border Radius diset ke 20px sesuai permintaan
        label.setStyleSheet(f"""
            border: {border_width} solid {border_color}; 
            border-radius: 20px; 
            background-color: #11111b;
        """)
        
        # Penanganan Efek (Center: Shadow, Side: Opacity)
        if is_center:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(35)
            shadow.setXOffset(0)
            shadow.setYOffset(10)
            shadow.setColor(QColor(0, 0, 0, 220))
            label.setGraphicsEffect(shadow)
        else:
            opacity = QGraphicsOpacityEffect()
            opacity.setOpacity(0.55)
            label.setGraphicsEffect(opacity)

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
        # Menggunakan transisi swww yang smooth
        subprocess.run([
            "swww", "img", self.images[self.current_index],
            "--transition-type", "outer",
            "--transition-pos", "0.5,0.5",
            "--transition-duration", "1.2",
            "--transition-fps", "60"
        ])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraCarousel()
    
    # Memastikan window muncul tepat di tengah monitor
    screen_geo = app.primaryScreen().geometry()
    window.move((screen_geo.width() - window.width()) // 2, 
                (screen_geo.height() - window.height()) // 2)
    
    window.show()
    sys.exit(app.exec())