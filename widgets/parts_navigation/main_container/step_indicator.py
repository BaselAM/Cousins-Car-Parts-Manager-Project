"""
Premium step indicator widget for the parts navigation system.
Features an elegant, iOS-inspired design with refined animations.
Enhanced for better visibility and theme integration.
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QLabel, QSizePolicy,
                             QGraphicsDropShadowEffect, QHBoxLayout)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize, pyqtProperty
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QPainterPath

from themes import get_color

class PremiumStepIndicator(QFrame):
    """A premium visual indicator for a step in the navigation process."""

    def __init__(self, number, text, translator):
        super().__init__()
        self.number = number
        self.text = text
        self.translator = translator
        self.is_current = False
        self.is_completed = False
        self._hover = False
        self._progress = 0.0  # For progress animation (0.0 to 1.0)

        # For animations
        self._animation = None
        self._scale = 1.0
        self._opacity = 1.0

        self.setup_ui()
        self.apply_theme()

        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)

    def setup_ui(self):
        """Initialize and arrange UI elements with premium spacing and visibility."""
        self.setObjectName("premiumStepIndicator")
        self.setFixedSize(60, 70)  # Fixed size for consistency

        # Main layout with refined spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        # Circle container for better animation control
        self.circle_container = QFrame()
        self.circle_container.setObjectName("stepCircleContainer")
        self.circle_container.setFixedSize(40, 40)

        # Circle layout
        circle_layout = QHBoxLayout(self.circle_container)
        circle_layout.setContentsMargins(0, 0, 0, 0)
        circle_layout.setAlignment(Qt.AlignCenter)

        # Number label
        self.number_label = QLabel(str(self.number))
        self.number_label.setObjectName("stepNumber")
        self.number_label.setAlignment(Qt.AlignCenter)
        self.number_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Use elegant font
        font = QFont()
        font.setFamily("Helvetica Neue")
        font.setBold(True)
        font.setPointSize(13)
        self.number_label.setFont(font)

        # Checkmark for completed steps (initially hidden)
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

        # Text label with refined typography
        self.text_label = QLabel(self.translator.t(self.text))
        self.text_label.setObjectName("stepText")
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        # Use elegant font for label
        text_font = QFont()
        text_font.setFamily("Helvetica Neue")
        text_font.setPointSize(10)  # Slightly larger for better readability
        self.text_label.setFont(text_font)

        layout.addWidget(self.text_label, 0, Qt.AlignCenter)

    def apply_theme(self):
        """Apply premium styling based on system theme colors for better integration."""
        # Get theme colors with fallbacks
        highlight = get_color('highlight', '#4299E1')
        text_color = get_color('text', '#E2E8F0')
        card_bg = get_color('card_bg', '#1E3A5F')
        border_color = get_color('border', '#2C5282')

        # Compute derived colors for gradients and effects
        highlight_darker = QColor(highlight).darker(115).name()
        highlight_lighter = QColor(highlight).lighter(115).name()
        card_bg_lighter = QColor(card_bg).lighter(110).name()

        # Apply shadow effect - softer for better integration
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 40))  # Lighter shadow
        shadow.setOffset(0, 2)
        self.circle_container.setGraphicsEffect(shadow)

        # Different styling based on state
        if self.is_completed:
            # Apply completed state styling
            self.circle_container.setStyleSheet(f"""
                #stepCircleCompleted {{
                    background-color: {highlight};
                    color: white;
                    border-radius: 20px;
                    border: 1px solid {highlight_darker};
                }}
            """)

            self.text_label.setStyleSheet(f"""
                #stepTextCompleted {{
                    color: {highlight};
                    font-weight: 600;
                    margin-top: 5px;
                }}
            """)
        elif self.is_current:
            # Apply current state styling
            self.circle_container.setStyleSheet(f"""
                #stepCircleCurrent {{
                    background-color: {highlight_lighter};
                    color: white;
                    border-radius: 20px;
                    border: 2px solid white;
                }}
            """)

            self.text_label.setStyleSheet(f"""
                #stepTextCurrent {{
                    color: {highlight};
                    font-weight: 600;
                    margin-top: 5px;
                }}
            """)

            # Enhance shadow for current step
            shadow.setBlurRadius(12)
            shadow.setColor(QColor(0, 0, 0, 60))
        else:
            # Apply future state styling
            self.circle_container.setStyleSheet(f"""
                #stepCircleFuture {{
                    background-color: {card_bg_lighter};
                    color: {text_color};
                    border-radius: 20px;
                    border: 1px solid {border_color};
                }}
            """)

            self.text_label.setStyleSheet(f"""
                #stepTextFuture {{
                    color: {text_color};
                    opacity: 0.7;
                    margin-top: 5px;
                }}
            """)

    def set_state(self, is_current=False, is_completed=False, animate=True):
        """Set the visual state with premium animations."""
        # Store previous state for animation
        was_current = self.is_current
        was_completed = self.is_completed

        # Update state
        self.is_current = is_current
        self.is_completed = is_completed

        # Set appropriate object names for styling
        if is_completed:
            self.circle_container.setObjectName("stepCircleCompleted")
            self.text_label.setObjectName("stepTextCompleted")
            self.number_label.hide()
            self.checkmark.show()
        elif is_current:
            self.circle_container.setObjectName("stepCircleCurrent")
            self.text_label.setObjectName("stepTextCurrent")
            self.number_label.show()
            self.checkmark.hide()
        else:
            self.circle_container.setObjectName("stepCircleFuture")
            self.text_label.setObjectName("stepTextFuture")
            self.number_label.show()
            self.checkmark.hide()

        # Apply theme with updated states
        self.apply_theme()

        # Animate transition if needed
        if animate and (was_current != is_current or was_completed != is_completed):
            self.animate_state_change()

    def animate_state_change(self):
        """Animate transition between states for a premium feel with improved reliability."""
        # Stop any running animation
        if self._animation and self._animation.state() == QPropertyAnimation.Running:
            self._animation.stop()

        # Create scale animation
        self._animation = QPropertyAnimation(self, b"scale")
        self._animation.setDuration(250)  # Shorter duration for better response
        self._animation.setStartValue(1.0)
        self._animation.setEndValue(1.15)  # Slightly larger scale for more noticeable effect
        self._animation.setEasingCurve(QEasingCurve.OutQuad)

        # Connect to a slot that will scale back down
        self._animation.finished.connect(self._animate_scale_down)

        # Start animation
        self._animation.start()

    def _animate_scale_down(self):
        """Animate scaling back down after the initial scale up."""
        # Create new animation for scaling down
        self._animation = QPropertyAnimation(self, b"scale")
        self._animation.setDuration(200)
        self._animation.setStartValue(1.15)
        self._animation.setEndValue(1.0)
        self._animation.setEasingCurve(QEasingCurve.OutQuad)
        self._animation.start()

    def update_translations(self):
        """Update the text when language changes."""
        self.text_label.setText(self.translator.t(self.text))

    # Properties for animation
    def _get_scale(self):
        return self._scale

    def _set_scale(self, scale):
        if self._scale != scale:
            self._scale = scale
            self.circle_container.setFixedSize(int(40 * scale), int(40 * scale))

    scale = pyqtProperty(float, _get_scale, _set_scale)

    # Mouse events for hover effects
    def enterEvent(self, event):
        self._hover = True
        if not self.is_current and not self.is_completed:
            self.animate_hover(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover = False
        if not self.is_current and not self.is_completed:
            self.animate_hover(False)
        super().leaveEvent(event)

    def animate_hover(self, hovering):
        """Animate the hover state for a premium feel."""
        # Stop any running animation
        if self._animation and self._animation.state() == QPropertyAnimation.Running:
            self._animation.stop()

        # Create hover animation
        self._animation = QPropertyAnimation(self, b"opacity")
        self._animation.setDuration(150)  # Faster for better responsiveness

        if hovering:
            self._animation.setStartValue(1.0)
            self._animation.setEndValue(0.8)
        else:
            self._animation.setStartValue(0.8)
            self._animation.setEndValue(1.0)

        self._animation.setEasingCurve(QEasingCurve.InOutQuad)
        self._animation.start()

    def _get_opacity(self):
        return self._opacity

    def _set_opacity(self, opacity):
        if self._opacity != opacity:
            self._opacity = opacity
            self.setStyleSheet(f"opacity: {opacity};")
            self.update()

    opacity = pyqtProperty(float, _get_opacity, _set_opacity)

    def sizeHint(self):
        """Return the preferred size for the widget."""
        return QSize(60, 70)

    def paintEvent(self, event):
        """Custom paint event to enhance visual appearance."""
        super().paintEvent(event)

        # Custom painting for premium appearance
        # This would be appropriate for adding subtle effects like
        # highlights, shadows, or other decorative elements

        # For now we're letting the stylesheet handle most styling