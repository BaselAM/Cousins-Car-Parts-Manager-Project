"""
Details selection widget for the parts navigation system.
The sixth step in the parts navigation hierarchy.
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QFormLayout,
                             QComboBox, QLineEdit, QSpinBox, QHBoxLayout,
                             QRadioButton, QButtonGroup, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from .base_step_widget import BaseStepWidget
from .ui_utils import InfoHeader
from .database_worker import DatabaseOperator
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.details')

class DetailsWidget(BaseStepWidget):
    """
    Sixth step in the parts navigation - selecting additional details/specifications
    for the chosen product
    """
    # Signal emitted when details are selected
    details_selected = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        super().__init__(translator, db, parent)

        # Set up data
        self.current_product = None

    def setup_ui(self):
        """Initialize and arrange UI elements"""
        # Call parent setup first
        super().setup_ui()

        # Update title
        self.title.setText(self.translator.t('select_details'))

        # Product info at top
        self.product_info = InfoHeader(self.translator)
        self.main_layout.addWidget(self.product_info)

        # Form container
        self.form_frame = QFrame()
        self.form_frame.setObjectName("formFrame")
        form_layout = QFormLayout(self.form_frame)
        form_layout.setContentsMargins(20, 20, 20, 20)
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

        # Manufacturer selection
        self.manufacturer_label = QLabel(self.translator.t('manufacturer'))
        self.manufacturer_combo = QComboBox()
        form_layout.addRow(self.manufacturer_label, self.manufacturer_combo)

        # Material selection
        self.material_label = QLabel(self.translator.t('material'))
        self.material_combo = QComboBox()
        form_layout.addRow(self.material_label, self.material_combo)

        # Quality level
        self.quality_label = QLabel(self.translator.t('quality'))

        # Quality container
        quality_container = QWidget()
        quality_layout = QHBoxLayout(quality_container)
        quality_layout.setContentsMargins(0, 0, 0, 0)
        quality_layout.setSpacing(15)

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

        form_layout.addRow(self.quality_label, quality_container)

        # Quantity selection
        self.quantity_label = QLabel(self.translator.t('quantity'))
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(99)
        self.quantity_spin.setValue(1)
        form_layout.addRow(self.quantity_label, self.quantity_spin)

        # Special comments
        self.comments_label = QLabel(self.translator.t('comments'))
        self.comments_input = QLineEdit()
        self.comments_input.setPlaceholderText(self.translator.t('comments_placeholder'))
        form_layout.addRow(self.comments_label, self.comments_input)

        # Add form to main layout
        self.main_layout.addWidget(self.form_frame, 1)

        # Continue button
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 10, 0, 0)

        self.continue_button = QFrame()
        self.continue_button.setObjectName("continueButton")
        self.continue_button.setCursor(Qt.PointingHandCursor)
        self.continue_button.setMinimumHeight(50)

        continue_layout = QVBoxLayout(self.continue_button)
        continue_layout.setContentsMargins(0, 0, 0, 0)

        self.continue_button_text = QLabel(self.translator.t('continue_button'))
        self.continue_button_text.setObjectName("continueButtonText")
        self.continue_button_text.setAlignment(Qt.AlignCenter)

        continue_layout.addWidget(self.continue_button_text, 0, Qt.AlignCenter)

        button_layout.addStretch(1)
        button_layout.addWidget(self.continue_button)
        button_layout.addStretch(1)

        self.main_layout.addLayout(button_layout)

        # Connect signals
        self.continue_button.mousePressEvent = self.on_continue_clicked

        # Update help text
        self.help_text.setText(self.translator.t('select_details_help'))

    def apply_theme(self):
        """Apply current theme"""
        # Call parent apply_theme first
        super().apply_theme()

        # Apply theme to our specific components
        self.product_info.apply_theme()

        # Get theme colors
        bg_color = get_color('background')
        card_bg = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        highlight = get_color('highlight')

        # Apply theme to form and inputs
        self.form_frame.setStyleSheet(f"""
            #formFrame {{
                background-color: {card_bg};
                border: 1px solid {border_color};
                border-radius: 10px;
            }}
            
            QLabel {{
                color: {text_color};
                font-size: 14px;
            }}
            
            QLineEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }}
            
            QComboBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 8px;
                min-width: 200px;
                font-size: 14px;
            }}
            
            QComboBox::drop-down {{
                border: none;
                width: 24px;
            }}
            
            QComboBox:hover {{
                border: 1px solid {highlight};
            }}
            
            QSpinBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 8px;
                min-width: 80px;
                font-size: 14px;
            }}
            
            QRadioButton {{
                color: {text_color};
                font-size: 14px;
                spacing: 8px;
            }}
            
            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 1px solid {border_color};
            }}
            
            QRadioButton::indicator:checked {{
                background-color: {highlight};
                border: 2px solid {highlight};
                padding: 2px;
            }}
            
            QRadioButton::indicator:unchecked {{
                background-color: {bg_color};
                border: 1px solid {border_color};
            }}
        """)

        # Apply theme to continue button
        self.continue_button.setStyleSheet(f"""
            #continueButton {{
                background-color: {highlight};
                color: white;
                border-radius: 25px;
                min-width: 180px;
                max-width: 220px;
            }}
            
            #continueButton:hover {{
                background-color: {QColor(highlight).darker(110).name()};
            }}
            
            #continueButtonText {{
                color: white;
                font-size: 16px;
                font-weight: bold;
            }}
        """)

    def update_translations(self):
        """Update all translatable text"""
        # Update our own texts
        self.title.setText(self.translator.t('select_details'))
        self.help_text.setText(self.translator.t('select_details_help'))

        # Update form labels
        self.manufacturer_label.setText(self.translator.t('manufacturer'))
        self.material_label.setText(self.translator.t('material'))
        self.quality_label.setText(self.translator.t('quality'))
        self.quantity_label.setText(self.translator.t('quantity'))
        self.comments_label.setText(self.translator.t('comments'))
        self.comments_input.setPlaceholderText(self.translator.t('comments_placeholder'))

        # Update quality radio buttons
        self.standard_radio.setText(self.translator.t('quality_standard'))
        self.premium_radio.setText(self.translator.t('quality_premium'))
        self.oem_radio.setText(self.translator.t('quality_oem'))

        # Update continue button
        self.continue_button_text.setText(self.translator.t('continue_button'))

        # Update product info if a product is selected
        if self.current_product:
            self.product_info.set_info(
                f"{self.current_product['name']} - {self.current_product['category']}"
            )

    def on_show(self):
        """Called when this step is shown"""
        # Nothing to do here - everything is set up when set_product is called
        pass

    def set_product(self, product_data):
        """Set the current product and update the form with its available options"""
        if not product_data:
            return

        self.current_product = product_data

        # Update product info
        self.product_info.set_info(f"{product_data['name']} - {product_data['category']}")

        # Load appropriate options based on product
        self.load_manufacturer_options()
        self.load_material_options()

        # Set default quantity to 1
        self.quantity_spin.setValue(1)

        # Set max quantity to available stock
        max_quantity = min(product_data.get('quantity', 99), 99)
        if max_quantity < 1:
            max_quantity = 1  # Allow at least 1
        self.quantity_spin.setMaximum(max_quantity)

        # Clear comments
        self.comments_input.clear()

    def set_previous_step_data(self, data):
        """Set data from previous step"""
        if data:
            self.set_product(data)

    def load_manufacturer_options(self):
        """Load manufacturer options for the current product"""
        try:
            # Clear existing items
            self.manufacturer_combo.clear()

            # For a real implementation, get manufacturers from database
            # For now, use some default options
            if self.current_product and self.current_product.get('category'):
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
            else:
                # Default options if no product is set
                self.manufacturer_combo.addItems(['OEM', 'Aftermarket', 'Generic'])

        except Exception as e:
            logger.error(f"Error loading manufacturers: {str(e)}")
            # Add default items if error occurs
            self.manufacturer_combo.clear()
            self.manufacturer_combo.addItems(['OEM', 'Aftermarket', 'Generic'])

    def load_material_options(self):
        """Load material options for the current product"""
        try:
            # Clear existing items
            self.material_combo.clear()

            # For a real implementation, get materials from database
            # For now, use some default options
            if self.current_product and self.current_product.get('category'):
                category = self.current_product['category']

                if category == 'Brake System':
                    materials = ['Ceramic', 'Semi-metallic', 'Organic', 'Cast Iron', 'Carbon Fiber']
                elif category == 'Engine Parts':
                    materials = ['Metal', 'Rubber', 'Silicone', 'Plastic', 'Paper']
                elif category == 'Suspension':
                    materials = ['Steel', 'Aluminum', 'Rubber', 'Polyurethane', 'Composite']
                else:
                    materials = ['Metal', 'Plastic', 'Rubber', 'Composite', 'Carbon Fiber']

                self.material_combo.addItems(materials)
            else:
                # Default options if no product is set
                self.material_combo.addItems(['Metal', 'Plastic', 'Rubber', 'Composite', 'Carbon Fiber'])

        except Exception as e:
            logger.error(f"Error loading materials: {str(e)}")
            # Add default items if error occurs
            self.material_combo.clear()
            self.material_combo.addItems(['Metal', 'Plastic', 'Rubber', 'Composite', 'Carbon Fiber'])

    def get_selected_quality(self):
        """Get the selected quality level"""
        if self.standard_radio.isChecked():
            return self.translator.t('quality_standard')
        elif self.premium_radio.isChecked():
            return self.translator.t('quality_premium')
        elif self.oem_radio.isChecked():
            return self.translator.t('quality_oem')
        else:
            return self.translator.t('quality_standard')  # Default

    def on_continue_clicked(self, event=None):
        """Handle click on continue button"""
        if not self.current_product:
            return

        # Gather selected details
        details = {
            'manufacturer': self.manufacturer_combo.currentText(),
            'material': self.material_combo.currentText(),
            'quality': self.get_selected_quality(),
            'quantity': self.quantity_spin.value(),
            'comments': self.comments_input.text().strip()
        }

        logger.info(f"Details selected for {self.current_product['name']}: {details}")

        # Save selected details
        self.step_data = details

        # Emit signals for main container
        self.details_selected.emit(details)
        self.step_completed.emit(details)

    def reset(self):
        """Reset this step's data"""
        super().reset()
        self.current_product = None
        self.product_info.set_info("")
        self.manufacturer_combo.clear()
        self.material_combo.clear()
        self.standard_radio.setChecked(True)
        self.quantity_spin.setValue(1)
        self.comments_input.clear()

    def can_proceed(self):
        """Check if user can proceed to next step"""
        return self.step_data is not None