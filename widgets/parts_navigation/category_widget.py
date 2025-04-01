"""
Category selection widget for the parts navigation system.
The fourth step in the parts navigation hierarchy.
"""
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt, pyqtSignal

from .base_step_widget import BaseStepWidget
from .ui_utils import SearchBox, InfoHeader, TilesGrid
from .database_worker import DatabaseOperator
from logger import get_logger

logger = get_logger('parts_navigation.category')

class CategoryWidget(BaseStepWidget):
    """
    Fourth step in the parts navigation - selecting a part category for the chosen car
    """
    # Signal emitted when a category is selected
    category_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        super().__init__(translator, db, parent)

        # Initialize database operator
        self.db_operator = DatabaseOperator(self.db)

        # Set up data
        self.current_car = None
        self.categories = []
        self.filtered_categories = []

    def setup_ui(self):
        """Initialize and arrange UI elements"""
        # Call parent setup first
        super().setup_ui()

        # Update title
        self.title.setText(self.translator.t('select_category'))

        # Car info at top
        self.car_info = InfoHeader(self.translator)
        self.main_layout.addWidget(self.car_info)

        # Search box
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_categories_placeholder',
            label_key='search_categories'
        )
        self.search_box.search_changed.connect(self.filter_categories)
        self.main_layout.addWidget(self.search_box)

        # Create scroll area for categories grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Container for the categories
        self.categories_container = QFrame()
        container_layout = QVBoxLayout(self.categories_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Categories grid with fewer columns since categories are larger
        self.categories_grid = TilesGrid(self.translator, columns=3)
        self.categories_grid.item_selected.connect(self.on_category_clicked)
        container_layout.addWidget(self.categories_grid)

        # Add scroll area to main layout
        scroll_area.setWidget(self.categories_container)
        self.main_layout.addWidget(scroll_area, 1)  # Takes most space

        # Update help text
        self.help_text.setText(self.translator.t('select_category_help'))

    def apply_theme(self):
        """Apply current theme"""
        # Call parent apply_theme first
        super().apply_theme()

        # Apply theme to our specific components
        self.search_box.apply_theme()
        self.car_info.apply_theme()
        self.categories_grid.apply_theme()

    def update_translations(self):
        """Update all translatable text"""
        # Update our own texts
        self.title.setText(self.translator.t('select_category'))
        self.help_text.setText(self.translator.t('select_category_help'))

        # Update child widgets
        self.search_box.update_translations()

        # Update car info if car is selected
        self._update_car_info()

        # Reload categories to refresh translations
        self.populate_categories_grid()

    def on_show(self):
        """Called when this step is shown"""
        # No direct action needed as categories are loaded when set_car is called
        pass

    def set_car(self, car_data):
        """Set the current car and load categories for it"""
        if not car_data:
            return

        self.current_car = car_data

        # Update car info
        self._update_car_info()

        # Load categories for this car
        self.load_categories()

    def _update_car_info(self):
        """Update the car info header"""
        if not self.current_car:
            self.car_info.set_info("")
            return

        if 'year' in self.current_car:
            self.car_info.set_info(
                f"{self.current_car['brand']} {self.current_car['model']} ({self.current_car['year']})"
            )
        else:
            self.car_info.set_info(
                f"{self.current_car['brand']} {self.current_car['model']}"
            )

    def set_previous_step_data(self, data):
        """Set data from previous step"""
        # Previous step may include year and car data
        if data and 'car' in data:
            self.set_car(data['car'])

    def load_categories(self):
        """Load categories for the current car from the database"""
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
        """Handle loaded categories data"""
        # Hide loading indicator
        self.show_loading(False)

        # Store categories
        self.categories = categories if categories else []
        self.filtered_categories = self.categories.copy()

        car_info = f"{self.current_car['brand']} {self.current_car['model']}"
        if 'year' in self.current_car:
            car_info += f" ({self.current_car['year']})"

        logger.info(f"Loaded {len(self.categories)} unique categories for {car_info}")

        # Populate the grid
        self.populate_categories_grid()

        # Restore selection if already had one
        if self.step_data:
            self.categories_grid.set_selected(self.step_data)

    def on_database_error(self, error_msg):
        """Handle database error"""
        self.handle_error(f"Error loading categories: {error_msg}")
        self.show_loading(False)

    def filter_categories(self, search_text):
        """Filter categories based on search text"""
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
        """Populate the grid with category tiles"""
        # Define function to get icon path for a category
        def get_category_icon(category):
            category_name = category['category'].lower().replace(' ', '_')
            return f"resources/icons/{category_name}.png"

        # Populate the grid
        self.categories_grid.populate(self.filtered_categories, get_category_icon)

    def on_category_clicked(self, category):
        """Handle click on a category tile"""
        logger.info(f"Category clicked: {category['category']}")

        # Store the selected category
        self.step_data = category

        # Emit signals for main container
        self.category_selected.emit(category)
        self.step_completed.emit(category)

    def reset(self):
        """Reset this step's data"""
        super().reset()
        self.search_box.clear()
        self.categories_grid.clear()
        self.current_car = None
        self.car_info.set_info("")
        self.categories = []
        self.filtered_categories = []

    def can_proceed(self):
        """Check if user can proceed to next step"""
        return self.step_data is not None