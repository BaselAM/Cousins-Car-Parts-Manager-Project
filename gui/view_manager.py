# gui/view_manager.py
from PyQt5.QtWidgets import QMessageBox
from logger import get_logger

# Import widgets
from widgets.home_page import HomePageWidget
from widgets.products import ProductsWidget
from widgets.statistics import StatisticsWidget
from widgets.settings.settings_widget import SettingsWidget
from widgets.help import HelpWidget
from parts_navigation import PartsNavigationContainer

logger = get_logger(__name__)


class GUIViewManager:
    """
    Manages view creation, loading, and navigation.
    Handles view switching and maintains references to all view widgets.
    """

    def __init__(self, parent, translator, parts_db):
        """
        Initialize the view manager.

        Args:
            parent: The main GUI instance
            translator: Translator object for localization
            parts_db: Database connection for parts data
        """
        self.parent = parent
        self.translator = translator
        self.parts_db = parts_db

        # Initialize view widgets
        self.products_widget = None
        self.statistics_widget = None
        self.settings_widget = None
        self.help_widget = None
        self.parts_navigation_widget = None
        self.home_page = None

    def preload_views(self):
        """Initialize all view widgets"""
        self.products_widget = ProductsWidget(self.translator, self.parts_db, parent=self.parent)
        self.statistics_widget = StatisticsWidget(self.translator, parent=self.parent)
        self.settings_widget = SettingsWidget(self.translator, self.parent.update_language, self.parent)
        self.help_widget = HelpWidget(self.translator, parent=self.parent)
        self.parts_navigation_widget = PartsNavigationContainer(
            self.translator,
            self.parts_db,
            parent=self.parent
        )

    def create_home_page(self, navigation_functions):
        """
        Create the home page widget.

        Args:
            navigation_functions: Dictionary of navigation callback functions

        Returns:
            HomePageWidget: The created home page widget
        """
        self.home_page = HomePageWidget(self.translator, navigation_functions, parent=self.parent)
        return self.home_page

    # Navigation methods
    def show_home(self, content_stack):
        """Switch to home page view"""
        content_stack.setCurrentWidget(self.home_page)

    def show_products(self, content_stack):
        """Switch to products view"""
        content_stack.setCurrentWidget(self.products_widget)

    def show_statistics(self, content_stack):
        """Switch to statistics view"""
        content_stack.setCurrentWidget(self.statistics_widget)

    def show_settings(self, content_stack):
        """Switch to settings view"""
        content_stack.setCurrentWidget(self.settings_widget)

    def show_help(self, content_stack):
        """Switch to help documentation view"""
        content_stack.setCurrentWidget(self.help_widget)

    def show_parts(self, content_stack, translator):
        """Open the parts navigation system"""
        try:
            # First check if we need to recreate the parts navigation widget
            # This ensures any existing lingering animations/operations are properly cleaned up
            if self.parts_navigation_widget:
                # Explicitly clean up any running operations in the component
                if hasattr(self.parts_navigation_widget, 'cleanup_animations'):
                    self.parts_navigation_widget.cleanup_animations()

                # For any brand loading threads
                if hasattr(self.parts_navigation_widget, 'ui_builder') and \
                        hasattr(self.parts_navigation_widget.ui_builder, 'brand_step') and \
                        hasattr(self.parts_navigation_widget.ui_builder.brand_step, 'logo_manager'):
                    logo_manager = self.parts_navigation_widget.ui_builder.brand_step.logo_manager
                    if hasattr(logo_manager, 'thread_pool'):
                        # Wait for thread pool to finish current tasks
                        logo_manager.thread_pool.waitForDone(300)  # 300ms timeout

                # Remove from content stack and mark for deletion
                content_stack.removeWidget(self.parts_navigation_widget)
                self.parts_navigation_widget.deleteLater()

                # Create a new instance
                self.parts_navigation_widget = PartsNavigationContainer(
                    self.translator,
                    self.parts_db,
                    parent=self.parent
                )

                # Add to content stack
                content_stack.addWidget(self.parts_navigation_widget)

            # Now show the widget
            content_stack.setCurrentWidget(self.parts_navigation_widget)

        except Exception as e:
            logger.error(f"Error showing parts navigation: {str(e)}")
            QMessageBox.warning(self.parent, translator.t("parts_button"),
                                f"Could not load parts navigation: {str(e)}")

    def show_web_search(self, translator):
        """Open web search for car parts"""
        # You'll need to implement this feature
        QMessageBox.information(self.parent, translator.t("web_search_button"),
                                translator.t("search_options"))

    def show_notifications(self, translator):
        """Show notifications panel"""
        QMessageBox.information(self.parent, translator.t("notifications"),
                                translator.t("popout_notifications"))

    def show_chat(self, message=None):
        """Handle chat messages from the chat widget"""
        if message:
            # If message provided, it's from the chat widget so don't show popup
            logger.debug(f"Chat message handled in chat widget: {message}")
            # The actual chat handling is already done in the widget
            return

        # This branch only executes when clicking the chat button directly
        # If you want to implement a full-page chat view later, you could do it here
        pass

    def on_search_entered(self, top_bar):
        """Handle search queries"""
        search_text = top_bar.search_widget.search_edit.text().strip()
        if search_text:
            self.show_products(self.parent.content_stack)
            self.products_widget.highlight_product(search_text)

    def update_translations(self):
        """Update translations for all view widgets"""
        for widget in [
            self.home_page,
            self.products_widget,
            self.statistics_widget,
            self.settings_widget,
            self.help_widget,
            self.parts_navigation_widget
        ]:
            if widget and hasattr(widget, 'update_translations'):
                widget.update_translations()