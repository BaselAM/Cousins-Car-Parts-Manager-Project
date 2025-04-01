"""
Custom UI components with elegant design.
"""

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QGroupBox, QStyleOptionGroupBox, QLabel
from PyQt5.QtGui import QPainter, QPainterPath, QColor


class ElegantGroupBox(QGroupBox):
    """Custom GroupBox with more elegant appearance and better theming support"""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setObjectName("elegantGroupBox")

    def paintEvent(self, event):
        """Custom painting for more elegant group box"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get colors from theme or use defaults
        try:
            import themes
            border_color = QColor(themes.get_color('border'))
            bg_color = QColor(themes.get_color('card_bg'))
            title_color = QColor(themes.get_color('text'))
        except:
            # Fallback colors
            border_color = QColor(180, 180, 180)
            bg_color = QColor(245, 245, 245)
            title_color = QColor(60, 60, 60)

        # Create path for rounded rectangle
        path = QPainterPath()
        rect = self.rect().adjusted(1, 1, -1, -1)
        path.addRoundedRect(rect, 6, 6)

        # Fill background
        painter.fillPath(path, bg_color)

        # Draw border
        painter.setPen(border_color)
        painter.drawPath(path)

        # Draw title
        if self.title():
            title_rect = self.style().subControlRect(
                self.style().CC_GroupBox,
                self.styleOptionFromStyle(self.style()),
                self.style().SC_GroupBoxLabel,
                self
            )

            # Create background for title
            title_bg = QRect(title_rect)
            title_bg.adjust(-5, 0, 5, 0)

            painter.fillRect(title_bg, bg_color)

            # Draw title text
            painter.setPen(title_color)
            painter.drawText(title_rect, Qt.AlignCenter, self.title())

    def styleOptionFromStyle(self, style):
        """Create style options for the group box"""
        option = QStyleOptionGroupBox()
        option.initFrom(self)
        option.text = self.title()
        return option


class RichTextLabel(QLabel):
    """Enhanced label with rich text support and automatic styling"""

    def __init__(self, text="", parent=None, style=None):
        """Initialize with optional text and style"""
        super().__init__(text, parent)
        self.setTextFormat(Qt.RichText)
        self.setWordWrap(True)
        self.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.setOpenExternalLinks(True)

        if style:
            self.setObjectName(style)

    def setStyleClass(self, class_name):
        """Set CSS style class for the label"""
        self.setObjectName(class_name)
        self.style().unpolish(self)
        self.style().polish(self)