"""
Premium steps panel for elegant navigation.
Features sophisticated layout and animations with an iOS-inspired design.
Enhanced for better visibility and theme integration.
"""
from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QFrame, QScrollArea,
                             QVBoxLayout, QSizePolicy, QLabel, QApplication)
from PyQt5.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
                          QSequentialAnimationGroup, QTimer, pyqtSignal)
from PyQt5.QtGui import QPainter, QColor, QPen, QLinearGradient, QPalette

from .step_indicator import PremiumStepIndicator
from .premium_step_connector import PremiumStepConnector
from themes import get_color

class PremiumStepsPanel(QWidget):
    """
    A premium panel for step indicators with elegant visual design and animations.
    Inspired by high-end iOS and Android applications.
    """

    # Signal emitted when a step is clicked
    step_clicked = pyqtSignal(int)

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.step_indicators = []
        self.step_connectors = []
        self.current_step = 0
        self.previous_step = 0
        self.scroll_timer = None

        # Create stylish scroll area for responsive design
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Set up the UI with premium elements and improved visibility."""
        self.setObjectName("premiumStepsPanel")

        # Main layout with proper spacing and margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 5, 0, 5)  # Reduced vertical margins
        main_layout.setSpacing(0)

        # Create the panel container for proper styling
        self.panel_container = QFrame()
        self.panel_container.setObjectName("stepsContainer")
        self.panel_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.panel_container.setMinimumHeight(90)  # Ensure enough height for indicators

        panel_layout = QVBoxLayout(self.panel_container)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        # Create scroll area for responsive design with improved visibility
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("stepsScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setMinimumHeight(90)  # Ensure enough height

        # Content widget for scroll area
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scrollContent")
        self.scroll_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.scroll_content.setMinimumHeight(80)  # Ensure enough height

        # Horizontal layout for step indicators with proper spacing
        self.steps_layout = QHBoxLayout(self.scroll_content)
        self.steps_layout.setContentsMargins(20, 10, 20, 5)  # Adjusted margins
        self.steps_layout.setSpacing(0)  # We'll control spacing with connector width
        self.steps_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)  # Align left for better scrolling

        # Add scroll content to scroll area
        self.scroll_area.setWidget(self.scroll_content)

        # Add scroll area to panel container
        panel_layout.addWidget(self.scroll_area)

        # Add panel container to main layout
        main_layout.addWidget(self.panel_container)

        # Define and create the steps
        self.create_steps()

    def apply_theme(self):
        """Apply system theme styling to the panel with improved visibility."""
        # Get theme colors with fallbacks
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        border_color = get_color('border', '#2C5282')

        # Create a lighter version of the card background
        card_bg_obj = QColor(card_bg)
        card_bg_lighter = card_bg_obj.lighter(108).name()

        # Apply styling to the panel and scroll area
        self.setStyleSheet(f"""
            #premiumStepsPanel {{
                background-color: transparent;
                border: none;
            }}
            
            #stepsContainer {{
                background-color: {card_bg_lighter};
                border-radius: 8px;
                border: 1px solid {border_color};
                margin: 5px 10px;
                padding: 0px;
            }}
            
            #stepsScrollArea {{
                background-color: transparent;
                border: none;
            }}
            
            #scrollContent {{
                background-color: transparent;
                border: none;
            }}
            
            QScrollBar:horizontal {{
                height: 0px;  /* Hide scrollbar but keep functionality */
                background: transparent;
            }}
        """)

    def create_steps(self):
        """Create premium step indicators with connectors and proper spacing."""
        # Define all steps with elegant naming
        step_texts = [
            'brand_step',
            'model_step',
            'year_step',
            'category_step',
            'product_step',
            'details_step',
            'final_step'
        ]

        # Create indicators with connectors
        for i, text in enumerate(step_texts):
            # Create premium indicator
            indicator = PremiumStepIndicator(i + 1, text, self.translator)

            # Ensure it has proper sizing for visibility
            indicator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            indicator.setMinimumSize(60, 70)
            indicator.setMaximumSize(60, 70)

            # Make it clickable
            indicator.mousePressEvent = lambda event, idx=i: self.on_step_click(idx)

            # Add to layout
            self.steps_layout.addWidget(indicator, 0, Qt.AlignVCenter)
            self.step_indicators.append(indicator)

            # Add premium connector between steps (except after last step)
            if i < len(step_texts) - 1:
                connector = PremiumStepConnector()
                connector.setMinimumWidth(30)  # Ensure minimum width for visibility
                connector.setMaximumHeight(6)  # Control height
                self.steps_layout.addWidget(connector, 1)  # Takes available space
                self.step_connectors.append(connector)

        # Add stretch at the end to center the steps horizontally
        # self.steps_layout.addStretch(1)

        # Update the initial state
        self.set_current_step(0, animate=False)

        # Initialize scroll position
        QTimer.singleShot(100, self.scroll_to_current)

    def set_current_step(self, step_index, animate=True):
        """
        Set the current step with elegant animations and ensure visibility.

        Args:
            step_index: Index of the current step
            animate: Whether to animate the transition
        """
        # Store for animation direction
        self.previous_step = self.current_step
        self.current_step = step_index

        # Update all indicators
        for i, indicator in enumerate(self.step_indicators):
            is_completed = i < step_index
            is_current = i == step_index

            # Apply state with animation
            indicator.set_state(is_current, is_completed, animate)

        # Update connectors with animation
        for i, connector in enumerate(self.step_connectors):
            connector.set_completed(i < step_index, animate)

        # Ensure the current step is visible - with improved timing
        if animate:
            # Use a timer to scroll after animations have started
            if self.scroll_timer:
                self.scroll_timer.stop()

            self.scroll_timer = QTimer(self)
            self.scroll_timer.setSingleShot(True)
            self.scroll_timer.timeout.connect(self.scroll_to_current)
            self.scroll_timer.start(150)  # Slightly longer delay for reliable scrolling
        else:
            # For non-animated changes, scroll immediately
            QTimer.singleShot(50, self.scroll_to_current)

    def scroll_to_current(self):
        """Scroll to make current step visible with improved reliability and centering."""
        # Get the current indicator widget
        if 0 <= self.current_step < len(self.step_indicators):
            current_indicator = self.step_indicators[self.current_step]

            # Compute global position and then convert to scroll area coordinates
            indicator_pos = current_indicator.mapTo(self.scroll_content, current_indicator.pos())

            # Calculate center offset to position current step in center of visible area
            center_offset = (self.scroll_area.width() - current_indicator.width()) // 2

            # Calculate target scroll position with centering
            target_x = max(0, indicator_pos.x() - center_offset)

            # Ensure we don't scroll beyond content width
            max_scroll = self.scroll_content.width() - self.scroll_area.width()
            if max_scroll > 0:  # Only limit if content is wider than viewport
                target_x = min(target_x, max_scroll)

            # Use a smooth animation to scroll
            scrollbar = self.scroll_area.horizontalScrollBar()

            # Start animation from current position
            animation = QPropertyAnimation(scrollbar, b"value")
            animation.setDuration(300)  # Smooth duration
            animation.setStartValue(scrollbar.value())
            animation.setEndValue(target_x)
            animation.setEasingCurve(QEasingCurve.OutCubic)  # Smooth easing
            animation.start()

    def on_step_click(self, step_index):
        """Handle click on a step indicator."""
        # Only allow clicking on completed steps or the next available step
        if step_index <= self.current_step + 1 and step_index != self.current_step:
            self.step_clicked.emit(step_index)

    def update_translations(self):
        """Update translations for all indicators."""
        for indicator in self.step_indicators:
            indicator.update_translations()

    def resizeEvent(self, event):
        """Handle resize events to maintain visual appearance."""
        super().resizeEvent(event)

        # After resize, ensure the current step is visible
        QTimer.singleShot(50, self.scroll_to_current)

    def paintEvent(self, event):
        """Custom paint event for premium appearance with fade effects at edges."""
        super().paintEvent(event)

        # Only paint the gradient overlays if the content is wider than the viewport
        if self.scroll_content.width() > self.scroll_area.width():
            # Apply fade gradient overlays at edges for better visual integration
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            # Get appropriate colors based on the current theme
            bg_color = get_color('card_bg', '#1E3A5F')
            fade_color_obj = QColor(bg_color)
            fade_color_obj.setAlpha(150)  # Semi-transparent

            # Convert to RGBA string format for gradient
            fade_color = f"rgba({fade_color_obj.red()}, {fade_color_obj.green()}, {fade_color_obj.blue()}, 0.7)"
            fade_trans = f"rgba({fade_color_obj.red()}, {fade_color_obj.green()}, {fade_color_obj.blue()}, 0.0)"

            # Left fade gradient
            left_gradient = QLinearGradient(0, 0, 40, 0)
            left_gradient.setColorAt(0.0, QColor(fade_color))
            left_gradient.setColorAt(1.0, QColor(fade_trans))
            painter.fillRect(0, 0, 40, self.height(), left_gradient)

            # Right fade gradient
            right_gradient = QLinearGradient(self.width() - 40, 0, self.width(), 0)
            right_gradient.setColorAt(0.0, QColor(fade_trans))
            right_gradient.setColorAt(1.0, QColor(fade_color))
            painter.fillRect(self.width() - 40, 0, 40, self.height(), right_gradient)