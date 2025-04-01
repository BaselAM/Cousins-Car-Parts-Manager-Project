from PyQt5.QtWidgets import QFrame, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QParallelAnimationGroup


class StatusBar(QFrame):
    """
    A sleek, elegant status bar that remains slim by default.
    When a message is shown, it expands smoothly to reveal the icon and text,
    then auto-collapses back to its slim state.
    It supports theme integration via the set_theme() method and custom message types:
      - "success": for successful operations (green text)
      - "loaded": for loaded products messages (white text)
      - "select": for select mode (blue text)
    """
    # Add state_changed signal
    state_changed = pyqtSignal(bool)  # True when expanded, False when collapsed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_type = "info"
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.collapse)
        self.collapsed_height = 20  # Slim height when idle
        self.expanded_height = 60  # Expanded height to display messages
        self.animation_duration = 200  # Animation duration (ms) - REDUCED for smoother feel
        self.theme = {}  # To be set via set_theme()

        # Add state tracking
        self.is_expanded = False
        self.is_animating = False

        # Configure animations for smoother transitions
        self.setup_animations()

        # Create message durations for different types
        self.message_durations = {
            "success": 2500,  # 2.5 seconds for success messages
            "error": 8000,  # 8 seconds for errors
            "warning": 5000,  # 5 seconds for warnings
            "info": 4000,  # 4 seconds for info messages
            "loaded": 2500,  # 2.5 seconds for loaded messages
            "select": 1500  # 1.5 seconds for selection mode messages
        }

        self.setup_ui()
        self.setObjectName("statusBar")
        self.setMinimumHeight(self.collapsed_height)
        self.setMaximumHeight(self.collapsed_height)

        # Add a premium drop shadow for a floating effect - IMPROVED for better performance
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)  # Reduced blur radius for better performance
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 80))  # Reduced opacity for better performance
        self.setGraphicsEffect(shadow)

    def setup_animations(self):
        """Set up smoother animations with improved performance"""
        # Height animation with optimized easing curve
        self.height_animation = QPropertyAnimation(self, b"maximumHeight")
        self.height_animation.setDuration(self.animation_duration)
        self.height_animation.setEasingCurve(QEasingCurve.OutQuad)  # Smoother curve

        # Opacity animation for fade effects (optional, not used yet)
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(self.animation_duration)
        self.opacity_animation.setEasingCurve(QEasingCurve.OutQuad)

        # Animation group for coordinated animations
        self.animation_group = QParallelAnimationGroup()
        self.animation_group.addAnimation(self.height_animation)

        # Connect finished signal to handle state after animation
        self.animation_group.finished.connect(self._handle_animation_finished)

    def _handle_animation_finished(self):
        """Handle state after animation finishes"""
        self.is_animating = False
        if not self.is_expanded:
            self._clear_message()

    def setup_ui(self):
        # Use a styled panel so the frame is rendered
        self.setFrameShape(QFrame.StyledPanel)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(10)

        # Refined, smaller icon for elegance
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(24, 24)
        self.status_icon.setAlignment(Qt.AlignCenter)

        # Status text with modern, premium styling
        self.status_text = QLabel()
        self.status_text.setWordWrap(True)
        self.status_text.setMinimumWidth(200)  # Set minimum width
        self.status_text.setAlignment(
            Qt.AlignLeading | Qt.AlignVCenter)  # Align to start for RTL support
        font = QFont("Segoe UI", 13)
        font.setWeight(QFont.Medium)
        self.status_text.setFont(font)

        # For RTL languages like Hebrew, adjust the layout direction
        if self.layoutDirection() == Qt.RightToLeft:
            layout.addWidget(self.status_text, 1)
            layout.addWidget(self.status_icon)
        else:
            layout.addWidget(self.status_icon)
            layout.addWidget(self.status_text, 1)

        # Initialize with no text or icon
        self.status_text.setText("")
        self.status_icon.setPixmap(QPixmap())

    def setLayoutDirection(self, direction):
        """Override to handle layout changes when RTL/LTR direction changes"""
        super().setLayoutDirection(direction)

        # Re-arrange widgets based on layout direction
        layout = self.layout()
        if layout:
            # Clear the layout
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    layout.removeWidget(item.widget())

            # Re-add widgets in the correct order
            if direction == Qt.RightToLeft:
                layout.addWidget(self.status_text, 1)
                layout.addWidget(self.status_icon)
            else:
                layout.addWidget(self.status_icon)
                layout.addWidget(self.status_text, 1)

    def set_theme(self, theme):
        """
        Set the theme dictionary for the status bar.
        Expected format:
            {
              "success": {"bg": <hex>, "border": <hex>, "text": <hex>},
              "error":   {"bg": <hex>, "border": <hex>, "text": <hex>},
              "warning": {"bg": <hex>, "border": <hex>, "text": <hex>},
              "info":    {"bg": <hex>, "border": <hex>, "text": <hex>}
            }
        You can also provide custom types like "loaded" and "select".
        """
        self.theme = theme

    def _lighten_color(self, hex_color, percent):
        """Return a lighter version of the given hex color by the specified percent."""
        c = QColor(hex_color)
        return c.lighter(100 + percent).name()

    def _get_premium_style(self, type):
        # Custom style overrides for custom message types
        custom_types = {
            "loaded": {"bg": "#3c3c3c", "border": "#3c3c3c", "text": "#FFFFFF"},
            "select": {"bg": "#d0eaff", "border": "#007bff", "text": "#007bff"}
        }
        if type in custom_types:
            style = self.theme.get(type, custom_types[type])
        else:
            defaults = {
                "success": {"bg": "#e8f5e9", "border": "#81c784", "text": "#2E7D32"},
                "error": {"bg": "#ffebee", "border": "#e57373", "text": "#C62828"},
                "warning": {"bg": "#fff8e1", "border": "#ffd54f", "text": "#EF6C00"},
                "info": {"bg": "#e3f2fd", "border": "#64b5f6", "text": "#1565C0"}
            }
            style = self.theme.get(type, defaults.get(type, defaults["info"]))
        # Create a subtle vertical gradient for a premium feel
        gradient = (
            f"qlineargradient(x1:0, y1:0, x2:0, y2:1, "
            f"stop:0 {style['bg']}, stop:1 {self._lighten_color(style['bg'], 30)})"
        )
        return f"""
            #statusBar {{
                background: {gradient};
                border: 2px solid {style["border"]};
                border-radius: 15px;
                padding: 10px 14px;
            }}
            QLabel {{
                background: transparent;
                color: {style["text"]};
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 500;
            }}
        """

    def show_message(self, message, type="info", duration=None):
        """
        Expands the status bar to show a message with an icon,
        applies the premium style based on the message type,
        then auto-collapses after `duration` milliseconds.

        If duration is None, will use type-specific duration.
        """
        # Skip showing messages for selection deactivation
        # This fixes the unwanted "Selection mode deactivated" message
        if message and (
                "selection mode deactivate" in message.lower() or
                "selection disabled" in message.lower() or
                "selection mode off" in message.lower()
        ):
            self.collapse()
            return

        # Use type-specific duration if none provided
        if duration is None:
            duration = self.message_durations.get(type, 5000)

        # Cancel existing auto-hide timer
        if self.auto_hide_timer.isActive():
            self.auto_hide_timer.stop()

        self.current_type = type

        # If we're already animating, stop current animation
        if self.is_animating:
            self.animation_group.stop()

        # Update state and emit signal
        was_expanded = self.is_expanded
        self.is_expanded = True
        if not was_expanded:
            self.state_changed.emit(True)

        # Set the icon based on message type
        icon_map = {
            "success": "resources/check_icon.png",
            "error": "resources/error_icon.png",
            "warning": "resources/warning_icon.png",
            "info": "resources/info_icon.png",
            "loaded": "resources/info_icon.png",  # You can adjust icons per type
            "select": "resources/select_icon.png"
        }
        icon_path = icon_map.get(type, icon_map["info"])
        try:
            pix = QPixmap(icon_path).scaled(24, 24, Qt.KeepAspectRatio,
                                            Qt.SmoothTransformation)
            self.status_icon.setPixmap(pix)
        except Exception:
            self.status_icon.setText("")

        # Handle message with placeholder protection
        safe_message = message
        try:
            # Check if it's a formatting string with {placeholders}
            if "{" in message and "}" in message:
                # Test format with dummy values to see if it's valid
                try:
                    test = message.format(count=0, file="test.csv")
                except KeyError:
                    # Has placeholders but wrong ones, display as-is
                    pass
        except Exception:
            # If any error occurs, use message as-is
            pass

        self.status_text.setText(safe_message)
        self.setStyleSheet(self._get_premium_style(type))

        # Execute smooth expansion animation
        self.height_animation.setStartValue(self.height())
        self.height_animation.setEndValue(self.expanded_height)

        self.is_animating = True
        self.animation_group.start()

        # Start auto-collapse timer
        self.auto_hide_timer.start(duration)

    def collapse(self):
        """
        Animate the collapse back to the slim state and clear the message.
        """
        # Don't do anything if we're already collapsed or collapsing
        if not self.is_expanded or (self.is_animating and self.height() < self.expanded_height):
            return

        # Cancel auto-hide timer
        if self.auto_hide_timer.isActive():
            self.auto_hide_timer.stop()

        # If we're already animating, stop current animation
        if self.is_animating:
            self.animation_group.stop()

        # Update state
        self.is_expanded = False
        self.state_changed.emit(False)

        # Execute smooth collapse animation
        self.height_animation.setStartValue(self.height())
        self.height_animation.setEndValue(self.collapsed_height)

        self.is_animating = True
        self.animation_group.start()

    def _clear_message(self):
        """Clear message text and icon after collapse animation completes"""
        self.status_text.setText("")
        self.status_icon.clear()

    def cancel_auto_hide(self):
        """Cancel the auto-collapse timer."""
        if self.auto_hide_timer.isActive():
            self.auto_hide_timer.stop()

    def clear(self):
        """Alias for collapse, to support external calls."""
        self.collapse()

    def show_sequential_messages(self, first_message, second_message,
                                 first_type="success",
                                 second_type="info", first_duration=None,
                                 second_duration=None):
        """
        Shows a sequence of two messages:
        1. First message (typically a success message) for first_duration milliseconds
        2. Then second message (typically loaded products info) for second_duration milliseconds
        3. Then collapses the status bar

        This creates a smooth flow of information for the user after operations.

        If durations are None, will use type-specific durations.
        """
        # Skip showing messages for selection deactivation
        if first_message and any(txt in first_message.lower() for txt in [
            "selection mode deactivate", "selection disabled", "selection mode off"
        ]):
            # If first message should be skipped but second message exists,
            # just show the second message
            if second_message and not any(txt in second_message.lower() for txt in [
                "selection mode deactivate", "selection disabled", "selection mode off"
            ]):
                self.show_message(second_message, second_type, second_duration)
            else:
                self.collapse()
            return

        # Use type-specific durations if none provided
        if first_duration is None:
            first_duration = self.message_durations.get(first_type, 2500)
        if second_duration is None:
            second_duration = self.message_durations.get(second_type, 4000)

        # Cancel any previous timers
        if self.auto_hide_timer.isActive():
            self.auto_hide_timer.stop()

        # Make sure any pending message updates are cancelled
        for timer in self.findChildren(QTimer):
            if timer != self.auto_hide_timer and timer.isSingleShot():
                timer.stop()

        # Show the first message immediately
        self.show_message(first_message, first_type, first_duration + 100)

        # Skip second message if it's empty or a deactivation message
        if not second_message or any(txt in second_message.lower() for txt in [
            "selection mode deactivate", "selection disabled", "selection mode off"
        ]):
            return

        # Schedule the second message with a dedicated timer
        second_msg_timer = QTimer(self)
        second_msg_timer.setSingleShot(True)
        second_msg_timer.timeout.connect(
            lambda: self._show_second_message(second_message, second_type, second_duration))
        second_msg_timer.start(first_duration)

    def _show_second_message(self, message, type, duration):
        """Helper method to show the second message in the sequence."""
        # Skip if deactivation message
        if message and any(txt in message.lower() for txt in [
            "selection mode deactivate", "selection disabled", "selection mode off"
        ]):
            self.collapse()
            return

        self.show_message(message, type, duration)