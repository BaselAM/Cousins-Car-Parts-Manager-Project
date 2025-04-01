"""
Final display widget for the parts navigation system.
The seventh and last step in the parts navigation hierarchy.
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QHBoxLayout,
                             QGridLayout, QPushButton, QScrollArea, QMessageBox,
                             QListWidget, QListWidgetItem, QSplitter, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QColor
from pathlib import Path

from .base_step_widget import BaseStepWidget
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.final')

class FinalWidget(BaseStepWidget):
    """
    Seventh and final step in the parts navigation - showing complete part details
    and allowing purchase or further actions
    """
    # Signal for requesting to go back
    back_requested = pyqtSignal()

    def __init__(self, translator, db, parent=None):
        super().__init__(translator, db, parent)

        # Set up data
        self.current_part = None
        self.similar_parts = []

    def setup_ui(self):
        """Initialize and arrange UI elements"""
        # Call parent setup first (but we'll override the main layout)
        super().setup_ui()

        # Clear the default layout and set up a new one
        # First, remove all existing widgets
        for i in reversed(range(self.main_layout.count())):
            item = self.main_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                # Remove items from nested layout
                layout = item.layout()
                for j in reversed(range(layout.count())):
                    nested_item = layout.itemAt(j)
                    if nested_item.widget():
                        nested_item.widget().deleteLater()

        # Clear the main layout
        while self.main_layout.count():
            item = self.main_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Set new content margins
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Title
        self.title = QLabel(self.translator.t('part_details'))
        self.title.setObjectName("finalTitle")
        self.title.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title)

        # Splitter for main content and similar parts
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(8)
        splitter.setChildrenCollapsible(False)

        # Main details container
        details_container = QFrame()
        details_container.setObjectName("detailsContainer")
        details_layout = QHBoxLayout(details_container)
        details_layout.setContentsMargins(20, 20, 20, 20)
        details_layout.setSpacing(20)

        # Left side - Image & actions
        left_container = QFrame()
        left_container.setObjectName("leftContainer")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(10, 10, 10, 10)
        left_layout.setSpacing(15)

        # Part image
        self.image_frame = QFrame()
        self.image_frame.setObjectName("imageFrame")
        self.image_frame.setMinimumSize(250, 250)
        self.image_frame.setMaximumSize(300, 300)

        image_layout = QVBoxLayout(self.image_frame)
        image_layout.setContentsMargins(10, 10, 10, 10)

        self.image_label = QLabel()
        self.image_label.setObjectName("partImage")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(True)
        self.image_label.setMinimumSize(220, 220)
        self.image_label.setMaximumSize(280, 280)

        # Default image
        default_img = QPixmap("resources/default_part.png")
        if not default_img.isNull():
            self.image_label.setPixmap(default_img)
        else:
            self.image_label.setText(self.translator.t('no_image'))

        image_layout.addWidget(self.image_label, 0, Qt.AlignCenter)
        left_layout.addWidget(self.image_frame, 0, Qt.AlignCenter)

        # Action buttons
        action_layout = QVBoxLayout()
        action_layout.setContentsMargins(0, 10, 0, 0)
        action_layout.setSpacing(10)

        self.add_to_cart_button = QPushButton(self.translator.t('add_to_cart'))
        self.add_to_cart_button.setObjectName("primaryButton")
        self.add_to_cart_button.clicked.connect(self.on_add_to_cart)

        self.print_button = QPushButton(self.translator.t('print_details'))
        self.print_button.setObjectName("secondaryButton")
        self.print_button.clicked.connect(self.on_print)

        action_layout.addWidget(self.add_to_cart_button)
        action_layout.addWidget(self.print_button)

        left_layout.addLayout(action_layout)
        details_layout.addWidget(left_container)

        # Right side - Details grid
        right_container = QScrollArea()
        right_container.setObjectName("rightContainer")
        right_container.setWidgetResizable(True)
        right_container.setFrameShape(QFrame.NoFrame)

        details_widget = QWidget()
        details_widget.setObjectName("detailsWidget")
        details_grid = QGridLayout(details_widget)
        details_grid.setContentsMargins(10, 10, 10, 10)
        details_grid.setVerticalSpacing(15)
        details_grid.setHorizontalSpacing(15)

        # Row 0 - Part name
        self.part_name_label = QLabel(self.translator.t('part_name'))
        self.part_name_label.setObjectName("detailLabel")
        self.part_name_value = QLabel("-")
        self.part_name_value.setObjectName("detailValue")

        details_grid.addWidget(self.part_name_label, 0, 0)
        details_grid.addWidget(self.part_name_value, 0, 1)

        # Row 1 - Car info
        self.car_label = QLabel(self.translator.t('car_info'))
        self.car_label.setObjectName("detailLabel")
        self.car_value = QLabel("-")
        self.car_value.setObjectName("detailValue")

        details_grid.addWidget(self.car_label, 1, 0)
        details_grid.addWidget(self.car_value, 1, 1)

        # Row 2 - Category
        self.category_label = QLabel(self.translator.t('category'))
        self.category_label.setObjectName("detailLabel")
        self.category_value = QLabel("-")
        self.category_value.setObjectName("detailValue")

        details_grid.addWidget(self.category_label, 2, 0)
        details_grid.addWidget(self.category_value, 2, 1)

        # Row 3 - Manufacturer
        self.manufacturer_label = QLabel(self.translator.t('manufacturer'))
        self.manufacturer_label.setObjectName("detailLabel")
        self.manufacturer_value = QLabel("-")
        self.manufacturer_value.setObjectName("detailValue")

        details_grid.addWidget(self.manufacturer_label, 3, 0)
        details_grid.addWidget(self.manufacturer_value, 3, 1)

        # Row 4 - Material
        self.material_label = QLabel(self.translator.t('material'))
        self.material_label.setObjectName("detailLabel")
        self.material_value = QLabel("-")
        self.material_value.setObjectName("detailValue")

        details_grid.addWidget(self.material_label, 4, 0)
        details_grid.addWidget(self.material_value, 4, 1)

        # Row 5 - Quality
        self.quality_label = QLabel(self.translator.t('quality'))
        self.quality_label.setObjectName("detailLabel")
        self.quality_value = QLabel("-")
        self.quality_value.setObjectName("detailValue")

        details_grid.addWidget(self.quality_label, 5, 0)
        details_grid.addWidget(self.quality_value, 5, 1)

        # Row 6 - Price
        self.price_label = QLabel(self.translator.t('price'))
        self.price_label.setObjectName("detailLabel")
        self.price_value = QLabel("-")
        self.price_value.setObjectName("priceValue")

        details_grid.addWidget(self.price_label, 6, 0)
        details_grid.addWidget(self.price_value, 6, 1)

        # Row 7 - Quantity
        self.quantity_label = QLabel(self.translator.t('quantity'))
        self.quantity_label.setObjectName("detailLabel")
        self.quantity_value = QLabel("-")
        self.quantity_value.setObjectName("detailValue")

        details_grid.addWidget(self.quantity_label, 7, 0)
        details_grid.addWidget(self.quantity_value, 7, 1)

        # Row 8 - Selected quantity
        self.selected_quantity_label = QLabel(self.translator.t('selected_quantity'))
        self.selected_quantity_label.setObjectName("detailLabel")
        self.selected_quantity_value = QLabel("-")
        self.selected_quantity_value.setObjectName("detailValue")

        details_grid.addWidget(self.selected_quantity_label, 8, 0)
        details_grid.addWidget(self.selected_quantity_value, 8, 1)

        # Row 9 - Comments
        self.comments_label = QLabel(self.translator.t('comments'))
        self.comments_label.setObjectName("detailLabel")
        self.comments_value = QLabel("-")
        self.comments_value.setObjectName("detailValue")
        self.comments_value.setWordWrap(True)

        details_grid.addWidget(self.comments_label, 9, 0, Qt.AlignTop)
        details_grid.addWidget(self.comments_value, 9, 1)

        # Set column stretch
        details_grid.setColumnStretch(0, 1)
        details_grid.setColumnStretch(1, 2)

        right_container.setWidget(details_widget)
        details_layout.addWidget(right_container, 1)  # Give more space to details

        # Add details container to splitter
        splitter.addWidget(details_container)

        # Similar parts container
        similar_container = QFrame()
        similar_container.setObjectName("similarContainer")
        similar_layout = QVBoxLayout(similar_container)
        similar_layout.setContentsMargins(20, 20, 20, 20)
        similar_layout.setSpacing(10)

        # Similar parts title
        similar_title = QLabel(self.translator.t('similar_parts'))
        similar_title.setObjectName("similarTitle")
        similar_title.setAlignment(Qt.AlignCenter)
        similar_layout.addWidget(similar_title)

        # Similar parts list
        self.similar_list = QListWidget()
        self.similar_list.setObjectName("similarList")
        self.similar_list.setMinimumHeight(120)  # Keep it compact
        self.similar_list.setMaximumHeight(180)
        self.similar_list.setAlternatingRowColors(True)
        self.similar_list.setSelectionMode(QListWidget.SingleSelection)
        self.similar_list.itemClicked.connect(self.on_similar_part_clicked)
        similar_layout.addWidget(self.similar_list)

        # Add similar container to splitter
        splitter.addWidget(similar_container)

        # Set splitter sizes
        splitter.setSizes([700, 200])  # More space for details, less for similar parts

        # Add splitter to main layout
        self.main_layout.addWidget(splitter)

        # Back button at bottom
        back_layout = QHBoxLayout()
        back_layout.setContentsMargins(0, 10, 0, 0)

        self.back_button = QPushButton(self.translator.t('back_button'))
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(self.on_back_clicked)

        back_layout.addWidget(self.back_button)
        back_layout.addStretch(1)

        self.main_layout.addLayout(back_layout)

    def apply_theme(self):
        """Apply current theme"""
        # Call parent apply_theme first for basic parts
        super().apply_theme()

        # Apply theme to our specific components
        bg_color = get_color('background')
        card_bg = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        highlight = get_color('highlight')

        # Update title style
        self.title.setStyleSheet(f"""
            #finalTitle {{
                color: {text_color};
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
        """)

        # Apply styles to containers and details
        for widget_id in ["detailsContainer", "similarContainer"]:
            widget = self.findChild(QFrame, widget_id)
            if widget:
                widget.setStyleSheet(f"""
                    #{widget_id} {{
                        background-color: {card_bg};
                        border: 1px solid {border_color};
                        border-radius: 10px;
                    }}
                """)

        # Left side container
        self.image_frame.setStyleSheet(f"""
            #imageFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
        """)

        # Detail labels and values
        detail_style = f"""
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
        """
        self.setStyleSheet(self.styleSheet() + detail_style)

        # Buttons
        button_style = f"""
            #primaryButton {{
                background-color: {highlight};
                color: white;
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 15px;
                font-weight: bold;
                min-width: 150px;
            }}
            
            #primaryButton:hover {{
                background-color: {QColor(highlight).darker(110).name()};
            }}
            
            #secondaryButton {{
                background-color: {get_color('button')};
                color: {text_color};
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 15px;
                min-width: 150px;
            }}
            
            #secondaryButton:hover {{
                background-color: {get_color('button_hover')};
            }}
            
            #backButton {{
                background-color: {get_color('button')};
                color: {text_color};
                border: none;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 15px;
                min-width: 120px;
            }}
            
            #backButton:hover {{
                background-color: {get_color('button_hover')};
            }}
        """
        self.setStyleSheet(self.styleSheet() + button_style)

        # Similar parts title and list
        similar_style = f"""
            #similarTitle {{
                color: {highlight};
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
            }}
            
            #similarList {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                font-size: 14px;
                alternate-background-color: {QColor(bg_color).darker(105).name()};
            }}
            
            #similarList::item:selected {{
                background-color: {highlight};
                color: white;
            }}
            
            QSplitter::handle {{
                background-color: {border_color};
            }}
            
            QSplitter::handle:horizontal {{
                width: 8px;
            }}
            
            QSplitter::handle:vertical {{
                height: 8px;
            }}
        """
        self.setStyleSheet(self.styleSheet() + similar_style)

    def update_translations(self):
        """Update all translatable text"""
        # Update our own texts
        self.title.setText(self.translator.t('part_details'))

        # Update details labels
        self.part_name_label.setText(self.translator.t('part_name'))
        self.car_label.setText(self.translator.t('car_info'))
        self.category_label.setText(self.translator.t('category'))
        self.manufacturer_label.setText(self.translator.t('manufacturer'))
        self.material_label.setText(self.translator.t('material'))
        self.quality_label.setText(self.translator.t('quality'))
        self.price_label.setText(self.translator.t('price'))
        self.quantity_label.setText(self.translator.t('quantity'))
        self.selected_quantity_label.setText(self.translator.t('selected_quantity'))
        self.comments_label.setText(self.translator.t('comments'))

        # Update buttons
        self.add_to_cart_button.setText(self.translator.t('add_to_cart'))
        self.print_button.setText(self.translator.t('print_details'))
        self.back_button.setText(self.translator.t('back_button'))

        # Update similar parts section
        title_label = self.findChild(QLabel, "similarTitle")
        if title_label:
            title_label.setText(self.translator.t('similar_parts'))

        # Refresh part data if available
        if self.current_part:
            self.set_complete_data(self.current_part)

    def on_show(self):
        """Called when this step is shown"""
        # Nothing to do here - everything is set up when set_complete_data is called
        pass

    def set_complete_data(self, part_data):
        """Set all the part data and update the display"""
        if not part_data:
            return

        self.current_part = part_data

        # Update part details
        self.part_name_value.setText(part_data.get('name', '-'))
        self.car_value.setText(
            f"{part_data.get('make', '-')} {part_data.get('model', '-')} ({part_data.get('year', '-')})")
        self.category_value.setText(part_data.get('category', '-'))
        self.manufacturer_value.setText(part_data.get('manufacturer', '-'))
        self.material_value.setText(part_data.get('material', '-'))
        self.quality_value.setText(part_data.get('quality', '-'))

        # Format price
        price = part_data.get('price', 0)
        currency = self.translator.t('currency_symbol')
        self.price_value.setText(f"{currency} {price:.2f}")

        # Set quantities
        self.quantity_value.setText(str(part_data.get('quantity', 0)))
        self.selected_quantity_value.setText(str(part_data.get('selected_quantity', 1)))

        # Set comments
        comments = part_data.get('comments', '-')
        if not comments or comments.strip() == '':
            comments = '-'
        self.comments_value.setText(comments)

        # Try to load part image
        self.load_part_image(part_data)

        # Load similar parts
        self.load_similar_parts(part_data)

        # Store as step data
        self.step_data = part_data

    def set_previous_step_data(self, data):
        """Set data from previous step"""
        # We need the product data and details data to build complete data
        if not hasattr(self, 'product_data'):
            self.product_data = {}

        if data:
            # Details data should be the latest
            details_data = data

            # We need to get product data from previous steps
            if self.current_part:
                product_data = self.current_part

                # Create complete part data for final display
                complete_data = {
                    'make': product_data.get('make', '-'),
                    'model': product_data.get('model', '-'),
                    'year': product_data.get('year', '-'),
                    'category': product_data.get('category', '-'),
                    'name': product_data.get('name', '-'),
                    'manufacturer': details_data.get('manufacturer', '-'),
                    'material': details_data.get('material', '-'),
                    'quality': details_data.get('quality', '-'),
                    'price': product_data.get('price', 0),
                    'quantity': product_data.get('quantity', 0),
                    'selected_quantity': details_data.get('quantity', 1),
                    'comments': details_data.get('comments', '-')
                }

                self.set_complete_data(complete_data)

    def load_part_image(self, part_data):
        """Load the part image from the given data"""
        try:
            # First, try to load from a direct image path if available
            image_path = part_data.get('image_path', '')

            if image_path and Path(image_path).exists():
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    self.image_label.setPixmap(pixmap.scaled(
                        self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    return

            # Try to load a category-based image
            category = part_data.get('category', '').lower().replace(' ', '_')
            category_img_path = f"resources/parts/{category}.png"
            if Path(category_img_path).exists():
                pixmap = QPixmap(category_img_path)
                if not pixmap.isNull():
                    self.image_label.setPixmap(pixmap.scaled(
                        self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    return

            # If all attempts failed, load default image
            default_img = QPixmap("resources/default_part.png")
            if not default_img.isNull():
                self.image_label.setPixmap(default_img.scaled(
                    self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                self.image_label.setText(self.translator.t('no_image'))

        except Exception as e:
            logger.error(f"Error loading part image: {str(e)}")
            self.image_label.setText(self.translator.t('image_error'))

    def load_similar_parts(self, part_data):
        """Load similar parts for the current part"""
        try:
            # Clear existing items
            self.similar_list.clear()
            self.similar_parts = []

            if not part_data:
                return

            # Get parts from database that match the category
            category = part_data.get('category', '')
            if not category:
                return

            # Get all parts
            all_parts = self.db.get_all_parts()

            # Filter parts by category
            similar_parts = []
            for part in all_parts:
                if isinstance(part, dict) and part.get('category') == category:
                    # Skip the current part
                    if part.get('product_name') == part_data.get('name'):
                        continue

                    similar_parts.append({
                        'id': part.get('parcode', 0),
                        'name': part.get('product_name', ''),
                        'category': part.get('category', ''),
                        'price': part.get('price', 0),
                        'quantity': part.get('quantity', 0),
                        'manufacturer': part.get('manufacturer', '')
                    })

            # Limit to a reasonable number
            self.similar_parts = similar_parts[:10]

            # If no similar parts found, add some test data
            if not self.similar_parts:
                self.add_test_similar_parts(part_data)

            # Populate the list
            for part in self.similar_parts:
                # Create an item for the part
                item = QListWidgetItem()

                # Format the display text
                name = part.get('name', '')
                manufacturer = part.get('manufacturer', '')
                price = part.get('price', 0)
                currency = self.translator.t('currency_symbol')

                display_text = f"{name}"
                if manufacturer:
                    display_text += f" - {manufacturer}"
                display_text += f" ({currency} {price:.2f})"

                item.setText(display_text)
                item.setData(Qt.UserRole, part)

                self.similar_list.addItem(item)

            logger.info(f"Loaded {len(self.similar_parts)} similar parts")

        except Exception as e:
            logger.error(f"Error loading similar parts: {str(e)}")
            self.similar_parts = []

    def add_test_similar_parts(self, part_data):
        """Add test similar parts when none are found in the database"""
        category = part_data.get('category', '')

        # Create some test similar parts
        for i in range(1, 6):
            similar_part = {
                'id': 20000 + i,
                'name': f"Test {category} Part {i}",
                'category': category,
                'price': part_data.get('price', 0) * (0.8 + (i * 0.1)),  # Vary the price
                'quantity': max(1, part_data.get('quantity', 10) - i),
                'manufacturer': f"Manufacturer {i}"
            }
            self.similar_parts.append(similar_part)

    def on_similar_part_clicked(self, item):
        """Handle click on a similar part in the list"""
        part_data = item.data(Qt.UserRole)
        if part_data:
            # Show a dialog asking if the user wants to switch
            response = QMessageBox.question(
                self,
                self.translator.t('switch_part'),
                self.translator.t('switch_part_confirm').format(part=part_data.get('name', '')),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No  # Default is No
            )

            if response == QMessageBox.Yes:
                # Switch to the selected part
                # In a real implementation, this would load the full part details
                # For now, just use what we have and update the display
                car_data = {
                    'make': self.current_part.get('make', '-'),
                    'model': self.current_part.get('model', '-'),
                    'year': self.current_part.get('year', '-')
                }

                complete_data = {
                    'name': part_data.get('name', ''),
                    'make': car_data.get('make', ''),
                    'model': car_data.get('model', ''),
                    'year': car_data.get('year', ''),
                    'category': part_data.get('category', ''),
                    'manufacturer': part_data.get('manufacturer', ''),
                    'material': self.current_part.get('material', ''),  # Use current values
                    'quality': self.current_part.get('quality', ''),
                    'price': part_data.get('price', 0),
                    'quantity': part_data.get('quantity', 0),
                    'selected_quantity': 1,
                    'comments': ''
                }

                self.set_complete_data(complete_data)

    def on_add_to_cart(self):
        """Handle add to cart button click"""
        if not self.current_part:
            return

        # Get the selected quantity
        quantity = int(self.selected_quantity_value.text() or 1)

        # In a real implementation, this would call a method to add to cart
        # For now, just show a message
        QMessageBox.information(
            self,
            self.translator.t('added_to_cart_title'),
            self.translator.t('added_to_cart_message').format(
                quantity=quantity,
                name=self.current_part.get('name', ''),
                price=float(self.current_part.get('price', 0)) * quantity
            )
        )

        logger.info(f"Added to cart: {quantity} x {self.current_part.get('name', '')}")

    def on_print(self):
        """Handle print button click"""
        if not self.current_part:
            return

        # In a real implementation, this would open a print dialog
        # For now, just show a message
        QMessageBox.information(
            self,
            self.translator.t('print_title'),
            self.translator.t('print_message').format(
                name=self.current_part.get('name', '')
            )
        )

        logger.info(f"Printing details for: {self.current_part.get('name', '')}")

    def on_back_clicked(self):
        """Handle back button click"""
        # Emit signal to go back to previous step
        self.back_requested.emit()

    def reset(self):
        """Reset this step's data"""
        super().reset()
        self.current_part = None
        self.similar_parts = []
        self.similar_list.clear()

        # Reset all fields to default values
        self.part_name_value.setText("-")
        self.car_value.setText("-")
        self.category_value.setText("-")
        self.manufacturer_value.setText("-")
        self.material_value.setText("-")
        self.quality_value.setText("-")
        self.price_value.setText("-")
        self.quantity_value.setText("-")
        self.selected_quantity_value.setText("-")
        self.comments_value.setText("-")

        # Reset image to default
        default_img = QPixmap("resources/default_part.png")
        if not default_img.isNull():
            self.image_label.setPixmap(default_img)
        else:
            self.image_label.setText(self.translator.t('no_image'))

    def can_proceed(self):
        """Check if user can proceed to next step"""
        # This is the final step, so there is no "next" step
        return False