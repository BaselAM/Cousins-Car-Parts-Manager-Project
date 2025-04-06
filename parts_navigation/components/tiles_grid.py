"""
TilesGrid component for organizing selection tiles.

A premium grid layout for organizing selection tiles with responsive design,
elegant styling and proper toggle functionality.
"""
from PyQt5.QtWidgets import (QFrame, QGridLayout, QLabel, QScrollArea,
                             QWidget, QVBoxLayout, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize

from .grid_tile import GridTile
from themes import get_color


class TilesGrid(QFrame):
    """
    A premium grid for organizing selection tiles with responsive design.

    Features:
    - Clean, elegant layout
    - Automatic column adjustment based on available width
    - Scrolling for overflow
    - Toggle selection management
    """
    # Signal emitted when a tile is selected or deselected
    item_selected = pyqtSignal(dict)  # Contains the selected item's data

    def __init__(self, translator, columns=4, parent=None, allow_toggle=True):
        """
        Initialize the tiles grid.

        Args:
            translator: Translator for localization
            columns: Number of columns in the grid
            parent: Parent widget
            allow_toggle: Whether to allow toggling selection (deselect on second click)
        """
        super().__init__(parent)
        self.translator = translator
        self.columns = columns
        self.tiles = []
        self.selected_item = None
        self.allow_toggle = allow_toggle  # Add toggle support

        # Set up UI
        self.setObjectName("tilesGrid")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements with elegant spacing."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Create scroll area for grid
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setObjectName("tilesScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container for the grid
        self.grid_container = QWidget()
        self.grid_container.setObjectName("gridContainer")

        # Grid layout with tighter spacing
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(6, 6, 6, 6)
        self.grid_layout.setSpacing(6)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Set equal column stretch
        for i in range(self.columns):
            self.grid_layout.setColumnStretch(i, 1)

        # Add container to scroll area
        self.scroll_area.setWidget(self.grid_container)

        # Add scroll area to main layout
        layout.addWidget(self.scroll_area)

    def apply_theme(self):
        """Apply premium styling based on system theme."""
        # Get theme colors
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        text_color = get_color('text', '#E2E8F0')
        border_color = get_color('border', '#2C5282')

        # Apply styling
        self.setStyleSheet(f"""
            #tilesGrid {{
                background-color: transparent;
                border: none;
            }}

            #tilesScrollArea {{
                background-color: transparent;
                border: none;
            }}

            #gridContainer {{
                background-color: {bg_color};
                border-radius: 8px;
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

        # Apply theme to all tiles
        for tile in self.tiles:
            tile.apply_theme()

    def populate(self, items, icon_getter=None):
        """
        Populate the grid with items.

        Args:
            items: List of data dictionaries for each tile
            icon_getter: Function that takes an item and returns an icon path
        """
        # Clear existing tiles
        self.clear()

        # If no items, show empty message
        if not items:
            empty_label = QLabel(self.translator.t('no_items_found'))
            empty_label.setObjectName("emptyMessage")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setWordWrap(True)
            self.grid_layout.addWidget(empty_label, 0, 0, 1, self.columns)
            return

        # Calculate best column count before adding items
        viewport_width = self.scroll_area.viewport().width()
        self.adjust_columns_to_width(viewport_width)

        # Add items to grid
        for i, item in enumerate(items):
            # Get icon path if needed
            icon_path = None
            if icon_getter:
                icon_path = icon_getter(item)

            # Check if this item should be selected
            is_selected = (self.selected_item is not None and
                           self._compare_items(item, self.selected_item))

            # Create tile
            tile = GridTile(item, icon_path, is_selected)
            tile.clicked.connect(self._on_tile_clicked)

            # Calculate position
            row = i // self.columns
            col = i % self.columns

            # Add to grid with column span of 1 and alignment
            self.grid_layout.addWidget(tile, row, col, 1, 1, Qt.AlignCenter)

            # Store reference to tile
            self.tiles.append(tile)

        # Update container size
        self._update_container_size()

    def _update_container_size(self):
        """Update the size of the grid container based on content."""
        if not self.tiles:
            return

        # Calculate rows
        rows = (len(self.tiles) + self.columns - 1) // self.columns

        # Calculate height for tiles
        tile_height = 120  # Default tile height
        spacing = self.grid_layout.spacing()
        margins = self.grid_layout.contentsMargins()

        # Calculate container height
        height = (rows * tile_height) + ((rows - 1) * spacing) + margins.top() + margins.bottom()

        # Set minimum height
        self.grid_container.setMinimumHeight(height)

    def _on_tile_clicked(self, item_data):
        """
        Handle tile click event with toggle support.

        Args:
            item_data: Data from the clicked tile
        """
        # Check if this is the already selected tile
        is_currently_selected = (self.selected_item is not None and
                                 self._compare_items(item_data, self.selected_item))

        # Update selection state regardless of toggle feature
        # This ensures we always emit a signal with the clicked item
        self.selected_item = None if (
                    is_currently_selected and hasattr(self, 'allow_toggle') and self.allow_toggle) else item_data

        # Update selection state of all tiles
        for tile in self.tiles:
            if self.selected_item is None:
                # If toggling off, deselect all
                tile.set_selected(False)
            else:
                # Otherwise, select only the matching one
                tile.set_selected(self._compare_items(tile.data, self.selected_item))

        # Always emit the clicked item, even on deselection
        # This ensures consistent behavior in step handling
        self.item_selected.emit(item_data)

    def _compare_items(self, item1, item2):
        """
        Compare two items to determine if they represent the same entity.

        Args:
            item1: First item data
            item2: Second item data

        Returns:
            bool: True if items represent the same entity
        """
        if not item1 or not item2:
            return False

        # Compare first values in each dictionary
        try:
            value1 = next(iter(item1.values()))
            value2 = next(iter(item2.values()))
            return value1 == value2
        except:
            return False

    def clear(self):
        """Clear all tiles from the grid."""
        # Remove all widgets from grid
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:  # Check if the item has an associated widget
                    self.grid_layout.removeWidget(widget)
                    widget.deleteLater()
                else:
                    # Handle spacers or other layout items without widgets
                    self.grid_layout.removeItem(item)

        # Clear tiles list and selection
        self.tiles = []
        self.selected_item = None

    def set_selected(self, item_data):
        """
        Set the selected item.

        Args:
            item_data: Data dictionary of the item to select
        """
        if not item_data:
            # Clear selection if None provided
            self.selected_item = None
            for tile in self.tiles:
                tile.set_selected(False)
            return

        # Update selected item
        self.selected_item = item_data

        # Update tile selection states
        for tile in self.tiles:
            tile.set_selected(self._compare_items(tile.data, item_data))

    def set_columns(self, columns):
        """
        Set the number of columns in the grid.

        Args:
            columns: Number of columns
        """
        if columns == self.columns or columns < 1:
            return

        # Update columns
        self.columns = columns

        # Update column stretch factors
        for i in range(self.columns):
            self.grid_layout.setColumnStretch(i, 1)

        # Re-layout existing tiles
        if self.tiles:
            # Get existing data and selection state
            existing_data = [tile.data for tile in self.tiles]
            existing_icons = []

            # Capture icon paths if available
            for tile in self.tiles:
                if hasattr(tile, 'icon_path'):
                    existing_icons.append(tile.icon_path)
                else:
                    existing_icons.append(None)

            # Remember selected item
            selected_item = self.selected_item

            # Clear grid and tiles list without deleting widgets yet
            for tile in self.tiles:
                self.grid_layout.removeWidget(tile)

            # Now it's safe to clear the list
            self.tiles.clear()

            # Create new tiles with the same data
            for i, (data, icon) in enumerate(zip(existing_data, existing_icons)):
                # Create new tile
                tile = GridTile(data, icon, is_selected=(self._compare_items(data, selected_item) if selected_item else False))
                tile.clicked.connect(self._on_tile_clicked)

                # Add to layout with new positioning
                row = i // self.columns
                col = i % self.columns
                self.grid_layout.addWidget(tile, row, col)
                self.tiles.append(tile)

        # Update container size
        self._update_container_size()

    def adjust_columns_to_width(self, width):
        """
        Automatically adjust columns based on available width.

        Args:
            width: Available width in pixels
        """
        # Calculate optimal column count based on available width
        min_tile_width = 90   # Minimum acceptable tile width
        ideal_tile_width = 110  # Ideal tile width for aesthetics

        spacing = self.grid_layout.spacing()
        margins = self.grid_layout.contentsMargins()

        # Calculate available width
        available_width = width - margins.left() - margins.right()

        # Calculate maximum number of columns that would fit
        max_columns = max(1, (available_width + spacing) // (min_tile_width + spacing))

        # Ideal number of columns (prefer slightly larger tiles if space permits)
        ideal_columns = max(1, (available_width + spacing) // (ideal_tile_width + spacing))

        # Choose the best number of columns
        new_columns = max(ideal_columns, min(max_columns, self.columns + 1))

        # Update columns if different
        if new_columns != self.columns:
            self.set_columns(new_columns)
            return True
        return False

    def resizeEvent(self, event):
        """Handle resize events to adjust column count."""
        super().resizeEvent(event)

        # Get the current width of the viewport
        viewport_width = self.scroll_area.viewport().width()

        # Adjust columns to new width
        if self.adjust_columns_to_width(viewport_width):
            # Reload the grid if columns changed
            if self.tiles:
                existing_data = [tile.data for tile in self.tiles]
                existing_selected = self.selected_item

                # Store icon paths
                icon_paths = []
                for tile in self.tiles:
                    if hasattr(tile, 'icon_path'):
                        icon_paths.append(tile.icon_path)
                    else:
                        icon_paths.append(None)

                # Create icon getter
                def get_stored_icon(item, index):
                    if index < len(icon_paths):
                        return icon_paths[index]
                    return None

                # Clear and repopulate
                self.clear()

                # Re-add items with new column layout
                for i, item in enumerate(existing_data):
                    # Get icon path if needed
                    icon_path = get_stored_icon(item, i)

                    # Check if this item should be selected
                    is_selected = (existing_selected is not None and
                                  self._compare_items(item, existing_selected))

                    # Create tile
                    tile = GridTile(item, icon_path, is_selected)
                    tile.clicked.connect(self._on_tile_clicked)

                    # Calculate position with new column count
                    row = i // self.columns
                    col = i % self.columns

                    # Add to grid
                    self.grid_layout.addWidget(tile, row, col, 1, 1, Qt.AlignCenter)

                    # Store reference to tile
                    self.tiles.append(tile)

                # Restore selection
                self.selected_item = existing_selected