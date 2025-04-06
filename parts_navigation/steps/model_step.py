"""
Model selection step for the parts navigation system.

A premium step for selecting car models with elegant styling and animations.
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

logger = get_logger('parts_navigation.steps.model')


class ModelStep(BaseStepWidget):
    """
    Second step in the parts navigation - selecting a car model

    Features:
    - Clean, elegant layout with premium styling
    - Brand information display
    - Responsive grid layout
    - Search functionality
    - Smooth animations
    """
    # Signal emitted when a model is selected
    model_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        """
        Initialize the model step.

        Args:
            translator: Translator for localization
            db: Database connection
            parent: Parent widget
        """
        # Initialize database operator
        self.db_operator = DatabaseOperator(db)

        # Set up data
        self.current_brand = None
        self.models = []
        self.filtered_models = []

        # Call parent init after our initialization
        super().__init__(translator, db, parent)

    def setup_ui(self):
        """Initialize and arrange UI elements with compact styling."""
        # Call parent setup first
        super().setup_ui()

        # Set title
        self.title.setText(self.translator.t('select_model'))

        # Brand info header with premium styling but more compact
        self.brand_info = InfoHeader(self.translator)
        self.brand_info.setMaximumHeight(40)  # Limit height
        self.content_layout.addWidget(self.brand_info)

        # Search box with premium styling but more compact
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_models_placeholder',
            label_key='search_models',
            show_button=False
        )
        self.search_box.search_changed.connect(self.filter_models)
        self.search_box.setMaximumHeight(38)  # Limit height
        self.content_layout.addWidget(self.search_box)

        # Models grid with premium styling - takes most space
        self.models_grid = TilesGrid(self.translator, columns=4)
        self.models_grid.item_selected.connect(self.on_model_clicked)

        # Set size policy for better display
        self.models_grid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Ensure grid gets plenty of space
        self.models_grid.setMinimumHeight(280)  # Still gives enough height for content

        self.content_layout.addWidget(self.models_grid, 10)  # Give it most of the space with stretch factor

        # Simplify help text to save space
        self.help_text.setText(self.translator.t('select_model_help'))

    def apply_theme(self):
        """Apply premium styling based on system theme."""
        # Call parent apply_theme first
        super().apply_theme()

        # Apply theme to our components
        self.brand_info.apply_theme()
        self.search_box.apply_theme()
        self.models_grid.apply_theme()

    def update_translations(self):
        """Update all translatable text when language changes."""
        # Call parent first
        super().update_translations()

        # Update our texts
        self.title.setText(self.translator.t('select_model'))
        self.help_text.setText(self.translator.t('select_model_help'))

        # Update child components
        self.search_box.update_translations()

        # Update brand info
        self._update_brand_info()

        # Reload models to refresh translations
        self.populate_models_grid()

    def on_show(self):
        """Called when this step is shown."""
        # Call parent first
        super().on_show()

        # Refresh models if we have a brand
        if self.current_brand:
            self.load_models()

    def _update_brand_info(self):
        """Update the brand info header."""
        if not self.current_brand:
            self.brand_info.set_info("")
            return

        # Get info text
        info_text = self.translator.t('models_for_brand',
                                      brand=self.current_brand['brand'])

        # Update header
        self.brand_info.set_info(info_text)

    def set_brand(self, brand_data):
        """
        Set the current brand and load its models.

        Args:
            brand_data: Brand data dictionary
        """
        if not brand_data:
            return

        # Set brand
        self.current_brand = brand_data

        # Update info
        self._update_brand_info()

        # Load models
        self.load_models()

    def set_previous_step_data(self, data):
        """
        Set data from previous step.

        Args:
            data: Previous step data
        """
        # Previous step would be brand selection
        if data:
            self.set_brand(data)

    def load_models(self):
        """Load models for the current brand."""
        if not self.current_brand:
            return

        # Show loading indicator
        self.show_loading(True)

        # Clear existing data
        self.models = []
        self.filtered_models = []
        self.models_grid.clear()

        # Execute database operation
        self.db_operator.execute(
            "get_models",
            self.on_models_loaded,
            self.on_database_error,
            brand=self.current_brand
        )

    def on_models_loaded(self, models):
        """
        Handle loaded models data.

        Args:
            models: List of model dictionaries
        """
        # Hide loading indicator
        self.show_loading(False)

        # Store models
        self.models = models if models else []
        self.filtered_models = self.models.copy()

        logger.info(f"Loaded {len(self.models)} models for {self.current_brand['brand']}")

        # Populate the grid
        self.populate_models_grid()

        # Restore selection if already had one
        if self.step_data:
            self.models_grid.set_selected(self.step_data)

    def on_database_error(self, error_msg):
        """
        Handle database error.

        Args:
            error_msg: Error message
        """
        self.handle_error(f"Error loading models: {error_msg}")

        # Clean up UI state
        self.show_loading(False)
        self.models_grid.clear()

        # Create empty message
        empty_label = QLabel(self.translator.t('models_load_error'))
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setWordWrap(True)
        self.models_grid.grid_layout.addWidget(empty_label, 0, 0, 1, 4)  # span 4 columns

    def filter_models(self, search_text):
        """
        Filter models based on search text.

        Args:
            search_text: Search text to filter by
        """
        search_text = search_text.lower().strip()

        if not search_text:
            # If search is empty, show all models
            self.filtered_models = self.models.copy()
        else:
            # Filter models that contain the search text
            self.filtered_models = [
                model for model in self.models
                if search_text in model['model'].lower()
            ]

        # Repopulate the grid with filtered models
        self.populate_models_grid()

    def populate_models_grid(self):
        """Populate the grid with model tiles."""
        # Populate the grid
        self.models_grid.populate(self.filtered_models)

    def on_model_clicked(self, model):
        """
        Handle model selection.

        Args:
            model: Selected model data
        """
        logger.info(f"Model selected: {model}")

        # Store selected model
        self.step_data = model

        # Emit signals
        self.model_selected.emit(model)
        self.step_completed.emit(model)

    def reset(self):
        """Reset this step's data and UI state."""
        # Call parent reset
        super().reset()

        # Clear search and grid
        self.search_box.clear()
        self.models_grid.clear()

        # Clear data
        self.current_brand = None
        self.brand_info.set_info("")
        self.models = []
        self.filtered_models = []

    def can_proceed(self):
        """Check if we can proceed to the next step."""
        return self.step_data is not None