"""
Modern Register Widget for the Abu Mukh Car Parts Management System.
This widget provides a clean interface for processing sales and receiving inventory.
"""
import datetime
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer, QEvent, QPropertyAnimation, QEasingCurve, QPoint
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QScrollArea, QGridLayout, QSpinBox, QMessageBox, QCompleter,
    QSizePolicy, QStackedWidget, QDialog, QGraphicsDropShadowEffect, QListWidget,
    QListWidgetItem, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette, QCursor

from widgets.products.components.barcode_scanner_button import BarcodeScannerButton
from themes import get_color, get_size, get_font_size
from size_policy import SizePolicyMixin, ResponsiveFontMixin


class CustomDialog(QDialog):
    """A beautifully styled custom dialog that integrates with the theme system."""

    def __init__(self, title, message, icon_type="info", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setMinimumWidth(400)

        # Set up the UI
        self.setup_ui(title, message, icon_type)
        self.apply_styling()

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

    def setup_ui(self, title, message, icon_type):
        """Set up the dialog UI with an elegant layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header area with icon and title
        header_layout = QHBoxLayout()

        # Icon label
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)

        # Set appropriate icon based on type
        icon_path = None
        if icon_type == "info":
            icon_path = "resources/info_icon.png"
            fallback_emoji = "ℹ️"
            self.icon_color = QColor(get_color('highlight', '#2196F3'))
        elif icon_type == "warning":
            icon_path = "resources/warning_icon.png"
            fallback_emoji = "⚠️"
            self.icon_color = QColor(get_color('warning', '#FFC107'))
        elif icon_type == "error":
            icon_path = "resources/error_icon.png"
            fallback_emoji = "❌"
            self.icon_color = QColor(get_color('error', '#F44336'))
        elif icon_type == "success":
            icon_path = "resources/success_icon.png"
            fallback_emoji = "✅"
            self.icon_color = QColor(get_color('success', '#4CAF50'))
        elif icon_type == "question":
            icon_path = "resources/question_icon.png"
            fallback_emoji = "❓"
            self.icon_color = QColor(get_color('highlight', '#2196F3'))

        # Try to load icon, use emoji as fallback
        if icon_path:
            try:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    self.icon_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.icon_label.setText(fallback_emoji)
                    font = self.icon_label.font()
                    font.setPointSize(24)
                    self.icon_label.setFont(font)
            except:
                self.icon_label.setText(fallback_emoji)
                font = self.icon_label.font()
                font.setPointSize(24)
                self.icon_label.setFont(font)
        else:
            self.icon_label.setText(fallback_emoji)
            font = self.icon_label.font()
            font.setPointSize(24)
            self.icon_label.setFont(font)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setObjectName("dialogTitle")
        font = self.title_label.font()
        font.setPointSize(get_font_size("xlarge"))
        font.setBold(True)
        self.title_label.setFont(font)

        # Add to header layout
        header_layout.addWidget(self.icon_label)
        header_layout.addSpacing(16)
        header_layout.addWidget(self.title_label, 1)

        # Message label with larger font
        self.message_label = QLabel(message)
        self.message_label.setObjectName("dialogMessage")
        self.message_label.setWordWrap(True)
        font = self.message_label.font()
        font.setPointSize(get_font_size("large"))
        self.message_label.setFont(font)

        # Button layout
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(1)

        # Add components to main layout
        layout.addLayout(header_layout)
        layout.addWidget(self.message_label)
        layout.addStretch(1)
        layout.addLayout(self.button_layout)

    def apply_styling(self):
        """Apply elegant styling to the dialog."""
        # Get theme colors
        bg_color = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        button_color = get_color('button')
        button_hover = get_color('button_hover')
        highlight_color = get_color('highlight')

        # Create style sheet
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {get_size('border_radius_large')}px;
            }}
            
            #dialogTitle {{
                color: {text_color};
            }}
            
            #dialogMessage {{
                color: {text_color};
                margin: 10px 0;
            }}
            
            QPushButton {{
                background-color: {button_color};
                color: {text_color};
                border: none;
                border-radius: {get_size('border_radius_medium')}px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: {get_font_size('medium')}px;
                min-width: 100px;
                min-height: 40px;
            }}
            
            QPushButton:hover {{
                background-color: {button_hover};
            }}
            
            QPushButton:pressed {{
                background-color: {get_color('button_pressed')};
            }}
            
            QPushButton#primaryButton {{
                background-color: {highlight_color};
                color: {get_color('highlight_text', '#FFFFFF')};
            }}
            
            QPushButton#primaryButton:hover {{
                background-color: {QColor(highlight_color).lighter(110).name()};
            }}
            
            QPushButton#primaryButton:pressed {{
                background-color: {QColor(highlight_color).darker(110).name()};
            }}
            
            QPushButton#dangerButton {{
                background-color: {get_color('error')};
                color: white;
            }}
            
            QPushButton#dangerButton:hover {{
                background-color: {QColor(get_color('error')).lighter(110).name()};
            }}
            
            QPushButton#dangerButton:pressed {{
                background-color: {QColor(get_color('error')).darker(110).name()};
            }}
            
            QPushButton#successButton {{
                background-color: {get_color('success')};
                color: white;
            }}
            
            QPushButton#successButton:hover {{
                background-color: {QColor(get_color('success')).lighter(110).name()};
            }}
            
            QPushButton#successButton:pressed {{
                background-color: {QColor(get_color('success')).darker(110).name()};
            }}
        """)

    def add_button(self, text, role="normal", is_default=False, callback=None):
        """Add a button to the dialog with appropriate styling."""
        button = QPushButton(text)
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # Set button style based on role
        if role == "primary":
            button.setObjectName("primaryButton")
        elif role == "danger":
            button.setObjectName("dangerButton")
        elif role == "success":
            button.setObjectName("successButton")

        # Set as default button if specified
        if is_default:
            button.setDefault(True)

        # Connect callback if provided
        if callback:
            button.clicked.connect(callback)

        # Add to button layout
        self.button_layout.addWidget(button)
        return button


class InfoDialog(CustomDialog):
    """Information dialog with a single OK button."""

    def __init__(self, title, message, parent=None):
        super().__init__(title, message, "info", parent)
        self.ok_button = self.add_button("OK", "primary", True, self.accept)


class WarningDialog(CustomDialog):
    """Warning dialog with a single OK button."""

    def __init__(self, title, message, parent=None):
        super().__init__(title, message, "warning", parent)
        self.ok_button = self.add_button("OK", "primary", True, self.accept)


class ErrorDialog(CustomDialog):
    """Error dialog with a single OK button."""

    def __init__(self, title, message, parent=None):
        super().__init__(title, message, "error", parent)
        self.ok_button = self.add_button("OK", "primary", True, self.accept)


class SuccessDialog(CustomDialog):
    """Success dialog with a single OK button."""

    def __init__(self, title, message, parent=None):
        super().__init__(title, message, "success", parent)
        self.ok_button = self.add_button("OK", "success", True, self.accept)


class ConfirmationDialog(CustomDialog):
    """Confirmation dialog with Yes and No buttons."""

    def __init__(self, title, message, yes_text="Yes", no_text="No", parent=None):
        super().__init__(title, message, "question", parent)

        # Add No button (closes with reject)
        self.no_button = self.add_button(no_text, "normal", False, self.reject)

        # Add Yes button (closes with accept)
        self.yes_button = self.add_button(yes_text, "primary", True, self.accept)


"""
Updates to improve the Product Detail Card appearance and fix quantity selector functionality.
Replace these classes in your register_widget.py file.
"""


