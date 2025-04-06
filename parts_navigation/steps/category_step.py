"""
Category selection step for the parts navigation system.

A premium step for selecting part categories with elegant styling and animations.
"""
from PyQt5.QtWidgets import QVBoxLayout, QFrame, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ..base import BaseStepWidget
from ..components.search_box import SearchBox
from ..components.info_header import InfoHeader
from ..components.tiles_grid import TilesGrid
from ..utils.database_worker import DatabaseOperator
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.steps.category')


class CategoryStep(BaseStepWidget):
    """
    Fourth step in the parts navigation - selecting a part category

    Features:
    - Clean, elegant layout with premium styling
    - Car information display
    - Responsive grid layout
    - Search functionality
    - Smooth animations
    """
    # Signal emitted when a category is selected
    category_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        """
        Initialize the category step.

        Args:
            translator: Translator for localization
            db: Database connection
            parent: Parent widget
        """
        # Initialize database operator
        self.db_operator = DatabaseOperator(db)

        # Set up data
        self.current_car = None
        self.categories = []
        self.filtered_categories = []

        # Call parent init after our initialization
        super().__init__(translator, db, parent)

    def setup_ui(self):
        """Initialize and arrange UI elements with compact styling."""
        # Call parent setup first
        super().setup_ui()

        # Set title
        self.title.setText(self.translator.t('select_category'))

        # Car info header with premium styling but more compact
        self.car_info = InfoHeader(self.translator)
        self.car_info.setMaximumHeight(40)  # Limit height
        self.content_layout.addWidget(self.car_info)

        # Search box with premium styling but more compact
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_categories_placeholder',
            label_key='search_categories',
            show_button=False
        )
        self.search_box.search_changed.connect(self.filter_categories)
        self.search_box.setMaximumHeight(38)  # Limit height
        self.content_layout.addWidget(self.search_box)

        # Categories grid with premium styling - takes most space
        # Fewer columns for categories (they're larger)
        self.categories_grid = TilesGrid(self.translator, columns=3)
        self.categories_grid.item_selected.connect(self.on_category_clicked)

        # Set size policy for better display
        self.categories_grid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Ensure grid gets plenty of space
        self.categories_grid.setMinimumHeight(280)  # Still gives enough height for content

        self.content_layout.addWidget(self.categories_grid, 10)  # Give it most of the space with stretch factor

        # Simplify help text to save space
        self.help_text.setText(self.translator.t('select_category_help'))

    def apply_theme(self):
        """Apply premium styling based on system theme."""
        # Call parent apply_theme first
        super().apply_theme()

        # Apply theme to our components
        self.car_info.apply_theme()
        self.search_box.apply_theme()
        self.categories_grid.apply_theme()

    def update_translations(self):
        """Update all translatable text when language changes."""
        # Call parent first
        super().update_translations()

        # Update our texts
        self.title.setText(self.translator.t('select_category'))
        self.help_text.setText(self.translator.t('select_category_help'))

        # Update child components
        self.search_box.update_translations()

        # Update car info
        self._update_car_info()

        # Reload categories to refresh translations
        self.populate_categories_grid()

    def on_show(self):
        """Called when this step is shown."""
        # Call parent first
        super().on_show()

        # Refresh categories if we have a car
        if self.current_car:
            self.load_categories()

    def _update_car_info(self):
        """Update the car info header."""
        if not self.current_car:
            self.car_info.set_info("")
            return

        # Get info text
        car_info = f"{self.current_car['brand']} {self.current_car['model']}"
        if 'year' in self.current_car:
            car_info += f" ({self.current_car['year']})"

        # Update header
        self.car_info.set_info(car_info)

    def set_car(self, car_data):
        """
        Set the current car and load categories.

        Args:
            car_data: Car data dictionary
        """
        if not car_data:
            return

        # Set car
        self.current_car = car_data

        # Update info
        self._update_car_info()

        # Load categories
        self.load_categories()

    def set_previous_step_data(self, data):
        """
        Set data from previous step.

        Args:
            data: Previous step data
        """
        # Previous step would be year selection with car data
        if data and 'car' in data:
            self.set_car(data['car'])

    def load_categories(self):
        """Load categories for the current car."""
        if not self.current_car:
            return

        # Show loading indicator
        self.show_loading(True)

        # Clear existing data
        self.categories = []
        self.filtered_categories = []
        self.categories_grid.clear()

        # Execute database operation
        self.db_operator.execute(
            "get_categories",
            self.on_categories_loaded,
            self.on_database_error,
            car=self.current_car
        )

    def on_categories_loaded(self, categories):
        """
        Handle loaded categories data.

        Args:
            categories: List of category dictionaries
        """
        # Hide loading indicator
        self.show_loading(False)

        # Store categories
        self.categories = categories if categories else []
        self.filtered_categories = self.categories.copy()

        car_info = f"{self.current_car['brand']} {self.current_car['model']}"
        if 'year' in self.current_car:
            car_info += f" ({self.current_car['year']})"

        logger.info(f"Loaded {len(self.categories)} categories for {car_info}")

        # Populate the grid
        self.populate_categories_grid()

        # Restore selection if already had one
        if self.step_data:
            self.categories_grid.set_selected(self.step_data)

    def on_database_error(self, error_msg):
        """
        Handle database error.

        Args:
            error_msg: Error message
        """
        self.handle_error(f"Error loading categories: {error_msg}")

        # Clean up UI state
        self.show_loading(False)
        self.categories_grid.clear()

        # Create empty message
        empty_label = QLabel(self.translator.t('categories_load_error'))
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setWordWrap(True)
        self.categories_grid.grid_layout.addWidget(empty_label, 0, 0, 1, 3)  # span 3 columns

    def filter_categories(self, search_text):
        """
        Filter categories based on search text.

        Args:
            search_text: Search text to filter by
        """
        search_text = search_text.lower().strip()

        if not search_text:
            # If search is empty, show all categories
            self.filtered_categories = self.categories.copy()
        else:
            # Filter categories that contain the search text
            self.filtered_categories = [
                category for category in self.categories
                if search_text in category['category'].lower()
            ]

        # Repopulate the grid with filtered categories
        self.populate_categories_grid()

    def populate_categories_grid(self):
        """Populate the grid with category tiles."""

        # Define function to get icon path for a category
        def get_category_icon(category):
            category_name = category['category'].lower().replace(' ', '_')
            return f"resources/categories/{category_name}.png"

        # Populate the grid with icons
        self.categories_grid.populate(self.filtered_categories, get_category_icon)

    def on_category_clicked(self, category):
        """
        Handle category selection.

        Args:
            category: Selected category data
        """
        logger.info(f"Category selected: {category}")

        # Store selected category
        self.step_data = category

        # Emit signals
        self.category_selected.emit(category)
        self.step_completed.emit(category)

    def reset(self):
        """Reset this step's data and UI state."""
        # Call parent reset
        super().reset()

        # Clear search and grid
        self.search_box.clear()
        self.categories_grid.clear()

        # Clear data
        self.current_car = None
        self.car_info.set_info("")
        self.categories = []
        self.filtered_categories = []

    def can_proceed(self):
        """Check if we can proceed to the next step."""
        return self.step_data is not None