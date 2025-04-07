"""
TilesGrid component for organizing selection tiles.

A premium grid layout for organizing selection tiles with responsive design,
elegant styling and proper toggle functionality.
"""
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (QFrame, QGridLayout, QLabel, QScrollArea,
                             QWidget, QVBoxLayout, QSizePolicy, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QSize


from themes import get_color
from .grid_tile import GridTile
from logger import get_logger

# Add this logger definition right after the imports
logger = get_logger('parts_navigation.components.tiles_grid')

"""
This is a self-contained fix for TilesGrid to ensure proper grid layout.
Replace your entire TilesGrid class with this implementation or modify your 
existing class to match these key elements.
"""


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
        self.grid_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Grid layout - CRITICAL: Set proper column configuration
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(6, 6, 6, 6)
        self.grid_layout.setSpacing(8)  # Add some spacing between items
        self.grid_layout.setHorizontalSpacing(8)  # Explicit horizontal spacing
        self.grid_layout.setVerticalSpacing(8)  # Explicit vertical spacing
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        # Configure columns EXPLICITLY - IMPORTANT!
        for i in range(self.columns):
            self.grid_layout.setColumnStretch(i, 1)
            self.grid_layout.setColumnMinimumWidth(i, 90)  # Set a minimum width for each column

        # Add container to scroll area
        self.scroll_area.setWidget(self.grid_container)

        # Add scroll area to main layout
        layout.addWidget(self.scroll_area)

    def _create_tile(self, item, index, icon_getter=None):
        """
        Create a grid tile for an item.

        Args:
            item: Data dictionary for the tile
            index: Index of the item
            icon_getter: Optional function to get icon for the item

        Returns:
            GridTile: The created tile
        """
        # Get icon path if icon getter is provided
        icon_path = None
        if icon_getter:
            try:
                icon_path = icon_getter(item)
            except Exception as e:
                logger.error(f"Error getting icon at index {index}: {e}")

        # Create tile with the item data and icon
        from .grid_tile import GridTile
        tile = GridTile(item, icon_path)

        # IMPORTANT: Configure tile for grid layout
        tile.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        tile.setMinimumSize(90, 110)  # Minimum size

        # Connect click signal
        tile.clicked.connect(self._on_tile_clicked)

        return tile

    def populate(self, items, icon_getter=None):
        """
        Populate the grid with data items.

        Args:
            items: List of data dictionaries
            icon_getter: Optional function to get icon for an item
        """
        try:
            # Clear existing tiles
            self.clear()

            # CRITICAL - reset grid layout configuration
            for i in range(self.columns):
                self.grid_layout.setColumnStretch(i, 1)
                self.grid_layout.setColumnMinimumWidth(i, 90)

            # If no items, show empty message
            if not items:
                empty_label = QLabel(self.translator.t('no_items'))
                empty_label.setAlignment(Qt.AlignCenter)
                empty_label.setWordWrap(True)
                self.grid_layout.addWidget(empty_label, 0, 0, 1, self.columns)
                return

            # Set number of columns explicitly based on current width
            container_width = self.grid_container.width()
            if container_width > 0:
                # Calculate optimal columns based on width
                tile_width = 100  # Target width for tiles
                spacing = self.grid_layout.horizontalSpacing()
                margins = self.grid_layout.contentsMargins()
                available_width = container_width - margins.left() - margins.right()
                optimal_columns = max(1, int(available_width / (tile_width + spacing)))

                # Update columns if significantly different
                if abs(optimal_columns - self.columns) > 1:
                    self.columns = optimal_columns
                    # Reset column configuration
                    for i in range(self.columns):
                        self.grid_layout.setColumnStretch(i, 1)
                        self.grid_layout.setColumnMinimumWidth(i, 90)

            logger.info(f"Populating grid with {len(items)} items using {self.columns} columns")

            # Add items in batches
            chunk_size = 8
            for start_idx in range(0, len(items), chunk_size):
                end_idx = min(start_idx + chunk_size, len(items))
                chunk = items[start_idx:end_idx]

                # Process this chunk
                for i, item in enumerate(chunk):
                    # Calculate row and column
                    absolute_idx = i + start_idx
                    row = absolute_idx // self.columns
                    col = absolute_idx % self.columns

                    logger.debug(f"Adding item {absolute_idx} at position row={row}, col={col}")

                    try:
                        # Create tile
                        tile = self._create_tile(item, absolute_idx, icon_getter)

                        # Add to grid at specific position
                        self.grid_layout.addWidget(tile, row, col, 1, 1)

                        # Add to tiles list
                        self.tiles.append(tile)
                    except Exception as e:
                        logger.error(f"Error creating tile at index {absolute_idx}: {e}")

                # Process events after each chunk
                QApplication.processEvents()

            # Force layout update
            self.grid_layout.update()
            self.grid_container.updateGeometry()
            QApplication.processEvents()

            # Verify the grid configuration
            self._verify_grid_layout()

        except Exception as e:
            logger.error(f"Error in populate: {e}")

    def _verify_grid_layout(self):
        """Verify and debug grid layout configuration."""
        try:
            col_count = 0
            for i in range(self.grid_layout.columnCount()):
                if self.grid_layout.columnStretch(i) > 0:
                    col_count += 1

            logger.info(f"Grid has {col_count} active columns configured")
            logger.info(f"Total tiles: {len(self.tiles)}")

            # Check for visible tiles
            visible_count = 0
            for tile in self.tiles:
                if tile.isVisible():
                    visible_count += 1

            logger.info(f"Visible tiles: {visible_count}")

        except Exception as e:
            logger.error(f"Error verifying grid layout: {e}")

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

    def resizeEvent(self, event):
        """Handle resize events to adjust column count."""
        super().resizeEvent(event)

        # Only adjust columns if we have a significant size change
        if abs(event.size().width() - event.oldSize().width()) > 50:
            self.adjust_columns_to_width(event.size().width())

    def adjust_columns_to_width(self, width):
        """
        Automatically adjust columns based on available width.

        Args:
            width: Available width in pixels
        """
        # Calculate optimal column count based on available width
        tile_width = 100  # Target width for each tile
        min_tile_width = 90  # Minimum acceptable tile width

        spacing = self.grid_layout.horizontalSpacing()
        margins = self.grid_layout.contentsMargins()

        # Calculate available width for the grid
        available_width = width - margins.left() - margins.right()

        # Calculate maximum number of columns that would fit
        max_columns = max(1, (available_width + spacing) // (min_tile_width + spacing))

        # Calculate ideal number of columns
        ideal_columns = max(1, (available_width + spacing) // (tile_width + spacing))

        # Choose a reasonable number of columns
        new_columns = min(max_columns, max(ideal_columns, 1))

        # Update columns if different enough to matter
        if abs(new_columns - self.columns) > 0:
            logger.info(f"Adjusting columns from {self.columns} to {new_columns}")
            self.set_columns(new_columns)
            return True
        return False

    def set_columns(self, columns):
        """
        Set the number of columns in the grid.

        Args:
            columns: Number of columns
        """
        if columns == self.columns or columns < 1:
            return

        logger.info(f"Setting grid to {columns} columns")

        # Update columns
        self.columns = columns

        # Clear and rebuild grid configuration
        for i in range(self.grid_layout.columnCount()):
            self.grid_layout.setColumnStretch(i, 0)

        # Set new column stretch factors
        for i in range(columns):
            self.grid_layout.setColumnStretch(i, 1)
            self.grid_layout.setColumnMinimumWidth(i, 90)

        # Only re-layout if we have tiles
        if self.tiles:
            # Remember current selection and data
            existing_data = [tile.data for tile in self.tiles]
            existing_icons = []
            selected_item = self.selected_item

            # Store icon paths
            for tile in self.tiles:
                if hasattr(tile, 'icon_path'):
                    existing_icons.append(tile.icon_path)
                else:
                    existing_icons.append(None)

            # Clear grid
            self.clear()

            # Re-add tiles with new layout
            for i, (data, icon) in enumerate(zip(existing_data, existing_icons)):
                # Calculate new position
                row = i // self.columns
                col = i % self.columns

                # Create new tile
                tile = self._create_tile(data, i, lambda item: icon)
                tile.set_selected(self.selected_item is not None and self._compare_items(data, selected_item))

                # Add to new position
                self.grid_layout.addWidget(tile, row, col, 1, 1)
                self.tiles.append(tile)

            # Force update
            self.grid_layout.update()
            self.updateGeometry()

            # Restore selection
            self.selected_item = selected_item

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
        hover_bg = get_color('button_hover', QColor(card_bg).lighter(115).name())

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