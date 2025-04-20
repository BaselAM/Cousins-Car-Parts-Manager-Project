"""
Floating action button component for the Smart Search Widget.
"""

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QToolButton, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor, QCursor

# Try to import theme and logger modules - handle gracefully if not available
try:
    from themes import get_color, get_size, get_font_size
    from logger import get_logger
    logger = get_logger('widgets.smart_search_widget.components.fab')
except ImportError:
    # Simple fallback logger if the standard logger is unavailable
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('widgets.smart_search_widget.components.fab')

    # Fallback theme functions
    def get_color(name):
        colors = {
            'background': '#F5F5F5',
            'card_bg': '#FFFFFF',
            'text': '#333333',
            'title': '#111111',
            'secondary_text': '#666666',
            'border': '#DDDDDD',
            'highlight': '#3A7BDF',
            'input_bg': '#FFFFFF',
            'button': '#3A7BDF',
            'button_hover': '#2A5CBF',
            'button_pressed': '#1A4CAF',
            'success': '#4CAF50',
            'selected': '#E3F2FD',
            'shadow': '#00000033',
            'button_disabled': '#CCCCCC',
            'text_disabled': '#999999'
        }
        return colors.get(name, '#FFFFFF')

    def get_size(name):
        sizes = {
            'padding': 10,
            'margin': 10,
            'border_radius': 5,
            'tiny': 4,
            'small': 8,
            'medium': 16,
            'large': 24
        }
        return sizes.get(name, 10)

    def get_font_size(name):
        sizes = {
            'small': 10,
            'medium': 12,
            'regular': 14,
            'large': 16,
            'title': 20
        }
        return sizes.get(name, 14)


class FloatingActionButton(QToolButton):
    """Modern duplicate product button with animation effects."""

    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator  # Store the translator reference

        # Set fixed size for the button - now rectangular for status bar
        self.setFixedSize(QSize(120, 32))
        self.setObjectName("floatingActionButton")

        # Apply shadow effect with less prominence
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(get_color('shadow')))
        shadow.setOffset(1, 1)
        self.setGraphicsEffect(shadow)

        # Use translated text if translator is available
        if translator:
            self.setText(translator.t('duplicate'))
        else:
            self.setText("Duplicate")

        # Set cursor to pointing hand
        self.setCursor(Qt.PointingHandCursor)

        # Apply theme styling
        self.apply_theme()

    def update_translation(self):
        """Update button text based on current language"""
        if hasattr(self, 'translator') and self.translator:
            self.setText(self.translator.t('duplicate'))

    def apply_theme(self):
        """Apply theme styling to the button."""
        self.setStyleSheet(f"""
            QToolButton#floatingActionButton {{
                background-color: {get_color('button')};
                color: white;
                border-radius: {get_size('tiny')}px;
                font-size: {get_font_size('regular')}px;
                font-weight: bold;
                border: none;
                padding: 2px 8px;
            }}
            QToolButton#floatingActionButton:hover {{
                background-color: {get_color('button_hover')};
            }}
            QToolButton#floatingActionButton:pressed {{
                background-color: {get_color('button_pressed')};
            }}
            QToolButton#floatingActionButton:disabled {{
                background-color: {get_color('button_disabled')};
                color: {get_color('text_disabled')};
            }}
        """)

    def enterEvent(self, event):
        """Handle mouse enter event for subtle highlight."""
        # Enhance shadow slightly
        shadow = self.graphicsEffect()
        if shadow and isinstance(shadow, QGraphicsDropShadowEffect):
            shadow.setBlurRadius(10)
            shadow.setColor(QColor(get_color('shadow')))
            shadow.setOffset(1, 2)

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event to revert effects."""
        # Restore shadow
        shadow = self.graphicsEffect()
        if shadow and isinstance(shadow, QGraphicsDropShadowEffect):
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(get_color('shadow')))
            shadow.setOffset(1, 1)

        super().leaveEvent(event)