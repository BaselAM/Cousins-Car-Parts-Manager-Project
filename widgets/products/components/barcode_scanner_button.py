"""
Complete barcode scanner button implementation with enhanced animations and translation support.
Replace your entire barcode_scanner_button.py file with this.
"""
import os
import logging
from PyQt5.QtWidgets import (QLabel, QDialog, QVBoxLayout, QHBoxLayout,
                             QPushButton, QApplication, QMessageBox, QFrame, QGraphicsDropShadowEffect,
                             QInputDialog, QLineEdit)
from PyQt5.QtCore import (Qt, pyqtSignal, QTimer, QEvent, QObject, QPropertyAnimation,
                          QEasingCurve, QRect, QSize, QPoint, pyqtProperty)
from PyQt5.QtGui import QPixmap, QPainter, QColor, QIcon, QFontMetrics, QLinearGradient, QBrush

# Create module logger
logger = logging.getLogger(__name__)

# Try importing themes, with fallback
try:
    from themes import get_color
except ImportError:
    logger.warning("Could not import themes module. Using fallback colors.")

    def get_color(name, default=None):
        """Fallback color function if themes module is not available"""
        colors = {
            'background': '#FFFFFF',
            'text': '#333333',
            'highlight': '#2196F3',
            'success': '#4CAF50',
        }
        return colors.get(name, default) if default else colors.get(name, '#000000')


class BarcodeEventFilter(QObject):
    """
    Event filter that captures keyboard input which might come from a barcode scanner.
    Barcode scanners typically send characters in rapid succession followed by Enter.
    """
    barcode_detected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buffer = ""
        self.timer = QTimer()
        self.timer.timeout.connect(self.reset_buffer)
        self.timer.setSingleShot(True)
        self.min_length = 4  # Minimum barcode length

    def eventFilter(self, obj, event):
        """Filter keyboard events to detect barcode scanner input"""
        if event.type() == QEvent.KeyPress:
            # Reset timer on each keypress (barcode scanners send keys very quickly)
            if self.timer.isActive():
                self.timer.stop()

            key = event.key()

            # Check for Enter key, which often terminates barcode scanner input
            if key == Qt.Key_Return or key == Qt.Key_Enter:
                if len(self.buffer) >= self.min_length:
                    self.barcode_detected.emit(self.buffer)
                    self.buffer = ""
                    return True  # Consume the event
                self.buffer = ""  # Reset if buffer too short
            elif key == Qt.Key_Escape:
                self.buffer = ""  # Reset on Escape
            else:
                # Add character to buffer
                text = event.text()
                if text and text.isprintable():
                    self.buffer += text
                    # Start timer - if no keypress occurs within 50ms, it's probably not a scanner
                    self.timer.start(50)

        # Always return False to allow normal event processing
        return False

    def reset_buffer(self):
        """Reset the buffer if timeout occurs"""
        self.buffer = ""