class QuantitySelector(QWidget):
    """An enhanced quantity selector with +/- buttons and a spinbox."""

    quantity_changed = pyqtSignal(int)

    def __init__(self, parent=None, initial_value=1, min_value=1, max_value=999):
        super().__init__(parent)
        self.setup_ui(initial_value, min_value, max_value)

    def setup_ui(self, initial_value, min_value, max_value):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)  # Increased spacing

        # Minus button - make it more prominent
        self.minus_btn = QPushButton("-")
        self.minus_btn.setFixedSize(40, 40)  # Slightly larger
        self.minus_btn.setObjectName("quantityButton")
        self.minus_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.minus_btn.clicked.connect(self.decrease_quantity)

        # Quantity spinbox - improved styling
        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(min_value)
        self.spinbox.setMaximum(max_value)
        self.spinbox.setValue(initial_value)
        self.spinbox.setFixedHeight(40)  # Match button height
        self.spinbox.setMinimumWidth(70)  # Wider for better visibility
        self.spinbox.setAlignment(Qt.AlignCenter)
        self.spinbox.valueChanged.connect(self.on_quantity_changed)

        # Disable keyboard tracking to prevent rapid-fire signals
        self.spinbox.setKeyboardTracking(False)

        # Plus button - make it more prominent
        self.plus_btn = QPushButton("+")
        self.plus_btn.setFixedSize(40, 40)  # Slightly larger
        self.plus_btn.setObjectName("quantityButton")
        self.plus_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.plus_btn.clicked.connect(self.increase_quantity)

        # Add widgets to layout
        layout.addWidget(self.minus_btn)
        layout.addWidget(self.spinbox)
        layout.addWidget(self.plus_btn)

        # Apply enhanced styling
        self.apply_styling()

        # Explicitly set focus policy to prevent unexpected focus behavior
        self.setFocusPolicy(Qt.StrongFocus)
        self.spinbox.setFocusPolicy(Qt.StrongFocus)

    def apply_styling(self):
        """Apply enhanced styling to the quantity selector."""
        highlight_color = get_color('highlight')
        text_color = get_color('text')

        button_style = f"""
            QPushButton#quantityButton {{
                background-color: {get_color('button')};
                color: {text_color};
                border-radius: 6px;
                font-weight: bold;
                font-size: 18px;
                margin: 0px;
                padding: 0px;
                border: none;
                box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
            }}

            QPushButton#quantityButton:hover {{
                background-color: {get_color('button_hover')};
                transform: translateY(-1px);
                box-shadow: 0px 3px 5px rgba(0, 0, 0, 0.3);
            }}

            QPushButton#quantityButton:pressed {{
                background-color: {get_color('button_pressed')};
                transform: translateY(1px);
                box-shadow: 0px 1px 2px rgba(0, 0, 0, 0.2);
            }}

            QSpinBox {{
                background-color: {get_color('input_bg')};
                color: {text_color};
                border: 2px solid {get_color('border')};
                border-radius: 6px;
                padding: 2px 10px;
                font-size: 16px;
                font-weight: bold;
                selection-background-color: {highlight_color};
            }}

            QSpinBox:focus {{
                border: 2px solid {highlight_color};
            }}

            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0;
                height: 0;
                border: none;
                background: none;
            }}
        """
        self.setStyleSheet(button_style)

    def increase_quantity(self):
        """Increase the quantity by 1 with improved feedback."""
        current = self.spinbox.value()
        max_val = self.spinbox.maximum()

        # Only change if not at maximum
        if current < max_val:
            self.spinbox.setValue(current + 1)

            # Provide visual feedback on button press
            self.plus_btn.setStyleSheet(f"""
                background-color: {get_color('button_pressed')};
            """)
            QTimer.singleShot(150, self.reset_button_style)

    def decrease_quantity(self):
        """Decrease the quantity by 1 with improved feedback."""
        current = self.spinbox.value()
        min_val = self.spinbox.minimum()

        # Only change if not at minimum
        if current > min_val:
            self.spinbox.setValue(current - 1)

            # Provide visual feedback on button press
            self.minus_btn.setStyleSheet(f"""
                background-color: {get_color('button_pressed')};
            """)
            QTimer.singleShot(150, self.reset_button_style)

    def reset_button_style(self):
        """Reset button styling after visual feedback."""
        self.plus_btn.setStyleSheet("")
        self.minus_btn.setStyleSheet("")

    def on_quantity_changed(self, value):
        """Emit signal when quantity changes."""
        self.quantity_changed.emit(value)

    def get_quantity(self):
        """Get the current quantity value."""
        return self.spinbox.value()

    def set_quantity(self, value):
        """Set the quantity value with bounds checking."""
        min_val = self.spinbox.minimum()
        max_val = self.spinbox.maximum()
        bounded_value = max(min_val, min(value, max_val))
        self.spinbox.setValue(bounded_value)


