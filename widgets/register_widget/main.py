"""
Modified RegisterWidget implementation with theme change support for ProductDetailCard.
"""
import datetime
from PyQt5.QtCore import (
    Qt, pyqtSignal, QPropertyAnimation, QTimer, QPoint,
    QEasingCurve, QParallelAnimationGroup, QEvent
)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QStackedWidget, QDialog, QSizePolicy,
    QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QColor, QCursor

from themes import get_color, get_size, get_font_size
from themes.theme_events import theme_event_manager  # Import the theme event manager
from .utils import SizePolicyMixin
from .ui import (
    EnhancedScrollBar, InfoDialog, WarningDialog, ErrorDialog,
    SuccessDialog, ConfirmationDialog, EmptyStateWidget,
    ProductDetailCard, CartWidget, EnhancedSearchBox
)

class RegisterWidget(QWidget, SizePolicyMixin):
    """
    Modern register widget that supports both selling and supply modes,
    with separate cart interfaces for each mode and multiple product display.
    With improved theme change support.
    """

    transaction_completed = pyqtSignal(dict)  # Emitted when a transaction is completed

    def __init__(self, translator=None, db=None, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.db = db

        # Current mode
        self.current_mode = "sell"  # "sell" or "supply"

        # Product suggestions for search
        self.product_suggestions = []

        # Current products data
        self.current_products = []  # Changed from single product to list of products

        # Set up UI
        self.setup_ui()

        # Load product suggestions
        self.load_product_suggestions()

        # Connect to theme change events
        theme_event_manager.theme_changed.connect(self.on_theme_changed)

        # Connect to database sync manager
        self.connect_to_sync_manager()

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the register widget UI with dual mode support."""
        # Set expanding policy for the widget
        self.set_expanding_policy()

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Left panel for product browsing (2/3 width)
        self.left_panel = QWidget()
        self.left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # Header with title and mode toggle
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel(self._translate("register_title", "Register"))
        title_label.setObjectName("registerTitle")
        font = title_label.font()
        font.setPointSize(get_font_size("xxlarge"))
        font.setBold(True)
        title_label.setFont(font)

        # Mode toggle buttons
        mode_container = QFrame()
        mode_container.setObjectName("modeToggleContainer")
        mode_layout = QHBoxLayout(mode_container)
        mode_layout.setContentsMargins(10, 10, 10, 10)
        mode_layout.setSpacing(0)

        self.sell_mode_btn = QPushButton(self._translate("sell_mode", "Sell Mode"))
        self.sell_mode_btn.setObjectName("sellModeButton")
        self.sell_mode_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.sell_mode_btn.setCheckable(True)
        self.sell_mode_btn.setChecked(True)
        self.sell_mode_btn.clicked.connect(lambda: self.set_mode("sell"))

        self.supply_mode_btn = QPushButton(self._translate("supply_mode", "Supply Mode"))
        self.supply_mode_btn.setObjectName("supplyModeButton")
        self.supply_mode_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.supply_mode_btn.setCheckable(True)
        self.supply_mode_btn.clicked.connect(lambda: self.set_mode("supply"))

        mode_layout.addWidget(self.sell_mode_btn)
        mode_layout.addWidget(self.supply_mode_btn)

        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(mode_container)

        left_layout.addLayout(header_layout)

        # Search section
        search_container = QFrame()
        search_container.setObjectName("searchContainer")
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(20, 20, 20, 20)

        # Create enhanced search box with improved functionality
        self.search_box = EnhancedSearchBox(translator=self.translator, db=self.db)
        self.search_box.search_submitted.connect(self.search_products)
        self.search_box.barcode_scanned.connect(
            lambda barcode: self.search_products(barcode, True))  # Barcodes always use precise search
        self.search_box.product_selected.connect(self.display_products)

        search_layout.addWidget(self.search_box)
        left_layout.addWidget(search_container)

        # Create content stack
        self.content_stack = QStackedWidget()
        self.content_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Empty state
        self.empty_state = EmptyStateWidget(translator=self.translator)
        self.content_stack.addWidget(self.empty_state)

        # Product results container - improved for better scrolling
        self.products_scroll_area = QScrollArea()
        self.products_scroll_area.setObjectName("productsScrollArea")
        self.products_scroll_area.setWidgetResizable(True)  # CRITICAL: This must be true
        self.products_scroll_area.setFrameShape(QFrame.NoFrame)

        # Explicitly set scroll policies
        self.products_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.products_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Set custom scrollbars
        self.products_scroll_area.setVerticalScrollBar(EnhancedScrollBar(Qt.Vertical))
        self.products_scroll_area.setHorizontalScrollBar(EnhancedScrollBar(Qt.Horizontal))

        # Create a simple QWidget as the content container
        self.products_content = QWidget()
        self.products_content.setObjectName("productsContent")

        # Use a simple VBox layout that expands vertically
        self.products_layout = QVBoxLayout(self.products_content)
        self.products_layout.setContentsMargins(20, 20, 20, 20)
        self.products_layout.setSpacing(16)
        self.products_layout.setAlignment(Qt.AlignTop)  # Important for proper card positioning

        # Set the content widget to the scroll area
        self.products_scroll_area.setWidget(self.products_content)
        self.content_stack.addWidget(self.products_scroll_area)

        # Initially show empty state
        self.content_stack.setCurrentWidget(self.empty_state)

        left_layout.addWidget(self.content_stack, 1)  # Give content stack the most space

        # Right panel (Cart Area)
        # Create a stacked widget to hold both cart panels
        self.cart_stack = QStackedWidget()
        self.cart_stack.setObjectName("cartStack")

        # Create SELL MODE cart panel
        self.sell_cart_panel = QWidget()
        self.sell_cart_panel.setObjectName("sellCartPanel")
        sell_cart_layout = QVBoxLayout(self.sell_cart_panel)
        sell_cart_layout.setContentsMargins(0, 0, 0, 0)
        sell_cart_layout.setSpacing(0)

        # Create a cart widget for sell mode
        self.sell_cart_widget = CartWidget(mode="sell", translator=self.translator)
        self.sell_cart_widget.checkout_clicked.connect(self.process_cart)
        sell_cart_layout.addWidget(self.sell_cart_widget)

        # Create SUPPLY MODE cart panel
        self.supply_cart_panel = QWidget()
        self.supply_cart_panel.setObjectName("supplyCartPanel")
        supply_cart_layout = QVBoxLayout(self.supply_cart_panel)
        supply_cart_layout.setContentsMargins(0, 0, 0, 0)
        supply_cart_layout.setSpacing(0)

        # Create a cart widget for supply mode
        self.supply_cart_widget = CartWidget(mode="supply", translator=self.translator)
        self.supply_cart_widget.checkout_clicked.connect(self.process_cart)
        supply_cart_layout.addWidget(self.supply_cart_widget)

        # Add both panels to the cart stack
        self.cart_stack.addWidget(self.sell_cart_panel)
        self.cart_stack.addWidget(self.supply_cart_panel)

        # Create the right panel to hold the cart stack
        self.right_panel = QWidget()
        self.right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)
        right_layout.addWidget(self.cart_stack)

        # Set panel sizes
        main_layout.addWidget(self.left_panel, 2)  # 2/3 of width
        main_layout.addWidget(self.right_panel, 1)  # 1/3 of width

        # Apply shadow effects to containers
        for container in [search_container, self.sell_cart_widget, self.supply_cart_widget]:
            shadow = QGraphicsDropShadowEffect(container)
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 30))
            shadow.setOffset(0, 3)
            container.setGraphicsEffect(shadow)

        # Initially show the sell cart
        self.cart_stack.setCurrentWidget(self.sell_cart_panel)

        # Apply initial theme
        self.apply_theme()

    def on_theme_changed(self, theme_name):
        """Handle theme changes by updating all styled components."""
        # Update the overall widget theme
        self.apply_theme()

        # Update product cards if they exist
        self._update_card_theme()

        # Update cart widgets
        if hasattr(self, 'sell_cart_widget') and hasattr(self.sell_cart_widget, 'apply_theme'):
            self.sell_cart_widget.apply_theme()

        if hasattr(self, 'supply_cart_widget') and hasattr(self.supply_cart_widget, 'apply_theme'):
            self.supply_cart_widget.apply_theme()

    def set_mode(self, mode):
        """Set the current mode (sell or supply) and update UI."""
        if mode not in ["sell", "supply"]:
            return

        self.current_mode = mode

        # Update toggle buttons
        self.sell_mode_btn.setChecked(mode == "sell")
        self.supply_mode_btn.setChecked(mode == "supply")

        # Update the cart stack to show the appropriate cart panel
        if mode == "sell":
            self.cart_stack.setCurrentWidget(self.sell_cart_panel)
        else:  # supply mode
            self.cart_stack.setCurrentWidget(self.supply_cart_panel)

        # Update all product cards if visible
        if self.current_products and self.content_stack.currentWidget() == self.products_scroll_area:
            self._update_product_cards_mode()

    def _update_product_cards_mode(self):
        """Update all product cards to match the current mode."""
        # Look for the cards container
        cards_container = None
        for i in range(self.products_layout.count()):
            widget = self.products_layout.itemAt(i).widget()
            if widget and widget.objectName() == "cardsContainer":
                cards_container = widget
                break

        if cards_container:
            # Get the layout of the cards container
            cards_layout = cards_container.layout()
            if cards_layout:
                # Update each product card in the layout
                for i in range(cards_layout.count()):
                    item = cards_layout.itemAt(i)
                    if item and item.widget() and isinstance(item.widget(), ProductDetailCard):
                        item.widget().set_mode(self.current_mode)

    def add_to_cart(self, product_data, quantity):
        """Add a product to the appropriate cart based on current mode."""
        # Get the active cart based on current mode
        active_cart = self.sell_cart_widget if self.current_mode == "sell" else self.supply_cart_widget

        if active_cart.add_item(product_data, quantity):
            message = (
                self._translate("added_to_cart", "Added to cart")
                if self.current_mode == "sell"
                else self._translate("added_to_supply", "Added to supply list")
            )
            self.show_success(
                message,
                f"{quantity} x {product_data.get('product_name')}"
            )

    def _silent_load_product_suggestions(self):
        """Load product suggestions without emitting signals."""
        if not self.db:
            return

        try:
            # Get all products
            products = self.db.get_all_parts()
            print(f"RegisterWidget: Silently loaded {len(products)} products for suggestions")

            # Set products in the enhanced search box
            if hasattr(self, 'search_box') and self.search_box:
                if hasattr(self.search_box, 'set_filtered_products'):
                    self.search_box.set_filtered_products(products)

            # For legacy compatibility, also maintain the suggestions list
            self.product_suggestions = []

            for product in products:
                if isinstance(product, dict):
                    # Add product name
                    name = product.get('product_name')
                    if name and name not in self.product_suggestions:
                        self.product_suggestions.append(name)

                    # Add parcode
                    parcode = product.get('parcode')
                    if parcode and str(parcode) not in self.product_suggestions:
                        self.product_suggestions.append(str(parcode))

                    # Add manufacturer (helps with searching by brand)
                    manufacturer = product.get('manufacturer')
                    if manufacturer and manufacturer not in self.product_suggestions:
                        self.product_suggestions.append(manufacturer)

                    # Add car brands from compatible_brands
                    compatible_brands = product.get('compatible_brands')
                    if compatible_brands:
                        brands = [brand.strip() for brand in str(compatible_brands).split(',')]
                        for brand in brands:
                            if brand and brand not in self.product_suggestions:
                                self.product_suggestions.append(brand)

            # Update suggestions in the search box if the old method is still supported
            if hasattr(self, 'search_box') and self.search_box:
                if hasattr(self.search_box, 'update_suggestions'):
                    self.search_box.update_suggestions(self.product_suggestions)

            print("RegisterWidget: Completed silent product suggestions update")

        except Exception as e:
            print(f"Error silently loading product suggestions: {e}")
            import traceback
            print(traceback.format_exc())

    def process_cart(self, cart_data):
        """Process the cart (checkout or process supply) with console debugging."""
        print("\n===== CART PROCESSING STARTED =====")
        print(f"Mode: {cart_data.get('mode', 'unknown')}")

        if not self.db:
            print("ERROR: Database connection is not available!")
            return

        items = cart_data.get('items', [])
        mode = cart_data.get('mode')

        print(f"Number of items in cart: {len(items)}")

        if not items:
            print("WARNING: Cart is empty, nothing to process")
            return

        try:
            # Create transaction data for each item
            transactions = []
            print("\n----- Processing Individual Items -----")

            for idx, item in enumerate(items):
                parcode = item.get('parcode')
                product_name = item.get('product_name', 'Unknown Product')
                price = item.get('price', 0.0)
                quantity = item.get('cart_quantity', 1)
                current_stock = item.get('quantity', 0)

                print(f"\nItem #{idx + 1}: {product_name} (Parcode: {parcode})")
                print(f"  Current stock: {current_stock}")
                print(f"  Quantity to {'sell' if mode == 'sell' else 'add'}: {quantity}")
                print(f"  Price per unit: ${price:.2f}")

                # Validate stock for sell mode
                if mode == "sell" and quantity > current_stock:
                    print(f"  ERROR: Insufficient stock! Available: {current_stock}, Requested: {quantity}")
                    self.show_warning(
                        self._translate("insufficient_stock", "Insufficient Stock"),
                        self._translate(
                            "insufficient_stock_msg",
                            f"Not enough stock for {product_name}. Available: {current_stock}"
                        )
                    )
                    return

                # Calculate new quantity
                new_quantity = current_stock - quantity if mode == "sell" else current_stock + quantity
                print(
                    f"  New stock will be: {new_quantity} ({current_stock} {'-' if mode == 'sell' else '+'} {quantity})")

                # Debug database call - THIS IS THE KEY PART
                print(f"  Calling db.update_part(parcode={parcode}, quantity={new_quantity})")

                # Here's where the issue might be - the database expects ID, not parcode
                # Let's check if the part exists first by parcode
                try:
                    # Check if we can get a part by parcode
                    if hasattr(self.db, 'get_part_by_parcode'):
                        part = self.db.get_part_by_parcode(parcode)
                        if part:
                            print(f"  ✓ Found part in database: ID={part.get('id')}, Parcode={part.get('parcode')}")

                            # Try to update using part ID (which is what the database expects)
                            part_id = part.get('id')
                            if part_id:
                                print(f"  Calling db.update_part with part_id={part_id}, quantity={new_quantity}")
                                # Use FIELD, VALUE format that the DB expects
                                success = self.db.update_part(part_id, quantity=new_quantity)

                                if success:
                                    print(f"  ✓ Database update result: Success")

                                    # Emit signal for product update - THIS IS THE KEY ADDITION
                                    try:
                                        from utils.database_sync import db_sync_manager

                                        # Create a copy of the complete updated product
                                        updated_product_data = dict(part)  # Start with a copy of the original part
                                        updated_product_data['quantity'] = new_quantity  # Update the quantity

                                        # Debug output
                                        print(f"  Emitting product_updated signal with updated data:")
                                        print(f"    Product: {updated_product_data.get('product_name')}")
                                        print(f"    ID: {updated_product_data.get('id')}")
                                        print(f"    New Quantity: {new_quantity}")

                                        # Emit the signal to notify all listeners (including SmartSearchWidget)
                                        db_sync_manager.emit_product_updated(updated_product_data)
                                    except Exception as e:
                                        print(f"  ❌ Error emitting product update signal: {e}")
                                        import traceback
                                        print(traceback.format_exc())
                                else:
                                    print(f"  ❌ Database update result: Failed")
                            else:
                                print("  ❌ ERROR: Part ID is missing, cannot update")
                        else:
                            print(f"  ❌ ERROR: Part with parcode {parcode} not found in database")
                    else:
                        # Fall back to direct update if get_part_by_parcode doesn't exist
                        print("  ⚠️ Falling back to direct update by parcode")
                        # NOTE: This might not work if the DB is expecting 'id' not 'parcode'
                        self.db.update_part(parcode, quantity=new_quantity)
                except Exception as db_err:
                    print(f"  ❌ Database update FAILED: {db_err}")
                    raise

                # Create transaction record
                transaction = {
                    'type': 'sell' if mode == "sell" else 'receive',
                    'product': product_name,
                    'parcode': parcode,
                    'quantity': quantity,
                    'price': price * quantity,
                    'timestamp': f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
                }
                print(f"  Created transaction record: {transaction}")

                transactions.append(transaction)

                # Emit transaction signal for each item
                print(f"  Emitting transaction_completed signal")
                self.transaction_completed.emit(transaction)

            # Show success message
            total_items = sum(item.get('cart_quantity', 1) for item in items)
            total_price = sum(item.get('price', 0.0) * item.get('cart_quantity', 1) for item in items)

            print(f"\n----- Transaction Summary -----")
            print(f"Total items: {total_items}")
            print(f"Total price: ${total_price:.2f}")

            if mode == "sell":
                print("Clearing sell cart and showing success message")
                self.show_success(
                    self._translate("checkout_complete", "Checkout Complete"),
                    self._translate(
                        "checkout_complete_msg",
                        f"Sold {total_items} items for ${total_price:.2f}"
                    )
                )
                # Clear only the sell cart
                self.sell_cart_widget.clear_cart()
            else:
                print("Clearing supply cart and showing success message")
                self.show_success(
                    self._translate("supply_complete", "Supply Processed"),
                    self._translate(
                        "supply_complete_msg",
                        f"Added {total_items} items to inventory for ${total_price:.2f}"
                    )
                )
                # Clear only the supply cart
                self.supply_cart_widget.clear_cart()

            # Reset UI
            print("Resetting UI and reloading suggestions")
            self.content_stack.setCurrentWidget(self.empty_state)
            self.current_products = []  # Reset current products list

            # Reload suggestions
            self.load_product_suggestions()
            print("===== CART PROCESSING COMPLETED SUCCESSFULLY =====")

        except Exception as e:
            import traceback
            print(f"❌ ERROR in process_cart: {e}")
            print(traceback.format_exc())
            self.show_error(
                self._translate("process_error", "Processing Error"),
                str(e)
            )
            print("===== CART PROCESSING FAILED =====")

    def load_product_suggestions(self):
        """Load comprehensive product suggestions for the search box."""
        if not self.db:
            return

        try:
            # Get all products
            products = self.db.get_all_parts()

            # Set products in the enhanced search box
            if hasattr(self.search_box, 'set_filtered_products'):
                self.search_box.set_filtered_products(products)

            # For legacy compatibility, also maintain the suggestions list
            self.product_suggestions = []

            for product in products:
                if isinstance(product, dict):
                    # Add product name
                    name = product.get('product_name')
                    if name and name not in self.product_suggestions:
                        self.product_suggestions.append(name)

                    # Add parcode
                    parcode = product.get('parcode')
                    if parcode and str(parcode) not in self.product_suggestions:
                        self.product_suggestions.append(str(parcode))

                    # Add manufacturer (helps with searching by brand)
                    manufacturer = product.get('manufacturer')
                    if manufacturer and manufacturer not in self.product_suggestions:
                        self.product_suggestions.append(manufacturer)

                    # Add car brands from compatible_brands
                    compatible_brands = product.get('compatible_brands')
                    if compatible_brands:
                        brands = [brand.strip() for brand in str(compatible_brands).split(',')]
                        for brand in brands:
                            if brand and brand not in self.product_suggestions:
                                self.product_suggestions.append(brand)

            # Update suggestions in the search box if the old method is still supported
            if hasattr(self.search_box, 'update_suggestions'):
                self.search_box.update_suggestions(self.product_suggestions)

        except Exception as e:
            print(f"Error loading product suggestions: {e}")

    def search_products(self, query, is_precise_search=False):
        """
        Search for products with improved approach specifically targeting multiple products.
        """
        if not self.db:
            self.show_error(self._translate(
                "error", "Error"),
                self._translate("db_connection_error", "Database connection is not available")
            )
            return

        try:
            # Clean the query
            query = query.strip()
            if not query:
                return

            # Get ALL products first to check for duplicates
            all_products = self.db.get_all_parts()
            print(f"SEARCH: Retrieved {len(all_products)} total products from database")

            # Check for duplicate product names
            name_counts = {}
            for product in all_products:
                name = str(product.get('product_name', '')).lower().strip()
                if name in name_counts:
                    name_counts[name] += 1
                else:
                    name_counts[name] = 1

            # Print any duplicates
            duplicates = [(name, count) for name, count in name_counts.items() if count > 1]
            if duplicates:
                print(f"SEARCH: Found {len(duplicates)} product names with multiple instances")
                for name, count in duplicates:
                    if name == query.lower().strip():
                        print(f"SEARCH: The query '{query}' has {count} matches in database!")

            # Initialize array for matching products
            matching_products = []
            query_lower = query.lower().strip()

            # Manual search through all products
            if is_precise_search:
                print(f"SEARCH: Looking for products with barcode '{query}'")
                # Barcode search - find ALL products with the exact barcode
                for product in all_products:
                    barcode = str(product.get('parcode', '')).strip()
                    if barcode == query:
                        print(
                            f"  Found match: {product.get('product_name')} (Barcode: {barcode}, ID: {product.get('id', 'unknown')})")
                        matching_products.append(product)
            else:
                print(f"SEARCH: Looking for products with name '{query}'")
                # Name search - find ALL products with the exact name
                for product in all_products:
                    name = str(product.get('product_name', '')).lower().strip()
                    if name == query_lower:
                        print(
                            f"  Found match: {product.get('product_name')} (Barcode: {product.get('parcode')}, ID: {product.get('id', 'unknown')})")
                        matching_products.append(product)

            # Show results count
            print(f"SEARCH COMPLETE: Found {len(matching_products)} matches for '{query}'")

            # Debug all matching products
            if matching_products:
                print("SEARCH RESULTS:")
                for idx, product in enumerate(matching_products):
                    print(
                        f"  {idx + 1}. {product.get('product_name')} (Barcode: {product.get('parcode')}, ID: {product.get('id', 'unknown')})")

                # Display ALL matching products
                self.display_products(matching_products)
            else:
                # No matches found
                search_type = "barcode" if is_precise_search else "product name"
                self.show_warning(
                    self._translate("no_results", "No Results"),
                    self._translate("no_results_msg", f"No products found with {search_type}: '{query}'")
                )
                self.content_stack.setCurrentWidget(self.empty_state)
                self.current_products = []

        except Exception as e:
            import traceback
            print(f"SEARCH ERROR: {e}")
            print(traceback.format_exc())
            self.show_error(
                self._translate("search_error", "Search Error"),
                str(e)
            )

    def display_products(self, products):
        """
        Display multiple products in the results view with elegant card styling.
        Integrates with the theme system for a consistent modern look.
        """
        # Force products to be a list
        if not isinstance(products, list):
            products = [products]

        if not products:
            return

        # Store current products
        self.current_products = list(products)

        # Clear existing products layout
        self._clear_products_layout()

        # Add results count label with refined typography
        count_text = f"Found {len(products)} matching product{'' if len(products) == 1 else 's'}"
        results_label = QLabel(self._translate("search_results_count", count_text))
        results_label.setObjectName("resultsCountLabel")
        results_label.setAlignment(Qt.AlignLeft)
        font = results_label.font()
        font.setPointSize(get_font_size("large"))
        font.setBold(True)
        results_label.setFont(font)

        self.products_layout.addWidget(results_label)

        # Add an elegant separator with refined styling
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setMaximumHeight(1)
        separator.setStyleSheet(f"background-color: {get_color('border')};")
        self.products_layout.addWidget(separator)
        self.products_layout.addSpacing(10)

        # Create an elegant container for the product cards
        cards_container = QFrame()
        cards_container.setObjectName("cardsContainer")
        cards_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Create layout for the cards with refined spacing
        cards_layout = QVBoxLayout(cards_container)
        cards_layout.setContentsMargins(8, 8, 8, 8)
        cards_layout.setSpacing(16)  # Elegant spacing between cards
        cards_layout.setAlignment(Qt.AlignTop)

        # Add product cards with elegant styling
        for idx, product in enumerate(products):
            # Create product card
            product_card = ProductDetailCard(product, translator=self.translator)
            product_card.setObjectName(f"productCard_{idx}")
            product_card.set_mode(self.current_mode)
            product_card.add_to_cart.connect(self.add_to_cart)

            # Add card to layout
            cards_layout.addWidget(product_card)

            # Add elegant separator between cards (except after the last one)
            if idx < len(products) - 1:
                card_separator = QFrame()
                card_separator.setProperty("cardSeparator", "true")  # For styling
                card_separator.setFrameShape(QFrame.HLine)
                card_separator.setFrameShadow(QFrame.Sunken)
                card_separator.setMaximumHeight(1)

                # Apply custom styling directly
                border_color = QColor(get_color('border'))
                lighter_border = border_color.lighter(120).name()
                card_separator.setStyleSheet(f"background-color: {lighter_border}; margin: 8px 10px;")

                cards_layout.addWidget(card_separator)

        # Add the cards container to the main layout
        self.products_layout.addWidget(cards_container)

        # Add stretch to push content to the top
        self.products_layout.addStretch(1)

        # Set scrollbar policies for elegant appearance
        self.products_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.products_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.products_scroll_area.setWidgetResizable(True)

        # Show the products container
        self.content_stack.setCurrentWidget(self.products_scroll_area)

        # Reset scroll position
        self.products_scroll_area.verticalScrollBar().setValue(0)

        # Force layout updates
        cards_container.updateGeometry()
        self.products_content.updateGeometry()
        self.products_scroll_area.updateGeometry()

    def _clear_products_layout(self):
        """Clear all widgets from the products layout."""
        while self.products_layout.count():
            item = self.products_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _update_card_theme(self):
        """Update the theme of product cards after theme changes."""
        # Check if we have product cards to update
        if not hasattr(self, 'products_layout') or not self.products_layout:
            return

        # Update product cards if they exist
        for i in range(self.products_layout.count()):
            widget = self.products_layout.itemAt(i).widget()
            if isinstance(widget, ProductDetailCard) and hasattr(widget, 'apply_styling'):
                widget.apply_styling()
                # If the card has a current mode, reapply the mode styling
                if hasattr(widget, 'current_mode'):
                    widget.set_mode(widget.current_mode)

        # Force repaint of container
        if hasattr(self, 'products_content'):
            self.products_content.update()
            self.products_scroll_area.update()

    def apply_theme(self):
        """Apply theme styling to the widget with enhanced colors and modern aesthetics."""
        # Core colors
        background_color = QColor(get_color('background'))
        card_bg_color = QColor(get_color('card_bg'))
        highlight_color = QColor(get_color('highlight'))
        error_color = QColor(get_color('error'))
        border_color = QColor(get_color('border'))
        text_color = QColor(get_color('text'))
        title_color = QColor(get_color('title'))

        # Determine dark mode
        from themes import get_current_theme
        is_dark = get_current_theme() in ["dark", "classic"]

        # Subtle overlays
        subtle_highlight = QColor(highlight_color)
        subtle_highlight.setAlpha(30)
        subtle_error = QColor(error_color)
        subtle_error.setAlpha(30)

        # Card gradient
        card_bg_gradient_start = QColor(card_bg_color)
        card_bg_gradient_end = QColor(card_bg_color.lighter(103 if is_dark else 102))

        # Precompute scrollbar colors
        scroll_shadow_alpha = 40 if is_dark else 10
        scroll_shadow_color = QColor(0, 0, 0, scroll_shadow_alpha)
        scroll_handle_color = QColor(255, 255, 255, 50) if is_dark else QColor(0, 0, 0, 30)

        # Build and apply stylesheet
        self.setStyleSheet(f"""
            /* Base panels */
            #leftPanel, #rightPanel {{
                background-color: transparent;
            }}

            /* Title */
            #registerTitle {{
                color: {title_color.name()};
                margin-bottom: 10px;
                font-weight: bold;
                letter-spacing: 0.3px;
            }}

            /* Mode toggle container */
            #modeToggleContainer {{
                background-color: {card_bg_color.name()};
                border-radius: {get_size('border_radius_medium')}px;
                border: 1px solid {border_color.name()};
                box-shadow: 0 2px 6px {QColor(0, 0, 0, 20).name()};
            }}

            /* Toggle buttons */
            #sellModeButton, #supplyModeButton {{
                background-color: transparent;
                color: {text_color.name()};
                border: none;
                border-radius: {get_size('border_radius_medium')}px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 100px;
                transition: background-color 0.2s;
            }}
            #sellModeButton:checked {{
                background-color: {error_color.name()};
                color: white;
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
            }}
            #supplyModeButton:checked {{
                background-color: {highlight_color.name()};
                color: white;
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
            }}

            /* Search container */
            #searchContainer {{
                background-color: {card_bg_color.name()};
                border-radius: {get_size('border_radius_large')}px;
                border: 1px solid {border_color.name()};
                box-shadow: 0 4px 12px {scroll_shadow_color.name()};
            }}

            /* Products scroll area */
            #productsScrollArea {{
                background-color: {card_bg_color.name()};
                border-radius: {get_size('border_radius_large')}px;
                border: 1px solid {border_color.name()};
                padding: 0px;
                margin: 0px;
            }}
            #productsContent {{
                background-color: transparent;
                border: none;
            }}

            /* Results label */
            #resultsCountLabel {{
                color: {title_color.name()};
                font-size: {get_font_size('large')}px;
                font-weight: bold;
                margin: 5px 0 10px 0;
                padding-left: 5px;
                letter-spacing: 0.2px;
            }}

            /* Cards container */
            #cardsContainer {{
                background-color: transparent;
                border: none;
                padding: 10px 0px;
            }}
            QFrame[cardSeparator="true"] {{
                background-color: {border_color.lighter(120).name()};
                max-height: 1px;
                margin: 8px 10px;
            }}

            /* === Custom Scrollbars === */
            QScrollBar:vertical {{
                background: {background_color.darker(105).name()};
                width: 10px;
                margin: 2px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {scroll_handle_color.name()};
                min-height: 30px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {highlight_color.name()};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                background: {background_color.darker(105).name()};
                height: 10px;
                margin: 2px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal {{
                background: {scroll_handle_color.name()};
                min-width: 30px;
                border-radius: 5px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {highlight_color.name()};
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}

            /* Cart stack */
            #cartStack {{
                background-color: transparent;
            }}
        """)

    # Dialog methods
    def show_error(self, title, message):
        """Show an error message dialog."""
        dialog = ErrorDialog(title, message, self)
        dialog.exec_()

    def show_warning(self, title, message):
        """Show a warning message dialog."""
        dialog = WarningDialog(title, message, self)
        dialog.exec_()

    def show_info(self, title, message):
        """Show an info message dialog."""
        dialog = InfoDialog(title, message, self)
        dialog.exec_()

    def show_success(self, title, message):
        """Show a success message dialog."""
        dialog = SuccessDialog(title, message, self)
        dialog.exec_()

    def show_confirmation(self, title, message, yes_text="Yes", no_text="No"):
        """Show a confirmation dialog.

        Returns:
            bool: True if confirmed, False otherwise
        """
        dialog = ConfirmationDialog(title, message, yes_text, no_text, self)
        result = dialog.exec_()
        return result == QDialog.Accepted

    # Add these methods to the RegisterWidget class in main.py

    def connect_to_sync_manager(self):
        """Connect to the database sync manager to receive change notifications."""
        try:
            # Import here to avoid circular imports
            from utils.database_sync import db_sync_manager

            # Register with sync manager
            db_sync_manager.register_listener(self)

            # Connect signals to refresh methods
            db_sync_manager.product_added.connect(self._handle_product_added)
            db_sync_manager.product_updated.connect(self._handle_product_updated)
            db_sync_manager.product_deleted.connect(self._handle_product_deleted)
            db_sync_manager.products_loaded.connect(self._handle_products_loaded)

            print("RegisterWidget connected to database sync manager")
        except Exception as e:
            print(f"Error connecting to sync manager: {e}")

    def disconnect_from_sync_manager(self):
        """Disconnect from the database sync manager."""
        try:
            from utils.database_sync import db_sync_manager

            # Disconnect signals
            db_sync_manager.product_added.disconnect(self._handle_product_added)
            db_sync_manager.product_updated.disconnect(self._handle_product_updated)
            db_sync_manager.product_deleted.disconnect(self._handle_product_deleted)
            db_sync_manager.products_loaded.disconnect(self._handle_products_loaded)

            # Unregister from sync manager
            db_sync_manager.unregister_listener(self)

            print("RegisterWidget disconnected from database sync manager")
        except Exception as e:
            print(f"Error disconnecting from sync manager: {e}")

    def _handle_product_added(self, product_data):
        """Handle notification that a product was added in another widget."""
        print(f"RegisterWidget notified of product addition: {product_data}")
        # Reload product suggestions
        self.load_product_suggestions()

    def _handle_product_updated(self, product_data):
        """Handle notification that a product was updated in another widget."""
        print(f"RegisterWidget notified of product update: {product_data}")
        # Reload product suggestions
        self.load_product_suggestions()

        # Update current products if displaying the updated product
        if self.current_products:
            for i, product in enumerate(self.current_products):
                if product.get('id') == product_data.get('id') or product.get('parcode') == product_data.get('parcode'):
                    self.current_products[i] = product_data
                    self.display_products(self.current_products)
                    break

    def _handle_product_deleted(self, product_id):
        """Handle notification that a product was deleted in another widget."""
        print(f"RegisterWidget notified of product deletion: {product_id}")
        # Reload product suggestions
        self.load_product_suggestions()

        # Update current products if displaying the deleted product
        if self.current_products:
            new_products = [p for p in self.current_products if p.get('id') != product_id]
            if len(new_products) != len(self.current_products):
                self.current_products = new_products
                if new_products:
                    self.display_products(new_products)
                else:
                    self.content_stack.setCurrentWidget(self.empty_state)

    def _handle_products_loaded(self):
        """Handle notification that products were loaded in another widget."""
        print("RegisterWidget notified of products loaded event")
        # Reload product suggestions
        self.load_product_suggestions()

    def closeEvent(self, event):
        """Handle widget close event."""
        try:
            # Disconnect from sync manager
            self.disconnect_from_sync_manager()

            # Call the parent class closeEvent if it exists
            super().closeEvent(event)
        except Exception as e:
            print(f"Error during close event: {e}")
            event.accept()

    # Add this to RegisterWidget class after successfully adding a product

    def _add_product_to_database(self, product_data):
        """Add a product to the database and emit the appropriate signal."""
        if not self.db or not hasattr(self.db, 'add_part'):
            print("Error: Database connection or add_part method not available")
            return False

        try:
            # Add the product to the database using the add_part method
            success = self.db.add_part(
                category=product_data.get('category', ''),
                product_name=product_data.get('product_name', ''),
                quantity=product_data.get('quantity', 0),
                price=product_data.get('price', 0.0),
                original=product_data.get('original', False),
                manufacturer=product_data.get('manufacturer', ''),
                parcode=product_data.get('parcode', ''),
                compatible_models=product_data.get('compatible_models', ''),
                compatible_brands=product_data.get('compatible_brands', '')
            )

            if success:
                print(f"Successfully added product: {product_data.get('product_name')}")

                # Emit signal for product addition
                try:
                    from utils.database_sync import db_sync_manager

                    # Get the newly added product with its ID
                    new_product = self.db.get_part_by_parcode(product_data.get('parcode'))
                    if new_product:
                        # Emit the signal with the complete product data
                        print(f"Emitting product_added signal for new product ID: {new_product.get('id')}")
                        db_sync_manager.emit_product_added(new_product)
                    else:
                        print("Warning: Added product not found for signal emission")
                except Exception as e:
                    print(f"Error emitting product addition signal: {e}")

                return True
            else:
                print(f"Failed to add product: {product_data.get('product_name')}")
                return False

        except Exception as e:
            print(f"Error adding product to database: {e}")
            return False