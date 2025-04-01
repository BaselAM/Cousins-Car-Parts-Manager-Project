"""
Model selection widget for the parts navigation system.
The second step in the parts navigation hierarchy.
"""
from PyQt5.QtWidgets import QScrollArea, QVBoxLayout, QFrame, QListWidget, QListWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal

from .base_step_widget import BaseStepWidget
from .ui_utils import SearchBox, InfoHeader
from .database_worker import DatabaseOperator
from logger import get_logger

logger = get_logger('parts_navigation.model')

class ModelWidget(BaseStepWidget):
    """
    Second step in the parts navigation - selecting a car model for a specific brand
    """
    # Signal emitted when a model is selected
    model_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        super().__init__(translator, db, parent)

        # Initialize database operator
        self.db_operator = DatabaseOperator(self.db)

        # Set up data
        self.current_brand = None
        self.models = []
        self.filtered_models = []

    def setup_ui(self):
        """Initialize and arrange UI elements"""
        # Call parent setup first
        super().setup_ui()

        # Update title
        self.title.setText(self.translator.t('select_model'))

        # Brand info at top
        self.brand_info = InfoHeader(self.translator)
        self.main_layout.addWidget(self.brand_info)

        # Search box
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_models_placeholder',
            label_key='search_models'
        )
        self.search_box.search_changed.connect(self.filter_models)
        self.main_layout.addWidget(self.search_box)

        # Models list
        self.models_list = QListWidget()
        self.models_list.setObjectName("modelsList")
        self.models_list.itemClicked.connect(self.on_model_clicked)
        self.models_list.itemDoubleClicked.connect(self.on_model_double_clicked)
        self.main_layout.addWidget(self.models_list, 1)  # Takes most space

        # Update help text
        self.help_text.setText(self.translator.t('select_model_help'))

    def apply_theme(self):
        """Apply current theme"""
        # Call parent apply_theme first
        super().apply_theme()

        # Apply theme to our specific components
        self.search_box.apply_theme()
        self.brand_info.apply_theme()

        # Apply theme to models list
        bg_color = self.get_color('card_bg')
        text_color = self.get_color('text')
        border_color = self.get_color('border')
        highlight = self.get_color('highlight')
        button_hover = self.get_color('button_hover')

        self.models_list.setStyleSheet(f"""
            #modelsList {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
                outline: none;
            }}
            
            #modelsList::item {{
                padding: 8px;
                border-bottom: 1px solid {border_color};
            }}
            
            #modelsList::item:selected {{
                background-color: {highlight};
                color: white;
            }}
            
            #modelsList::item:hover {{
                background-color: {button_hover};
            }}
        """)

    def update_translations(self):
        """Update all translatable text"""
        # Update our own texts
        self.title.setText(self.translator.t('select_model'))
        self.help_text.setText(self.translator.t('select_model_help'))

        # Update child widgets
        self.search_box.update_translations()

        # Update brand info if a brand is selected
        if self.current_brand:
            self.brand_info.set_info(
                self.translator.t('models_for_brand').format(brand=self.current_brand['brand'])
            )

        # Reload models list to refresh translations
        self.populate_models_list()

    def on_show(self):
        """Called when this step is shown"""
        # No direct action needed as models are loaded when set_brand is called
        pass

    def set_brand(self, brand_data):
        """Set the current brand and load models for it"""
        if not brand_data:
            return

        self.current_brand = brand_data
        self.brand_info.set_info(
            self.translator.t('models_for_brand').format(brand=brand_data['brand'])
        )

        # Load models for this brand
        self.load_models()

    def set_previous_step_data(self, data):
        """Set data from previous step"""
        if data:
            self.set_brand(data)

    def load_models(self):
        """Load models for the current brand from the database"""
        if not self.current_brand:
            return

        # Show loading indicator
        self.show_loading(True)

        # Clear existing data
        self.models = []
        self.filtered_models = []
        self.models_list.clear()

        # Execute database operation
        self.db_operator.execute(
            "get_models",
            self.on_models_loaded,
            self.on_database_error,
            brand=self.current_brand
        )

    def on_models_loaded(self, models):
        """Handle loaded models data"""
        # Hide loading indicator
        self.show_loading(False)

        # Store models
        self.models = models if models else []
        self.filtered_models = self.models.copy()

        logger.info(f"Loaded {len(self.models)} unique models for {self.current_brand['brand']}")

        # Populate the list
        self.populate_models_list()

        # Restore selection if already had one
        if self.step_data:
            self._select_model(self.step_data)

    def on_database_error(self, error_msg):
        """Handle database error"""
        self.handle_error(f"Error loading models: {error_msg}")
        self.show_loading(False)

    def filter_models(self, search_text):
        """Filter models based on search text"""
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

        # Repopulate the list with filtered models
        self.populate_models_list()

    def populate_models_list(self):
        """Populate the list with model items"""
        # Clear existing items
        self.models_list.clear()

        # Check if we have any models
        if not self.filtered_models:
            item = QListWidgetItem(self.translator.t('no_models_found'))
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.models_list.addItem(item)
            return

        # Add model items to list
        for model in self.filtered_models:
            item = QListWidgetItem(model['model'])
            item.setData(Qt.UserRole, model)
            self.models_list.addItem(item)

    def _select_model(self, model_data):
        """Select a model in the list"""
        for i in range(self.models_list.count()):
            item = self.models_list.item(i)
            item_data = item.data(Qt.UserRole)
            if item_data and item_data['model'] == model_data['model']:
                self.models_list.setCurrentItem(item)
                break

    def on_model_clicked(self, item):
        """Handle click on a model item"""
        model_data = item.data(Qt.UserRole)
        if model_data:
            logger.info(f"Model clicked: {model_data['model']}")

            # Store the selected model
            self.step_data = model_data

            # Emit signal for main container
            self.model_selected.emit(model_data)
            self.step_completed.emit(model_data)

    def on_model_double_clicked(self, item):
        """Handle double-click on a model item"""
        # Same as on_model_clicked, but might be used to navigate directly to next step
        self.on_model_clicked(item)

    def reset(self):
        """Reset this step's data"""
        super().reset()
        self.search_box.clear()
        self.models_list.clear()
        self.current_brand = None
        self.brand_info.set_info("")
        self.models = []
        self.filtered_models = []

    def can_proceed(self):
        """Check if user can proceed to next step"""
        return self.step_data is not None

    def get_color(self, color_key):
        """Utility function to get a color from the theme system"""
        from themes import get_color
        return get_color(color_key)