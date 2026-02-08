import sys
import os
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize

class NobaraCarousel(QWidget):
    def __init__(self):
        super().__init__()
        self.path = "/home/xeeukanbara/Pictures/wallpapers/"
        
        # Fallback
        if not os.path.exists(self.path):
            self.path = os.path.expanduser("~/Pictures")

        self.images = sorted([os.path.join(self.path, f) for f in os.listdir(self.path) 
                             if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif'))])
        
        self.current_index = 0
        self.initUI()

    def initUI(self):
        # Setup Window (Frameless & Transparan agar estetik di Hyprland)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(1100, 500)

        # Layout Utama
        self.main_layout = QVBoxLayout()
        self.carousel_layout = QHBoxLayout()
        self.carousel_layout.setSpacing(40)
        self.carousel_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Widget untuk 3 Slot Gambar
        self.slot_left = QLabel()
        self.slot_center = QLabel()
        self.slot_right = QLabel()

        # Styling Slot
        self.setup_slot(self.slot_left, 280, 160, 0.6)   # Samping (Kecil)
        self.setup_slot(self.slot_center, 540, 300, 1.0) # Tengah (Besar)
        self.setup_slot(self.slot_right, 280, 160, 0.6)  # Samping (Kecil)

        self.carousel_layout.addWidget(self.slot_left)
        self.carousel_layout.addWidget(self.slot_center)
        self.carousel_layout.addWidget(self.slot_right)

        # Label Nama File di bawah Center
        self.name_label = QLabel()
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.name_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: rgba(0,0,0,0.5); padding: 5px; border-radius: 10px;")

        self.main_layout.addLayout(self.carousel_layout)
        self.main_layout.addWidget(self.name_label)
        self.setLayout(self.main_layout)

        self.update_display()

    def setup_slot(self, label, w, h, opacity):
        label.setFixedSize(w, h)
        label.setStyleSheet(f"border-radius: 20px; border: 2px solid rgba(255,255,255,{opacity}); background: #000;")
        label.setScaledContents(True)

    def update_display(self):
        # Logika Index untuk 3 gambar (Left, Center, Right)
        total = len(self.images)
        idx_c = self.current_index
        idx_l = (idx_c - 1) % total
        idx_r = (idx_c + 1) % total

        # Render Gambar ke Slot
        self.render_image(self.slot_left, self.images[idx_l])
        self.render_image(self.slot_center, self.images[idx_c], is_center=True)
        self.render_image(self.slot_right, self.images[idx_r])

        # Update Nama File
        self.name_label.setText(os.path.basename(self.images[idx_c]))

    def render_image(self, label, path, is_center=False):
        pixmap = QPixmap(path)
        # Efek Glow Pink jika di tengah
        border = "4px solid #f5c2e7" if is_center else "2px solid #313244"
        label.setStyleSheet(f"border: {border}; border-radius: 20px; background: #000;")
        label.setPixmap(pixmap.scaled(label.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, 
                                     Qt.TransformationMode.SmoothTransformation))

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
            "--transition-type", "grow",
            "--transition-pos", "center",
            "--transition-duration", "1.2"
        ])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = NobaraCarousel()
    window.show()
    sys.exit(app.exec())