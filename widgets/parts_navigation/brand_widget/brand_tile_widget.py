"""
Brand tile widget for the parts navigation system with internet logo loading.
Displays brand logos fetched from the internet with elegant loading animations.
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QSizePolicy,
                            QGraphicsDropShadowEffect, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QPixmap, QColor, QFont, QPainter, QPainterPath

from themes import get_color

class BrandTileWidget(QFrame):
    """
    A clean, elegant tile widget for displaying a car brand.
    Includes logo loaded from the internet and name with selection states.
    """
    # Signal emitted when tile is clicked
    clicked = pyqtSignal(dict)

    def __init__(self, brand_data, logo_manager=None, selected=False, parent=None):
        super().__init__(parent)
        self.brand_data = brand_data
        self.logo_manager = logo_manager
        self.selected = selected
        self.hovered = False
        self.is_loading_logo = False
        self.loading_progress = 0
        self.loading_timer = None
        self.setup_ui()
        self.apply_theme()

        # Load logo if manager provided
        if self.logo_manager:
            self.load_logo_from_internet()

    def setup_ui(self):
        """Set up the UI components with clean layout"""
        self.setObjectName("brandTile")
        self.setCursor(Qt.PointingHandCursor)

        # Set size policy for better responsiveness
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setMinimumSize(100, 110)
        self.setMaximumSize(180, 160)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)

        # Logo container for better control
        self.logo_container = QFrame()
        self.logo_container.setObjectName("logoContainer")
        self.logo_container.setMinimumSize(70, 70)
        self.logo_container.setMaximumSize(90, 90)

        logo_layout = QVBoxLayout(self.logo_container)
        logo_layout.setContentsMargins(2, 2, 2, 2)
        logo_layout.setAlignment(Qt.AlignCenter)

        # Logo label
        self.logo_label = QLabel()
        self.logo_label.setObjectName("brandLogo")
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setScaledContents(True)
        self.logo_label.setMinimumSize(60, 60)
        self.logo_label.setMaximumSize(80, 80)
        logo_layout.addWidget(self.logo_label)

        # Progress bar for logo loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("logoProgress")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setMaximumHeight(4)
        logo_layout.addWidget(self.progress_bar)
        self.progress_bar.hide()

        # Add logo container to main layout
        layout.addWidget(self.logo_container, 0, Qt.AlignCenter)

        # Brand name label
        self.name_label = QLabel(self.brand_data.get('brand', ''))
        self.name_label.setObjectName("brandName")
        self.name_label.setAlignment(Qt.AlignCenter)
        self.name_label.setWordWrap(True)

        # Use a clean font for the brand name
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.name_label.setFont(font)

        layout.addWidget(self.name_label, 0, Qt.AlignCenter)

        # Set a default text logo until we load the real one
        self._set_text_logo()

    def _set_text_logo(self):
        """Set a text-based logo using the first letter of the brand name"""
        brand_name = self.brand_data.get('brand', '')
        if brand_name:
            first_letter = brand_name[0].upper()

            # Create a stylish text logo
            self.logo_label.setText(first_letter)

            # Get colors from the theme
            bg_color = get_color('highlight')
            text_color = get_color('highlight_text', '#FFFFFF')

            self.logo_label.setStyleSheet(f"""
                background-color: {bg_color};
                color: {text_color};
                font-size: 28px;
                font-weight: bold;
                border-radius: 30px;
            """)

    def apply_theme(self):
        """Apply theme styling based on state"""
        # Get colors from theme
        bg_color = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        highlight = get_color('highlight')
        hover_color = get_color('button_hover')
        secondary_text = get_color('secondary_text')

        # Base style for normal state
        base_style = f"""
            #brandTile {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 10px;
            }}
            
            #logoContainer {{
                background-color: transparent;
            }}
            
            #brandName {{
                color: {text_color};
                margin-top: 5px;
            }}
            
            #logoProgress {{
                background-color: {bg_color};
                border: none;
            }}
            
            #logoProgress::chunk {{
                background-color: {highlight};
                border-radius: 2px;
            }}
        """

        # Different styling based on selection state
        if self.selected:
            selected_style = f"""
                #brandTile {{
                    background-color: {hover_color};
                    border: 2px solid {highlight};
                }}
                
                #brandName {{
                    color: {highlight};
                    font-weight: bold;
                }}
            """
            self.setStyleSheet(base_style + selected_style)

            # Add shadow effect for selected state
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(12)
            shadow.setColor(QColor(0, 0, 0, 40))
            shadow.setOffset(0, 2)
            self.setGraphicsEffect(shadow)
        else:
            # Handle hover state
            hover_style = ""
            if self.hovered:
                hover_style = f"""
                    #brandTile {{
                        background-color: {hover_color};
                        border: 1px solid {highlight};
                    }}
                """
            self.setStyleSheet(base_style + hover_style)

            # Remove any graphics effect
            self.setGraphicsEffect(None)

    def set_selected(self, selected):
        """Set the selection state of this tile"""
        if self.selected != selected:
            self.selected = selected
            self.apply_theme()

            # Add subtle animation when selection changes
            if selected:
                self._animate_selection()

    def _animate_selection(self):
        """Add a subtle animation when selected"""
        # Create a scale animation
        animation = QPropertyAnimation(self, b"minimumSize")
        animation.setStartValue(self.minimumSize())
        animation.setEndValue(QSize(self.minimumSize().width(), self.minimumSize().height() + 5))
        animation.setDuration(150)
        animation.setEasingCurve(QEasingCurve.OutQuad)

        # Create reverse animation
        reverse_animation = QPropertyAnimation(self, b"minimumSize")
        reverse_animation.setStartValue(QSize(self.minimumSize().width(), self.minimumSize().height() + 5))
        reverse_animation.setEndValue(self.minimumSize())
        reverse_animation.setDuration(150)
        reverse_animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Connect animations
        animation.finished.connect(reverse_animation.start)

        # Start first animation
        animation.start()

    def load_logo_from_internet(self):
        """Load the brand logo from the internet using LogoManager"""
        if not self.logo_manager:
            return

        brand_name = self.brand_data.get('brand', '')
        if not brand_name:
            return

        # Check if already in memory cache
        pixmap = self.logo_manager.get_logo(brand_name)
        if pixmap:
            self._set_logo_pixmap(pixmap)
        else:
            # Start progress animation while loading
            self._start_logo_loading_animation()

            # Connect to logo_ready signal
            self.logo_manager.logo_ready.connect(self._on_logo_ready)

    def _start_logo_loading_animation(self):
        """Start a loading animation while fetching the logo"""
        self.is_loading_logo = True
        self.loading_progress = 0
        self.progress_bar.setValue(0)
        self.progress_bar.show()

        # Create a timer to simulate progress
        if self.loading_timer is None:
            self.loading_timer = QTimer(self)
            self.loading_timer.timeout.connect(self._update_loading_progress)

        # Start with 40ms interval for smooth animation
        self.loading_timer.start(40)

    def _update_loading_progress(self):
        """Update the loading progress animation"""
        if self.loading_progress >= 90:
            # Slow down when near end
            self.loading_timer.setInterval(100)
            self.loading_progress += 0.5
        else:
            self.loading_progress += 2

        self.progress_bar.setValue(int(self.loading_progress))

    def _stop_logo_loading_animation(self):
        """Stop the logo loading animation"""
        if self.loading_timer:
            self.loading_timer.stop()

        self.is_loading_logo = False

        # Create fade-out animation for progress bar
        if self.progress_bar.isVisible():
            fade_out = QPropertyAnimation(self.progress_bar, b"opacity")
            self.progress_bar.setGraphicsEffect(QGraphicsDropShadowEffect())
            self.progress_bar.graphicsEffect().setEnabled(False)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.0)
            fade_out.setDuration(300)
            fade_out.setEasingCurve(QEasingCurve.OutQuad)
            fade_out.finished.connect(self.progress_bar.hide)
            fade_out.start()

    def _on_logo_ready(self, brand_name, pixmap):
        """Handle downloaded logo"""
        if brand_name.lower() == self.brand_data.get('brand', '').lower():
            self._set_logo_pixmap(pixmap)
            self._stop_logo_loading_animation()

            # Disconnect to avoid receiving other brands' logos
            try:
                self.logo_manager.logo_ready.disconnect(self._on_logo_ready)
            except:
                pass

    def _set_logo_pixmap(self, pixmap):
        """Set the logo pixmap with a nice fade-in effect"""
        if pixmap and not pixmap.isNull():
            # Reset text and styling
            self.logo_label.setText("")
            self.logo_label.setStyleSheet("")

            # Apply rounded corners to the logo
            rounded_pixmap = self._create_rounded_pixmap(pixmap)
            self.logo_label.setPixmap(rounded_pixmap.scaled(
                self.logo_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

            # Create fade-in animation
            fade_in = QPropertyAnimation(self.logo_label, b"windowOpacity")
            self.logo_label.setWindowOpacity(0.0)
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setDuration(300)
            fade_in.setEasingCurve(QEasingCurve.OutCubic)
            fade_in.start()

    def _create_rounded_pixmap(self, pixmap):
        """Create a rounded version of the pixmap"""
        # Create a new pixmap for the rounded version
        rounded = QPixmap(pixmap.size())
        rounded.fill(Qt.transparent)

        # Create a painter to draw the rounded version
        painter = QPainter(rounded)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Create a path for the rounded rectangle
        path = QPainterPath()
        path.addRoundedRect(0, 0, pixmap.width(), pixmap.height(), 10, 10)

        # Clip to the rounded path and draw the original pixmap
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        return rounded

    def mousePressEvent(self, event):
        """Handle mouse press event"""
        # Emit clicked signal with brand data
        self.clicked.emit(self.brand_data)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter event"""
        self.hovered = True
        self.apply_theme()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event"""
        self.hovered = False
        self.apply_theme()
        super().leaveEvent(event)