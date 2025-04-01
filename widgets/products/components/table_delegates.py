from PyQt5.QtWidgets import QStyledItemDelegate, QLineEdit
from PyQt5.QtGui import QColor, QPainter, QBrush
from PyQt5.QtCore import Qt, QRect, QEvent
from themes import get_color


class ThemedItemDelegate(QStyledItemDelegate):
    """A delegate for styling table items with an elegant, sleek editing appearance
    with support for row highlighting."""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Dictionary to keep track of highlighted rows: {row_number: QColor}
        self.highlight_rows = {}

        # Default theme colors
        self.theme_colors = {
            'bg': get_color('background'),
            'text': get_color('text'),
            'highlight': get_color('highlight')
        }

    def set_theme_colors(self, bg=None, text=None, highlight=None):
        """Update the theme colors used by the delegate"""
        if bg: self.theme_colors['bg'] = bg
        if text: self.theme_colors['text'] = text
        if highlight: self.theme_colors['highlight'] = highlight

    def set_highlight_row(self, row, color=None):
        """
        Set a row to be highlighted with the given color

        Args:
            row: The row number to highlight
            color: QColor for highlighting, or None to remove highlight
        """
        if color:
            self.highlight_rows[row] = color
        else:
            if row in self.highlight_rows:
                del self.highlight_rows[row]

    def paint(self, painter, option, index):
        """Custom paint method to apply highlighting to specific rows"""
        # Check if this cell is in a highlighted row
        if index.row() in self.highlight_rows:
            highlight_color = self.highlight_rows[index.row()]

            # Fill with highlight color
            painter.save()
            painter.fillRect(option.rect, highlight_color)

            # Create a copy of the style option with adjusted colors
            opt = option.__class__(option)
            opt.backgroundBrush = QBrush(highlight_color)

            # Determine text color - use dark text on light backgrounds
            highlight_brightness = highlight_color.red() * 0.299 + highlight_color.green() * 0.587 + highlight_color.blue() * 0.114
            if highlight_brightness > 160:  # Threshold for light vs dark background
                text_color = QColor(30, 30, 30)  # Dark text for light backgrounds
            else:
                text_color = QColor(240, 240, 240)  # Light text for dark backgrounds

            # Apply calculated text color
            opt.palette.setColor(opt.palette.Text, text_color)

            # Draw the text with our custom option
            super().paint(painter, opt, index)
            painter.restore()
        else:
            # Normal painting for non-highlighted rows
            super().paint(painter, option, index)

    def createEditor(self, parent, option, index):
        """Create a custom styled editor for cell editing"""
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            # Use a more refined style for the editor
            bg_color = self.theme_colors['bg']
            highlight_color = self.theme_colors['highlight']
            text_color = self.theme_colors['text']

            editor.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: none;
                    border-radius: 0px;
                    border-bottom: 2px solid {highlight_color};
                    selection-background-color: {highlight_color};
                    selection-color: {bg_color};
                    padding-left: 8px;
                    padding-right: 8px;
                    padding-top: 0px;
                    padding-bottom: 0px;
                    font-size: 14px;
                }}
            """)
        return editor

    def updateEditorGeometry(self, editor, option, index):
        """Precisely position the editor within the cell"""
        # Create a precise rectangle that fully covers the cell content
        rect = QRect(option.rect)

        # Adjust to perfectly align with cell content and remove gaps
        rect.setLeft(rect.left())
        rect.setRight(rect.right())
        rect.setTop(rect.top())
        rect.setBottom(rect.bottom())

        editor.setGeometry(rect)


class ThemedNumericDelegate(ThemedItemDelegate):
    """A delegate specifically for numeric fields with right alignment and formatting"""

    def createEditor(self, parent, option, index):
        """Create an editor with right alignment for numbers"""
        editor = super().createEditor(parent, option, index)
        if isinstance(editor, QLineEdit):
            editor.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        return editor

    def setModelData(self, editor, model, index):
        """Format numeric data correctly when editing is complete"""
        if not isinstance(editor, QLineEdit):
            super().setModelData(editor, model, index)
            return

        try:
            text = editor.text().strip()
            if text:
                # Format as number with 2 decimal places for price column (index 5)
                if index.column() == 5:  # Price column
                    value = float(text.replace(',', '.'))
                    model.setData(index, f"{value:.2f}")
                else:  # Quantity column (index 4)
                    value = int(text)
                    model.setData(index, str(value))
            else:
                model.setData(index, "0")
        except (ValueError, TypeError):
            # If conversion fails, keep the original data
            pass