# gui/view_manager.py
from PyQt5.QtWidgets import QMessageBox
from logger import get_logger

# Import widgets
from widgets.home_page import HomePageWidget
from widgets.products import ProductsWidget
# Import the premium statistics widget instead of the original
from widgets.statistics import StatisticsWidget
from widgets.settings.settings_widget import SettingsWidget
from widgets.help import HelpWidget
from widgets.register_widget import RegisterWidget

# Configure module logger
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
        self.smart_search_widget = None  # Add the new widget reference
        self.register_widget = None
        self.home_page = None

    def preload_views(self):
        """Initialize all view widgets"""
        self.products_widget = ProductsWidget(self.translator, self.parts_db, parent=self.parent)

        # Use the PremiumStatisticsWidget instead of the original StatisticsWidget
        self.statistics_widget = StatisticsWidget(self.translator, parent=self.parent)
        # Set up the database connection for the statistics widget
        self.statistics_widget.setup_database(self.parts_db)

        self.settings_widget = SettingsWidget(self.translator, self.parent.update_language, self.parent)
        self.help_widget = HelpWidget(self.translator, parent=self.parent)

        # Initialize the Smart Search widget (will implement later)
        # Commented out for now until the widget is implemented
        # self.smart_search_widget = SmartSearchWidget(self.translator, self.parts_db, parent=self.parent)

        # Pre-initialize the register widget to prevent loading delay when first accessed
        self.register_widget = RegisterWidget(
            translator=self.translator,
            db=self.parts_db,
            parent=self.parent
        )

        # Connect signals
        if hasattr(self.register_widget, 'transaction_completed'):
            self.register_widget.transaction_completed.connect(self.on_transaction_completed)

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

    def show_register(self, content_stack):
        """Show the register widget for sales and inventory management"""
        try:
            # Check if register widget already exists or create it
            if not self.register_widget:
                logger.info("Creating new register widget")
                # Create the register widget
                self.register_widget = RegisterWidget(
                    translator=self.translator,
                    db=self.parts_db,
                    parent=self.parent
                )

                # Connect transaction signals
                if hasattr(self.register_widget, 'transaction_completed'):
                    self.register_widget.transaction_completed.connect(self.on_transaction_completed)

                # Add to content stack
                content_stack.addWidget(self.register_widget)
            elif self.register_widget.parent() is None:
                # If widget exists but isn't in the stack (was removed)
                logger.info("Re-adding existing register widget to stack")
                content_stack.addWidget(self.register_widget)

            # Check if widget is already in stack
            index = content_stack.indexOf(self.register_widget)
            if index == -1:
                # Widget isn't in the stack yet
                logger.info("Adding register widget to stack")
                content_stack.addWidget(self.register_widget)

            # Switch to register widget
            logger.info("Switching to register widget")
            content_stack.setCurrentWidget(self.register_widget)

        except Exception as e:
            logger.error(f"Error showing register widget: {str(e)}")
            raise

    def on_transaction_completed(self, transaction_data):
        """Handle completed transactions from register widget"""
        # Log the transaction
        transaction_type = transaction_data.get('type', 'unknown')
        product_name = transaction_data.get('product', 'unknown')
        quantity = transaction_data.get('quantity', 0)
        price = transaction_data.get('price', 0.0)

        # Use the module logger instead of self.logger
        if transaction_type == 'sell':
            logger.info(f"Sale completed: {quantity} x {product_name} for ${price:.2f}")
        elif transaction_type == 'receive':
            logger.info(f"Stock received: {quantity} x {product_name} worth ${price:.2f}")

        # You could add code here to save transactions to a database
        # or update other UI components with the transaction data

    # Navigation methods
    def show_home(self, content_stack):
        """Switch to home page view"""
        content_stack.setCurrentWidget(self.home_page)

    def show_products(self, content_stack):
        """Switch to products view"""
        content_stack.setCurrentWidget(self.products_widget)

    def show_statistics(self, content_stack):
        """Switch to statistics view with improved database handling"""
        content_stack.setCurrentWidget(self.statistics_widget)

        # Refresh data when statistics view is shown
        if hasattr(self.statistics_widget, 'setup_database'):
            # Check if we need to set up the database
            if not hasattr(self.statistics_widget, 'db') or self.statistics_widget.db is None:
                # Get the settings DB from the parent if available
                settings_db = None
                if hasattr(self.parent, 'settings_db'):
                    settings_db = self.parent.settings_db

                # Set up the database with the settings
                self.statistics_widget.setup_database(self.parts_db, settings_db)
            else:
                # Just refresh data
                self.statistics_widget.refresh_data()
        elif hasattr(self.statistics_widget, 'refresh_data'):
            self.statistics_widget.refresh_data()

    def show_settings(self, content_stack):
        """Switch to settings view"""
        content_stack.setCurrentWidget(self.settings_widget)

    def show_help(self, content_stack):
        """Switch to help documentation view"""
        content_stack.setCurrentWidget(self.help_widget)

    def show_smart_search(self, content_stack):
        """Show the Smart Search widget"""
        try:
            # Check if Smart Search widget already exists or create it
            if not self.smart_search_widget:
                logger.info("Creating new Smart Search widget")

                # Import here to avoid circular imports
                from smart_search.smart_search_widget import SmartSearchWidget

                # Create the Smart Search widget
                self.smart_search_widget = SmartSearchWidget(
                    translator=self.translator,
                    db=self.parts_db,
                    parent=self.parent
                )

                # Add to content stack
                content_stack.addWidget(self.smart_search_widget)
            elif self.smart_search_widget.parent() is None:
                # If widget exists but isn't in the stack (was removed)
                logger.info("Re-adding existing Smart Search widget to stack")
                content_stack.addWidget(self.smart_search_widget)

            # Check if widget is already in stack
            index = content_stack.indexOf(self.smart_search_widget)
            if index == -1:
                # Widget isn't in the stack yet
                logger.info("Adding Smart Search widget to stack")
                content_stack.addWidget(self.smart_search_widget)

            # Switch to Smart Search widget
            logger.info("Switching to Smart Search widget")
            content_stack.setCurrentWidget(self.smart_search_widget)

        except Exception as e:
            logger.error(f"Error showing Smart Search widget: {str(e)}")
            # Show temporary message until widget is implemented
            QMessageBox.information(
                self.parent,
                self.translator.t("smart_search_button") if hasattr(self, 'translator') else "Smart Search",
                "Smart Search functionality is under development."
            )

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
            self.smart_search_widget,  # Added
            self.register_widget
        ]:
            if widget and hasattr(widget, 'update_translations'):
                widget.update_translations()