class ProductDetailCard(QFrame):
    """An enhanced card that displays product details with quantity selection."""

    def __init__(self, product_data, parent=None, translator=None):
        super().__init__(parent)
        self.product_data = product_data
        self.translator = translator
        self.setup_ui()

        # Add shadow effect for depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the card UI with enhanced styling."""
        self.setObjectName("productCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(250)  # Slightly taller for better spacing

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)  # Increased margins
        layout.setSpacing(20)  # More spacing

        # Product name header with bigger font
        name = self.product_data.get('product_name', 'Unknown Product')
        self.name_label = QLabel(name)
        self.name_label.setObjectName("productName")
        font = self.name_label.font()
        font.setPointSize(get_font_size("xxlarge"))  # Larger font
        font.setBold(True)
        self.name_label.setFont(font)
        layout.addWidget(self.name_label)

        # Product details section with card-like appearance
        details_card = QFrame()
        details_card.setObjectName("detailsCard")
        details_layout = QVBoxLayout(details_card)
        details_layout.setContentsMargins(20, 20, 20, 20)
        details_layout.setSpacing(15)

        # Section title
        details_title = QLabel(self._translate("product_details", "Product Details"))
        details_title.setObjectName("sectionTitle")
        font = details_title.font()
        font.setPointSize(get_font_size("large"))
        font.setBold(True)
        details_title.setFont(font)
        details_layout.addWidget(details_title)

        # Grid for details with 2 columns
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(30)  # More horizontal spacing
        grid_layout.setVerticalSpacing(12)
        details_layout.addLayout(grid_layout)

        # Get product details with fallbacks
        parcode = self.product_data.get('parcode', 'N/A')
        category = self.product_data.get('category', 'N/A')
        price = self.product_data.get('price', 0.0)
        stock = self.product_data.get('quantity', 0)
        manufacturer = self.product_data.get('manufacturer', 'N/A')
        is_original = "Yes" if self.product_data.get('original', False) else "No"

        # Format price with 2 decimal places
        formatted_price = f"${price:.2f}" if price is not None else "N/A"

        # Create detail labels
        details = [
            (self._translate("id", "ID"), f"{parcode}"),
            (self._translate("category", "Category"), category),
            (self._translate("price", "Price"), formatted_price),
            (self._translate("quantity", "In Stock"), f"{stock}"),
            (self._translate("manufacturer", "Manufacturer"), manufacturer),
            (self._translate("original_part", "Original Part"), is_original)
        ]

        # Add compatible brands/models if available
        brands = self.product_data.get('compatible_brands', '')
        if brands:
            details.append((self._translate("compatible_brands", "Compatible Brands"), brands))

        models = self.product_data.get('compatible_models', '')
        if models:
            details.append((self._translate("compatible_models", "Compatible Models"), models))

        years = self.product_data.get('model_years', '')
        if years:
            details.append((self._translate("model_years", "Model Years"), years))

        # Add all details to grid with improved styling
        for row, (label_text, value_text) in enumerate(details):
            # Create label with icon or visual indicator
            label_container = QWidget()
            label_layout = QHBoxLayout(label_container)
            label_layout.setContentsMargins(0, 0, 0, 0)
            label_layout.setSpacing(8)

            # Add a colored dot as a visual indicator
            indicator = QFrame()
            indicator.setFixedSize(8, 8)
            indicator.setObjectName("fieldIndicator")
            label_layout.addWidget(indicator)

            # Label with the field name
            label = QLabel(f"{label_text}:")
            label.setObjectName("detailLabel")
            font = label.font()
            font.setPointSize(get_font_size("medium"))
            font.setBold(True)
            label.setFont(font)
            label_layout.addWidget(label)
            label_layout.addStretch()

            # Create value with enhanced styling
            value = QLabel(value_text)
            value.setObjectName("detailValue")
            value.setWordWrap(True)
            value.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Make text selectable
            value_font = value.font()
            value_font.setPointSize(get_font_size("medium"))
            value.setFont(value_font)

            # Add to grid layout
            grid_layout.addWidget(label_container, row, 0)
            grid_layout.addWidget(value, row, 1)

        # Add details card to main layout
        layout.addWidget(details_card)

        # Quantity section as its own card
        quantity_card = QFrame()
        quantity_card.setObjectName("quantityCard")
        quantity_layout = QVBoxLayout(quantity_card)
        quantity_layout.setContentsMargins(20, 20, 20, 20)

        # Quantity section title
        qty_title = QLabel(self._translate("select_quantity", "Select Quantity"))
        qty_title.setObjectName("sectionTitle")
        font = qty_title.font()
        font.setPointSize(get_font_size("large"))
        font.setBold(True)
        qty_title.setFont(font)
        quantity_layout.addWidget(qty_title)

        # Quantity selector with instruction text
        qty_container = QWidget()
        qty_container_layout = QHBoxLayout(qty_container)
        qty_container_layout.setContentsMargins(0, 10, 0, 0)

        # Max quantity note
        max_qty = max(1, int(stock)) if stock is not None else 999
        qty_note = QLabel(self._translate("max_quantity_note", f"Maximum: {max_qty}"))
        qty_note.setObjectName("quantityNote")

        # Enhanced quantity selector
        self.quantity_selector = QuantitySelector(initial_value=1, min_value=1, max_value=max_qty)

        # Layout the quantity controls
        qty_container_layout.addWidget(self.quantity_selector)
        qty_container_layout.addWidget(qty_note)
        qty_container_layout.addStretch(1)

        quantity_layout.addWidget(qty_container)

        # Add quantity card to main layout
        layout.addWidget(quantity_card)

        # Add spacer at the bottom
        layout.addStretch(1)

        # Apply enhanced styling
        self.apply_styling()

    def apply_styling(self):
        """Apply enhanced styling to the card."""
        highlight_color = get_color('highlight')
        card_bg = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        secondary_text = get_color('secondary_text')

        # Generate a slightly darker shade for the section cards
        card_bg_darker = QColor(card_bg)
        if card_bg_darker.lightness() > 128:
            card_bg_darker = card_bg_darker.darker(105)  # Darken slightly if light
        else:
            card_bg_darker = card_bg_darker.lighter(105)  # Lighten slightly if dark

        self.setStyleSheet(f"""
            #productCard {{
                background-color: {card_bg};
                border-radius: {get_size('border_radius_large')}px;
                border: 1px solid {border_color};
                padding: 5px;
            }}

            #productName {{
                color: {highlight_color};
                margin-bottom: 15px;
                padding-bottom: 5px;
                border-bottom: 2px solid {QColor(highlight_color).lighter(150).name()};
            }}

            #detailsCard, #quantityCard {{
                background-color: {card_bg_darker.name()};
                border-radius: {get_size('border_radius_medium')}px;
                border: 1px solid {border_color};
            }}

            #sectionTitle {{
                color: {highlight_color};
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 1px solid {border_color};
            }}

            #detailLabel {{
                color: {text_color};
                padding: 2px 0px;
            }}

            #detailValue {{
                color: {text_color};
                padding: 2px 0px;
            }}

            #fieldIndicator {{
                background-color: {highlight_color};
                border-radius: 4px;
            }}

            #quantityNote {{
                color: {secondary_text};
                font-style: italic;
                margin-left: 15px;
                padding-top: 10px;
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


class RelatedProductsSection(QWidget):
    """Enhanced section that displays related products."""

    product_selected = pyqtSignal(dict)
    add_related_clicked = pyqtSignal()

    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator
        self.products = []
        self.setup_ui()

        # Add shadow effect for depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the related products section UI with enhanced styling."""
        self.setObjectName("relatedProductsSection")

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)  # Increased margins
        layout.setSpacing(20)  # More spacing

        # Header with title and add button - improved layout
        header_container = QFrame()
        header_container.setObjectName("headerContainer")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 10)  # Bottom padding

        # Title with icon
        title_container = QWidget()
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(10)

        # Create a colored dot as a visual indicator
        indicator = QFrame()
        indicator.setFixedSize(10, 10)
        indicator.setObjectName("relatedIndicator")
        title_layout.addWidget(indicator)

        # Title text
        self.title_label = QLabel(self._translate("related_products", "Related Products"))
        self.title_label.setObjectName("relatedProductsTitle")
        font = self.title_label.font()
        font.setPointSize(get_font_size("xlarge"))  # Larger font
        font.setBold(True)
        self.title_label.setFont(font)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch(1)

        header_layout.addWidget(title_container)

        # Add related product button - enhanced styling
        self.add_button = QPushButton(self._translate("add_related", "Add Related"))
        self.add_button.setObjectName("addRelatedButton")
        self.add_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_button.setMinimumHeight(36)  # Taller button
        self.add_button.clicked.connect(self.add_related_clicked.emit)
        header_layout.addWidget(self.add_button)

        # Add the header to main layout
        layout.addWidget(header_container)

        # Add separator below header
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("relatedSeparator")
        layout.addWidget(separator)

        # Products scroll area with better styling
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("relatedProductsScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setMinimumHeight(150)  # Set minimum height

        # Scroll content with dynamic layout
        self.scroll_content = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 10, 0, 10)  # Add padding top/bottom
        self.scroll_layout.setSpacing(20)  # More space between items
        self.scroll_layout.setAlignment(Qt.AlignLeft)

        # Empty state label with icon
        empty_container = QWidget()
        empty_layout = QVBoxLayout(empty_container)
        empty_layout.setContentsMargins(20, 20, 20, 20)
        empty_layout.setAlignment(Qt.AlignCenter)

        empty_icon = QLabel("🔍")  # Using emoji as icon
        empty_icon.setAlignment(Qt.AlignCenter)
        font = empty_icon.font()
        font.setPointSize(32)  # Large icon
        empty_icon.setFont(font)
        empty_layout.addWidget(empty_icon)

        self.empty_label = QLabel(self._translate("no_related_products", "No related products found"))
        self.empty_label.setObjectName("noRelatedLabel")
        self.empty_label.setAlignment(Qt.AlignCenter)
        font = self.empty_label.font()
        font.setPointSize(get_font_size("large"))
        self.empty_label.setFont(font)
        empty_layout.addWidget(self.empty_label)

        self.scroll_layout.addWidget(empty_container, 1)  # Use stretch to center

        # Set scroll widget
        self.scroll_area.setWidget(self.scroll_content)

        # Add to main layout
        layout.addWidget(self.scroll_area)

        # Apply enhanced styling
        self.apply_styling()

    def apply_styling(self):
        """Apply enhanced styling to the related products section."""
        highlight_color = get_color('highlight')
        card_bg = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        secondary_text = get_color('secondary_text')

        # Create a slightly lighter shade for hover effects
        highlight_light = QColor(highlight_color).lighter(130).name()

        self.setStyleSheet(f"""
            #relatedProductsSection {{
                background-color: {card_bg};
                border-radius: {get_size('border_radius_large')}px;
                border: 1px solid {border_color};
            }}

            #headerContainer {{
                border-bottom: none;
                background-color: transparent;
            }}

            #relatedProductsTitle {{
                color: {highlight_color};
                padding-bottom: 5px;
            }}

            #relatedIndicator {{
                background-color: {highlight_color};
                border-radius: 5px;
            }}

            #relatedSeparator {{
                background-color: {border_color};
                height: 1px;
                margin: 0px 0px 10px 0px;
            }}

            #addRelatedButton {{
                background-color: {highlight_color};
                color: white;
                border: none;
                border-radius: {get_size('border_radius_medium')}px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 120px;
            }}

            #addRelatedButton:hover {{
                background-color: {highlight_light};
                box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
            }}

            #addRelatedButton:pressed {{
                background-color: {QColor(highlight_color).darker(110).name()};
                box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.2);
            }}

            #noRelatedLabel {{
                color: {secondary_text};
                font-style: italic;
                margin: 10px;
            }}

            #relatedProductsScroll {{
                background-color: transparent;
                border: none;
            }}

            QScrollBar:horizontal {{
                height: 12px;
                background: {QColor(card_bg).darker(105).name()};
                border-radius: 6px;
            }}

            QScrollBar::handle:horizontal {{
                background: {QColor(highlight_color).lighter(150).name()};
                min-width: 50px;
                border-radius: 6px;
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)

    def set_products(self, products):
        """Set the related products to display with improved transitions."""
        self.products = products

        # Clear existing content
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add products or empty state
        if not products:
            # Empty state with icon
            empty_container = QWidget()
            empty_layout = QVBoxLayout(empty_container)
            empty_layout.setContentsMargins(20, 20, 20, 20)
            empty_layout.setAlignment(Qt.AlignCenter)

            empty_icon = QLabel("🔍")  # Using emoji as icon
            empty_icon.setAlignment(Qt.AlignCenter)
            font = empty_icon.font()
            font.setPointSize(32)  # Large icon
            empty_icon.setFont(font)
            empty_layout.addWidget(empty_icon)

            self.empty_label = QLabel(self._translate("no_related_products", "No related products found"))
            self.empty_label.setObjectName("noRelatedLabel")
            self.empty_label.setAlignment(Qt.AlignCenter)
            font = self.empty_label.font()
            font.setPointSize(get_font_size("large"))
            self.empty_label.setFont(font)
            empty_layout.addWidget(self.empty_label)

            self.scroll_layout.addWidget(empty_container, 1)  # Use stretch to center
        else:
            # Add products with staggered animation
            for index, product in enumerate(products):
                product_item = RelatedProductItem(product, translator=self.translator)
                product_item.selected.connect(self.on_product_selected)

                # Set initial opacity for animation
                opacity_effect = QGraphicsOpacityEffect(product_item)
                opacity_effect.setOpacity(0.0)
                product_item.setGraphicsEffect(opacity_effect)

                self.scroll_layout.addWidget(product_item)

                # Create fade-in animation with staggered timing
                fade_animation = QPropertyAnimation(opacity_effect, b"opacity")
                fade_animation.setDuration(300)
                fade_animation.setStartValue(0.0)
                fade_animation.setEndValue(1.0)
                fade_animation.setEasingCurve(QEasingCurve.OutCubic)

                # Stagger the animations
                QTimer.singleShot(index * 100, fade_animation.start)

            # Add stretch at the end
            self.scroll_layout.addStretch(1)

    def on_product_selected(self, product_data):
        """Handle when a related product is selected."""
        self.product_selected.emit(product_data)


class RelatedProductItem(QFrame):
    """An enhanced card that displays a related product with basic details."""

    selected = pyqtSignal(dict)

    def __init__(self, product_data, parent=None, translator=None):
        super().__init__(parent)
        self.product_data = product_data
        self.translator = translator
        self.setup_ui()

        # Add shadow effect for depth
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the related product item UI with enhanced styling."""
        self.setObjectName("relatedProductItem")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setFixedWidth(200)  # Fixed width for consistent layout
        self.setMinimumHeight(160)  # Minimum height

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Product name header with icon
        name = self.product_data.get('product_name', 'Unknown Product')

        # Create header with icon
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Add a colored icon/indicator
        indicator = QLabel("•")  # Bullet point as indicator
        indicator.setObjectName("productIndicator")
        indicator.setAlignment(Qt.AlignCenter)
        font = indicator.font()
        font.setPointSize(14)
        font.setBold(True)
        indicator.setFont(font)
        header_layout.addWidget(indicator)

        # Product name
        self.name_label = QLabel(name)
        self.name_label.setObjectName("relatedProductName")
        self.name_label.setWordWrap(True)
        font = self.name_label.font()
        font.setPointSize(get_font_size("medium"))
        font.setBold(True)
        self.name_label.setFont(font)
        header_layout.addWidget(self.name_label, 1)  # Give name stretch priority

        layout.addWidget(header_container)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("itemSeparator")
        layout.addWidget(separator)

        # Manufacturer and price in a vertical layout for better space usage
        details_layout = QVBoxLayout()
        details_layout.setSpacing(6)

        # Manufacturer with icon
        manufacturer = self.product_data.get('manufacturer', '-')
        manufacturer_layout = QHBoxLayout()
        manufacturer_layout.setSpacing(8)

        manufacturer_icon = QLabel("🏭")  # Factory emoji
        manufacturer_icon.setObjectName("detailIcon")
        manufacturer_layout.addWidget(manufacturer_icon)

        manufacturer_text = f"{manufacturer}"
        self.manufacturer_label = QLabel(manufacturer_text)
        self.manufacturer_label.setObjectName("relatedProductDetail")
        manufacturer_layout.addWidget(self.manufacturer_label, 1)

        details_layout.addLayout(manufacturer_layout)

        # Price with icon
        price = self.product_data.get('price', 0.0)
        price_layout = QHBoxLayout()
        price_layout.setSpacing(8)

        price_icon = QLabel("💰")  # Money bag emoji
        price_icon.setObjectName("detailIcon")
        price_layout.addWidget(price_icon)

        formatted_price = f"${price:.2f}" if price is not None else "N/A"
        self.price_label = QLabel(formatted_price)
        self.price_label.setObjectName("relatedProductPrice")
        font = self.price_label.font()
        font.setBold(True)
        self.price_label.setFont(font)
        price_layout.addWidget(self.price_label, 1)

        details_layout.addLayout(price_layout)

        layout.addLayout(details_layout)

        # Add spacer
        layout.addStretch(1)

        # "Select" button with enhanced styling
        self.select_button = QPushButton(self._translate("select_button", "Select"))
        self.select_button.setObjectName("selectRelatedButton")
        self.select_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.select_button.setMinimumHeight(36)  # Taller button
        self.select_button.clicked.connect(self.on_selected)
        layout.addWidget(self.select_button)

        # Apply enhanced styling
        self.apply_styling()

        # Track hover state for animations
        self.installEventFilter(self)
        self._hovered = False

    def apply_styling(self):
        """Apply enhanced styling to the related product item."""
        highlight_color = get_color('highlight')
        card_bg = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')

        # Create a slightly darker shade for the item background
        card_bg_darker = QColor(card_bg)
        if card_bg_darker.lightness() > 128:
            card_bg_darker = card_bg_darker.darker(105)  # Darken slightly if light
        else:
            card_bg_darker = card_bg_darker.lighter(105)  # Lighten slightly if dark

        self.setStyleSheet(f"""
            #relatedProductItem {{
                background-color: {card_bg_darker.name()};
                border-radius: {get_size('border_radius_medium')}px;
                border: 1px solid {border_color};
            }}

            #relatedProductItem:hover {{
                border: 2px solid {highlight_color};
                background-color: {QColor(highlight_color).lighter(190).name()};
            }}

            #productIndicator {{
                color: {highlight_color};
                font-weight: bold;
            }}

            #relatedProductName {{
                color: {highlight_color};
                margin-bottom: 5px;
            }}

            #itemSeparator {{
                background-color: {border_color};
                height: 1px;
                margin: 0px;
            }}

            #relatedProductDetail {{
                color: {text_color};
                font-size: {get_font_size('small')}px;
            }}

            #relatedProductPrice {{
                color: {text_color};
                font-weight: bold;
                font-size: {get_font_size('medium')}px;
            }}

            #detailIcon {{
                font-size: {get_font_size('medium')}px;
            }}

            #selectRelatedButton {{
                background-color: {highlight_color};
                color: white;
                border: none;
                border-radius: {get_size('border_radius_small')}px;
                padding: 8px 15px;
                font-size: {get_font_size('medium')}px;
                font-weight: bold;
                min-height: 36px;
            }}

            #selectRelatedButton:hover {{
                background-color: {QColor(highlight_color).lighter(110).name()};
                box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.2);
            }}

            #selectRelatedButton:pressed {{
                background-color: {QColor(highlight_color).darker(110).name()};
                box-shadow: 0px 1px 3px rgba(0, 0, 0, 0.2);
            }}
        """)

    def on_selected(self):
        """Emit signal when the product is selected with animation feedback."""
        # Create a quick "press" animation
        original_pos = self.pos()
        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(100)
        animation.setStartValue(original_pos)
        animation.setEndValue(original_pos + QPoint(0, 5))  # Move slightly down
        animation.setEasingCurve(QEasingCurve.OutQuad)

        # Create a return animation
        return_animation = QPropertyAnimation(self, b"pos")
        return_animation.setDuration(100)
        return_animation.setStartValue(original_pos + QPoint(0, 5))
        return_animation.setEndValue(original_pos)
        return_animation.setEasingCurve(QEasingCurve.OutBounce)

        # Connect animations in sequence
        animation.finished.connect(return_animation.start)

        # When return is done, emit the signal
        return_animation.finished.connect(lambda: self.selected.emit(self.product_data))

        # Start the animation sequence
        animation.start()

    def eventFilter(self, obj, event):
        """Handle mouse events for hover effects."""
        if obj is self:
            if event.type() == QEvent.Enter:
                self._hovered = True
                self.raise_()  # Bring to front on hover

                # Slightly lift the card on hover
                shadow = self.graphicsEffect()
                if shadow:
                    # Increase blur radius and offset
                    shadow.setBlurRadius(15)
                    shadow.setOffset(0, 6)

                return True

            elif event.type() == QEvent.Leave:
                self._hovered = False

                # Reset shadow when not hovered
                shadow = self.graphicsEffect()
                if shadow:
                    # Reset blur radius and offset
                    shadow.setBlurRadius(10)
                    shadow.setOffset(0, 4)

                return True

        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.LeftButton:
            # Visual feedback - darken background
            current_style = self.styleSheet()
            self.setStyleSheet(current_style + f"""
                #relatedProductItem {{
                    background-color: {QColor(get_color('highlight')).lighter(170).name()};
                }}
            """)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release event."""
        if event.button() == Qt.LeftButton:
            # Reset styling
            self.apply_styling()

            # Only emit signal if released inside the widget
            if self.rect().contains(event.pos()):
                self.on_selected()
        super().mouseReleaseEvent(event)

class ProductDetailCard(QFrame):
    """A card that displays product details with quantity selection."""

    def __init__(self, product_data, parent=None, translator=None):
        super().__init__(parent)
        self.product_data = product_data
        self.translator = translator
        self.setup_ui()

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the card UI."""
        self.setObjectName("productCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setMinimumHeight(200)

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Product name header
        name = self.product_data.get('product_name', 'Unknown Product')
        self.name_label = QLabel(name)
        self.name_label.setObjectName("productName")
        font = self.name_label.font()
        font.setPointSize(get_font_size("xlarge"))
        font.setBold(True)
        self.name_label.setFont(font)
        layout.addWidget(self.name_label)

        # Details layout with 2 columns
        details_layout = QGridLayout()
        details_layout.setHorizontalSpacing(25)
        details_layout.setVerticalSpacing(12)

        # Get product details with fallbacks
        parcode = self.product_data.get('parcode', 'N/A')
        category = self.product_data.get('category', 'N/A')
        price = self.product_data.get('price', 0.0)
        stock = self.product_data.get('quantity', 0)
        manufacturer = self.product_data.get('manufacturer', 'N/A')
        is_original = "Yes" if self.product_data.get('original', False) else "No"

        # Format price with 2 decimal places
        formatted_price = f"${price:.2f}" if price is not None else "N/A"

        # Create detail labels
        details = [
            (self._translate("id", "ID"), f"{parcode}"),
            (self._translate("category", "Category"), category),
            (self._translate("price", "Price"), formatted_price),
            (self._translate("quantity", "In Stock"), f"{stock}"),
            (self._translate("manufacturer", "Manufacturer"), manufacturer),
            (self._translate("original_part", "Original Part"), is_original)
        ]

        # Add compatible brands/models if available
        brands = self.product_data.get('compatible_brands', '')
        if brands:
            details.append((self._translate("compatible_brands", "Compatible Brands"), brands))

        models = self.product_data.get('compatible_models', '')
        if models:
            details.append((self._translate("compatible_models", "Compatible Models"), models))

        years = self.product_data.get('model_years', '')
        if years:
            details.append((self._translate("model_years", "Model Years"), years))

        # Add all details to grid
        for row, (label_text, value_text) in enumerate(details):
            # Create label
            label = QLabel(f"{label_text}:")
            label.setObjectName("detailLabel")
            font = label.font()
            font.setPointSize(get_font_size("medium"))
            font.setBold(True)
            label.setFont(font)

            # Create value
            value = QLabel(value_text)
            value.setObjectName("detailValue")
            value.setWordWrap(True)
            value_font = value.font()
            value_font.setPointSize(get_font_size("medium"))
            value.setFont(value_font)

            # Add to layout
            details_layout.addWidget(label, row, 0)
            details_layout.addWidget(value, row, 1)

        layout.addLayout(details_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("detailSeparator")
        layout.addWidget(separator)

        # Bottom section with quantity selector
        bottom_layout = QHBoxLayout()

        # Quantity label
        qty_label = QLabel(self._translate("select_quantity", "Quantity:"))
        qty_label.setObjectName("quantityLabel")
        font = qty_label.font()
        font.setPointSize(get_font_size("large"))
        font.setBold(True)
        qty_label.setFont(font)

        # Quantity selector
        max_qty = max(1, int(stock)) if stock is not None else 999
        self.quantity_selector = QuantitySelector(initial_value=1, min_value=1, max_value=max_qty)

        # Add to bottom layout
        bottom_layout.addWidget(qty_label)
        bottom_layout.addWidget(self.quantity_selector)
        bottom_layout.addStretch(1)

        layout.addLayout(bottom_layout)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply styling to the card."""
        self.setStyleSheet(f"""
            #productCard {{
                background-color: {get_color('card_bg')};
                border-radius: {get_size('border_radius_medium')}px;
                border: 1px solid {get_color('border')};
            }}
            
            #productName {{
                color: {get_color('highlight')};
                margin-bottom: 10px;
            }}
            
            #detailLabel {{
                color: {get_color('text')};
            }}
            
            #detailValue {{
                color: {get_color('text')};
            }}
            
            #detailSeparator {{
                color: {get_color('border')};
                background-color: {get_color('border')};
                height: 1px;
                margin: 5px 0;
            }}
            
            #quantityLabel {{
                color: {get_color('highlight')};
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


