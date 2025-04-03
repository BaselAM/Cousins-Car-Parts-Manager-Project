"""
UI utility classes and functions for the parts navigation system.
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QHBoxLayout,
                             QSizePolicy, QLineEdit, QGridLayout, QScrollArea, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QPixmap, QFont, QColor
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.ui_utils')


class SearchBox(QFrame):
    """A reusable search box widget with label and search input."""

    search_changed = pyqtSignal(str)

    def __init__(self, translator, placeholder_key='search_placeholder', label_key='search'):
        super().__init__()
        self.translator = translator
        self.placeholder_key = placeholder_key
        self.label_key = label_key
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 3)
        layout.setSpacing(2)

        self.search_label = QLabel(self.translator.t(self.label_key))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.translator.t(self.placeholder_key))
        self.search_input.textChanged.connect(self.search_changed.emit)

        # Make label fixed width but not too large
        self.search_label.setFixedWidth(40)

        # Set size policies for adaptive sizing
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.search_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.search_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input, 1)  # Takes most space

    def apply_theme(self):
        """Apply current theme."""
        self.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text')};
            }}

            QLineEdit {{
                background-color: {get_color('card_bg')};
                color: {get_color('text')};
                border: 1px solid {get_color('border')};
                border-radius: 3px;
                padding: 3px;
            }}
        """)

    def update_translations(self):
        """Update all translatable text."""
        self.search_label.setText(self.translator.t(self.label_key))
        self.search_input.setPlaceholderText(self.translator.t(self.placeholder_key))

    def clear(self):
        """Clear the search input."""
        self.search_input.clear()

    def set_text(self, text):
        """Set the search input text."""
        self.search_input.setText(text)

    def get_text(self):
        """Get the search input text."""
        return self.search_input.text()


class InfoHeader(QFrame):
    """A header widget displaying information about the previous selections."""

    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 3)
        layout.setSpacing(0)

        self.info_label = QLabel()
        self.info_label.setObjectName("infoLabel")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)

        # Use size policy to make it compact but adaptable
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.info_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        layout.addWidget(self.info_label)

    def apply_theme(self):
        """Apply current theme."""
        self.setStyleSheet(f"""
            #infoLabel {{
                color: {get_color('highlight')};
                font-weight: bold;
                margin-bottom: 2px;
                padding: 2px;
            }}
        """)

    def set_info(self, info_text):
        """Set the information text."""
        self.info_label.setText(info_text)
        self.setVisible(bool(info_text))

    def update_translations(self):
        """Update all translatable text."""
        # Nothing to update directly - content is set externally
        pass


"""
Improved GridTile from ui_utils.py for better visibility and styling.
"""


