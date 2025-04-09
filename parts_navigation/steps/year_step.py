"""
Year selection step for the parts navigation system.

A premium step for selecting model years with elegant styling and animations.
"""
from PyQt5.QtWidgets import QVBoxLayout, QFrame, QLabel, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from ..base import BaseStepWidget
from ..components.search_box import SearchBox
from ..components.info_header import InfoHeader
from ..components.tiles_grid import TilesGrid
from utils.database_worker import DatabaseOperator
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.steps.year')


class YearStep(BaseStepWidget):
    """
    Third step in the parts navigation - selecting a model year

    Features:
    - Clean, elegant layout with premium styling
    - Brand and model information display
    - Responsive grid layout
    - Search functionality
    - Smooth animations
    """
    # Signal emitted when a year is selected
    year_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        """
        Initialize the year step.

        Args:
            translator: Translator for localization
            db: Database connection
            parent: Parent widget
        """
        # Initialize database operator
        self.db_operator = DatabaseOperator(db)

        # Set up data
        self.current_brand = None
        self.current_model = None
        self.years = []
        self.filtered_years = []

        # Call parent init after our initialization
        super().__init__(translator, db, parent)

    def setup_ui(self):
        """Initialize and arrange UI elements with compact styling."""
        # Call parent setup first
        super().setup_ui()

        # Set title
        self.title.setText(self.translator.t('select_year'))

        # Car info header with premium styling but more compact
        self.car_info = InfoHeader(self.translator)
        self.car_info.setMaximumHeight(40)  # Limit height
        self.content_layout.addWidget(self.car_info)

        # Search box with premium styling but more compact
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_years_placeholder',
            label_key='search_years',
            show_button=False
        )
        self.search_box.search_changed.connect(self.filter_years)
        self.search_box.setMaximumHeight(38)  # Limit height
        self.content_layout.addWidget(self.search_box)

        # Years grid with premium styling - takes most space
        # More columns for years since they're smaller
        self.years_grid = TilesGrid(self.translator, columns=5)
        self.years_grid.item_selected.connect(self.on_year_clicked)

        # Set size policy for better display
        self.years_grid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Ensure grid gets plenty of space
        self.years_grid.setMinimumHeight(280)  # Still gives enough height for content

        self.content_layout.addWidget(self.years_grid, 10)  # Give it most of the space with stretch factor

        # Simplify help text to save space
        self.help_text.setText(self.translator.t('select_year_help'))
    def apply_theme(self):
        """Apply premium styling based on system theme."""
        # Call parent apply_theme first
        super().apply_theme()

        # Apply theme to our components
        self.car_info.apply_theme()
        self.search_box.apply_theme()
        self.years_grid.apply_theme()

    def update_translations(self):
        """Update all translatable text when language changes."""
        # Call parent first
        super().update_translations()

        # Update our texts
        self.title.setText(self.translator.t('select_year'))
        self.help_text.setText(self.translator.t('select_year_help'))

        # Update child components
        self.search_box.update_translations()

        # Update car info
        self._update_car_info()

        # Reload years to refresh translations
        self.populate_years_grid()

    def on_show(self):
        """Called when this step is shown."""
        # Call parent first
        super().on_show()

        # Refresh years if we have brand and model
        if self.current_brand and self.current_model:
            self.load_years()

    def _update_car_info(self):
        """Update the car info header."""
        if not self.current_brand or not self.current_model:
            self.car_info.set_info("")
            return

        # Get info text
        info_text = f"{self.current_brand['brand']} {self.current_model['model']}"

        # Update header
        self.car_info.set_info(info_text)

    def set_brand_model(self, brand_data, model_data):
        """
        Set the current brand and model and load years.

        Args:
            brand_data: Brand data dictionary
            model_data: Model data dictionary
        """
        if not brand_data or not model_data:
            return

        # Set brand and model
        self.current_brand = brand_data
        self.current_model = model_data

        # Update info
        self._update_car_info()

        # Load years
        self.load_years()

    def set_previous_step_data(self, data):
        """
        Set data from previous step.

        Args:
            data: Previous step data
        """
        # Previous step would be model selection
        if data and self.current_brand:
            self.current_model = data
            self._update_car_info()
            self.load_years()

    def load_years(self):
        """Load years for the current brand and model."""
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
        """
        Handle loaded years data.

        Args:
            years: List of year dictionaries
        """
        # Hide loading indicator
        self.show_loading(False)

        # Store years
        self.years = years if years else []
        self.filtered_years = self.years.copy()

        logger.info(f"Loaded {len(self.years)} years for {self.current_brand['brand']} {self.current_model['model']}")

        # Populate the grid
        self.populate_years_grid()

        # Restore selection if already had one
        if self.step_data:
            self.years_grid.set_selected(self.step_data)

    def on_database_error(self, error_msg):
        """
        Handle database error.

        Args:
            error_msg: Error message
        """
        self.handle_error(f"Error loading years: {error_msg}")

        # Clean up UI state
        self.show_loading(False)
        self.years_grid.clear()

        # Create empty message
        empty_label = QLabel(self.translator.t('years_load_error'))
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setWordWrap(True)
        self.years_grid.grid_layout.addWidget(empty_label, 0, 0, 1, 5)  # span 5 columns

    def filter_years(self, search_text):
        """
        Filter years based on search text.

        Args:
            search_text: Search text to filter by
        """
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
        """Populate the grid with year tiles."""
        # Populate the grid - years don't have icons, so no icon_getter
        self.years_grid.populate(self.filtered_years)

    def on_year_clicked(self, year):
        """
        Handle year selection.

        Args:
            year: Selected year data
        """
        logger.info(f"Year selected: {year}")

        # Store selected year
        self.step_data = year

        # Create a car object with brand, model, and year
        if self.current_brand and self.current_model:
            car_data = {
                'brand': self.current_brand['brand'],
                'model': self.current_model['model'],
                'year': year['year']
            }

            # Emit signals with combined car data
            self.year_selected.emit(year)
            self.step_completed.emit({
                'year': year,
                'car': car_data
            })

    def reset(self):
        """Reset this step's data and UI state."""
        # Call parent reset
        super().reset()

        # Clear search and grid
        self.search_box.clear()
        self.years_grid.clear()

        # Clear data
        self.current_brand = None
        self.current_model = None
        self.car_info.set_info("")
        self.years = []
        self.filtered_years = []

    def can_proceed(self):
        """Check if we can proceed to the next step."""
        return self.step_data is not None