class SearchBox(QWidget):
    """Advanced search box with barcode scanner integration and autocomplete."""

    search_submitted = pyqtSignal(str)
    barcode_scanned = pyqtSignal(str)

    def __init__(self, parent=None, translator=None, suggestions=None):
        super().__init__(parent)
        self.translator = translator
        self.suggestions = suggestions or []
        self.setup_ui()

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the search box UI."""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

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

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText(self._translate(
            "search_placeholder", "Search by name, ID, category...")
        )
        self.search_input.setMinimumHeight(45)

        # Set up completer for suggestions
        self.completer = QCompleter(self.suggestions)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.search_input.setCompleter(self.completer)

        # Connect signals
        self.search_input.returnPressed.connect(self.submit_search)

        # Barcode scanner button
        self.barcode_btn = BarcodeScannerButton(parent=self, translator=self.translator)
        self.barcode_btn.barcode_scanned.connect(self.on_barcode_scanned)

        # Search button
        self.search_btn = QPushButton(self._translate("search_button", "Search"))
        self.search_btn.setObjectName("searchButton")
        self.search_btn.setMinimumHeight(45)
        self.search_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.search_btn.clicked.connect(self.submit_search)

        # Add widgets to layout
        layout.addWidget(search_icon_label)
        layout.addWidget(self.search_input, 1)  # Search input takes most space
        layout.addWidget(self.barcode_btn)
        layout.addWidget(self.search_btn)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply styling to the search box."""
        self.setStyleSheet(f"""
            #searchIcon {{
                color: {get_color('secondary_text')};
            }}
            
            #searchInput {{
                background-color: {get_color('input_bg')};
                color: {get_color('text')};
                border: 1px solid {get_color('border')};
                border-radius: {get_size('border_radius_medium')}px;
                padding: 10px 15px;
                font-size: {get_font_size('medium')}px;
            }}
            
            #searchInput:focus {{
                border: 2px solid {get_color('highlight')};
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
                background-color: {QColor(get_color('highlight')).lighter(110).name()};
            }}
            
            #searchButton:pressed {{
                background-color: {QColor(get_color('highlight')).darker(110).name()};
            }}
        """)

    def submit_search(self):
        """Submit the search query."""
        query = self.search_input.text().strip()
        if query:
            self.search_submitted.emit(query)

    def on_barcode_scanned(self, barcode, barcode_format=None):
        """Handle barcode scan."""
        if barcode:
            self.search_input.setText(barcode)
            self.barcode_scanned.emit(barcode)
            # Also trigger a search
            self.search_submitted.emit(barcode)

    def update_suggestions(self, suggestions):
        """Update the autocomplete suggestions."""
        self.suggestions = suggestions
        self.completer.setModel(None)
        self.completer = QCompleter(self.suggestions)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.search_input.setCompleter(self.completer)

    def clear(self):
        """Clear the search input."""
        self.search_input.clear()


