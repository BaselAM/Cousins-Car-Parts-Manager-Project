"""
Product card component for displaying product details in an elegant card format.
"""

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                             QToolButton, QWidget, QGraphicsDropShadowEffect, QPushButton)
from PyQt5.QtGui import QFont, QColor
# Try to import theme and logger modules - handle gracefully if not available
try:
    from themes import get_color, get_size, get_font_size
    from themes.core import _current_theme
    from logger import get_logger
    logger = get_logger('widgets.smart_search_widget.components.product_card')
except ImportError:
    # Simple fallback logger if the standard logger is unavailable
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('widgets.smart_search_widget.components.product_card')

    # Fallback theme functions
    def get_color(name):
        colors = {
            'background': '#F5F5F5',
            'card_bg': '#FFFFFF',
            'text': '#333333',
            'title': '#111111',
            'secondary_text': '#666666',
            'border': '#DDDDDD',
            'highlight': '#3A7BDF',
            'input_bg': '#FFFFFF',
            'button': '#3A7BDF',
            'button_hover': '#2A5CBF',
            'button_pressed': '#1A4CAF',
            'success': '#4CAF50',
            'selected': '#E3F2FD',
            'shadow': '#00000033',
            'secondary': '#E0E0E0'
        }
        return colors.get(name, '#FFFFFF')

    def get_size(name):
        sizes = {
            'padding': 10,
            'margin': 10,
            'border_radius': 5,
            'tiny': 4,
            'small': 8,
            'medium': 16,
            'large': 24
        }
        return sizes.get(name, 10)

    def get_font_size(name):
        sizes = {
            'small': 10,
            'medium': 12,
            'regular': 14,
            'large': 16,
            'title': 20
        }
        return sizes.get(name, 14)

    _current_theme = "light"