class ScanLineAnimation(QFrame):
    """
    A custom widget that displays a smooth scanning line animation over the barcode icon.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(120, 120)

        # Animation properties
        self._scan_position = 0.0  # 0.0 to 1.0 representing the scan line position
        self._glow_opacity = 0.5   # 0.0 to 1.0 for pulsing glow effect

        # Set up the scan line animation
        self.scan_animation = QPropertyAnimation(self, b"scanPosition")
        self.scan_animation.setDuration(1800)  # slower for a more elegant effect
        self.scan_animation.setStartValue(0.0)
        self.scan_animation.setEndValue(1.0)
        self.scan_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.scan_animation.setLoopCount(-1)  # infinite loop

        # Set up the glow animation
        self.glow_animation = QPropertyAnimation(self, b"glowOpacity")
        self.glow_animation.setDuration(1500)
        self.glow_animation.setStartValue(0.3)
        self.glow_animation.setEndValue(0.7)
        self.glow_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.glow_animation.setLoopCount(-1)  # infinite loop

        # Start the animations
        self.scan_animation.start()
        self.glow_animation.start()

    def setScanPosition(self, position):
        """Set the scan line position and update the widget"""
        if self._scan_position != position:
            self._scan_position = position
            self.update()

    def scanPosition(self):
        """Get the current scan position"""
        return self._scan_position

    # Define the property for QPropertyAnimation
    scanPosition = pyqtProperty(float, scanPosition, setScanPosition)

    def setGlowOpacity(self, opacity):
        """Set the glow effect opacity and update the widget"""
        if self._glow_opacity != opacity:
            self._glow_opacity = opacity
            self.update()

    def glowOpacity(self):
        """Get the current glow opacity"""
        return self._glow_opacity

    # Define the property for QPropertyAnimation
    glowOpacity = pyqtProperty(float, glowOpacity, setGlowOpacity)

    def paintEvent(self, event):
        """Custom paint event to draw the scan line and glow effects"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get colors from theme
        highlight_color = QColor(get_color('highlight', '#2196F3'))

        # Define the rectangle for the scan line
        rect = self.rect()
        center = rect.center()
        radius = min(rect.width(), rect.height()) / 2 - 5

        # Draw subtle glow around the whole circle
        glow_color = QColor(highlight_color)
        glow_color.setAlphaF(self._glow_opacity * 0.3)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow_color))
        painter.drawEllipse(center, radius + 5, radius + 5)

        # Draw the scanning line
        scan_y = rect.top() + self._scan_position * rect.height()
        line_gradient = QLinearGradient(
            rect.left(), scan_y - 5, rect.right(), scan_y + 5
        )

        # Create a smooth gradient effect for the scan line
        scan_color = QColor(highlight_color)

        # Transparent color for gradient edges
        transparent = QColor(scan_color)
        transparent.setAlphaF(0.0)

        # Fully opaque color for the center
        opaque = QColor(scan_color)
        opaque.setAlphaF(0.8)

        # Set up gradient stops
        line_gradient.setColorAt(0.0, transparent)
        line_gradient.setColorAt(0.1, opaque)
        line_gradient.setColorAt(0.5, opaque)
        line_gradient.setColorAt(0.9, opaque)
        line_gradient.setColorAt(1.0, transparent)

        # Draw the scan line
        scan_rect = QRect(rect.left(), int(scan_y - 2), rect.width(), 4)
        painter.setBrush(QBrush(line_gradient))
        painter.drawRect(scan_rect)

        # Draw scan glow around the line
        glow_rect = QRect(rect.left(), int(scan_y - 12), rect.width(), 24)
        glow_gradient = QLinearGradient(
            rect.left(), glow_rect.top(), rect.left(), glow_rect.bottom()
        )

        glow_transparent = QColor(scan_color)
        glow_transparent.setAlphaF(0.0)

        glow_visible = QColor(scan_color)
        glow_visible.setAlphaF(0.2)

        glow_gradient.setColorAt(0.0, glow_transparent)
        glow_gradient.setColorAt(0.5, glow_visible)
        glow_gradient.setColorAt(1.0, glow_transparent)

        painter.setBrush(QBrush(glow_gradient))
        painter.drawRect(glow_rect)

    def stopAnimations(self):
        """Stop all running animations"""
        self.scan_animation.stop()
        self.glow_animation.stop()

    def startSuccessAnimation(self):
        """Start a success animation to indicate barcode was detected"""
        # Stop the scanning animations
        self.stopAnimations()

        # Set up a success animation
        success_color = QColor(get_color('success', '#4CAF50'))

        # Save current opacity for smooth transition
        current_opacity = self._glow_opacity

        # Create new animation for success effect
        self.success_animation = QPropertyAnimation(self, b"glowOpacity")
        self.success_animation.setDuration(800)
        self.success_animation.setStartValue(current_opacity)
        self.success_animation.setEndValue(0.9)
        self.success_animation.setEasingCurve(QEasingCurve.OutQuad)
        self.success_animation.start()

        # Update to use success color
        self.update()


