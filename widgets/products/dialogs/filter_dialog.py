"""
Enhanced filter dialog using the new styled widgets system.

This dialog allows users to filter products by various criteria.
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QFormLayout,
                             QGridLayout, QButtonGroup)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from themes import get_color
from widgets.products.dialogs.base_dialog import ElegantDialog
from widgets.products.components.styled_widgets import (
    StyledPushButton, StyledLineEdit, StyledDoubleSpinBox,
    StyledGroupBox, StyledRadioButton, StyledTitleLabel
)


class FilterDialog(ElegantDialog):
    """Enhanced filter dialog with improved styling and user experience."""

    def __init__(self, translator, parent=None, currency_symbol="₪"):
        super().__init__(translator, parent, title='filter_title')

        # Make the dialog more compact
        self.setMinimumWidth(420)
        self.setMinimumHeight(400)

        # Use the provided currency symbol or default to ILS
        self.currency_symbol = currency_symbol

        # Initialize empty filters dictionary
        self.filters = {
            "category": "",
            "name": "",
            "brand": "",
            "model": "",
            "min_price": None,
            "max_price": None,
            "stock_status": None  # This is the key we'll use for stock filtering
        }

        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog UI with styled widgets"""
        # Add a title label with medium font
        title_label = StyledTitleLabel(self.translator.t('filter_criteria'))
        self.main_layout.addWidget(title_label)

        # Create a form layout for filter inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(10)  # Reduced spacing
        form_layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Product Details Group
        product_group = StyledGroupBox(self.translator.t('product_details'))
        product_grid = QGridLayout(product_group)
        product_grid.setSpacing(8)  # Reduced spacing
        product_grid.setContentsMargins(8, 12, 8, 8)  # Adjusted to fit title

        # Product Name
        name_label = QLabel(self.translator.t('product_name') + ":")
        self.name_input = StyledLineEdit()
        self.name_input.setPlaceholderText(self.translator.t('name_placeholder'))
        product_grid.addWidget(name_label, 0, 0)
        product_grid.addWidget(self.name_input, 0, 1)

        # Category
        category_label = QLabel(self.translator.t('category') + ":")
        self.category_input = StyledLineEdit()
        self.category_input.setPlaceholderText(self.translator.t('category_placeholder'))
        product_grid.addWidget(category_label, 1, 0)
        product_grid.addWidget(self.category_input, 1, 1)

        form_layout.addRow("", product_group)

        # Car Details Group
        car_group = StyledGroupBox(self.translator.t('car_details'))
        car_grid = QGridLayout(car_group)
        car_grid.setSpacing(8)  # Reduced spacing
        car_grid.setContentsMargins(8, 12, 8, 8)  # Adjusted to fit title

        # Brand
        brand_label = QLabel(self.translator.t('brand') + ":")
        self.brand_input = StyledLineEdit()
        self.brand_input.setPlaceholderText(self.translator.t('brand_placeholder'))
        car_grid.addWidget(brand_label, 0, 0)
        car_grid.addWidget(self.brand_input, 0, 1)

        # Model
        model_label = QLabel(self.translator.t('model') + ":")
        self.model_input = StyledLineEdit()
        self.model_input.setPlaceholderText(self.translator.t('model_placeholder'))
        car_grid.addWidget(model_label, 1, 0)
        car_grid.addWidget(self.model_input, 1, 1)

        form_layout.addRow("", car_group)

        # Price range and Stock Status in the same row
        dual_layout = QHBoxLayout()

        # Price range group - make it smaller
        price_group = StyledGroupBox(self.translator.t('price_range'))
        price_layout = QHBoxLayout(price_group)
        price_layout.setSpacing(5)  # Reduced spacing
        price_layout.setContentsMargins(8, 12, 8, 8)  # Adjusted to fit title

        # Min price with styled widget
        min_layout = QVBoxLayout()
        min_layout.setSpacing(2)  # Very small spacing
        min_label = QLabel(self.translator.t('min'))
        self.min_price = StyledDoubleSpinBox()
        self.min_price.setRange(0, 9999.99)
        self.min_price.setPrefix(f"{self.currency_symbol} ")
        self.min_price.setFixedWidth(100)  # Smaller width
        min_layout.addWidget(min_label)
        min_layout.addWidget(self.min_price)

        # Max price with styled widget
        max_layout = QVBoxLayout()
        max_layout.setSpacing(2)  # Very small spacing
        max_label = QLabel(self.translator.t('max'))
        self.max_price = StyledDoubleSpinBox()
        self.max_price.setRange(0, 9999.99)
        self.max_price.setPrefix(f"{self.currency_symbol} ")
        self.max_price.setFixedWidth(100)  # Smaller width
        max_layout.addWidget(max_label)
        max_layout.addWidget(self.max_price)

        price_layout.addLayout(min_layout)
        price_layout.addLayout(max_layout)

        # Stock status group with styled radio buttons
        stock_group = StyledGroupBox(self.translator.t('stock_status'))
        stock_layout = QVBoxLayout(stock_group)
        stock_layout.setSpacing(3)  # Reduced spacing
        stock_layout.setContentsMargins(8, 12, 8, 8)  # Adjusted to fit title

        self.in_stock_all = StyledRadioButton(self.translator.t('all_products'))
        self.in_stock_yes = StyledRadioButton(self.translator.t('in_stock_only'))
        self.in_stock_no = StyledRadioButton(self.translator.t('out_of_stock_only'))

        # Create a button group for stock status radio buttons
        self.stock_button_group = QButtonGroup(self)
        self.stock_button_group.addButton(self.in_stock_all, 0)
        self.stock_button_group.addButton(self.in_stock_yes, 1)
        self.stock_button_group.addButton(self.in_stock_no, 2)

        self.in_stock_all.setChecked(True)  # Default to all products

        stock_layout.addWidget(self.in_stock_all)
        stock_layout.addWidget(self.in_stock_yes)
        stock_layout.addWidget(self.in_stock_no)

        # Add both groups side by side
        dual_layout.addWidget(price_group, 1)
        dual_layout.addWidget(stock_group, 1)
        form_layout.addRow("", dual_layout)

        # Add form to main layout
        self.main_layout.addLayout(form_layout)

        # Add separator before buttons
        self.add_separator()

        # Create buttons
        self.reset_btn = StyledPushButton(self.translator.t('reset'))
        if QIcon("resources/reset_icon.png").isNull() == False:
            self.reset_btn.setIcon(QIcon("resources/reset_icon.png"))
        self.reset_btn.clicked.connect(self.reset_filters)

        self.cancel_btn = StyledPushButton(self.translator.t('cancel'))
        if QIcon("resources/cancel_icon.png").isNull() == False:
            self.cancel_btn.setIcon(QIcon("resources/cancel_icon.png"))
        self.cancel_btn.clicked.connect(self.reject)

        self.apply_btn = StyledPushButton(self.translator.t('apply_filter'), is_primary=True)
        if QIcon("resources/filter_icon.png").isNull() == False:
            self.apply_btn.setIcon(QIcon("resources/filter_icon.png"))
        self.apply_btn.clicked.connect(self.apply_filters)

        # Add buttons to layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.apply_btn)

        self.main_layout.addLayout(button_layout)

    def reset_filters(self):
        """Reset all filter fields to default values."""
        self.category_input.clear()
        self.name_input.clear()
        self.brand_input.clear()
        self.model_input.clear()
        self.min_price.setValue(0)
        self.max_price.setValue(0)
        self.in_stock_all.setChecked(True)

        # Reset the filters dictionary too
        self.filters = {
            "category": "",
            "name": "",
            "brand": "",
            "model": "",
            "min_price": None,
            "max_price": None,
            "stock_status": None
        }

    def apply_filters(self):
        """Apply filters and store values with simplified stock status handling."""
        self.filters["category"] = self.category_input.text().strip()
        self.filters["name"] = self.name_input.text().strip()
        self.filters["brand"] = self.brand_input.text().strip()
        self.filters["model"] = self.model_input.text().strip()

        # Only set min/max price if they're not at default values
        if self.min_price.value() > 0:
            self.filters["min_price"] = self.min_price.value()
        else:
            self.filters["min_price"] = None

        if self.max_price.value() > 0:
            self.filters["max_price"] = self.max_price.value()
        else:
            self.filters["max_price"] = None

        # Simplified stock status handling - use a simple string identifier
        if self.in_stock_yes.isChecked():
            self.filters["stock_status"] = "in_stock"
        elif self.in_stock_no.isChecked():
            self.filters["stock_status"] = "out_of_stock"
        else:
            self.filters["stock_status"] = None

        self.accept()

    def get_filters(self):
        """Return the current filter settings."""
        return self.filters

    def initialize_from_saved_settings(self, saved_settings):
        """Initialize the dialog with previously saved settings"""
        if not saved_settings:
            return

        # Set text fields
        if saved_settings.get("category"):
            self.category_input.setText(saved_settings["category"])

        if saved_settings.get("name"):
            self.name_input.setText(saved_settings["name"])

        if saved_settings.get("brand"):
            self.brand_input.setText(saved_settings["brand"])

        if saved_settings.get("model"):
            self.model_input.setText(saved_settings["model"])

        # Set price range
        if saved_settings.get("min_price") is not None:
            self.min_price.setValue(saved_settings["min_price"])

        if saved_settings.get("max_price") is not None:
            self.max_price.setValue(saved_settings["max_price"])

        # Set stock status radio buttons
        if saved_settings.get("stock_status") == "in_stock":
            self.in_stock_yes.setChecked(True)
        elif saved_settings.get("stock_status") == "out_of_stock":
            self.in_stock_no.setChecked(True)
        else:
            self.in_stock_all.setChecked(True)