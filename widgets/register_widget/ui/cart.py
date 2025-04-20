"""
Cart components for managing shopping cart functionality.
"""
from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QPropertyAnimation, QTimer
from PyQt5.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidgetItem, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QColor, QCursor
from themes import get_color, get_size, get_font_size
from .quantity_selector import QuantitySelector
from .enhanced_scroll_bar import EnhancedScrollBar

class CartItem(QFrame):
    """A beautifully styled cart item with modern aesthetics."""

    remove_clicked = pyqtSignal(str)  # parcode of item to remove
    quantity_changed = pyqtSignal(str, int)  # parcode, new quantity

    def __init__(self, product_data, mode, parent=None, translator=None):
        super().__init__(parent)
        self.product_data = product_data
        self.mode = mode  # "sell" or "supply"
        self.translator = translator
        self.setup_ui()
        self.installEventFilter(self)

        # Track hover state for animations
        self.hovered = False

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the cart item UI with an elegant, modern design."""
        self.setObjectName("cartItem")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Modern, refined layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # Left side: Item info with elegant stacking
        info_container = QFrame()
        info_container.setObjectName("cartItemInfo")
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(4)

        # Product name with elegant styling
        name = self.product_data.get('product_name', 'Unknown Product')
        self.name_label = QLabel(name)
        self.name_label.setObjectName("cartItemName")
        self.name_label.setWordWrap(True)
        font = self.name_label.font()
        font.setBold(True)
        self.name_label.setFont(font)

        # Product details in subtle styling
        price = self.product_data.get('price', 0.0)
        formatted_price = f"${price:.2f}" if price is not None else "N/A"
        self.price_label = QLabel(formatted_price)
        self.price_label.setObjectName("cartItemPrice")

        # Add labels to info layout
        info_layout.addWidget(self.name_label)
        info_layout.addWidget(self.price_label)

        # Right side: Controls in vertical alignment for better spacing
        controls_container = QFrame()
        controls_container.setObjectName("cartItemControls")
        controls_layout = QVBoxLayout(controls_container)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(6)

        # Quantity controls in a row
        quantity_layout = QHBoxLayout()
        quantity_layout.setSpacing(8)

        # Quantity label
        qty_label = QLabel(self._translate("quantity", "Qty:"))
        qty_label.setObjectName("cartItemQtyLabel")
        quantity_layout.addWidget(qty_label)

        # Quantity selector with proper limits
        max_qty = 999
        if self.mode == "sell":
            stock = self.product_data.get('quantity', 0)
            max_qty = max(1, int(stock)) if stock is not None else 1

        self.quantity_selector = QuantitySelector(
            initial_value=self.product_data.get('cart_quantity', 1),
            min_value=1,
            max_value=max_qty,
            mode=self.mode
        )
        self.quantity_selector.quantity_changed.connect(self.on_quantity_changed)
        self.quantity_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        quantity_layout.addWidget(self.quantity_selector)

        # Remove button with elegant styling
        self.remove_btn = QPushButton("×")
        self.remove_btn.setObjectName("cartItemRemoveBtn")
        self.remove_btn.setFixedSize(30, 30)  # Slightly larger for better touch target
        self.remove_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.remove_btn.clicked.connect(self.on_remove_clicked)
        self.remove_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.remove_btn.setToolTip(self._translate("remove_item", "Remove Item"))

        # Remove button in its own container for positioning
        remove_container = QFrame()
        remove_layout = QHBoxLayout(remove_container)
        remove_layout.setContentsMargins(0, 0, 0, 0)
        remove_layout.setAlignment(Qt.AlignRight)
        remove_layout.addWidget(self.remove_btn)

        # Add everything to the controls layout
        controls_layout.addLayout(quantity_layout)
        controls_layout.addWidget(remove_container)

        # Add main components to the layout with proper spacing
        main_layout.addWidget(info_container, 1)  # Info gets most of the space
        main_layout.addWidget(controls_container, 0)  # Controls take minimum space

        # Apply elegant styling
        self.apply_styling()

        # Add subtle shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        # Ensure initial text truncation
        self.update_text_display()

    def apply_styling(self):
        """Apply elegant styling to the cart item with refined theme integration."""
        # Get theme colors for consistent styling
        card_bg = get_color('card_bg')
        text_color = get_color('text')
        secondary_text = get_color('secondary_text')
        border_color = get_color('border')

        # Mode-specific colors with refined variations
        if self.mode == "sell":
            mode_color = get_color('error')
            # Create refined color variations
            mode_light = QColor(mode_color).lighter(190).name()
            mode_medium = QColor(mode_color).lighter(150).name()
            remove_bg = QColor(mode_color).lighter(130).name()
            remove_hover = mode_color
        else:  # supply mode
            mode_color = get_color('highlight')
            # Create refined color variations
            mode_light = QColor(mode_color).lighter(190).name()
            mode_medium = QColor(mode_color).lighter(150).name()
            remove_bg = QColor(mode_color).lighter(130).name()
            remove_hover = mode_color

        # Create elegant style with refined effects
        self.setStyleSheet(f"""
            #cartItem {{
                background-color: {QColor(card_bg).lighter(104).name()};
                border-radius: 10px;
                border: 1px solid {QColor(border_color).lighter(120).name()};
            }}

            #cartItem:hover {{
                background-color: {QColor(card_bg).lighter(107).name()};
                border: 1px solid {mode_medium};
            }}

            #cartItemName {{
                color: {text_color};
                font-size: {get_font_size('medium')}px;
                font-weight: bold;
            }}

            #cartItemPrice {{
                color: {mode_color};
                font-size: {get_font_size('small')}px;
                font-weight: bold;
            }}

            #cartItemQtyLabel {{
                color: {secondary_text};
                font-size: {get_font_size('small')}px;
            }}

            #cartItemRemoveBtn {{
                background-color: {remove_bg};
                color: white;
                border-radius: 15px;
                font-weight: bold;
                font-size: 18px;
                padding: 0px;
                margin: 0px;
                border: none;
                text-align: center;
                qproperty-alignment: AlignCenter;
            }}

            #cartItemRemoveBtn:hover {{
                background-color: {remove_hover};
            }}
        """)

    def on_quantity_changed(self, value):
        """Handle quantity changes with proper type conversion."""
        parcode = self.product_data.get('parcode')
        if parcode is not None:
            # Ensure parcode is string
            self.quantity_changed.emit(str(parcode), value)

    def on_remove_clicked(self):
        """Handle remove button click with proper type conversion."""
        parcode = self.product_data.get('parcode')
        if parcode is not None:
            # Ensure parcode is string
            self.remove_clicked.emit(str(parcode))

    def update_quantity(self, value):
        """Update the displayed quantity."""
        self.quantity_selector.set_quantity(value)

    def update_text_display(self):
        """Update text display based on available width."""
        # Calculate available width
        available_width = self.width() - 150  # Allow for controls

        # Get product name
        name = self.product_data.get('product_name', 'Unknown Product')
        font_metrics = self.name_label.fontMetrics()

        # If space is limited, truncate with ellipsis
        if available_width < 200:
            truncated_name = font_metrics.elidedText(name, Qt.ElideMiddle, available_width)
            self.name_label.setText(truncated_name)
            self.name_label.setToolTip(name)  # Show full name on hover
        else:
            self.name_label.setText(name)
            self.name_label.setWordWrap(True)

    def enterEvent(self, event):
        """Handle mouse enter event for hover effects."""
        self.hovered = True

        # Subtle shadow enhancement on hover
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))  # Increased opacity
        shadow.setOffset(0, 3)  # Increased offset
        self.setGraphicsEffect(shadow)

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event for hover effects."""
        self.hovered = False

        # Restore default shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))  # Default opacity
        shadow.setOffset(0, 2)  # Default offset
        self.setGraphicsEffect(shadow)

        super().leaveEvent(event)

    def eventFilter(self, obj, event):
        """Event filter to monitor resize events."""
        if obj == self and event.type() == QEvent.Resize:
            self.update_text_display()
        return super().eventFilter(obj, event)

    def resizeEvent(self, event):
        """Handle resize events."""
        super().resizeEvent(event)
        self.update_text_display()


