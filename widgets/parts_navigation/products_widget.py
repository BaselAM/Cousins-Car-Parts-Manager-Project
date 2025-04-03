"""
Products selection widget for the parts navigation system.
The fifth step in the parts navigation hierarchy.
"""
from PyQt5.QtWidgets import (QScrollArea, QVBoxLayout, QFrame, QHBoxLayout,
                             QLabel, QGridLayout, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from .base_step_widget import BaseStepWidget
from .ui_utils import SearchBox, InfoHeader
from .database_worker import DatabaseOperator
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.products')

class ProductCard(QFrame):
    """A card displaying product information with a selectable design."""

    clicked = pyqtSignal(dict)

    def __init__(self, product, is_selected=False):
        super().__init__()
        self.product = product
        self.is_selected = is_selected
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements"""
        self.setObjectName("productCardSelected" if self.is_selected else "productCard")
        self.setCursor(Qt.PointingHandCursor)

        # Use adaptive sizing
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Left side - Basic info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)

        # Product name
        self.name_label = QLabel(self.product['name'])
        self.name_label.setObjectName("productName")
        self.name_label.setWordWrap(True)

        # Use appropriate size policy
        self.name_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Use smaller font
        font = QFont()
        font.setBold(True)
        self.name_label.setFont(font)

        info_layout.addWidget(self.name_label)

        # Category
        self.category_label = QLabel(self.product['category'])
        self.category_label.setObjectName("productCategory")
        self.category_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        info_layout.addWidget(self.category_label)

        # Add info layout to main layout
        layout.addLayout(info_layout, 3)  # Give more space to info

        # Right side - Price and availability
        details_layout = QVBoxLayout()
        details_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        details_layout.setSpacing(2)

        # Price
        self.price_label = QLabel()
        self.price_label.setObjectName("productPrice")
        self.price_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.update_price_label()
        details_layout.addWidget(self.price_label, 0, Qt.AlignRight)

        # Quantity/stock
        self.stock_label = QLabel()
        self.stock_label.setObjectName("productStock")
        self.stock_label.setTextFormat(Qt.RichText)
        self.stock_label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.update_stock_label()
        details_layout.addWidget(self.stock_label, 0, Qt.AlignRight)

        # Add details layout to main layout
        layout.addLayout(details_layout, 1)

    def update_price_label(self):
        """Update the price label with current value and currency."""
        from translations import get_translator
        translator = get_translator()

        price = self.product.get('price', 0)
        if price == 0:
            self.price_label.setText(translator.t('price_not_available'))
        else:
            currency = translator.t('currency_symbol')
            self.price_label.setText(f"{translator.t('price')}: {currency} {price:.2f}")

    def update_stock_label(self):
        """Update the stock label with current quantity."""
        from translations import get_translator
        translator = get_translator()

        quantity = self.product.get('quantity', 0)

        # Set color based on stock level
        if quantity > 5:
            stock_color = "green"
            stock_text = translator.t('in_stock')
        elif quantity > 0:
            stock_color = "orange"
            stock_text = translator.t('low_stock')
        else:
            stock_color = "red"
            stock_text = translator.t('out_of_stock')

        self.stock_label.setText(
            f"{translator.t('stock')}: <span style='color:{stock_color};'>{stock_text} ({quantity})</span>"
        )

    def apply_theme(self):
        """Apply theme based on selection state."""
        bg_color = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        highlight = get_color('highlight')
        button_hover = get_color('button_hover')
        secondary_text = get_color('secondary_text')

        # Base style with no fixed dimensions
        base_style = """
            border-radius: 5px;
            padding: 2px;
        """

        # Different styling based on selection state
        if self.is_selected:
            self.setStyleSheet(f"""
                #productCardSelected {{
                    background-color: {button_hover};
                    border: 1px solid {highlight};
                    {base_style}
                }}
                
                #productName {{
                    color: {text_color};
                    font-weight: bold;
                }}
                
                #productCategory {{
                    color: {secondary_text};
                    font-style: italic;
                }}
                
                #productPrice {{
                    color: {highlight};
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                #productCard {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    {base_style}
                }}
                
                #productCard:hover {{
                    border: 1px solid {highlight};
                    background-color: {button_hover};
                }}
                
                #productName {{
                    color: {text_color};
                    font-weight: bold;
                }}
                
                #productCategory {{
                    color: {secondary_text};
                    font-style: italic;
                }}
                
                #productPrice {{
                    color: {highlight};
                    font-weight: bold;
                }}
            """)

    def update_translations(self):
        """Update translatable text when language changes."""
        self.update_price_label()
        self.update_stock_label()

    def set_selected(self, selected):
        """Set the selection state of this card."""
        if self.is_selected != selected:
            self.is_selected = selected
            self.setObjectName("productCardSelected" if selected else "productCard")
            self.apply_theme()
            self.style().unpolish(self)
            self.style().polish(self)

    def mousePressEvent(self, event):
        """Handle mouse press events for clicks."""
        self.clicked.emit(self.product)
        super().mousePressEvent(event)


class ProductsWidget(BaseStepWidget):
    """
    Fifth step in the parts navigation - selecting a specific product
    within a category for a chosen car
    """
    # Signal emitted when a product is selected
    product_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        # Initialize product_cards list before calling super().__init__
        # so it's available when apply_theme is called from the base class
        self.product_cards = []

        # Initialize database operator
        self.db_operator = DatabaseOperator(db)

        # Set up data
        self.current_car = None
        self.current_category = None
        self.products = []
        self.filtered_products = []

        # Call parent init after our initialization
        super().__init__(translator, db, parent)

    def setup_ui(self):
        """Initialize and arrange UI elements"""
        # Call parent setup first
        super().setup_ui()

        # Update title
        self.title.setText(self.translator.t('select_product'))

        # Selection info at top
        self.selection_info = InfoHeader(self.translator)
        self.main_layout.addWidget(self.selection_info)

        # Search box
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_products_placeholder',
            label_key='search_products'
        )
        self.search_box.search_changed.connect(self.filter_products)
        self.main_layout.addWidget(self.search_box)

        # Create scroll area for products list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Container for the products
        self.products_container = QFrame()
        self.products_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.products_layout = QVBoxLayout(self.products_container)
        self.products_layout.setContentsMargins(3, 3, 3, 3)
        self.products_layout.setSpacing(3)

        # Add scroll area to main layout
        scroll_area.setWidget(self.products_container)
        self.main_layout.addWidget(scroll_area, 1)  # Takes most space

        # Update help text
        self.help_text.setText(self.translator.t('select_product_help'))

    def apply_theme(self):
        """Apply current theme"""
        # Call parent apply_theme first
        super().apply_theme()

        # Apply theme to our specific components
        self.search_box.apply_theme()
        self.selection_info.apply_theme()

        # Apply theme to all product cards
        # Use hasattr check to ensure product_cards exists
        # (this method might be called from different places)
        if hasattr(self, 'product_cards'):
            for card in self.product_cards:
                card.apply_theme()

    def update_translations(self):
        """Update all translatable text"""
        # Update our own texts
        self.title.setText(self.translator.t('select_product'))
        self.help_text.setText(self.translator.t('select_product_help'))

        # Update child widgets
        self.search_box.update_translations()

        # Update selection info
        self._update_selection_info()

        # Update all product cards
        # Use hasattr check for safety
        if hasattr(self, 'product_cards'):
            for card in self.product_cards:
                card.update_translations()

    def on_show(self):
        """Called when this step is shown"""
        # No direct action needed as products are loaded when set_filters is called
        pass

    def set_filters(self, car_data, category_data):
        """Set filter criteria for products"""
        if not car_data or not category_data:
            return

        self.current_car = car_data
        self.current_category = category_data

        # Update selection info
        self._update_selection_info()

        # Load products for these filters
        self.load_products()

    def _update_selection_info(self):
        """Update the selection info header"""
        if not self.current_car or not self.current_category:
            self.selection_info.set_info("")
            return

        car_info = f"{self.current_car['brand']} {self.current_car['model']}"
        if 'year' in self.current_car:
            car_info += f" ({self.current_car['year']})"

        self.selection_info.set_info(f"{car_info} - {self.current_category['category']}")

    def set_previous_step_data(self, data):
        """Set data from previous step"""
        if data and self.current_car:
            self.current_category = data
            self._update_selection_info()
            self.load_products()

    def show_search_results(self, results):
        """Display products from a search query"""
        # Clear current selection state
        self.reset_selection()

        # Show search results header
        self.selection_info.set_info(self.translator.t('search_results'))

        # Set products directly from results
        self.products = []

        # Process each result into our product format
        for part in results:
            product = {
                'id': part.get('parcode', 0),
                'name': part.get('product_name', ''),
                'category': part.get('category', ''),
                'price': part.get('price', 0),
                'quantity': part.get('quantity', 0),
                'compatible_brands': part.get('compatible_brands', ''),
                'compatible_models': part.get('compatible_models', ''),
                'model_years': part.get('model_years', '')
            }
            self.products.append(product)

        self.filtered_products = self.products.copy()
        logger.info(f"Displaying {len(self.products)} search results")

        # Populate with search results
        self.populate_products_list()

    def load_products(self):
        """Load products matching the current filters from the database"""
        if not self.current_car or not self.current_category:
            return

        # Show loading indicator
        self.show_loading(True)

        # Clear existing data
        self.products = []
        self.filtered_products = []
        self.clear_products_list()

        # Execute database operation
        self.db_operator.execute(
            "get_products",
            self.on_products_loaded,
            self.on_database_error,
            car=self.current_car,
            category=self.current_category
        )

    def on_products_loaded(self, products):
        """Handle loaded products data"""
        # Hide loading indicator
        self.show_loading(False)

        # Store products
        self.products = products if products else []
        self.filtered_products = self.products.copy()

        car_info = f"{self.current_car['brand']} {self.current_car['model']}"
        if 'year' in self.current_car:
            car_info += f" ({self.current_car['year']})"

        logger.info(
            f"Loaded {len(self.products)} products for {car_info} in {self.current_category['category']}"
        )

        # Populate the list
        self.populate_products_list()

        # Restore selection if already had one
        if self.step_data:
            self._select_product(self.step_data)

    def on_database_error(self, error_msg):
        """Handle database error"""
        self.handle_error(f"Error loading products: {error_msg}")
        self.show_loading(False)

    def filter_products(self, search_text):
        """Filter products based on search text"""
        search_text = search_text.lower().strip()

        if not search_text:
            # If search is empty, show all products
            self.filtered_products = self.products.copy()
        else:
            # Filter products that contain the search text in name or category
            self.filtered_products = [
                product for product in self.products
                if search_text in product['name'].lower() or
                   search_text in product['category'].lower()
            ]

        # Repopulate the list with filtered products
        self.populate_products_list()

    def populate_products_list(self):
        """Populate the list with product cards"""
        # Clear existing widgets
        self.clear_products_list()

        # Check if we have any products
        if not self.filtered_products:
            empty_label = QLabel(self.translator.t('no_products_found'))
            empty_label.setAlignment(Qt.AlignCenter)
            self.products_layout.addWidget(empty_label)
            return

        # Add product cards to list
        for product in self.filtered_products:
            # Check if this is the selected product
            is_selected = (self.step_data is not None and
                          self._compare_products(product, self.step_data))

            # Create card
            card = ProductCard(product, is_selected)
            card.clicked.connect(self.on_product_clicked)

            # Add to layout
            self.products_layout.addWidget(card)
            self.product_cards.append(card)

        # Add stretch at the end to push cards to the top
        self.products_layout.addStretch(1)

    def clear_products_list(self):
        """Clear all products from the list"""
        # Remove all widgets from layout
        for i in reversed(range(self.products_layout.count())):
            item = self.products_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    self.products_layout.removeWidget(widget)
                    widget.deleteLater()

        # Clear product cards list
        self.product_cards = []

    def _compare_products(self, product1, product2):
        """Compare two products to check if they're the same."""
        if not product1 or not product2:
            return False

        # Compare by ID if available
        if 'id' in product1 and 'id' in product2:
            return product1['id'] == product2['id']

        # Otherwise compare by name
        return product1.get('name', '') == product2.get('name', '')

    def _select_product(self, product):
        """Select a product in the list"""
        # Update selection status of all cards
        for card in self.product_cards:
            card.set_selected(self._compare_products(card.product, product))

    def on_product_clicked(self, product):
        """Handle click on a product card"""
        logger.info(f"Product clicked: {product['name']}")

        # Store the selected product
        self.step_data = product

        # Update selection status of all cards
        self._select_product(product)

        # Emit signals for main container
        self.product_selected.emit(product)
        self.step_completed.emit(product)

    def reset_selection(self):
        """Reset selection state without clearing products"""
        self.step_data = None
        for card in self.product_cards:
            card.set_selected(False)

    def reset(self):
        """Reset this step's data"""
        super().reset()
        self.search_box.clear()
        self.clear_products_list()
        self.current_car = None
        self.current_category = None
        self.selection_info.set_info("")
        self.products = []
        self.filtered_products = []

    def can_proceed(self):
        """Check if user can proceed to next step"""
        return self.step_data is not None

    def highlight_product(self, search_term):
        """Highlight a product matching the search term"""
        if not search_term or not self.products:
            return

        search_term = search_term.lower()

        # Find a matching product
        for product in self.products:
            if search_term in product['name'].lower():
                # Select this product
                self.step_data = product
                self._select_product(product)

                # Emit signals
                self.product_selected.emit(product)
                self.step_completed.emit(product)
                return True

        return False