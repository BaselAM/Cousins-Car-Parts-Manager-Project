"""
Brands grid widget for the parts navigation system.
Manages the display and layout of brand tiles in an elegant grid layout.
"""
from PyQt5.QtWidgets import (QFrame, QGridLayout, QLabel,
                             QSizePolicy, QScrollArea, QVBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from .brand_tile_widget import BrandTileWidget
from themes import get_color


class BrandsGridWidget(QFrame):
    """
    A grid display for brand tiles with elegant layout and selection handling.
    """
    # Signal emitted when a brand is selected
    brand_selected = pyqtSignal(dict)

    def __init__(self, translator, columns=4, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.columns = columns
        self.brand_tiles = []
        self.selected_brand = None
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Set up the UI with clean, elegant layout"""
        self.setObjectName("brandsGrid")

        # Set size policy for responsive layout
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area for the grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Container for the grid
        self.grid_container = QFrame()
        self.grid_container.setObjectName("gridContainer")

        # Grid layout
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        self.grid_layout.setSpacing(12)

        # Set up equal column stretch
        for i in range(self.columns):
            self.grid_layout.setColumnStretch(i, 1)

        # Add container to scroll area
        self.scroll_area.setWidget(self.grid_container)

        # Add scroll area to main layout
        layout.addWidget(self.scroll_area)

    def apply_theme(self):
        """Apply elegant theme styling"""
        # Get colors from theme
        bg_color = get_color('background')
        card_bg = get_color('card_bg')
        border_color = get_color('border')

        # Apply styling
        self.setStyleSheet(f"""
            #brandsGrid {{
                background-color: transparent;
                border: none;
            }}

            #gridContainer {{
                background-color: {bg_color};
                border: none;
            }}

            QScrollBar:vertical {{
                background: {bg_color};
                width: 10px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background: {border_color};
                min-height: 20px;
                border-radius: 5px;
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        # Apply theme to all brand tiles
        for tile in self.brand_tiles:
            tile.apply_theme()

    def populate(self, brands, icon_getter=None):
        """
        Populate the grid with brand tiles

        Args:
            brands: List of brand dictionaries
            icon_getter: Function to get icon path for a brand
        """
        # Clear existing tiles
        self.clear()

        # If no brands, show empty message
        if not brands:
            empty_label = QLabel(self.translator.t('no_brands_found'))
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setWordWrap(True)

            # Style the empty message
            font = QFont()
            font.setPointSize(12)
            font.setItalic(True)
            empty_label.setFont(font)

            self.grid_layout.addWidget(empty_label, 0, 0, 1, self.columns)
            return

        # Add brand tiles to grid
        for i, brand in enumerate(brands):
            # Get icon path
            icon_path = None
            if icon_getter:
                icon_path = icon_getter(brand)

            # Create tile
            is_selected = (self.selected_brand is not None and
                           self.selected_brand.get('brand') == brand.get('brand'))

            tile = BrandTileWidget(brand, icon_path, is_selected)
            tile.clicked.connect(self._on_brand_tile_clicked)

            # Add to grid
            row = i // self.columns
            col = i % self.columns
            self.grid_layout.addWidget(tile, row, col)

            # Store reference to tile
            self.brand_tiles.append(tile)

    def _on_brand_tile_clicked(self, brand):
        """Handle brand tile click event"""
        # Update selected brand
        self.selected_brand = brand

        # Update selection state of all tiles
        for tile in self.brand_tiles:
            is_selected = (tile.brand_data.get('brand') == brand.get('brand'))
            tile.set_selected(is_selected)

        # Emit selection signal
        self.brand_selected.emit(brand)

    def clear(self):
        """Clear all brand tiles from the grid"""
        # Remove all widgets from grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear tile list and selection
        self.brand_tiles = []
        self.selected_brand = None

    def set_selected(self, brand):
        """Set the selected brand programmatically"""
        if not brand:
            return

        # Find matching tile and select it
        for tile in self.brand_tiles:
            if tile.brand_data.get('brand') == brand.get('brand'):
                self._on_brand_tile_clicked(brand)
                break