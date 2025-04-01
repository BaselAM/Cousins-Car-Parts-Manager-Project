"""
Brand selection widget for the parts navigation system.
The first step in the parts navigation hierarchy.
"""
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt, pyqtSignal

from .base_step_widget import BaseStepWidget
from .ui_utils import SearchBox, TilesGrid
from .database_worker import DatabaseOperator
from logger import get_logger

logger = get_logger('parts_navigation.brand')

class BrandWidget(BaseStepWidget):
    """
    First step in the parts navigation - selecting a car brand
    Displays a grid of brands with logos
    """
    # Signal emitted when a brand is selected
    brand_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        super().__init__(translator, db, parent)

        # Initialize database operator
        self.db_operator = DatabaseOperator(self.db)

        # Set up data
        self.brands = []
        self.filtered_brands = []

    def setup_ui(self):
        """Initialize and arrange UI elements"""
        # Call parent setup first
        super().setup_ui()

        # Update title
        self.title.setText(self.translator.t('select_brand'))

        # Search box
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_brands_placeholder',
            label_key='search_brands'
        )
        self.search_box.search_changed.connect(self.filter_brands)
        self.main_layout.addWidget(self.search_box)

        # Create scroll area for brands grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Container for the brands
        self.brands_container = QFrame()
        container_layout = QVBoxLayout(self.brands_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Brands grid
        self.brands_grid = TilesGrid(self.translator, columns=4)
        self.brands_grid.item_selected.connect(self.on_brand_clicked)
        container_layout.addWidget(self.brands_grid)

        # Add scroll area to main layout
        scroll_area.setWidget(self.brands_container)
        self.main_layout.addWidget(scroll_area, 1)  # Takes most space

        # Update help text
        self.help_text.setText(self.translator.t('select_brand_help'))

    def apply_theme(self):
        """Apply current theme"""
        # Call parent apply_theme first
        super().apply_theme()

        # Apply theme to our specific components
        self.search_box.apply_theme()
        self.brands_grid.apply_theme()

    def update_translations(self):
        """Update all translatable text"""
        # Update our own texts
        self.title.setText(self.translator.t('select_brand'))
        self.help_text.setText(self.translator.t('select_brand_help'))

        # Update child widgets
        self.search_box.update_translations()

        # Reload brands to refresh translations
        self.populate_brands_grid()

    def on_show(self):
        """Called when this step is shown"""
        # Load brands when the widget is shown
        self.load_brands()

    def on_brand_clicked(self, brand):
        """Handle click on a brand tile"""
        logger.info(f"Brand clicked: {brand['brand']}")

        # Store the selected brand
        self.step_data = brand

        # Emit signal for main container
        self.brand_selected.emit(brand)
        self.step_completed.emit(brand)

    def load_brands(self):
        """Load car brands from database"""
        # Show loading indicator
        self.show_loading(True)

        # Clear existing data
        self.brands = []
        self.filtered_brands = []
        self.brands_grid.clear()

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
            self.brands_grid.set_selected(self.step_data)

    def on_database_error(self, error_msg):
        """Handle database error"""
        self.handle_error(f"Error loading brands: {error_msg}")
        self.show_loading(False)

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
        """Populate the grid with brand items"""
        # Define function to get icon path for a brand
        def get_brand_icon(brand):
            brand_name = brand['brand'].lower().replace(' ', '_')
            return f"resources/logos/{brand_name}.png"

        # Populate the grid
        self.brands_grid.populate(self.filtered_brands, get_brand_icon)

    def reset(self):
        """Reset this step's data"""
        super().reset()
        self.search_box.clear()
        self.brands_grid.clear()
        self.brands = []
        self.filtered_brands = []

    def can_proceed(self):
        """Check if user can proceed to next step"""
        return self.step_data is not None