class CartWidget(QWidget):
    """An elegant, modern cart widget with refined aesthetics."""

    checkout_clicked = pyqtSignal(dict)  # Cart data including all items

    def __init__(self, mode="sell", parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator
        self.mode = mode  # "sell" or "supply"
        self.cart_items = {}  # Dict of parcode: product_data
        self.setup_ui()
        self.installEventFilter(self)

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the cart widget UI with an elegant, modern design."""
        self.setObjectName("cartWidget")

        # Main layout with refined spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Enhanced header with elegant styling
        header_container = QFrame()
        header_container.setObjectName("cartHeaderContainer")
        header_container.setFrameShape(QFrame.NoFrame)
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(8)

        # Mode-specific title and styling
        if self.mode == "sell":
            title_text = self._translate("sell_cart_title", "Sales Cart")
            mode_text = self._translate("sell_mode", "Sell Mode")
            icon_text = "🛒"  # Shopping cart icon
        else:
            title_text = self._translate("supply_cart_title", "Supply Cart")
            mode_text = self._translate("supply_mode", "Supply Mode")
            icon_text = "📦"  # Box/supply icon

        # Icon label for visual interest
        self.icon_label = QLabel(icon_text)
        self.icon_label.setObjectName("cartIcon")
        font = self.icon_label.font()
        font.setPointSize(16)
        self.icon_label.setFont(font)

        # Title with refined typography
        self.title_label = QLabel(title_text)
        self.title_label.setObjectName("cartTitle")
        font = self.title_label.font()
        font.setPointSize(get_font_size("large"))
        font.setBold(True)
        self.title_label.setFont(font)

        # Elegant mode indicator with pill shape
        self.mode_label = QLabel(mode_text)
        self.mode_label.setObjectName(f"cart{self.mode.capitalize()}ModeLabel")
        mode_font = self.mode_label.font()
        mode_font.setBold(True)
        self.mode_label.setFont(mode_font)
        self.mode_label.setAlignment(Qt.AlignCenter)
        # Set a fixed height but flexible width for the pill
        self.mode_label.setFixedHeight(28)
        self.mode_label.setMinimumWidth(80)

        # Add elements to header
        header_layout.addWidget(self.icon_label)
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.mode_label)

        layout.addWidget(header_container)

        # Elegant divider line
        divider = QFrame()
        divider.setObjectName("cartDivider")
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        layout.addWidget(divider)

        # Modern scroll area for cart items
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("cartScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Custom stylish scrollbars
        self.scroll_area.setVerticalScrollBar(EnhancedScrollBar(Qt.Vertical))
        self.scroll_area.setHorizontalScrollBar(EnhancedScrollBar(Qt.Horizontal))

        # Content area with refined spacing
        self.scroll_content = QWidget()
        self.scroll_content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.scroll_content.setObjectName("cartScrollContent")
        self.items_layout = QVBoxLayout(self.scroll_content)
        self.items_layout.setContentsMargins(4, 4, 4, 4)
        self.items_layout.setSpacing(10)
        self.items_layout.setAlignment(Qt.AlignTop)

        # Stylish empty state with icon
        empty_container = QWidget()
        empty_container.setObjectName("emptyCartContainer")
        empty_layout = QVBoxLayout(empty_container)

        # Empty icon
        empty_icon = QLabel("🛒" if self.mode == "sell" else "📦")
        empty_icon.setObjectName("emptyCartIcon")
        empty_icon.setAlignment(Qt.AlignCenter)
        font = empty_icon.font()
        font.setPointSize(32)
        empty_icon.setFont(font)

        # Empty message
        empty_message = (
            self._translate("empty_cart_sell", "Your sales cart is empty")
            if self.mode == "sell"
            else self._translate("empty_cart_supply", "Your supply list is empty")
        )
        self.empty_label = QLabel(empty_message)
        self.empty_label.setObjectName("emptyCartLabel")
        self.empty_label.setAlignment(Qt.AlignCenter)

        # Empty hint
        empty_hint = QLabel(
            self._translate("empty_cart_hint", "Add items using the search panel")
        )
        empty_hint.setObjectName("emptyCartHint")
        empty_hint.setAlignment(Qt.AlignCenter)

        empty_layout.addStretch(1)
        empty_layout.addWidget(empty_icon)
        empty_layout.addWidget(self.empty_label)
        empty_layout.addWidget(empty_hint)
        empty_layout.addStretch(1)

        self.items_layout.addWidget(empty_container)

        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area, 1)  # Give scroll area stretching priority

        # Elegant footer with refined styling
        footer_container = QFrame()
        footer_container.setObjectName("cartFooterContainer")
        footer_container.setFrameShape(QFrame.NoFrame)
        footer_layout = QVBoxLayout(footer_container)
        footer_layout.setContentsMargins(12, 10, 12, 10)
        footer_layout.setSpacing(12)

        # Subtle divider before totals
        top_divider = QFrame()
        top_divider.setObjectName("cartFooterDivider")
        top_divider.setFrameShape(QFrame.HLine)
        top_divider.setFrameShadow(QFrame.Sunken)
        footer_layout.addWidget(top_divider)

        # Enhanced totals section
        totals_container = QFrame()
        totals_container.setObjectName("cartTotalsContainer")
        totals_layout = QVBoxLayout(totals_container)
        totals_layout.setContentsMargins(8, 8, 8, 8)
        totals_layout.setSpacing(8)

        # Subtotal with improved alignment
        subtotal_layout = QHBoxLayout()
        subtotal_layout.setSpacing(8)

        self.subtotal_label = QLabel(self._translate("subtotal", "Subtotal:"))
        self.subtotal_label.setObjectName("cartSubtotalLabel")
        self.subtotal_value = QLabel("$0.00")
        self.subtotal_value.setObjectName("cartSubtotalValue")
        self.subtotal_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        subtotal_layout.addWidget(self.subtotal_label)
        subtotal_layout.addStretch(1)
        subtotal_layout.addWidget(self.subtotal_value)
        totals_layout.addLayout(subtotal_layout)

        # Total items with improved alignment
        items_layout = QHBoxLayout()
        items_layout.setSpacing(8)

        self.items_label = QLabel(self._translate("total_items", "Total Items:"))
        self.items_label.setObjectName("cartItemsLabel")
        self.items_value = QLabel("0")
        self.items_value.setObjectName("cartItemsValue")
        self.items_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        items_layout.addWidget(self.items_label)
        items_layout.addStretch(1)
        items_layout.addWidget(self.items_value)
        totals_layout.addLayout(items_layout)

        footer_layout.addWidget(totals_container)

        # Modern checkout button with elegant styling
        button_text = (
            self._translate("checkout", "Checkout")
            if self.mode == "sell"
            else self._translate("process_supply", "Process Supply")
        )

        self.checkout_btn = QPushButton(button_text)
        self.checkout_btn.setObjectName(f"cart{self.mode.capitalize()}Button")
        self.checkout_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.checkout_btn.setMinimumHeight(48)
        self.checkout_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.checkout_btn.clicked.connect(self.on_checkout_clicked)
        self.checkout_btn.setEnabled(False)  # Disabled initially when cart is empty

        footer_layout.addWidget(self.checkout_btn)
        layout.addWidget(footer_container)

        # Apply elegant styling
        self.apply_styling()

        # Apply shadow effects
        self.apply_shadow_effects()

    def apply_shadow_effects(self):
        """Apply elegant shadow effects to cart components."""
        # Main container shadow
        main_shadow = QGraphicsDropShadowEffect()
        main_shadow.setBlurRadius(20)
        main_shadow.setColor(QColor(0, 0, 0, 40))
        main_shadow.setOffset(0, 2)
        self.setGraphicsEffect(main_shadow)

        # Button shadow
        button_shadow = QGraphicsDropShadowEffect()
        button_shadow.setBlurRadius(10)
        button_shadow.setColor(QColor(0, 0, 0, 60))
        button_shadow.setOffset(0, 2)
        self.checkout_btn.setGraphicsEffect(button_shadow)

    def apply_styling(self):
        """Apply elegant styling to the cart widget with theme integration."""
        # Get theme colors for consistent styling
        card_bg = get_color('card_bg')
        bg_color = get_color('background')
        text_color = get_color('text')
        title_color = get_color('title')
        border_color = get_color('border')
        secondary_text = get_color('secondary_text')
        highlight_color = get_color('highlight')

        # Mode-specific colors with elegant variations
        if self.mode == "sell":
            mode_color = get_color('error')
            mode_bg_color = QColor(get_color('error')).lighter(190).name()
            button_color = get_color('error')
            accent_color = QColor(get_color('error')).lighter(140).name()
        else:  # supply mode
            mode_color = get_color('highlight')
            mode_bg_color = QColor(get_color('highlight')).lighter(190).name()
            button_color = get_color('highlight')
            accent_color = QColor(get_color('highlight')).lighter(140).name()

        # Button styling with careful color handling
        button_hover_color = QColor(button_color).lighter(110).name()
        button_pressed_color = QColor(button_color).darker(110).name()
        button_text_color = get_color('highlight_text', '#FFFFFF')

        # Create a refined style sheet with elegant effects
        self.setStyleSheet(f"""
            #cartWidget {{
                background-color: {QColor(card_bg).lighter(102).name()};
                border-radius: {get_size('border_radius_large')}px;
                border: 1px solid {QColor(border_color).lighter(110).name()};
            }}

            #cartHeaderContainer {{
                background-color: {QColor(card_bg).darker(105).name()};
                border-top-left-radius: {get_size('border_radius_large') - 1}px;
                border-top-right-radius: {get_size('border_radius_large') - 1}px;
                border-bottom: 1px solid {border_color};
            }}

            #cartIcon {{
                color: {mode_color};
                padding-right: 6px;
            }}

            #cartTitle {{
                color: {title_color};
                font-size: {get_font_size('large')}px;
            }}

            #cart{self.mode.capitalize()}ModeLabel {{
                color: {mode_color};
                background-color: {mode_bg_color};
                padding: 4px 12px;
                border-radius: 14px;
                border: 1px solid {QColor(mode_color).lighter(150).name()};
            }}

            #cartDivider, #cartFooterDivider {{
                color: {QColor(border_color).lighter(120).name()};
                background-color: {QColor(border_color).lighter(120).name()};
                height: 1px;
                margin: 0px;
            }}

            #cartScrollContent {{
                background-color: transparent;
            }}

            #cartScroll {{
                background-color: {QColor(card_bg).lighter(103).name()};
                border: none;
            }}

            #emptyCartContainer {{
                background-color: transparent;
                margin: 20px;
            }}

            #emptyCartIcon {{
                color: {QColor(secondary_text).lighter(130).name()};
                margin-bottom: 10px;
            }}

            #emptyCartLabel {{
                color: {secondary_text};
                font-size: {get_font_size('medium')}px;
                font-weight: bold;
            }}

            #emptyCartHint {{
                color: {QColor(secondary_text).lighter(120).name()};
                font-size: {get_font_size('small')}px;
                font-style: italic;
                margin-top: 5px;
            }}

            #cartFooterContainer {{
                background-color: {QColor(card_bg).darker(103).name()};
                border-bottom-left-radius: {get_size('border_radius_large') - 1}px;
                border-bottom-right-radius: {get_size('border_radius_large') - 1}px;
                border-top: 1px solid {border_color};
            }}

            #cartTotalsContainer {{
                background-color: {QColor(card_bg).lighter(105).name()};
                border-radius: 8px;
                border: 1px solid {QColor(border_color).lighter(110).name()};
            }}

            #cartSubtotalLabel, #cartItemsLabel {{
                color: {text_color};
                font-size: {get_font_size('medium')}px;
            }}

            #cartSubtotalValue, #cartItemsValue {{
                color: {mode_color};
                font-size: {get_font_size('medium')}px;
                font-weight: bold;
            }}

            #{f"cart{self.mode.capitalize()}Button"} {{
                background-color: {button_color};
                color: {button_text_color};
                border-radius: 8px;
                font-weight: bold;
                font-size: {get_font_size('medium')}px;
                padding: 12px 20px;
                border: none;
            }}

            #{f"cart{self.mode.capitalize()}Button"}:hover {{
                background-color: {button_hover_color};
            }}

            #{f"cart{self.mode.capitalize()}Button"}:pressed {{
                background-color: {button_pressed_color};
            }}

            #{f"cart{self.mode.capitalize()}Button"}:disabled {{
                background-color: {get_color('button_disabled', '#aaaaaa')};
                color: {get_color('text_disabled', '#dddddd')};
            }}
        """)

    def add_item(self, product_data, quantity=1):
        """Add an item to the cart."""
        parcode = product_data.get('parcode')

        if not parcode:
            return False

        # Check if item already exists in cart
        if parcode in self.cart_items:
            # Update quantity
            current_data = self.cart_items[parcode]
            current_qty = current_data.get('cart_quantity', 1)
            new_qty = current_qty + quantity

            # Apply quantity limits for sell mode
            if self.mode == "sell":
                max_qty = product_data.get('quantity', 0)
                new_qty = min(new_qty, max_qty)

            current_data['cart_quantity'] = new_qty

            # Update UI
            self._update_cart_display()
            return True

        # New item
        product_copy = product_data.copy()
        product_copy['cart_quantity'] = quantity
        self.cart_items[parcode] = product_copy

        # Update UI
        self._update_cart_display()
        return True

    def remove_item(self, parcode):
        """Remove an item from the cart."""
        # First try to find the item with the parcode as a string
        if parcode in self.cart_items:
            del self.cart_items[parcode]
            self._update_cart_display()
            return True

        # If not found, try to find it as an integer (convert the string to integer)
        try:
            int_parcode = int(parcode)
            if int_parcode in self.cart_items:
                del self.cart_items[int_parcode]
                self._update_cart_display()
                return True
        except (ValueError, TypeError):
            pass

        # If still not found, try to convert all keys to strings for comparison
        str_parcode = str(parcode)
        for key in list(self.cart_items.keys()):
            if str(key) == str_parcode:
                del self.cart_items[key]
                self._update_cart_display()
                return True

        return False

    def update_item_quantity(self, parcode, quantity):
        """Update the quantity of an item in the cart."""
        # Handle both string and integer parcodes
        found = False

        # Try direct lookup
        if parcode in self.cart_items:
            self.cart_items[parcode]['cart_quantity'] = quantity
            found = True
        else:
            # Try as integer
            try:
                int_parcode = int(parcode)
                if int_parcode in self.cart_items:
                    self.cart_items[int_parcode]['cart_quantity'] = quantity
                    found = True
            except (ValueError, TypeError):
                pass

            # Try comparing as strings
            if not found:
                str_parcode = str(parcode)
                for key in self.cart_items:
                    if str(key) == str_parcode:
                        self.cart_items[key]['cart_quantity'] = quantity
                        found = True
                        break

        if found:
            self._update_totals()
            return True
        return False

    def clear_cart(self):
        """Clear all items from the cart."""
        self.cart_items = {}
        self._update_cart_display()

    def get_cart_data(self):
        """Get all cart data for checkout."""
        return {
            'mode': self.mode,
            'items': list(self.cart_items.values()),
            'total_price': self._calculate_total(),
            'total_items': self._calculate_item_count()
        }

    def _update_cart_display(self):
        """Update the cart items display."""
        # Clear current items
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add items or empty state
        if not self.cart_items:
            # Stylish empty state with icon
            empty_container = QWidget()
            empty_container.setObjectName("emptyCartContainer")
            empty_layout = QVBoxLayout(empty_container)

            # Empty icon
            empty_icon = QLabel("🛒" if self.mode == "sell" else "📦")
            empty_icon.setObjectName("emptyCartIcon")
            empty_icon.setAlignment(Qt.AlignCenter)
            font = empty_icon.font()
            font.setPointSize(32)
            empty_icon.setFont(font)

            # Empty message
            empty_message = (
                self._translate("empty_cart_sell", "Your sales cart is empty")
                if self.mode == "sell"
                else self._translate("empty_cart_supply", "Your supply list is empty")
            )
            self.empty_label = QLabel(empty_message)
            self.empty_label.setObjectName("emptyCartLabel")
            self.empty_label.setAlignment(Qt.AlignCenter)

            # Empty hint
            empty_hint = QLabel(
                self._translate("empty_cart_hint", "Add items using the search panel")
            )
            empty_hint.setObjectName("emptyCartHint")
            empty_hint.setAlignment(Qt.AlignCenter)

            empty_layout.addStretch(1)
            empty_layout.addWidget(empty_icon)
            empty_layout.addWidget(self.empty_label)
            empty_layout.addWidget(empty_hint)
            empty_layout.addStretch(1)

            self.items_layout.addWidget(empty_container)
            self.checkout_btn.setEnabled(False)
        else:
            # Add items directly without animations that might cause problems
            for parcode, product_data in self.cart_items.items():
                item_widget = CartItem(product_data, self.mode, translator=self.translator)
                # Connect signals
                item_widget.remove_clicked.connect(self.remove_item)
                item_widget.quantity_changed.connect(self.update_item_quantity)

                # Add widget - no animation for now to ensure visibility
                self.items_layout.addWidget(item_widget)

            # Add stretch at the end
            self.items_layout.addStretch(1)

            # Enable checkout button
            self.checkout_btn.setEnabled(True)

        # Update totals
        self._update_totals()

    def _update_totals(self):
        """Update the totals display."""
        total_price = self._calculate_total()
        total_items = self._calculate_item_count()

        self.subtotal_value.setText(f"${total_price:.2f}")
        self.items_value.setText(str(total_items))

    def _calculate_total(self):
        """Calculate the total price of all items in the cart."""
        total = 0.0
        for product_data in self.cart_items.values():
            price = product_data.get('price', 0.0)
            quantity = product_data.get('cart_quantity', 1)

            # Convert price to float to ensure type consistency
            if hasattr(price, 'to_float'):  # For Decimal objects with to_float method
                price = price.to_float()
            else:
                try:
                    price = float(price)  # Works with both floats and Decimal objects
                except (TypeError, ValueError):
                    price = 0.0  # Default if conversion fails

            total += price * quantity
        return total

    def _calculate_item_count(self):
        """Calculate the total number of items in the cart."""
        count = 0
        for product_data in self.cart_items.values():
            count += product_data.get('cart_quantity', 1)
        return count

    def on_checkout_clicked(self):
        """Handle checkout button click."""
        self.checkout_clicked.emit(self.get_cart_data())

    def eventFilter(self, obj, event):
        """Handle resize events to dynamically adjust layout."""
        if obj == self and event.type() == QEvent.Resize:
            width = self.width()
            # Update widget layout based on available width
            self._update_layout_for_width(width)

        return super().eventFilter(obj, event)

    def _update_layout_for_width(self, width):
        """Update widget layout based on available width."""
        # Force refresh of cart items to update their text display
        for i in range(self.items_layout.count()):
            item = self.items_layout.itemAt(i).widget()
            if isinstance(item, CartItem):
                item.update_text_display()