"""
Enhanced Register Widget for the Abu Mukh Car Parts Management System.
This widget provides a cleaner interface with improved styling and layout,
dual mode functionality (sell/supply), and a cart system.
"""
import datetime
from PyQt5.QtCore import (
    Qt, pyqtSignal, QSize, QTimer, QEvent, QPropertyAnimation,
    QEasingCurve, QParallelAnimationGroup, QPoint
)
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QFrame, QScrollArea, QGridLayout, QSpinBox, QMessageBox, QCompleter,
    QSizePolicy, QStackedWidget, QDialog, QGraphicsDropShadowEffect, QListWidget,
    QListWidgetItem, QScrollBar, QApplication, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette, QCursor

from widgets.products.components.barcode_scanner_button import BarcodeScannerButton
from themes import get_color, get_size, get_font_size
from size_policy import SizePolicyMixin, ResponsiveFontMixin

class EnhancedScrollBar(QScrollBar):
    """A custom scrollbar with enhanced styling."""

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.apply_styling()

    def apply_styling(self):
        """Apply enhanced styling to the scrollbar."""
        background_color = QColor(get_color('background'))
        self.setStyleSheet(f"""
            QScrollBar {{
                background: {background_color.darker(110).name()};
                border-radius: 6px;
                margin: 0px;
            }}
            
            QScrollBar:horizontal {{
                height: 12px;
            }}
            
            QScrollBar:vertical {{
                width: 12px;
            }}
            
            QScrollBar::handle {{
                background: {get_color('border')};
                border-radius: 6px;
                min-height: 30px;
                min-width: 30px;
            }}
            
            QScrollBar::handle:hover {{
                background: {get_color('highlight')};
            }}
            
            QScrollBar::add-line, QScrollBar::sub-line {{
                width: 0px;
                height: 0px;
            }}
            
            QScrollBar::add-page, QScrollBar::sub-page {{
                background: none;
            }}
        """)


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
        highlight_color_lighter = QColor(highlight_color).lighter(110).name()
        highlight_color_darker = QColor(highlight_color).darker(110).name()
        error_color = get_color('error')
        error_color_lighter = QColor(error_color).lighter(110).name()
        error_color_darker = QColor(error_color).darker(110).name()
        success_color = get_color('success')
        success_color_lighter = QColor(success_color).lighter(110).name()
        success_color_darker = QColor(success_color).darker(110).name()

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
                background-color: {highlight_color_lighter};
            }}
            
            QPushButton#primaryButton:pressed {{
                background-color: {highlight_color_darker};
            }}
            
            QPushButton#dangerButton {{
                background-color: {error_color};
                color: white;
            }}
            
            QPushButton#dangerButton:hover {{
                background-color: {error_color_lighter};
            }}
            
            QPushButton#dangerButton:pressed {{
                background-color: {error_color_darker};
            }}
            
            QPushButton#successButton {{
                background-color: {success_color};
                color: white;
            }}
            
            QPushButton#successButton:hover {{
                background-color: {success_color_lighter};
            }}
            
            QPushButton#successButton:pressed {{
                background-color: {success_color_darker};
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