class GridTile(QFrame):
    """A clickable tile for grid layouts with icon and text - improved for visibility."""

    clicked = pyqtSignal(dict)

    def __init__(self, data, icon_path=None, is_selected=False):
        super().__init__()
        self.data = data
        self.icon_path = icon_path
        self.is_selected = is_selected
        self.setup_ui()
        self.apply_theme()

        # IMPROVED: Set fixed size for consistency
        self.setFixedSize(120, 90)

    def setup_ui(self):
        """Initialize and arrange UI elements for better visibility."""
        # Main layout with proper spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignCenter)

        # Icon container with better sizing
        self.icon_container = QFrame()
        self.icon_container.setObjectName("iconContainer")
        self.icon_container.setFixedSize(50, 50)  # Fixed size for consistency

        icon_layout = QVBoxLayout(self.icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)

        # Icon or first letter with better visibility
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setFixedSize(40, 40)  # Fixed size for consistency

        # Try to load icon if provided
        if self.icon_path:
            pixmap = QPixmap(self.icon_path)
            if not pixmap.isNull():
                self.icon_label.setPixmap(pixmap.scaled(
                    40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                # Use first letter as fallback
                self._set_text_icon()
        else:
            self._set_text_icon()

        icon_layout.addWidget(self.icon_label)
        layout.addWidget(self.icon_container, 0, Qt.AlignCenter)

        # Text label with proper sizing and wrapping
        self.text_label = QLabel(self._get_display_text())
        self.text_label.setObjectName("tileText")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setFixedHeight(30)  # Fixed height for consistency

        # Improved font sizing for better readability
        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        self.text_label.setFont(font)

        layout.addWidget(self.text_label, 0, Qt.AlignCenter)

        # Set cursor for better UX
        self.setCursor(Qt.PointingHandCursor)

        # Set object name for styling
        self.setObjectName("tileSelected" if self.is_selected else "tile")

    def _set_text_icon(self):
        """Set the icon to display the first letter of the item with improved styling."""
        # Get the first character of the first value in the data dict
        first_value = next(iter(self.data.values()), "")
        first_char = first_value[0].upper() if first_value else "?"

        # Use a larger font for better visibility
        self.icon_label.setText(first_char)

        # Get highlight color for better theme integration
        highlight = get_color('highlight', '#4299E1')

        self.icon_label.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            background-color: {highlight};
            color: white;
            border-radius: 20px;
            min-width: 40px;
            min-height: 40px;
            max-width: 40px;
            max-height: 40px;
            padding: 0px;
        """)

    def _get_display_text(self):
        """Get the text to display on the tile with error handling."""
        try:
            # Return the first value in the data dict
            return next(iter(self.data.values()), "")
        except Exception:
            # Return something safe if dictionary is empty
            return "Unknown"

    def apply_theme(self):
        """Apply current theme based on selection state with improved styling."""
        # Get theme colors
        bg_color = get_color('card_bg', '#1E3A5F')
        text_color = get_color('text', '#E2E8F0')
        border_color = get_color('border', '#2C5282')
        highlight = get_color('highlight', '#4299E1')
        button_hover = get_color('button_hover', '#4299E1')

        # Enhanced styling for better visibility
        if self.is_selected:
            self.setStyleSheet(f"""
                #tileSelected {{
                    background-color: {button_hover};
                    border: 2px solid {highlight};
                    border-radius: 8px;
                    padding: 4px;
                }}

                #iconContainer {{
                    background-color: transparent;
                }}

                #tileText {{
                    color: {text_color};
                    font-weight: bold;
                    margin-top: 4px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                #tile {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                    padding: 4px;
                }}

                #tile:hover {{
                    border: 1px solid {highlight};
                    background-color: {QColor(bg_color).lighter(110).name()};
                }}

                #iconContainer {{
                    background-color: transparent;
                }}

                #tileText {{
                    color: {text_color};
                    margin-top: 4px;
                }}
            """)

    def mousePressEvent(self, event):
        """Handle mouse press events with improved feedback."""
        # Add visual feedback
        if not self.is_selected:
            # Create a temporary style for press effect
            current_style = self.styleSheet()
            bg_color = get_color('card_bg', '#1E3A5F')
            highlight = get_color('highlight', '#4299E1')

            pressed_style = f"""
                #tile {{
                    background-color: {QColor(bg_color).darker(110).name()};
                    border: 1px solid {highlight};
                    border-radius: 8px;
                    padding: 4px;
                }}
            """

            self.setStyleSheet(pressed_style)

            # Schedule restoration of normal style
            QTimer.singleShot(100, lambda: self.setStyleSheet(current_style))

        # Emit clicked signal with data
        self.clicked.emit(self.data)
        super().mousePressEvent(event)

    def set_selected(self, selected):
        """Set the selection state of the tile with improved visual feedback."""
        if self.is_selected != selected:
            self.is_selected = selected
            self.setObjectName("tileSelected" if selected else "tile")
            self.apply_theme()

            # Add scale animation for selection change
            if selected:
                # Create a temporary scale effect
                animation = QPropertyAnimation(self, b"geometry")
                animation.setDuration(150)

                original_geo = self.geometry()
                expanded_geo = QRect(
                    original_geo.x() - 2,
                    original_geo.y() - 2,
                    original_geo.width() + 4,
                    original_geo.height() + 4
                )

                animation.setStartValue(original_geo)
                animation.setEndValue(expanded_geo)
                animation.setEasingCurve(QEasingCurve.OutQuad)

                # Return to original size after animation
                animation.finished.connect(
                    lambda: QTimer.singleShot(50, lambda: self.setGeometry(original_geo))
                )

                animation.start()


class TilesGrid(QFrame):
    """A grid layout for displaying tiles with better visibility and responsiveness."""

    item_selected = pyqtSignal(dict)

    def __init__(self, translator, columns=4):
        super().__init__()
        self.translator = translator
        self.columns = columns
        self.tiles = []
        self.selected_data = None
        self.setup_ui()
        self.apply_theme()

        # IMPROVED: Set better size policies
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(300)  # Ensure minimum height for visibility

    def setup_ui(self):
        """Initialize and arrange UI elements for better visibility."""
        self.setObjectName("tilesContainer")

        # Main layout with proper sizing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)  # Small spacing between elements

        # Scroll area to contain the grid for better display
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Container for the grid
        self.grid_container = QWidget()
        self.grid_container.setObjectName("gridContainer")
        self.grid_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Grid with minimal spacing
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(10)  # Increased spacing for better visibility
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)  # Align to top-left

        # Set equal column and row stretch
        for i in range(self.columns):
            self.grid_layout.setColumnStretch(i, 1)

        # Add the grid container to the scroll area
        self.scroll_area.setWidget(self.grid_container)

        # Add the scroll area to the main layout
        layout.addWidget(self.scroll_area)

    def apply_theme(self):
        """Apply current theme with better styling."""
        # Get theme colors
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        border_color = get_color('border', '#2C5282')

        self.setStyleSheet(f"""
            #tilesContainer {{
                background-color: transparent;
                border: none;
            }}

            #gridContainer {{
                background-color: {bg_color};
                border-radius: 8px;
                padding: 5px;
            }}

            QScrollBar:vertical {{
                background: {bg_color};
                width: 14px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background: {border_color};
                min-height: 20px;
                border-radius: 7px;
                margin: 2px;
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar:horizontal {{
                background: {bg_color};
                height: 14px;
                margin: 0px;
            }}

            QScrollBar::handle:horizontal {{
                background: {border_color};
                min-width: 20px;
                border-radius: 7px;
                margin: 2px;
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """)

    def populate(self, items, icon_getter=None):
        """
        Populate the grid with tiles for the given items with improved layout.

        Args:
            items (list): List of dictionaries with data for each tile
            icon_getter (callable, optional): Function that takes an item and returns an icon path
        """
        # Clear current tiles
        self.clear()

        # If no items, show empty message
        if not items:
            empty_label = QLabel(self.translator.t('no_items_found'))
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
            self.grid_layout.addWidget(empty_label, 0, 0, 1, self.columns)
            return

        # Create new tiles
        for i, item in enumerate(items):
            # Get icon path if needed
            icon_path = icon_getter(item) if icon_getter else None

            # Create tile
            is_selected = (self.selected_data is not None and
                           self._compare_items(item, self.selected_data))
            tile = GridTile(item, icon_path, is_selected)
            tile.clicked.connect(self._on_tile_clicked)

            # IMPROVED: Set fixed size for tiles to ensure consistent layout
            tile.setFixedSize(120, 90)

            # Add to grid with improved layout calculation
            row = i // self.columns
            col = i % self.columns
            self.grid_layout.addWidget(tile, row, col)
            self.tiles.append(tile)

        # Calculate and set appropriate grid container height
        rows = (len(items) + self.columns - 1) // self.columns  # Ceiling division
        min_height = rows * 100  # 100px per row (90px tile + spacing)
        self.grid_container.setMinimumHeight(min_height)

    def clear(self):
        """Clear all tiles with proper cleanup."""
        # Remove all tiles from grid
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    self.grid_layout.removeWidget(widget)
                    widget.deleteLater()

        self.tiles = []
        self.selected_data = None

        # Reset minimum height
        self.grid_container.setMinimumHeight(100)