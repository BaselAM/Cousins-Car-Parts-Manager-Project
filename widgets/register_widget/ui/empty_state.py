"""
Empty state component displayed when no product is selected.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QFont, QColor

from themes import get_color, get_font_size


class EmptyStateWidget(QWidget):
    """Widget to display when no product is selected."""

    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator
        self.setup_ui()

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the empty state UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 50, 20, 50)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignCenter)

        # Add search icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setObjectName("emptyStateIcon")

        # Try to load search icon
        try:
            icon_path = "resources/search_big_icon.png"
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("🔍")
                font = icon_label.font()
                font.setPointSize(60)
                icon_label.setFont(font)
        except:
            icon_label.setText("🔍")
            font = icon_label.font()
            font.setPointSize(60)
            icon_label.setFont(font)

        layout.addWidget(icon_label)

        # Add message
        message_label = QLabel(self._translate(
            "search_product_prompt",
            "Search for a product using the search bar or scan a barcode"
        ))
        message_label.setObjectName("emptyStateMessage")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        font = message_label.font()
        font.setPointSize(get_font_size("xlarge"))
        message_label.setFont(font)

        layout.addWidget(message_label)

        # Add subtitle with additional instructions
        subtitle_label = QLabel(self._translate(
            "empty_state_subtitle",
            "You can search by product name, ID, or category"
        ))
        subtitle_label.setObjectName("emptyStateSubtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)

        layout.addWidget(subtitle_label)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply styling to the empty state."""
        secondary_text_color = QColor(get_color('secondary_text'))

        self.setStyleSheet(f"""
            #emptyStateIcon {{
                color: {secondary_text_color.lighter(130).name()};
            }}

            #emptyStateMessage {{
                color: {get_color('secondary_text')};
                margin-bottom: 10px;
            }}

            #emptyStateSubtitle {{
                color: {secondary_text_color.lighter(130).name()};
                font-size: {get_font_size('medium')}px;
                margin-top: -10px;
            }}
        """)