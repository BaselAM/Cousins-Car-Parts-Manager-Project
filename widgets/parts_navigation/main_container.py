"""
Main container for the Parts Navigation system.
Orchestrates the hierarchical navigation through car parts.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QStackedWidget,
                            QHBoxLayout, QFrame, QPushButton, QMessageBox,
                            QLayout, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QColor

from .brand_widget import BrandWidget
from .model_widget import ModelWidget
from .year_widget import YearWidget
from .category_widget import CategoryWidget
from .products_widget import ProductsWidget
from .details_widget import DetailsWidget
from .final_widget import FinalWidget
from .navigation import NavigationState
from .ui_utils import SearchBox

from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.container')

class StepIndicator(QFrame):
    """A visual indicator for a step in the navigation process."""

    def __init__(self, number, text, translator):
        super().__init__()
        self.number = number
        self.text = text
        self.translator = translator
        self.is_current = False
        self.is_completed = False
        self.setup_ui()

    def setup_ui(self):
        """Initialize and arrange UI elements."""
        self.setObjectName("stepIndicator")
        self.setMinimumSize(70, 60)
        self.setMaximumSize(100, 70)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Circle with number
        self.circle = QLabel(str(self.number))
        self.circle.setObjectName("stepCircle")
        self.circle.setAlignment(Qt.AlignCenter)
        self.circle.setMinimumSize(30, 30)  # Larger circles
        self.circle.setMaximumSize(30, 30)
        layout.addWidget(self.circle, 0, Qt.AlignCenter)

        # Step text
        self.text_label = QLabel(self.translator.t(self.text))
        self.text_label.setObjectName("stepText")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)

        # Use a slightly larger font size for better readability
        font = self.text_label.font()
        font.setPointSize(9)  # Increased from 8
        self.text_label.setFont(font)

        layout.addWidget(self.text_label, 0, Qt.AlignCenter)

    def set_state(self, is_current=False, is_completed=False):
        """Set the visual state of this indicator."""
        self.is_current = is_current
        self.is_completed = is_completed

        # Set CSS class based on state
        if is_current:
            self.circle.setObjectName("stepCircleCurrent")
            self.text_label.setObjectName("stepTextCurrent")
        elif is_completed:
            self.circle.setObjectName("stepCircleCompleted")
            self.text_label.setObjectName("stepTextCompleted")
        else:
            self.circle.setObjectName("stepCircleFuture")
            self.text_label.setObjectName("stepTextFuture")

        # Force style refresh
        self.circle.style().unpolish(self.circle)
        self.circle.style().polish(self.circle)
        self.text_label.style().unpolish(self.text_label)
        self.text_label.style().polish(self.text_label)

    def update_translations(self):
        """Update the text when language changes."""
        self.text_label.setText(self.translator.t(self.text))


class PartsNavigationContainer(QWidget):
    """Container for the hierarchical parts navigation wizard."""

    def __init__(self, translator, db, parent=None):
        super().__init__(parent)
        self.setObjectName("partsContainer")
        self.translator = translator
        self.db = db

        # Set up navigation state
        self.navigation_state = NavigationState()

        # Configure size policy for responsive behavior
        # Expanding means it will take more space when available
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set a generous minimum size so it starts wider
        self.setMinimumSize(950, 650)

        # Initialize UI
        self.setup_ui()
        self.apply_theme()

    def sizeHint(self):
        """Return a preferred size that's larger than default."""
        # This suggests to the layout system how big this widget would like to be
        return QSize(1000, 700)

    def setup_ui(self):
        """Create the UI components."""
        # Main layout with generous margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)

        # Title
        self.title_label = QLabel(self.translator.t('parts_navigation_title'))
        self.title_label.setObjectName("partsNavigationTitle")

        # Make title larger and more prominent
        font = self.title_label.font()
        font.setPointSize(font.pointSize() + 2)
        font.setBold(True)
        self.title_label.setFont(font)

        main_layout.addWidget(self.title_label, alignment=Qt.AlignCenter)

        # Search bar at the top
        self.setup_search_bar()

        # Content area that will expand with the container
        content_frame = QFrame()
        content_frame.setObjectName("partsContent")
        content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.content_layout = QVBoxLayout(content_frame)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)

        # Set up step indicators
        self.setup_step_indicators()

        # Create stacked widget for steps that expands with container
        self.steps_stack = QStackedWidget()
        self.steps_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_layout.addWidget(self.steps_stack, 1)  # Stretch factor of 1

        # Navigation buttons
        self.setup_navigation_buttons()

        # Add content frame to main layout with stretch factor
        main_layout.addWidget(content_frame, 1)  # Stretch factor of 1

        # Create and connect all the step widgets
        self.create_step_widgets()

    def setup_search_bar(self):
        """Create the search bar at the top."""
        # Use our reusable SearchBox component
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_parts_placeholder',
            label_key='search_parts'
        )
        self.search_box.search_changed.connect(self.on_search_typed)

        # Expand search box horizontally to use available space
        self.search_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Search button
        search_layout = QHBoxLayout()
        search_layout.addWidget(self.search_box, 1)  # Stretch factor for search box

        # Search button
        self.search_button = QPushButton(self.translator.t('search_button'))
        self.search_button.setObjectName("searchButton")
        self.search_button.clicked.connect(self.on_search)
        self.search_button.setMinimumWidth(120)  # Wider button

        search_layout.addWidget(self.search_button)

        self.layout().addLayout(search_layout)

    def setup_step_indicators(self):
        """Create step indicator widgets."""
        self.steps_layout = QHBoxLayout()
        self.steps_layout.setContentsMargins(0, 0, 0, 20)  # Increased bottom margin
        self.steps_layout.setSpacing(12)  # Increased spacing between indicators

        # Define all steps
        step_texts = [
            'brand_step',
            'model_step',
            'year_step',
            'category_step',
            'product_step',
            'details_step',
            'final_step'
        ]

        # Step indicators and connector lines
        self.step_indicators = []
        self.step_lines = []

        # Create step indicators
        for i, text in enumerate(step_texts):
            # Create indicator
            indicator = StepIndicator(i + 1, text, self.translator)
            self.steps_layout.addWidget(indicator, 0, Qt.AlignCenter)
            self.step_indicators.append(indicator)

            # Add connector line if not the last step
            if i < len(step_texts) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setObjectName("stepLineFuture")
                line.setFixedWidth(30)  # Wider connecting lines
                line.setFixedHeight(2)  # Slightly thicker lines
                line.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                self.steps_layout.addWidget(line, 0, Qt.AlignCenter)
                self.step_lines.append(line)

        # Add to content layout
        self.content_layout.addLayout(self.steps_layout)

    def setup_navigation_buttons(self):
        """Create back/next navigation buttons."""
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 15, 0, 0)  # Increased top margin

        # Back button - make wider
        self.back_button = QPushButton(self.translator.t('back_button'))
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(self.on_back_clicked)
        self.back_button.setMinimumWidth(120)  # Wider button

        # Next button - make wider
        self.next_button = QPushButton(self.translator.t('next_button'))
        self.next_button.setObjectName("nextButton")
        self.next_button.clicked.connect(self.on_next_clicked)
        self.next_button.setMinimumWidth(120)  # Wider button

        # Add buttons with stretch
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.next_button)

        self.content_layout.addLayout(buttons_layout)

    def create_step_widgets(self):
        """Create all the navigation step widgets."""
        # Step 1: Brand selection
        self.brand_widget = BrandWidget(self.translator, self.db)
        self.brand_widget.step_completed.connect(self.on_brand_selected)
        self.steps_stack.addWidget(self.brand_widget)

        # Step 2: Model selection
        self.model_widget = ModelWidget(self.translator, self.db)
        self.model_widget.step_completed.connect(self.on_model_selected)
        self.steps_stack.addWidget(self.model_widget)

        # Step 3: Year selection
        self.year_widget = YearWidget(self.translator, self.db)
        self.year_widget.step_completed.connect(self.on_year_selected)
        self.steps_stack.addWidget(self.year_widget)

        # Step 4: Category selection
        self.category_widget = CategoryWidget(self.translator, self.db)
        self.category_widget.step_completed.connect(self.on_category_selected)
        self.steps_stack.addWidget(self.category_widget)

        # Step 5: Product selection
        self.products_widget = ProductsWidget(self.translator, self.db)
        self.products_widget.step_completed.connect(self.on_product_selected)
        self.steps_stack.addWidget(self.products_widget)

        # Step 6: Details selection
        self.details_widget = DetailsWidget(self.translator, self.db)
        self.details_widget.step_completed.connect(self.on_details_selected)
        self.steps_stack.addWidget(self.details_widget)

        # Step 7: Final confirmation
        self.final_widget = FinalWidget(self.translator, self.db)
        self.final_widget.back_requested.connect(self.on_final_back)
        self.steps_stack.addWidget(self.final_widget)

        # Start at the first step
        self.go_to_step(0)

    def get_step_widget(self, step_index):
        """Get the widget for a specific step."""
        if 0 <= step_index < self.steps_stack.count():
            return self.steps_stack.widget(step_index)
        return None

    def go_to_step(self, step_index):
        """Navigate to a specific step in the wizard."""
        if 0 <= step_index < self.steps_stack.count():
            # Validate navigation
            if step_index > 0 and not self.can_go_to_step(step_index):
                logger.warning(f"Cannot go to step {step_index}: missing required data")
                return False

            # Get the current and next widgets
            current_step = self.steps_stack.currentIndex()
            current_widget = self.get_step_widget(current_step)
            next_widget = self.get_step_widget(step_index)

            # Notify widgets about show/hide
            if current_widget:
                current_widget.on_hide()

            if next_widget:
                # Pass data from previous step if moving forward
                if step_index > current_step and current_step >= 0:
                    previous_data = self.navigation_state.get_step_data(current_step)
                    next_widget.set_previous_step_data(previous_data)

                # Show the widget
                next_widget.on_show()

            # Change to the requested step
            self.steps_stack.setCurrentIndex(step_index)

            # Update step indicators
            self.update_step_indicators(step_index)

            # Update button states
            self.update_navigation_buttons()

            logger.info(f"Navigated to step {step_index}")
            return True

        logger.warning(f"Invalid step index: {step_index}")
        return False

    def can_go_to_step(self, step_index):
        """Check if we can navigate to a specific step."""
        # Step 0 (brand) is always accessible
        if step_index == 0:
            return True

        # Step 1 (model) requires brand
        if step_index >= 1 and not self.navigation_state.has_brand():
            return False

        # Step 2 (year) requires model
        if step_index >= 2 and not self.navigation_state.has_model():
            return False

        # Step 3 (category) requires year and car
        if step_index >= 3 and not self.navigation_state.has_car():
            return False

        # Step 4 (product) requires category
        if step_index >= 4 and not self.navigation_state.has_category():
            return False

        # Step 5 (details) requires product
        if step_index >= 5 and not self.navigation_state.has_product():
            return False

        # Step 6 (final) requires details
        if step_index >= 6 and not self.navigation_state.has_details():
            return False

        return True

    def update_step_indicators(self, current_step):
        """Update the appearance of step indicators."""
        for i, indicator in enumerate(self.step_indicators):
            is_completed = i < current_step
            is_current = i == current_step
            indicator.set_state(is_current, is_completed)

        # Update the connector lines
        for i, line in enumerate(self.step_lines):
            if i < current_step:
                # Completed connector
                line.setObjectName("stepLineCompleted")
            else:
                # Future connector
                line.setObjectName("stepLineFuture")

            # Force style refresh
            line.style().unpolish(line)
            line.style().polish(line)

    def update_navigation_buttons(self):
        """Update the state of the navigation buttons."""
        current_step = self.steps_stack.currentIndex()

        # Back button is enabled except on first step
        self.back_button.setEnabled(current_step > 0)

        # Next button is enabled if we can go to next step
        next_enabled = self.can_go_to_next_step(current_step)
        self.next_button.setEnabled(next_enabled)

        # Change next button text for final step
        if current_step == 5:  # Details step (before final)
            self.next_button.setText(self.translator.t('finish_button'))
        elif current_step == 6:  # Final step
            self.next_button.setText(self.translator.t('done_button'))
        else:
            self.next_button.setText(self.translator.t('next_button'))

    def can_go_to_next_step(self, current_step):
        """Check if we can go to the next step."""
        # Get the current widget
        current_widget = self.get_step_widget(current_step)

        # Check if the widget says we can proceed
        if current_widget and hasattr(current_widget, 'can_proceed'):
            return current_widget.can_proceed()

        return False

    def on_back_clicked(self):
        """Handle back button click."""
        current_step = self.steps_stack.currentIndex()
        if current_step > 0:
            self.go_to_step(current_step - 1)

    def on_next_clicked(self):
        """Handle next button click."""
        current_step = self.steps_stack.currentIndex()

        # If on final step, reset and start over
        if current_step == 6:  # Final step
            self.reset_navigation()
            return

        # Otherwise try to go to next step
        if self.can_go_to_next_step(current_step):
            self.go_to_step(current_step + 1)

    def on_brand_selected(self, brand_data):
        """Handle brand selection."""
        logger.info(f"Brand selected: {brand_data}")
        self.navigation_state.brand = brand_data
        self.update_navigation_buttons()

    def on_model_selected(self, model_data):
        """Handle model selection."""
        logger.info(f"Model selected: {model_data}")
        self.navigation_state.model = model_data
        self.update_navigation_buttons()

    def on_year_selected(self, data):
        """Handle year selection."""
        # Data contains both year and constructed car object
        if not data or 'car' not in data:
            logger.warning("Invalid year selection data")
            return

        logger.info(f"Year selected: {data.get('year', '')}")
        self.navigation_state.year = data
        self.navigation_state.car = data['car']
        self.update_navigation_buttons()

    def on_category_selected(self, category_data):
        """Handle category selection."""
        logger.info(f"Category selected: {category_data}")
        self.navigation_state.category = category_data
        self.update_navigation_buttons()

    def on_product_selected(self, product_data):
        """Handle product selection."""
        logger.info(f"Product selected: {product_data}")
        self.navigation_state.product = product_data
        self.update_navigation_buttons()

    def on_details_selected(self, details_data):
        """Handle details selection."""
        logger.info(f"Details selected: {details_data}")
        self.navigation_state.details = details_data
        self.update_navigation_buttons()

    def on_final_back(self):
        """Handle back button from final widget."""
        self.go_to_step(5)  # Go back to details step

    def reset_navigation(self):
        """Reset the navigation to the beginning."""
        # Reset navigation state
        self.navigation_state.reset()

        # Reset all widgets
        for i in range(self.steps_stack.count()):
            widget = self.get_step_widget(i)
            if widget and hasattr(widget, 'reset'):
                widget.reset()

        # Go back to first step
        self.go_to_step(0)

        # Clear search
        self.search_box.clear()

        logger.info("Navigation reset to beginning")

    def on_search_typed(self, search_text):
        """Handle typing in the search box."""
        # Enable search button only if there's text
        self.search_button.setEnabled(bool(search_text.strip()))

    def on_search(self):
        """Handle search function."""
        search_text = self.search_box.get_text().strip()
        if not search_text:
            return

        logger.info(f"Searching for: {search_text}")

        try:
            # Search parts by text
            results = self.db.search_parts(search_text)

            if not results:
                QMessageBox.information(
                    self,
                    self.translator.t('search_results'),
                    self.translator.t('no_results_found')
                )
                return

            if len(results) == 1:
                # Single result, show it directly
                self.show_search_result(results[0])
            else:
                # Multiple results, jump to product selection with filtered results
                self.navigation_state.reset()

                # Go to products widget and show search results
                self.go_to_step(4)  # Jump to product selection
                self.products_widget.show_search_results(results)

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            QMessageBox.warning(
                self,
                self.translator.t('search_error'),
                str(e)
            )

    def show_search_result(self, part):
        """Display a single search result."""
        # Construct data needed for display
        product_data = {
            'name': part.get('product_name', ''),
            'category': part.get('category', ''),
            'price': part.get('price', 0),
            'quantity': part.get('quantity', 0),
            'id': part.get('parcode', 0)
        }

        # Get compatible car info
        compatible_brands = part.get('compatible_brands', '').split(',')
        compatible_models = part.get('compatible_models', '').split(',')
        model_years = part.get('model_years', '').split(',')

        brand = compatible_brands[0].strip() if compatible_brands else ''
        model = compatible_models[0].strip() if compatible_models else ''
        year = model_years[0].strip() if model_years else ''

        car_data = {
            'brand': brand,
            'model': model,
            'year': year
        }

        # Reset navigation state
        self.navigation_state.reset()

        # Set product data
        self.navigation_state.product = product_data
        self.navigation_state.car = car_data

        # Jump to details step
        self.go_to_step(5)  # Go to details step
        self.details_widget.set_product(product_data)

    def apply_theme(self):
        """Apply theme colors to UI components."""
        # Get theme colors
        bg_color = get_color('background')
        card_bg = get_color('card_bg')
        text_color = get_color('text')
        highlight = get_color('highlight')
        border_color = get_color('border')

        # Apply styles
        self.setStyleSheet(f"""
            #partsNavigationTitle {{
                color: {text_color};
                font-size: 26px;  /* Increased from 24px */
                font-weight: bold;
                margin-bottom: 20px;  /* Increased from 15px */
            }}
            
            #partsContent {{
                background-color: {card_bg};
                border-radius: 12px;  /* Increased from 10px */
                border: 1px solid {border_color};
                padding: 25px;  /* Increased from 20px */
            }}
            
            #searchButton {{
                background-color: {highlight};
                color: white;
                border: none;
                border-radius: 6px;  /* Increased from 5px */
                padding: 10px 20px;  /* Increased from 8px 15px */
                font-size: 15px;  /* Increased from 14px */
                font-weight: bold;
            }}
            
            #searchButton:hover {{
                background-color: {QColor(highlight).darker(110).name()};
            }}
            
            #searchButton:disabled {{
                background-color: {QColor(highlight).darker(140).name()};
                color: {QColor(card_bg).darker(110).name()};
            }}
            
            /* Step indicators */
            #stepCircleCompleted {{
                background-color: {highlight};
                color: white;
                border-radius: 15px;  /* Increased from 12px */
                font-weight: bold;
                font-size: 14px;  /* Increased from 12px */
            }}
            
            #stepTextCompleted {{
                color: {highlight};
                font-weight: bold;
                font-size: 9px;  /* Increased from 8px */
            }}
            
            #stepCircleCurrent {{
                background-color: {highlight};
                color: white;
                border-radius: 15px;  /* Increased from 12px */
                font-weight: bold;
                border: 2px solid white;
                font-size: 14px;  /* Increased from 12px */
            }}
            
            #stepTextCurrent {{
                color: {highlight};
                font-weight: bold;
                text-decoration: underline;
                font-size: 9px;  /* Increased from 8px */
            }}
            
            #stepCircleFuture {{
                background-color: {get_color('button')};
                color: {text_color};
                border-radius: 15px;  /* Increased from 12px */
                font-size: 14px;  /* Increased from 12px */
            }}
            
            #stepTextFuture {{
                color: {text_color};
                font-size: 9px;  /* Increased from 8px */
            }}
            
            #stepLineCompleted {{
                background-color: {highlight};
            }}
            
            #stepLineFuture {{
                background-color: {border_color};
            }}
            
            /* Navigation buttons */
            #backButton {{
                background-color: {get_color('button')};
                color: {text_color};
                border: none;
                border-radius: 20px;
                padding: 12px 25px;  /* Increased from 10px 20px */
                font-size: 15px;  /* Increased from 14px */
                min-width: 120px;  /* Increased from 100px */
                max-width: 170px;  /* Increased from 150px */
            }}
            
            #backButton:hover {{
                background-color: {get_color('button_hover')};
            }}
            
            #backButton:disabled {{
                background-color: {get_color('button_disabled')};
                color: {get_color('text_disabled')};
            }}
            
            #nextButton {{
                background-color: {highlight};
                color: white;
                border: none;
                border-radius: 20px;
                padding: 12px 25px;  /* Increased from 10px 20px */
                font-size: 15px;  /* Increased from 14px */
                font-weight: bold;
                min-width: 120px;  /* Increased from 100px */
                max-width: 170px;  /* Increased from 150px */
            }}
            
            #nextButton:hover {{
                background-color: {QColor(highlight).darker(110).name()};
            }}
            
            #nextButton:disabled {{
                background-color: {QColor(highlight).darker(150).name()};
                color: {QColor(card_bg).darker(120).name()};
            }}
        """)

        # Apply theme to search box
        self.search_box.apply_theme()

    def update_translations(self):
        """Update all text when language changes."""
        # Update title
        self.title_label.setText(self.translator.t('parts_navigation_title'))

        # Update search
        self.search_box.update_translations()
        self.search_button.setText(self.translator.t('search_button'))

        # Update step indicators
        for indicator in self.step_indicators:
            indicator.update_translations()

        # Update navigation buttons
        self.back_button.setText(self.translator.t('back_button'))

        # Update next button based on current step
        current_step = self.steps_stack.currentIndex()
        if current_step == 5:  # Details step (before final)
            self.next_button.setText(self.translator.t('finish_button'))
        elif current_step == 6:  # Final step
            self.next_button.setText(self.translator.t('done_button'))
        else:
            self.next_button.setText(self.translator.t('next_button'))

        # Update each widget if they've been created
        for i in range(self.steps_stack.count()):
            widget = self.get_step_widget(i)
            if widget and hasattr(widget, 'update_translations'):
                widget.update_translations()