class PulsatingIconFrame(QFrame):
    """
    A frame that displays the barcode icon with subtle pulsating effects.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("iconFrame")
        self.setFixedSize(120, 120)

        # First create the icon label that will hold the barcode icon
        self.icon_label = QLabel()
        self.icon_label.setObjectName("scanIcon")
        self.icon_label.setAlignment(Qt.AlignCenter)

        # Shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        shadow_color = QColor(0, 0, 0, 40)
        self.shadow.setColor(shadow_color)
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)

        # Initialize animation properties
        self._scale_factor = 1.0

        # Setup layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.addWidget(self.icon_label)

        # Create the scan line animation overlay
        self.scan_line = ScanLineAnimation(self)
        self.scan_line.raise_()

        # Subtle scale animation - start after everything is set up
        self.scale_animation = QPropertyAnimation(self, b"scaleFactor")
        self.scale_animation.setDuration(1800)
        self.scale_animation.setStartValue(0.98)
        self.scale_animation.setEndValue(1.02)
        self.scale_animation.setEasingCurve(QEasingCurve.InOutSine)
        self.scale_animation.setLoopCount(-1)

        # Start animation on next event loop cycle to ensure UI is fully set up
        QTimer.singleShot(100, self.scale_animation.start)

    def setScaleFactor(self, factor):
        """Set the scale factor and update the widget appearance"""
        if self._scale_factor != factor:
            self._scale_factor = factor
            self.updateTransform()

    def scaleFactor(self):
        """Get the current scale factor"""
        return self._scale_factor

    # Define the property for QPropertyAnimation
    scaleFactor = pyqtProperty(float, scaleFactor, setScaleFactor)

    def updateTransform(self):
        """Update the widget transformation based on scale factor"""
        # Just trigger an update to refresh the widget
        self.update()

    def startSuccessAnimation(self):
        """Stop normal animations and transition to success state"""
        # Stop the scaling animation
        self.scale_animation.stop()

        # Start a quick "pop" animation for success
        current_scale = self._scale_factor

        # Create a quick grow animation
        self.grow_animation = QPropertyAnimation(self, b"scaleFactor")
        self.grow_animation.setDuration(200)
        self.grow_animation.setStartValue(current_scale)
        self.grow_animation.setEndValue(1.05)
        self.grow_animation.setEasingCurve(QEasingCurve.OutBack)

        # Then subtly settle back
        self.settle_animation = QPropertyAnimation(self, b"scaleFactor")
        self.settle_animation.setDuration(600)
        self.settle_animation.setStartValue(1.05)
        self.settle_animation.setEndValue(1.0)
        self.settle_animation.setEasingCurve(QEasingCurve.OutElastic)

        # Set up sequential animations
        self.grow_animation.finished.connect(self.settle_animation.start)
        self.grow_animation.start()

        # Start the success animation in the scan line
        self.scan_line.startSuccessAnimation()

        # Update the frame styling for success
        success_color = get_color('success', '#4CAF50')
        self.setStyleSheet(f"""
            #iconFrame {{
                background-color: {QColor(success_color).lighter(170).name()};
                border-radius: 60px;
                border: 2px solid {success_color};
            }}
        """)


class AnimatedStatusLabel(QLabel):
    """
    A status label with smooth text animations.
    """
    def __init__(self, text, parent=None):
        # Remove underscores and format text elegantly
        formatted_text = text.replace("_", " ").title()
        super().__init__(formatted_text, parent)
        self.setObjectName("statusLabel")
        self.setAlignment(Qt.AlignCenter)

        # Animation properties
        self._opacity = 1.0

        # Opacity animation for text changes
        self.opacity_animation = QPropertyAnimation(self, b"opacity")
        self.opacity_animation.setDuration(300)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Waiting dots animation
        self.base_text = formatted_text
        self.dots_state = 0
        self.dots_timer = QTimer(self)
        self.dots_timer.setInterval(800)  # Slower dots animation (was 500)
        self.dots_timer.timeout.connect(self.updateDots)
        self.dots_timer.start()

    def setOpacity(self, opacity):
        """Set the opacity and update the widget"""
        if self._opacity != opacity:
            self._opacity = opacity
            self.setStyleSheet(f"opacity: {opacity};")
            self.update()

    def opacity(self):
        """Get the current opacity"""
        return self._opacity

    # Define the property for QPropertyAnimation
    opacity = pyqtProperty(float, opacity, setOpacity)

    def updateDots(self):
        """Update the waiting dots animation"""
        self.dots_state = (self.dots_state + 1) % 4
        dots = "." * self.dots_state
        self.setText(f"{self.base_text}{dots}")

    def changeText(self, new_text):
        """Change the text with a smooth animation"""
        # Format text elegantly
        formatted_text = new_text.replace("_", " ").title()

        # Save the new base text
        self.base_text = formatted_text

        # Fade out
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.3)

        # Set up the fade back in
        fade_in = QPropertyAnimation(self, b"opacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0.3)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InOutQuad)

        # When fade out completes, update text and start fade in
        self.opacity_animation.finished.connect(lambda: self.setText(formatted_text))
        self.opacity_animation.finished.connect(fade_in.start)

        # Start the animation sequence
        self.opacity_animation.start()

    def stopAnimations(self):
        """Stop all animations"""
        if self.dots_timer.isActive():
            self.dots_timer.stop()


class ScanningDialog(QDialog):
    """
    Premium scanning dialog with high-end animations that integrate with the theme system.
    """
    barcode_scanned = pyqtSignal(str)

    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator

        # Configure dialog properties
        self.setWindowTitle(self._translate("barcode:scan_barcode", "Scan Barcode"))
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setFixedSize(400, 320)  # Slightly taller for better proportions
        self.setModal(True)

        # Set up the UI
        self.setup_ui()

        # Apply theme-aware styling
        self.apply_styling()

        # Set up barcode capture
        self.event_filter = BarcodeEventFilter(self)
        self.event_filter.barcode_detected.connect(self.on_barcode_detected)
        self.installEventFilter(self.event_filter)

        # Focus dialog to capture keyboard input
        self.setFocus()

    def _translate(self, key, default):
        """Get translated text with fallback"""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the premium UI with animations"""
        # Use a vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # Header with enhanced title
        title_label = QLabel(self._translate("barcode:scan_barcode", "Scan Barcode"))
        title_label.setObjectName("scanDialogTitle")
        font = title_label.font()
        font.setPointSize(20)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Create the animated icon frame
        self.icon_frame = PulsatingIconFrame(self)

        # Center the icon frame
        center_layout = QHBoxLayout()
        center_layout.addStretch(1)
        center_layout.addWidget(self.icon_frame)
        center_layout.addStretch(1)
        main_layout.addLayout(center_layout)

        # Animated status label
        self.status_label = AnimatedStatusLabel(
            self._translate("barcode:waiting_for_scan", "Waiting for barcode scan"),
            self
        )
        font = self.status_label.font()
        font.setPointSize(14)
        self.status_label.setFont(font)
        main_layout.addWidget(self.status_label)

        # Note label with subtle styling
        note_text = self._translate("barcode:scan_note",
                                  "Position your barcode scanner and scan any barcode.\nPress ESC to cancel.")
        note_label = QLabel(note_text)
        note_label.setObjectName("noteLabel")
        note_label.setAlignment(Qt.AlignCenter)
        note_label.setWordWrap(True)
        main_layout.addWidget(note_label)

        # Add spacer
        main_layout.addStretch(1)

        # Cancel button with smooth hover effects
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        self.cancel_button = QPushButton(self._translate("barcode:cancel", "Cancel"))
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setCursor(Qt.PointingHandCursor)

        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        # Load the icon
        self.setup_icon()

    def setup_icon(self):
        """Set up the barcode icon with theme-aware handling"""
        import os

        try:
            # Try standard paths - try more paths to find the icon
            icon_paths = [
                "resources/barcode.png",
                "./resources/barcode.png",
                "resources/icons/barcode.png",
                "../resources/barcode.png",
            ]

            icon_loaded = False
            for path in icon_paths:
                if os.path.exists(path):
                    logger.debug(f"Found barcode icon at: {path}")
                    pixmap = QPixmap(path)
                    if not pixmap.isNull():
                        # Scale the icon to fit properly - make it larger for better visibility
                        pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                        # Get background color
                        bg_color = get_color('background', '#FFFFFF')
                        text_color = get_color('text', '#000000')

                        # Create a version with stronger contrast
                        enhanced_pixmap = QPixmap(pixmap.size())
                        enhanced_pixmap.fill(Qt.transparent)

                        painter = QPainter(enhanced_pixmap)
                        painter.setRenderHint(QPainter.Antialiasing)
                        painter.setRenderHint(QPainter.SmoothPixmapTransform)
                        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                        painter.drawPixmap(0, 0, pixmap)

                        # Apply darker color for better visibility
                        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)

                        # Create a darker version of the icon for better visibility
                        # Use a pure black or white based on theme for maximum contrast
                        if bg_color.startswith('#'):
                            hex_color = bg_color.lstrip('#')
                            if len(hex_color) == 6:
                                r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
                                brightness = (r * 299 + g * 587 + b * 114) / 1000

                                if brightness < 128:
                                    # Dark theme - use pure white for icon
                                    icon_color = QColor(255, 255, 255)
                                else:
                                    # Light theme - use pure black for icon
                                    icon_color = QColor(0, 0, 0)

                                painter.fillRect(enhanced_pixmap.rect(), icon_color)
                        else:
                            # Default to black if no background color
                            painter.fillRect(enhanced_pixmap.rect(), QColor(0, 0, 0))

                        painter.end()

                        # Set the enhanced pixmap
                        self.icon_frame.icon_label.setPixmap(enhanced_pixmap)

                        # Add a shadow to the icon for depth
                        try:
                            icon_shadow = QGraphicsDropShadowEffect(self.icon_frame.icon_label)
                            icon_shadow.setBlurRadius(10)
                            icon_shadow.setColor(QColor(0, 0, 0, 60))
                            icon_shadow.setOffset(0, 1)
                            self.icon_frame.icon_label.setGraphicsEffect(icon_shadow)
                        except Exception as shadow_err:
                            logger.error(f"Could not apply icon shadow: {shadow_err}")

                        # Set additional styling for the icon label
                        self.icon_frame.icon_label.setStyleSheet("""
                            QLabel#scanIcon {
                                padding: 5px;
                                background-color: transparent;
                            }
                        """)

                        icon_loaded = True
                        break

            # Fallback if icon not loaded
            if not icon_loaded:
                logger.warning("No barcode icon found! Using text fallback.")
                self.icon_frame.icon_label.setText("🔍")
                font = self.icon_frame.icon_label.font()
                font.setPointSize(40)  # Larger emoji
                self.icon_frame.icon_label.setFont(font)
                self.icon_frame.icon_label.setAlignment(Qt.AlignCenter)
                self.icon_frame.icon_label.setStyleSheet("color: #333333;")
        except Exception as e:
            logger.error(f"Error loading icon: {e}")
            # Last resort fallback
            self.icon_frame.icon_label.setText("🔍")
            self.icon_frame.icon_label.setAlignment(Qt.AlignCenter)

    def apply_styling(self):
        """Apply premium styling with theme integration"""
        try:
            # Get theme colors
            bg_color = get_color('background', '#FFFFFF')
            text_color = get_color('text', '#000000')
            highlight_color = get_color('highlight', '#2196F3')
            border_color = get_color('border', '#E0E0E0')

            # Main dialog styling
            dialog_style = f"""
                QDialog {{
                    background-color: {bg_color};
                    color: {text_color};
                    border-radius: 12px;
                }}
                
                #scanDialogTitle {{
                    color: {text_color};
                    font-weight: bold;
                }}
                
                #iconFrame {{
                    background-color: {QColor(highlight_color).lighter(180).name()};
                    border-radius: 60px;
                    border: 2px solid {QColor(highlight_color).lighter(130).name()};
                }}
                
                #scanIcon {{
                    background-color: transparent;
                    padding: 5px;
                }}
                
                #statusLabel {{
                    color: {text_color};
                    font-weight: bold;
                }}
                
                #noteLabel {{
                    color: {QColor(text_color).lighter(130).name()};
                    opacity: 0.8;
                }}
                
                QPushButton {{
                    background-color: {highlight_color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10px 20px;
                    font-weight: bold;
                    min-height: 40px;
                }}
                
                QPushButton:hover {{
                    background-color: {QColor(highlight_color).lighter(110).name()};
                }}
                
                QPushButton:pressed {{
                    background-color: {QColor(highlight_color).darker(110).name()};
                }}
            """
            self.setStyleSheet(dialog_style)

            # Add shadow to the dialog for depth
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 40))
            shadow.setOffset(0, 4)
            self.setGraphicsEffect(shadow)

            # Add a stronger border to the icon frame to make it stand out
            icon_frame_style = f"""
                background-color: {QColor(highlight_color).lighter(180).name()};
                border-radius: 60px;
                border: 3px solid {QColor(highlight_color).name()};
            """
            self.icon_frame.setStyleSheet(icon_frame_style)

        except Exception as e:
            logger.error(f"Style application error: {e}")
            # If styling fails, apply minimal styling to ensure usability
            self.setStyleSheet("""
                QDialog {
                    background-color: white;
                    color: black;
                }
            """)

    def on_barcode_detected(self, barcode):
        """Handle detected barcode with premium visual feedback"""
        if not barcode:
            return

        # Stop the animations
        self.status_label.stopAnimations()

        # Update the status with a smooth animation
        self.status_label.changeText(self._translate("barcode:barcode_detected", "Barcode detected!"))

        # Apply success styling
        success_color = get_color('success', '#4CAF50')
        self.status_label.setStyleSheet(f"color: {success_color}; font-weight: bold;")

        # Start success animations in the icon frame
        self.icon_frame.startSuccessAnimation()

        # Emit signal with the barcode
        self.barcode_scanned.emit(barcode)

        # Close dialog after a short delay with a smooth fade
        QTimer.singleShot(1200, self.accept)

    def keyPressEvent(self, event):
        """Handle key press events"""
        # Allow Escape key to close the dialog
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            # Let the event filter handle other keys
            super().keyPressEvent(event)


