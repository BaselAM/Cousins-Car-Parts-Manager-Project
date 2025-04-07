"""
Base classes for the parts navigation system.

This module provides the foundation for all step widgets and the navigation container.
It ensures consistent behavior and styling across all steps.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy,
                             QGraphicsOpacityEffect, QHBoxLayout, QStackedWidget)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QColor, QFont, QPainter, QPainterPath

from logger import get_logger
from themes import get_color

logger = get_logger('parts_navigation.base')


class BaseStepWidget(QWidget):
    """
    Base class for all navigation step widgets.

    Provides:
    - Standard layout structure with premium styling
    - Loading indicator with animation
    - Help text with elegant typography
    - Signal for step completion
    - Responsive sizing
    - Theme application
    - Animation support
    """
    # Signal emitted when this step is completed
    step_completed = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        """
        Initialize the base step widget.

        Args:
            translator: Translation service for localization
            db: Database connection
            parent: Parent widget
        """
        super().__init__(parent)
        self.translator = translator
        self.db = db
        self.step_data = {}  # Data for this step
        self.is_loading = False
        self.active_animations = []

        # Configure responsive sizing - CRITICAL for proper display
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Reduced minimum size to be more flexible
        self.setMinimumSize(550, 350)

        # Initialize UI
        self.setup_ui()
        self.apply_theme()

    def sizeHint(self):
        """Return a reasonable default size."""
        return QSize(800, 600)  # Good starting size

    def setup_ui(self):
        """Initialize and arrange UI elements with compact styling."""
        # Main layout with minimal margins
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(4)  # Minimized spacing

        # Add a card container for the content with premium look
        self.content_frame = QFrame(self)
        self.content_frame.setObjectName("stepContentFrame")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(8, 8, 8, 8)  # Reduced margins
        self.content_layout.setSpacing(4)  # Minimized spacing

        # Set proper sizing for content frame - CRITICAL for layout
        self.content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a compact header with title and separator
        header_container = QWidget()
        header_container.setMaximumHeight(36)  # Reduced height
        header_layout = QVBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(2)  # Minimal spacing

        # Title with premium typography but smaller
        self.title = QLabel()
        self.title.setObjectName("stepTitle")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Smaller font
        font = QFont("SF Pro Display", 14)  # Reduced from 16
        font.setBold(True)
        self.title.setFont(font)

        header_layout.addWidget(self.title)

        # Subtle separator
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setObjectName("titleSeparator")
        self.separator.setMaximumHeight(1)
        header_layout.addWidget(self.separator)

        # Add header to content layout
        self.content_layout.addWidget(header_container)

        # Loading indicator with compact design
        self.loading_frame = QFrame()
        self.loading_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.loading_frame.setObjectName("loadingFrame")
        self.loading_frame.setMaximumHeight(36)  # Reduced height

        loading_layout = QVBoxLayout(self.loading_frame)
        loading_layout.setContentsMargins(4, 4, 4, 4)  # Reduced margins

        # Add loading label
        self.loading_label = QLabel(self.translator.t('loading'))
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setObjectName("loadingLabel")
        self.loading_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Smaller loading text
        loading_font = QFont("SF Pro Text", 12)  # Reduced from 14
        loading_font.setBold(True)
        self.loading_label.setFont(loading_font)

        loading_layout.addWidget(self.loading_label)
        self.content_layout.addWidget(self.loading_frame)
        self.loading_frame.hide()

        # Content area - will be filled by subclasses
        self.content_layout.addStretch(1)  # Push content to the top

        # Help text at the bottom, but much more compact
        self.help_text = QLabel()
        self.help_text.setObjectName("helpText")
        self.help_text.setAlignment(Qt.AlignCenter)
        self.help_text.setWordWrap(True)
        self.help_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.help_text.setMaximumHeight(36)  # Reduced height

        # Smaller help text
        help_font = QFont("SF Pro Text", 11)  # Reduced from 13
        help_font.setItalic(True)
        self.help_text.setFont(help_font)

        # Add help text to content layout
        self.content_layout.addWidget(self.help_text)

        # Add content frame to main layout - CRITICAL: give it a high stretch factor
        self.main_layout.addWidget(self.content_frame, 10)  # Takes all available space

    def apply_theme(self):
        """Apply current theme with elegant styling that matches the system theme."""
        # Get theme colors with fallbacks to ensure consistency
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        text_color = get_color('text', '#E2E8F0')
        border_color = get_color('border', '#2C5282')
        highlight = get_color('highlight', '#4299E1')
        secondary_text = get_color('secondary_text', '#A0AEC0')

        # Compute derived colors for enhanced styling
        card_bg_lighter = QColor(card_bg).lighter(108).name()
        highlight_lighter = QColor(highlight).lighter(115).name()
        highlight_darker = QColor(highlight).darker(115).name()

        # Create rgba format for the highlight with transparency
        h_color = QColor(highlight)
        highlight_trans = f"rgba({h_color.red()}, {h_color.green()}, {h_color.blue()}, 0.2)"

        # Apply background color directly to this widget for better compatibility
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(bg_color))
        self.setPalette(palette)

        # Set the entire styling with premium appearance
        self.setStyleSheet(f"""
            /* Base widget styling */
            QWidget {{
                color: {text_color};
                font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
            }}

            /* Content frame styling */
            #stepContentFrame {{
                background-color: {card_bg};
                border-radius: 10px;
                border: none; /* Removed border for cleaner look */
                padding: 4px; /* Reduced padding */
            }}

            /* Title styling with premium typography */
            #stepTitle {{
                color: {text_color};
                font-weight: bold;
                font-size: 14px; /* Reduced size */
                margin-bottom: 6px; /* Reduced margin */
                padding: 4px; /* Reduced padding */
                font-family: "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
                letter-spacing: -0.2px;
            }}

            /* Title separator styling */
            #titleSeparator {{
                background-color: {border_color};
                opacity: 0.5;
                margin-left: 20px;
                margin-right: 20px;
                margin-bottom: 6px; /* Reduced margin */
            }}

            /* Loading frame with premium styling */
            #loadingFrame {{
                background-color: {card_bg_lighter};
                border-radius: 6px; /* Reduced radius */
                border: 1px solid {highlight};
                margin: 6px 16px; /* Reduced margins */
                padding: 6px; /* Reduced padding */
            }}

            /* Loading label with accent color */
            #loadingLabel {{
                color: {highlight};
                font-weight: bold;
                padding: 2px; /* Reduced padding */
                font-size: 12px; /* Reduced font size */
            }}

            /* Help text with refined styling */
            #helpText {{
                color: {secondary_text};
                font-style: italic;
                margin-top: 6px; /* Reduced margin */
                margin-bottom: 2px; /* Reduced margin */
                padding: 6px 8px; /* Reduced padding */
                background-color: transparent;
                border-radius: 6px; /* Reduced radius */
                font-size: 11px; /* Reduced font size */
                line-height: 1.3; /* Reduced line height */
            }}

            /* Style for all buttons within this widget to ensure consistency */
            QPushButton {{
                background-color: {highlight};
                color: white;
                border-radius: 6px;
                padding: 6px 14px; /* Reduced padding */
                font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
                font-weight: 600;
                font-size: 13px; /* Reduced font size */
                border: none;
            }}

            QPushButton:hover {{
                background-color: {highlight_lighter};
            }}

            QPushButton:pressed {{
                background-color: {highlight_darker};
            }}

            QPushButton:disabled {{
                background-color: {secondary_text};
                color: {text_color};
                opacity: 0.7;
            }}

            #primaryButton {{
                background-color: {highlight};
                color: white;
                font-weight: bold;
            }}

            #primaryButton:hover {{
                background-color: {highlight_lighter};
            }}

            #primaryButton:pressed {{
                background-color: {highlight_darker};
            }}

            /* Style for input elements to match the theme */
            QLineEdit, QComboBox {{
                background-color: {card_bg_lighter};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 6px; /* Reduced padding */
                font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
                font-size: 13px; /* Reduced font size */
            }}

            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border: 1px solid {highlight};
                background-color: {QColor(card_bg_lighter).darker(102).name()};
            }}
        """)

    def update_translations(self):
        """Update all translatable text with elegant handling."""
        # Update loading text with current language
        if hasattr(self, 'loading_label'):
            self.loading_label.setText(self.translator.t('loading'))

    def reset(self):
        """Reset this step's data with elegant animations."""
        # Cancel any active animations
        self._cancel_animations()

        # Reset data
        self.step_data = {}

    def on_show(self):
        """
        Called when this step is shown with premium entrance animation.

        Override in subclasses to initialize data or UI when shown.
        Base implementation adds a subtle fade-in animation.
        """
        # First ensure widget is visible but transparent
        if not self.graphicsEffect() or not isinstance(self.graphicsEffect(), QGraphicsOpacityEffect):
            self.setGraphicsEffect(QGraphicsOpacityEffect(self))

        # CRITICAL: Start with higher opacity (0.7) instead of 0
        self.graphicsEffect().setOpacity(0.7)

        # Use a shorter animation duration (150ms instead of 350ms)
        QTimer.singleShot(10, lambda: self._animate_opacity(0.7, 1, 150))

    def on_hide(self):
        """
        Called when this step is hidden.

        Override in subclasses to clean up when hidden.
        Base implementation cancels any active animations.
        """
        # Cancel any active animations
        self._cancel_animations()

    def can_proceed(self):
        """
        Check if user can proceed to next step.

        Default implementation checks if step_data is not empty.
        Override in subclasses for specific logic.

        Returns:
            bool: True if can proceed, False otherwise
        """
        return bool(self.step_data)

    def get_step_data(self):
        """
        Get the data for this step.

        Returns:
            dict: The step data
        """
        return self.step_data

    def set_previous_step_data(self, data):
        """
        Set data from previous step.

        Args:
            data: Data from the previous step
        """
        pass

    def show_loading(self, show=True):
        """
        Show or hide the loading indicator with elegant animation.

        Args:
            show (bool): Whether to show or hide the loading indicator
        """
        self.is_loading = show

        if show:
            # Reset opacity and make visible before animating
            if not self.loading_frame.graphicsEffect() or not isinstance(self.loading_frame.graphicsEffect(), QGraphicsOpacityEffect):
                self.loading_frame.setGraphicsEffect(QGraphicsOpacityEffect(self.loading_frame))

            self.loading_frame.graphicsEffect().setOpacity(0)
            self.loading_frame.show()

            # Animate fade in
            loading_anim = self._animate_widget_opacity(self.loading_frame, 0, 1, 250)

            # Important: Only set target_widget if animation was created
            if loading_anim:
                loading_anim.target_widget = self.loading_frame
        else:
            # Animate fade out
            fade_out = self._animate_widget_opacity(self.loading_frame, 1, 0, 250)
            if fade_out:
                # Store reference to widget for cleanup in finished handler
                fade_out.target_widget = self.loading_frame

                # Use a proper function instead of connecting directly to hide
                def hide_loading_frame():
                    self.loading_frame.hide()

                fade_out.finished.connect(hide_loading_frame)

    def handle_error(self, error_msg):
        """
        Handle an error in a standardized, elegant way.

        Args:
            error_msg (str): The error message
        """
        self.show_loading(False)
        logger.error(f"Error in {self.__class__.__name__}: {error_msg}")

    def _animate_opacity(self, start_value, end_value, duration):
        """
        Animate the opacity of the entire widget with premium smooth transitions.

        Args:
            start_value (float): Starting opacity (0.0 to 1.0)
            end_value (float): Ending opacity (0.0 to 1.0)
            duration (int): Animation duration in milliseconds

        Returns:
            QPropertyAnimation: The animation object
        """
        # Create effect if needed, or reuse existing one
        if not self.graphicsEffect() or not isinstance(self.graphicsEffect(), QGraphicsOpacityEffect):
            opacity_effect = QGraphicsOpacityEffect(self)
            self.setGraphicsEffect(opacity_effect)
        else:
            opacity_effect = self.graphicsEffect()

        opacity_effect.setOpacity(start_value)

        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)  # Premium smooth easing

        # Keep track of active animations
        self.active_animations.append(animation)

        # IMPORTANT: Use a stable function connection instead of lambda
        animation.finished.connect(self._on_animation_finished)

        # CRITICAL: Store references to prevent GC issues - explicitly set target_widget
        animation.target_widget = self
        animation._effect = opacity_effect

        animation.start()
        return animation

    def _animate_widget_opacity(self, widget, start_value, end_value, duration):
        """
        Animate the opacity of a specific widget with premium smooth transitions.

        Args:
            widget (QWidget): The widget to animate
            start_value (float): Starting opacity (0.0 to 1.0)
            end_value (float): Ending opacity (0.0 to 1.0)
            duration (int): Animation duration in milliseconds

        Returns:
            QPropertyAnimation: The animation object
        """
        # Safety check
        if widget is None:
            logger.warning("Attempted to animate a None widget")
            return None

        # Create effect if needed, or reuse existing
        if not widget.graphicsEffect() or not isinstance(widget.graphicsEffect(), QGraphicsOpacityEffect):
            opacity_effect = QGraphicsOpacityEffect(widget)
            widget.setGraphicsEffect(opacity_effect)
        else:
            opacity_effect = widget.graphicsEffect()

        opacity_effect.setOpacity(start_value)

        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)  # Premium smooth easing

        # Keep track of active animations
        self.active_animations.append(animation)

        # IMPORTANT: Use a stable function connection instead of lambda
        animation.finished.connect(self._on_animation_finished)

        # CRITICAL: Store references to prevent GC issues - explicitly set target_widget
        animation.target_widget = widget
        animation._effect = opacity_effect
        animation._widget = widget

        animation.start()
        return animation

    def _on_animation_finished(self, animation=None):
        """Handle animation completion with proper cleanup."""
        # If called directly as a slot, the sender is the animation
        if animation is None:
            animation = self.sender()

        if animation is None:
            return

        # Remove from active animations if present
        if animation in self.active_animations:
            self.active_animations.remove(animation)

        # Additional cleanup if needed
        if hasattr(animation, 'target_widget') and animation.target_widget is not None:
            if hasattr(animation, 'endValue') and animation.endValue() == 0.0:  # If this was a fade-out
                animation.target_widget.hide()

    def _cancel_animations(self):
        """Cancel all active animations with proper cleanup."""
        for animation in self.active_animations.copy():
            animation.stop()

        self.active_animations.clear()


