"""
Base class for all navigation step widgets.
Provides common functionality and standardized interfaces with elegant implementation.
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy,
                             QGraphicsOpacityEffect, QHBoxLayout)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve, QTimer
from PyQt5.QtGui import QColor, QFont
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.base')

class BaseStepWidget(QWidget):
    """
    Base class for all navigation step widgets.

    Provides common functionality including:
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

        # Configure responsive sizing
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setMinimumSize(0, 0)  # Remove minimum size constraints for proper scaling

        # Initialize UI
        self.setup_ui()
        self.apply_theme()

    def sizeHint(self):
        """Return a modest default size that won't distort layouts."""
        return QSize(300, 400)  # Larger default size for premium appearance

    def setup_ui(self):
        """Initialize and arrange UI elements with elegant spacing and premium styling."""
        # Main layout with refined spacing
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins to use space efficiently
        self.main_layout.setSpacing(8)  # Reduced spacing

        # IMPROVED: Set the widget to expand in both directions
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add a card container for the content with premium look
        self.content_frame = QFrame(self)
        self.content_frame.setObjectName("stepContentFrame")
        self.content_layout = QVBoxLayout(self.content_frame)
        self.content_layout.setContentsMargins(15, 15, 15, 15)  # Inner padding
        self.content_layout.setSpacing(12)

        # IMPROVED: Set the content frame to expand in both directions
        self.content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Title with premium typography
        self.title = QLabel()
        self.title.setObjectName("stepTitle")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Enhanced typography with premium font
        font = self.title.font()
        font.setBold(True)
        font.setPointSize(16)  # Larger size for more impact
        self.title.setFont(font)

        self.content_layout.addWidget(self.title)

        # Subtle separator for visual hierarchy
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setObjectName("titleSeparator")
        self.separator.setMaximumHeight(1)
        self.content_layout.addWidget(self.separator)

        # Loading indicator with sophisticated design
        self.loading_frame = QFrame()
        self.loading_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.loading_frame.setObjectName("loadingFrame")

        loading_layout = QVBoxLayout(self.loading_frame)
        loading_layout.setContentsMargins(10, 10, 10, 10)

        # Add animated loading indicator (spinner or progress bar)
        # For now, just use a better styled text label
        self.loading_label = QLabel(self.translator.t('loading'))
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setObjectName("loadingLabel")
        self.loading_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Enhanced loading text
        loading_font = self.loading_label.font()
        loading_font.setBold(True)
        loading_font.setPointSize(14)  # Larger for better visibility
        self.loading_label.setFont(loading_font)

        loading_layout.addWidget(self.loading_label)
        self.content_layout.addWidget(self.loading_frame)
        self.loading_frame.hide()

        # Help text with elegant styling
        self.help_text = QLabel()
        self.help_text.setObjectName("helpText")
        self.help_text.setAlignment(Qt.AlignCenter)
        self.help_text.setWordWrap(True)
        self.help_text.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Apply subtle font styling to help text
        help_font = self.help_text.font()
        help_font.setItalic(True)
        help_font.setPointSize(13)  # Slightly larger for better readability
        self.help_text.setFont(help_font)

        # IMPROVED: Add stretch after title section to push content and help text apart
        self.content_layout.addStretch(0)

        # Add to main layout (not content frame)
        self.main_layout.addWidget(self.content_frame, 1)  # Takes all available space

        # IMPROVED: Don't add stretch in content layout - each widget will manage its own space
        # self.content_layout.addStretch(1)  # Remove this line as it can cause layout issues

        # Add help text to the bottom of content layout
        self.content_layout.addWidget(self.help_text)

        # IMPROVED: Set minimum sizes
        self.setMinimumSize(600, 400)
        self.content_frame.setMinimumSize(580, 380)

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

        # Content frame styling
        content_frame_style = f"""
            /* Premium content frame styling */
            #stepContentFrame {{
                background-color: {card_bg};
                border-radius: 12px;
                border: 1px solid {border_color};
                padding: 5px;
            }}
            
            /* Title separator styling */
            #titleSeparator {{
                background-color: {border_color};
                opacity: 0.5;
                margin-left: 20px;
                margin-right: 20px;
                margin-bottom: 10px;
            }}
        """

        # Set the entire styling with premium appearance
        self.setStyleSheet(f"""
            /* Base widget styling */
            BaseStepWidget {{
                background-color: {bg_color};
            }}
            
            /* Title styling with premium typography */
            #stepTitle {{
                color: {text_color};
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 10px;
                padding: 6px;
                font-family: "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
                letter-spacing: -0.2px;
            }}
            
            {content_frame_style}
            
            /* Standard label styling */
            QLabel {{
                color: {text_color};
                font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
            }}
            
            /* Loading frame with premium styling */
            #loadingFrame {{
                background-color: {card_bg_lighter};
                border-radius: 8px;
                border: 1px solid {highlight};
                margin: 10px 20px;
                padding: 8px;
            }}
            
            /* Loading label with accent color */
            #loadingLabel {{
                color: {highlight};
                font-weight: bold;
                padding: 5px;
                font-size: 14px;
            }}
            
            /* Help text with refined styling */
            #helpText {{
                color: {secondary_text};
                font-style: italic;
                margin-top: 12px;
                margin-bottom: 5px;
                padding: 10px 12px;
                background-color: {card_bg};
                border-radius: 8px;
                border: 1px solid {border_color};
                font-size: 13px;
                line-height: 1.4;
            }}
            
            /* Style for all buttons within this widget to ensure consistency */
            QPushButton {{
                background-color: {highlight};
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
                font-weight: 600;
                border: none;
            }}
            
            QPushButton:hover {{
                background-color: {highlight_lighter};
            }}
            
            QPushButton:pressed {{
                background-color: {highlight_darker};
            }}
            
            /* Style for input elements to match the theme */
            QLineEdit, QComboBox {{
                background-color: {card_bg_lighter};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 8px;
                font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
            }}
            
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {highlight};
                background-color: {QColor(card_bg_lighter).darker(102).name()};
            }}
        """)

        # Apply background color directly to this widget for better compatibility
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(bg_color))
        self.setPalette(palette)

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
        self.setGraphicsEffect(QGraphicsOpacityEffect(self))
        self.graphicsEffect().setOpacity(0)

        # Then animate with a slight slide-up effect using a QTimer
        # for the premium appearance many iOS/Android apps use
        QTimer.singleShot(50, lambda: self._animate_opacity(0, 1, 350))

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
            self.loading_frame.setGraphicsEffect(QGraphicsOpacityEffect(self.loading_frame))
            self.loading_frame.graphicsEffect().setOpacity(0)
            self.loading_frame.show()

            # Animate fade in
            loading_anim = self._animate_widget_opacity(self.loading_frame, 0, 1, 250)

            # Store reference to widget for cleanup in finished handler
            loading_anim.target_widget = self.loading_frame
        else:
            # Animate fade out
            fade_out = self._animate_widget_opacity(self.loading_frame, 1, 0, 250)
            if fade_out:
                # Store reference to widget for cleanup in finished handler
                fade_out.target_widget = self.loading_frame
                fade_out.finished.connect(self.loading_frame.hide)

    def handle_error(self, error_msg):
        """
        Handle an error in a standardized, elegant way.

        Args:
            error_msg (str): The error message
        """
        self.show_loading(False)
        logger.error(f"Error in {self.__class__.__name__}: {error_msg}")

        # In a real implementation, you might show an error message
        # with an elegant animation or visual treatment

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
        opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(start_value)

        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)  # Premium smooth easing

        # Keep track of active animations
        self.active_animations.append(animation)
        animation.finished.connect(lambda: self._on_animation_finished(animation))

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
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(start_value)

        animation = QPropertyAnimation(opacity_effect, b"opacity")
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.OutCubic)  # Premium smooth easing

        # Keep track of active animations
        self.active_animations.append(animation)
        animation.finished.connect(lambda: self._on_animation_finished(animation))

        animation.start()
        return animation

    def _on_animation_finished(self, animation):
        """Handle animation completion with proper cleanup."""
        if animation in self.active_animations:
            self.active_animations.remove(animation)

        # Additional cleanup if needed
        if hasattr(animation, 'target_widget'):
            if animation.endValue() == 0.0:  # If this was a fade-out
                animation.target_widget.hide()

    def _cancel_animations(self):
        """Cancel all active animations with proper cleanup."""
        for animation in self.active_animations.copy():
            animation.stop()

        self.active_animations.clear()