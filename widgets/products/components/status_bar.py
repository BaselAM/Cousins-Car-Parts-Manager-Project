from PyQt5.QtWidgets import QFrame, QLabel, QHBoxLayout, QGraphicsDropShadowEffect
from PyQt5.QtGui import QPixmap, QFont, QColor
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QParallelAnimationGroup
import logging

# Create module logger
logger = logging.getLogger(__name__)


class StatusBar(QFrame):
    """
    A sleek, elegant status bar that remains slim by default.
    When a message is shown, it expands smoothly to reveal the icon and text,
    then auto-collapses back to its slim state.

    Enhanced version with:
    - Action-specific styling with fully colored background
    - Message deduplication
    - Better queue management
    - Dialog-aware behavior (stays open until dialogs close)
    """
    # Add state_changed signal
    state_changed = pyqtSignal(bool)  # True when expanded, False when collapsed

    # Message priority levels
    MESSAGE_PRIORITY = {
        "error": 100,  # Highest priority
        "warning": 80,
        "barcode": 90,  # New: Barcode scanning actions
        "add": 85,  # New: Add product actions
        "delete": 85,  # New: Delete actions
        "filter": 75,  # New: Filter actions
        "print": 75,  # New: Print actions
        "export": 70,  # New: Export actions
        "success": 60,
        "info": 40,  # General info
        "loaded": 30,  # Product loaded messages
        "select": 20  # Selection mode - lowest priority
    }

    # Dialog action types that should keep the status bar open
    DIALOG_ACTIONS = ["barcode", "add", "filter", "print", "export", "delete"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_type = "info"
        self.current_message = ""  # Track current message for deduplication
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.collapse)
        self.collapsed_height = 20  # Slim height when idle
        self.expanded_height = 60  # Expanded height to display messages
        self.animation_duration = 200  # Animation duration (ms)
        self.theme = {}  # To be set via set_theme()

        # Track whether a dialog-related action is in progress
        self.dialog_action_in_progress = False
        self.current_dialog_action = None

        # Add state tracking
        self.is_expanded = False
        self.is_animating = False

        # Add message queue for better message management
        self.message_queue = []
        self.current_message_priority = 0
        self.queue_timer = QTimer(self)
        self.queue_timer.setSingleShot(True)
        self.queue_timer.timeout.connect(self._process_message_queue)

        # Debug timer to log state - helps with debugging dialog state issues
        self.debug_timer = QTimer(self)
        self.debug_timer.timeout.connect(self._debug_log_state)
        self.debug_timer.start(5000)  # Log state every 5 seconds

        # Configure animations for smoother transitions
        self.setup_animations()

        # Create message durations for different types
        self.message_durations = {
            "success": 2500,  # 2.5 seconds for success messages
            "error": 8000,  # 8 seconds for errors
            "warning": 5000,  # 5 seconds for warnings
            "info": 4000,  # 4 seconds for info messages
            "loaded": 2500,  # 2.5 seconds for loaded messages
            "select": 1500,  # 1.5 seconds for selection mode messages
            "barcode": 30000,  # 30 seconds for barcode operations (will be closed manually)
            "add": 30000,  # 30 seconds for add operations (will be closed manually)
            "filter": 30000,  # 30 seconds for filter operations (will be closed manually)
            "print": 30000,  # 30 seconds for print operations (will be closed manually)
            "export": 30000,  # 30 seconds for export operations (will be closed manually)
            "delete": 30000  # 30 seconds for delete operations (will be closed manually)
        }

        self.setup_ui()
        self.setObjectName("statusBar")
        self.setMinimumHeight(self.collapsed_height)
        self.setMaximumHeight(self.collapsed_height)

        # Add a premium drop shadow for a floating effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(3)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(shadow)

    def _debug_log_state(self):
        """Log the current state for debugging purposes"""
        logger.debug(f"StatusBar state: dialog_action_in_progress={self.dialog_action_in_progress}, "
              f"current_dialog_action={self.current_dialog_action}, "
              f"is_expanded={self.is_expanded}, "
              f"message_queue={len(self.message_queue)}")

    def setup_animations(self):
        """Set up smoother animations with improved performance"""
        # Height animation with optimized easing curve
        self.height_animation = QPropertyAnimation(self, b"maximumHeight")
        self.height_animation.setDuration(self.animation_duration)
        self.height_animation.setEasingCurve(QEasingCurve.OutQuad)  # Smoother curve

        # Opacity animation for fade effects
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
                layout.addWidget(self.status_text)
                layout.addWidget(self.status_icon)
            else:
                layout.addWidget(self.status_icon)
                layout.addWidget(self.status_text)

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

    def _get_premium_style(self, type):
        # Custom style overrides for custom message types
        # THE DARK PURPLE COLOR FOR ALL DIALOG ACTIONS
        dialog_action_color = "#483d8b"  # DarkSlateBlue - a dark purple
        dialog_action_border = "#372b6e"  # Darker border
        dialog_action_text = "#ffffff"  # White text for contrast

        custom_types = {
            "loaded": {"bg": "#3c3c3c", "border": "#3c3c3c", "text": "#FFFFFF"},
            "select": {"bg": "#007bff", "border": "#0069d9", "text": "#FFFFFF"},  # Fully colored select

            # Use dark purple for all dialog actions
            "barcode": {"bg": dialog_action_color, "border": dialog_action_border, "text": dialog_action_text},
            "add": {"bg": dialog_action_color, "border": dialog_action_border, "text": dialog_action_text},
            "filter": {"bg": dialog_action_color, "border": dialog_action_border, "text": dialog_action_text},
            "print": {"bg": dialog_action_color, "border": dialog_action_border, "text": dialog_action_text},
            "export": {"bg": dialog_action_color, "border": dialog_action_border, "text": dialog_action_text},
            "delete": {"bg": dialog_action_color, "border": dialog_action_border, "text": dialog_action_text},

            # Other message types with full color
            "success": {"bg": "#28a745", "border": "#1e7e34", "text": "#FFFFFF"},
            "error": {"bg": "#dc3545", "border": "#bd2130", "text": "#FFFFFF"},
            "warning": {"bg": "#ffc107", "border": "#d39e00", "text": "#212529"},
            "info": {"bg": "#17a2b8", "border": "#138496", "text": "#FFFFFF"}
        }

        if type in custom_types:
            style = self.theme.get(type, custom_types[type])
        else:
            # Default to info style
            style = self.theme.get(type, custom_types["info"])

        # Use solid background color with full opacity
        # Make sure the entire status bar is fully colored
        return f"""
            #statusBar {{
                background-color: {style["bg"]};
                border: 2px solid {style["border"]};
                border-radius: 15px;
                padding: 10px 14px;
                color: {style["text"]};
            }}

            #statusBar QLabel {{
                background: transparent;
                color: {style["text"]};
                font-size: 13px;
                font-family: 'Segoe UI', sans-serif;
                font-weight: 500;
            }}
        """

    def _process_message_queue(self):
        """Process the next message in the queue if available"""
        if not self.message_queue:
            # Reset current priority when queue is empty
            self.current_message_priority = 0
            return

        # Get the next message with highest priority
        self.message_queue.sort(key=lambda x: x["priority"], reverse=True)
        next_message = self.message_queue.pop(0)

        # Show the message
        self._show_message_directly(
            next_message["message"],
            next_message["type"],
            next_message["duration"]
        )

        # Update current priority
        self.current_message_priority = next_message["priority"]

    def _prune_message_queue(self):
        """Remove lower priority messages when queue gets too long"""
        if len(self.message_queue) > 4:  # Don't let queue get too long
            # Keep only highest priority messages
            self.message_queue.sort(key=lambda x: x["priority"], reverse=True)
            self.message_queue = self.message_queue[:3]  # Keep top 3 messages

    def _show_message_directly(self, message, type="info", duration=None):
        """Internal method to directly show a message without queueing"""
        # Update current message for deduplication
        self.current_message = message

        # Use type-specific duration if none provided
        if duration is None:
            duration = self.message_durations.get(type, 5000)

        # Cancel existing auto-hide timer
        if self.auto_hide_timer.isActive():
            self.auto_hide_timer.stop()

        self.current_type = type

        # Check if this is a dialog action
        if type in self.DIALOG_ACTIONS:
            self.dialog_action_in_progress = True
            self.current_dialog_action = type
            logger.debug(f"Started dialog action: {type}")

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
            "loaded": "resources/info_icon.png",
            "select": "resources/select_icon.png",
            "barcode": "resources/barcode.png",  # New barcode icon
            "add": "resources/add_icon.png",  # New add icon
            "filter": "resources/filter_icon.png",  # New filter icon
            "print": "resources/print_icon.png",  # New print icon
            "export": "resources/export_icon.png",  # New export icon
            "delete": "resources/delete_icon.png"  # New delete icon
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

        # Start auto-collapse timer ONLY for non-dialog actions
        if type not in self.DIALOG_ACTIONS:
            self.auto_hide_timer.start(duration)

        # Schedule processing the next message after this one
        if not self.dialog_action_in_progress:
            self.queue_timer.start(duration + 100)

    def show_message(self, message, type="info", duration=None, priority=None):
        """
        Enhanced show_message with priority handling and deduplication.

        If a higher priority message is currently shown, this message will be
        queued. If this message has higher priority, it will interrupt current message.
        """
        # Skip empty messages
        if not message or message.strip() == "":
            return

        # Skip showing messages for selection deactivation
        if message and any(text in message.lower() for text in [
            "selection mode deactivate", "selection disabled", "selection mode off"
        ]):
            self.collapse()
            return

        # If a dialog action is in progress and this is a success message,
        # it might be a completion message, so we'll end the dialog action
        if self.dialog_action_in_progress and type == "success":
            # Do not end dialog action here automatically
            pass

        # Determine priority
        if priority is None:
            priority = self.MESSAGE_PRIORITY.get(type, 0)

        # Use type-specific duration if none provided
        if duration is None:
            duration = self.message_durations.get(type, 5000)

        # Deduplication: If this exact message is already in the queue or currently shown, skip it
        if message == self.current_message:
            return

        if any(item["message"] == message for item in self.message_queue):
            # If it's a duplicate but higher priority, replace the existing one
            for item in self.message_queue:
                if item["message"] == message:
                    item["priority"] = max(item["priority"], priority)
                    item["type"] = type  # Update type in case it changed
                    return

        # Check if we should show this message now or queue it
        if not self.is_expanded or priority >= self.current_message_priority:
            # Cancel any pending queue processing
            if self.queue_timer.isActive():
                self.queue_timer.stop()

            # Update current priority
            self.current_message_priority = priority

            # Show the message directly
            self._show_message_directly(message, type, duration)

            # Clear lower priority messages from queue if this is a high priority message
            if priority > 60:  # Higher than success
                self.message_queue = [msg for msg in self.message_queue if msg["priority"] >= priority]
        else:
            # Add to queue
            self.message_queue.append({
                "message": message,
                "type": type,
                "duration": duration,
                "priority": priority
            })

            # Prune the queue if it gets too long
            self._prune_message_queue()

    def start_dialog_action(self, action_type, message=None):
        if action_type not in self.DIALOG_ACTIONS:
            logger.warning(f"Invalid action_type '{action_type}' for start_dialog_action")
            return

        # Use the message provided by the caller.
        # If no message is provided, create a basic fallback.
        if not message:
            logger.warning(f"No message provided for start_dialog_action type '{action_type}'. Using generic fallback.")
            msg = f"Processing {action_type}..."
        else:
            msg = message

        self.dialog_action_in_progress = True
        self.current_dialog_action = action_type
        logger.debug(f"Starting dialog action: {action_type} - Message: '{msg}'")

        priority = self.MESSAGE_PRIORITY.get(action_type, 75)

        self.show_message(msg, action_type, None, priority)

    def end_dialog_action(self, success_message=None):
        """
        Indicate that a dialog action has ended.
        This will allow the status bar to collapse after showing a success message.

        Args:
            success_message: Optional success message to show before collapsing
        """
        if not self.dialog_action_in_progress:
            logger.warning("end_dialog_action called but no dialog action in progress")
            return

        # Clear dialog action status
        action_type = self.current_dialog_action
        logger.debug(f"Ending dialog action: {action_type} - Success: {success_message}")
        self.dialog_action_in_progress = False
        self.current_dialog_action = None

        # Show success message if provided
        if success_message:
            self.show_message(success_message, "success", 2000, 60)

        # Force a collapse after a delay
        QTimer.singleShot(2500, self.force_collapse)

        # Process any queued messages
        if self.message_queue:
            self.queue_timer.start(3000)  # Allow success message to show first

    def show_action_feedback(self, action_type, message=None):
        """
        Show immediate feedback when user initiates an action

        Args:
            action_type: One of "barcode", "add", "filter", "print", "export", "delete"
            message: Optional custom message, otherwise uses default for action
        """
        # For dialog actions, use start_dialog_action instead
        if action_type in self.DIALOG_ACTIONS:
            self.start_dialog_action(action_type, message)
            return

        # For non-dialog actions
        action_messages = {
            "select": "Entering selection mode..."
        }

        if action_type in action_messages:
            msg = message if message else action_messages[action_type]
            # Use action-specific type and appropriate priority
            priority = self.MESSAGE_PRIORITY.get(action_type, 50)
            self.show_message(msg, action_type, None, priority)

    def collapse(self):
        """
        Animate the collapse back to the slim state and clear the message.
        Won't collapse if a dialog action is in progress.
        """
        # Don't collapse if a dialog action is in progress
        if self.dialog_action_in_progress:
            logger.debug(f"Not collapsing because dialog action in progress: {self.current_dialog_action}")
            return

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

        # Process the next message in the queue when collapsed
        if self.message_queue:
            self.queue_timer.start(self.animation_duration + 50)

    def _clear_message(self):
        """Clear message text and icon after collapse animation completes"""
        self.current_message = ""  # Reset current message for deduplication
        self.status_text.setText("")
        self.status_icon.clear()

        # Process the next message in the queue if available
        if self.message_queue and not self.queue_timer.isActive():
            self.queue_timer.start(100)

    def cancel_auto_hide(self):
        """Cancel the auto-collapse timer."""
        if self.auto_hide_timer.isActive():
            self.auto_hide_timer.stop()

    def clear(self):
        """Alias for collapse, to support external calls."""
        self.collapse()

    def force_collapse(self):
        """Force collapse even if a dialog action is in progress"""
        # Reset dialog action status
        old_action = self.current_dialog_action
        self.dialog_action_in_progress = False
        self.current_dialog_action = None

        logger.debug(f"Force collapsing status bar (was dialog: {old_action})")

        # Now perform normal collapse
        self.collapse()

    def clear_queue(self):
        """Clear the message queue"""
        self.message_queue.clear()
        if self.queue_timer.isActive():
            self.queue_timer.stop()

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

        # If a dialog action was in progress, end it
        if self.dialog_action_in_progress:
            self.end_dialog_action()

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
            if timer != self.auto_hide_timer and timer != self.debug_timer and timer.isSingleShot():
                timer.stop()

        # Show the first message immediately
        self.show_message(first_message, first_type, first_duration + 100)

        # Skip second message if it's empty or a deactivation message
        if not second_message or any(txt in second_message.lower() for txt in [
            "selection mode deactivate", "selection disabled", "selection mode off"
        ]):
            return

        # Add second message to queue with slightly higher priority to ensure it shows next
        first_priority = self.MESSAGE_PRIORITY.get(first_type, 40)
        second_priority = first_priority + 1  # Slightly higher to guarantee sequence

        self.message_queue.append({
            "message": second_message,
            "type": second_type,
            "duration": second_duration,
            "priority": second_priority
        })