class QuantitySelector(QWidget):
    """A custom quantity selector with +/- buttons and a spinbox that's aware of transaction mode."""

    quantity_changed = pyqtSignal(int)

    def __init__(self, parent=None, initial_value=1, min_value=1, max_value=999, mode="view"):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self.mode = mode  # "view", "sell", or "supply"
        self.setup_ui(initial_value)

    def setup_ui(self, initial_value):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Minus button
        self.minus_btn = QPushButton("-")
        self.minus_btn.setFixedSize(36, 36)
        self.minus_btn.setObjectName("quantityButton")
        self.minus_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.minus_btn.clicked.connect(self.decrease_quantity)

        # Quantity spinbox
        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(self.min_value)
        self.spinbox.setMaximum(self.max_value)
        self.spinbox.setValue(initial_value)
        self.spinbox.setFixedHeight(36)
        self.spinbox.setMinimumWidth(60)
        self.spinbox.setAlignment(Qt.AlignCenter)
        self.spinbox.valueChanged.connect(self.on_quantity_changed)

        # Plus button
        self.plus_btn = QPushButton("+")
        self.plus_btn.setFixedSize(36, 36)
        self.plus_btn.setObjectName("quantityButton")
        self.plus_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.plus_btn.clicked.connect(self.increase_quantity)

        # Add widgets to layout
        layout.addWidget(self.minus_btn)
        layout.addWidget(self.spinbox)
        layout.addWidget(self.plus_btn)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply consistent styling to the quantity selector."""
        button_style = f"""
            QPushButton#quantityButton {{
                background-color: {get_color('button')};
                color: {get_color('text')};
                border-radius: 6px;
                font-weight: bold;
                font-size: 18px;
            }}
            
            QPushButton#quantityButton:hover {{
                background-color: {get_color('button_hover')};
            }}
            
            QPushButton#quantityButton:pressed {{
                background-color: {get_color('button_pressed')};
            }}
            
            QSpinBox {{
                background-color: {get_color('input_bg')};
                color: {get_color('text')};
                border: 1px solid {get_color('border')};
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 16px;
            }}
            
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0;
                height: 0;
                border: none;
            }}
        """
        self.setStyleSheet(button_style)

    def increase_quantity(self):
        """Increase the quantity by 1."""
        current = self.spinbox.value()
        self.spinbox.setValue(current + 1)

    def decrease_quantity(self):
        """Decrease the quantity by 1."""
        current = self.spinbox.value()
        if current > self.min_value:
            self.spinbox.setValue(current - 1)

    def on_quantity_changed(self, value):
        """Emit signal when quantity changes."""
        self.quantity_changed.emit(value)

    def get_quantity(self):
        """Get the current quantity value."""
        return self.spinbox.value()

    def set_quantity(self, value):
        """Set the quantity value."""
        self.spinbox.setValue(value)

    def set_mode(self, mode, current_stock=None):
        """Set the transaction mode and adjust limits accordingly.

        Args:
            mode (str): 'view', 'sell', or 'supply'
            current_stock (int, optional): Current stock level, used for 'sell' mode
        """
        self.mode = mode

        # Adjust limits based on mode
        if mode == "sell" and current_stock is not None:
            # In sell mode, can't sell more than current stock
            max_value = max(1, current_stock)
            self.spinbox.setMaximum(max_value)

            # If current value exceeds stock, adjust it
            if self.spinbox.value() > max_value:
                self.spinbox.setValue(max_value)

            # Apply sell mode styling
            self.setObjectName("sellModeSelector")

        elif mode == "supply":
            # In supply mode, can add large quantities
            self.spinbox.setMaximum(999)

            # Apply supply mode styling
            self.setObjectName("supplyModeSelector")

        else:  # "view" mode
            # In view mode, use the default max value
            self.spinbox.setMaximum(self.max_value)

            # Apply default styling
            self.setObjectName("viewModeSelector")

        # Apply mode-specific styling
        self.update_mode_styling()

    def update_mode_styling(self):
        """Apply visual styling based on current mode."""
        base_style = self.styleSheet()

        # Remove any previous mode styling
        base_style = base_style.replace("#sellModeSelector {", "#ignoreThis {")
        base_style = base_style.replace("#supplyModeSelector {", "#ignoreThis {")
        base_style = base_style.replace("#viewModeSelector {", "#ignoreThis {")

        # Add mode-specific styles
        error_color = QColor(get_color('error', '#F44336'))
        highlight_color = QColor(get_color('highlight', '#2196F3'))

        if self.mode == "sell":
            border_color = error_color
            extra_style = f"""
                #sellModeSelector QSpinBox {{
                    border: 2px solid {border_color.name()};
                }}
                
                #sellModeSelector QPushButton#quantityButton {{
                    border: 1px solid {border_color.name()};
                }}
            """
        elif self.mode == "supply":
            border_color = highlight_color
            extra_style = f"""
                #supplyModeSelector QSpinBox {{
                    border: 2px solid {border_color.name()};
                }}
                
                #supplyModeSelector QPushButton#quantityButton {{
                    border: 1px solid {border_color.name()};
                }}
            """
        else:  # view mode
            extra_style = ""

        # Apply the updated style
        self.setStyleSheet(base_style + extra_style)


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


class ProductDetailCard(QFrame):
    """A compact card that displays product details with improved styling and layout."""

    add_to_cart = pyqtSignal(dict, int)  # Product data, quantity

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
        """Set up the card UI with a sleek, modern styling and layout."""
        self.setObjectName("productCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.setMinimumHeight(140)  # Even more compact
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Create a container for the content with margins
        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("productCardContent")

        # Main layout for the overall widget with margins to create space around the card
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 16, 18, 16)
        main_layout.setSpacing(0)  # No spacing between the container and content

        # Layout for the actual content
        layout = QVBoxLayout(self.content_widget)
        layout.setContentsMargins(16, 14, 16, 14)  # Balanced internal margins
        layout.setSpacing(6)  # Tighter spacing for sleeker look

        # Add the content widget to the main layout
        main_layout.addWidget(self.content_widget)

        # Modern shadow effect with no dependency on borders
        shadow = QGraphicsDropShadowEffect(self.content_widget)
        shadow.setBlurRadius(25)  # Larger blur for softer edges
        shadow.setColor(QColor(0, 0, 0, 20))  # More subtle shadow
        shadow.setOffset(0, 3)  # Slight offset for depth
        self.content_widget.setGraphicsEffect(shadow)

        # Header layout with product name - more modern, clean look
        header_layout = QVBoxLayout()
        header_layout.setSpacing(2)
        header_layout.setContentsMargins(0, 0, 0, 2)  # Minimal margins

        # Product name with modern typography
        name = self.product_data.get('product_name', 'Unknown Product')
        self.name_label = QLabel(name)
        self.name_label.setObjectName("productName")
        self.name_label.setWordWrap(True)
        font = self.name_label.font()
        font.setPointSize(get_font_size("large"))
        font.setBold(True)
        self.name_label.setFont(font)

        header_layout.addWidget(self.name_label)
        layout.addLayout(header_layout)

        # No visible divider - more modern approach
        # Instead of a visible line, use spacing for separation
        layout.addSpacing(2)

        # Integrated layout with horizontal arrangement for better compactness
        main_content = QHBoxLayout()
        main_content.setSpacing(12)  # Slightly more spacing for breathing room

        # Details section with modern styling
        info_container = QFrame()
        info_container.setObjectName("infoContainer")
        info_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(12, 10, 12, 10)
        info_layout.setSpacing(6)  # Tighter spacing for sleek look

        # Details layout with 2 columns - more modern grid
        details_layout = QGridLayout()
        details_layout.setHorizontalSpacing(10)
        details_layout.setVerticalSpacing(4)  # Even tighter for sleek look

        # Get product details with fallbacks
        parcode = self.product_data.get('parcode', 'N/A')
        price = self.product_data.get('price', 0.0)
        stock = self.product_data.get('quantity', 0)
        manufacturer = self.product_data.get('manufacturer', 'N/A')

        # Format price with 2 decimal places
        formatted_price = f"${price:.2f}" if price is not None else "N/A"

        # Create detail labels with enhanced styling - only show the requested fields
        details = [
            (self._translate("parcode", "Parcode"), f"{parcode}"),
            (self._translate("manufacturer", "Manufacturer"), manufacturer),
            (self._translate("price", "Price"), formatted_price),
            (self._translate("quantity", "In Stock"), f"{stock}")
        ]

        # Add all details to grid with modern, sleek styling
        for row, (label_text, value_text) in enumerate(details):
            # Create label with modern typography
            label = QLabel(f"{label_text}")  # Removed colon for cleaner look
            label.setObjectName("detailLabel")
            font = label.font()
            font.setPointSize(get_font_size("small"))
            font.setBold(True)
            label.setFont(font)
            label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            # Create value with container for clean alignment
            value_container = QWidget()
            value_container.setObjectName("detailValueContainer")
            value_layout = QHBoxLayout(value_container)
            value_layout.setContentsMargins(0, 0, 0, 0)

            value = QLabel(value_text)
            value.setObjectName("detailValue")
            value.setWordWrap(True)
            value.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            value_font = value.font()
            value_font.setPointSize(get_font_size("small"))
            value.setFont(value_font)

            value_layout.addWidget(value, 1)
            value_layout.addStretch()

            # Add to layout with proper alignment
            details_layout.addWidget(label, row, 0, Qt.AlignLeft | Qt.AlignTop)
            details_layout.addWidget(value_container, row, 1, 1, 1)

        # Set column stretch to ensure proper alignment
        details_layout.setColumnStretch(0, 0)  # Labels don't stretch
        details_layout.setColumnStretch(1, 1)  # Values stretch

        info_layout.addLayout(details_layout)
        main_content.addWidget(info_container, 3)  # Give info section more space

        # Action section with sleek controls
        action_container = QFrame()
        action_container.setObjectName("actionContainer")
        action_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        action_layout = QVBoxLayout(action_container)
        action_layout.setContentsMargins(12, 10, 12, 10)
        action_layout.setSpacing(10)  # Slightly more spacing for modern look

        # Quantity label with cleaner styling
        qty_label = QLabel(self._translate("select_quantity", "Quantity"))  # Full word for cleaner look
        qty_label.setObjectName("quantityLabel")
        qty_label.setAlignment(Qt.AlignLeft)
        font = qty_label.font()
        font.setPointSize(get_font_size("small"))  # Smaller for cleaner look
        font.setBold(True)
        qty_label.setFont(font)
        action_layout.addWidget(qty_label)

        # Quantity selector with modern styling
        max_qty = max(1, int(stock)) if stock is not None else 999
        self.quantity_selector = QuantitySelector(initial_value=1, min_value=1, max_value=max_qty, mode="view")
        self.quantity_selector.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        action_layout.addWidget(self.quantity_selector)

        # Add some spacing
        action_layout.addSpacing(8)

        # Modern, sleek button
        self.add_cart_btn = QPushButton(self._translate("add_to_cart", "Add to Cart"))
        self.add_cart_btn.setObjectName("addToCartButton")
        self.add_cart_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_cart_btn.setMinimumHeight(36)  # Slightly taller for touch-friendly design
        self.add_cart_btn.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.add_cart_btn.clicked.connect(self.on_add_to_cart)
        action_layout.addWidget(self.add_cart_btn)

        # Add stretch to push elements to the top
        action_layout.addStretch(1)

        main_content.addWidget(action_container, 1)  # Give action container less space
        layout.addLayout(main_content)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply ultra-modern, sleek styling to the card."""
        # Create QColor objects
        highlight_color = QColor(get_color('highlight'))
        card_bg_color = QColor(get_color('card_bg'))
        text_color = QColor(get_color('text'))
        secondary_text = QColor(get_color('secondary_text'))

        # Modern palette adjustments
        card_bg_lighter = card_bg_color.lighter(103).name()

        self.setStyleSheet(f"""
            #productCard {{
                background-color: transparent;
                border: none;
            }}

            #productCardContent {{
                background-color: {get_color('card_bg')};
                border-radius: {int(get_size('border_radius_medium') * 1.2)}px;
                border: none; /* No visible border for ultra-modern look */
            }}

            #productName {{
                color: {get_color('highlight')};
                margin-bottom: 2px;
                font-size: {get_font_size("large")}px;
                letter-spacing: -0.2px;
            }}

            #infoContainer, #actionContainer {{
                background-color: {card_bg_lighter};
                border-radius: 8px;
                border: none;
            }}

            #detailLabel {{
                color: {secondary_text.lighter(110).name()};
                padding-right: 8px;
                min-width: 75px;
                font-size: {get_font_size("small")}px;
                letter-spacing: 0.2px;
            }}

            #detailValueContainer {{
                margin-right: 6px;
            }}

            #detailValue {{
                color: {text_color.darker(105).name()};
                font-weight: bold;
            }}

            #quantityLabel {{
                color: {secondary_text.lighter(105).name()};
                font-size: {get_font_size("small")}px;
                margin-bottom: 2px;
            }}

            #addToCartButton {{
                background-color: {get_color('highlight')};
                color: white;
                border-radius: {int(get_size('border_radius_small') * 1.5)}px;
                font-weight: bold;
                font-size: {get_font_size("small")}px;
                padding: 8px 15px;
                border: none;
            }}

            #addToCartButton:hover {{
                background-color: {highlight_color.lighter(110).name()};
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

    def set_mode(self, mode):
        """Set the mode (sell/supply) and update the UI accordingly with ultra-modern styling."""
        # Update the quantity selector mode
        current_stock = self.product_data.get('quantity', 0)
        self.quantity_selector.set_mode(mode, current_stock if mode == "sell" else None)

        # Create QColor objects for error and highlight
        error_color = QColor(get_color('error'))
        highlight_color = QColor(get_color('highlight'))
        card_bg_color = QColor(get_color('card_bg'))

        # Get theme-specific colors
        btn_color = error_color if mode == "sell" else highlight_color
        btn_hover = btn_color.lighter(110).name()

        # Ultra-modern: Instead of borders, use a subtle background tint
        if mode == "sell":
            # For sell mode: extremely subtle red tint
            tint_color = f"rgba({error_color.red()}, {error_color.green()}, {error_color.blue()}, 0.03)"
            glow_color = error_color
        else:
            # For supply mode: extremely subtle blue tint
            tint_color = f"rgba({highlight_color.red()}, {highlight_color.green()}, {highlight_color.blue()}, 0.03)"
            glow_color = highlight_color

        # Apply ultra-modern styling: no borders, just subtle effects
        self.content_widget.setStyleSheet(f"""
            background-color: {get_color('card_bg')};
            border-radius: {int(get_size('border_radius_medium') * 1.2)}px;
            border: none;
            background-image: radial-gradient(circle at center, {tint_color}, transparent 70%);
        """)

        # Update the shadow color to match the mode for an ultra-subtle glow effect
        shadow = QGraphicsDropShadowEffect(self.content_widget)
        shadow.setBlurRadius(25)
        shadow_color = QColor(glow_color.red(), glow_color.green(), glow_color.blue(),
                              15)  # Ultra-subtle colored shadow
        shadow.setColor(shadow_color)
        shadow.setOffset(0, 3)
        self.content_widget.setGraphicsEffect(shadow)

        # Update the add to cart button with flat modern styling
        if mode == "sell":
            self.add_cart_btn.setText(self._translate("add_to_cart", "Add to Cart"))
            self.add_cart_btn.setStyleSheet(f"""
                background-color: {error_color.name()};
                color: white;
                border-radius: {int(get_size('border_radius_small') * 1.5)}px;
                font-weight: bold;
                font-size: {get_font_size('small')}px;
                padding: 8px 15px;
                border: none;
            """)
            # Add hover style
            self.add_cart_btn.setStyleSheet(self.add_cart_btn.styleSheet() + f"""
                QPushButton#addToCartButton:hover {{
                    background-color: {error_color.lighter(110).name()};
                }}
            """)
        else:  # supply mode
            self.add_cart_btn.setText(self._translate("add_to_supply", "Add to Supply"))
            self.add_cart_btn.setStyleSheet(f"""
                background-color: {highlight_color.name()};
                color: white;
                border-radius: {int(get_size('border_radius_small') * 1.5)}px;
                font-weight: bold;
                font-size: {get_font_size('small')}px;
                padding: 8px 15px;
                border: none;
            """)
            # Add hover style
            self.add_cart_btn.setStyleSheet(self.add_cart_btn.styleSheet() + f"""
                QPushButton#addToCartButton:hover {{
                    background-color: {highlight_color.lighter(110).name()};
                }}
            """)


class RelatedProductItem(QFrame):
    """A clean, modern card that displays a related product with minimal styling."""

    selected = pyqtSignal(dict)
    quick_add_clicked = pyqtSignal(dict, int)  # product_data, quantity=1

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
        """Set up the related product item UI with clean, modern styling."""
        self.setObjectName("relatedProductItem")
        self.setFrameShape(QFrame.StyledPanel)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setMinimumHeight(180)  # Reasonable height
        self.setMinimumWidth(250)  # Reasonable width

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Product name
        name = self.product_data.get('product_name', 'Unknown Product')
        self.name_label = QLabel(name)
        self.name_label.setObjectName("relatedProductName")
        self.name_label.setWordWrap(True)
        font = self.name_label.font()
        font.setPointSize(get_font_size("medium"))
        font.setBold(True)
        self.name_label.setFont(font)
        layout.addWidget(self.name_label)

        # Simple separator
        separator = QFrame()
        separator.setObjectName("relatedProductSeparator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)

        # Details grid
        details_layout = QGridLayout()
        details_layout.setSpacing(8)
        details_layout.setContentsMargins(0, 0, 0, 0)

        # Get product details
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

        # Add details to grid
        for row, (label_text, value_text) in enumerate(details):
            label = QLabel(f"{label_text}:")
            label.setObjectName("relatedDetailLabel")

            value = QLabel(value_text)
            value.setObjectName("relatedDetailValue")
            value.setWordWrap(True)

            details_layout.addWidget(label, row, 0, Qt.AlignLeft)
            details_layout.addWidget(value, row, 1, Qt.AlignLeft)

        # Column stretch
        details_layout.setColumnStretch(0, 0)  # Labels don't stretch
        details_layout.setColumnStretch(1, 1)  # Values stretch

        layout.addLayout(details_layout)
        layout.addStretch(1)

        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        # View Details button
        self.details_button = QPushButton(self._translate("view_details", "View Details"))
        self.details_button.setObjectName("viewDetailsButton")
        self.details_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.details_button.clicked.connect(self.on_selected)

        # Quick Add button
        self.add_button = QPushButton(self._translate("quick_add", "Quick Add"))
        self.add_button.setObjectName("quickAddButton")
        self.add_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.add_button.clicked.connect(self.on_quick_add)

        buttons_layout.addWidget(self.details_button)
        buttons_layout.addWidget(self.add_button)
        layout.addLayout(buttons_layout)

        # Apply simple shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply clean, modern styling to the related product item."""
        highlight_color = QColor(get_color('highlight'))

        self.setStyleSheet(f"""
            #relatedProductItem {{
                background-color: {get_color('card_bg')};
                border-radius: {get_size('border_radius_medium')}px;
                border: 1px solid {get_color('border')};
            }}

            #relatedProductItem:hover {{
                border: 1px solid {highlight_color.name()};
                background-color: {QColor(get_color('card_bg')).lighter(105).name()};
            }}

            #relatedProductName {{
                color: {highlight_color.name()};
                font-weight: bold;
                margin-bottom: 5px;
            }}

            #relatedProductSeparator {{
                color: {get_color('border')};
                background-color: {get_color('border')};
                height: 1px;
                margin: 5px 0;
            }}

            #relatedDetailLabel {{
                color: {get_color('secondary_text')};
                font-size: {get_font_size('small')}px;
                padding-right: 10px;
                min-width: 80px;
            }}

            #relatedDetailValue {{
                color: {get_color('text')};
                font-size: {get_font_size('small')}px;
                font-weight: bold;
            }}

            #viewDetailsButton, #quickAddButton {{
                border-radius: {get_size('border_radius_small')}px;
                padding: 6px 12px;
                font-weight: bold;
                margin-top: 5px;
            }}

            #viewDetailsButton {{
                background-color: transparent;
                color: {highlight_color.name()};
                border: 1px solid {highlight_color.name()};
            }}

            #viewDetailsButton:hover {{
                background-color: {QColor(highlight_color).lighter(180).name()};
            }}

            #quickAddButton {{
                background-color: {highlight_color.name()};
                color: white;
                border: 1px solid {highlight_color.name()};
            }}

            #quickAddButton:hover {{
                background-color: {highlight_color.lighter(110).name()};
            }}
        """)

    def enterEvent(self, event):
        """Handle mouse enter to raise the shadow slightly."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave to restore normal shadow."""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 25))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        super().leaveEvent(event)

    def on_selected(self):
        """Emit signal when the product is selected."""
        self.selected.emit(self.product_data)

    def on_quick_add(self):
        """Emit signal to quickly add this product to the cart/list."""
        # Default quantity is 1
        self.quick_add_clicked.emit(self.product_data, 1)

    def mousePressEvent(self, event):
        """Handle mouse press event."""
        if event.button() == Qt.LeftButton:
            self.on_selected()
        super().mousePressEvent(event)


