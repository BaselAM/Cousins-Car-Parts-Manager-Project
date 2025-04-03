"""
Premium parts navigation container with elegant iOS-inspired design.
Provides a sophisticated user experience with refined animations and styling.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QStackedWidget,
                            QHBoxLayout, QFrame, QPushButton, QMessageBox,
                            QSizePolicy, QGraphicsOpacityEffect)
from PyQt5.QtCore import (Qt, pyqtSignal, QSize, QPropertyAnimation,
                         QEasingCurve, QParallelAnimationGroup,QTimer,)
from PyQt5.QtGui import QFont, QColor

# Import premium components
from .premium_steps_panel import PremiumStepsPanel
from .premium_styling import generate_premium_stylesheet, load_premium_fonts
from widgets.parts_navigation.ui_utils import SearchBox

# Import the step widgets
from widgets.parts_navigation.brand_widget import BrandWidget
from widgets.parts_navigation.model_widget import ModelWidget
from widgets.parts_navigation.year_widget import YearWidget
from widgets.parts_navigation.category_widget import CategoryWidget
from widgets.parts_navigation.products_widget import ProductsWidget
from widgets.parts_navigation.details_widget import DetailsWidget
from widgets.parts_navigation.final_widget import FinalWidget
from widgets.parts_navigation.navigation import NavigationState

from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.container')

class PartsNavigationContainer(QWidget):
    """Container for the hierarchical parts navigation with premium styling."""

    def __init__(self, translator, db, parent=None):
        super().__init__(parent)
        self.setObjectName("partsContainer")
        self.translator = translator
        self.db = db

        # Set up navigation state
        self.navigation_state = NavigationState()

        # Configure size policy for responsive behavior
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

        # Remove minimum size entirely to allow full adaptability
        self.setMinimumSize(0, 0)

        # Load premium fonts
        load_premium_fonts()

        # Initialize UI with premium styling
        self.setup_ui()
        self.apply_premium_theme()

        # Animation properties
        self._current_animation = None

    def sizeHint(self):
        """Return the preferred size with premium proportions."""
        return QSize(800, 600)  # Larger default size for premium experience

    def setup_ui(self):
        """Create a premium UI with refined spacing and elements."""
        # Main layout with elegant spacing
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)  # More breathing room
        main_layout.setSpacing(15)  # Refined spacing

        # Title with premium typography
        self.title_label = QLabel(self.translator.t('parts_navigation_title'))
        self.title_label.setObjectName("partsNavigationTitle")
        self.title_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Premium font styling
        font = QFont("SF Pro Display", 18)
        font.setBold(True)
        font.setLetterSpacing(QFont.AbsoluteSpacing, -0.5)  # Apple-style negative tracking
        self.title_label.setFont(font)

        main_layout.addWidget(self.title_label, 0, Qt.AlignCenter)

        # Subtle separator with refined appearance
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("titleSeparator")
        separator.setMaximumHeight(1)
        main_layout.addWidget(separator)

        # Search bar with premium styling
        self.setup_premium_search()

        # Content area with premium styling
        content_frame = QFrame()
        content_frame.setObjectName("partsContent")
        content_frame.setSizePolicy(QSizePolicy.Expanding,
                                    QSizePolicy.Expanding)  # IMPROVED: Use Expanding for both dimensions

        # Set minimum size to ensure enough space
        content_frame.setMinimumWidth(700)  # IMPROVED: Ensure minimum width
        content_frame.setMinimumHeight(500)  # IMPROVED: Ensure minimum height

        self.content_layout = QVBoxLayout(content_frame)
        self.content_layout.setContentsMargins(15, 15, 15, 15)  # Generous internal padding
        self.content_layout.setSpacing(15)  # Elegant spacing

        # Premium step indicators panel in a dedicated container
        self.steps_panel_container = QFrame()
        self.steps_panel_container.setObjectName("stepsPanelContainer")
        self.steps_panel_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        # Use a layout for the container
        steps_container_layout = QVBoxLayout(self.steps_panel_container)
        steps_container_layout.setContentsMargins(0, 0, 0, 10)
        steps_container_layout.setSpacing(0)

        # Create and add the steps panel
        self.steps_panel = PremiumStepsPanel(self.translator)
        self.steps_panel.step_clicked.connect(self.on_step_indicator_clicked)
        steps_container_layout.addWidget(self.steps_panel)

        # Add the container to the main content layout
        self.content_layout.addWidget(self.steps_panel_container)

        # Step indicators and connectors references for API compatibility
        self.step_indicators = self.steps_panel.step_indicators
        self.step_connectors = self.steps_panel.step_connectors

        # Create stacked widget for steps with fade transition effect
        self.steps_stack = QStackedWidget()
        self.steps_stack.setObjectName("stepsStack")
        self.steps_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # IMPROVED: Use Expanding policy

        # IMPROVED: Set minimum size for the stack to ensure contents are visible
        self.steps_stack.setMinimumHeight(350)

        # Add to layout with stretch factor so it takes available space
        self.content_layout.addWidget(self.steps_stack, 1)

        # Premium navigation buttons
        self.setup_premium_navigation_buttons()

        # Add content frame to main layout with stretch factor
        main_layout.addWidget(content_frame, 1)

        # IMPROVED: Explicitly set the size of this container
        self.setMinimumSize(800, 600)
        self.resize(900, 700)  # Start with a generous size

        # Create and connect all the step widgets
        self.create_step_widgets()

    def setup_premium_search(self):
        """Create an elegantly styled search section."""
        # Container for search with premium styling
        search_container = QFrame()
        search_container.setObjectName("searchContainer")
        search_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Search layout with refined spacing
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 5, 10, 5)
        search_layout.setSpacing(10)

        # Enhanced SearchBox with premium styling
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_parts_placeholder',
            label_key='search_parts'
        )
        self.search_box.search_changed.connect(self.on_search_typed)
        self.search_box.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Style the input directly for premium appearance
        self.search_box.search_input.setObjectName("searchInput")
        self.search_box.search_label.hide()  # Hide label for cleaner look

        # Premium search button
        self.search_button = QPushButton(self.translator.t('search_button'))
        self.search_button.setObjectName("searchButton")
        self.search_button.clicked.connect(self.on_search)
        self.search_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        # Add to search layout
        search_layout.addWidget(self.search_box, 1)
        search_layout.addWidget(self.search_button)

        # Add to main layout
        self.layout().addWidget(search_container)

    def setup_premium_navigation_buttons(self):
        """Create elegantly styled navigation buttons with better styling controls."""
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 15, 0, 0)
        buttons_layout.setSpacing(20)  # More spacing between buttons

        # Premium back button - explicitly styled
        self.back_button = QPushButton(self.translator.t('back_button'))
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(self.on_back_clicked)
        self.back_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.back_button.setCursor(Qt.PointingHandCursor)

        # Set minimum size for better proportions
        self.back_button.setMinimumWidth(120)
        self.back_button.setMinimumHeight(44)

        # Premium next button - explicitly styled
        self.next_button = QPushButton(self.translator.t('next_button'))
        self.next_button.setObjectName("nextButton")
        self.next_button.clicked.connect(self.on_next_clicked)
        self.next_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.next_button.setCursor(Qt.PointingHandCursor)

        # Set minimum size for better proportions
        self.next_button.setMinimumWidth(120)
        self.next_button.setMinimumHeight(44)

        # Add buttons with stretch for proper positioning
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.next_button)

        self.content_layout.addLayout(buttons_layout)

    def create_step_widgets(self):
        """Create all the navigation step widgets with improved sizing and visibility."""
        # Step 1: Brand selection
        self.brand_widget = BrandWidget(self.translator, self.db)
        self.brand_widget.step_completed.connect(self.on_brand_selected)
        # IMPROVED: Set minimum size for the widget to ensure visibility
        self.brand_widget.setMinimumSize(600, 400)
        self.steps_stack.addWidget(self.brand_widget)

        # Step 2: Model selection
        self.model_widget = ModelWidget(self.translator, self.db)
        self.model_widget.step_completed.connect(self.on_model_selected)
        # IMPROVED: Set minimum size for the widget to ensure visibility
        self.model_widget.setMinimumSize(600, 400)
        self.steps_stack.addWidget(self.model_widget)

        # Step 3: Year selection
        self.year_widget = YearWidget(self.translator, self.db)
        self.year_widget.step_completed.connect(self.on_year_selected)
        # IMPROVED: Set minimum size for the widget to ensure visibility
        self.year_widget.setMinimumSize(600, 400)
        self.steps_stack.addWidget(self.year_widget)

        # Step 4: Category selection
        self.category_widget = CategoryWidget(self.translator, self.db)
        self.category_widget.step_completed.connect(self.on_category_selected)
        # IMPROVED: Set minimum size for the widget to ensure visibility
        self.category_widget.setMinimumSize(600, 400)
        self.steps_stack.addWidget(self.category_widget)

        # Step 5: Product selection
        self.products_widget = ProductsWidget(self.translator, self.db)
        self.products_widget.step_completed.connect(self.on_product_selected)
        # IMPROVED: Set minimum size for the widget to ensure visibility
        self.products_widget.setMinimumSize(600, 400)
        self.steps_stack.addWidget(self.products_widget)

        # Step 6: Details selection
        self.details_widget = DetailsWidget(self.translator, self.db)
        self.details_widget.step_completed.connect(self.on_details_selected)
        # IMPROVED: Set minimum size for the widget to ensure visibility
        self.details_widget.setMinimumSize(600, 400)
        self.steps_stack.addWidget(self.details_widget)

        # Step 7: Final confirmation
        self.final_widget = FinalWidget(self.translator, self.db)
        self.final_widget.back_requested.connect(self.on_final_back)
        # IMPROVED: Set minimum size for the widget to ensure visibility
        self.final_widget.setMinimumSize(600, 400)
        self.steps_stack.addWidget(self.final_widget)

        # IMPROVED: Update all widgets with proper theme
        self.go_to_step(0)

        # IMPROVED: Initial update of UI state
        QTimer.singleShot(100, self.update_navigation_buttons)

    def animate_transition(self, from_index, to_index):
        """Animate the transition between steps with premium effects - simplified for better compatibility."""
        if from_index == to_index:
            return False

        # Get the widgets for animation
        from_widget = self.get_step_widget(from_index)
        to_widget = self.get_step_widget(to_index)

        if not from_widget or not to_widget:
            return False

        # Cancel any running animation
        if self._current_animation and self._current_animation.state() == QPropertyAnimation.Running:
            self._current_animation.stop()

        # Create parallel animation group for sophisticated effect
        self._current_animation = QParallelAnimationGroup()

        # Set up fade out animation for current widget
        current_opacity_effect = QGraphicsOpacityEffect(from_widget)
        from_widget.setGraphicsEffect(current_opacity_effect)
        current_opacity_effect.setOpacity(1.0)  # Start fully visible

        fade_out = QPropertyAnimation(current_opacity_effect, b"opacity")
        fade_out.setDuration(200)  # Quick fade-out
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.OutQuad)  # Simpler easing curve

        # Set up fade in animation for next widget
        next_opacity_effect = QGraphicsOpacityEffect(to_widget)
        to_widget.setGraphicsEffect(next_opacity_effect)
        next_opacity_effect.setOpacity(0.0)  # Start fully transparent

        fade_in = QPropertyAnimation(next_opacity_effect, b"opacity")
        fade_in.setDuration(250)  # Slightly longer fade-in
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InOutQuad)  # Simpler easing curve

        # Connect signals to handle the actual widget change
        fade_out.finished.connect(lambda: self.steps_stack.setCurrentIndex(to_index))

        # Add animations to group
        self._current_animation.addAnimation(fade_out)

        # Slight delay before fade in for more polished feel
        fade_in_timer = QTimer()
        fade_in_timer.setSingleShot(True)
        fade_in_timer.timeout.connect(lambda: self._current_animation.addAnimation(fade_in))
        fade_in_timer.start(100)

        # Start animation
        self._current_animation.start()

        return True
    def get_step_widget(self, step_index):
        """Get the widget for a specific step."""
        if 0 <= step_index < self.steps_stack.count():
            return self.steps_stack.widget(step_index)
        return None

    def go_to_step(self, step_index):
        """Navigate to a specific step with premium transitions."""
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

            # Animate transition between steps or do immediate change if animation fails
            animated = self.animate_transition(current_step, step_index)
            if not animated:
                self.steps_stack.setCurrentIndex(step_index)

            # Update premium step indicators
            self.steps_panel.set_current_step(step_index)

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

    def update_navigation_buttons(self):
        """Update the state of the navigation buttons with premium styling."""
        current_step = self.steps_stack.currentIndex()

        # Back button is enabled except on first step
        self.back_button.setEnabled(current_step > 0)

        # Next button is enabled if we can go to next step
        next_enabled = self.can_go_to_next_step(current_step)
        self.next_button.setEnabled(next_enabled)

        # Change next button text for final step with premium wording
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

    def on_step_indicator_clicked(self, step_index):
        """Handle click on a step indicator from premium panel."""
        # Only allow clicks to steps we can navigate to
        if self.can_go_to_step(step_index):
            self.go_to_step(step_index)

    def on_back_clicked(self):
        """Handle back button click with premium transitions."""
        current_step = self.steps_stack.currentIndex()
        if current_step > 0:
            self.go_to_step(current_step - 1)

    def on_next_clicked(self):
        """Handle next button click with premium transitions."""
        current_step = self.steps_stack.currentIndex()

        # If on final step, reset and start over
        if current_step == 6:  # Final step
            self.reset_navigation()
            return

        # Otherwise try to go to next step
        if self.can_go_to_next_step(current_step):
            self.go_to_step(current_step + 1)

    def on_brand_selected(self, brand_data):
        """Handle brand selection with premium transitions."""
        logger.info(f"Brand selected: {brand_data}")
        self.navigation_state.brand = brand_data
        self.update_navigation_buttons()

    def on_model_selected(self, model_data):
        """Handle model selection with premium transitions."""
        logger.info(f"Model selected: {model_data}")
        self.navigation_state.model = model_data
        self.update_navigation_buttons()

    def on_year_selected(self, data):
        """Handle year selection with premium transitions."""
        # Data contains both year and constructed car object
        if not data or 'car' not in data:
            logger.warning("Invalid year selection data")
            return

        logger.info(f"Year selected: {data.get('year', '')}")
        self.navigation_state.year = data
        self.navigation_state.car = data['car']
        self.update_navigation_buttons()

    def on_category_selected(self, category_data):
        """Handle category selection with premium transitions."""
        logger.info(f"Category selected: {category_data}")
        self.navigation_state.category = category_data
        self.update_navigation_buttons()

    def on_product_selected(self, product_data):
        """Handle product selection with premium transitions."""
        logger.info(f"Product selected: {product_data}")
        self.navigation_state.product = product_data
        self.update_navigation_buttons()

    def on_details_selected(self, details_data):
        """Handle details selection with premium transitions."""
        logger.info(f"Details selected: {details_data}")
        self.navigation_state.details = details_data
        self.update_navigation_buttons()

    def on_final_back(self):
        """Handle back button from final widget with premium transitions."""
        self.go_to_step(5)  # Go back to details step

    def reset_navigation(self):
        """Reset the navigation with elegant animations."""
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
        """Handle typing in the search box with premium UX."""
        # Enable search button only if there's text
        self.search_button.setEnabled(bool(search_text.strip()))

    def on_search(self):
        """Handle search function with premium transitions."""
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
        """Display a single search result with premium transitions."""
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

    def apply_premium_theme(self):
        """Apply premium enhanced theme styling with improved step indicators integration."""
        # Get theme colors with proper fallbacks
        colors = {
            'background': get_color('background', '#0F2942'),
            'card_bg': get_color('card_bg', '#1E3A5F'),
            'text': get_color('text', '#E2E8F0'),
            'highlight': get_color('highlight', '#4299E1'),
            'border': get_color('border', '#2C5282'),
            'button': get_color('button', '#3182CE'),
            'button_hover': get_color('button_hover', '#4299E1'),
            'button_pressed': get_color('button_pressed', '#2B6CB0'),
            'button_disabled': get_color('button_disabled', '#718096'),
            'text_disabled': get_color('text_disabled', '#A0AEC0'),
            'secondary_text': get_color('secondary_text', '#A0AEC0')
        }

        # Calculate derived colors for enhanced styling
        card_bg_lighter = QColor(colors['card_bg']).lighter(108).name()

        # Style for steps panel container
        steps_panel_style = f"""
            /* Premium steps panel container styling */
            #stepsPanelContainer {{
                background-color: {colors['card_bg']};
                border-radius: 10px;
                border: 1px solid {colors['border']};
                margin-bottom: 10px;
                padding: 0px;
            }}
        """

        # Generate and apply premium stylesheet with added steps panel styling
        stylesheet = generate_premium_stylesheet(colors)

        # Add steps panel styling to the stylesheet
        stylesheet += steps_panel_style

        # Apply the complete stylesheet
        self.setStyleSheet(stylesheet)

        # Apply specific styles directly to the steps panel for better integration
        self.steps_panel.setStyleSheet(f"""
            #premiumStepsPanel {{
                background-color: transparent;
                border: none;
                margin: 0px;
                padding: 0px;
            }}
        """)

        # Also apply direct styling to buttons for better reliability
        back_button_style = f"""
            background-color: {card_bg_lighter};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 25px;
            padding: 12px 24px;
            font-weight: 600;
        """
        self.back_button.setStyleSheet(back_button_style)

        next_button_style = f"""
            background-color: {colors['highlight']};
            color: white;
            border: none;
            border-radius: 25px;
            padding: 12px 24px;
            font-weight: bold;
        """
        self.next_button.setStyleSheet(next_button_style)

    def update_translations(self):
        """Update all text when language changes."""
        # Update title
        self.title_label.setText(self.translator.t('parts_navigation_title'))

        # Update search
        self.search_box.update_translations()
        self.search_button.setText(self.translator.t('search_button'))

        # Update step indicators
        self.steps_panel.update_translations()

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