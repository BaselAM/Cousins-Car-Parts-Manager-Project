"""
InfoHeader component for displaying contextual information.

A premium header component that displays information about the current selection
with elegant styling and animations.
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel,
                             QSizePolicy, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor

from themes import get_color


class InfoHeader(QFrame):
    """
    A premium header displaying contextual information with elegant styling.

    Features:
    - Clean, iOS-inspired design
    - Fade animations when content changes
    - Premium styling with theme support
    """

    def __init__(self, translator, parent=None):
        """
        Initialize the info header.

        Args:
            translator: Translator for localization
            parent: Parent widget
        """
        super().__init__(parent)
        self.translator = translator
        self.current_text = ""

        # Set up UI
        self.setObjectName("infoHeader")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.setMinimumHeight(50)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements with elegant spacing."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)  # Generous padding
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignCenter)

        # Info label with premium typography
        self.info_label = QLabel()
        self.info_label.setObjectName("infoText")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)

        # Premium font styling
        font = QFont("SF Pro Display", 15)
        font.setBold(True)
        font.setLetterSpacing(QFont.AbsoluteSpacing, -0.3)  # Subtle negative tracking
        self.info_label.setFont(font)

        layout.addWidget(self.info_label)

    def apply_theme(self):
        """Apply premium styling based on system theme."""
        # Get theme colors
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        text_color = get_color('text', '#E2E8F0')
        border_color = get_color('border', '#2C5282')
        highlight = get_color('highlight', '#4299E1')

        # Compute derived colors
        card_bg_lighter = QColor(card_bg).lighter(108).name()
        highlight_lighter = QColor(highlight).lighter(115).name()

        # Apply styling
        self.setStyleSheet(f"""
            #infoHeader {{
                background-color: {card_bg_lighter};
                border-radius: 10px;
                border: 1px solid {border_color};
            }}

            #infoHeader:empty {{
                background-color: transparent;
                border: none;
            }}

            #infoText {{
                color: {highlight};
                font-weight: bold;
                font-size: 15px;
                padding: 8px;
            }}
        """)

    def set_info(self, info_text):
        """
        Set the information text with a smooth fade animation.

        Args:
            info_text: Text to display
        """
        # Skip if no change or empty
        if info_text == self.current_text:
            return

        # Hide if empty
        if not info_text:
            self.current_text = ""
            self.info_label.setText("")
            self.hide()
            return

        # Show if hidden
        if not self.isVisible():
            self.show()

        # If changing from empty to content, just set directly
        if not self.current_text:
            self.current_text = info_text
            self.info_label.setText(info_text)
            return

        # Animate change with fade effect
        self._animate_text_change(info_text)

    def _animate_text_change(self, new_text):
        """
        Animate changing the text with a fade transition.

        Args:
            new_text: New text to display
        """
        # Apply opacity effect if not already present
        if not self.info_label.graphicsEffect():
            effect = QGraphicsOpacityEffect(self.info_label)
            effect.setOpacity(1.0)
            self.info_label.setGraphicsEffect(effect)

        # Create fade out animation
        fade_out = QPropertyAnimation(self.info_label.graphicsEffect(), b"opacity")
        fade_out.setDuration(150)  # Quick fade
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.OutQuad)

        # Update text when faded out
        def update_text():
            self.current_text = new_text
            self.info_label.setText(new_text)

            # Create fade in animation
            fade_in = QPropertyAnimation(self.info_label.graphicsEffect(), b"opacity")
            fade_in.setDuration(200)  # Slightly slower fade in
            fade_in.setStartValue(0.0)
            fade_in.setEndValue(1.0)
            fade_in.setEasingCurve(QEasingCurve.InOutQuad)
            fade_in.start()

        # Connect update to fade out completion
        fade_out.finished.connect(update_text)

        # Start animation
        fade_out.start()