class ActionButton(QPushButton):
    """Stylized action button for the register widget."""

    def __init__(self, text, icon_path=None, action_type=None, parent=None):
        super().__init__(text, parent)
        self.action_type = action_type  # 'sell' or 'receive'

        # Set icon if provided
        if icon_path:
            try:
                self.setIcon(QIcon(icon_path))
                self.setIconSize(QSize(28, 28))  # Larger icons
            except:
                pass  # Silently fail if icon can't be loaded

        # Set object name based on action type
        if action_type:
            self.setObjectName(f"{action_type}Button")

        # Set minimum size
        self.setMinimumHeight(54)  # Taller buttons
        self.setMinimumWidth(160)  # Wider buttons

        # Set cursor
        self.setCursor(QCursor(Qt.PointingHandCursor))

        # Set font
        font = self.font()
        font.setPointSize(get_font_size("large"))
        font.setBold(True)
        self.setFont(font)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply styling based on action type."""
        if self.action_type == 'sell':
            # Sell button styling (green)
            self.setStyleSheet(f"""
                #{self.action_type}Button {{
                    background-color: {get_color('success')};
                    color: white;
                    border-radius: {get_size('border_radius_medium')}px;
                    font-weight: bold;
                    padding: 10px 24px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                }}
                
                #{self.action_type}Button:hover {{
                    background-color: {QColor(get_color('success')).lighter(110).name()};
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                }}
                
                #{self.action_type}Button:pressed {{
                    background-color: {QColor(get_color('success')).darker(110).name()};
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
                }}
                
                #{self.action_type}Button:disabled {{
                    background-color: #808080;
                    color: #D0D0D0;
                    box-shadow: none;
                }}
            """)
        elif self.action_type == 'receive':
            # Receive button styling (blue)
            self.setStyleSheet(f"""
                #{self.action_type}Button {{
                    background-color: {get_color('highlight')};
                    color: white;
                    border-radius: {get_size('border_radius_medium')}px;
                    font-weight: bold;
                    padding: 10px 24px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                }}
                
                #{self.action_type}Button:hover {{
                    background-color: {QColor(get_color('highlight')).lighter(110).name()};
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                }}
                
                #{self.action_type}Button:pressed {{
                    background-color: {QColor(get_color('highlight')).darker(110).name()};
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
                }}
                
                #{self.action_type}Button:disabled {{
                    background-color: #808080;
                    color: #D0D0D0;
                    box-shadow: none;
                }}
            """)
        else:
            # Default styling
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {get_color('button')};
                    color: {get_color('text')};
                    border-radius: {get_size('border_radius_medium')}px;
                    font-weight: bold;
                    padding: 10px 24px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                }}
                
                QPushButton:hover {{
                    background-color: {get_color('button_hover')};
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
                }}
                
                QPushButton:pressed {{
                    background-color: {get_color('button_pressed')};
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
                }}
                
                QPushButton:disabled {{
                    background-color: #808080;
                    color: #D0D0D0;
                    box-shadow: none;
                }}
            """)