class NavigationContainer(QWidget):
    """
    Container for the hierarchical parts navigation.

    Manages:
    - Step widgets
    - Step indicators
    - Navigation flow
    - Transitions between steps
    """

    def __init__(self, translator, db, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.db = db
        self.setObjectName("partsNavigationContainer")

        # Set up a proper size policy for responsiveness
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(800, 600)  # Minimum size to look good

        # Initialize UI
        self.setup_ui()
        self.apply_theme()

        # Will hold current animation
        self._current_animation = None

        # Initialize with first step
        self.go_to_step(0)

    def setup_ui(self):
        """Initialize and arrange UI elements with premium styling."""
        # Will be implemented in full container class
        pass

    def apply_theme(self):
        """Apply current theme with elegant styling."""
        # Will be implemented in full container class
        pass

    def create_step_widgets(self):
        """Create all the navigation step widgets."""
        # Will be implemented in full container class
        pass

    def go_to_step(self, step_index):
        """Navigate to a specific step with premium transitions."""
        # Will be implemented in full container class
        pass

    def animate_transition(self, from_index, to_index):
        """Animate the transition between steps with premium effects."""
        # Will be implemented in full container class
        pass

    def update_navigation_buttons(self):
        """Update the state of the navigation buttons with premium styling."""
        # Will be implemented in full container class
        pass