"""
Brand selection widget for the parts navigation system.
The first step in the parts navigation hierarchy with elegant, clean styling.
Enhanced for better visibility and performance.
"""
from PyQt5.QtWidgets import (QScrollArea, QVBoxLayout, QFrame, QHBoxLayout,
                             QLabel, QSizePolicy, QGridLayout)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from .base_step_widget import BaseStepWidget
from .ui_utils import SearchBox, TilesGrid
from .database_worker import DatabaseOperator
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.brand')

class BrandWidget(BaseStepWidget):
    """
    First step in the parts navigation - selecting a car brand
    Displays a grid of brands with logos in an elegant design
    """
    # Signal emitted when a brand is selected
    brand_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        # Initialize database operator
        self.db_operator = DatabaseOperator(db)

        # Set up data
        self.brands = []
        self.filtered_brands = []

        # Call parent init after our initialization
        super().__init__(translator, db, parent)

        # IMPROVED: Set size policy for better visibility
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # IMPROVED: Set minimum size to ensure visibility
        self.setMinimumSize(600, 400)

    def setup_ui(self):
        """Initialize and arrange UI elements with elegant spacing and clean design"""
        # Call parent setup first
        super().setup_ui()

        # Update title with refined typography
        self.title.setText(self.translator.t('select_brand'))
        title_font = self.title.font()
        title_font.setPointSize(18)  # IMPROVED: Larger title for better visibility
        title_font.setBold(True)
        self.title.setFont(title_font)

        # Content container for better organization - using the content layout from parent
        # IMPROVED: Use content_layout directly from parent class instead of adding a new container

        # Description text with clean styling
        self.description = QLabel(self.translator.t('select_brand_subtitle'))
        self.description.setObjectName("stepDescription")
        self.description.setAlignment(Qt.AlignCenter)
        self.description.setWordWrap(True)

        # IMPROVED: Style and size the description text
        desc_font = QFont()
        desc_font.setPointSize(14)
        self.description.setFont(desc_font)
        self.description.setMinimumHeight(30)

        self.content_layout.addWidget(self.description)

        # Search box with clean styling
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_brands_placeholder',
            label_key='search_brands'
        )
        self.search_box.search_changed.connect(self.filter_brands)
        self.content_layout.addWidget(self.search_box)

        # Create scroll area for brands grid - IMPROVED: Better configuration
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setObjectName("brandsScrollArea")
        self.scroll_area.setMinimumHeight(250)  # IMPROVED: Ensure minimum height

        # IMPROVED: Use better size policy
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Container for the brands
        self.brands_container = QFrame()
        self.brands_container.setObjectName("brandsContainer")
        container_layout = QVBoxLayout(self.brands_container)
        container_layout.setContentsMargins(5, 5, 5, 5)

        # IMPROVED: Set proper size policy for container
        self.brands_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Brands grid with clean styling - IMPROVED: Create with proper columns
        self.brands_grid = TilesGrid(self.translator, columns=4)
        self.brands_grid.setObjectName("brandsGrid")
        self.brands_grid.item_selected.connect(self.on_brand_clicked)

        # IMPROVED: Set proper size policy for grid
        self.brands_grid.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        container_layout.addWidget(self.brands_grid)

        # Add scroll area to content layout
        self.scroll_area.setWidget(self.brands_container)
        self.content_layout.addWidget(self.scroll_area, 1)  # Takes most space

        # Update help text with clean typography
        self.help_text.setText(self.translator.t('select_brand_help'))
        help_font = self.help_text.font()
        help_font.setItalic(True)
        self.help_text.setFont(help_font)

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
            #stepDescription {{
                color: {text_color};
                font-size: 14px;
                margin-bottom: 10px;
                padding: 5px;
            }}
            
            #brandsContainer {{
                background-color: transparent;
                border: none;
            }}
            
            #brandsScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """

        # Apply all styles
        self.setStyleSheet(self.styleSheet() + content_style)

        # Apply theme to our specific components
        self.search_box.apply_theme()
        self.brands_grid.apply_theme()

    def on_show(self):
        """Called when this step is shown"""
        # Call parent method first
        super().on_show()

        # Load brands when the widget is shown
        self.load_brands()

        # IMPROVED: Adjust scroll area size
        self.scroll_area.updateGeometry()

    def load_brands(self):
        """Load car brands from database with clean loading indicator"""
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

    def populate_brands_grid(self):
        """Populate the grid with brand items"""
        # Define function to get icon path for a brand
        def get_brand_icon(brand):
            brand_name = brand['brand'].lower().replace(' ', '_')
            return f"resources/logos/{brand_name}.png"

        # Populate the grid
        self.brands_grid.populate(self.filtered_brands, get_brand_icon)

    # Other methods remain unchanged...