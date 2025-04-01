from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSpacerItem, QSizePolicy
from typing import Optional

# Use absolute imports instead of relative imports
from widgets.header.search_widget import ModernSearchWidget
from widgets.header.notifications_widget import NotificationsWidget
from widgets.header.navigation_widget import NavigationWidget
from widgets.header.chatbot.direct_chat import DirectChatWidget as ChatWidget
from widgets.header.date_time_widget import LuxuryDateTimeWidget
from themes import get_color

# Import the custom logger
from logger import get_logger

# Get a module-specific logger
logger = get_logger(__name__)


class TopBarWidget(QWidget):
    """
    Main top bar widget with premium components.

    Provides a unified header containing navigation, date/time display,
    search functionality, chat access, and notifications in a responsive
    layout that adapts to the application theme.
    """
    search_submitted = pyqtSignal(str)
    home_clicked = pyqtSignal()
    notification_clicked = pyqtSignal()
    chat_clicked = pyqtSignal(str)
    # This flag is used to prevent showing "coming soon" messages
    chat_is_available = True  # IMPORTANT: Set to True to enable chat

    def __init__(self, translator, database, parent: Optional[QWidget] = None):
        """
        Initialize the top bar with all required components.

        Args:
            translator: Translation service object
            database: Database connection for data-dependent components
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.translator = translator
        self.database = database

        logger.debug("Initializing TopBarWidget")

        self._setup_ui()
        self.apply_theme()

    def _setup_ui(self) -> None:
        """Create and arrange all top bar components in their layout."""
        logger.debug("Setting up TopBarWidget UI components")

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 10, 20, 10)
        main_layout.setSpacing(15)  # Increased spacing between elements

        # Create the navigation widget with home button
        self.navigation_widget = NavigationWidget(self.translator)
        self.navigation_widget.home_clicked.connect(self.home_clicked)

        # Create luxury date and time widget
        self.date_time_widget = LuxuryDateTimeWidget(self.translator)

        # Create modern search widget - now always visible with fixed size
        self.search_widget = ModernSearchWidget(self.translator, self.database)
        self.search_widget.search_submitted.connect(self.search_submitted)

        # Create chat widget with expandable chat interface
        self.chat_widget = ChatWidget(self.translator)
        logger.debug("Chat widget initialized")

        # MODIFIED: Connect directly to chat signals - single connection only
        if hasattr(self.chat_widget, 'chat_submitted'):
            self.chat_widget.chat_submitted.connect(self._on_chat_message)
            logger.debug("Connected to chat_submitted signal")
        elif hasattr(self.chat_widget, 'message_sent'):
            self.chat_widget.message_sent.connect(self._on_chat_message)
            logger.debug("Connected to message_sent signal (legacy)")
        else:
            logger.warning("No chat signals found to connect to")

        # Create notifications widget with dropdown
        self.notifications_widget = NotificationsWidget(self.translator)
        self.notifications_widget.notification_clicked.connect(self.notification_clicked)

        # Layout arrangement:
        # Left section: navigation and date/time
        main_layout.addWidget(self.navigation_widget)
        main_layout.addWidget(self.date_time_widget)

        # Middle section: search bar gets maximum space
        # We give search substantial room by placing it between spacers
        left_spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        main_layout.addSpacerItem(left_spacer)

        # Set a stretch factor for the search widget to make it prominent
        main_layout.addWidget(self.search_widget, 3)  # Higher stretch factor

        # Right section: flexible space, chat and notifications
        right_spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        main_layout.addSpacerItem(right_spacer)
        main_layout.addWidget(self.chat_widget)
        main_layout.addWidget(self.notifications_widget)

        # Set fixed height for the top bar
        self.setFixedHeight(60)

        # Set object name for styling
        self.setObjectName("topBarWidget")

        logger.debug("TopBar UI setup complete")

    def _on_chat_message(self, message):
        """
        Handle chat messages and emit the chat_clicked signal.
        This is now a direct connection without showing any "coming soon" message.
        """
        logger.info(f"TopBarWidget received chat message: {message}")

        # Forward the message to any connected slots
        self.chat_clicked.emit(message)

    def clear_search(self) -> None:
        """Clear the search input field."""
        self.search_widget.clear_search()

    def set_notification_count(self, count: int) -> None:
        """
        Set the notification counter badge.

        Args:
            count: Number of notifications to display
        """
        self.notifications_widget.set_notification_count(count)

    def update_translations(self) -> None:
        """Update translations for all child components."""
        try:
            logger.debug("Updating translations in TopBarWidget")
            # Update all component translations
            self.search_widget.update_translations()
            self.notifications_widget.update_translations()
            self.navigation_widget.update_translations()
            self.chat_widget.update_translations()
            self.date_time_widget.update_translations()
        except Exception as e:
            logger.error(f"Error updating translations in top bar: {str(e)}")

    def apply_theme(self) -> None:
        """Apply current theme to the top bar and all its components."""
        try:
            logger.debug("Applying theme to TopBarWidget")
            header_color = get_color('header')
            border_color = get_color('border')

            # Apply theme to the top bar container with improved styling
            self.setStyleSheet(f"""
                #topBarWidget {{
                    background-color: {header_color};
                    border-bottom: 1px solid {border_color};
                }}
            """)

            # Apply theme to all child components
            self._apply_component_themes()
        except Exception as e:
            logger.error(f"Error applying theme to top bar: {str(e)}")
            # Fallback minimal styling
            self.setStyleSheet("""
                #topBarWidget {
                    background-color: #2c3e50;
                    border-bottom: 1px solid #34495e;
                }
            """)

    def _apply_component_themes(self) -> None:
        """Apply theme to all child components individually."""
        # Apply theme to each component with proper error handling
        components = [
            self.search_widget,
            self.notifications_widget,
            self.navigation_widget,
            self.chat_widget,
            self.date_time_widget
        ]

        for component in components:
            try:
                if hasattr(component, 'apply_theme'):
                    component.apply_theme()
            except Exception as e:
                logger.error(f"Error applying theme to {component.__class__.__name__}: {str(e)}")

    def resizeEvent(self, event) -> None:
        """
        Handle window resize events to adapt layout if needed.

        Ensures the search bar maintains visibility and prominence
        at various window sizes.
        """
        super().resizeEvent(event)

        # Get current width
        width = self.width()

        # Responsive adjustments based on width
        if width < 800:
            # For very narrow screens, date/time widget can be hidden
            self.date_time_widget.setVisible(False)
        else:
            self.date_time_widget.setVisible(True)