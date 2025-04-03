"""
Brand selection widget for the parts navigation system.
The first step in the parts navigation hierarchy with elegant styling and internet logos.
"""
from PyQt5.QtWidgets import (QVBoxLayout, QFrame, QHBoxLayout,
                             QLabel, QSizePolicy, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from widgets.parts_navigation.base_step_widget import BaseStepWidget
from widgets.parts_navigation.ui_utils import SearchBox
from widgets.parts_navigation.brand_widget.brand_tile_widget import BrandTileWidget
from widgets.parts_navigation.logo_downloader import LogoManager
from widgets.parts_navigation.database_worker import DatabaseOperator
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.brand')

class BrandWidget(BaseStepWidget):
    """
    First step in the parts navigation - selecting a car brand
    Displays a grid of brands with logos loaded from the internet
    """
    # Signal emitted when a brand is selected
    brand_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        # Initialize database operator
        self.db_operator = DatabaseOperator(db)

        # Initialize logo manager
        self.logo_manager = LogoManager()

        # Set up data
        self.brands = []
        self.filtered_brands = []
        self.brand_tiles = []

        # Call parent init after our initialization
        super().__init__(translator, db, parent)

    def setup_ui(self):
        """Initialize and arrange UI elements with elegant spacing and clean design"""
        # Call parent setup first
        super().setup_ui()

        # Update title with refined typography
        self.title.setText(self.translator.t('select_brand'))
        title_font = self.title.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title.setFont(title_font)

        # Content container for better organization
        content_container = QFrame()
        content_container.setObjectName("contentContainer")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(15, 15, 15, 15)
        content_layout.setSpacing(15)

        # Description text with clean styling
        self.description = QLabel(self.translator.t('select_brand_subtitle'))
        self.description.setObjectName("stepDescription")
        self.description.setAlignment(Qt.AlignCenter)
        self.description.setWordWrap(True)
        content_layout.addWidget(self.description)

        # Search box with clean styling
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_brands_placeholder',
            label_key='search_brands'
        )
        self.search_box.search_changed.connect(self.filter_brands)
        content_layout.addWidget(self.search_box)

        # Scroll area for brands grid
        self.scroll_area = QFrame()
        self.scroll_area.setObjectName("brandsScrollArea")
        scroll_layout = QVBoxLayout(self.scroll_area)
        scroll_layout.setContentsMargins(5, 5, 5, 5)

        # Create grid for brands
        self.brands_grid = QGridLayout()
        self.brands_grid.setContentsMargins(10, 10, 10, 10)
        self.brands_grid.setSpacing(12)
        self.brands_grid.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Add grid to scroll area
        scroll_layout.addLayout(self.brands_grid)
        scroll_layout.addStretch(1)  # Push all content to the top

        # Add scroll area to content layout
        content_layout.addWidget(self.scroll_area, 1)

        # Add content container to main layout
        self.main_layout.addWidget(content_container, 1)

        # Update help text with clean typography
        self.help_text.setText(self.translator.t('select_brand_help'))
        help_font = self.help_text.font()
        help_font.setItalic(True)
        self.help_text.setFont(help_font)

        # Connect to logo manager signals
        self.logo_manager.logo_ready.connect(self._update_brand_tile_logo)

    def apply_theme(self):
        """Apply clean, elegant theme that matches the system"""
        # Call parent apply_theme first
        super().apply_theme()

        # Get theme colors
        bg_color = get_color('background')
        card_bg = get_color('card_bg')
        text_color = get_color('text')
        highlight = get_color('highlight')
        border_color = get_color('border')
        secondary_text = get_color('secondary_text')

        # Apply clean styling to content container
        content_style = f"""
            #contentContainer {{
                background-color: {card_bg};
                border-radius: 8px;
                border: 1px solid {border_color};
            }}
            
            #stepDescription {{
                color: {secondary_text};
                font-size: 13px;
                margin-bottom: 5px;
            }}
            
            #brandsScrollArea {{
                background-color: {bg_color};
                border-radius: 6px;
                border: 1px solid {border_color};
            }}
        """

        # Apply all styles
        self.setStyleSheet(self.styleSheet() + content_style)

        # Apply theme to our specific components
        self.search_box.apply_theme()

        # Apply theme to all brand tiles
        for tile in self.brand_tiles:
            tile.apply_theme()

    def update_translations(self):
        """Update all translatable text"""
        # Update our own texts
        self.title.setText(self.translator.t('select_brand'))
        self.description.setText(self.translator.t('select_brand_subtitle'))
        self.help_text.setText(self.translator.t('select_brand_help'))

        # Update child widgets
        self.search_box.update_translations()

        # Reload brands to refresh translations
        self.populate_brands_grid()

    def on_show(self):
        """Called when this step is shown"""
        # Call parent method first
        super().on_show()

        # Load brands when the widget is shown
        self.load_brands()

    def on_brand_clicked(self, brand):
        """Handle click on a brand tile"""
        logger.info(f"Brand clicked: {brand['brand']}")

        # Store the selected brand
        self.step_data = brand

        # Update selection status of all tiles
        for tile in self.brand_tiles:
            is_selected = (tile.brand_data.get('brand') == brand.get('brand'))
            tile.set_selected(is_selected)

        # Emit signal for main container
        self.brand_selected.emit(brand)
        self.step_completed.emit(brand)

    def load_brands(self):
        """Load car brands from database with clean loading indicator"""
        # Show loading indicator
        self.show_loading(True)

        # Clear existing data
        self.brands = []
        self.filtered_brands = []
        self.clear_brands_grid()

        # Execute database operation
        self.db_operator.execute(
            "get_brands",
            self.on_brands_loaded,
            self.on_database_error
        )

    def on_brands_loaded(self, brands):
        """Handle loaded brands data"""
        # Hide loading indicator
        self.show_loading(False)

        # Store brands
        self.brands = brands if brands else []
        self.filtered_brands = self.brands.copy()

        logger.info(f"Loaded {len(self.brands)} unique brands")

        # Populate the grid
        self.populate_brands_grid()

        # Restore selection if already had one
        if self.step_data:
            self._update_selected_brand(self.step_data)

    def _update_selected_brand(self, brand):
        """Update the selected brand in the grid"""
        if not brand:
            return

        for tile in self.brand_tiles:
            is_selected = (tile.brand_data.get('brand') == brand.get('brand'))
            tile.set_selected(is_selected)

    def on_database_error(self, error_msg):
        """Handle database error with clean error visualization"""
        self.handle_error(f"Error loading brands: {error_msg}")

        # Clean up UI
        self.show_loading(False)
        self.clear_brands_grid()
        self.filtered_brands = []
        self.brands = []

    def filter_brands(self, search_text):
        """Filter brands based on search text"""
        search_text = search_text.lower().strip()

        if not search_text:
            # If search is empty, show all brands
            self.filtered_brands = self.brands.copy()
        else:
            # Filter brands that contain the search text
            self.filtered_brands = [
                brand for brand in self.brands
                if search_text in brand['brand'].lower()
            ]

        # Repopulate the grid with filtered brands
        self.populate_brands_grid()

    def populate_brands_grid(self):
        """Populate the grid with brand items using internet logos"""
        # Clear existing grid
        self.clear_brands_grid()

        # If no brands, show empty message
        if not self.filtered_brands:
            empty_label = QLabel(self.translator.t('no_brands_found'))
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setWordWrap(True)
            empty_label.setObjectName("emptyMessage")

            # Style the empty message
            font = QFont()
            font.setPointSize(12)
            font.setItalic(True)
            empty_label.setFont(font)

            self.brands_grid.addWidget(empty_label, 0, 0, 1, 4)  # span 4 columns
            return

        # Calculate columns based on widget width
        columns = 4  # Default

        # Add brand tiles to grid
        for i, brand in enumerate(self.filtered_brands):
            # Create tile with internet logo loading
            is_selected = (self.step_data is not None and
                          self.step_data.get('brand') == brand.get('brand'))

            tile = BrandTileWidget(brand, self.logo_manager, is_selected)
            tile.clicked.connect(self.on_brand_clicked)

            # Calculate position
            row = i // columns
            col = i % columns

            # Add to grid
            self.brands_grid.addWidget(tile, row, col)

            # Store reference
            self.brand_tiles.append(tile)

    def clear_brands_grid(self):
        """Clear all brand tiles from the grid"""
        # Remove all widgets from grid
        while self.brands_grid.count():
            item = self.brands_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Clear tile list
        self.brand_tiles = []

    def _update_brand_tile_logo(self, brand_name, pixmap):
        """Update brand tile when logo is downloaded"""
        # Find matching tiles and update them
        for tile in self.brand_tiles:
            if tile.brand_data.get('brand', '').lower() == brand_name.lower():
                # The tile will update itself since it's connected to logo_manager signals
                pass

    def reset(self):
        """Reset this step's data"""
        # Call parent reset
        super().reset()

        # Clear UI elements
        if hasattr(self, 'search_box'):
            self.search_box.clear()

        self.clear_brands_grid()

        # Reset data
        self.brands = []
        self.filtered_brands = []

    def can_proceed(self):
        """Check if user can proceed to next step"""
        return self.step_data is not None