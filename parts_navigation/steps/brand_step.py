"""
Brand selection step for the parts navigation system.

A premium step for selecting car brands with elegant styling and animations.
"""
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QFrame, QSizePolicy, QApplication
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

    def setup_preloading(self, db_operator=None):
        """Set up preloading of brands and logos.

        Args:
            db_operator: Shared database operator (optional)
        """
        # Use the provided db_operator or create our own
        op = db_operator if db_operator else self.db_operator

        logger.info("Starting to preload brands data")

        # Load brands in background
        try:
            op.execute(
                "get_brands",
                self._handle_preloaded_brands,
                self._handle_preload_error
            )
        except Exception as e:
            logger.error(f"Error setting up brand preloading: {e}")

    def _handle_preloaded_brands(self, brands):
        """Handle preloaded brands data for faster display.

        Args:
            brands: List of brand dictionaries
        """
        try:
            # Store brands without triggering UI updates
            self.brands = brands if brands else []
            self.filtered_brands = self.brands.copy()

            logger.info(f"Preloaded {len(self.brands)} brands")

            # Start preloading logos for all brands
            brand_names = [brand['brand'] for brand in self.brands if 'brand' in brand]
            if brand_names and self.logo_manager:
                self.logo_manager.preload_logos(brand_names)
                logger.info(f"Started preloading {len(brand_names)} brand logos")
        except Exception as e:
            logger.error(f"Error handling preloaded brands: {e}")

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
        try:
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
        except Exception as e:
            logger.error(f"Error in on_brands_loaded: {e}")
            self.show_loading(False)

    def on_database_error(self, error_msg):
        """
        Handle database error.

        Args:
            error_msg: Error message
        """
        try:
            self.handle_error(f"Error loading brands: {error_msg}")

            # Clean up UI state
            self.show_loading(False)
            self.brands_grid.clear()

            # Create empty message
            empty_label = QLabel(self.translator.t('brands_load_error'))
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setWordWrap(True)
            self.brands_grid.grid_layout.addWidget(empty_label, 0, 0, 1, 4)  # span 4 columns
        except Exception as e:
            logger.error(f"Error in on_database_error: {e}")
            self.show_loading(False)

    def filter_brands(self, search_text):
        """
        Filter brands based on search text.

        Args:
            search_text: Search text to filter by
        """
        try:
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
        except Exception as e:
            logger.error(f"Error in filter_brands: {e}")

    def populate_brands_grid(self):
        """Populate the grid with brand tiles using cached logos when available."""
        try:
            def get_brand_icon(brand):
                """Get brand icon with optimized caching."""
                # Extract brand name from data
                brand_name = brand['brand']

                # Try to get from logo manager cache first for instant display
                if self.logo_manager:
                    cached_logo = self.logo_manager.get_logo_sync(brand_name)
                    if cached_logo is not None:  # Use is not None check to accept empty pixmaps
                        return cached_logo

                # Original fallback logic for file paths
                if 'byd' in brand_name.lower():
                    return "resources/brands/byd.png"
                elif 'chery' in brand_name.lower() or 'cherry' in brand_name.lower():
                    return "resources/brands/chery.png"
                elif 'gaz' in brand_name.lower():
                    return "resources/brands/gaz.png"
                elif brand_name.lower() == 'mg' or 'morris garages' in brand_name.lower():
                    return "resources/brands/mg.png"
                elif 'iveco' in brand_name.lower():
                    return "resources/brands/iveco.png"
                elif 'mini' in brand_name.lower():
                    return "resources/brands/mini.png"

                # Standard approach for other brands
                normalized_name = brand_name.lower().replace(' ', '_')
                return f"resources/brands/{normalized_name}.png"

            # Check if brands_grid exists
            if hasattr(self, 'brands_grid') and self.brands_grid:
                # Populate the grid with optimized brand loading
                self.brands_grid.populate(self.filtered_brands, get_brand_icon)
        except Exception as e:
            logger.error(f"Error in populate_brands_grid: {e}")

    def _update_brand_logo(self, brand_name, pixmap):
        """
        Update brand logo when downloaded.

        Args:
            brand_name: Brand name
            pixmap: Logo pixmap
        """
        try:
            # Refresh the grid to show the updated logo
            # In a full implementation, we would update just the affected tile
            self.populate_brands_grid()
        except Exception as e:
            logger.error(f"Error in _update_brand_logo: {e}")

    def on_brand_clicked(self, brand):
        """
        Handle brand selection.

        Args:
            brand: Selected brand data
        """
        try:
            logger.info(f"Brand selected: {brand}")

            # Store selected brand
            self.step_data = brand

            # Emit signals
            self.brand_selected.emit(brand)
            self.step_completed.emit(brand)
        except Exception as e:
            logger.error(f"Error in on_brand_clicked: {e}")

    def reset(self):
        """Reset this step's data and UI state."""
        try:
            # Call parent reset
            super().reset()

            # Clear search and grid
            if hasattr(self, 'search_box') and self.search_box:
                self.search_box.clear()

            if hasattr(self, 'brands_grid') and self.brands_grid:
                self.brands_grid.clear()

            # Clear data
            self.brands = []
            self.filtered_brands = []
        except Exception as e:
            logger.error(f"Error in reset: {e}")

    def can_proceed(self):
        """Check if we can proceed to the next step."""
        return self.step_data is not None

    def load_brands(self):
        """Load car brands from the database."""
        try:
            # Show loading indicator
            self.show_loading(True)

            # Clear existing data
            self.brands = []
            self.filtered_brands = []

            if hasattr(self, 'brands_grid') and self.brands_grid:
                self.brands_grid.clear()

            # Now execute database operation in background
            if hasattr(self, 'db_operator') and self.db_operator:
                self.db_operator.execute(
                    "get_brands",
                    self.on_brands_loaded,
                    self.on_database_error
                )
            else:
                logger.error("db_operator not available for brand loading")
                self.on_database_error("Database operator not available")
        except Exception as e:
            logger.error(f"Error in load_brands: {e}")
            self.on_database_error(f"Error loading brands: {e}")

    def _handle_preload_error(self, error_msg):
        """Handle error during preloading.

        Args:
            error_msg: Error message
        """
        logger.warning(f"Error preloading brands: {error_msg}")
        # Don't show UI error since this is background preloading

    def on_hide(self):
        """Called when this step is hidden."""
        try:
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
        except Exception as e:
            logger.error(f"Error in on_hide: {e}")

    def __del__(self):
        """Clean up resources when the step is destroyed."""
        try:
            # Only clean up the database operator if we own it
            if hasattr(self, 'owns_db_operator') and self.owns_db_operator and hasattr(self, 'db_operator'):
                try:
                    self.db_operator.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up db_operator in {self.__class__.__name__}: {e}")
        except Exception as e:
            logger.error(f"Error in __del__: {e}")

    def on_show(self):
        """Called when this step is shown."""
        try:
            # Call parent first for consistent behavior (includes fade animation)
            super().on_show()

            # Always show placeholder brands immediately for better UX
            self._show_placeholder_brands()

            # Use a slightly longer timer to ensure UI is stable
            if self.brands:
                # If we already have brand data, update after a short delay
                QTimer.singleShot(50, self._update_with_real_brands)
            else:
                # If no data yet, load it with a longer delay to prevent UI freezing
                QTimer.singleShot(100, self.load_brands)
        except Exception as e:
            logger.error(f"Error in on_show: {e}")

    def _show_placeholder_brands(self):
        """Show placeholder brands immediately so the UI is visible."""
        try:
            # Clear existing data without waiting for database
            if hasattr(self, 'brands_grid') and self.brands_grid:
                self.brands_grid.clear()

            # Create placeholder data - smaller number to reduce processing time
            placeholder_brands = []
            for i in range(8):  # Reduced from 12 to 8 for faster loading
                placeholder_brands.append({'brand': f'Loading...{i + 1}'})

            # Use a special flag to indicate these are placeholders
            self._showing_placeholders = True

            # Populate grid with placeholders - use minimal processing
            if hasattr(self, 'brands_grid') and self.brands_grid:
                self.brands_grid.populate(placeholder_brands)
        except Exception as e:
            logger.error(f"Error showing placeholder brands: {e}")
            # Don't propagate the exception

    def _update_with_real_brands(self):
        """Update the UI with real brand data after it's initially visible."""
        try:
            if hasattr(self, '_showing_placeholders') and self._showing_placeholders:
                # Now we can take time to populate with real data
                self.populate_brands_grid()

                # Restore selection if we had one
                if self.step_data:
                    self.brands_grid.set_selected(self.step_data)

                # Clear placeholder flag
                self._showing_placeholders = False
        except Exception as e:
            logger.error(f"Error updating with real brands: {e}")