from PyQt5.QtWidgets import QWidget, QDesktopWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer, QEasingCurve, pyqtSlot
from config import APP_ROOT as SCRIPT_DIR


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.opacity_effect = None
        self.animation = None
        self.timer = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setAttribute(Qt.WA_NoSystemBackground)  # Prevent background repaints

        screen = QDesktopWidget().availableGeometry()
        sw, sh = screen.width(), screen.height()
        target_w, target_h = int(sw * 0.30), int(sh * 0.30)

        try:
            # More efficient image loading with QImage first
            image = QImage(str(SCRIPT_DIR / 'resources/intro.jpg'))
            if image.isNull():
                raise FileNotFoundError("Splash image not found!")

            # Convert to pixmap only after scaling the QImage (more efficient)
            image = image.scaled(target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.pixmap = QPixmap.fromImage(image)
        except Exception as e:
            # Fallback to direct pixmap loading if QImage approach fails
            pix = QPixmap(str(SCRIPT_DIR / 'resources/intro.jpg'))
            if pix.isNull():
                raise FileNotFoundError("Splash image not found!")
            self.pixmap = pix.scaled(target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Resize once the pixmap is prepared
        self.resize(self.pixmap.size())
        self.move((sw - self.pixmap.width()) // 2, (sh - self.pixmap.height()) // 2)

        # Simplified opacity effect - always at full opacity
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)  # Always at full opacity

        # Optional subtle animation for visual interest without dimming
        # You can comment these lines if you want no animation at all
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(4000)  # 4 seconds duration
        self.animation.setStartValue(1.0)  # Start at full opacity
        self.animation.setKeyValueAt(0.5, 0.97)  # Very slight dip in the middle (barely noticeable)
        self.animation.setEndValue(1.0)  # End at full opacity
        self.animation.setEasingCurve(QEasingCurve.InOutSine)
        self.animation.start()

        # Shorter splash display time
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.close_splash)
        self.timer.start(4000)  # 4 seconds total display time

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)  # Only use necessary hints
        painter.drawPixmap(self.rect(), self.pixmap)

    @pyqtSlot()
    def close_splash(self):
        """Slot to close the splash screen."""
        self.close()

    def closeEvent(self, event):
        try:
            # First stop any ongoing operations
            if self.animation and self.animation.state() == QPropertyAnimation.Running:
                self.animation.stop()

            if self.timer and self.timer.isActive():
                self.timer.stop()

            # Store reference to effect before clearing it
            effect = self.graphicsEffect()

            # Clear the graphics effect first
            self.setGraphicsEffect(None)

            # Set references to None to prevent any further access
            self.opacity_effect = None
            self.animation = None
            self.timer = None

        except Exception as e:
            print(f"Splash cleanup error: {str(e)}")

        # Call parent closeEvent last
        super().closeEvent(event)