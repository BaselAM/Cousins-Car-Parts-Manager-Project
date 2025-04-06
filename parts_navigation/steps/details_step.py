"""
Details configuration step for the parts navigation system.

A premium step for configuring product details with elegant styling and animations.
"""
from PyQt5.QtWidgets import (QVBoxLayout, QFrame, QLabel, QSizePolicy, QFormLayout,
                             QComboBox, QSpinBox, QLineEdit, QRadioButton,
                             QButtonGroup, QHBoxLayout, QPushButton, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QColor

from ..base import BaseStepWidget
from ..components.info_header import InfoHeader
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.steps.details')


class DetailsStep(BaseStepWidget):
    """
    Sixth step in the parts navigation - configuring product details

    Features:
    - Clean, elegant layout with premium styling
    - Product information display
    - Form fields for configuration options
    - Submit button with validation
    - Smooth animations
    """
    # Signal emitted when details are configured
    details_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        """
        Initialize the details step.

        Args:
            translator: Translator for localization
            db: Database connection
            parent: Parent widget
        """
        # Set up data
        self.current_product = None

        # Call parent init after our initialization
        super().__init__(translator, db, parent)

    def setup_ui(self):
        """Initialize and arrange UI elements with compact styling."""
        # Call parent setup first
        super().setup_ui()

        # Set title
        self.title.setText(self.translator.t('configure_details'))

        # Product info header with premium styling but more compact
        self.product_info = InfoHeader(self.translator)
        self.product_info.setMaximumHeight(40)  # Limit height
        self.content_layout.addWidget(self.product_info)

        # Create split layout for product image and form
        details_layout = QHBoxLayout()
        details_layout.setContentsMargins(6, 6, 6, 6)  # Reduced margins
        details_layout.setSpacing(10)  # Slightly reduced spacing

        # Left side - Product image (slightly smaller)
        self.image_container = QFrame()
        self.image_container.setObjectName("productImageContainer")
        self.image_container.setFixedSize(180, 180)  # Reduced from 200,200

        image_layout = QVBoxLayout(self.image_container)
        image_layout.setContentsMargins(6, 6, 6, 6)  # Reduced margins
        image_layout.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setObjectName("productImage")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(160, 160)  # Reduced from 180,180
        self.image_label.setText("No Image")

        image_layout.addWidget(self.image_label)
        details_layout.addWidget(self.image_container, 0, Qt.AlignTop | Qt.AlignLeft)

        # Right side - Form
        form_container = QFrame()
        form_container.setObjectName("detailsFormContainer")

        form_layout = QFormLayout(form_container)
        form_layout.setContentsMargins(10, 10, 10, 10)  # Reduced margins
        form_layout.setSpacing(10)  # Reduced spacing
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Add form fields with premium styling

        # Manufacturer selection
        self.manufacturer_label = QLabel(self.translator.t('manufacturer'))
        self.manufacturer_label.setObjectName("formLabel")
        self.manufacturer_combo = QComboBox()
        self.manufacturer_combo.setObjectName("formInput")
        form_layout.addRow(self.manufacturer_label, self.manufacturer_combo)

        # Material selection
        self.material_label = QLabel(self.translator.t('material'))
        self.material_label.setObjectName("formLabel")
        self.material_combo = QComboBox()
        self.material_combo.setObjectName("formInput")
        form_layout.addRow(self.material_label, self.material_combo)

        # Quality level
        self.quality_label = QLabel(self.translator.t('quality'))
        self.quality_label.setObjectName("formLabel")

        # Quality container for radio buttons
        quality_widget = QWidget()
        quality_layout = QHBoxLayout(quality_widget)
        quality_layout.setContentsMargins(0, 0, 0, 0)
        quality_layout.setSpacing(10)  # Reduced spacing

        # Radio buttons for quality
        self.quality_group = QButtonGroup(self)

        self.standard_radio = QRadioButton(self.translator.t('quality_standard'))
        self.premium_radio = QRadioButton(self.translator.t('quality_premium'))
        self.oem_radio = QRadioButton(self.translator.t('quality_oem'))

        self.quality_group.addButton(self.standard_radio, 1)
        self.quality_group.addButton(self.premium_radio, 2)
        self.quality_group.addButton(self.oem_radio, 3)

        # Default selection
        self.standard_radio.setChecked(True)

        quality_layout.addWidget(self.standard_radio)
        quality_layout.addWidget(self.premium_radio)
        quality_layout.addWidget(self.oem_radio)
        quality_layout.addStretch(1)

        form_layout.addRow(self.quality_label, quality_widget)

        # Quantity selection
        self.quantity_label = QLabel(self.translator.t('quantity'))
        self.quantity_label.setObjectName("formLabel")
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setObjectName("formInput")
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(99)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setSingleStep(1)
        form_layout.addRow(self.quantity_label, self.quantity_spin)

        # Special comments
        self.comments_label = QLabel(self.translator.t('comments'))
        self.comments_label.setObjectName("formLabel")
        self.comments_input = QLineEdit()
        self.comments_input.setObjectName("formInput")
        self.comments_input.setPlaceholderText(self.translator.t('comments_placeholder'))
        form_layout.addRow(self.comments_label, self.comments_input)

        details_layout.addWidget(form_container, 1)  # Form takes most space

        self.content_layout.addLayout(details_layout, 10)  # Details take most space

        # Continue button with premium styling
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 6, 0, 0)  # Reduced top margin
        button_layout.setSpacing(0)

        button_layout.addStretch(1)  # Push button to right side

        self.continue_button = QPushButton(self.translator.t('continue_button'))
        self.continue_button.setObjectName("primaryButton")
        self.continue_button.clicked.connect(self.on_continue_clicked)
        self.continue_button.setMinimumWidth(140)  # Slightly smaller
        self.continue_button.setMinimumHeight(36)  # Slightly smaller

        button_layout.addWidget(self.continue_button)

        self.content_layout.addLayout(button_layout)

        # Simplify help text to save space
        self.help_text.setText(self.translator.t('configure_details_help'))

    def apply_theme(self):
        """Apply premium styling based on system theme."""
        # Call parent apply_theme first
        super().apply_theme()

        # Apply theme to our components
        self.product_info.apply_theme()

        # Get theme colors
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        text_color = get_color('text', '#E2E8F0')
        border_color = get_color('border', '#2C5282')
        highlight = get_color('highlight', '#4299E1')

        # Compute derived colors
        card_bg_lighter = QColor(card_bg).lighter(108).name()

        # Apply styling to image container
        self.image_container.setStyleSheet(f"""
            #productImageContainer {{
                background-color: {card_bg_lighter};
                border-radius: 8px;
                border: 1px solid {border_color};
            }}

            #productImage {{
                background-color: {bg_color};
                border-radius: 6px;
                padding: 5px;
            }}
        """)

        # Apply styling to form elements
        form_style = f"""
            #detailsFormContainer {{
                background-color: {card_bg_lighter};
                border-radius: 8px;
                border: 1px solid {border_color};
            }}

            #formLabel {{
                color: {text_color};
                font-weight: bold;
            }}

            #formInput {{
                background-color: {card_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 8px;
                min-height: 20px;
            }}

            QComboBox {{
                background-color: {card_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 8px;
                min-width: 150px;
            }}

            QComboBox:focus, QSpinBox:focus, QLineEdit:focus {{
                border: 1px solid {highlight};
            }}

            QSpinBox {{
                background-color: {card_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 8px;
                min-width: 80px;
            }}

            QRadioButton {{
                color: {text_color};
                spacing: 5px;
            }}

            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 1px solid {border_color};
            }}

            QRadioButton::indicator:checked {{
                background-color: {highlight};
                border: 1px solid {highlight};
            }}
        """

        self.setStyleSheet(self.styleSheet() + form_style)

    def update_translations(self):
        """Update all translatable text when language changes."""
        # Call parent first
        super().update_translations()

        # Update our texts
        self.title.setText(self.translator.t('configure_details'))
        self.help_text.setText(self.translator.t('configure_details_help'))

        # Update form labels
        self.manufacturer_label.setText(self.translator.t('manufacturer'))
        self.material_label.setText(self.translator.t('material'))
        self.quality_label.setText(self.translator.t('quality'))
        self.quantity_label.setText(self.translator.t('quantity'))
        self.comments_label.setText(self.translator.t('comments'))

        # Update radio buttons
        self.standard_radio.setText(self.translator.t('quality_standard'))
        self.premium_radio.setText(self.translator.t('quality_premium'))
        self.oem_radio.setText(self.translator.t('quality_oem'))

        # Update button
        self.continue_button.setText(self.translator.t('continue_button'))

        # Update comments placeholder
        self.comments_input.setPlaceholderText(self.translator.t('comments_placeholder'))

        # Update product info if product is selected
        if self.current_product:
            self._update_product_info()

    def on_show(self):
        """Called when this step is shown."""
        # Call parent first
        super().on_show()

        # Refresh details if we have a product
        if self.current_product:
            self.load_product_details()

    def _update_product_info(self):
        """Update the product info header."""
        if not self.current_product:
            self.product_info.set_info("")
            return

        # Get info text
        product_name = self.current_product.get('name', '')
        category = self.current_product.get('category', '')

        if category:
            info_text = f"{product_name} - {category}"
        else:
            info_text = product_name

        # Update header
        self.product_info.set_info(info_text)

    def set_product(self, product_data):
        """
        Set the current product and load its details.

        Args:
            product_data: Product data dictionary
        """
        if not product_data:
            return

        # Set product
        self.current_product = product_data

        # Update info
        self._update_product_info()

        # Load product details
        self.load_product_details()

    def set_previous_step_data(self, data):
        """
        Set data from previous step.

        Args:
            data: Previous step data
        """
        # Previous step would be product selection
        if data:
            self.set_product(data)

    def load_product_details(self):
        """Load details for the current product."""
        if not self.current_product:
            return

        # Update product image
        self.load_product_image()

        # Load manufacturer options based on product category
        self.load_manufacturer_options()

        # Load material options based on product category
        self.load_material_options()

        # Reset form fields
        self.standard_radio.setChecked(True)
        self.quantity_spin.setValue(1)
        self.comments_input.clear()

        # Set quantity limits based on available stock
        max_quantity = min(self.current_product.get('quantity', 99), 99)
        if max_quantity < 1:
            max_quantity = 1  # Always allow at least 1
        self.quantity_spin.setMaximum(max_quantity)

    def load_product_image(self):
        """Load the product image."""
        if not self.current_product:
            return

        # Try to load product image by ID
        image_path = f"resources/products/{self.current_product.get('id', 0)}.png"
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            # Scale and display product image
            self.image_label.setPixmap(pixmap.scaled(
                170, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # If no product image, try category image
            if 'category' in self.current_product:
                category_image = f"resources/categories/{self.current_product['category'].lower().replace(' ', '_')}.png"
                pixmap = QPixmap(category_image)
                if not pixmap.isNull():
                    self.image_label.setPixmap(pixmap.scaled(
                        170, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.image_label.setText(self.translator.t('no_image'))
            else:
                self.image_label.setText(self.translator.t('no_image'))

    def load_manufacturer_options(self):
        """Load manufacturer options based on product category."""
        self.manufacturer_combo.clear()

        if not self.current_product or not self.current_product.get('category'):
            # Default manufacturers
            self.manufacturer_combo.addItems(['OEM', 'Aftermarket', 'Generic'])
            return

        # Load manufacturers based on category
        category = self.current_product['category']

        if category == 'Brake System':
            manufacturers = ['Brembo', 'ATE', 'Bosch', 'TRW', 'Ferodo']
        elif category == 'Engine Parts':
            manufacturers = ['Bosch', 'Mann', 'Mahle', 'NGK', 'Valeo']
        elif category == 'Suspension':
            manufacturers = ['Bilstein', 'KYB', 'Monroe', 'Sachs', 'Koni']
        else:
            manufacturers = ['OEM', 'Aftermarket', 'Generic']

        self.manufacturer_combo.addItems(manufacturers)

    def load_material_options(self):
        """Load material options based on product category."""
        self.material_combo.clear()

        if not self.current_product or not self.current_product.get('category'):
            # Default materials
            self.material_combo.addItems(['Metal', 'Plastic', 'Rubber'])
            return

        # Load materials based on category
        category = self.current_product['category']

        if category == 'Brake System':
            materials = ['Ceramic', 'Semi-metallic', 'Organic', 'Cast Iron']
        elif category == 'Engine Parts':
            materials = ['Metal', 'Rubber', 'Silicone', 'Plastic', 'Paper']
        elif category == 'Suspension':
            materials = ['Steel', 'Aluminum', 'Rubber', 'Polyurethane']
        else:
            materials = ['Metal', 'Plastic', 'Rubber', 'Composite']

        self.material_combo.addItems(materials)

    def get_selected_quality(self):
        """Get the selected quality level."""
        if self.standard_radio.isChecked():
            return self.translator.t('quality_standard')
        elif self.premium_radio.isChecked():
            return self.translator.t('quality_premium')
        elif self.oem_radio.isChecked():
            return self.translator.t('quality_oem')
        else:
            return self.translator.t('quality_standard')  # Default

    def on_continue_clicked(self):
        """Handle continue button click."""
        if not self.current_product:
            return

        # Collect form data
        details = {
            'manufacturer': self.manufacturer_combo.currentText(),
            'material': self.material_combo.currentText(),
            'quality': self.get_selected_quality(),
            'quantity': self.quantity_spin.value(),
            'comments': self.comments_input.text().strip()
        }

        logger.info(f"Details configured for {self.current_product['name']}: {details}")

        # Store selected details
        self.step_data = details

        # Emit signals
        self.details_selected.emit(details)
        self.step_completed.emit(details)

    def reset(self):
        """Reset this step's data and UI state."""
        # Call parent reset
        super().reset()

        # Clear product and form
        self.current_product = None
        self.product_info.set_info("")
        self.image_label.setText(self.translator.t('no_image'))
        self.manufacturer_combo.clear()
        self.material_combo.clear()
        self.standard_radio.setChecked(True)
        self.quantity_spin.setValue(1)
        self.comments_input.clear()

    def can_proceed(self):
        """Check if we can proceed to the next step."""
        return self.step_data is not None