class RelatedProductsSection(QWidget):
    """A simplified, modern section that displays related products."""

    product_selected = pyqtSignal(dict)
    add_related_clicked = pyqtSignal()
    quick_add_product = pyqtSignal(dict, int)  # product_data, quantity

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
        """Set up the related products section UI with a sleek, modern design."""
        self.setObjectName("relatedProductsSection")
        self.setMinimumHeight(350)  # Increased height for visibility

        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header with title and add button
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

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

        # Simple separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("relatedProductsSeparator")
        layout.addWidget(separator)

        # Grid layout for products - simple but effective
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setSpacing(15)

        # Empty state label
        self.empty_label = QLabel(self._translate("no_related_products", "No related products found"))
        self.empty_label.setObjectName("noRelatedLabel")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(self.empty_label, 0, 0, 1, 2, Qt.AlignCenter)

        # Create a scroll area for the products
        scroll_area = QScrollArea()
        scroll_area.setObjectName("relatedProductsScroll")
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(self.grid_container)

        # Set custom scrollbar
        scroll_area.setVerticalScrollBar(EnhancedScrollBar(Qt.Vertical))

        layout.addWidget(scroll_area, 1)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply modern, clean styling to the related products section."""
        highlight_color = QColor(get_color('highlight'))
        card_bg_color = QColor(get_color('card_bg'))

        self.setStyleSheet(f"""
            #relatedProductsSection {{
                background-color: {QColor(card_bg_color).lighter(103).name()};
                border-radius: {get_size('border_radius_medium')}px;
                border: 1px solid {QColor(highlight_color).lighter(160).name()};
            }}

            #relatedProductsTitle {{
                color: {highlight_color.name()};
                font-size: {get_font_size("large")}px;
            }}

            #relatedProductsSeparator {{
                color: {QColor(highlight_color).lighter(170).name()};
                background-color: {QColor(highlight_color).lighter(170).name()};
                height: 1px;
            }}

            #addRelatedButton {{
                background-color: {highlight_color.name()};
                color: white;
                border-radius: {get_size('border_radius_small')}px;
                padding: 6px 12px;
                font-weight: bold;
            }}

            #addRelatedButton:hover {{
                background-color: {highlight_color.lighter(110).name()};
            }}

            #noRelatedLabel {{
                color: {get_color('secondary_text')};
                font-style: italic;
                padding: 30px;
                font-size: {get_font_size('medium')}px;
            }}
        """)

    def set_products(self, products):
        """Set the related products to display."""
        self.products = products

        # Clear existing items from the grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add products or empty state
        if not products or len(products) == 0:
            # Empty state
            self.empty_label = QLabel(self._translate("no_related_products", "No related products found"))
            self.empty_label.setObjectName("noRelatedLabel")
            self.empty_label.setAlignment(Qt.AlignCenter)
            self.grid_layout.addWidget(self.empty_label, 0, 0, 1, 2, Qt.AlignCenter)
        else:
            # Add products in a 2-column grid
            for i, product in enumerate(products):
                row = i // 2
                col = i % 2

                product_item = RelatedProductItem(product, translator=self.translator)
                product_item.selected.connect(self.on_product_selected)
                product_item.quick_add_clicked.connect(self.on_quick_add_product)

                self.grid_layout.addWidget(product_item, row, col)

            # Make sure the grid expands properly
            self.grid_layout.setRowStretch(len(products) // 2 + 1, 1)
            self.grid_layout.setColumnStretch(0, 1)
            self.grid_layout.setColumnStretch(1, 1)

    def on_product_selected(self, product_data):
        """Handle when a related product is selected."""
        self.product_selected.emit(product_data)

    def on_quick_add_product(self, product_data, quantity):
        """Handle when a product's quick add button is clicked."""
        self.quick_add_product.emit(product_data, quantity)


