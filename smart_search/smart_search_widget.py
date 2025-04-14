# smart_search/smart_search_widget.py

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QHBoxLayout, QPushButton, QLineEdit,
    QComboBox, QGridLayout, QScrollArea,
    QSizePolicy
)
from PyQt5.QtGui import QFont, QColor
from themes import get_color, get_size
from logger import get_logger

logger = get_logger('smart_search.widget')


class SmartSearchWidget(QWidget):
    """
    Smart Search widget for advanced part finding functionality.

    This replaces the previous parts navigation with a more modern,
    AI-powered search experience.
    """

    def __init__(self, translator, db, parent=None):
        """
        Initialize the Smart Search widget.

        Args:
            translator: Translation service for localization
            db: Database connection
            parent: Parent widget
        """
        super().__init__(parent)
        self.translator = translator
        self.db = db

        # Configure widget
        self.setObjectName("smartSearchWidget")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set up UI
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements with premium styling."""
        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Title with premium styling
        self.title = QLabel("Smart Search")
        self.title.setObjectName("smartSearchTitle")
        title_font = QFont("Segoe UI", 18)
        title_font.setBold(True)
        self.title.setFont(title_font)
        self.title.setAlignment(Qt.AlignCenter)

        # Add title to layout
        self.main_layout.addWidget(self.title)

        # Create search section
        self.setup_search_section()

        # Create results area (placeholder for now)
        self.setup_results_area()

        # Add stretch to push everything to the top
        self.main_layout.addStretch(1)

    def setup_search_section(self):
        """Create search section with input and filters."""
        # Search container
        search_container = QFrame()
        search_container.setObjectName("searchContainer")
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(10, 15, 10, 15)
        search_layout.setSpacing(10)

        # Search input row
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("Enter part name, number, or description...")
        input_layout.addWidget(self.search_input, 3)

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.setObjectName("searchButton")
        self.search_button.clicked.connect(self.on_search)
        input_layout.addWidget(self.search_button)

        # Add input row to search layout
        search_layout.addLayout(input_layout)

        # Filter row
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(15)

        # Category filter
        category_layout = QHBoxLayout()
        category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        self.category_combo.addItem("All Categories")
        # Add categories here (will populate from database later)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_combo, 1)
        filter_layout.addLayout(category_layout, 1)

        # Brand filter
        brand_layout = QHBoxLayout()
        brand_label = QLabel("Brand:")
        self.brand_combo = QComboBox()
        self.brand_combo.addItem("All Brands")
        # Add brands here (will populate from database later)
        brand_layout.addWidget(brand_label)
        brand_layout.addWidget(self.brand_combo, 1)
        filter_layout.addLayout(brand_layout, 1)

        # Add filter row to search layout
        search_layout.addLayout(filter_layout)

        # Add search container to main layout
        self.main_layout.addWidget(search_container)

    def setup_results_area(self):
        """Create results area for displaying search results."""
        # Results container
        results_container = QFrame()
        results_container.setObjectName("resultsContainer")
        results_layout = QVBoxLayout(results_container)
        results_layout.setContentsMargins(10, 15, 10, 15)

        # Results title
        results_title = QLabel("Search Results")
        results_title.setObjectName("resultsTitle")
        title_font = QFont("Segoe UI", 14)
        title_font.setBold(True)
        results_title.setFont(title_font)
        results_layout.addWidget(results_title)

        # Results scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Scroll content widget
        scroll_content = QWidget()
        self.results_grid = QGridLayout(scroll_content)
        self.results_grid.setContentsMargins(0, 0, 0, 0)
        self.results_grid.setSpacing(10)

        # Add placeholder message
        placeholder = QLabel("Enter a search query to find parts")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setObjectName("placeholderText")
        self.results_grid.addWidget(placeholder, 0, 0, 1, 1, Qt.AlignCenter)

        # Set scroll content and add to layout
        scroll_area.setWidget(scroll_content)
        results_layout.addWidget(scroll_area)

        # Add results container to main layout
        self.main_layout.addWidget(results_container, 1)

    def apply_theme(self):
        """Apply theme styling to the widget."""
        # Get theme colors
        bg_color = get_color('background')
        card_bg = get_color('card_bg')
        text_color = get_color('text')
        highlight = get_color('highlight')
        border_color = get_color('border')

        # Apply styling
        self.setStyleSheet(f"""
            #smartSearchWidget {{
                background-color: {bg_color};
            }}

            #smartSearchTitle {{
                color: {text_color};
                font-size: 18pt;
                padding: 10px;
            }}

            #searchContainer, #resultsContainer {{
                background-color: {card_bg};
                border-radius: 8px;
                border: 1px solid {border_color};
            }}

            #searchInput {{
                padding: 8px;
                border-radius: 4px;
                border: 1px solid {border_color};
                background-color: {bg_color};
                color: {text_color};
            }}

            #searchButton {{
                background-color: {highlight};
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }}

            #searchButton:hover {{
                background-color: {QColor(highlight).lighter(110).name()};
            }}

            #resultsTitle {{
                color: {text_color};
                font-size: 14pt;
                padding-bottom: 10px;
            }}

            QComboBox {{
                padding: 6px;
                border-radius: 4px;
                border: 1px solid {border_color};
                background-color: {bg_color};
                color: {text_color};
            }}

            QLabel {{
                color: {text_color};
            }}

            #placeholderText {{
                color: {QColor(text_color).darker(120).name()};
                font-size: 12pt;
                font-style: italic;
            }}
        """)

    def on_search(self):
        """Handle search button click."""
        search_text = self.search_input.text().strip()
        if not search_text:
            return

        logger.info(f"Smart Search query: {search_text}")

        # TODO: Implement actual search functionality
        # For now, just update the placeholder text
        if self.results_grid.count() > 0:
            # Clear existing items
            while self.results_grid.count():
                item = self.results_grid.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

        # Add placeholder result message
        result_msg = QLabel(f"Found 0 results for: {search_text}\n(Smart Search functionality coming soon)")
        result_msg.setAlignment(Qt.AlignCenter)
        result_msg.setObjectName("placeholderText")
        self.results_grid.addWidget(result_msg, 0, 0, 1, 1, Qt.AlignCenter)

    def update_translations(self):
        """Update all translatable text."""
        # Hard-coded for now since this is custom
        self.title.setText("Smart Search")
        self.search_button.setText("Search")

        # When translations are added to the system, uncomment:
        # self.title.setText(self.translator.t("smart_search_title"))
        # self.search_button.setText(self.translator.t("search_button"))