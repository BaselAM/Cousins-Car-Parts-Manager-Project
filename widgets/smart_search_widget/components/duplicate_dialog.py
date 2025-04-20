"""
Duplicate product dialog component for the Smart Search Widget.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                           QLineEdit, QPushButton, QFormLayout, QSpinBox,
                           QDoubleSpinBox, QCheckBox, QMessageBox)

# Try to import theme and logger modules - handle gracefully if not available
try:
    from themes import get_color, get_size, get_font_size, apply_dialog_theme
    from logger import get_logger
    logger = get_logger('widgets.smart_search_widget.components.duplicate_dialog')
except ImportError:
    # Simple fallback logger if the standard logger is unavailable
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('widgets.smart_search_widget.components.duplicate_dialog')

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

    # Fallback apply_dialog_theme function
    def apply_dialog_theme(dialog, title):
        pass  # Just a placeholder, styling will be applied manually


class DuplicateProductDialog(QDialog):
    """Dialog for duplicating a product with a new barcode."""

    def __init__(self, product, translator, parent=None):
        super().__init__(parent)
        self.product = product
        self.translator = translator

        self.setWindowTitle(self.translator.t('duplicate_product'))
        self.setMinimumWidth(450)
        self.setMinimumHeight(500)

        self._init_ui()
        self.apply_theme()

    def apply_theme(self):
        """Apply theme styling to the dialog."""
        # Apply dialog theme if available
        try:
            apply_dialog_theme(self, self.translator.t('duplicate_product'))
        except:
            # Apply shadow and styling manually
            self.setStyleSheet(f"""
                QDialog {{
                    background-color: {get_color('background')};
                    border-radius: {get_size('border_radius')}px;
                }}
                QLabel {{
                    color: {get_color('text')};
                }}
                QLabel.title {{
                    font-size: {get_font_size('large')}px;
                    font-weight: bold;
                    color: {get_color('title')};
                    padding-bottom: {get_size('small')}px;
                }}
                QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
                    padding: {get_size('small')}px;
                    border-radius: {get_size('tiny')}px;
                    border: 1px solid {get_color('border')};
                    background-color: {get_color('input_bg')};
                    min-height: 20px;
                    color: {get_color('text')};
                }}
                QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
                    border: 2px solid {get_color('highlight')};
                }}
                QPushButton {{
                    padding: {get_size('small')}px {get_size('medium')}px;
                    border-radius: {get_size('tiny')}px;
                    font-weight: bold;
                    min-height: 20px;
                    color: {get_color('text')};
                    background-color: {get_color('secondary')};
                }}
                QPushButton:hover {{
                    background-color: {get_color('button_hover')};
                }}
                QPushButton#primaryButton {{
                    background-color: {get_color('button')};
                    color: white;
                    border: none;
                }}
                QPushButton#primaryButton:hover {{
                    background-color: {get_color('button_hover')};
                }}
                QPushButton#primaryButton:pressed {{
                    background-color: {get_color('button_pressed')};
                }}
                QLineEdit:read-only {{
                    background-color: {get_color('secondary')};
                    color: {get_color('secondary_text')};
                }}
            """)

    def _init_ui(self):
        """Initialize dialog UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Title
        title_label = QLabel(self.translator.t('duplicate_product'))
        title_label.setProperty("class", "title")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Description
        desc_label = QLabel(self.translator.t('duplicate_desc'))
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(desc_label)

        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Product name (read-only)
        self.name_edit = QLineEdit(self.product.get('product_name', ''))
        self.name_edit.setReadOnly(True)
        form_layout.addRow(self.translator.t('product_name'), self.name_edit)

        # Category (read-only)
        self.category_edit = QLineEdit(self.product.get('category', ''))
        self.category_edit.setReadOnly(True)
        form_layout.addRow(self.translator.t('category'), self.category_edit)

        # New barcode (required, must be unique)
        self.parcode_edit = QLineEdit()
        self.parcode_edit.setPlaceholderText(self.translator.t('new_barcode_required'))
        form_layout.addRow(self.translator.t('new_barcode'), self.parcode_edit)

        # Price (editable)
        self.price_edit = QDoubleSpinBox()
        self.price_edit.setRange(0, 999999.99)
        self.price_edit.setValue(self.product.get('price', 0))
        self.price_edit.setPrefix("$")
        self.price_edit.setDecimals(2)
        form_layout.addRow(self.translator.t('price'), self.price_edit)

        # Quantity (editable)
        self.quantity_edit = QSpinBox()
        self.quantity_edit.setRange(0, 9999)
        self.quantity_edit.setValue(self.product.get('quantity', 0))
        form_layout.addRow(self.translator.t('quantity'), self.quantity_edit)

        # Original part
        self.original_check = QCheckBox()
        self.original_check.setChecked(bool(self.product.get('original', False)))
        form_layout.addRow(self.translator.t('original'), self.original_check)

        # Manufacturer (editable)
        self.manufacturer_edit = QLineEdit(self.product.get('manufacturer', ''))
        form_layout.addRow(self.translator.t('manufacturer'), self.manufacturer_edit)

        # Compatible models (read-only)
        self.compatible_edit = QLineEdit(self.product.get('compatible_models', ''))
        self.compatible_edit.setReadOnly(True)
        form_layout.addRow(self.translator.t('compatible_models'), self.compatible_edit)

        # Add form to layout
        layout.addLayout(form_layout)

        # Add spacer
        layout.addStretch(1)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

        # Save button
        self.save_button = QPushButton(self.translator.t('duplicate'))
        self.save_button.setObjectName("primaryButton")
        self.save_button.setMinimumHeight(40)
        self.save_button.clicked.connect(self.accept)

        # Cancel button
        self.cancel_button = QPushButton(self.translator.t('cancel'))
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

    def get_data(self):
        """Get the data from the dialog."""
        return {
            'product_name': self.name_edit.text(),
            'category': self.category_edit.text(),
            'parcode': self.parcode_edit.text(),
            'price': self.price_edit.value(),
            'quantity': self.quantity_edit.value(),
            'original': self.original_check.isChecked(),
            'manufacturer': self.manufacturer_edit.text(),
            'compatible_models': self.compatible_edit.text(),
            'compatible_brands': self.product.get('compatible_brands', ''),
        }

    def validate(self):
        """Validate the dialog data."""
        # Check if barcode is provided
        if not self.parcode_edit.text().strip():
            QMessageBox.warning(
                self,
                self.translator.t('validation_error'),
                self.translator.t('barcode_required')
            )
            return False

        return True

    def accept(self):
        """Handle the dialog acceptance."""
        if self.validate():
            super().accept()