from PyQt5.QtCore import QSortFilterProxyModel, QStringListModel, Qt, QModelIndex


class PrioritizedCompleterModel(QSortFilterProxyModel):
    """A model that sorts completions by relevance."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.query = ""
        self.is_precise_mode = False

    def set_filter_text(self, text, is_precise=False):
        """Set the text to filter by and whether to use precise mode."""
        self.query = text.lower()
        self.is_precise_mode = is_precise
        self.invalidateFilter()
        self.sort(0, Qt.AscendingOrder)

    def lessThan(self, left, right):
        """Sort items by relevance."""
        left_text = self.sourceModel().data(left).lower()
        right_text = self.sourceModel().data(right).lower()

        # Calculate relevance scores
        left_score = self._calculate_score(left_text)
        right_score = self._calculate_score(right_text)

        # Higher score comes first
        if left_score != right_score:
            return left_score > right_score

        # If scores are equal, alphabetical order
        return left_text < right_text

    def _calculate_score(self, text):
        """Calculate a relevance score for sorting completions."""
        if not self.query:
            return 0

        text = text.lower()

        # Exact match is highest priority
        if text == self.query:
            return 100

        # Starts with query is next highest priority
        if text.startswith(self.query):
            return 90 - len(text)  # Shorter matches rank higher

        # Contains query as a whole word
        if f" {self.query} " in f" {text} ":
            return 80 - text.index(self.query)  # Earlier matches rank higher

        # Contains query anywhere
        if self.query in text:
            return 70 - text.index(self.query)

        # No match
        return 0

    def filterAcceptsRow(self, source_row, source_parent):
        """Determine if the row should be included in the results."""
        # Get the source data
        index = self.sourceModel().index(source_row, 0, source_parent)
        text = self.sourceModel().data(index).lower()

        # If no query, accept all
        if not self.query:
            return True

        # In precise mode, only accept items starting with the query
        if self.is_precise_mode:
            return text.startswith(self.query)

        # In smart mode, accept anything containing the query
        return self.query in text


class SearchBox(QWidget):
    """Advanced search box with barcode scanner integration, dual-mode suggestions,
    and enhanced styling for the suggestions dropdown."""

    search_submitted = pyqtSignal(str, bool)  # query, is_precise_search
    barcode_scanned = pyqtSignal(str)

    def __init__(self, parent=None, translator=None, suggestions=None):
        super().__init__(parent)
        self.translator = translator
        self.suggestions = suggestions or []
        self.is_precise_search = False  # Default to smart search
        self.setup_ui()
        self.style_completer_popup()

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
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

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText(self._translate(
            "search_placeholder", "Search by product name or ID...")
        )
        self.search_input.setMinimumHeight(45)

        # Set up completer for suggestions
        self.completer = QCompleter(self.suggestions)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)  # Default to smart mode
        self.completer.setMaxVisibleItems(10)  # Limit visible items for better appearance
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

        # Add widgets to search row
        search_row.addWidget(search_icon_label)
        search_row.addWidget(self.search_input, 1)  # Search input takes most space
        search_row.addWidget(self.barcode_btn)
        search_row.addWidget(self.search_btn)

        layout.addLayout(search_row)

        # Search mode toggle row
        mode_row = QHBoxLayout()
        mode_row.setContentsMargins(0, 0, 0, 0)
        mode_row.setSpacing(5)

        # Mode label
        mode_label = QLabel(self._translate("search_mode", "Search Mode:"))
        mode_label.setObjectName("searchModeLabel")

        # Smart search button
        self.smart_btn = QPushButton(self._translate("smart_search", "Smart"))
        self.smart_btn.setObjectName("smartSearchButton")
        self.smart_btn.setCheckable(True)
        self.smart_btn.setChecked(True)  # Default to smart search
        self.smart_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.smart_btn.clicked.connect(lambda: self.set_search_mode(False))

        # Precise search button
        self.precise_btn = QPushButton(self._translate("precise_search", "Precise"))
        self.precise_btn.setObjectName("preciseSearchButton")
        self.precise_btn.setCheckable(True)
        self.precise_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.precise_btn.clicked.connect(lambda: self.set_search_mode(True))

        # Search mode description
        self.mode_description = QLabel(self._translate(
            "smart_search_desc", "Finds products containing your search terms")
        )
        self.mode_description.setObjectName("searchModeDescription")

        # Add widgets to mode row
        mode_row.addWidget(mode_label)
        mode_row.addWidget(self.smart_btn)
        mode_row.addWidget(self.precise_btn)
        mode_row.addStretch(1)
        mode_row.addWidget(self.mode_description)

        layout.addLayout(mode_row)

        # Apply styling
        self.apply_styling()

        # Monitor for popup appearance to apply custom styling
        self.search_input.installEventFilter(self)

    def eventFilter(self, obj, event):
        """Event filter to catch when completer popup appears."""
        if obj == self.search_input and event.type() == QEvent.KeyPress:
            # When a key is pressed that might trigger the popup
            QTimer.singleShot(50, self.style_completer_popup)
        return super().eventFilter(obj, event)

    def style_completer_popup(self):
        """Apply elegant styling to the completer popup."""
        popup = self.completer.popup()
        if popup:
            # Set up scrollbar for the popup
            vertical_scrollbar = EnhancedScrollBar(Qt.Vertical, popup)
            popup.setVerticalScrollBar(vertical_scrollbar)

            # Make the popup slightly wider than the search box
            popup.setMinimumWidth(self.search_input.width() + 50)

            # Add shadow effect
            shadow = QGraphicsDropShadowEffect(popup)
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(0, 0, 0, 80))
            shadow.setOffset(0, 4)
            popup.setGraphicsEffect(shadow)

            # Get theme colors for styling
            bg_color = get_color('card_bg')
            border_color = get_color('border')
            highlight_color = get_color('highlight')
            text_color = get_color('text')
            hover_bg = QColor(highlight_color).lighter(170).name()

            # Create an elegant style for the popup
            popup.setStyleSheet(f"""
                QListView {{
                    background-color: {bg_color};
                    border: 1px solid {border_color};
                    border-radius: {get_size('border_radius_medium')}px;
                    padding: 8px 4px;
                    outline: none;
                    font-size: {get_font_size('medium')}px;
                    color: {text_color};
                }}

                QListView::item {{
                    padding: 10px 12px;
                    border-radius: {get_size('border_radius_small')}px;
                    margin: 2px 4px;
                }}

                QListView::item:hover {{
                    background-color: {hover_bg};
                }}

                QListView::item:selected {{
                    background-color: {highlight_color};
                    color: white;
                }}
            """)

    def apply_styling(self):
        """Apply styling to the search box."""
        highlight_color = QColor(get_color('highlight'))

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

            #smartSearchButton, #preciseSearchButton {{
                background-color: {get_color('button')};
                color: {get_color('text')};
                border: 1px solid {get_color('border')};
                border-radius: {get_size('border_radius_small')}px;
                padding: 5px 10px;
                font-size: {get_font_size('small')}px;
            }}

            #smartSearchButton:checked, #preciseSearchButton:checked {{
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

    def set_search_mode(self, is_precise):
        """Set the search mode and update completer behavior."""
        self.is_precise_search = is_precise

        # Update buttons
        self.smart_btn.setChecked(not is_precise)
        self.precise_btn.setChecked(is_precise)

        # Update description
        if is_precise:
            self.mode_description.setText(self._translate(
                "precise_search_desc", "Finds products matching your search exactly")
            )
            # Change completer behavior for precise mode
            self.completer.setFilterMode(Qt.MatchStartsWith)
        else:
            self.mode_description.setText(self._translate(
                "smart_search_desc", "Finds products containing your search terms")
            )
            # Change completer behavior for smart mode
            self.completer.setFilterMode(Qt.MatchContains)

        # Reapply the completer to trigger updating
        self.search_input.setCompleter(self.completer)

        # Re-style the popup
        QTimer.singleShot(50, self.style_completer_popup)

    def submit_search(self):
        """Submit the search query."""
        query = self.search_input.text().strip()
        if query:
            self.search_submitted.emit(query, self.is_precise_search)

    def on_barcode_scanned(self, barcode, barcode_format=None):
        """Handle barcode scan."""
        if barcode:
            self.search_input.setText(barcode)
            self.barcode_scanned.emit(barcode)
            # Also trigger a search (barcodes are always precise)
            self.search_submitted.emit(barcode, True)

    def update_suggestions(self, suggestions):
        """Update the autocomplete suggestions."""
        self.suggestions = suggestions

        # Create a new completer with the updated suggestions
        self.completer = QCompleter(self.suggestions)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setMaxVisibleItems(10)  # Limit visible items for better appearance

        # Keep the current filter mode
        if self.is_precise_search:
            self.completer.setFilterMode(Qt.MatchStartsWith)
        else:
            self.completer.setFilterMode(Qt.MatchContains)

        # Apply the new completer
        self.search_input.setCompleter(self.completer)

        # Make sure to apply styling
        QTimer.singleShot(50, self.style_completer_popup)

    def clear(self):
        """Clear the search input."""
        self.search_input.clear()


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
        secondary_text_color = QColor(get_color('secondary_text'))

        self.setStyleSheet(f"""
            #emptyStateIcon {{
                color: {secondary_text_color.lighter(130).name()};
            }}
            
            #emptyStateMessage {{
                color: {get_color('secondary_text')};
                margin-bottom: 10px;
            }}
            
            #emptyStateSubtitle {{
                color: {secondary_text_color.lighter(130).name()};
                font-size: {get_font_size('medium')}px;
                margin-top: -10px;
            }}
        """)


class RegisterWidget(QWidget, SizePolicyMixin):
    """
    Modern register widget that supports both selling and supply modes,
    with separate cart interfaces for each mode.
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

    # This is the focused modification of the RegisterWidget class
    # We're only changing the setup_ui and set_mode methods to implement separate cart panels

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

        # Create search box with enhanced functionality
        self.search_box = SearchBox(translator=self.translator)
        self.search_box.search_submitted.connect(self.search_product)
        self.search_box.barcode_scanned.connect(
            lambda barcode: self.search_product(barcode, True))  # Barcodes always use precise search

        search_layout.addWidget(self.search_box)
        left_layout.addWidget(search_container)

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

        # Set custom scrollbars
        self.product_container.setVerticalScrollBar(EnhancedScrollBar(Qt.Vertical))
        self.product_container.setHorizontalScrollBar(EnhancedScrollBar(Qt.Horizontal))

        # Product content widget
        self.product_content = QWidget()
        self.product_layout = QVBoxLayout(self.product_content)
        self.product_layout.setContentsMargins(0, 0, 0, 0)
        self.product_layout.setSpacing(20)

        self.product_container.setWidget(self.product_content)
        self.content_stack.addWidget(self.product_container)

        # Initially show empty state
        self.content_stack.setCurrentWidget(self.empty_state)

        left_layout.addWidget(self.content_stack, 1)  # Give content stack the most space

        # ======= RIGHT PANEL (CART AREA) =======
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

        # Apply styling
        self.apply_theme()

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

        # Update product card if visible
        if self.current_product and self.content_stack.currentWidget() == self.product_container:
            product_card = None
            for i in range(self.product_layout.count()):
                widget = self.product_layout.itemAt(i).widget()
                if isinstance(widget, ProductDetailCard):
                    product_card = widget
                    break

            if product_card:
                product_card.set_mode(mode)

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

    def process_cart(self, cart_data):
        """Process the cart (checkout or process supply)."""
        # Original implementation, but with improved cart clearing
        if not self.db:
            return

        items = cart_data.get('items', [])
        mode = cart_data.get('mode')

        if not items:
            return

        try:
            # Create transaction data for each item
            transactions = []

            for item in items:
                parcode = item.get('parcode')
                product_name = item.get('product_name', 'Unknown Product')
                price = item.get('price', 0.0)
                quantity = item.get('cart_quantity', 1)
                current_stock = item.get('quantity', 0)

                # Validate stock for sell mode
                if mode == "sell" and quantity > current_stock:
                    self.show_warning(
                        self._translate("insufficient_stock", "Insufficient Stock"),
                        self._translate(
                            "insufficient_stock_msg",
                            f"Not enough stock for {product_name}. Available: {current_stock}"
                        )
                    )
                    return

                # Update stock in database
                new_quantity = current_stock - quantity if mode == "sell" else current_stock + quantity
                self.db.update_part(parcode, quantity=new_quantity)

                # Create transaction record
                transaction = {
                    'type': 'sell' if mode == "sell" else 'receive',
                    'product': product_name,
                    'parcode': parcode,
                    'quantity': quantity,
                    'price': price * quantity,
                    'timestamp': f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S}"
                }

                transactions.append(transaction)

                # Emit transaction signal for each item
                self.transaction_completed.emit(transaction)

            # Show success message
            total_items = sum(item.get('cart_quantity', 1) for item in items)
            total_price = sum(item.get('price', 0.0) * item.get('cart_quantity', 1) for item in items)

            if mode == "sell":
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
            self.content_stack.setCurrentWidget(self.empty_state)
            self.current_product = None

            # Reload suggestions
            self.load_product_suggestions()

        except Exception as e:
            self.show_error(
                self._translate("process_error", "Processing Error"),
                str(e)
            )



    def load_product_suggestions(self):
        """Load comprehensive product suggestions for the search box."""
        # Same as original implementation
        if not self.db:
            return

        try:
            # Get all products
            products = self.db.get_all_parts()

            # Collect product data for suggestions
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

                    # Add manufacturer (helps with searching by brand)
                    manufacturer = product.get('manufacturer')
                    if manufacturer and manufacturer not in suggestions:
                        suggestions.append(manufacturer)

                    # Add car brands from compatible_brands
                    compatible_brands = product.get('compatible_brands')
                    if compatible_brands:
                        brands = [brand.strip() for brand in str(compatible_brands).split(',')]
                        for brand in brands:
                            if brand and brand not in suggestions:
                                suggestions.append(brand)

            # Update suggestions
            self.product_suggestions = suggestions
            self.search_box.update_suggestions(suggestions)

        except Exception as e:
            print(f"Error loading product suggestions: {e}")

    def create_cart_transition_animation(self, old_mode, new_mode):
        """Create a smooth transition animation between cart widgets."""
        # Get the source and target widgets
        source = self.sell_cart_widget if old_mode == "sell" else self.supply_cart_widget
        target = self.sell_cart_widget if new_mode == "sell" else self.supply_cart_widget

        # Define the direction (left to right or right to left)
        direction = 1 if old_mode == "sell" and new_mode == "supply" else -1

        # Transfer cart items if needed
        if hasattr(self, 'preserve_cart_items') and self.preserve_cart_items:
            # Copy cart items from source to target
            target.cart_items = source.cart_items.copy()
            target._update_cart_display()

        # Set up fade-out and slide animations for the old widget
        fade_out = QPropertyAnimation(source, b"windowOpacity")
        fade_out.setDuration(200)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.OutQuad)

        # When fade-out completes, switch widgets and fade in
        fade_out.finished.connect(lambda: self.cart_stack.setCurrentWidget(target))
        fade_out.finished.connect(lambda: self.start_fade_in(target))

        # Start the animation
        fade_out.start()

    def start_fade_in(self, widget):
        """Start fade-in animation for a cart widget."""
        # Set initial opacity
        widget.setWindowOpacity(0.0)

        # Create and start the fade-in animation
        fade_in = QPropertyAnimation(widget, b"windowOpacity")
        fade_in.setDuration(200)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InQuad)
        fade_in.start()


    def search_product(self, query, is_precise_search=False):
        """Search for a product with properly functioning smart search."""
        # Same as original implementation
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

            # PRECISE SEARCH MODE
            if is_precise_search:
                # First try parcode (exact match)
                if query.isdigit():
                    product = self.db.get_part(int(query))
                    if product:
                        self.display_product(product)
                        return

                # Then try exact name match
                product = self.db.get_part_by_name(query)
                if product:
                    self.display_product(product)
                    return

                # If no exact match found, show message
                self.show_warning(
                    self._translate("no_results", "No Results"),
                    self._translate(
                        "no_precise_results_msg",
                        f"No products exactly matching '{query}'. Try smart search for partial matches."
                    )
                )

                # Reset to empty state
                self.content_stack.setCurrentWidget(self.empty_state)
                self.current_product = None
                return

            # SMART SEARCH MODE
            else:
                # For numerical queries, try parcode first (exact match)
                if query.isdigit():
                    product = self.db.get_part(int(query))
                    if product:
                        self.display_product(product)
                        return

                # Use the database's built-in search functionality
                # This already handles partial matching across all text columns
                products = self.db.search_parts(query)

                if products and len(products) > 0:
                    # Display the first match
                    self.display_product(products[0])
                    return

                # No matches found
                self.show_warning(
                    self._translate("no_results", "No Results"),
                    self._translate(
                        "no_smart_results_msg",
                        f"No products found containing '{query}'."
                    )
                )

                # Reset to empty state
                self.content_stack.setCurrentWidget(self.empty_state)
                self.current_product = None

        except Exception as e:
            self.show_error(
                self._translate("search_error", "Search Error"),
                str(e)
            )

    def display_product(self, product):
        """Display a product in the detail view with enhanced styling."""
        if not product:
            return

        # Store current product
        self.current_product = product

        # Clear existing product layout
        while self.product_layout.count():
            item = self.product_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create product detail card with current mode
        product_card = ProductDetailCard(product, translator=self.translator)
        product_card.set_mode(self.current_mode)
        product_card.add_to_cart.connect(self.add_to_cart)

        # Find related products
        related_products = self.find_related_products(product)

        # Add related products section with quick add support
        related_section = RelatedProductsSection(translator=self.translator)
        related_section.product_selected.connect(self.display_product)
        related_section.add_related_clicked.connect(self.handle_add_related)
        related_section.quick_add_product.connect(self.add_to_cart)  # Connect quick add signal
        related_section.set_products(related_products)

        # Show the product container
        self.content_stack.setCurrentWidget(self.product_container)

        # Add widgets to layout
        self.product_layout.addWidget(product_card)
        self.product_layout.addWidget(related_section)

    def find_related_products(self, product):
        """Find related products based on category, compatible cars, and brand."""
        # Same as original implementation
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
        # Same as original implementation
        self.show_info(
            self._translate("add_related", "Add Related Product"),
            self._translate("add_related_info",
                            "To add a related product, please add a new product with similar attributes.")
        )

    def apply_theme(self):
        """Apply theme styling to the widget with enhanced colors."""
        # Same as original implementation with added cart stack styling
        background_color = QColor(get_color('background'))
        highlight_color = QColor(get_color('highlight'))
        error_color = QColor(get_color('error'))

        self.setStyleSheet(f"""
            #leftPanel, #rightPanel {{
                background-color: transparent;
            }}

            #registerTitle {{
                color: {get_color('title')};
                margin-bottom: 10px;
            }}

            #modeToggleContainer {{
                background-color: {get_color('card_bg')};
                border-radius: {get_size('border_radius_medium')}px;
                border: 1px solid {get_color('border')};
            }}

            #sellModeButton, #supplyModeButton {{
                background-color: transparent;
                color: {get_color('text')};
                border: none;
                border-radius: {get_size('border_radius_medium')}px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 100px;
            }}

            #sellModeButton:checked {{
                background-color: {get_color('error')};
                color: white;
            }}

            #supplyModeButton:checked {{
                background-color: {get_color('highlight')};
                color: white;
            }}

            #searchContainer, #productContainer {{
                background-color: {get_color('card_bg')};
                border-radius: {get_size('border_radius_large')}px;
                border: 2px solid {get_color('border')};
            }}

            #cartStack {{
                background-color: transparent;
            }}

            /* Custom scrollbar styling */
            QScrollBar:vertical {{
                background: {background_color.darker(110).name()};
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical {{
                background: {get_color('border')};
                min-height: 30px;
                border-radius: 6px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {get_color('highlight')};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                background: {background_color.darker(110).name()};
                height: 12px;
                margin: 0px;
                border-radius: 6px;
            }}

            QScrollBar::handle:horizontal {{
                background: {get_color('border')};
                min-width: 30px;
                border-radius: 6px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background: {get_color('highlight')};
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}
        """)

    # Dialog methods (same as original)
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

