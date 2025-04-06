"""
Step indicator components for the parts navigation system.

This module provides step indicator and connector components for
visualizing the navigation progress with elegant animations.
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QHBoxLayout,
                             QGraphicsDropShadowEffect, QSizePolicy)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, QSize
from PyQt5.QtCore import pyqtProperty
from PyQt5.QtGui import QFont, QColor, QPainter

from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.indicators')


class StepIndicator(QFrame):
    """
    A premium visual indicator for a step in the navigation process.

    Features:
    - Clean, iOS-inspired design
    - Smooth state transitions
    - Visual states: current, completed, future
    """
    # Signal emitted when clicked
    clicked = pyqtSignal(int)  # Step index

    def __init__(self, step_index, text_key, translator, parent=None):
        """
        Initialize the step indicator.

        Args:
            step_index: Index of this step (0-based)
            text_key: Translation key for the step text
            translator: Translator for localization
            parent: Parent widget
        """
        super().__init__(parent)
        self.step_index = step_index
        self.text_key = text_key
        self.translator = translator
        self.is_current = False
        self.is_completed = False
        self._hover = False
        self._scale = 1.0

        # Configure widget
        self.setObjectName("stepIndicator")
        self.setFixedSize(50, 62)  # Reduced size
        self.setMouseTracking(True)  # For hover effects
        self.setCursor(Qt.PointingHandCursor)

        # Set up UI
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements with premium styling."""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)  # Reduced margins
        layout.setSpacing(2)  # Reduced spacing
        layout.setAlignment(Qt.AlignCenter)

        # Circle container
        self.circle_container = QFrame()
        self.circle_container.setObjectName("stepCircle")
        self.circle_container.setFixedSize(32, 32)  # Reduced size

        # Circle layout
        circle_layout = QHBoxLayout(self.circle_container)
        circle_layout.setContentsMargins(0, 0, 0, 0)
        circle_layout.setAlignment(Qt.AlignCenter)

        # Number label
        self.number_label = QLabel(str(self.step_index + 1))
        self.number_label.setObjectName("stepNumber")
        self.number_label.setAlignment(Qt.AlignCenter)
        self.number_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Premium font
        font = QFont("SF Pro Display", 12)  # Smaller size
        font.setBold(True)
        self.number_label.setFont(font)

        # Checkmark for completed steps
        self.checkmark = QLabel("✓")
        self.checkmark.setObjectName("stepCheckmark")
        self.checkmark.setAlignment(Qt.AlignCenter)
        self.checkmark.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.checkmark.setFont(font)
        self.checkmark.hide()

        # Add to circle layout
        circle_layout.addWidget(self.number_label)
        circle_layout.addWidget(self.checkmark)

        # Add circle container to main layout
        layout.addWidget(self.circle_container, 0, Qt.AlignCenter)

        # Text label
        self.text_label = QLabel(self.translator.t(self.text_key))
        self.text_label.setObjectName("stepText")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Premium font for label
        text_font = QFont("SF Pro Text", 9)  # Smaller size
        self.text_label.setFont(text_font)

        # Add to main layout
        layout.addWidget(self.text_label, 0, Qt.AlignCenter)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)  # Reduced blur
        shadow.setColor(QColor(0, 0, 0, 30))  # Reduced opacity
        shadow.setOffset(0, 1)  # Reduced offset
        self.circle_container.setGraphicsEffect(shadow)

    def apply_theme(self):
        """Apply premium styling based on current state."""
        # Get theme colors
        highlight = get_color('highlight', '#4299E1')
        text_color = get_color('text', '#E2E8F0')
        card_bg = get_color('card_bg', '#1E3A5F')
        border_color = get_color('border', '#2C5282')

        # Derived colors
        highlight_darker = QColor(highlight).darker(115).name()
        highlight_lighter = QColor(highlight).lighter(115).name()
        card_bg_lighter = QColor(card_bg).lighter(110).name()

        # Update object names based on state
        if self.is_completed:
            self.circle_container.setObjectName("stepCircleCompleted")
            self.text_label.setObjectName("stepTextCompleted")
        elif self.is_current:
            self.circle_container.setObjectName("stepCircleCurrent")
            self.text_label.setObjectName("stepTextCurrent")
        else:
            self.circle_container.setObjectName("stepCircleFuture")
            self.text_label.setObjectName("stepTextFuture")

        # Apply styling based on state
        base_style = """
            #stepIndicator {
                background-color: transparent;
                border: none;
            }
        """

        if self.is_completed:
            # Completed state
            circle_style = f"""
                #stepCircleCompleted {{
                    background-color: {highlight};
                    color: white;
                    border-radius: 16px;  /* Half of circle size */
                    border: 1px solid {highlight_darker};
                }}

                #stepCheckmark {{
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                }}

                #stepTextCompleted {{
                    color: {highlight};
                    font-weight: 600;
                    font-size: 9px;
                    margin-top: 3px;
                }}
            """
            # Update shadow for completed
            shadow = self.circle_container.graphicsEffect()
            if shadow:
                shadow.setColor(QColor(0, 0, 50, 25))
                shadow.setBlurRadius(6)

        elif self.is_current:
            # Current state
            circle_style = f"""
                #stepCircleCurrent {{
                    background-color: {highlight_lighter};
                    color: white;
                    border-radius: 16px;  /* Half of circle size */
                    border: 2px solid white;
                }}

                #stepNumber {{
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }}

                #stepTextCurrent {{
                    color: {highlight};
                    font-weight: 600;
                    font-size: 9px;
                    margin-top: 3px;
                }}
            """
            # Enhanced shadow for current
            shadow = self.circle_container.graphicsEffect()
            if shadow:
                shadow.setColor(QColor(0, 0, 100, 50))
                shadow.setBlurRadius(8)

        else:
            # Future state
            circle_style = f"""
                #stepCircleFuture {{
                    background-color: {card_bg_lighter};
                    color: {text_color};
                    border-radius: 16px;  /* Half of circle size */
                    border: 1px solid {border_color};
                }}

                #stepNumber {{
                    color: {text_color};
                    font-size: 12px;
                }}

                #stepTextFuture {{
                    color: {text_color};
                    opacity: 0.7;
                    font-size: 9px;
                    margin-top: 3px;
                }}
            """
            # Subtle shadow for future
            shadow = self.circle_container.graphicsEffect()
            if shadow:
                shadow.setColor(QColor(0, 0, 0, 15))
                shadow.setBlurRadius(4)

        # Apply the complete style
        self.setStyleSheet(base_style + circle_style)

        # Show/hide elements based on state
        if self.is_completed:
            self.number_label.hide()
            self.checkmark.show()
        else:
            self.number_label.show()
            self.checkmark.hide()

    def set_state(self, is_current=False, is_completed=False, animate=True):
        """
        Set the visual state with premium animations.

        Args:
            is_current: Whether this is the current step
            is_completed: Whether this step is completed
            animate: Whether to animate the transition
        """
        # Skip if no change
        if self.is_current == is_current and self.is_completed == is_completed:
            return

        # Update state
        self.is_current = is_current
        self.is_completed = is_completed

        # Apply new styling
        self.apply_theme()

        # Animate if requested
        if animate:
            self._animate_state_change()

    def _animate_state_change(self):
        """Animate transition between states."""
        # Create scale animation for pulse effect
        scale_animation = QPropertyAnimation(self, b"scale")
        scale_animation.setDuration(200)  # Shorter duration
        scale_animation.setStartValue(1.0)
        scale_animation.setEndValue(1.12)  # Smaller scale
        scale_animation.setEasingCurve(QEasingCurve.OutQuad)

        # Scale back down after pulse
        scale_animation.finished.connect(self._animate_scale_down)

        # Start animation
        scale_animation.start()

    def _animate_scale_down(self):
        """Scale down after pulse animation."""
        scale_animation = QPropertyAnimation(self, b"scale")
        scale_animation.setDuration(150)  # Shorter duration
        scale_animation.setStartValue(1.12)  # Smaller scale
        scale_animation.setEndValue(1.0)
        scale_animation.setEasingCurve(QEasingCurve.OutQuad)
        scale_animation.start()

    def update_translations(self):
        """Update text when language changes."""
        self.text_label.setText(self.translator.t(self.text_key))

    # Property for scale animation
    def _get_scale(self):
        return self._scale

    def _set_scale(self, scale):
        if self._scale != scale:
            self._scale = scale
            self.circle_container.setFixedSize(int(32 * scale), int(32 * scale))

    scale = pyqtProperty(float, _get_scale, _set_scale)

    # Mouse event handlers
    def mousePressEvent(self, event):
        """Handle mouse press to emit clicked signal."""
        self.clicked.emit(self.step_index)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        """Handle mouse enter for hover effect."""
        self._hover = True
        # Add hover effect if not current or completed
        if not self.is_current and not self.is_completed:
            self.setGraphicsEffect(QGraphicsDropShadowEffect())
            self.graphicsEffect().setColor(QColor(0, 0, 0, 20))  # Reduced opacity
            self.graphicsEffect().setBlurRadius(8)
            self.graphicsEffect().setOffset(0, 1)  # Reduced offset
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave to end hover effect."""
        self._hover = False
        # Remove hover effect
        if not self.is_current and not self.is_completed:
            self.setGraphicsEffect(None)
        super().leaveEvent(event)


class StepConnector(QFrame):
    """
    A connector between step indicators showing progress.

    Features:
    - Clean, minimal design
    - Progress indicator
    - Smooth animations
    - Supports horizontal and vertical layouts
    """

    def __init__(self, vertical=False, parent=None):
        """Initialize the connector."""
        super().__init__(parent)
        self.setObjectName("stepConnector")
        self.vertical = vertical

        if vertical:
            self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
            self.setFixedWidth(4)  # Smaller width
        else:
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.setFixedHeight(4)  # Smaller height

        # Progress tracking
        self._progress = 0.0
        self._is_completed = False

        # Set up UI
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements."""
        # Main layout
        if self.vertical:
            layout = QVBoxLayout(self)
        else:
            layout = QHBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Base track (shown always)
        self.track = QFrame()
        self.track.setObjectName("connectorTrack")

        if self.vertical:
            self.track.setFixedWidth(2)  # Thinner
        else:
            self.track.setFixedHeight(2)  # Thinner

        # Progress overlay (grows as step is completed)
        self.progress_overlay = QFrame()
        self.progress_overlay.setObjectName("connectorProgress")

        if self.vertical:
            self.progress_overlay.setFixedWidth(2)  # Thinner
            self.progress_overlay.setMaximumHeight(0)  # Initially hidden
        else:
            self.progress_overlay.setFixedHeight(2)  # Thinner
            self.progress_overlay.setMaximumWidth(0)  # Initially hidden

        # Add track to layout
        layout.addWidget(self.track, 1)

        # Progress overlay positioned absolutely
        self.progress_overlay.setParent(self)

        if self.vertical:
            self.progress_overlay.move(1, 0)  # Centered
        else:
            self.progress_overlay.move(0, 1)  # Centered

    def update_progress(self):
        """Update the visual progress indicator."""
        if self.vertical:
            # Calculate height based on progress
            progress_height = int(self.height() * self._progress)
            # Update overlay height
            self.progress_overlay.setFixedHeight(progress_height)
            # Update position (always centered horizontally)
            self.progress_overlay.move(1, 0)
        else:
            # Calculate width based on progress
            progress_width = int(self.width() * self._progress)
            # Update overlay width
            self.progress_overlay.setFixedWidth(progress_width)
            # Update position (always centered vertically)
            self.progress_overlay.move(0, 1)

    def apply_theme(self):
        """Apply premium styling."""
        # Get theme colors
        highlight = get_color('highlight', '#4299E1')
        border_color = get_color('border', '#2C5282')

        # Apply styling
        self.setStyleSheet(f"""
            #stepConnector {{
                background-color: transparent;
                border: none;
            }}

            #connectorTrack {{
                background-color: {border_color};
                border-radius: 1px;
            }}

            #connectorProgress {{
                background-color: {highlight};
                border-radius: 1px;
            }}
        """)

    def set_completed(self, completed, animate=True):
        """
        Set the completed state with animation.

        Args:
            completed: Whether this connector is completed
            animate: Whether to animate the transition
        """
        # Skip if no change
        if self._is_completed == completed:
            return

        # Update state
        self._is_completed = completed

        # Update visually
        if animate:
            self.animate_progress(1.0 if completed else 0.0)
        else:
            self._progress = 1.0 if completed else 0.0
            self.update_progress()

    def animate_progress(self, target_progress, duration=400):  # Shorter duration
        """
        Animate the progress indicator.

        Args:
            target_progress: Target progress value (0.0 to 1.0)
            duration: Animation duration in milliseconds
        """
        # Create animation
        animation = QPropertyAnimation(self, b"progress")
        animation.setDuration(duration)
        animation.setStartValue(self._progress)
        animation.setEndValue(target_progress)
        animation.setEasingCurve(QEasingCurve.OutQuart)
        animation.start()

    # Property for progress animation
    def _get_progress(self):
        return self._progress

    def _set_progress(self, progress):
        if self._progress != progress:
            self._progress = progress
            self.update_progress()

    progress = pyqtProperty(float, _get_progress, _set_progress)

    def resizeEvent(self, event):
        """Handle resize to update progress indicator."""
        super().resizeEvent(event)
        self.update_progress()