class ProductCard(QFrame):
    """Enhanced product card with modern styling and improved label-value proximity."""

    def __init__(self, product, translator, on_edit_callback, on_delete_callback, parent=None):
        super().__init__(parent)
        self.product = product
        self.translator = translator
        self.on_edit = on_edit_callback
        self.on_delete = on_delete_callback
        self.is_expanded = False
        self.extra_info_container = None

        self.setObjectName("productCard")
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        # Set theme class based on current theme
        if _current_theme in ["dark", "classic"]:
            self.setProperty("class", "darkTheme")
        else:
            self.setProperty("class", "lightTheme")

        # Init UI and styling
        self._init_ui()
        self.apply_theme()

    def apply_theme(self):
        """Apply theme styling to the product card."""
        # Apply shadow effect with theme colors
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(get_color('shadow')))
        shadow.setOffset(2, 2)
        self.setGraphicsEffect(shadow)

        # Apply custom styling with theme colors and larger, more elegant text
        self.setStyleSheet(f"""
            QFrame#productCard {{
                border-radius: {get_size('border_radius')}px;
                background-color: {get_color('card_bg')};
                border: 1px solid {get_color('border')};
                padding: 2px;
            }}

            QLabel#productCardName {{
                font-size: {get_font_size('large') + 2}px;
                font-weight: bold;
                color: {get_color('title')};
                letter-spacing: 0.3px;
                margin-bottom: 2px;
            }}
            
            QLabel#productCardID {{
                margin-bottom: 4px;
                font-size: {get_font_size('regular')}px;
            }}

            QLabel.fieldLabel {{
                font-weight: bold;
                color: {get_color('secondary_text')};
                padding-right: 1px;
                font-size: {get_font_size('regular')}px;
            }}

            QLabel.fieldValue {{
                color: {get_color('text')};
                font-size: {get_font_size('regular')}px;
                font-weight: 500;
                padding-left: 1px;
            }}

            QFrame#cardSeparator {{
                background-color: {get_color('border')};
                max-height: 1px;
                margin: 6px 0px;
            }}

            QToolButton#cardEditButton, QToolButton#cardDeleteButton {{
                background-color: transparent; 
                border: none;
                color: {get_color('text')};
                font-size: {get_font_size('large') + 4}px;
            }}

            QToolButton#cardEditButton:hover, QToolButton#cardDeleteButton:hover {{
                background-color: {get_color('secondary')};
                border-radius: {get_size('tiny')}px;
            }}
            
            QPushButton#showMoreButton {{
                background-color: {get_color('button')};
                color: white;
                border: none;
                border-radius: {get_size('small')}px;
                padding: 4px 8px;
                font-size: {get_font_size('small')}px;
                font-weight: 500;
                max-width: 100px;
                margin-top: 4px;
            }}
            
            QPushButton#showMoreButton:hover {{
                background-color: {get_color('button_hover')};
            }}
            
            QPushButton#showMoreButton:pressed {{
                background-color: {get_color('button_pressed')};
            }}
        """)

    def _init_ui(self):
        """Initialize the product card UI with improved layout."""
        # Main layout with reduced padding for compactness
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(6)

        # Create a fixed content container that won't resize during animations
        self.fixed_content = QWidget()
        fixed_layout = QVBoxLayout(self.fixed_content)
        fixed_layout.setContentsMargins(0, 0, 0, 0)
        fixed_layout.setSpacing(6)

        # Top section with product name, ID and actions
        top_section = QHBoxLayout()
        top_section.setSpacing(10)

        # Product name and ID in separate containers
        name_container = QVBoxLayout()
        name_container.setSpacing(4)

        # Product name with better typography
        name = self.product.get('product_name', 'Unknown Product')
        barcode = str(self.product.get('parcode', 'N/A'))

        # Name in its own label
        name_label = QLabel(f"<b>{name}</b>")
        name_label.setObjectName("productCardName")
        name_font = QFont()
        name_font.setPointSize(get_font_size('large') + 2)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setWordWrap(True)

        # ID in a separate label with distinctive styling
        id_label = QLabel(f"<span style='background-color: {get_color('highlight')}; color: white; padding: 2px 6px; border-radius: 4px;'>ID: {barcode}</span>")
        id_label.setObjectName("productCardID")

        # Add name and ID to container
        name_container.addWidget(name_label)
        name_container.addWidget(id_label)

        # Action buttons in an elegant container - more compact
        actions_container = QFrame()
        actions_container.setObjectName("cardActionsContainer")
        actions_container.setMaximumWidth(70)
        actions_container.setMinimumWidth(70)

        actions_layout = QHBoxLayout(actions_container)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(4)

        # Edit button with better styling - smaller
        edit_button = QToolButton()
        edit_button.setObjectName("cardEditButton")
        edit_button.setText("✏️")
        edit_button.setToolTip(self.translator.t('edit'))
        edit_button.setMinimumSize(QSize(32, 32))
        edit_button.setMaximumSize(QSize(32, 32))
        edit_button.clicked.connect(lambda: self.on_edit(self.product))

        # Delete button with better styling - smaller
        delete_button = QToolButton()
        delete_button.setObjectName("cardDeleteButton")
        delete_button.setText("🗑️")
        delete_button.setToolTip(self.translator.t('remove'))
        delete_button.setMinimumSize(QSize(32, 32))
        delete_button.setMaximumSize(QSize(32, 32))
        delete_button.clicked.connect(lambda: self.on_delete(self.product))

        actions_layout.addWidget(edit_button)
        actions_layout.addWidget(delete_button)

        top_section.addLayout(name_container, 1)
        top_section.addWidget(actions_container)

        # Add a separator line with style
        separator = QFrame()
        separator.setObjectName("cardSeparator")
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("margin-top: 4px; margin-bottom: 4px;")

        # Create main fields (using the combined label approach)
        # Price
        price = self.product.get('price', 0)
        price_str = f"${price:.2f}" if price is not None else "N/A"

        # Quantity
        qty = self.product.get('quantity', 0)
        qty_str = str(qty) if qty is not None else "N/A"

        # Manufacturer
        manufacturer = self.product.get('manufacturer', 'N/A')
        manufacturer_str = manufacturer if manufacturer else 'N/A'

        # Create the main fields layout using combined labels
        main_fields_layout = QVBoxLayout()
        main_fields_layout.setSpacing(2)
        main_fields_layout.setContentsMargins(0, 0, 0, 0)

        # Create price label
        price_label = QLabel(f"<b>{self.translator.t('price')}:</b> {price_str}")
        price_label.setStyleSheet(f"""
            font-size: {get_font_size('regular')}px;
            padding: 0px;
            margin: 0px;
        """)
        main_fields_layout.addWidget(price_label)

        # Create quantity label
        qty_label = QLabel(f"<b>{self.translator.t('quantity')}:</b> {qty_str}")
        qty_label.setStyleSheet(f"""
            font-size: {get_font_size('regular')}px;
            padding: 0px;
            margin: 0px;
        """)
        main_fields_layout.addWidget(qty_label)

        # Create manufacturer label
        mfg_label = QLabel(f"<b>{self.translator.t('manufacturer')}:</b> {manufacturer_str}")
        mfg_label.setStyleSheet(f"""
            font-size: {get_font_size('regular')}px;
            padding: 0px;
            margin: 0px;
        """)
        main_fields_layout.addWidget(mfg_label)

        # Add the fixed content components
        fixed_layout.addLayout(top_section)
        fixed_layout.addWidget(separator)
        fixed_layout.addLayout(main_fields_layout)

        # Add fixed content to main layout
        main_layout.addWidget(self.fixed_content)

        # Extra info container (initially hidden)
        self.extra_info_container = QWidget()
        self.extra_info_container.setVisible(False)

        # Category
        category = self.product.get('category', 'N/A')

        # Original (Yes/No)
        is_original = self.product.get('original', False)
        original_str = self.translator.t('yes') if is_original else self.translator.t('no')

        # Extra info layout
        extra_info_layout = QVBoxLayout(self.extra_info_container)
        extra_info_layout.setContentsMargins(0, 8, 0, 0)
        extra_info_layout.setSpacing(2)  # Reduced spacing

        # Extra separator for expanded section
        extra_separator = QFrame()
        extra_separator.setObjectName("cardSeparator")
        extra_separator.setFrameShape(QFrame.HLine)
        extra_separator.setFrameShadow(QFrame.Sunken)
        extra_info_layout.addWidget(extra_separator)

        # Category label
        category_label = QLabel(f"<b>{self.translator.t('category')}:</b> {category}")
        category_label.setStyleSheet(f"""
            font-size: {get_font_size('regular')}px;
            padding: 0px;
            margin: 0px;
        """)
        extra_info_layout.addWidget(category_label)

        # Original label
        original_label = QLabel(f"<b>{self.translator.t('original')}:</b> {original_str}")
        original_label.setStyleSheet(f"""
            font-size: {get_font_size('regular')}px;
            padding: 0px;
            margin: 0px;
        """)
        extra_info_layout.addWidget(original_label)

        # Car compatibility if available
        if 'compatible_brands' in self.product or 'compatible_models' in self.product:
            compatibility_text = (
                f"{self.product.get('compatible_brands', 'N/A')} - "
                f"{self.product.get('compatible_models', 'N/A')}"
            )

            # Car compatibility label
            compat_label = QLabel(f"<b>{self.translator.t('car')}:</b> {compatibility_text}")
            compat_label.setStyleSheet(f"""
                font-size: {get_font_size('regular')}px;
                padding: 0px;
                margin: 0px;
            """)
            compat_label.setWordWrap(True)
            extra_info_layout.addWidget(compat_label)

        # Add extra info container to main layout
        main_layout.addWidget(self.extra_info_container)

        # Create "Show More" button
        show_more_container = QHBoxLayout()
        show_more_container.setAlignment(Qt.AlignCenter)

        self.show_more_button = QPushButton(self.translator.t('show_more'))
        self.show_more_button.setObjectName("showMoreButton")
        self.show_more_button.setCursor(Qt.PointingHandCursor)
        self.show_more_button.clicked.connect(self.toggle_expanded)

        show_more_container.addWidget(self.show_more_button)

        # Add button to main layout
        main_layout.addLayout(show_more_container)

    def toggle_expanded(self):
        """Toggle expanded state to show or hide additional information."""
        self.is_expanded = not self.is_expanded

        # Show or hide the extra content immediately without animation
        self.extra_info_container.setVisible(self.is_expanded)

        # Update button text based on state
        if self.is_expanded:
            self.show_more_button.setText(self.translator.t('show_less'))
        else:
            self.show_more_button.setText(self.translator.t('show_more'))

        # Force a layout update
        self.adjustSize()

    def enterEvent(self, event):
        """Handle mouse enter event for hover effects."""
        # Scale up shadow slightly on hover
        shadow = self.graphicsEffect()
        if shadow and isinstance(shadow, QGraphicsDropShadowEffect):
            shadow.setBlurRadius(20)
            shadow.setColor(QColor(get_color('shadow')))
            shadow.setOffset(3, 3)

        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event to revert hover effects."""
        # Return shadow to normal
        shadow = self.graphicsEffect()
        if shadow and isinstance(shadow, QGraphicsDropShadowEffect):
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(get_color('shadow')))
            shadow.setOffset(2, 2)

        super().leaveEvent(event)