"""
Product selection step for the parts navigation system.

A premium step for selecting specific products with elegant styling and animations.
"""
from PyQt5.QtWidgets import (QVBoxLayout, QFrame, QLabel, QSizePolicy,
                             QHBoxLayout, QScrollArea, QWidget, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QPixmap, QColor

from ..base import BaseStepWidget
from ..components.search_box import SearchBox
from ..components.info_header import InfoHeader
from ..utils.database_worker import DatabaseOperator
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.steps.product')


class ProductCard(QFrame):
    """
    A premium card for displaying product details.

    Features:
    - Clean, iOS-inspired design
    - Selection highlighting
    - Hover effects
    - Detailed product information display
    """
    # Signal emitted when card is clicked
    clicked = pyqtSignal(dict)  # Contains the product data

    def __init__(self, product, is_selected=False, parent=None):
        """
        Initialize the product card.

        Args:
            product: Product data dictionary
            is_selected: Whether the card is initially selected
            parent: Parent widget
        """
        super().__init__(parent)
        self.product = product
        self.is_selected = is_selected
        self.is_hovered = False

        # Set up UI
        self.setObjectName("productCard")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        self.setMinimumHeight(120)
        self.setup_ui()
        self.apply_theme()

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

    def setup_ui(self):
        """Initialize and arrange UI elements with compact styling."""
        # Call parent setup first
        super().setup_ui()

        # Set title
        self.title.setText(self.translator.t('select_product'))

        # Selection info header with premium styling but more compact
        self.selection_info = InfoHeader(self.translator)
        self.selection_info.setMaximumHeight(40)  # Limit height
        self.content_layout.addWidget(self.selection_info)

        # Search box with premium styling but more compact
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_products_placeholder',
            label_key='search_products',
            show_button=False
        )
        self.search_box.search_changed.connect(self.filter_products)
        self.search_box.setMaximumHeight(38)  # Limit height
        self.content_layout.addWidget(self.search_box)

        # Create scroll area for products - this needs most of the space
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setObjectName("productsScrollArea")

        # Container for products
        self.products_container = QWidget()
        self.products_container.setObjectName("productsContainer")

        # Layout for product cards with reduced spacing
        self.products_layout = QVBoxLayout(self.products_container)
        self.products_layout.setContentsMargins(4, 4, 4, 4)  # Reduced margins
        self.products_layout.setSpacing(6)  # Reduced spacing

        # Add container to scroll area
        self.scroll_area.setWidget(self.products_container)

        # Set size policy for proper expansion
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.products_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Ensure scroll area gets enough height
        self.scroll_area.setMinimumHeight(280)  # Give it significant space

        self.content_layout.addWidget(self.scroll_area, 10)  # Give it most of the space with stretch factor

        # Simplify help text to save space
        self.help_text.setText(self.translator.t('select_product_help'))

    def _animate_selection(self):
        """Add a subtle animation effect when selected"""
        # Create a temporary opacity effect
        effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(effect)

        # Animate opacity for a flash effect
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(300)
        anim.setStartValue(0.7)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)

        # Clear effect when done
        anim.finished.connect(lambda: self.setGraphicsEffect(None))

        # Start animation
        anim.start()
        # Keep reference to prevent garbage collection
        self._effect_animation = anim

    def _get_stock_text(self):
        """Get stock text with color indication based on quantity."""
        quantity = self.product.get('quantity', 0)

        if quantity > 10:
            return f"<span style='color:green;'>In Stock ({quantity})</span>"
        elif quantity > 0:
            return f"<span style='color:orange;'>Low Stock ({quantity})</span>"
        else:
            return f"<span style='color:red;'>Out of Stock</span>"

    def apply_theme(self):
        """Apply premium styling based on current state."""
        # Get theme colors
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        text_color = get_color('text', '#E2E8F0')
        border_color = get_color('border', '#2C5282')
        highlight = get_color('highlight', '#4299E1')
        secondary_text = get_color('secondary_text', '#A0AEC0')

        # Compute derived colors
        hover_bg = get_color('button_hover', '#4299E1')

        # Apply styling based on state
        if self.is_selected:
            # Selected state - enhanced styling
            self.setObjectName("productCardSelected")

            self.setStyleSheet(f"""
                #productCardSelected {{
                    background-color: {hover_bg};
                    border: 2px solid {highlight};
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                }}

                #productImage {{
                    background-color: {bg_color};
                    border-radius: 8px;
                    padding: 5px;
                }}

                #productName {{
                    color: {text_color};
                    font-weight: bold;
                }}

                #productCategory {{
                    color: {text_color};
                    font-style: italic;
                }}

                #productPrice {{
                    color: white;
                    font-weight: bold;
                }}
            """)
        else:
            # Normal or hovered state
            self.setObjectName("productCard")

            # Modify styling based on hover state
            hover_style = ""
            if self.is_hovered:
                hover_style = f"""
                    background-color: {QColor(card_bg).lighter(110).name()};
                    border: 1px solid {highlight};
                """

            self.setStyleSheet(f"""
                #productCard {{
                    background-color: {card_bg};
                    border: 1px solid {border_color};
                    border-radius: 10px;
                    {hover_style}
                }}

                #productImage {{
                    background-color: {QColor(bg_color).lighter(110).name()};
                    border-radius: 8px;
                    padding: 5px;
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

    def set_selected(self, selected):
        """
        Set the selection state with elegant visual feedback.

        Args:
            selected: Whether the card should be selected
        """
        if self.is_selected == selected:
            return

        self.is_selected = selected
        self.apply_theme()

        # Add animation for selection change
        if selected:
            self._animate_selection()
    # Mouse event handlers
    def mousePressEvent(self, event):
        """Handle mouse press."""
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release to emit clicked signal."""
        self.clicked.emit(self.product)
        super().mouseReleaseEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        self.is_hovered = True
        self.apply_theme()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave to end hover effect."""
        self.is_hovered = False
        self.apply_theme()
        super().leaveEvent(event)


class ProductStep(BaseStepWidget):
    """
    Fifth step in the parts navigation - selecting a specific product

    Features:
    - Clean, elegant layout with premium styling
    - Car and category information display
    - Detailed product cards
    - Search functionality
    - Smooth animations
    """
    # Signal emitted when a product is selected
    product_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        """
        Initialize the product step.

        Args:
            translator: Translator for localization
            db: Database connection
            parent: Parent widget
        """
        # Initialize database operator
        self.db_operator = DatabaseOperator(db)

        # Set up data
        self.current_car = None
        self.current_category = None
        self.products = []
        self.filtered_products = []
        self.product_cards = []

        # Call parent init after our initialization
        super().__init__(translator, db, parent)

    def setup_ui(self):
        """Initialize and arrange UI elements with premium styling."""
        # Call parent setup first
        super().setup_ui()

        # Set title
        self.title.setText(self.translator.t('select_product'))

        # Selection info header with premium styling
        self.selection_info = InfoHeader(self.translator)
        self.content_layout.addWidget(self.selection_info)

        # Search box with premium styling
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_products_placeholder',
            label_key='search_products',
            show_button=False
        )
        self.search_box.search_changed.connect(self.filter_products)
        self.content_layout.addWidget(self.search_box)

        # Create scroll area for products
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setObjectName("productsScrollArea")

        # Container for products
        self.products_container = QWidget()
        self.products_container.setObjectName("productsContainer")

        # Layout for product cards
        self.products_layout = QVBoxLayout(self.products_container)
        self.products_layout.setContentsMargins(5, 5, 5, 5)
        self.products_layout.setSpacing(10)

        # Add container to scroll area
        self.scroll_area.setWidget(self.products_container)

        # Set size policy for proper expansion
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.products_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.content_layout.addWidget(self.scroll_area, 1)  # Give it most of the space

        # Update help text
        self.help_text.setText(self.translator.t('select_product_help'))

    def apply_theme(self):
        """Apply premium styling based on system theme."""
        # Call parent apply_theme first
        super().apply_theme()

        # Apply theme to our components
        self.selection_info.apply_theme()
        self.search_box.apply_theme()

        # Get theme colors for scroll area
        bg_color = get_color('background', '#0F2942')

        # Apply styling to scroll area
        self.scroll_area.setStyleSheet(f"""
            #productsScrollArea {{
                background-color: transparent;
                border: none;
            }}

            #productsContainer {{
                background-color: {bg_color};
                border-radius: 8px;
            }}
        """)

        # Apply theme to all product cards
        for card in self.product_cards:
            card.apply_theme()

    def update_translations(self):
        """Update all translatable text when language changes."""
        # Call parent first
        super().update_translations()

        # Update our texts
        self.title.setText(self.translator.t('select_product'))
        self.help_text.setText(self.translator.t('select_product_help'))

        # Update child components
        self.search_box.update_translations()

        # Update selection info
        self._update_selection_info()

        # Reload products to refresh translations
        self.populate_products_list()

    def on_show(self):
        """Called when this step is shown."""
        # Call parent first
        super().on_show()

        # Refresh products if we have car and category
        if self.current_car and self.current_category:
            self.load_products()

    def _update_selection_info(self):
        """Update the selection info header."""
        if not self.current_car or not self.current_category:
            self.selection_info.set_info("")
            return

        # Get info text
        car_info = f"{self.current_car['brand']} {self.current_car['model']}"
        if 'year' in self.current_car:
            car_info += f" ({self.current_car['year']})"

        info_text = f"{car_info} - {self.current_category['category']}"

        # Update header
        self.selection_info.set_info(info_text)

    def set_filters(self, car_data, category_data):
        """
        Set filter criteria for products.

        Args:
            car_data: Car data dictionary
            category_data: Category data dictionary
        """
        if not car_data or not category_data:
            return

        # Set filters
        self.current_car = car_data
        self.current_category = category_data

        # Update info
        self._update_selection_info()

        # Load products
        self.load_products()

    def set_previous_step_data(self, data):
        """
        Set data from previous step.

        Args:
            data: Previous step data
        """
        # Previous step would be category selection
        if data and self.current_car:
            self.current_category = data
            self._update_selection_info()
            self.load_products()

    def load_products(self):
        """Load products for the current car and category."""
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
        """
        Handle loaded products data.

        Args:
            products: List of product dictionaries
        """
        # Hide loading indicator
        self.show_loading(False)

        # Store products
        self.products = products if products else []
        self.filtered_products = self.products.copy()

        info_text = f"{self.current_car['brand']} {self.current_car['model']}"
        if 'year' in self.current_car:
            info_text += f" ({self.current_car['year']})"

        logger.info(f"Loaded {len(self.products)} products for {info_text} in {self.current_category['category']}")

        # Populate the list
        self.populate_products_list()

        # Restore selection if already had one
        if self.step_data:
            self._select_product(self.step_data)

    def on_database_error(self, error_msg):
        """
        Handle database error.

        Args:
            error_msg: Error message
        """
        self.handle_error(f"Error loading products: {error_msg}")

        # Clean up UI state
        self.show_loading(False)
        self.clear_products_list()

        # Create empty message
        empty_label = QLabel(self.translator.t('products_load_error'))
        empty_label.setAlignment(Qt.AlignCenter)
        empty_label.setWordWrap(True)
        self.products_layout.addWidget(empty_label)

    def filter_products(self, search_text):
        """
        Filter products based on search text.

        Args:
            search_text: Search text to filter by
        """
        search_text = search_text.lower().strip()

        if not search_text:
            # If search is empty, show all products
            self.filtered_products = self.products.copy()
        else:
            # Filter products that contain the search text in name or category
            self.filtered_products = [
                product for product in self.products
                if search_text in product['name'].lower() or
                   (product.get('category', '') and search_text in product['category'].lower())
            ]

        # Repopulate the list with filtered products
        self.populate_products_list()

    def populate_products_list(self):
        """Populate the list with product cards."""
        # Clear existing cards
        self.clear_products_list()

        # If no products, show empty message
        if not self.filtered_products:
            empty_label = QLabel(self.translator.t('no_products_found'))
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setWordWrap(True)
            self.products_layout.addWidget(empty_label)
            return

        # Add product cards
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
        """Clear all products from the list."""
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
        """
        Compare two products to check if they're the same.

        Args:
            product1: First product data
            product2: Second product data

        Returns:
            bool: True if products are the same
        """
        if not product1 or not product2:
            return False

        # Compare by ID if available
        if 'id' in product1 and 'id' in product2:
            return product1['id'] == product2['id']

        # Otherwise compare by name
        return product1.get('name', '') == product2.get('name', '')

    def _select_product(self, product):
        """
        Select a product in the list.

        Args:
            product: Product data dictionary
        """
        # Update selection status of all cards
        for card in self.product_cards:
            card.set_selected(self._compare_products(card.product, product))

    def on_product_clicked(self, product):
        """
        Handle product selection.

        Args:
            product: Selected product data
        """
        logger.info(f"Product selected: {product}")

        # Store selected product
        self.step_data = product

        # Update selection status of all cards
        self._select_product(product)

        # Emit signals
        self.product_selected.emit(product)
        self.step_completed.emit(product)

    def show_search_results(self, results):
        """
        Display products from a search query.

        Args:
            results: Search results list
        """
        # Clear current selection state
        self.reset_selection()

        # Show search results header
        self.selection_info.set_info(self.translator.t('search_results'))

        # Clear existing products
        self.products = []
        self.filtered_products = []

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

    def reset_selection(self):
        """Reset selection state without clearing products."""
        self.step_data = None
        for card in self.product_cards:
            card.set_selected(False)

    def reset(self):
        """Reset this step's data and UI state."""
        # Call parent reset
        super().reset()

        # Clear search and products
        self.search_box.clear()
        self.clear_products_list()

        # Clear data
        self.current_car = None
        self.current_category = None
        self.selection_info.set_info("")
        self.products = []
        self.filtered_products = []

    def can_proceed(self):
        """Check if we can proceed to the next step."""
        return self.step_data is not None