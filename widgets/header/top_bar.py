from PyQt5.QtCore import Qt, pyqtSignal, QSize, QTimer, QEvent, QTime
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QSpacerItem, QSizePolicy,
    QFrame, QVBoxLayout, QToolButton, QLabel
)
from typing import Optional

# Use absolute imports
from widgets.header.search_widget import IOSSearchWidget as ModernSearchWidget
from widgets.header.notifications_widget import NotificationsWidget
from widgets.header.navigation_widget import NavigationWidget
from widgets.header.chatbot.direct_chat import DirectChatWidget as ChatWidget
from widgets.header.date_time_widget import LuxuryDateTimeWidget

# Modified import path for InternetStatusWidget (adjust based on your actual file structure)
# If internet_status_widget.py is in the same directory as top_bar.py:
from widgets.header.internet_status_widget import InternetStatusWidget

# If internet_status_widget.py is in the widgets/header directory:
# from widgets.header.internet_status_widget import InternetStatusWidget

from themes import get_color, get_size
from size_policy import SizePolicyMixin, ResponsiveFontMixin

# Import the custom logger
from logger import get_logger

# Get a module-specific logger
logger = get_logger(__name__)


class ResponsiveTopBarWidget(QWidget, SizePolicyMixin):
    """
    Enhanced top bar widget with responsive layout capabilities.

    Dynamically adapts to available space and parent container size changes
    while maintaining essential functionality and visual hierarchy.
    """
    search_submitted = pyqtSignal(str)
    home_clicked = pyqtSignal()
    notification_clicked = pyqtSignal()
    chat_clicked = pyqtSignal(str)

    # Configuration constants
    COMPACT_WIDTH_THRESHOLD = 750  # Width threshold for compact mode
    MINIMUM_WIDTH_THRESHOLD = 500  # Width threshold for ultra-compact mode

    def __init__(self, translator, database, parent: Optional[QWidget] = None):
        """
        Initialize the responsive top bar with adaptive components.

        Args:
            translator: Translation service object
            database: Database connection for data-dependent components
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.translator = translator
        self.database = database
        self.current_mode = "normal"  # Tracks current display mode
        self.internet_status_widget = None  # Ensure this is defined before any possible exceptions

        logger.debug("Initializing ResponsiveTopBarWidget")

        self._setup_ui()
        self.apply_theme()

        # Track previous size to detect changes
        self._previous_width = self.width()
        self._previous_height = self.height()

        # Setup resize timer to prevent excessive updates
        self._resize_timer = QTimer(self)
        self._resize_timer.setSingleShot(True)
        self._resize_timer.timeout.connect(self._handle_delayed_resize)

    def _setup_ui(self) -> None:
        """Create a responsive layout with flex containers and adaptive components."""
        logger.debug("Setting up ResponsiveTopBarWidget UI components")

        # Use a wrapper for controlling overall layout
        self.main_frame = QFrame(self)
        self.main_frame.setObjectName("topBarFrame")

        # Main horizontal layout with dynamic margins
        self.main_layout = QHBoxLayout(self.main_frame)
        self.main_layout.setSpacing(8)  # Smaller spacing for better element density
        self.update_layout_margins()  # Set initial margins based on size

        # === LEFT SECTION: Navigation and Date/Time ===
        self.left_section = QFrame()
        self.left_section.setObjectName("leftSection")
        self.left_layout = QHBoxLayout(self.left_section)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(5)

        # Navigation widget with home button
        self.navigation_widget = NavigationWidget(self.translator)
        self.navigation_widget.home_clicked.connect(self.home_clicked)
        self.navigation_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        # Date and time widget (hideable)
        self.date_time_widget = LuxuryDateTimeWidget(self.translator)
        self.date_time_widget.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)

        # Add to left section
        self.left_layout.addWidget(self.navigation_widget)
        self.left_layout.addWidget(self.date_time_widget)

        # === MIDDLE SECTION: Search ===
        # Search widget with adaptive sizing
        self.search_widget = ModernSearchWidget(self.translator, self.database)
        self.search_widget.search_submitted.connect(self.search_submitted)
        self.search_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # === RIGHT SECTION: Chat, Notifications, and Internet Status ===
        self.right_section = QFrame()
        self.right_section.setObjectName("rightSection")
        self.right_layout = QHBoxLayout(self.right_section)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(5)

        # Chat widget
        self.chat_widget = ChatWidget(self.translator)
        self.chat_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        logger.debug("Chat widget initialized")

        # Connect chat signals
        if hasattr(self.chat_widget, 'chat_submitted'):
            self.chat_widget.chat_submitted.connect(self._on_chat_message)
            logger.debug("Connected to chat_submitted signal")
        elif hasattr(self.chat_widget, 'message_sent'):
            self.chat_widget.message_sent.connect(self._on_chat_message)
            logger.debug("Connected to message_sent signal (legacy)")

        # Notifications widget
        self.notifications_widget = NotificationsWidget(self.translator)
        self.notifications_widget.notification_clicked.connect(self.notification_clicked)
        self.notifications_widget.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)

        # Internet status widget - with enhanced error handling and logging
        try:
            logger.debug("Attempting to initialize internet status widget")
            self.internet_status_widget = InternetStatusWidget(self.translator)
            self.internet_status_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

            # Make it slightly larger for better visibility during testing
            self.internet_status_widget.setFixedWidth(40)

            logger.debug("Internet status widget initialized successfully")

            # Force an immediate update of the connection status
            QTimer.singleShot(100, self.internet_status_widget.check_connection)
            QTimer.singleShot(200, self.internet_status_widget.update_display)
        except Exception as e:
            logger.error(f"Could not initialize internet status widget: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())  # Print full stack trace
            self.internet_status_widget = None

        # Add widgets to right section
        self.right_layout.addWidget(self.chat_widget)
        self.right_layout.addWidget(self.notifications_widget)

        # Add internet status widget with explicit visibility check
        if self.internet_status_widget is not None:
            logger.debug("Adding internet status widget to right layout")
            self.right_layout.addWidget(self.internet_status_widget)
            self.internet_status_widget.setVisible(True)
            self.internet_status_widget.raise_()  # Ensure it's on top
            logger.debug(f"Internet status widget visibility: {self.internet_status_widget.isVisible()}")
        else:
            logger.warning("Internet status widget not available - skipping")

        # === Create overflow menu for ultra-compact mode ===
        self.overflow_menu = self._create_overflow_menu()
        self.overflow_menu.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.overflow_menu.hide()  # Hidden by default

        # === Add all sections to main layout ===
        self.main_layout.addWidget(self.left_section)
        self.main_layout.addWidget(self.search_widget, 1)  # Search gets highest stretch priority
        self.main_layout.addWidget(self.right_section)
        self.main_layout.addWidget(self.overflow_menu)

        # === Create main wrapper layout ===
        wrapper_layout = QHBoxLayout(self)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.addWidget(self.main_frame)

        # Set main frame to expand fully
        self.main_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Set object name for styling
        self.setObjectName("topBarWidget")

        logger.debug("ResponsiveTopBar UI setup complete")

        # Initial layout mode based on current size
        self._update_layout_mode()

        # Force a second layout update after a short delay
        QTimer.singleShot(500, self._force_layout_update)

    def _force_layout_update(self):
        """Force a layout update to ensure all widgets are properly shown"""
        logger.debug("Forcing layout update")
        self.updateGeometry()
        self.layout().activate()

        # Force visibility of key components
        if self.internet_status_widget is not None:
            self.internet_status_widget.setVisible(True)
            self.internet_status_widget.repaint()
            logger.debug(f"Internet status widget visibility after force: {self.internet_status_widget.isVisible()}")

        self.right_section.setVisible(True)
        self.right_section.repaint()

    def _create_overflow_menu(self):
        """Create overflow menu button for compact layouts"""
        menu_container = QFrame()
        menu_container.setObjectName("overflowMenuContainer")

        layout = QHBoxLayout(menu_container)
        layout.setContentsMargins(0, 0, 0, 0)

        menu_button = QToolButton()
        menu_button.setText("≡")  # Menu hamburger icon
        menu_button.setObjectName("overflowMenuButton")
        menu_button.setToolTip(self.translator.t("more_options"))
        menu_button.setCursor(Qt.PointingHandCursor)
        menu_button.clicked.connect(self._show_overflow_menu)

        layout.addWidget(menu_button)

        return menu_container

    def _show_overflow_menu(self):
        """Show a popup menu with overflow options"""
        # This would create a custom popup with the hidden components
        logger.debug("Overflow menu clicked - would show popup")
        # In a real implementation, this would show chat and notification options
        # For now, we'll just toggle visibility of the right section as a demonstration
        self.right_section.setVisible(not self.right_section.isVisible())

    def _on_chat_message(self, message):
        """Handle chat messages and emit the chat_clicked signal."""
        logger.info(f"TopBarWidget received chat message: {message}")
        self.chat_clicked.emit(message)

    def update_layout_margins(self):
        """Adjust margins based on current size"""
        width = self.width()

        if width < self.MINIMUM_WIDTH_THRESHOLD:
            # Ultra-compact: minimal margins
            self.main_layout.setContentsMargins(5, 2, 5, 2)
        elif width < self.COMPACT_WIDTH_THRESHOLD:
            # Compact: reduced margins
            self.main_layout.setContentsMargins(10, 3, 10, 3)
        else:
            # Normal: standard margins
            self.main_layout.setContentsMargins(15, 4, 15, 4)

    def _update_layout_mode(self):
        """
        Enhanced layout mode update that prevents oscillation during resize.
        """
        # Skip layout updates when the window is resizing
        parent_window = self.window()
        if hasattr(parent_window, '_in_resize') and parent_window._in_resize:
            return

        width = self.width()

        # Add hysteresis to prevent mode oscillation
        # Only change modes if we're significantly over/under the threshold
        if self.current_mode == "ultra-compact" and width > (self.MINIMUM_WIDTH_THRESHOLD + 20):
            new_mode = "compact"
        elif self.current_mode == "compact" and width < (self.MINIMUM_WIDTH_THRESHOLD - 20):
            new_mode = "ultra-compact"
        elif self.current_mode == "compact" and width > (self.COMPACT_WIDTH_THRESHOLD + 20):
            new_mode = "normal"
        elif self.current_mode == "normal" and width < (self.COMPACT_WIDTH_THRESHOLD - 20):
            new_mode = "compact"
        else:
            # Keep the current mode to avoid oscillation
            new_mode = self.current_mode

        # Only update if mode changed
        if new_mode != self.current_mode:
            logger.debug(f"Layout mode changed from {self.current_mode} to {new_mode}")
            self.current_mode = new_mode
            self._apply_layout_mode()

        # Skip search width adjustments during active resize
        if not hasattr(parent_window, '_resize_processing') or not parent_window._resize_processing:
            self._update_search_width(width)

    def _apply_layout_mode(self):
        """Apply the current layout mode to components"""
        logger.debug(f"Applying layout mode: {self.current_mode}")

        if self.current_mode == "ultra-compact":
            # Ultra-compact mode: hide date/time and right section, show overflow
            self.date_time_widget.setVisible(False)
            self.right_section.setVisible(False)
            self.overflow_menu.setVisible(True)

        elif self.current_mode == "compact":
            # Compact mode: hide date/time, show right section, hide overflow
            self.date_time_widget.setVisible(False)
            self.right_section.setVisible(True)
            self.overflow_menu.setVisible(False)

            # Ensure internet status is visible within right section
            if self.internet_status_widget is not None:
                self.internet_status_widget.setVisible(True)
                logger.debug("Internet status widget set to visible in compact mode")

        else:
            # Normal mode: show all components
            self.date_time_widget.setVisible(True)
            self.right_section.setVisible(True)
            self.overflow_menu.setVisible(False)

            # Ensure internet status is visible within right section
            if self.internet_status_widget is not None:
                self.internet_status_widget.setVisible(True)
                logger.debug("Internet status widget set to visible in normal mode")

        # Update all layouts to accommodate changes
        self.updateGeometry()
        self.layout().activate()

    def _update_search_width(self, width):
        """Adjust search width based on available space"""
        # Calculate appropriate search width
        if width < self.MINIMUM_WIDTH_THRESHOLD:
            min_width = max(100, int(width * 0.4))  # 40% of width, minimum 100px
        elif width < self.COMPACT_WIDTH_THRESHOLD:
            min_width = max(180, int(width * 0.5))  # 50% of width, minimum 180px
        else:
            min_width = max(250, int(width * 0.6))  # 60% of width, minimum 250px

        # Apply the width to search widget
        self.search_widget.setMinimumWidth(min_width)

    def resizeEvent(self, event):
        """
        Improved resize event handler for the top bar with better debouncing.
        This will prevent excessive layout changes during window resize.
        """
        super().resizeEvent(event)

        # Check if parent window is being resized
        parent_window = self.window()
        if hasattr(parent_window, '_in_resize') and parent_window._in_resize:
            # During parent window resize, only update margins if really necessary
            current_width = self.width()
            significant_change = abs(current_width - self._previous_width) > 50

            if significant_change:
                # Only update margins, don't do full layout adjustment
                self.update_layout_margins()
                self._previous_width = current_width

            # Skip the timer-based update during active resize
            return

        # Update margins immediately as they're simple changes
        self.update_layout_margins()

        # Use a longer debounce time during active resize
        # to prevent layout flicker and oscillation
        self._resize_timer.start(250)  # 250ms debounce (increased)

    def _handle_delayed_resize(self):
        """Handle resize after debounce delay"""
        width = self.width()
        height = self.height()

        # Only process if size actually changed
        if width != self._previous_width or height != self._previous_height:
            self._previous_width = width
            self._previous_height = height

            # Update layout based on new size
            self._update_layout_mode()

    def event(self, event):
        """Handle parent resize and other events that might affect layout"""
        result = super().event(event)

        # Use QEvent type constants which are more reliable
        if event.type() in (QEvent.LayoutRequest, QEvent.ParentChange, QEvent.Show):
            # Schedule a layout update
            QTimer.singleShot(0, self._update_layout_mode)

        return result

    def clear_search(self):
        """Clear the search input field."""
        self.search_widget.clear_search()

    def set_notification_count(self, count):
        """Set the notification counter badge."""
        self.notifications_widget.set_notification_count(count)

    def update_translations(self):
        """Update translations for all child components."""
        try:
            logger.debug("Updating translations in ResponsiveTopBarWidget")
            components = [
                self.search_widget,
                self.notifications_widget,
                self.navigation_widget,
                self.chat_widget,
                self.date_time_widget
            ]

            # Add internet status widget conditionally
            if self.internet_status_widget is not None:
                components.append(self.internet_status_widget)

            for component in components:
                if hasattr(component, 'update_translations'):
                    component.update_translations()
        except Exception as e:
            logger.error(f"Error updating translations in top bar: {str(e)}")

    def apply_theme(self):
        """Apply current theme to all components with responsive styling."""
        try:
            logger.debug("Applying theme to ResponsiveTopBarWidget")
            header_color = get_color('header')
            border_color = get_color('border')
            text_color = get_color('text')
            button_bg = get_color('button')
            button_hover = get_color('button_hover')

            # Main top bar styling
            self.setStyleSheet(f"""
                #topBarWidget {{
                    background-color: {header_color};
                    border-bottom: 1px solid {border_color};
                }}

                #topBarFrame {{
                    background-color: transparent;
                    border: none;
                }}

                #leftSection, #rightSection {{
                    background-color: transparent;
                    border: none;
                }}

                #overflowMenuButton {{
                    background-color: transparent;
                    color: {text_color};
                    border: none;
                    border-radius: 15px;
                    padding: 4px 8px;
                    font-size: 16px;
                    font-weight: bold;
                    min-width: 30px;
                    min-height: 30px;
                }}

                #overflowMenuButton:hover {{
                    background-color: {button_hover};
                }}

                #overflowMenuContainer {{
                    background-color: transparent;
                    border: none;
                }}
            """)

            # Apply theme to all child components
            components = [
                self.search_widget,
                self.notifications_widget,
                self.navigation_widget,
                self.chat_widget,
                self.date_time_widget
            ]

            # Add internet status widget conditionally
            if self.internet_status_widget is not None:
                components.append(self.internet_status_widget)
                logger.debug("Applying theme to internet status widget")

            for component in components:
                if hasattr(component, 'apply_theme'):
                    component.apply_theme()

        except Exception as e:
            logger.error(f"Error applying theme to responsive top bar: {str(e)}")
            # Fallback minimal styling
            self.setStyleSheet("""
                #topBarWidget {
                    background-color: #2c3e50;
                    border-bottom: 1px solid #34495e;
                }

                #overflowMenuButton {
                    background-color: transparent;
                    color: white;
                    border: none;
                }
            """)

    def force_show_internet_status(self):
        """Force the internet status widget to be visible (for debugging)"""
        if self.internet_status_widget is not None:
            logger.debug("Forcing internet status widget to be visible")
            self.internet_status_widget.setVisible(True)
            self.internet_status_widget.raise_()
            self.internet_status_widget.repaint()

            # Make sure parent containers are visible
            self.right_section.setVisible(True)
            self.right_section.repaint()

            # Force layout update
            self.updateGeometry()
            self.layout().activate()

            return True
        else:
            logger.warning("Cannot force show - internet status widget is None")
            return False


# For backward compatibility
TopBarWidget = ResponsiveTopBarWidget