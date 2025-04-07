"""
GridTile component for selection widgets.

A premium tile component for grid layouts with elegant styling and stable behavior.
Used in brand, model, year and category selection steps.
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel,
                             QSizePolicy, QGraphicsOpacityEffect)
from PyQt5.QtCore import (Qt, pyqtSignal, QSize, QEasingCurve)
from PyQt5.QtGui import QPixmap, QColor, QFont

from themes import get_color


class GridTile(QFrame):
    """
    A premium tile for grid layouts with elegant styling and stable behavior.

    Features:
    - Clean, iOS-inspired design
    - Selection highlighting without layout shifts
    - Hover effects
    - Support for icons/images
    """
    # Signal emitted when tile is clicked
    clicked = pyqtSignal(dict)  # Contains the tile's data

    # Find the __init__ method in your GridTile class in parts_navigation/components/grid_tile.py
    # Look for this section of code:

    def __init__(self, data, icon_path=None, is_selected=False, parent=None):
        """
        Initialize the grid tile.

        Args:
            data: Dictionary containing the tile's data
            icon_path: Path to icon image (optional)
            is_selected: Whether the tile is initially selected
            parent: Parent widget
        """
        super().__init__(parent)
        self.data = data
        self.icon_path = icon_path
        self.is_selected = is_selected
        self.is_hovered = False

        # Set up UI
        self.setObjectName("gridTile")
        self.setCursor(Qt.PointingHandCursor)

        # MODIFY THIS SECTION - Replace the size policy code with:
        # Use a more flexible size policy that allows horizontal expansion
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumSize(90, 100)  # Minimum size instead of fixed
        self.setMaximumWidth(150)  # Add a maximum width to prevent tiles from getting too large

        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements with elegant spacing."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignCenter)

        # Icon container - fixed size
        self.icon_container = QFrame()
        self.icon_container.setObjectName("tileIconContainer")
        self.icon_container.setFixedSize(60, 60)

        icon_layout = QVBoxLayout(self.icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)

        # Icon label - fixed size
        self.icon_label = QLabel()
        self.icon_label.setObjectName("tileIcon")
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(50, 50)

        # Try to load icon if provided
        if self.icon_path:
            pixmap = QPixmap(self.icon_path)
            if not pixmap.isNull():
                self.icon_label.setPixmap(pixmap.scaled(
                    50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self._set_text_icon()
        else:
            self._set_text_icon()

        icon_layout.addWidget(self.icon_label)
        layout.addWidget(self.icon_container, 0, Qt.AlignCenter)

        # Text label
        self.text_label = QLabel(self._get_display_text())
        self.text_label.setObjectName("tileText")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)

        # Use nice font
        font = QFont("SF Pro Text", 12)
        font.setBold(True)
        self.text_label.setFont(font)

        layout.addWidget(self.text_label, 0, Qt.AlignCenter)

    def _set_text_icon(self):
        """Set a text-based icon using the first letter of the display text."""
        text = self._get_display_text()
        if text:
            first_char = text[0].upper()

            # Apply text icon styling
            self.icon_label.setText(first_char)

            # Get theme colors
            highlight = get_color('highlight', '#4299E1')
            text_color = get_color('highlight_text', '#FFFFFF')

            self.icon_label.setStyleSheet(f"""
                background-color: {highlight};
                color: {text_color};
                font-size: 24px;
                font-weight: bold;
                border-radius: 25px;
                min-width: 50px;
                min-height: 50px;
            """)

    def _get_display_text(self):
        """Extract the display text from the data dictionary."""
        # Try to get the primary value from the data
        if not self.data:
            return "Unknown"

        # Extract first value from dictionary
        try:
            return next(iter(self.data.values()), "Unknown")
        except:
            return "Unknown"

    def apply_theme(self):
        """Apply premium styling based on current state."""
        # Get theme colors
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        text_color = get_color('text', '#E2E8F0')
        border_color = get_color('border', '#2C5282')
        highlight = get_color('highlight', '#4299E1')

        # Compute derived colors
        card_bg_lighter = QColor(card_bg).lighter(108).name()
        hover_bg = get_color('button_hover', QColor(card_bg).lighter(115).name())

        # Apply styling based on state
        if self.is_selected:
            # Selected state
            self.setObjectName("gridTileSelected")

            self.setStyleSheet(f"""
                #gridTileSelected {{
                    background-color: {hover_bg};
                    border: 2px solid {highlight};
                    border-radius: 10px;
                }}

                #tileIconContainer {{
                    background-color: transparent;
                }}

                #tileText {{
                    color: {highlight};
                    font-weight: bold;
                }}
            """)
        else:
            # Normal or hovered state
            self.setObjectName("gridTile")

            # Modify styling based on hover state
            hover_style = ""
            if self.is_hovered:
                hover_style = f"""
                    background-color: {hover_bg};
                    border: 1px solid {highlight};
                """

            self.setStyleSheet(f"""
                #gridTile {{
                    background-color: {card_bg};
                    border: 1px solid {border_color};
                    border-radius: 10px;
                    {hover_style}
                }}

                #tileIconContainer {{
                    background-color: transparent;
                }}

                #tileText {{
                    color: {text_color};
                }}
            """)

    def set_selected(self, selected):
        """
        Set the selection state without animations.

        Args:
            selected: Whether the tile should be selected
        """
        if self.is_selected == selected:
            return

        self.is_selected = selected

        # Apply new styling immediately - no animations
        self.apply_theme()

    # Mouse event handlers
    def mousePressEvent(self, event):
        """Handle mouse press - just use standard handling."""
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release to emit clicked signal."""
        self.clicked.emit(self.data)
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        self.is_hovered = True
        self.apply_theme()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave to end hover effect."""
        self.is_hovered = False
        self.apply_theme()
        super().leaveEvent(event)