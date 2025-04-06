"""
Summary step for the parts navigation system.

A premium step for reviewing and confirming the complete selection
with elegant styling and animations.
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QSizePolicy,
                             QHBoxLayout, QGridLayout, QPushButton,
                             QScrollArea, QWidget, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QColor
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog, QPrintPreviewDialog

from ..base import BaseStepWidget
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.steps.summary')


class SummaryStep(BaseStepWidget):
    """
    Final step in the parts navigation - reviewing the complete selection

    Features:
    - Clean, elegant layout with premium styling
    - Complete selection display
    - Action buttons (add to cart, etc.)
    - Back navigation
    - Smooth animations
    """
    # Signal for requesting to go back to a specific step
    back_requested = pyqtSignal()

    # Signal for completing the process
    complete_requested = pyqtSignal(dict)  # Complete data

    def __init__(self, translator, db, parent=None):
        """
        Initialize the summary step.

        Args:
            translator: Translator for localization
            db: Database connection
            parent: Parent widget
        """
        # Set up data
        self.complete_data = None
        self.similar_parts = []

        # Call parent init
        super().__init__(translator, db, parent)

    def setup_ui(self):
        """Initialize and arrange UI elements with compact styling."""
        # Call parent setup first, but we'll customize more
        super().setup_ui()

        # Set title
        self.title.setText(self.translator.t('summary_title'))

        # Clear the content layout for a custom layout
        for i in reversed(range(self.content_layout.count())):
            item = self.content_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget and widget != self.title and widget != self.help_text:
                    widget.deleteLater()

        # Create main content area with premium styling
        content_area = QFrame()
        content_area.setObjectName("summaryContentArea")
        content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Layout for content area with reduced margins
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(6, 6, 6, 6)  # Reduced margins
        content_layout.setSpacing(10)  # Reduced spacing

        # Left side - Image and actions (slightly smaller)
        left_panel = QFrame()
        left_panel.setObjectName("leftSummaryPanel")
        left_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        left_panel.setMinimumWidth(200)  # Reduced from 220
        left_panel.setMaximumWidth(250)  # Kept the same

        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(6, 6, 6, 6)  # Reduced margins
        left_layout.setSpacing(10)  # Reduced spacing
        left_layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        # Image container (slightly smaller)
        self.image_frame = QFrame()
        self.image_frame.setObjectName("productImageFrame")
        self.image_frame.setMinimumSize(180, 180)  # Reduced from 200,200
        self.image_frame.setMaximumSize(220, 220)  # Reduced from 250,250

        image_layout = QVBoxLayout(self.image_frame)
        image_layout.setContentsMargins(6, 6, 6, 6)  # Reduced margins
        image_layout.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setObjectName("productImage")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumSize(160, 160)  # Reduced from 180,180
        self.image_label.setMaximumSize(200, 200)  # Reduced from 230,230
        self.image_label.setText(self.translator.t('no_image'))

        image_layout.addWidget(self.image_label)
        left_layout.addWidget(self.image_frame, 0, Qt.AlignCenter)

        # Action buttons with premium styling
        action_layout = QVBoxLayout()
        action_layout.setContentsMargins(0, 10, 0, 0)  # Reduced top margin
        action_layout.setSpacing(8)  # Reduced spacing

        self.add_to_cart_button = QPushButton(self.translator.t('add_to_cart'))
        self.add_to_cart_button.setObjectName("primaryButton")
        self.add_to_cart_button.clicked.connect(self.on_add_to_cart)
        self.add_to_cart_button.setMinimumHeight(36)  # Slightly smaller

        self.print_button = QPushButton(self.translator.t('print_details'))
        self.print_button.setObjectName("secondaryButton")
        self.print_button.clicked.connect(self.on_print)
        self.print_button.setMinimumHeight(36)  # Slightly smaller

        action_layout.addWidget(self.add_to_cart_button)
        action_layout.addWidget(self.print_button)

        left_layout.addLayout(action_layout)
        left_layout.addStretch(1)  # Push everything to the top

        content_layout.addWidget(left_panel)

        # Right side - Details grid
        right_panel = QScrollArea()
        right_panel.setObjectName("rightSummaryPanel")
        right_panel.setWidgetResizable(True)
        right_panel.setFrameShape(QFrame.NoFrame)
        right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        details_widget = QWidget()
        details_widget.setObjectName("detailsWidget")

        details_layout = QGridLayout(details_widget)
        details_layout.setContentsMargins(10, 10, 10, 10)  # Reduced margins
        details_layout.setVerticalSpacing(8)  # Reduced spacing
        details_layout.setHorizontalSpacing(15)  # Reduced spacing

        # Add all the detail rows with labels and values
        # Row 0 - Part name
        self.part_name_label = QLabel(self.translator.t('part_name'))
        self.part_name_label.setObjectName("detailLabel")
        self.part_name_value = QLabel("-")
        self.part_name_value.setObjectName("detailValue")

        details_layout.addWidget(self.part_name_label, 0, 0)
        details_layout.addWidget(self.part_name_value, 0, 1)

        # Row 1 - Car info
        self.car_label = QLabel(self.translator.t('car_info'))
        self.car_label.setObjectName("detailLabel")
        self.car_value = QLabel("-")
        self.car_value.setObjectName("detailValue")

        details_layout.addWidget(self.car_label, 1, 0)
        details_layout.addWidget(self.car_value, 1, 1)

        # Row 2 - Category
        self.category_label = QLabel(self.translator.t('category'))
        self.category_label.setObjectName("detailLabel")
        self.category_value = QLabel("-")
        self.category_value.setObjectName("detailValue")

        details_layout.addWidget(self.category_label, 2, 0)
        details_layout.addWidget(self.category_value, 2, 1)

        # Row 3 - Manufacturer
        self.manufacturer_label = QLabel(self.translator.t('manufacturer'))
        self.manufacturer_label.setObjectName("detailLabel")
        self.manufacturer_value = QLabel("-")
        self.manufacturer_value.setObjectName("detailValue")

        details_layout.addWidget(self.manufacturer_label, 3, 0)
        details_layout.addWidget(self.manufacturer_value, 3, 1)

        # Row 4 - Material
        self.material_label = QLabel(self.translator.t('material'))
        self.material_label.setObjectName("detailLabel")
        self.material_value = QLabel("-")
        self.material_value.setObjectName("detailValue")

        details_layout.addWidget(self.material_label, 4, 0)
        details_layout.addWidget(self.material_value, 4, 1)

        # Row 5 - Quality
        self.quality_label = QLabel(self.translator.t('quality'))
        self.quality_label.setObjectName("detailLabel")
        self.quality_value = QLabel("-")
        self.quality_value.setObjectName("detailValue")

        details_layout.addWidget(self.quality_label, 5, 0)
        details_layout.addWidget(self.quality_value, 5, 1)

        # Row 6 - Price
        self.price_label = QLabel(self.translator.t('price'))
        self.price_label.setObjectName("detailLabel")
        self.price_value = QLabel("-")
        self.price_value.setObjectName("priceValue")

        details_layout.addWidget(self.price_label, 6, 0)
        details_layout.addWidget(self.price_value, 6, 1)

        # Row 7 - Quantity
        self.quantity_label = QLabel(self.translator.t('selected_quantity'))
        self.quantity_label.setObjectName("detailLabel")
        self.quantity_value = QLabel("-")
        self.quantity_value.setObjectName("detailValue")

        details_layout.addWidget(self.quantity_label, 7, 0)
        details_layout.addWidget(self.quantity_value, 7, 1)

        # Row 8 - Comments
        self.comments_label = QLabel(self.translator.t('comments'))
        self.comments_label.setObjectName("detailLabel")
        self.comments_value = QLabel("-")
        self.comments_value.setObjectName("detailValue")
        self.comments_value.setWordWrap(True)

        details_layout.addWidget(self.comments_label, 8, 0, Qt.AlignTop)
        details_layout.addWidget(self.comments_value, 8, 1)

        # Set column stretch
        details_layout.setColumnStretch(0, 1)
        details_layout.setColumnStretch(1, 2)

        right_panel.setWidget(details_widget)
        content_layout.addWidget(right_panel, 1)  # Give details most space

        # Add content area to main layout
        self.content_layout.addWidget(content_area, 10)  # Give it a large stretch factor

        # Back button at bottom
        back_layout = QHBoxLayout()
        back_layout.setContentsMargins(0, 6, 0, 0)  # Reduced top margin

        self.back_button = QPushButton(self.translator.t('back_button'))
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(self.on_back_clicked)
        self.back_button.setMinimumHeight(36)  # Slightly smaller

        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        self.content_layout.addLayout(back_layout)

        # Simplify help text to save space
        self.help_text.setText(self.translator.t('summary_help'))

    def apply_theme(self):
        """Apply premium styling based on system theme."""
        # Call parent apply_theme first
        super().apply_theme()

        # Get theme colors
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        text_color = get_color('text', '#E2E8F0')
        border_color = get_color('border', '#2C5282')
        highlight = get_color('highlight', '#4299E1')

        # Compute derived colors
        card_bg_lighter = QColor(card_bg).lighter(108).name()
        highlight_lighter = QColor(highlight).lighter(115).name()

        # Apply styling to image frame
        self.image_frame.setStyleSheet(f"""
            #productImageFrame {{
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

        # Apply styling to panels
        panels_style = f"""
            #summaryContentArea {{
                background-color: transparent;
                border: none;
            }}

            #leftSummaryPanel, #rightSummaryPanel {{
                background-color: {card_bg_lighter};
                border-radius: 8px;
                border: 1px solid {border_color};
            }}

            #detailsWidget {{
                background-color: transparent;
                border: none;
            }}

            #detailLabel {{
                color: {text_color};
                font-weight: bold;
                font-size: 14px;
            }}

            #detailValue {{
                color: {text_color};
                font-size: 14px;
            }}

            #priceValue {{
                color: {highlight};
                font-size: 16px;
                font-weight: bold;
            }}

            #secondaryButton {{
                background-color: {card_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: normal;
            }}

            #secondaryButton:hover {{
                background-color: {QColor(card_bg).lighter(108).name()};
                border: 1px solid {highlight};
            }}

            #backButton {{
                background-color: {card_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 8px 16px;
            }}

            #backButton:hover {{
                background-color: {QColor(card_bg).lighter(108).name()};
                border: 1px solid {highlight};
            }}
        """

        self.setStyleSheet(self.styleSheet() + panels_style)

    def update_translations(self):
        """Update all translatable text when language changes."""
        # Call parent first
        super().update_translations()

        # Update our texts
        self.title.setText(self.translator.t('summary_title'))
        self.help_text.setText(self.translator.t('summary_help'))

        # Update details labels
        self.part_name_label.setText(self.translator.t('part_name'))
        self.car_label.setText(self.translator.t('car_info'))
        self.category_label.setText(self.translator.t('category'))
        self.manufacturer_label.setText(self.translator.t('manufacturer'))
        self.material_label.setText(self.translator.t('material'))
        self.quality_label.setText(self.translator.t('quality'))
        self.price_label.setText(self.translator.t('price'))
        self.quantity_label.setText(self.translator.t('selected_quantity'))
        self.comments_label.setText(self.translator.t('comments'))

        # Update buttons
        self.add_to_cart_button.setText(self.translator.t('add_to_cart'))
        self.print_button.setText(self.translator.t('print_details'))
        self.back_button.setText(self.translator.t('back_button'))

        # Refresh part data if available
        if self.complete_data:
            self.set_complete_data(self.complete_data)

    def on_show(self):
        """Called when this step is shown."""
        # Call parent first
        super().on_show()

        # No additional actions needed - data is set by set_complete_data

    def set_complete_data(self, data):
        """
        Set the complete data to display.

        Args:
            data: Complete selection data
        """
        if not data:
            return

        self.complete_data = data

        # Update part details
        self.part_name_value.setText(data.get('name', '-'))

        # Car info
        car_info = f"{data.get('brand', '-')} {data.get('model', '-')}"
        if 'year' in data:
            car_info += f" ({data.get('year', '-')})"
        self.car_value.setText(car_info)

        # Category
        self.category_value.setText(data.get('category', '-'))

        # Manufacturing details
        self.manufacturer_value.setText(data.get('manufacturer', '-'))
        self.material_value.setText(data.get('material', '-'))
        self.quality_value.setText(data.get('quality', '-'))

        # Price with currency
        price = data.get('price', 0)
        currency = self.translator.t('currency_symbol')
        self.price_value.setText(f"{currency} {price:.2f}")

        # Quantity
        self.quantity_value.setText(str(data.get('selected_quantity', 1)))

        # Comments
        comments = data.get('comments', '-')
        if not comments or comments.strip() == '':
            comments = '-'
        self.comments_value.setText(comments)

        # Load part image
        self.load_part_image(data)

        # Store as step data
        self.step_data = data

    def load_part_image(self, data):
        """
        Load and display the part image.

        Args:
            data: Part data containing ID and category
        """
        if not data:
            return

        # Try to load product image by ID
        image_path = f"resources/products/{data.get('id', 0)}.png"
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            # Scale and display product image
            self.image_label.setPixmap(pixmap.scaled(
                170, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            # If no product image, try category image
            if 'category' in data:
                category_image = f"resources/categories/{data['category'].lower().replace(' ', '_')}.png"
                pixmap = QPixmap(category_image)
                if not pixmap.isNull():
                    self.image_label.setPixmap(pixmap.scaled(
                        170, 170, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.image_label.setText(self.translator.t('no_image'))
            else:
                self.image_label.setText(self.translator.t('no_image'))

    def on_back_clicked(self):
        """Handle back button click."""
        logger.debug("Back button clicked on summary step")
        self.back_requested.emit()

    def on_add_to_cart(self):
        """Handle add to cart button click."""
        if not self.complete_data:
            return

        logger.info(f"Adding item to cart: {self.complete_data.get('name', 'unknown')}")

        # Calculate total price
        price = self.complete_data.get('price', 0)
        quantity = self.complete_data.get('selected_quantity', 1)
        total = price * quantity

        # Prepare order data
        order_data = {**self.complete_data, 'total_price': total}

        # Show confirmation message
        currency = self.translator.t('currency_symbol')
        message = self.translator.t(
            'add_to_cart_success',
            name=self.complete_data.get('name', 'Part'),
            quantity=quantity,
            total=f"{currency} {total:.2f}"
        )

        QMessageBox.information(
            self,
            self.translator.t('add_to_cart_title'),
            message
        )

        # Emit signal with complete order data
        self.complete_requested.emit(order_data)

    def on_print(self):
        """Handle print button click."""
        if not self.complete_data:
            return

        logger.info(f"Printing details for: {self.complete_data.get('name', 'unknown')}")

        try:
            # Create printer
            printer = QPrinter(QPrinter.HighResolution)
            printer.setPageSize(QPrinter.A4)

            # Show print preview dialog
            preview = QPrintPreviewDialog(printer, self)
            preview.paintRequested.connect(self._print_document)

            # Show dialog
            preview.exec_()

        except Exception as e:
            logger.error(f"Print error: {str(e)}")
            QMessageBox.warning(
                self,
                self.translator.t('print_error_title'),
                self.translator.t('print_error_message', error=str(e))
            )

    def _print_document(self, printer):
        """
        Paint the document for printing.

        Args:
            printer: QPrinter object
        """
        from PyQt5.QtGui import QTextDocument, QTextCursor, QTextTableFormat
        from PyQt5.QtGui import QTextBlockFormat, QTextCharFormat

        # Create document
        document = QTextDocument()
        cursor = QTextCursor(document)

        # Set up formatting
        title_format = QTextBlockFormat()
        title_format.setAlignment(Qt.AlignCenter)
        title_char_format = QTextCharFormat()
        title_char_format.setFontPointSize(16)
        title_char_format.setFontWeight(QFont.Bold)

        # Add title
        cursor.insertBlock(title_format)
        cursor.insertText(self.translator.t('order_details_title'), title_char_format)
        cursor.insertBlock()
        cursor.insertBlock()

        # Create table format
        table_format = QTextTableFormat()
        table_format.setCellPadding(10)
        table_format.setCellSpacing(0)
        table_format.setBorderStyle(QTextTableFormat.BorderStyle_Solid)
        table_format.setBorder(1)

        # Create table with 2 columns
        table = cursor.insertTable(9, 2, table_format)

        # Helper function for table cells
        def add_row(row, label, value):
            cell = table.cellAt(row, 0)
            cursor = cell.firstCursorPosition()
            format = QTextCharFormat()
            format.setFontWeight(QFont.Bold)
            cursor.insertText(label, format)

            cell = table.cellAt(row, 1)
            cursor = cell.firstCursorPosition()
            cursor.insertText(str(value))

        # Add data to table
        add_row(0, self.translator.t('part_name'), self.complete_data.get('name', '-'))
        add_row(1, self.translator.t('car_info'), self.car_value.text())
        add_row(2, self.translator.t('category'), self.complete_data.get('category', '-'))
        add_row(3, self.translator.t('manufacturer'), self.complete_data.get('manufacturer', '-'))
        add_row(4, self.translator.t('material'), self.complete_data.get('material', '-'))
        add_row(5, self.translator.t('quality'), self.complete_data.get('quality', '-'))
        add_row(6, self.translator.t('price'), self.price_value.text())
        add_row(7, self.translator.t('selected_quantity'),
                str(self.complete_data.get('selected_quantity', 1)))

        comments = self.complete_data.get('comments', '-')
        if not comments or comments.strip() == '':
            comments = '-'
        add_row(8, self.translator.t('comments'), comments)

        # Print the document
        document.print_(printer)

    def reset(self):
        """Reset this step's data and UI state."""
        # Call parent reset
        super().reset()

        # Clear data
        self.complete_data = None

        # Reset UI elements
        self.part_name_value.setText("-")
        self.car_value.setText("-")
        self.category_value.setText("-")
        self.manufacturer_value.setText("-")
        self.material_value.setText("-")
        self.quality_value.setText("-")
        self.price_value.setText("-")
        self.quantity_value.setText("-")
        self.comments_value.setText("-")
        self.image_label.setText(self.translator.t('no_image'))

    def can_proceed(self):
        """Check if we can proceed."""
        # This is the final step, so we can always proceed
        return True