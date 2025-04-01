"""
Year selection widget for the parts navigation system.
The third step in the parts navigation hierarchy.
"""
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt, pyqtSignal

from .base_step_widget import BaseStepWidget
from .ui_utils import SearchBox, InfoHeader, TilesGrid
from .database_worker import DatabaseOperator
from logger import get_logger

logger = get_logger('parts_navigation.year')

class YearWidget(BaseStepWidget):
    """
    Third step in the parts navigation - selecting a year for a specific brand and model
    """
    # Signal emitted when a year is selected
    year_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        super().__init__(translator, db, parent)

        # Initialize database operator
        self.db_operator = DatabaseOperator(self.db)

        # Set up data
        self.current_brand = None
        self.current_model = None
        self.years = []
        self.filtered_years = []

    def setup_ui(self):
        """Initialize and arrange UI elements"""
        # Call parent setup first
        super().setup_ui()

        # Update title
        self.title.setText(self.translator.t('select_year'))

        # Car info at top
        self.car_info = InfoHeader(self.translator)
        self.main_layout.addWidget(self.car_info)

        # Search box
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_years_placeholder',
            label_key='search_years'
        )
        self.search_box.search_changed.connect(self.filter_years)
        self.main_layout.addWidget(self.search_box)

        # Create scroll area for years grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Container for the years
        self.years_container = QFrame()
        container_layout = QVBoxLayout(self.years_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Years grid with more columns since years are smaller
        self.years_grid = TilesGrid(self.translator, columns=5)
        self.years_grid.item_selected.connect(self.on_year_clicked)
        container_layout.addWidget(self.years_grid)

        # Add scroll area to main layout
        scroll_area.setWidget(self.years_container)
        self.main_layout.addWidget(scroll_area, 1)  # Takes most space

        # Update help text
        self.help_text.setText(self.translator.t('select_year_help'))

    def apply_theme(self):
        """Apply current theme"""
        # Call parent apply_theme first
        super().apply_theme()

        # Apply theme to our specific components
        self.search_box.apply_theme()
        self.car_info.apply_theme()
        self.years_grid.apply_theme()

    def update_translations(self):
        """Update all translatable text"""
        # Update our own texts
        self.title.setText(self.translator.t('select_year'))
        self.help_text.setText(self.translator.t('select_year_help'))

        # Update child widgets
        self.search_box.update_translations()

        # Update car info if brand and model are selected
        self._update_car_info()

        # Reload years to refresh translations
        self.populate_years_grid()

    def on_show(self):
        """Called when this step is shown"""
        # No direct action needed as years are loaded when set_brand_model is called
        pass

    def set_brand_model(self, brand_data, model_data):
        """Set the current brand and model and load years for them"""
        if not brand_data or not model_data:
            return

        self.current_brand = brand_data
        self.current_model = model_data

        # Update car info
        self._update_car_info()

        # Load years for this brand and model
        self.load_years()

    def _update_car_info(self):
        """Update the car info header"""
        if not self.current_brand or not self.current_model:
            self.car_info.set_info("")
            return

        self.car_info.set_info(
            f"{self.current_brand['brand']} {self.current_model['model']}"
        )

    def set_previous_step_data(self, data):
        """Set data from previous step"""
        if data and self.current_brand:
            self.current_model = data
            self._update_car_info()
            self.load_years()

    def load_years(self):
        """Load years for the current brand and model from the database"""
        if not self.current_brand or not self.current_model:
            return

        # Show loading indicator
        self.show_loading(True)

        # Clear existing data
        self.years = []
        self.filtered_years = []
        self.years_grid.clear()

        # Execute database operation
        self.db_operator.execute(
            "get_years",
            self.on_years_loaded,
            self.on_database_error,
            brand=self.current_brand,
            model=self.current_model
        )

    def on_years_loaded(self, years):
        """Handle loaded years data"""
        # Hide loading indicator
        self.show_loading(False)

        # Store years
        self.years = years if years else []
        self.filtered_years = self.years.copy()

        logger.info(
            f"Loaded {len(self.years)} unique years for {self.current_brand['brand']} {self.current_model['model']}"
        )

        # Populate the grid
        self.populate_years_grid()

        # Restore selection if already had one
        if self.step_data:
            self.years_grid.set_selected(self.step_data)

    def on_database_error(self, error_msg):
        """Handle database error"""
        self.handle_error(f"Error loading years: {error_msg}")
        self.show_loading(False)

    def filter_years(self, search_text):
        """Filter years based on search text"""
        search_text = search_text.lower().strip()

        if not search_text:
            # If search is empty, show all years
            self.filtered_years = self.years.copy()
        else:
            # Filter years that contain the search text
            self.filtered_years = [
                year for year in self.years
                if search_text in year['year'].lower()
            ]

        # Repopulate the grid with filtered years
        self.populate_years_grid()

    def populate_years_grid(self):
        """Populate the grid with year tiles"""
        # Years typically don't have icons, so we pass None for icon_getter
        self.years_grid.populate(self.filtered_years)

    def on_year_clicked(self, year):
        """Handle click on a year tile"""
        logger.info(f"Year clicked: {year['year']}")

        # Store the selected year
        self.step_data = year

        # Create a car object with brand, model, and year
        if self.current_brand and self.current_model:
            car_data = {
                'brand': self.current_brand['brand'],
                'model': self.current_model['model'],
                'year': year['year']
            }

            # Emit signals for main container
            self.year_selected.emit(year)
            self.step_completed.emit({
                'year': year['year'],
                'car': car_data
            })

    def reset(self):
        """Reset this step's data"""
        super().reset()
        self.search_box.clear()
        self.years_grid.clear()
        self.current_brand = None
        self.current_model = None
        self.car_info.set_info("")
        self.years = []
        self.filtered_years = []

    def can_proceed(self):
        """Check if user can proceed to next step"""
        return self.step_data is not None