class StepsPanel(QFrame):
    """
    A panel displaying step indicators with connectors.

    Features:
    - Clean, premium design
    - Automatic layout
    - Step clicking
    """
    # Signal when a step is clicked
    step_clicked = pyqtSignal(int)  # Step index

    def __init__(self, translator, parent=None):
        """
        Initialize the steps panel.

        Args:
            translator: Translator for localization
            parent: Parent widget
        """
        super().__init__(parent)
        self.translator = translator
        self.step_indicators = []
        self.step_connectors = []
        self.current_step = 0

        # Set up UI
        self.setObjectName("stepsPanel")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(70)  # Reduced height
        self.setMaximumHeight(80)  # Limited maximum height

        # Initialize UI
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements."""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 5, 15, 5)  # Reduced margins
        layout.setSpacing(0)  # No spacing, connectors fill the gap

        # Step definitions
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
            # Create indicator
            indicator = StepIndicator(i, text, self.translator)
            indicator.clicked.connect(self.on_step_click)
            layout.addWidget(indicator)
            self.step_indicators.append(indicator)

            # Add connector between steps (except after last step)
            if i < len(step_texts) - 1:
                connector = StepConnector()
                layout.addWidget(connector, 1)  # Takes all available space
                self.step_connectors.append(connector)

    def apply_theme(self):
        """Apply premium styling."""
        # Get theme colors
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        border_color = get_color('border', '#2C5282')

        # Apply styling
        self.setStyleSheet(f"""
            #stepsPanel {{
                background-color: {QColor(card_bg).lighter(102).name()};
                border-radius: 6px;  /* Smaller radius */
                border: 1px solid {QColor(border_color).lighter(105).name()};
            }}
        """)

    def set_current_step(self, step_index, animate=True):
        """
        Set the current step.

        Args:
            step_index: Index of the current step
            animate: Whether to animate the transition
        """
        # Skip if no change
        if self.current_step == step_index:
            return

        # Store previous state
        previous_step = self.current_step
        self.current_step = step_index

        # Update indicators
        for i, indicator in enumerate(self.step_indicators):
            is_completed = i < step_index
            is_current = i == step_index
            indicator.set_state(is_current, is_completed, animate)

        # Update connectors
        for i, connector in enumerate(self.step_connectors):
            connector.set_completed(i < step_index, animate)

    def on_step_click(self, step_index):
        """Handle click on a step indicator."""
        # Emit signal
        self.step_clicked.emit(step_index)

    def update_translations(self):
        """Update translations when language changes."""
        for indicator in self.step_indicators:
            indicator.update_translations()


class StepDotsIndicator(QFrame):
    """
    A simplified dots-style step indicator for mobile/compact views.

    Features:
    - Minimal, clean design with dots
    - Animated state changes
    - Touch-friendly
    """
    # Signal when a dot is clicked
    step_clicked = pyqtSignal(int)  # Step index

    def __init__(self, step_count, translator, parent=None):
        """
        Initialize the dots indicator.

        Args:
            step_count: Number of steps
            translator: Translator for localization
            parent: Parent widget
        """
        super().__init__(parent)
        self.step_count = step_count
        self.translator = translator
        self.current_step = 0
        self.dot_frames = []

        # Set up UI
        self.setObjectName("stepDotsIndicator")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Initialize UI
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements."""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(8)

        # Create dots
        for i in range(self.step_count):
            dot = QFrame()
            dot.setObjectName(f"stepDot_{i}")
            dot.setFixedSize(10, 10)
            dot.setCursor(Qt.PointingHandCursor)
            dot.mousePressEvent = lambda event, idx=i: self.step_clicked.emit(idx)

            layout.addWidget(dot)
            self.dot_frames.append(dot)

    def apply_theme(self):
        """Apply premium styling."""
        # Get theme colors
        highlight = get_color('highlight', '#4299E1')
        border_color = get_color('border', '#2C5282')

        # Apply base styling
        self.setStyleSheet(f"""
            #stepDotsIndicator {{
                background-color: transparent;
                border: none;
            }}
        """)

        # Apply dot styling based on current step
        self.update_dot_styles()

    def update_dot_styles(self):
        """Update styling of all dots."""
        # Get theme colors
        highlight = get_color('highlight', '#4299E1')
        border_color = get_color('border', '#2C5282')

        # Apply styling to each dot
        for i, dot in enumerate(self.dot_frames):
            if i == self.current_step:
                # Current step
                dot.setStyleSheet(f"""
                    #stepDot_{i} {{
                        background-color: {highlight};
                        border-radius: 5px;
                    }}
                """)
            elif i < self.current_step:
                # Completed step
                dot.setStyleSheet(f"""
                    #stepDot_{i} {{
                        background-color: {highlight};
                        opacity: 0.7;
                        border-radius: 5px;
                    }}
                """)
            else:
                # Future step
                dot.setStyleSheet(f"""
                    #stepDot_{i} {{
                        background-color: {border_color};
                        border-radius: 5px;
                    }}
                """)

    def set_current_step(self, step_index):
        """
        Set the current step.

        Args:
            step_index: Index of the current step
        """
        # Skip if no change or invalid index
        if self.current_step == step_index or step_index < 0 or step_index >= self.step_count:
            return

        # Update state
        self.current_step = step_index

        # Update styling
        self.update_dot_styles()

        # Animate current dot
        self._animate_current_dot()

    def _animate_current_dot(self):
        """Animate the current dot for emphasis."""
        if 0 <= self.current_step < len(self.dot_frames):
            dot = self.dot_frames[self.current_step]

            # Create pulse animation
            animation = QPropertyAnimation(dot, b"minimumSize")
            animation.setDuration(350)
            animation.setStartValue(dot.minimumSize())
            animation.setEndValue(dot.minimumSize() + QSize(4, 4))
            animation.setEasingCurve(QEasingCurve.OutQuad)

            # Return to original size
            animation.finished.connect(lambda: self._animate_dot_reset(dot))

            # Start animation
            animation.start()

    def _animate_dot_reset(self, dot):
        """Reset dot size after pulse."""
        reset_animation = QPropertyAnimation(dot, b"minimumSize")
        reset_animation.setDuration(200)
        reset_animation.setStartValue(dot.minimumSize())
        reset_animation.setEndValue(QSize(10, 10))
        reset_animation.setEasingCurve(QEasingCurve.InOutQuad)
        reset_animation.start()