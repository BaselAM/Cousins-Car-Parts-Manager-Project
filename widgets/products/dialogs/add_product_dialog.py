"""
Fixed Add Product Dialog with proper barcode scanner button import
"""
import os
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFormLayout, QDoubleSpinBox, QSpinBox,
                             QInputDialog, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QColor

from themes import get_color
from widgets.products.dialogs.base_dialog import ElegantDialog

# Try importing the BarcodeScannerButton
try:
    from widgets.products.components.barcode_scanner_button import BarcodeScannerButton
    # Set flag to indicate import succeeded
    BARCODE_SCANNER_AVAILABLE = True
except ImportError:
    # Set flag to indicate we need to use fallback
    BARCODE_SCANNER_AVAILABLE = False


class AddProductDialog(ElegantDialog):
    """An elegant dialog for adding new products with improved validation and animation."""

    def __init__(self, translator, parent=None):
        super().__init__(translator, parent, title='product_details')
        self.setWindowTitle(self.translator.t('product_details'))
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self.product_data = {}
        self.barcode_scanner = None  # Initialize explicitly as None
        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog UI with safe error handling"""
        try:
            main_layout = QVBoxLayout(self)
            main_layout.setSpacing(15)
            main_layout.setContentsMargins(20, 20, 20, 20)

            # Add a title label with larger font
            title_label = QLabel(self.translator.t('product_details'))
            title_font = title_label.font()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(title_label)

            # Create a form layout for product inputs
            form_layout = QFormLayout()
            form_layout.setSpacing(15)
            form_layout.setLabelAlignment(Qt.AlignRight)
            form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)

            # Barcode (Product ID)
            barcode_label = QLabel(self.translator.t('barcode') + ":")
            self.barcode_layout = QHBoxLayout()
            self.barcode_layout.setSpacing(12)  # Space between input and icon

            # Add the barcode input
            self.barcode_input = QLineEdit()
            self.barcode_input.setPlaceholderText(self.translator.t('barcode_placeholder'))

            # Add the barcode scanner button with error handling using a separate method
            self._add_barcode_scanner()

            # Add the input to the layout
            self.barcode_layout.addWidget(self.barcode_input)

            # Add the scanner if it was successfully created
            if self.barcode_scanner is not None:
                self.barcode_layout.addWidget(self.barcode_scanner)

            form_layout.addRow(barcode_label, self.barcode_layout)

            # Category
            category_label = QLabel(self.translator.t('category') + ":")
            self.category_input = QLineEdit()
            self.category_input.setPlaceholderText(self.translator.t('category_placeholder'))
            form_layout.addRow(category_label, self.category_input)

            # Product Name (Required)
            product_name_label = QLabel(self.translator.t('product_name') + " *:")
            product_name_label.setStyleSheet("font-weight: bold;")
            self.product_name_input = QLineEdit()
            self.product_name_input.setPlaceholderText(
                self.translator.t('product_name_placeholder'))
            form_layout.addRow(product_name_label, self.product_name_input)

            # Compatible Models
            compatible_models_label = QLabel(self.translator.t('compatible_models') + ":")
            self.compatible_models_input = QLineEdit()
            self.compatible_models_input.setPlaceholderText(self.translator.t('compatible_models_placeholder'))
            form_layout.addRow(compatible_models_label, self.compatible_models_input)

            # Quantity
            quantity_label = QLabel(self.translator.t('quantity') + ":")
            self.quantity_input = QSpinBox()
            self.quantity_input.setRange(0, 9999)
            self.quantity_input.setValue(1)
            self.quantity_input.setButtonSymbols(QSpinBox.UpDownArrows)
            form_layout.addRow(quantity_label, self.quantity_input)

            # Price
            price_label = QLabel(self.translator.t('price') + ":")
            self.price_input = QDoubleSpinBox()
            self.price_input.setRange(0, 9999.99)
            self.price_input.setPrefix("$ ")
            self.price_input.setDecimals(2)
            self.price_input.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
            form_layout.addRow(price_label, self.price_input)

            # Required field note
            required_note = QLabel("* " + self.translator.t('required_field'))
            required_note.setStyleSheet("color: #888; font-style: italic; font-size: 12px;")
            required_note.setAlignment(Qt.AlignRight)
            form_layout.addRow("", required_note)

            main_layout.addLayout(form_layout)

            # Button layout
            button_layout = QHBoxLayout()
            button_layout.setSpacing(10)

            # Clear button
            self.clear_btn = QPushButton(self.translator.t('clear_all'))
            self.clear_btn.setIcon(QIcon("resources/clear_icon.png"))
            self.clear_btn.clicked.connect(self.clear_fields)
            self.clear_btn.setCursor(Qt.PointingHandCursor)
            button_layout.addWidget(self.clear_btn)

            # Spacer
            button_layout.addStretch()

            # Cancel button
            self.cancel_btn = QPushButton(self.translator.t('cancel'))
            self.cancel_btn.setIcon(QIcon("resources/cancel_icon.png"))
            self.cancel_btn.clicked.connect(self.reject)
            self.cancel_btn.setCursor(Qt.PointingHandCursor)
            button_layout.addWidget(self.cancel_btn)

            # Save button
            self.save_btn = QPushButton(self.translator.t('save'))
            self.save_btn.setIcon(QIcon("resources/save_icon.png"))
            self.save_btn.clicked.connect(self.save_product)
            self.save_btn.setCursor(Qt.PointingHandCursor)

            # Make Save button stand out
            highlight_color = get_color('highlight')
            bg_color = get_color('background')
            button_style = f"""
                QPushButton {{
                    background-color: {highlight_color};
                    color: {bg_color};
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    background-color: {QColor(highlight_color).lighter(110).name()};
                }}
                QPushButton:pressed {{
                    background-color: {QColor(highlight_color).darker(110).name()};
                }}
            """
            self.save_btn.setStyleSheet(button_style)

            button_layout.addWidget(self.save_btn)

            main_layout.addLayout(button_layout)

        except Exception as e:
            print(f"Error in setup_ui: {e}")
            import traceback
            traceback.print_exc()

    def _add_barcode_scanner(self):
        """Create and add the theme-aware barcode scanner button"""
        try:
            # Check if we can use the imported BarcodeScannerButton using our flag
            if BARCODE_SCANNER_AVAILABLE:
                # Create the button instance
                self.barcode_scanner = BarcodeScannerButton(self, self.translator)

                # Connect the barcode_scanned signal to our handler
                self.barcode_scanner.barcode_scanned.connect(self.on_barcode_scanned)
            else:
                # Try importing directly in this method
                try:
                    from widgets.products.components.theme_aware_barcode_button import ThemeAwareBarcodeScannerButton
                    self.barcode_scanner = ThemeAwareBarcodeScannerButton(self, self.translator)
                    self.barcode_scanner.barcode_scanned.connect(self.on_barcode_scanned)
                except ImportError:
                    # If import fails, use fallback
                    self._create_fallback_button()

        except Exception as e:
            print(f"Error creating barcode scanner: {e}")
            import traceback
            traceback.print_exc()
            # Create a minimal fallback if everything else fails
            self._create_fallback_button()

    def _create_fallback_button(self):
        """Create a simple fallback button if the theme-aware button can't be loaded"""
        try:
            from PyQt5.QtWidgets import QPushButton
            from PyQt5.QtCore import Qt
            from PyQt5.QtGui import QIcon

            self.barcode_scanner = QPushButton("", self)

            # Try to load the icon
            icon_paths = ["resources/barcode.png", "resources/icons/barcode.png"]
            icon_loaded = False

            for path in icon_paths:
                if os.path.exists(path):
                    self.barcode_scanner.setIcon(QIcon(path))
                    icon_loaded = True
                    break

            if not icon_loaded:
                self.barcode_scanner.setText("🔍")

            self.barcode_scanner.setFixedSize(40, 40)
            self.barcode_scanner.setCursor(Qt.PointingHandCursor)
            self.barcode_scanner.setToolTip("Scan Barcode")
            self.barcode_scanner.clicked.connect(self._show_simple_scan_dialog)
        except Exception as e:
            print(f"Error creating fallback button: {e}")
            self.barcode_scanner = None  # Give up if even this fails

    def _show_simple_scan_dialog(self):
        """Show a simple scan dialog as fallback"""
        try:
            title = "Scan Barcode"
            prompt = "Enter barcode:"

            if self.translator and hasattr(self.translator, 't'):
                title = self.translator.t('scan_barcode')
                prompt = self.translator.t('enter_barcode')

            barcode, ok = QInputDialog.getText(self, title, prompt, QLineEdit.Normal, "")

            if ok and barcode:
                self.on_barcode_scanned(barcode, "Unknown")
        except Exception as e:
            print(f"Error in fallback scan dialog: {e}")

    def on_barcode_scanned(self, barcode, barcode_format=None):
        """
        Handle barcode scanning result with defensive programming.

        Args:
            barcode: The barcode string
            barcode_format: Optional format string
        """
        try:
            # Handle case where barcode might be None or empty
            if not barcode:
                return

            # Set barcode text
            self.barcode_input.setText(barcode)

            # Auto-focus next field for better workflow
            self.category_input.setFocus()

            # Provide user feedback that scan was successful
            highlight_color = get_color('success', '#4CAF50')  # Green if theme has it, otherwise default green

            # Apply brief highlight effect to the barcode input
            original_style = self.barcode_input.styleSheet()

            # Apply success style
            self.barcode_input.setStyleSheet(f"""
                QLineEdit {{
                    background-color: {QColor(highlight_color).lighter(170).name()};
                    border: 1px solid {highlight_color};
                }}
            """)

            # Restore original style after 1 second
            QTimer.singleShot(1000, lambda: self.barcode_input.setStyleSheet(original_style))

        except Exception as e:
            print(f"Error in on_barcode_scanned: {e}")

    def clear_fields(self):
        """Clear all input fields."""
        try:
            self.barcode_input.clear()
            self.category_input.clear()
            self.product_name_input.clear()
            self.compatible_models_input.clear()
            self.quantity_input.setValue(1)
            self.price_input.setValue(0.00)

            # Return focus to barcode input
            self.barcode_input.setFocus()
        except Exception as e:
            print(f"Error in clear_fields: {e}")

    def save_product(self):
        """Validate and save product data."""
        try:
            # Check required fields
            product_name = self.product_name_input.text().strip()
            if not product_name:
                # Highlight the required field in red
                self.product_name_input.setStyleSheet("border: 2px solid red;")
                # Show error message
                error_color = get_color('status_error_text') or "#C62828"
                error_label = QLabel(self.translator.t('name_required'))
                error_label.setStyleSheet(f"color: {error_color}; font-weight: bold;")
                layout = self.layout()
                layout.insertWidget(1, error_label)  # Insert after title
                # Remove the error after 3 seconds
                QTimer.singleShot(3000, lambda: error_label.setParent(None))
                return

            # Collect all data
            self.product_data = {
                "parcode": self.barcode_input.text().strip(),
                "category": self.category_input.text().strip(),
                "product_name": product_name,
                "quantity": self.quantity_input.value(),
                "price": self.price_input.value(),
                "compatible_brands": "Other",  # Default brand
                "compatible_models": self.compatible_models_input.text().strip()
            }
            self.accept()
        except Exception as e:
            print(f"Error in save_product: {e}")

    def get_data(self):
        """Return the product data."""
        return self.product_data