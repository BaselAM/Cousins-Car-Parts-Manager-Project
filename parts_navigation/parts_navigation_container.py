"""
Premium parts navigation container.

This module provides the main container for the parts selection process with
elegant styling and smooth animations.
"""
import gc

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QStackedWidget,
                             QHBoxLayout, QFrame, QPushButton, QMessageBox,
                             QSizePolicy, QGraphicsOpacityEffect, QApplication)
from PyQt5.QtCore import (Qt, pyqtSignal, QSize, QPropertyAnimation,
                          QEasingCurve, QParallelAnimationGroup, QTimer)
from PyQt5.QtGui import QFont, QColor
from PyQt5 import sip  # Add this for checking if widgets have been deleted

# Import components
from .navigation_state import NavigationState
from .animation import AnimationManager
from .step_indicator import StepsPanel, StepDotsIndicator

# Import step widgets
from .steps.brand_step import BrandStep
from .steps.model_step import ModelStep
from .steps.year_step import YearStep
from .steps.category_step import CategoryStep
from .steps.product_step import ProductStep
from .steps.details_step import DetailsStep
from .steps.summary_step import SummaryStep

# Import search box
from .components.search_box import SearchBox

from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.container')


class PartsNavigationContainer(QWidget):
    """
    Container for the hierarchical parts navigation with premium styling.

    Features:
    - Clean, elegant layout with premium iOS-inspired design
    - Smooth transitions between steps
    - Visual step indicators with animations
    - Theme integration
    - Responsive sizing
    """

    def __init__(self, translator, db, parent=None):
        """
        Initialize the parts navigation container.
        """
        super().__init__(parent)
        self.translator = translator
        self.db = db
        self.setObjectName("partsNavigationContainer")

        # Set up navigation state
        self.navigation_state = NavigationState()

        # Configure size policy for responsive behavior
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Minimum size is important, but don't make it too large
        self.setMinimumSize(750, 550)

        # Initialize UI with premium styling
        self.setup_ui()
        self.apply_theme()

        # Animation properties
        self._current_animation = None

        # Create a shared database operator for preloading
        # Move import inside the method to avoid circular imports
        from utils.database_worker import DatabaseOperator
        self.shared_db_operator = DatabaseOperator(db)

        # Create and connect all the step widgets with preloading enabled
        self.create_step_widgets(preload=True)

        # Initialize with first step
        self.go_to_step(0)

    def _start_delayed_preloading(self):
        """Start preloading brand data with proper error handling"""
        if hasattr(self, 'brand_step') and self.brand_step:
            try:
                logger.info("Starting delayed brand preloading")
                # Ensure we have a valid shared_db_operator
                if hasattr(self, 'shared_db_operator') and self.shared_db_operator:
                    self.brand_step.setup_preloading(self.shared_db_operator)
                else:
                    logger.warning("Cannot preload brands: shared_db_operator not available")
            except Exception as e:
                logger.error(f"Error during delayed brand preloading: {e}")
                # Don't propagate the exception - just log it

    def cleanup_resources(self, existing_connection=None):
        """Complete cleanup of all resources when container is closed"""
        logger.debug("Performing comprehensive cleanup of parts navigation resources")

        # First clean up animations
        if hasattr(self, 'cleanup_animations'):
            try:
                self.cleanup_animations()
            except Exception as e:
                logger.error(f"Error cleaning up animations: {e}")

        # Clean up shared database operator
        if hasattr(self, 'shared_db_operator'):
            try:
                self.shared_db_operator.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up shared_db_operator: {e}")

        # Get references to all steps before cleaning up to avoid accessing them if they're deleted
        steps = []
        if hasattr(self, 'steps_stack'):
            for i in range(self.steps_stack.count()):
                try:
                    step = self.steps_stack.widget(i)
                    if step:
                        steps.append(step)
                except Exception:
                    pass  # Skip if widget can't be accessed

        # Clean up any threads or workers in steps
        for step in steps:
            try:
                # Clean up logo manager if exists
                if hasattr(step, 'logo_manager') and hasattr(step.logo_manager, 'thread_pool'):
                    try:
                        # Wait for thread pool to finish current tasks
                        step.logo_manager.thread_pool.waitForDone(100)  # 100ms timeout
                    except Exception as e:
                        logger.error(f"Error cleaning up logo_manager: {e}")

                # Clean up database operators
                if hasattr(step, 'db_operator') and step.db_operator:
                    try:
                        step.db_operator.cleanup()
                    except Exception as e:
                        logger.error(f"Error cleaning up db_operator: {e}")

                # Clean up any animations
                if hasattr(step, '_cancel_animations'):
                    try:
                        step._cancel_animations()
                    except Exception as e:
                        logger.error(f"Error cancelling animations: {e}")
            except Exception as e:
                logger.error(f"Error cleaning up step: {e}")

        # Process any pending events before attempting to close database
        QApplication.processEvents()

        # Clean up database connections last - but only if not using provided connection
        if existing_connection is None and hasattr(self, 'db') and self.db:
            try:
                # Force thread-safe closing
                self.db.ensure_connection()
                self.db.close_connection()
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")
        else:
            logger.debug("Using provided database connection - skipping close operation")

        logger.debug("Parts navigation resources cleanup completed")

    def sizeHint(self):
        """Return a size that works well within the content stack."""
        # Get content stack size if we can access it
        if self.parent() and hasattr(self.parent(), 'content_stack'):
            stack_size = self.parent().content_stack.size()
            # Return slightly smaller size to ensure it fits within the stack
            return QSize(stack_size.width() - 20, stack_size.height() - 20)

        # Otherwise return a reasonable default that works with the content stack
        return QSize(900, 650)

    def setup_ui(self):
        """Create a premium UI with refined spacing and elements."""
        # Main layout with optimized margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)  # Reduced from 10,10,10,10
        main_layout.setSpacing(4)  # Reduced for compact layout

        # Header section (more compact)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)  # Reduced spacing

        # Smaller title to save space
        self.title_label = QLabel(self.translator.t('parts_navigation_title'))
        self.title_label.setObjectName("partsNavigationTitle")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setFixedHeight(24)  # Reduced height
        header_layout.addWidget(self.title_label)

        # Create search box for header - more compact
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_parts_placeholder',
            label_key='search_parts',
            show_button=True
        )
        self.search_box.search_changed.connect(self.on_search_typed)
        self.search_box.search_submitted.connect(self.on_search)
        self.search_box.setMaximumHeight(30)  # Limited height
        header_layout.addWidget(self.search_box, 1)

        main_layout.addLayout(header_layout)

        # Very thin separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("titleSeparator")
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)

        # Content area with more space for steps
        content_frame = QFrame()
        content_frame.setObjectName("partsContent")
        content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Reduced margins in content layout
        self.content_layout = QVBoxLayout(content_frame)
        self.content_layout.setContentsMargins(6, 6, 6, 6)  # Reduced from 8,8,8,8
        self.content_layout.setSpacing(4)  # Reduced spacing

        # Step indicator at the top, more compact
        indicator_layout = QHBoxLayout()
        indicator_layout.setContentsMargins(0, 0, 0, 0)
        indicator_layout.setSpacing(4)

        # Smaller steps panel
        self.steps_panel = StepsPanel(self.translator)
        self.steps_panel.setMaximumHeight(40)  # Reduced from 60
        self.steps_panel.step_clicked.connect(self.on_step_indicator_clicked)
        indicator_layout.addWidget(self.steps_panel)

        # Add indicator to top of content layout
        self.content_layout.addLayout(indicator_layout)

        # Create stacked widget for steps with INCREASED PROPORTION
        self.steps_stack = QStackedWidget()
        self.steps_stack.setObjectName("stepsStack")
        self.steps_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Don't set minimum height - let it be determined by layout constraints
        # This was causing size issues
        # self.steps_stack.setMinimumHeight(480)

        # Add steps stack with MUCH HIGHER stretch factor - key for dominance
        self.content_layout.addWidget(self.steps_stack, 20)  # Doubled from 10

        # More compact navigation buttons
        self.setup_navigation_buttons()

        # Add content frame to main layout with higher stretch
        main_layout.addWidget(content_frame, 20)  # Huge increase from 1

        # Create and connect all the step widgets
        self.create_step_widgets()

        # Skip dots indicator since we aren't using it
        self.dots_indicator = None

    def setup_navigation_buttons(self):
        """Create compact navigation buttons that don't steal space from steps."""
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 4, 0, 0)  # Reduced top margin
        buttons_layout.setSpacing(12)  # Reduced spacing

        # Smaller back button
        self.back_button = QPushButton(self.translator.t('back_button'))
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(self.on_back_clicked)
        self.back_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.back_button.setCursor(Qt.PointingHandCursor)

        # More compact button size
        self.back_button.setMinimumWidth(90)
        self.back_button.setMinimumHeight(32)
        self.back_button.setMaximumHeight(36)

        # Smaller next button
        self.next_button = QPushButton(self.translator.t('next_button'))
        self.next_button.setObjectName("nextButton")
        self.next_button.clicked.connect(self.on_next_clicked)
        self.next_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        self.next_button.setCursor(Qt.PointingHandCursor)

        # More compact button size
        self.next_button.setMinimumWidth(90)
        self.next_button.setMinimumHeight(32)
        self.next_button.setMaximumHeight(36)

        # Add buttons with stretch for proper positioning
        buttons_layout.addWidget(self.back_button)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.next_button)

        self.content_layout.addLayout(buttons_layout)

    def apply_theme(self):
        """Apply premium styling based on system theme."""
        # Get theme colors with fallbacks to ensure consistency
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        text_color = get_color('text', '#E2E8F0')
        border_color = get_color('border', '#2C5282')
        highlight = get_color('highlight', '#4299E1')
        button = get_color('button', '#3182CE')
        secondary_text = get_color('secondary_text', '#A0AEC0')

        # Compute derived colors for enhanced styling
        card_bg_lighter = QColor(card_bg).lighter(108).name()
        highlight_lighter = QColor(highlight).lighter(115).name()
        highlight_darker = QColor(highlight).darker(115).name()
        button_hover = get_color('button_hover', highlight_lighter)
        button_pressed = get_color('button_pressed', highlight_darker)

        # Apply styling to main container - cleaner with subtle borders
        self.setStyleSheet(f"""
            #partsNavigationContainer {{
                background-color: {bg_color};
            }}

            #partsNavigationTitle {{
                color: {text_color};
                font-weight: bold;
                font-size: 14px;  /* Smaller font to save space */
                letter-spacing: -0.2px;
                padding: 2px;  /* Reduced padding */
                font-family: "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
            }}

            #titleSeparator {{
                background-color: {border_color};
                margin-left: 15px;
                margin-right: 15px;
                margin-bottom: 4px;  /* Reduced margin */
                height: 1px;
                opacity: 0.5;
            }}

            #searchContainer {{
                padding: 4px;  /* Reduced padding */
                background-color: {card_bg_lighter};
                border-radius: 6px;  /* Smaller radius */
                margin-bottom: 4px;  /* Reduced margin */
            }}

            #partsContent {{
                background-color: {card_bg};
                border-radius: 8px;  /* Reduced from 12px */
                border: none;
                padding: 8px;  /* Reduced from 15px */
            }}

            #stepsStack {{
                background-color: transparent;
                border: none;
            }}

            /* More compact navigation buttons */
            #backButton {{
                background-color: {card_bg_lighter};
                color: {text_color};
                border-radius: 16px;  /* Reduced radius */
                border: 1px solid {border_color};
                padding: 6px 14px;  /* Reduced padding */
                font-weight: 600;
                font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
                font-size: 13px;  /* Smaller font */
                letter-spacing: 0.1px;
            }}

            #backButton:hover {{
                background-color: {card_bg};
                border: 1px solid {highlight};
            }}

            #backButton:pressed {{
                background-color: {QColor(card_bg).darker(105).name()};
                padding-top: 7px;  /* Adjusted pressed effect */
                padding-bottom: 5px;
                border: 1px solid {highlight};
            }}

            #backButton:disabled {{
                background-color: {card_bg};
                color: {secondary_text};
                border: 1px solid {QColor(card_bg).darker(110).name()};
            }}

            #nextButton {{
                background-color: {highlight};
                color: white;
                border-radius: 16px;  /* Reduced radius */
                padding: 6px 14px;  /* Reduced padding */
                font-weight: bold;
                font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
                font-size: 13px;  /* Smaller font */
                letter-spacing: 0.1px;
                border: none;
            }}

            #nextButton:hover {{
                background-color: {highlight_lighter};
            }}

            #nextButton:pressed {{
                background-color: {highlight_darker};
                padding-top: 7px;  /* Adjusted pressed effect */
                padding-bottom: 5px;
            }}

            #nextButton:disabled {{
                background-color: {QColor(highlight).darker(140).name()};
                color: {QColor(text_color).darker(120).name()};
                opacity: 0.7;
            }}
        """)

    def showEvent(self, event):
        """Handle show event by properly sizing widgets with focus on step content."""
        super().showEvent(event)

        # DON'T set explicit heights based on percentages
        # This was causing layout issues with the content stack
        # Instead, let the layout system handle proportions

        # Force layout update
        self.updateGeometry()

    def resizeEvent(self, event):
        """Handle resize events to adjust UI for different screen sizes."""
        super().resizeEvent(event)

        # Toggle between full step panel and compact dots based on width
        width = self.width()

        # Keep proper null-checking for dots_indicator
        if width < 800 and hasattr(self, 'dots_indicator') and self.dots_indicator:
            # Switch to compact mode for narrow screens
            self.steps_panel.hide()
            self.dots_indicator.show()
        else:
            self.steps_panel.show()
            if hasattr(self, 'dots_indicator') and self.dots_indicator:
                self.dots_indicator.hide()

        # Make sure steps_stack is prioritized
        if hasattr(self, 'content_layout') and hasattr(self, 'steps_stack'):
            self.content_layout.setStretchFactor(self.steps_stack, 20)  # Maintain high stretch factor

    def setup_search_section(self):
        """Create an elegantly styled search section with premium controls."""
        # Container for search
        self.search_container = QFrame()
        self.search_container.setObjectName("searchContainer")
        self.search_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        # Layout
        search_layout = QHBoxLayout(self.search_container)
        search_layout.setContentsMargins(10, 5, 10, 5)
        search_layout.setSpacing(10)

        # Enhanced search box
        self.search_box = SearchBox(
            self.translator,
            placeholder_key='search_parts_placeholder',
            label_key='search_parts',
            show_button=True
        )
        self.search_box.search_changed.connect(self.on_search_typed)
        self.search_box.search_submitted.connect(self.on_search)
        search_layout.addWidget(self.search_box, 1)

    def get_step_widget(self, step_index):
        """
        Get the widget for a specific step.

        Args:
            step_index: Index of the step

        Returns:
            QWidget: The step widget or None if invalid index
        """
        if 0 <= step_index < self.steps_stack.count():
            return self.steps_stack.widget(step_index)
        return None

    def can_go_to_next_step(self, current_step):
        """
        Check if we can go to the next step.

        Args:
            current_step: Current step index

        Returns:
            bool: True if we can go to the next step
        """
        # Get the current widget
        current_widget = self.get_step_widget(current_step)

        # Check if the widget says we can proceed
        if current_widget and hasattr(current_widget, 'can_proceed'):
            return current_widget.can_proceed()

        return False

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

    def on_step_indicator_clicked(self, step_index):
        """
        Handle click on a step indicator.

        Args:
            step_index: Index of the clicked step
        """
        # Only allow clicks to steps we can navigate to
        if self.navigation_state.can_navigate_to_step(step_index):
            self.go_to_step(step_index)
        else:
            # Optionally show a message explaining why navigation is not possible
            missing_steps = []
            dependencies = self.navigation_state.get_dependency_chain(step_index)
            for dep in dependencies:
                if not self.navigation_state.get_step_data(dep):
                    step_name = self.get_step_name(dep)
                    if step_name:
                        missing_steps.append(step_name)

            if missing_steps:
                message = self.translator.t('missing_steps_message', steps=", ".join(missing_steps))
                QMessageBox.information(self, self.translator.t('navigation_error'), message)

    def get_step_name(self, step_index):
        """Get the name of a step for user messages."""
        step_keys = [
            'brand_step',
            'model_step',
            'year_step',
            'category_step',
            'product_step',
            'details_step',
            'final_step'
        ]

        if 0 <= step_index < len(step_keys):
            return self.translator.t(step_keys[step_index])
        return None

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
        """
        Handle brand selection.

        Args:
            brand_data: Selected brand data
        """
        logger.info(f"Brand selected: {brand_data}")

        # Update navigation state
        self.navigation_state.brand = brand_data

        # Update button states
        self.update_navigation_buttons()

        # Automatically proceed to the next step if this is a new selection
        # to avoid having to click Next
        current_step = self.steps_stack.currentIndex()
        if current_step == 0 and self.can_go_to_next_step(current_step):
            logger.debug("Automatically proceeding to model selection after brand selection")
            self.go_to_step(current_step + 1)

    def on_model_selected(self, model_data):
        """
        Handle model selection.

        Args:
            model_data: Selected model data
        """
        logger.info(f"Model selected: {model_data}")
        self.navigation_state.model = model_data
        self.update_navigation_buttons()

    def on_year_selected(self, data):
        """
        Handle year selection.

        Args:
            data: Selected year data with car info
        """
        # Data contains both year and constructed car object
        if not data or 'car' not in data:
            logger.warning("Invalid year selection data")
            return

        logger.info(f"Year selected: {data.get('year', '')}")
        self.navigation_state.year = data
        self.navigation_state.car = data['car']
        self.update_navigation_buttons()

    def on_category_selected(self, category_data):
        """
        Handle category selection.

        Args:
            category_data: Selected category data
        """
        logger.info(f"Category selected: {category_data}")
        self.navigation_state.category = category_data
        self.update_navigation_buttons()

    def on_product_selected(self, product_data):
        """
        Handle product selection.

        Args:
            product_data: Selected product data
        """
        logger.info(f"Product selected: {product_data}")
        self.navigation_state.product = product_data
        self.update_navigation_buttons()

    def on_details_selected(self, details_data):
        """
        Handle details selection.

        Args:
            details_data: Selected details data
        """
        logger.info(f"Details selected: {details_data}")
        self.navigation_state.details = details_data
        self.update_navigation_buttons()

    def on_final_back(self):
        """Handle back button from final widget."""
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
        """
        Handle typing in the search box.

        Args:
            search_text: The search text
        """
        # Update UI state based on search text
        pass

    def on_search(self, search_text):
        """
        Handle search function.

        Args:
            search_text: The search text to search for
        """
        search_text = search_text.strip()
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
                self.product_step.show_search_results(results)

        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            QMessageBox.warning(
                self,
                self.translator.t('search_error'),
                str(e)
            )

    def show_search_result(self, part):
        """
        Display a single search result.

        Args:
            part: The part data to display
        """
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
        self.details_step.set_product(product_data)

    def update_translations(self):
        """Update all translatable text when language changes."""
        # Update title and buttons
        self.title_label.setText(self.translator.t('parts_navigation_title'))
        self.back_button.setText(self.translator.t('back_button'))

        # Update search
        self.search_box.update_translations()

        # Update step indicators
        self.steps_panel.update_translations()

        # Update next button based on current step
        current_step = self.steps_stack.currentIndex()
        if current_step == 5:  # Details step (before final)
            self.next_button.setText(self.translator.t('finish_button'))
        elif current_step == 6:  # Final step
            self.next_button.setText(self.translator.t('done_button'))
        else:
            self.next_button.setText(self.translator.t('next_button'))

        # Update each step widget
        for i in range(self.steps_stack.count()):
            widget = self.get_step_widget(i)
            if widget and hasattr(widget, 'update_translations'):
                widget.update_translations()

    def go_to_step(self, step_index):
        """
        Navigate to a specific step with premium transitions.

        Args:
            step_index: Index of the step to navigate to

        Returns:
            bool: True if navigation was successful
        """
        if 0 <= step_index < self.steps_stack.count():
            # Get the current step index
            current_step = self.steps_stack.currentIndex()

            # Special handling for backward navigation - skip dependency check
            going_backward = step_index < current_step

            # Validate navigation using state manager (only for forward navigation)
            if not going_backward and step_index > 0 and not self.navigation_state.can_navigate_to_step(step_index):
                logger.warning(f"Cannot go to step {step_index}: missing required data")
                return False

            # Get the widgets
            current_widget = self.get_step_widget(current_step)
            next_widget = self.get_step_widget(step_index)

            # Notify widgets about show/hide
            if current_widget:
                current_widget.on_hide()

            if next_widget:
                # For backward navigation, we don't need to validate prerequisites
                # Pass data from previous step if moving forward
                if step_index > current_step and current_step >= 0:
                    previous_data = self.navigation_state.get_step_data(current_step)
                    next_widget.set_previous_step_data(previous_data)

                # Show the widget
                next_widget.on_show()

            # Animate transition between steps
            self.animate_transition(current_step, step_index)

            # Update step indicators
            self.steps_panel.set_current_step(step_index)
            # Important: Check if dots_indicator exists before using it
            if hasattr(self, 'dots_indicator') and self.dots_indicator:
                self.dots_indicator.set_current_step(step_index)

            # Update button states
            self.update_navigation_buttons()

            logger.info(f"Navigated to step {step_index}")
            return True

        logger.warning(f"Invalid step index: {step_index}")
        return False

    def cleanup_animations(self):
        """Clean up all animations and threads before destruction."""
        # Cancel any running transition animation
        if hasattr(self, '_current_animation') and self._current_animation:
            if self._current_animation.state() == QParallelAnimationGroup.Running:
                self._current_animation.stop()
            self._current_animation = None

        # Cleanup step animations if they exist
        for i in range(7):  # There are 7 steps
            step = self.get_step_widget(i)
            if step and hasattr(step, '_cancel_animations'):
                step._cancel_animations()

        # If there's a brand step with a logo manager, clean it up
        for child in self.findChildren(QWidget):
            if hasattr(child, 'logo_manager'):
                if hasattr(child.logo_manager, 'thread_pool'):
                    # Wait for thread pool to finish current tasks
                    child.logo_manager.thread_pool.waitForDone(100)  # 100ms timeout

    def animate_transition(self, from_index, to_index):
        """
        Animate the transition between steps with premium effects.

        Args:
            from_index: Current step index
            to_index: Target step index

        Returns:
            bool: True if animation started
        """
        if from_index == to_index:
            return False

        # Get the widgets for animation
        from_widget = self.get_step_widget(from_index)
        to_widget = self.get_step_widget(to_index)

        if not from_widget or not to_widget:
            # If widgets not available, just update the index
            self.steps_stack.setCurrentIndex(to_index)
            # Make sure button states are updated
            self.update_navigation_buttons()
            return False

        # Clean up any running animation first
        self.cleanup_animations()

        # Use animation manager for consistent effects
        self._current_animation = AnimationManager.fade_transition(
            from_widget, to_widget, self.steps_stack, to_index,
            duration=300, delay=100
        )

        # Store references to prevent memory issues
        self._current_animation._from_widget_ref = from_widget
        self._current_animation._to_widget_ref = to_widget

        # Add this line to ensure navigation buttons are updated after animation completes
        self._current_animation.finished.connect(self.update_navigation_buttons)

        return True

    def __del__(self):
        """Clean up resources on destruction."""
        self.cleanup_animations()

    def handle_close_event(self, event):
        """
        Handle application closing.

        Args:
            event: The close event to handle
        """
        try:
            # First clean up any parts navigation threads/animations
            if hasattr(self.parent, 'view_manager') and \
                    hasattr(self.parent.view_manager, 'parts_navigation_widget') and \
                    self.parent.view_manager.parts_navigation_widget:

                parts_nav = self.parent.view_manager.parts_navigation_widget
                # Use the new comprehensive cleanup method
                if hasattr(parts_nav, 'cleanup_resources'):
                    parts_nav.cleanup_resources()
                elif hasattr(parts_nav, 'cleanup_animations'):
                    parts_nav.cleanup_animations()

            # Process events to complete any pending operations
            QApplication.processEvents()

            # Close database connections
            self.parts_db.close_connection()
            self.settings_db.close()

            # Clean up resources
            if hasattr(self.parent, 'ui_builder') and hasattr(self.parent.ui_builder, 'top_bar'):
                self.parent.ui_builder.top_bar.deleteLater()

            if hasattr(self.parent, 'content_stack'):
                self.parent.content_stack.deleteLater()

            # Process pending events
            QApplication.processEvents()

            # Force garbage collection
            gc.collect()

            event.accept()
        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}")
            # Still accept the event to allow shutdown
            event.accept()
            # Don't call sys.exit() here - it can cause crashes
            # sys.exit(1)

    def create_step_widgets(self, preload=False):
        """Create all the navigation step widgets with preloading support."""
        # Step 1: Brand selection with preloading
        self.brand_step = BrandStep(self.translator, self.db,
                                    db_operator=getattr(self, 'shared_db_operator', None))
        self.brand_step.step_completed.connect(self.on_brand_selected)
        self.steps_stack.addWidget(self.brand_step)

        # Start preloading if requested - MODIFIED TO BE MORE ROBUST
        if preload:
            # Use a timer to delay preloading slightly to ensure UI is stable first
            QTimer.singleShot(50, self._start_delayed_preloading)

            # CRITICAL: Pre-create other steps but DEFER their database loading
            # This makes all step widgets exist but doesn't load their data yet
            QTimer.singleShot(150, self._create_remaining_steps)
        else:
            # Create all steps immediately if not preloading
            self._create_remaining_steps()

    def _create_remaining_steps(self):
        """Create the remaining step widgets in the background."""
        # Step 2: Model selection
        self.model_step = ModelStep(self.translator, self.db)
        self.model_step.step_completed.connect(self.on_model_selected)
        self.steps_stack.addWidget(self.model_step)

        # Step 3: Year selection
        self.year_step = YearStep(self.translator, self.db)
        self.year_step.step_completed.connect(self.on_year_selected)
        self.steps_stack.addWidget(self.year_step)

        # Step 4: Category selection
        self.category_step = CategoryStep(self.translator, self.db)
        self.category_step.step_completed.connect(self.on_category_selected)
        self.steps_stack.addWidget(self.category_step)

        # Use a timer to create the remaining steps with a delay
        # This prevents UI freezing on slower systems
        QTimer.singleShot(50, self._create_final_steps)

    def _create_final_steps(self):
        """Create the final step widgets with a slight delay."""
        # Step 5: Product selection
        self.product_step = ProductStep(self.translator, self.db)
        self.product_step.step_completed.connect(self.on_product_selected)
        self.steps_stack.addWidget(self.product_step)

        # Step 6: Details selection
        self.details_step = DetailsStep(self.translator, self.db)
        self.details_step.step_completed.connect(self.on_details_selected)
        self.steps_stack.addWidget(self.details_step)

        # Step 7: Final confirmation
        self.summary_step = SummaryStep(self.translator, self.db)
        self.summary_step.back_requested.connect(self.on_final_back)
        self.steps_stack.addWidget(self.summary_step)

        logger.info("All navigation steps created successfully")