# gui/ui_builder.py
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QStackedWidget, QSizePolicy, QDesktopWidget
)

from widgets.header import TopBarWidget
from widgets.layout import HeaderWidget, CopyrightWidget
from themes import get_size


class GUIBuilder:
    """
    Responsible for creating and configuring UI components.
    Handles widget creation, layouts, and connecting signals.
    """

    def __init__(self, parent, translator, view_manager, parts_db):
        """
        Initialize the UI builder.

        Args:
            parent: The main GUI instance
            translator: Translator object for localization
            view_manager: View manager for accessing and creating views
            parts_db: Database connection for parts data
        """
        self.parent = parent
        self.translator = translator
        self.view_manager = view_manager
        self.parts_db = parts_db

        # UI components
        self.header = None
        self.top_bar = None
        self.footer = None
        self.content_stack = None

    # Updates to the setup_ui method in GUIBuilder class to improve layout proportions

    # Modified portion of ui_builder.py setup_ui method

    # Modified portion of ui_builder.py setup_ui method

    # Complete setup_ui method for GUIBuilder class

    def setup_ui(self):
        """Create and arrange all UI components with improved proportional layout"""
        # Create navigation function dictionary
        navigation_functions = self._create_navigation_functions()

        # Create main widgets
        self.home_page = self.view_manager.create_home_page(navigation_functions)
        self.header = HeaderWidget(self.translator, self.parent.show_home, parent=self.parent)
        self.top_bar = TopBarWidget(self.translator, self.parts_db, parent=self.parent)

        # Create copyright widget and store a reference to it
        self.copyright_widget = CopyrightWidget(self.translator, parent=self.parent)
        # Give it a distinct object name to make it easier to find
        self.copyright_widget.setObjectName("copyrightWidget")

        # Set proportional sizing for header components
        # Use percentage-based height constraints instead of fixed pixel values
        screen_height = QDesktopWidget().availableGeometry().height()

        # Header height: between 5% and 10% of screen height
        header_min_height = int(screen_height * 0.05)
        header_max_height = int(screen_height * 0.1)
        header_preferred_height = get_size("header_height")

        # Constrain header height within reasonable bounds
        self.header.setMinimumHeight(min(header_min_height, header_preferred_height * 0.8))
        self.header.setMaximumHeight(min(header_max_height, header_preferred_height * 1.2))

        # Similar constraints for top bar
        topbar_height = int(screen_height * 0.06)  # 6% of screen height
        self.top_bar.setMinimumHeight(topbar_height * 0.8)
        self.top_bar.setMaximumHeight(topbar_height * 1.2)

        # Connect top bar signals
        self.top_bar.home_clicked.connect(self.parent.show_home)
        self.top_bar.notification_clicked.connect(self.parent.show_notifications)
        self.top_bar.chat_clicked.connect(self.parent.show_chat)
        self.top_bar.search_submitted.connect(self.parent.on_search_entered)

        # Create stacked widget for content
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.home_page)
        self.content_stack.addWidget(self.view_manager.products_widget)
        self.content_stack.addWidget(self.view_manager.statistics_widget)
        self.content_stack.addWidget(self.view_manager.settings_widget)
        self.content_stack.addWidget(self.view_manager.help_widget)
        self.content_stack.addWidget(self.view_manager.parts_navigation_widget)

        # Set parent's content stack reference
        self.parent.content_stack = self.content_stack

        # Use proportional size policies for content
        self.content_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Main layout with adaptive spacing based on screen size
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # Calculate margins as percentage of screen size
        screen_width = QDesktopWidget().availableGeometry().width()
        horizontal_margin = int(screen_width * 0.01)  # 1% of screen width

        # Apply proportional margins and spacing
        main_layout.setContentsMargins(horizontal_margin, 0, horizontal_margin, 0)
        main_layout.setSpacing(0)  # No spacing between components for more compact look

        # Add the header directly
        main_layout.addWidget(self.header)

        # Create a container for the top bar that will only add top spacing
        top_bar_container = QWidget()
        top_bar_container.setObjectName("topBarContainer")
        top_bar_layout = QVBoxLayout(top_bar_container)

        # Add top spacing only - adjust this value to push the top bar down more or less
        top_spacing = 20  # Pixels to push the top bar down

        # Only padding at the top, no other sides
        top_bar_layout.setContentsMargins(0, top_spacing, 0, 0)
        top_bar_layout.setSpacing(0)  # No internal spacing

        # Add the top bar to its container
        top_bar_layout.addWidget(self.top_bar)

        # Make the container transparent to not affect other styling
        top_bar_container.setStyleSheet("background-color: transparent;")

        # Add the container instead of the top bar directly
        main_layout.addWidget(top_bar_container)

        # Content stack gets most of the space with higher stretch factor
        main_layout.addWidget(self.content_stack, 10)

        # Add the copyright widget (using our stored reference)
        main_layout.addWidget(self.copyright_widget)

        # Save references to main widget and layout
        self.parent.main_widget = main_widget
        self.parent.main_layout = main_layout

        # Set as central widget
        self.parent.setCentralWidget(main_widget)

        # Set footer to None to make it explicit that it's not being used
        self.footer = None

    def update_all_components(self):
        """Update all UI components"""
        if self.header:
            self.header.update_translations()

        if self.top_bar:
            self.top_bar.update_translations()

        if self.footer:
            self.footer.update_translations()

        # Make sure to update the copyright widget translations
        if hasattr(self, 'copyright_widget') and self.copyright_widget:
            self.copyright_widget.update_translations()

        # Update views through view manager
        self.view_manager.update_translations()

    def _create_navigation_functions(self):
        """Create dictionary of navigation functions"""
        return {
            'products_button': self.parent.show_products,
            'statistics_button': self.parent.show_statistics,
            'settings_button': self.parent.show_settings,
            'help_button': self.parent.show_help,
            'parts_button': self.parent.show_parts,
            'web_search_button': self.parent.show_web_search,
            'exit_button': self.parent.exit_app
        }

