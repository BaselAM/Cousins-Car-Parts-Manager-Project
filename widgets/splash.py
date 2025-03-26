from PyQt5.QtWidgets import QWidget, QDesktopWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt, QPropertyAnimation, QTimer, QEasingCurve, pyqtSlot
from shared import SCRIPT_DIR  # Assuming SCRIPT_DIR is defined in shared


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)

        screen = QDesktopWidget().availableGeometry()
        sw, sh = screen.width(), screen.height()
        target_w, target_h = int(sw * 0.30), int(sh * 0.30)

        pix = QPixmap(str(SCRIPT_DIR / 'resources/intro.jpg'))
        if pix.isNull():
            raise FileNotFoundError("Splash image not found!")
        self.pixmap = pix.scaled(target_w, target_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.resize(self.pixmap.size())
        self.move((sw - self.pixmap.width()) // 2, (sh - self.pixmap.height()) // 2)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(8000)
        self.animation.setStartValue(1.0)
        self.animation.setKeyValueAt(0.3, 0.8)
        self.animation.setKeyValueAt(0.7, 0.85)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.InOutSine)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        # Connect the timeout to our dedicated slot; suppress static analysis warnings.
        self.timer.timeout.connect(self.close_splash)  # type: ignore
        self.animation.start()
        self.timer.start(6000)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap)

    @pyqtSlot()
    def close_splash(self):
        """Slot to close the splash screen."""
        self.close()

    def closeEvent(self, event):
        try:
            self.animation.stop()
            self.timer.stop()
        except Exception as e:
            print(f"Splash cleanup error: {str(e)}")
        super().closeEvent(event)
