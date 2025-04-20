"""
Enhanced search components using shared search components to ensure functionality
and behavior consistency across the application.
"""
from PyQt5.QtCore import (Qt, pyqtSignal, QPoint)
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QPushButton, QApplication, QFrame, QToolButton)
from PyQt5.QtGui import QColor, QCursor, QPixmap

# Import our shared search components
from search_components import SearchEdit, SearchDropdown

# Import theme and UI elements
try:
    from themes import get_color, get_size, get_font_size
    from .scroll_bar import EnhancedScrollBar
    from widgets.products.components.barcode_scanner_button import BarcodeScannerButton
except ImportError:
    # Simple fallback for barcode scanner if not available
    from PyQt5.QtWidgets import QToolButton

    class BarcodeScannerButton(QToolButton):
        """Fallback barcode scanner button if the real one is unavailable."""
        barcode_scanned = pyqtSignal(str)

        def __init__(self, parent=None, translator=None):
            super().__init__(parent)
            self.translator = translator
            self.setText("🔍")
            self.setToolTip("Scan Barcode")
            self.setFixedSize(40, 40)


class EnhancedSearchBox(QWidget):
    """
    Enhanced search box with a focus-preserving dropdown for suggestions.
    Uses the shared search components for consistent behavior across the application.
    """
    search_submitted = pyqtSignal(str, bool)  # query, is_precise_search
    barcode_scanned = pyqtSignal(str)
    product_selected = pyqtSignal(dict)  # Selected product data

    def __init__(self, parent=None, translator=None, db=None):
        super().__init__(parent)
        self.translator = translator
        self.db = db
        self.search_mode = "product_name"  # Default to product name search
        self.filtered_products = []  # List of all products after filtering

        self.setup_ui()

    def _translate(self, key, default=""):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            # Only pass the key to the translator's t() method
            # Don't pass default as a positional argument
            translated = self.translator.t(key)
            return translated if translated != key else default
        return default

    def setup_ui(self):
        """Set up the search box UI."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Search input row
        search_row = QHBoxLayout()
        search_row.setContentsMargins(0, 0, 0, 0)
        search_row.setSpacing(12)

        # Search icon
        search_icon_label = QLabel()
        search_icon_label.setFixedSize(24, 24)
        search_icon_label.setObjectName("searchIcon")

        # Try to load search icon
        try:
            icon_path = "resources/search_icon.png"
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                search_icon_label.setPixmap(pixmap)
            else:
                search_icon_label.setText("🔍")
        except:
            search_icon_label.setText("🔍")

        # Use our shared SearchEdit component
        self.search_input = SearchEdit(
            parent=self,
            object_name="searchInput",
            min_height=45
        )
        self.search_input.set_parent_widget(self)
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setPlaceholderText(self._translate(
            "search_placeholder", "Search by product name or ID...")
        )

        # Barcode scanner button (this is separate from the barcode search mode)
        self.barcode_scanner_btn = BarcodeScannerButton(parent=self, translator=self.translator)
        self.barcode_scanner_btn.barcode_scanned.connect(self.on_barcode_scanned)

        # Search button
        self.search_btn = QPushButton(self._translate("search_button", "Search"))
        self.search_btn.setObjectName("searchButton")
        self.search_btn.setMinimumHeight(45)
        self.search_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.search_btn.clicked.connect(self.submit_search)

        # Add widgets to search row
        search_row.addWidget(search_icon_label)
        search_row.addWidget(self.search_input, 1)  # Search input takes most space
        search_row.addWidget(self.barcode_scanner_btn)
        search_row.addWidget(self.search_btn)

        layout.addLayout(search_row)

        # Search mode toggle row
        mode_row = QHBoxLayout()
        mode_row.setContentsMargins(0, 0, 0, 0)
        mode_row.setSpacing(5)

        # Mode label
        mode_label = QLabel(self._translate("search_mode", "Search Mode:"))
        mode_label.setObjectName("searchModeLabel")

        # Product Name search button (formerly Smart search)
        self.product_name_btn = QPushButton(self._translate("product_name_search", "Product Name"))
        self.product_name_btn.setObjectName("productNameSearchButton")
        self.product_name_btn.setCheckable(True)
        self.product_name_btn.setChecked(True)  # Default to product name search
        self.product_name_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.product_name_btn.clicked.connect(lambda: self.set_search_mode("product_name"))

        # Barcode search button (formerly Precise search)
        self.barcode_btn = QPushButton(self._translate("barcode_search", "Barcode"))
        self.barcode_btn.setObjectName("barcodeSearchButton")
        self.barcode_btn.setCheckable(True)
        self.barcode_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.barcode_btn.clicked.connect(lambda: self.set_search_mode("barcode"))

        # Search mode description
        self.mode_description = QLabel(self._translate(
            "product_name_search_desc", "Search products by their name")
        )
        self.mode_description.setObjectName("searchModeDescription")

        # Add widgets to mode row
        mode_row.addWidget(mode_label)
        mode_row.addWidget(self.product_name_btn)
        mode_row.addWidget(self.barcode_btn)
        mode_row.addStretch(1)
        mode_row.addWidget(self.mode_description)

        layout.addLayout(mode_row)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply styling to the search box."""
        highlight_color = QColor(get_color('highlight'))

        self.setStyleSheet(f"""
            #searchIcon {{
                color: {get_color('secondary_text')};
            }}

            #searchButton {{
                background-color: {get_color('highlight')};
                color: {get_color('highlight_text', '#FFFFFF')};
                border-radius: {get_size('border_radius_medium')}px;
                font-weight: bold;
                padding: 0 20px;
                font-size: {get_font_size('medium')}px;
            }}

            #searchButton:hover {{
                background-color: {highlight_color.lighter(110).name()};
            }}

            #searchButton:pressed {{
                background-color: {highlight_color.darker(110).name()};
            }}

            #searchModeLabel {{
                color: {get_color('secondary_text')};
                font-size: {get_font_size('small')}px;
                margin-right: 5px;
            }}

            #productNameSearchButton, #barcodeSearchButton {{
                background-color: {get_color('button')};
                color: {get_color('text')};
                border: 1px solid {get_color('border')};
                border-radius: {get_size('border_radius_small')}px;
                padding: 5px 10px;
                font-size: {get_font_size('small')}px;
            }}

            #productNameSearchButton:checked, #barcodeSearchButton:checked {{
                background-color: {get_color('highlight')};
                color: {get_color('highlight_text', '#FFFFFF')};
                border-color: {get_color('highlight')};
            }}

            #searchModeDescription {{
                color: {get_color('secondary_text')};
                font-size: {get_font_size('small')}px;
                font-style: italic;
            }}
        """)

    def set_search_mode(self, mode):
        """Set the search mode and update behavior."""
        self.search_mode = mode

        # Update buttons
        self.product_name_btn.setChecked(mode == "product_name")
        self.barcode_btn.setChecked(mode == "barcode")

        # Update description
        if mode == "product_name":
            self.mode_description.setText(self._translate(
                "product_name_search_desc", "Search products by their name")
            )
        else:
            self.mode_description.setText(self._translate(
                "barcode_search_desc", "Search products by their barcode")
            )

        # Propagate mode to search input component
        self.search_input.set_search_mode(mode)

    def on_item_selected(self, text, products):
        """Handle item selection from dropdown."""
        # If we have products, emit the first one
        if products and len(products) > 0:
            self.product_selected.emit(products[0])
        else:
            # Otherwise just perform the search
            self.submit_search()

    def submit_search(self):
        """Submit the search query."""
        query = self.search_input.text().strip()
        if query:
            # For backward compatibility, emit True for barcode searches
            # which were previously "precise" searches
            is_precise = (self.search_mode == "barcode")
            self.search_submitted.emit(query, is_precise)

    def on_barcode_scanned(self, barcode):
        """Handle when a barcode is scanned."""
        if barcode:
            # Set mode to barcode when barcode is scanned
            self.set_search_mode("barcode")
            self.search_input.setText(barcode)
            self.barcode_scanned.emit(barcode)
            # Trigger a search (barcodes are precise)
            self.search_submitted.emit(barcode, True)

    def set_filtered_products(self, products):
        """Set the list of products available for search and suggestions."""
        self.filtered_products = products
        # Force update suggestions if text already exists
        text = self.search_input.text().strip()
        if text:
            self.search_input.update_suggestions(text)

    def clear(self):
        """Clear the search input and hide suggestions."""
        self.search_input.clear()
        self.search_input.dropdown.clear()
        self.search_input.dropdown.hide()

    def update_suggestions(self, suggestions):
        """Legacy method for backward compatibility with the original search box."""
        # Ignore this since we handle suggestions differently
        pass