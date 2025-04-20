"""
Product related components for displaying product details with enhanced styling
and dynamic theme responsiveness.
"""
from PyQt5.QtCore import Qt, pyqtSignal, QEvent, QSize
from PyQt5.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGridLayout, QScrollArea, QSizePolicy, QGraphicsDropShadowEffect,
    QSpacerItem, QMessageBox, QToolButton
)
from PyQt5.QtGui import QFont, QColor, QCursor, QIcon

from themes import get_color, get_size, get_font_size
from themes.theme_events import theme_event_manager
from .quantity_selector import QuantitySelector
from .enhanced_scroll_bar import EnhancedScrollBar
from bartender_integration import BartenderManager, PrintDialog

class IconButton(QToolButton):
    """Modern icon button with sophisticated hover effects"""

    def __init__(self, icon_char, tooltip, parent=None):
        super().__init__(parent)
        self.setText(icon_char)
        self.setToolTip(tooltip)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self.setObjectName("modernIconButton")

        # Set size policy and fixed size for consistent layout
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(32, 32)

        # Center the icon/text
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)

        # Use a larger font for Unicode icons
        font = self.font()
        font.setPointSize(14)
        self.setFont(font)

class ProductDetailCard(QFrame):
    """A modern, elegant card that displays product details with dynamic theme support."""

    add_to_cart = pyqtSignal(dict, int)  # Product data, quantity

    def __init__(self, product_data, parent=None, translator=None, settings_db=None):
        super().__init__(parent)
        self.product_data = product_data
        self.translator = translator
        self.current_mode = "view"  # Default mode

        # Initialize Bartender manager if settings_db is provided
        self.bartender_manager = None
        if settings_db:
            self.bartender_manager = BartenderManager(settings_db, translator)
            self.bartender_manager.printing_complete.connect(self.on_printing_complete)

        # Setup UI components
        self.setup_ui()

        # Connect to theme change events
        theme_event_manager.theme_changed.connect(self.on_theme_changed)

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the card UI with a refined, elegant styling and intuitive layout."""
        self.setObjectName("productCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.setMinimumHeight(110)  # Reduced height for compactness
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Create a container for the content with margins
        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("productCardContent")

        # Main layout for the overall widget with reduced margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 6, 8, 6)  # More compact margins
        main_layout.setSpacing(0)

        # Layout for the actual content
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(12, 10, 12, 10)  # More compact internal margins
        layout.setSpacing(4)  # Reduced spacing

        # Add the content widget to the main layout
        main_layout.addWidget(self.content_widget)

        # Modern shadow effect
        self.shadow = QGraphicsDropShadowEffect(self.content_widget)
        self.shadow.setBlurRadius(15)  # Reduced blur
        self.shadow.setColor(QColor(0, 0, 0, 15))
        self.shadow.setOffset(0, 2)
        self.content_widget.setGraphicsEffect(self.shadow)

        # Header layout with product name and bartender buttons
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)
        header_layout.setContentsMargins(0, 0, 0, 2)  # Reduced bottom margin

        # Left section for product name
        name_container = QWidget()
        name_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        name_layout = QVBoxLayout(name_container)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_layout.setSpacing(0)

        # Product name
        name = self.product_data.get('product_name', 'Unknown Product')
        self.name_label = QLabel(name)
        self.name_label.setObjectName("productName")
        self.name_label.setWordWrap(True)
        font = self.name_label.font()
        font.setPointSize(get_font_size("large"))
        font.setBold(True)
        self.name_label.setFont(font)

        name_layout.addWidget(self.name_label)
        header_layout.addWidget(name_container)

        # Right section for Bartender buttons
        button_container = QWidget()
        button_container.setObjectName("bartenderButtonContainer")
        button_container.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(5)

        # Preview button with icon
        self.preview_btn = IconButton("👁️", self._translate("preview_label", "Preview Label"))
        self.preview_btn.setObjectName("previewButton")
        self.preview_btn.clicked.connect(self.preview_product_label)
        button_layout.addWidget(self.preview_btn)

        # Print button with icon
        self.print_btn = IconButton("🖨️", self._translate("print_label", "Print Label"))
        self.print_btn.setObjectName("printButton")
        self.print_btn.clicked.connect(self.print_product_label)
        button_layout.addWidget(self.print_btn)

        header_layout.addWidget(button_container)
        layout.addLayout(header_layout)

        # Divider below header
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setFrameShadow(QFrame.Sunken)
        divider.setObjectName("headerDivider")
        layout.addWidget(divider)

        # Reduced spacing
        layout.addSpacing(2)

        # Main content using grid for better alignment
        main_content_widget = QWidget()
        main_content = QGridLayout(main_content_widget)
        main_content.setContentsMargins(0, 0, 0, 0)
        main_content.setHorizontalSpacing(6)  # Horizontal spacing between info and action sections
        main_content.setVerticalSpacing(0)  # No vertical spacing in the grid

        # Details section with refined styling
        info_container = QFrame()
        info_container.setObjectName("infoContainer")
        info_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(8, 6, 8, 6)  # Reduced margins
        info_layout.setSpacing(1)  # Tighter spacing

        # Details layout with 2 columns
        details_layout = QGridLayout()
        details_layout.setHorizontalSpacing(8)  # Reduced spacing
        details_layout.setVerticalSpacing(4)  # Reduced spacing

        # Get product details with fallbacks
        parcode = self.product_data.get('parcode', 'N/A')
        price = self.product_data.get('price', 0.0)
        stock = self.product_data.get('quantity', 0)
        manufacturer = self.product_data.get('manufacturer', 'N/A')

        # Format price with 2 decimal places
        formatted_price = f"${price:.2f}" if price is not None else "N/A"

        # Create detail labels
        details = [
            (self._translate("parcode", "Parcode"), f"{parcode}"),
            (self._translate("manufacturer", "Manufacturer"), manufacturer),
            (self._translate("price", "Price"), formatted_price),
            (self._translate("quantity", "In Stock"), f"{stock}")
        ]

        # Add all details to grid
        for row, (label_text, value_text) in enumerate(details):
            # Create label
            label = QLabel(f"{label_text}:")
            label.setObjectName("detailLabel")
            font = label.font()
            font.setPointSize(get_font_size("large"))
            font.setBold(True)
            label.setFont(font)
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            # Create value with container
            value_container = QWidget()
            value_container.setObjectName("detailValueContainer")
            value_layout = QHBoxLayout(value_container)
            value_layout.setContentsMargins(0, 0, 0, 0)

            value = QLabel(value_text)
            value.setObjectName("detailValue")
            value.setWordWrap(True)
            value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            # No direct font setting here

            value_layout.addWidget(value, 1)
            value_layout.addStretch()

            # Add to layout
            details_layout.addWidget(label, row, 0, Qt.AlignRight | Qt.AlignVCenter)
            details_layout.addWidget(value_container, row, 1, 1, 1)

        # Set column stretch
        details_layout.setColumnStretch(0, 0)
        details_layout.setColumnStretch(1, 1)

        info_layout.addLayout(details_layout)

        # Add info container to main grid
        main_content.addWidget(info_container, 0, 0, 5, 1)  # Spans all rows, first column

        # Action section - horizontal layout for buttons
        # Create a single button section that aligns with the quantity row (row 3)
        action_container = QFrame()
        action_container.setObjectName("actionContainer")
        action_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(6, 4, 6, 4)
        action_layout.setSpacing(6)

        # Quantity selector
        max_qty = max(1, int(stock)) if stock is not None else 999
        self.quantity_selector = QuantitySelector(initial_value=1, min_value=1, max_value=max_qty, mode="view")
        self.quantity_selector.setObjectName("compactQuantitySelector")
        self.quantity_selector.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        action_layout.addWidget(self.quantity_selector)

        # Add to cart button
        self.add_cart_btn = QPushButton(self._translate("add_to_cart", "Add to Cart"))
        self.add_cart_btn.setObjectName("addToCartButton")
        self.add_cart_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_cart_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.add_cart_btn.setMinimumHeight(28)
        self.add_cart_btn.setMaximumHeight(28)
        self.add_cart_btn.clicked.connect(self.on_add_to_cart)
        action_layout.addWidget(self.add_cart_btn)

        # Add action container to the 4th row (quantity row) in the second column
        main_content.addWidget(action_container, 4, 1, 1, 1)  # Row 4, col 1, 1x1 cell

        # Add empty widgets for other rows in column 1 to maintain grid structure
        for i in range(5):
            if i != 4:  # Skip the row where we added the action container
                spacer = QWidget()
                spacer.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
                main_content.addWidget(spacer, i, 1, 1, 1)

        # Set column stretch
        main_content.setColumnStretch(0, 3)  # Info section takes more space
        main_content.setColumnStretch(1, 2)  # Action section takes less space

        layout.addWidget(main_content_widget)

        # Apply initial styling
        self.apply_styling()

    def apply_styling(self):
        """Apply elegant, refined styling to the card with improved readability."""
        # Get base colors from the theme
        highlight_color = QColor(get_color('highlight'))
        accent_color = QColor(get_color('accent', "#805AD5"))  # Use accent color for Bartender buttons
        button_color = QColor(get_color('button'))
        card_bg_color = QColor(get_color('card_bg'))
        text_color = QColor(get_color('text'))
        secondary_text = QColor(get_color('secondary_text'))
        border_color = QColor(get_color('border'))

        # Create lighter/darker variations for depth
        card_bg_lighter = card_bg_color.lighter(105).name()
        border_subtle = border_color.darker(110).name()

        # Generate button colors with varying transparencies
        accent_trans = f"rgba({accent_color.red()}, {accent_color.green()}, {accent_color.blue()}, 0.9)"
        accent_hover = f"rgba({accent_color.red()}, {accent_color.green()}, {accent_color.blue()}, 1.0)"
        accent_pressed = accent_color.darker(110).name()

        # Apply elegant styling to the card
        self.setStyleSheet(f"""
            #productCard {{
                background-color: transparent;
                border: none;
            }}

            #productCardContent {{
                background-color: {get_color('card_bg')};
                border-radius: {get_size('border_radius_medium')}px;
                border: 1px solid {border_subtle};
            }}

            #productName {{
                color: {get_color('title')};
                font-size: {get_font_size("large")}px;
                letter-spacing: -0.2px;
            }}
            
            #headerDivider {{
                color: {border_subtle};
                height: 1px;
                background-color: {border_subtle};
                margin-top: 4px;
                margin-bottom: 4px;
            }}

            #infoContainer, #actionContainer {{
                background-color: {card_bg_lighter};
                border-radius: 6px;
                border: 1px solid {border_subtle};
            }}

            #detailLabel {{
                color: {secondary_text.name()};
                padding-right: 6px;
                min-width: 75px; /* Reduced width */
                font-size: {get_font_size("medium")}px;
                letter-spacing: 0.2px;
            }}

            #detailValue {{
                color: {text_color.name()};
                font-weight: normal;
                font-size: {get_font_size("xlarge") + 4}px; /* Larger font size */
            }}

            /* Style for more compact quantity selector */
            #compactQuantitySelector {{
                max-height: 28px; /* Match button height */
            }}

            /* These selectors should apply to all children of the quantity selector */
            #compactQuantitySelector * {{
                margin: 0;
                padding: 0;
            }}

            /* For the input and buttons inside the quantity selector */
            #compactQuantitySelector QLineEdit,
            #compactQuantitySelector QPushButton {{
                max-height: 28px;
                min-height: 28px;
            }}

            #addToCartButton {{
                background-color: {get_color('highlight')};
                color: {get_color('highlight_text')};
                border-radius: {get_size('border_radius_small')}px;
                font-weight: bold;
                font-size: {get_font_size("small")}px;
                padding: 4px 10px; /* Reduced padding */
                border: none;
                height: 28px; /* Compact height */
            }}

            #addToCartButton:hover {{
                background-color: {highlight_color.lighter(110).name()};
            }}

            #addToCartButton:pressed {{
                background-color: {highlight_color.darker(105).name()};
            }}
            
            #bartenderButtonContainer {{
                margin-top: 2px;
            }}
            
            #modernIconButton {{
                background-color: {accent_trans};
                color: {get_color('highlight_text')};
                border-radius: 16px;  /* Circular buttons */
                border: none;
                font-size: 14px;
                text-align: center;
            }}

            #modernIconButton:hover {{
                background-color: {accent_hover};
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
                transform: translateY(-1px);
            }}

            #modernIconButton:pressed {{
                background-color: {accent_pressed};
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                transform: translateY(0px);
            }}
        """)

    def get_product_id(self):
        """Get the product ID."""
        return self.product_data.get('parcode')

    def get_quantity(self):
        """Get the selected quantity."""
        return self.quantity_selector.get_quantity()

    def get_product_data(self):
        """Get the complete product data dictionary."""
        return self.product_data

    def get_transaction_data(self):
        """Get data needed for a transaction."""
        return {
            'parcode': self.product_data.get('parcode'),
            'product_name': self.product_data.get('product_name'),
            'price': self.product_data.get('price', 0.0),
            'quantity': self.quantity_selector.get_quantity()
        }

    def on_add_to_cart(self):
        """Handle add to cart button click."""
        quantity = self.quantity_selector.get_quantity()
        self.add_to_cart.emit(self.product_data, quantity)

    def preview_product_label(self):
        """Preview the product label in Bartender"""
        if not self.bartender_manager:
            QMessageBox.warning(
                self,
                self._translate("error", "Error"),
                self._translate("bartender_not_configured", "Bartender integration is not configured"),
                buttons=QMessageBox.Ok
            )
            return

        product_name = self.product_data.get('product_name', '')
        if product_name:
            success = self.bartender_manager.preview_label(product_name)
            if not success:
                # The BartenderManager will handle error messages, no need to show additional ones
                pass
        else:
            QMessageBox.warning(
                self,
                self._translate("error", "Error"),
                self._translate("product_name_missing", "Product name is missing"),
                buttons=QMessageBox.Ok
            )

    def print_product_label(self):
        """Print the product label"""
        if not self.bartender_manager:
            QMessageBox.warning(
                self,
                self._translate("error", "Error"),
                self._translate("bartender_not_configured", "Bartender integration is not configured"),
                buttons=QMessageBox.Ok
            )
            return

        product_name = self.product_data.get('product_name', '')
        if not product_name:
            QMessageBox.warning(
                self,
                self._translate("error", "Error"),
                self._translate("product_name_missing", "Product name is missing"),
                buttons=QMessageBox.Ok
            )
            return

        # Check if Bartender is properly configured
        if not self.bartender_manager.bartender_path or not self.bartender_manager.labels_folder:
            QMessageBox.warning(
                self,
                self._translate("error", "Error"),
                self._translate("bartender_not_configured", "Bartender executable path not configured in settings"),
                buttons=QMessageBox.Ok
            )
            return

        # Show print dialog to select number of copies
        print_dialog = PrintDialog(product_name, self.translator, self)
        if print_dialog.exec_() == PrintDialog.Accepted:
            quantity = print_dialog.get_quantity()
            self.bartender_manager.print_label(product_name, quantity)

    def on_printing_complete(self, success, message):
        """Handle print completion signal"""
        if success:
            QMessageBox.information(
                self,
                self._translate("success", "Success"),
                message,
                buttons=QMessageBox.Ok
            )
        else:
            QMessageBox.warning(
                self,
                self._translate("error", "Error"),
                message,
                buttons=QMessageBox.Ok
            )

    def on_theme_changed(self, theme_name):
        """Update styling when theme changes."""
        # Re-apply styling with the new theme colors
        self.apply_styling()

        # Re-apply mode-specific styling if needed
        if hasattr(self, 'current_mode'):
            self.set_mode(self.current_mode)

    def set_mode(self, mode):
        """Set the mode (sell/supply) and update the UI accordingly with modern, elegant styling."""
        # Store current mode for theme change updates
        self.current_mode = mode

        # Update the quantity selector mode
        current_stock = self.product_data.get('quantity', 0)
        self.quantity_selector.set_mode(mode, current_stock if mode == "sell" else None)

        # Get theme colors for the mode
        error_color = QColor(get_color('error'))
        highlight_color = QColor(get_color('highlight'))
        accent_color = QColor(get_color('accent', "#805AD5"))
        card_bg_color = QColor(get_color('card_bg'))

        # Determine button colors based on mode with transparency
        btn_color = error_color if mode == "sell" else highlight_color
        btn_transparent = f"rgba({btn_color.red()}, {btn_color.green()}, {btn_color.blue()}, 0.85)"
        btn_hover = btn_color.name()
        btn_pressed = btn_color.darker(105).name()

        # Create gradient overlay based on mode
        if mode == "sell":
            # Subtle red overlay for sell mode
            overlay_start = f"rgba({error_color.red()}, {error_color.green()}, {error_color.blue()}, 0.03)"
            overlay_end = f"rgba({error_color.red()}, {error_color.green()}, {error_color.blue()}, 0.01)"
        else:
            # Subtle blue overlay for supply mode
            overlay_start = f"rgba({highlight_color.red()}, {highlight_color.green()}, {highlight_color.blue()}, 0.03)"
            overlay_end = f"rgba({highlight_color.red()}, {highlight_color.green()}, {highlight_color.blue()}, 0.01)"

        # Apply modern mode-specific styling with gradient
        self.content_widget.setStyleSheet(f"""
            background-color: {get_color('card_bg')};
            border-radius: 16px;
            border: none;
            background: linear-gradient(135deg, {overlay_start}, {overlay_end});
        """)

        # Update the shadow color to match the mode with modern aesthetics
        shadow_color = QColor(btn_color.red(), btn_color.green(), btn_color.blue(), 15)
        self.shadow.setColor(shadow_color)
        self.shadow.setBlurRadius(30)  # Softer, more diffused shadow

        # Update button text and styling
        if mode == "sell":
            self.add_cart_btn.setText(self._translate("add_to_cart", "Add to Cart"))
        else:
            self.add_cart_btn.setText(self._translate("add_to_supply", "Add to Supply"))

        # Apply modern button styling
        self.add_cart_btn.setStyleSheet(f"""
            #addToCartButton {{
                background-color: {btn_transparent};
                color: {get_color('highlight_text')};
                border-radius: 8px;
                font-weight: 600;
                font-size: {get_font_size('large')}px;
                padding: 4px 16px;
                border: none;
                height: 36px;
            }}
            
            #addToCartButton:hover {{
                background-color: {btn_hover};
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
            
            #addToCartButton:pressed {{
                background-color: {btn_pressed};
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
        """)

        # Accent color with transparency for icon buttons based on current mode
        accent_trans = f"rgba({accent_color.red()}, {accent_color.green()}, {accent_color.blue()}, 0.9)"
        accent_hover = f"rgba({accent_color.red()}, {accent_color.green()}, {accent_color.blue()}, 1.0)"

        # Apply modern circular button styling
        modern_buttons_style = f"""
            #modernIconButton {{
                background-color: {accent_trans};
                color: {get_color('highlight_text')};
                border-radius: 16px;
                border: none;
                font-size: 14px;
                text-align: center;
            }}
            
            #modernIconButton:hover {{
                background-color: {accent_hover};
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
                transform: translateY(-1px);
                transition: all 0.2s ease;
            }}
            
            #modernIconButton:pressed {{
                background-color: {accent_color.darker(110).name()};
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                transform: translateY(0px);
            }}
        """

        # Update icon button styling
        self.preview_btn.setStyleSheet(modern_buttons_style)
        self.print_btn.setStyleSheet(modern_buttons_style)