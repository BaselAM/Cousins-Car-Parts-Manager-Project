"""
Enhanced ScrollBar component with custom styling.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollBar
from PyQt5.QtGui import QColor

from themes import get_color


class EnhancedScrollBar(QScrollBar):
    """A custom scrollbar with enhanced styling."""

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.apply_styling()

    def apply_styling(self):
        """Apply enhanced styling to the scrollbar."""
        background_color = QColor(get_color('background'))
        self.setStyleSheet(f"""
            QScrollBar {{
                background: {background_color.darker(110).name()};
                border-radius: 6px;
                margin: 0px;
            }}

            QScrollBar:horizontal {{
                height: 12px;
            }}

            QScrollBar:vertical {{
                width: 12px;
            }}

            QScrollBar::handle {{
                background: {get_color('border')};
                border-radius: 6px;
                min-height: 30px;
                min-width: 30px;
            }}

            QScrollBar::handle:hover {{
                background: {get_color('highlight')};
            }}

            QScrollBar::add-line, QScrollBar::sub-line {{
                width: 0px;
                height: 0px;
            }}

            QScrollBar::add-page, QScrollBar::sub-page {{
                background: none;
            }}
        """)