class EmptyStateWidget(QWidget):
    """Widget to display when no product is selected."""

    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator
        self.setup_ui()

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the empty state UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 50, 20, 50)
        layout.setSpacing(30)
        layout.setAlignment(Qt.AlignCenter)

        # Add search icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setObjectName("emptyStateIcon")

        # Try to load search icon
        try:
            icon_path = "resources/search_big_icon.png"
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(pixmap)
            else:
                icon_label.setText("🔍")
                font = icon_label.font()
                font.setPointSize(60)
                icon_label.setFont(font)
        except:
            icon_label.setText("🔍")
            font = icon_label.font()
            font.setPointSize(60)
            icon_label.setFont(font)

        layout.addWidget(icon_label)

        # Add message
        message_label = QLabel(self._translate(
            "search_product_prompt",
            "Search for a product using the search bar or scan a barcode"
        ))
        message_label.setObjectName("emptyStateMessage")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setWordWrap(True)
        font = message_label.font()
        font.setPointSize(get_font_size("xlarge"))
        message_label.setFont(font)

        layout.addWidget(message_label)

        # Add subtitle with additional instructions
        subtitle_label = QLabel(self._translate(
            "empty_state_subtitle",
            "You can search by product name, ID, or category"
        ))
        subtitle_label.setObjectName("emptyStateSubtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)

        layout.addWidget(subtitle_label)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply styling to the empty state."""
        self.setStyleSheet(f"""
            #emptyStateIcon {{
                color: {QColor(get_color('secondary_text')).lighter(130).name()};
            }}
            
            #emptyStateMessage {{
                color: {get_color('secondary_text')};
                margin-bottom: 10px;
            }}
            
            #emptyStateSubtitle {{
                color: {QColor(get_color('secondary_text')).lighter(130).name()};
                font-size: {get_font_size('medium')}px;
                margin-top: -10px;
            }}
        """)


class RelatedProductsSection(QWidget):
    """Section that displays related products."""

    product_selected = pyqtSignal(dict)
    add_related_clicked = pyqtSignal()

    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator
        self.products = []
        self.setup_ui()

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the related products section UI."""
        self.setObjectName("relatedProductsSection")

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # Header with title and add button
        header_layout = QHBoxLayout()

        # Title
        self.title_label = QLabel(self._translate("related_products", "Related Products"))
        self.title_label.setObjectName("relatedProductsTitle")
        font = self.title_label.font()
        font.setPointSize(get_font_size("large"))
        font.setBold(True)
        self.title_label.setFont(font)

        # Add related product button
        self.add_button = QPushButton(self._translate("add_related", "Add Related"))
        self.add_button.setObjectName("addRelatedButton")
        self.add_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_button.clicked.connect(self.add_related_clicked.emit)

        # Add to header layout
        header_layout.addWidget(self.title_label)
        header_layout.addStretch(1)
        header_layout.addWidget(self.add_button)

        layout.addLayout(header_layout)

        # Products scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("relatedProductsScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        # Scroll content
        self.scroll_content = QWidget()
        self.scroll_layout = QHBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setAlignment(Qt.AlignLeft)

        # Empty state label
        self.empty_label = QLabel(self._translate("no_related_products", "No related products found"))
        self.empty_label.setObjectName("noRelatedLabel")
        self.empty_label.setAlignment(Qt.AlignCenter)

        # Initially add empty label
        self.scroll_layout.addWidget(self.empty_label)

        # Set scroll widget
        self.scroll_area.setWidget(self.scroll_content)

        # Add to main layout
        layout.addWidget(self.scroll_area)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply styling to the related products section."""
        self.setStyleSheet(f"""
            #relatedProductsSection {{
                background-color: {get_color('card_bg')};
                border-radius: {get_size('border_radius_medium')}px;
                border: 1px solid {get_color('border')};
            }}
            
            #relatedProductsTitle {{
                color: {get_color('highlight')};
            }}
            
            #addRelatedButton {{
                background-color: transparent;
                color: {get_color('highlight')};
                border: 1px solid {get_color('highlight')};
                border-radius: {get_size('border_radius_small')}px;
                padding: 5px 10px;
                font-weight: bold;
            }}
            
            #addRelatedButton:hover {{
                background-color: {get_color('highlight')};
                color: {get_color('highlight_text', '#FFFFFF')};
            }}
            
            #noRelatedLabel {{
                color: {get_color('secondary_text')};
                font-style: italic;
                padding: 20px;
            }}
            
            #relatedProductsScroll {{
                background-color: transparent;
                border: none;
            }}
        """)

    def set_products(self, products):
        """Set the related products to display."""
        self.products = products

        # Clear existing content
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add products or empty state
        if not products:
            self.empty_label = QLabel(self._translate("no_related_products", "No related products found"))
            self.empty_label.setObjectName("noRelatedLabel")
            self.empty_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(self.empty_label)
        else:
            for product in products:
                product_item = RelatedProductItem(product, translator=self.translator)
                product_item.selected.connect(self.on_product_selected)
                self.scroll_layout.addWidget(product_item)

            # Add stretch at the end
            self.scroll_layout.addStretch(1)

    def on_product_selected(self, product_data):
        """Handle when a related product is selected."""
        self.product_selected.emit(product_data)


class RegisterWidget(QWidget, SizePolicyMixin):
    """
    Modern register widget that allows searching for products,
    displaying their details, and processing sales or receiving inventory.
    """

    transaction_completed = pyqtSignal(dict)  # Emitted when a transaction is completed

    def __init__(self, translator=None, db=None, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.db = db

        # Product suggestions for search
        self.product_suggestions = []

        # Current product data
        self.current_product = None

        # Set up UI
        self.setup_ui()

        # Load product suggestions
        self.load_product_suggestions()

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the register widget UI."""
        # Set expanding policy for the widget
        self.set_expanding_policy()

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Add title
        title_label = QLabel(self._translate("register_title", "Register"))
        title_label.setObjectName("registerTitle")
        font = title_label.font()
        font.setPointSize(get_font_size("xxlarge"))
        font.setBold(True)
        title_label.setFont(font)

        main_layout.addWidget(title_label)

        # Search section
        search_container = QFrame()
        search_container.setObjectName("searchContainer")
        search_layout = QVBoxLayout(search_container)
        search_layout.setContentsMargins(20, 20, 20, 20)

        # Create search box
        self.search_box = SearchBox(translator=self.translator)
        self.search_box.search_submitted.connect(self.search_product)
        self.search_box.barcode_scanned.connect(self.search_product)

        search_layout.addWidget(self.search_box)
        main_layout.addWidget(search_container)

        # Create content stack
        self.content_stack = QStackedWidget()
        self.content_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Empty state
        self.empty_state = EmptyStateWidget(translator=self.translator)
        self.content_stack.addWidget(self.empty_state)

        # Product detail container (will be created when a product is found)
        self.product_container = QScrollArea()
        self.product_container.setObjectName("productContainer")
        self.product_container.setWidgetResizable(True)
        self.product_container.setFrameShape(QFrame.NoFrame)

        # Product content widget
        self.product_content = QWidget()
        self.product_layout = QVBoxLayout(self.product_content)
        self.product_layout.setContentsMargins(0, 0, 0, 0)
        self.product_layout.setSpacing(20)

        self.product_container.setWidget(self.product_content)
        self.content_stack.addWidget(self.product_container)

        # Initially show empty state
        self.content_stack.setCurrentWidget(self.empty_state)

        main_layout.addWidget(self.content_stack, 1)  # Give content stack the most space

        # Action buttons container
        action_container = QFrame()
        action_container.setObjectName("actionContainer")
        action_layout = QHBoxLayout(action_container)
        action_layout.setContentsMargins(20, 20, 20, 20)
        action_layout.setSpacing(20)

        # Add spacer to push buttons to the right
        action_layout.addStretch(1)

        # Receive button
        self.receive_btn = ActionButton(
            self._translate("receive_button", "Receive Stock"),
            icon_path="resources/receive_icon.png",
            action_type="receive"
        )
        self.receive_btn.clicked.connect(self.handle_receive)

        # Sell button
        self.sell_btn = ActionButton(
            self._translate("sell_button", "Sell"),
            icon_path="resources/sell_icon.png",
            action_type="sell"
        )
        self.sell_btn.clicked.connect(self.handle_sell)

        # Add buttons
        action_layout.addWidget(self.receive_btn)
        action_layout.addWidget(self.sell_btn)

        # Disable buttons initially
        self.receive_btn.setEnabled(False)
        self.sell_btn.setEnabled(False)

        main_layout.addWidget(action_container)

        # Apply styling
        self.apply_theme()

    def apply_theme(self):
        """Apply theme styling to the widget."""
        self.setStyleSheet(f"""
            QWidget {{
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            
            #registerTitle {{
                color: {get_color('title')};
                margin-bottom: 10px;
            }}
            
            #searchContainer, #productContainer, #actionContainer {{
                background-color: {get_color('card_bg')};
                border-radius: {get_size('border_radius_large')}px;
                border: 1px solid {get_color('border')};
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }}
        """)

    def load_product_suggestions(self):
        """Load product suggestions for the search box."""
        if not self.db:
            return

        try:
            # Get all products
            products = self.db.get_all_parts()

            # Extract product names and IDs for suggestions
            suggestions = []

            for product in products:
                if isinstance(product, dict):
                    # Add product name
                    name = product.get('product_name')
                    if name and name not in suggestions:
                        suggestions.append(name)

                    # Add parcode
                    parcode = product.get('parcode')
                    if parcode and str(parcode) not in suggestions:
                        suggestions.append(str(parcode))

                    # Add category
                    category = product.get('category')
                    if category and category not in suggestions:
                        suggestions.append(category)

                    # Add manufacturer
                    manufacturer = product.get('manufacturer')
                    if manufacturer and manufacturer not in suggestions:
                        suggestions.append(manufacturer)

            # Update suggestions
            self.product_suggestions = suggestions
            self.search_box.update_suggestions(suggestions)

        except Exception as e:
            print(f"Error loading product suggestions: {e}")

    def search_product(self, query):
        """Search for a product by name, ID, or barcode."""
        if not self.db:
            self.show_error(self._translate(
                "error", "Error"),
                self._translate("db_connection_error", "Database connection is not available")
            )
            return

        try:
            # Try to search by parcode first (exact match)
            if query.isdigit():
                product = self.db.get_part(int(query))
                if product:
                    self.display_product(product)
                    return

            # Then try to search by name (exact match)
            product = self.db.get_part_by_name(query)
            if product:
                self.display_product(product)
                return

            # If not found, try fuzzy search
            products = self.db.search_parts(query)
            if products and len(products) > 0:
                # Display the first match
                self.display_product(products[0])

                # If multiple matches, show a message
                if len(products) > 1:
                    self.show_info(
                        self._translate("multiple_results", "Multiple Results"),
                        self._translate(
                            "multiple_results_msg",
                            f"Found {len(products)} products matching '{query}'. Showing the first match."
                        )
                    )
                return

            # If no product found
            self.show_warning(
                self._translate("no_results", "No Results"),
                self._translate(
                    "no_results_msg",
                    f"No products found matching '{query}'."
                )
            )

            # Reset to empty state
            self.content_stack.setCurrentWidget(self.empty_state)
            self.current_product = None
            self.receive_btn.setEnabled(False)
            self.sell_btn.setEnabled(False)

        except Exception as e:
            self.show_error(
                self._translate("search_error", "Search Error"),
                str(e)
            )

    def display_product(self, product):
        """Display a product in the detail view."""
        if not product:
            return

        # Store current product
        self.current_product = product

        # Clear existing product layout
        while self.product_layout.count():
            item = self.product_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create product detail card
        product_card = ProductDetailCard(product, translator=self.translator)
        self.product_layout.addWidget(product_card)

        # Find related products
        related_products = self.find_related_products(product)

        # Add related products section
        related_section = RelatedProductsSection(translator=self.translator)
        related_section.set_products(related_products)
        related_section.product_selected.connect(self.display_product)  # When a related product is selected
        related_section.add_related_clicked.connect(self.handle_add_related)
        self.product_layout.addWidget(related_section)

        # Show product container
        self.content_stack.setCurrentWidget(self.product_container)

        # Enable action buttons
        self.receive_btn.setEnabled(True)
        self.sell_btn.setEnabled(True)

        # Apply subtle animation for smooth transition
        fade_in = QPropertyAnimation(self.product_content, b"windowOpacity")
        fade_in.setDuration(150)
        fade_in.setStartValue(0.3)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.OutCubic)
        fade_in.start()

    def find_related_products(self, product):
        """Find related products based on category, compatible cars, and brand."""
        if not self.db or not product:
            return []

        try:
            # Get parameters to search for
            category = product.get('category')
            parcode = product.get('parcode')
            compatible_brands = product.get('compatible_brands', '')
            compatible_models = product.get('compatible_models', '')
            model_years = product.get('model_years', '')
            manufacturer = product.get('manufacturer', '')

            # Get all products
            all_products = self.db.get_all_parts()

            # Filter related products
            related = []

            for p in all_products:
                # Skip the current product itself
                if p.get('parcode') == parcode:
                    continue

                # Must be same category
                if p.get('category') != category:
                    continue

                # Must have at least one common compatible brand/model
                p_brands = p.get('compatible_brands', '')
                p_models = p.get('compatible_models', '')

                # Skip if no brand/model match
                has_common_brand = False
                has_common_model = False

                # Check for common brands
                if compatible_brands and p_brands:
                    brands1 = [b.strip() for b in compatible_brands.split(',')]
                    brands2 = [b.strip() for b in p_brands.split(',')]

                    # Check for any overlap
                    for b in brands1:
                        if b in brands2:
                            has_common_brand = True
                            break

                # Check for common models
                if compatible_models and p_models:
                    models1 = [m.strip() for m in compatible_models.split(',')]
                    models2 = [m.strip() for m in p_models.split(',')]

                    # Check for any overlap
                    for m in models1:
                        if m in models2:
                            has_common_model = True
                            break

                # Must have both a common brand and model, or none specified
                if not (has_common_brand or compatible_brands == '' or p_brands == '') or \
                   not (has_common_model or compatible_models == '' or p_models == ''):
                    continue

                # Add to related products
                related.append(p)

                # Limit to a reasonable number
                if len(related) >= 5:
                    break

            return related

        except Exception as e:
            print(f"Error finding related products: {e}")
            return []

    def handle_add_related(self):
        """Handle adding a related product."""
        # Open a dialog to add a related product
        # This would be implemented based on your application's design
        # For now, we'll just show a message
        self.show_info(
            self._translate("add_related", "Add Related Product"),
            self._translate("add_related_info", "To add a related product, please add a new product with similar attributes.")
        )

    def handle_sell(self):
        """Handle selling a product."""
        if not self.current_product or not self.db:
            return

        try:
            # Get product info from the detail card
            product_card = self.product_layout.itemAt(0).widget()
            if not isinstance(product_card, ProductDetailCard):
                return

            transaction_data = product_card.get_transaction_data()
            parcode = transaction_data['parcode']
            quantity = transaction_data['quantity']
            current_stock = self.current_product.get('quantity', 0)

            # Validate stock
            if quantity > current_stock:
                self.show_warning(
                    self._translate("insufficient_stock", "Insufficient Stock"),
                    self._translate(
                        "insufficient_stock_msg",
                        f"Not enough stock. Available: {current_stock}"
                    )
                )
                return

            # Confirm the sale
            confirm = self.show_confirmation(
                self._translate("confirm_sale", "Confirm Sale"),
                self._translate(
                    "confirm_sale_msg",
                    f"Sell {quantity} x {self.current_product.get('product_name')}?"
                ),
                self._translate("yes_sell", "Yes, Sell"),
                self._translate("cancel", "Cancel")
            )

            if not confirm:
                return

            # Update the stock in the database
            new_quantity = current_stock - quantity
            self.db.update_part(parcode, quantity=new_quantity)

            # Create transaction data
            transaction = {
                'type': 'sell',
                'product': self.current_product.get('product_name'),
                'parcode': parcode,
                'quantity': quantity,
                'price': self.current_product.get('price', 0.0) * quantity,
                'timestamp': f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
            }

            # Show success message
            self.show_success(
                self._translate("sale_complete", "Sale Complete"),
                self._translate(
                    "sale_complete_msg",
                    f"Sold {quantity} x {self.current_product.get('product_name')}"
                )
            )

            # Emit transaction completed signal
            self.transaction_completed.emit(transaction)

            # Reset UI
            self.search_box.clear()
            self.content_stack.setCurrentWidget(self.empty_state)
            self.current_product = None
            self.receive_btn.setEnabled(False)
            self.sell_btn.setEnabled(False)

            # Reload suggestions
            self.load_product_suggestions()

        except Exception as e:
            self.show_error(
                self._translate("sale_error", "Sale Error"),
                str(e)
            )

    def handle_receive(self):
        """Handle receiving new stock."""
        if not self.current_product or not self.db:
            return

        try:
            # Get product info from the detail card
            product_card = self.product_layout.itemAt(0).widget()
            if not isinstance(product_card, ProductDetailCard):
                return

            transaction_data = product_card.get_transaction_data()
            parcode = transaction_data['parcode']
            quantity = transaction_data['quantity']
            current_stock = self.current_product.get('quantity', 0)

            # Confirm receiving
            confirm = self.show_confirmation(
                self._translate("confirm_receive", "Confirm Receive"),
                self._translate(
                    "confirm_receive_msg",
                    f"Receive {quantity} x {self.current_product.get('product_name')}?"
                ),
                self._translate("yes_receive", "Yes, Receive"),
                self._translate("cancel", "Cancel")
            )

            if not confirm:
                return

            # Update the stock in the database
            new_quantity = current_stock + quantity
            self.db.update_part(parcode, quantity=new_quantity)

            # Create transaction data
            transaction = {
                'type': 'receive',
                'product': self.current_product.get('product_name'),
                'parcode': parcode,
                'quantity': quantity,
                'price': self.current_product.get('price', 0.0) * quantity,
                'timestamp': f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
            }

            # Show success message
            self.show_success(
                self._translate("receive_complete", "Stock Received"),
                self._translate(
                    "receive_complete_msg",
                    f"Added {quantity} x {self.current_product.get('product_name')} to inventory"
                )
            )

            # Emit transaction completed signal
            self.transaction_completed.emit(transaction)

            # Reset UI
            self.search_box.clear()
            self.content_stack.setCurrentWidget(self.empty_state)
            self.current_product = None
            self.receive_btn.setEnabled(False)
            self.sell_btn.setEnabled(False)

            # Reload suggestions
            self.load_product_suggestions()

        except Exception as e:
            self.show_error(
                self._translate("receive_error", "Receive Error"),
                str(e)
            )

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

    def update_translations(self):
        """Update all translations in the widget."""
        # This would update all text elements with new translations
        # Would be implemented as needed
        pass