class BarcodeScannerButton(QLabel):
    """
    Barcode scanner button that uses the barcode.png icon,
    changes color based on theme, and shows a scanning dialog.
    """
    barcode_scanned = pyqtSignal(str, str)  # barcode, format

    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator
        self.setObjectName("ThemeAwareBarcodeScannerButton")

        # Setup UI
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(42, 42)  # Make it a bit larger
        self.setToolTip(self._translate("barcode:scan_barcode_tooltip", "Scan Barcode"))

        # Load and apply icon based on theme
        self.update_icon()

    def _translate(self, key, default):
        """Get translated text with fallback"""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def update_icon(self):
        """Update the icon based on the current theme with enhanced contrast and visibility"""
        # Try to load icon from resources with more paths
        icon_paths = [
            "resources/barcode.png",
            "resources/icons/barcode.png",
            "../resources/barcode.png",
            "./resources/icons/barcode.png",
            "../resources/icons/barcode.png"
        ]

        icon_loaded = False
        for path in icon_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    # Get theme colors
                    bg_color = QColor(get_color('background'))
                    is_dark_theme = bg_color.lightness() < 128

                    # Scale the icon to fit the button with better sizing
                    pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)

                    if is_dark_theme:
                        # Create bright white version for dark themes
                        colored_pixmap = QPixmap(pixmap.size())
                        colored_pixmap.fill(Qt.transparent)

                        painter = QPainter(colored_pixmap)
                        painter.setRenderHint(QPainter.Antialiasing)
                        painter.setRenderHint(QPainter.SmoothPixmapTransform)
                        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                        painter.drawPixmap(0, 0, pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                        painter.fillRect(colored_pixmap.rect(), QColor(255, 255, 255))
                        painter.end()

                        self.setPixmap(colored_pixmap)
                    else:
                        # Use darker version for light theme for better visibility
                        colored_pixmap = QPixmap(pixmap.size())
                        colored_pixmap.fill(Qt.transparent)

                        painter = QPainter(colored_pixmap)
                        painter.setRenderHint(QPainter.Antialiasing)
                        painter.setRenderHint(QPainter.SmoothPixmapTransform)
                        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                        painter.drawPixmap(0, 0, pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
                        painter.fillRect(colored_pixmap.rect(), QColor(40, 40, 40))
                        painter.end()

                        self.setPixmap(colored_pixmap)

                    self.setAlignment(Qt.AlignCenter)
                    icon_loaded = True
                    break

        # Fallback if icon not loaded
        if not icon_loaded:
            logger.warning("No barcode icon found for button, using text fallback.")
            self.setText("🔍")
            font = self.font()
            font.setPointSize(20)
            self.setFont(font)
            self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            self.setStyleSheet("background-color: rgba(0, 0, 0, 0.1); border-radius: 5px;")
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        self.setStyleSheet("")
        if event.button() == Qt.LeftButton and self.rect().contains(event.pos()):
            self.scan_barcode()
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter events"""
        self.setStyleSheet("background-color: rgba(0, 0, 0, 0.05); border-radius: 5px;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave events"""
        self.setStyleSheet("")
        super().leaveEvent(event)

    def scan_barcode(self):
        """Show the scanning dialog and handle scanned barcodes"""
        dialog = ScanningDialog(self.parent(), self.translator)
        dialog.barcode_scanned.connect(self.on_barcode_detected)

        # Show dialog modally
        result = dialog.exec_()

        # If rejected, do nothing
        if result == QDialog.Rejected:
            return

    def on_barcode_detected(self, barcode):
        """Handle detected barcode from the dialog"""
        if not barcode:
            return

        # Add very basic barcode format detection
        barcode_format = "Unknown"
        if len(barcode) == 12 and barcode.isdigit():
            barcode_format = "UPC-A"
        elif len(barcode) == 13 and barcode.isdigit():
            barcode_format = "EAN-13"
        elif len(barcode) == 8 and barcode.isdigit():
            barcode_format = "EAN-8"

        # Emit the barcode scanned signal
        logger.info(f"Barcode detected: {barcode} (Format: {barcode_format})")
        self.barcode_scanned.emit(barcode, barcode_format)