"""
UI utility classes and functions for the parts navigation system.
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QHBoxLayout,
                             QSizePolicy, QLineEdit, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
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
        layout.setContentsMargins(0, 0, 0, 10)

        self.search_label = QLabel(self.translator.t(self.label_key))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.translator.t(self.placeholder_key))
        self.search_input.textChanged.connect(self.search_changed.emit)

        layout.addWidget(self.search_label)
        layout.addWidget(self.search_input, 1)  # Takes most space

    def apply_theme(self):
        """Apply current theme."""
        self.setStyleSheet(f"""
            QLabel {{
                color: {get_color('text')};
                font-size: 14px;
            }}

            QLineEdit {{
                background-color: {get_color('card_bg')};
                color: {get_color('text')};
                border: 1px solid {get_color('border')};
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
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
        layout.setContentsMargins(0, 0, 0, 10)

        self.info_label = QLabel()
        self.info_label.setObjectName("infoLabel")
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)

        layout.addWidget(self.info_label)

    def apply_theme(self):
        """Apply current theme."""
        self.setStyleSheet(f"""
            #infoLabel {{
                color: {get_color('highlight')};
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
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


class GridTile(QFrame):
    """A clickable tile for grid layouts with icon and text."""

    clicked = pyqtSignal(dict)

    def __init__(self, data, icon_path=None, is_selected=False):
        super().__init__()
        self.data = data
        self.icon_path = icon_path
        self.is_selected = is_selected
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)

        # Icon or first letter
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setMinimumSize(60, 60)
        self.icon_label.setMaximumSize(80, 80)

        # Try to load icon if provided
        if self.icon_path:
            pixmap = QPixmap(self.icon_path)
            if not pixmap.isNull():
                self.icon_label.setPixmap(pixmap.scaled(
                    self.icon_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                # Use first letter as fallback
                self._set_text_icon()
        else:
            self._set_text_icon()

        layout.addWidget(self.icon_label, 0, Qt.AlignCenter)

        # Text label
        self.text_label = QLabel(self._get_display_text())
        self.text_label.setObjectName("tileText")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)
        layout.addWidget(self.text_label, 0, Qt.AlignCenter)

        # Set cursor
        self.setCursor(Qt.PointingHandCursor)

        # Set object name for styling
        self.setObjectName("tileSelected" if self.is_selected else "tile")

    def _set_text_icon(self):
        """Set the icon to display the first letter of the item."""
        # Get the first character of the first value in the data dict
        first_value = next(iter(self.data.values()), "")
        first_char = first_value[0].upper() if first_value else "?"

        self.icon_label.setText(first_char)
        self.icon_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            background-color: #2980b9;
            color: white;
            border-radius: 10px;
        """)

    def _get_display_text(self):
        """Get the text to display on the tile."""
        # Return the first value in the data dict
        return next(iter(self.data.values()), "")

    def apply_theme(self):
        """Apply current theme based on selection state."""
        bg_color = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        highlight = get_color('highlight')
        button_hover = get_color('button_hover')

        # Base style for both states
        base_style = f"""
            border-radius: 10px;
            min-width: 120px;
            min-height: 120px;
            max-width: 150px;
            max-height: 150px;
        """

        # Different styling based on selection state
        if self.is_selected:
            self.setStyleSheet(f"""
                #tileSelected {{
                    background-color: {button_hover};
                    border: 2px solid {highlight};
                    {base_style}
                }}

                #tileText {{
                    color: {text_color};
                    font-size: 14px;
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                #tile {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    {base_style}
                }}

                #tile:hover {{
                    border: 2px solid {highlight};
                    background-color: {button_hover};
                }}

                #tileText {{
                    color: {text_color};
                    font-size: 14px;
                    font-weight: bold;
                }}
            """)

    def mousePressEvent(self, event):
        """Handle mouse press events for clicks."""
        self.clicked.emit(self.data)
        super().mousePressEvent(event)

    def set_selected(self, selected):
        """Set the selection state of the tile."""
        if self.is_selected != selected:
            self.is_selected = selected
            self.setObjectName("tileSelected" if selected else "tile")
            self.apply_theme()
            self.style().unpolish(self)
            self.style().polish(self)


class TilesGrid(QFrame):
    """A grid layout for displaying tiles."""

    item_selected = pyqtSignal(dict)

    def __init__(self, translator, columns=4):
        super().__init__()
        self.translator = translator
        self.columns = columns
        self.tiles = []
        self.selected_data = None
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements."""
        self.setObjectName("tilesContainer")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area and grid will be created in populate method
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setSpacing(10)

        layout.addLayout(self.grid_layout)

    def apply_theme(self):
        """Apply current theme."""
        self.setStyleSheet(f"""
            #tilesContainer {{
                background-color: transparent;
                border: none;
            }}
        """)

    def populate(self, items, icon_getter=None):
        """
        Populate the grid with tiles for the given items.

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
            self.grid_layout.addWidget(empty_label, 0, 0)
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

            # Add to grid
            row = i // self.columns
            col = i % self.columns
            self.grid_layout.addWidget(tile, row, col)
            self.tiles.append(tile)

    def _compare_items(self, item1, item2):
        """Compare two items to check if they're the same."""
        if not item1 or not item2:
            return False

        # Compare the first value in each dictionary
        key1 = next(iter(item1.keys()), None)
        key2 = next(iter(item2.keys()), None)

        if key1 and key2 and key1 == key2:
            return item1[key1] == item2[key2]

        return False

    def _on_tile_clicked(self, data):
        """Handle click on a tile."""
        self.selected_data = data

        # Update selection status of all tiles
        for tile in self.tiles:
            tile.set_selected(self._compare_items(tile.data, data))

        # Emit selected item
        self.item_selected.emit(data)

    def clear(self):
        """Clear all tiles."""
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

    def set_selected(self, data):
        """Set the selected item programmatically."""
        if data:
            # Find matching tile
            for tile in self.tiles:
                if self._compare_items(tile.data, data):
                    self._on_tile_clicked(data)
                    break

    def get_selected(self):
        """Get the currently selected item."""
        return self.selected_data