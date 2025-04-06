"""
Brand selection step for the parts navigation system.

A premium step for selecting car brands with elegant styling and animations.
"""
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QFrame, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from ..base import BaseStepWidget
from ..components.search_box import SearchBox
from ..components.tiles_grid import TilesGrid
from ..components.logo_manager import LogoManager
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.steps.brand')


class BrandStep(BaseStepWidget):
    """
    First step in the parts navigation - selecting a car brand

    Features:
    - Clean, elegant layout with premium styling
    - Brand logos loaded from the internet with caching
    - Responsive grid layout
    - Search functionality
    - Smooth animations
    """
    # Signal emitted when a brand is selected
    brand_selected = pyqtSignal(dict)

    def __init__(self, translator, db, db_operator=None, parent=None):
        """
        Initialize the brand step.

        Args:
            translator: Translator for localization
            db: Database connection
            db_operator: Shared database operator (optional)
            parent: Parent widget
        """
        # Initialize logo manager
        self.logo_manager = LogoManager()

        # Use the provided db_operator or create our own if none was provided
        if db_operator:
            self.db_operator = db_operator
            self.owns_db_operator = False
        else:
            # Backwards compatibility - create our own operator
            from ..utils.database_worker import DatabaseOperator
            self.db_operator = DatabaseOperator(db)
            self.owns_db_operator = True

        # Set up data
        self.brands = []
        self.filtered_brands = []

        # Call parent init after our initialization
        super().__init__(translator, db, parent)

    def setup_ui(self):
        """Initialize and arrange UI elements with compact styling."""
        # Call parent setup first
        super().setup_ui()

        # Set title
        self.title.setText(self.translator.t('select_brand'))

        # Description text with compact styling
        self.description = QLabel(self.translator.t('select_brand_subtitle'))
        self.description.setObjectName("stepDescription")
        self.description.setAlignment(Qt.AlignCenter)
        self.description.setWordWrap(True)
        self.description.setMaximumHeight(30)  # Limit height

        # Apply refined typography but smaller
        desc_font = QFont("SF Pro Text", 12)  # Reduced from 14
        desc_font.setItalic(True)
        self.description.setFont(desc_font)

        self.content_layout.addWidget(self.description)

        # Search box with premium styling but more compact
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_brands_placeholder',
            label_key='search_brands',
            show_button=False
        )
        self.search_box.search_changed.connect(self.filter_brands)
        self.search_box.setMaximumHeight(38)  # Limit height
        self.content_layout.addWidget(self.search_box)

        # Brands grid with premium styling - takes most space
        self.brands_grid = TilesGrid(self.translator, columns=4)
        self.brands_grid.item_selected.connect(self.on_brand_clicked)

        # Set size policy for better display
        self.brands_grid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Ensure grid gets plenty of space
        self.brands_grid.setMinimumHeight(280)  # Still gives enough height for content

        self.content_layout.addWidget(self.brands_grid, 10)  # Give it most of the space with stretch factor

        # Simplify help text to save space
        self.help_text.setText(self.translator.t('select_brand_help'))

    def apply_theme(self):
        """Apply premium styling based on system theme."""
        # Call parent apply_theme first
        super().apply_theme()

        # Get theme colors
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        text_color = get_color('text', '#E2E8F0')
        highlight = get_color('highlight', '#4299E1')
        secondary_text = get_color('secondary_text', '#A0AEC0')

        # Apply styling to description
        self.description.setStyleSheet(f"""
            #stepDescription {{
                color: {secondary_text};
                font-size: 14px;
                margin-bottom: 10px;
                padding: 5px;
            }}
        """)

        # Apply theme to search box and brands grid
        self.search_box.apply_theme()
        self.brands_grid.apply_theme()

    def update_translations(self):
        """Update all translatable text when language changes."""
        # Call parent first
        super().update_translations()

        # Update our texts
        self.title.setText(self.translator.t('select_brand'))
        self.description.setText(self.translator.t('select_brand_subtitle'))
        self.help_text.setText(self.translator.t('select_brand_help'))

        # Update child components
        self.search_box.update_translations()

        # Reload brands to refresh translations
        self.populate_brands_grid()

    def on_brands_loaded(self, brands):
        """
        Handle loaded brands data.

        Args:
            brands: List of brand dictionaries
        """
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
        """
        Handle database error.

        Args:
            error_msg: Error message
        """
        self.handle_error(f"Error loading brands: {error_msg}")

        # Clean up UI state
        self.show_loading(False)
        self.brands_grid.clear()

        # Create empty message
        empty_label = QLabel(self.translator.t('brands_load_error'))
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setWordWrap(True)
        self.brands_grid.grid_layout.addWidget(empty_label, 0, 0, 1, 4)  # span 4 columns

    def filter_brands(self, search_text):
        """
        Filter brands based on search text.

        Args:
            search_text: Search text to filter by
        """
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
        """Populate the grid with brand tiles."""

        # Define function to get icon path
        def get_brand_icon(brand):
            """Get brand icon with fallbacks for variant names"""
            # Extract brand name from data
            brand_name = brand['brand'].lower()

            # Handle specific brand name variants
            if 'byd' in brand_name:
                return "resources/brands/byd.png"
            elif 'chery' in brand_name or 'cherry' in brand_name:
                return "resources/brands/chery.png"
            elif 'gaz' in brand_name:
                return "resources/brands/gaz.png"
            elif brand_name == 'mg' or 'morris garages' in brand_name:
                return "resources/brands/mg.png"
            elif 'iveco' in brand_name:
                return "resources/brands/iveco.png"
            elif 'mini' in brand_name:
                return "resources/brands/mini.png"

            # Standard approach for other brands
            normalized_name = brand_name.replace(' ', '_')
            return f"resources/brands/{normalized_name}.png"

        # Populate the grid
        self.brands_grid.populate(self.filtered_brands, get_brand_icon)

    def _update_brand_logo(self, brand_name, pixmap):
        """
        Update brand logo when downloaded.

        Args:
            brand_name: Brand name
            pixmap: Logo pixmap
        """
        # Refresh the grid to show the updated logo
        # In a full implementation, we would update just the affected tile
        self.populate_brands_grid()

    def on_brand_clicked(self, brand):
        """
        Handle brand selection.

        Args:
            brand: Selected brand data
        """
        logger.info(f"Brand selected: {brand}")

        # Store selected brand
        self.step_data = brand

        # Emit signals
        self.brand_selected.emit(brand)
        self.step_completed.emit(brand)

    def reset(self):
        """Reset this step's data and UI state."""
        # Call parent reset
        super().reset()

        # Clear search and grid
        self.search_box.clear()
        self.brands_grid.clear()

        # Clear data
        self.brands = []
        self.filtered_brands = []

    def can_proceed(self):
        """Check if we can proceed to the next step."""
        return self.step_data is not None

    def on_show(self):
        """Called when this step is shown."""
        # Call parent first for consistent behavior
        super().on_show()

        # Show immediate loading indicator
        self.show_loading(True)

        # IMPORTANT: Use a timer to allow the UI to update
        # This makes the loading indicator appear immediately
        QTimer.singleShot(50, self.load_brands)

    def load_brands(self):
        """Load car brands from the database."""
        # Loading indicator is now shown by on_show method

        # Clear existing data
        self.brands = []
        self.filtered_brands = []
        self.brands_grid.clear()

        # Pre-populate with placeholder data while we wait for real data
        placeholder_brands = [
            {'brand': 'Loading...'},
            {'brand': 'Please wait...'},
            {'brand': 'Retrieving brands...'}
        ]
        self.brands_grid.populate(placeholder_brands)

        # Now execute database operation in background
        self.db_operator.execute(
            "get_brands",
            self.on_brands_loaded,
            self.on_database_error
        )

    def on_hide(self):
        """Called when this step is hidden."""
        # Call parent method first
        super().on_hide()

        # Cancel any running database operations
        if hasattr(self, 'db_operator') and self.db_operator:
            # Only terminate running operations, don't destroy the operator
            if hasattr(self.db_operator, 'worker') and self.db_operator.worker:
                if hasattr(self.db_operator.worker, 'finished'):
                    try:
                        self.db_operator.worker.finished.disconnect()
                    except Exception:
                        pass
                if hasattr(self.db_operator.worker, 'error'):
                    try:
                        self.db_operator.worker.error.disconnect()
                    except Exception:
                        pass

    def __del__(self):
        """Clean up resources when the step is destroyed."""
        # Only clean up the database operator if we own it
        if hasattr(self, 'owns_db_operator') and self.owns_db_operator and hasattr(self, 'db_operator'):
            try:
                self.db_operator.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up db_operator in {self.__class__.__name__}: {e}")