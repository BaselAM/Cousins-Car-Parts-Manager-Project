from pathlib import Path
import sys

# Logger setup
from logger import get_logger

logger = get_logger(__name__)

# Third-party imports
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow, QApplication, QWidget, QVBoxLayout, QStackedWidget,
    QMessageBox, QSizePolicy, QDesktopWidget
)

# Local application imports
from database.car_parts_db import CarPartsDB
from database.settings_db import SettingsDB
from themes import set_theme, get_color, get_size, get_font_size
from translations import get_translator
from widgets.header import TopBarWidget
from widgets.help import HelpWidget
from widgets.home_page import HomePageWidget
from widgets.layout import HeaderWidget, FooterWidget, CopyrightWidget
from widgets.parts_navigation import PartsNavigationContainer
from widgets.products import ProductsWidget
from widgets.settings.settings_widget import SettingsWidget
from widgets.statistics import StatisticsWidget
from size_policy import SizePolicyMixin


class GUI(QMainWindow, SizePolicyMixin):
    language_changed = pyqtSignal()

    def __init__(self, car_parts_db=None):
        super().__init__()
        # Initialize databases
        self.settings_db = SettingsDB()

        # Use provided database instance or create a new one
        self.parts_db = car_parts_db if car_parts_db else CarPartsDB()

        # Load theme
        saved_theme = self.settings_db.get_setting('theme', 'classic')
        set_theme(saved_theme)

        # Initialize language and direction
        self.current_language = self.settings_db.get_setting('language', 'en')
        self.rtl_enabled = self.settings_db.get_rtl_setting()

        # Get shared translator instance from the manager
        self.translator = get_translator(self.current_language)

        # Setup UI components
        self.setup_window_properties()
        self.preload_views()
        self.setup_ui()
        self.apply_theme()

        # Set initial layout direction
        self._apply_layout_direction_initially()

        # Apply final size adjustments
        self.optimize_window_size()


    def optimize_window_size(self):
        """Make final adjustments to window size after UI is created"""
        # Calculate the optimal height based on content requirements
        optimal_height = self.calculate_optimal_height()

        # Get current geometry
        current_geo = self.geometry()

        # Set the new geometry with optimal height
        self.setGeometry(
            current_geo.x(),
            current_geo.y(),
            current_geo.width(),
            optimal_height
        )

    # Update setup_window_properties in gui.py:

    def setup_window_properties(self):
        """Configure the main window size and position with taller proportions"""
        self.setWindowTitle(self.translator.t("window_title"))

        # Get available screen geometry
        screen = QDesktopWidget().availableGeometry()

        # Use more generous dimensions - 60% width, 80% height for better usability
        width_percent = 0.7
        height_percent = 0.8  # Increased from 0.75 to make window taller

        width = int(screen.width() * width_percent)
        height = int(screen.height() * height_percent)

        # Calculate center position
        x = screen.x() + (screen.width() - width) // 2
        y = screen.y() + (screen.height() - height) // 2

        # Set the geometry
        self.setGeometry(x, y, width, height)

        # Set reasonable minimum size
        min_width = int(screen.width() * 0.45)
        min_height = int(screen.height() * 0.6)  # Increased from 0.55
        self.setMinimumSize(min_width, min_height)

    # Update calculate_optimal_height in gui.py:

    def calculate_optimal_height(self):
        """Calculate optimal window height based on content"""
        # Get screen constraints
        screen = QDesktopWidget().availableGeometry()

        # Estimate required component heights with more generous allocations
        header_height = get_size("header_height")
        top_bar_height = 52
        content_min_height = 500  # Increased from 450 for a taller content area
        footer_height = get_size("footer_height")
        copyright_height = get_size("copyright_height")

        # Calculate total height with additional padding
        total_height = (
                header_height +
                top_bar_height +
                content_min_height +
                footer_height +
                copyright_height +
                get_size("spacing_large") * 2
        )

        # Constrain to reasonable minimum height (60% of screen)
        min_height = int(screen.height() * 0.6)  # Increased from 0.55

        return max(min_height, total_height)

    def preload_views(self):
        """Initialize all view widgets"""
        self.products_widget = ProductsWidget(self.translator, self.parts_db, parent=self)
        self.statistics_widget = StatisticsWidget(self.translator, parent=self)
        self.settings_widget = SettingsWidget(self.translator, self.update_language, self)
        self.help_widget = HelpWidget(self.translator, parent=self)
        self.parts_navigation_widget = PartsNavigationContainer(self.translator,
                                                                self.parts_db,
                                                                parent=self)

    def setup_ui(self):
        """Create and arrange all UI components"""
        navigation_functions = {
            'products_button': self.show_products,
            'statistics_button': self.show_statistics,
            'settings_button': self.show_settings,
            'help_button': self.show_help,
            'parts_button': self.show_parts,
            'web_search_button': self.show_web_search,
            'exit_button': self.exit_app
        }

        # Create main widgets
        self.home_page = HomePageWidget(self.translator, navigation_functions, parent=self)
        self.header = HeaderWidget(self.translator, self.show_home, parent=self)
        self.top_bar = TopBarWidget(self.translator, self.parts_db, parent=self)
        self.footer = FooterWidget(self.translator, parent=self)
        copyright_widget = CopyrightWidget(self.translator, parent=self)

        # Make top components more compact
        self.header.setMaximumHeight(get_size("header_height"))
        self.header.setMinimumHeight(get_size("header_height") * 0.8)

        # DO NOT set fixed height constraints for the responsive top bar
        # The responsive top bar will manage its own sizing

        # Make footer components more compact but don't limit max height
        # This allows them to scale better when window is expanded
        self.footer.setMinimumHeight(get_size("footer_height") * 0.7)
        copyright_widget.setMinimumHeight(get_size("copyright_height") * 0.7)

        # Connect top bar signals
        self.top_bar.home_clicked.connect(self.show_home)
        self.top_bar.notification_clicked.connect(self.show_notifications)
        self.top_bar.chat_clicked.connect(self.show_chat)
        self.top_bar.search_submitted.connect(self.on_search_entered)

        # Create stacked widget for content
        self.content_stack = QStackedWidget()
        self.content_stack.addWidget(self.home_page)
        self.content_stack.addWidget(self.products_widget)
        self.content_stack.addWidget(self.statistics_widget)
        self.content_stack.addWidget(self.settings_widget)
        self.content_stack.addWidget(self.help_widget)
        self.content_stack.addWidget(self.parts_navigation_widget)

        # Use better size policies for content - expanding in both directions for full screen use
        self.content_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set appropriate size policies for parts_navigation_widget
        self.parts_navigation_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.parts_navigation_widget.setMinimumSize(0, 0)  # Remove any minimum size constraints

        # Main layout with reduced spacing
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)  # No spacing between components for more compact look

        main_layout.addWidget(self.header)
        main_layout.addWidget(self.top_bar)
        main_layout.addWidget(self.content_stack, 10)  # Content gets most of the space
        main_layout.addWidget(self.footer)
        main_layout.addWidget(copyright_widget)

        # Set as central widget
        self.setCentralWidget(main_widget)

        # Start with home page
        self.show_home()

    def apply_theme(self):
        """Apply current theme to main window and components"""
        bg_color = get_color('background')
        text_color = get_color('text')

        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {bg_color};
            }}
            QWidget {{
                color: {text_color};
                font-family: 'Segoe UI', sans-serif;
            }}
        """)

        # Apply theme to all components that support it
        for widget in self.findChildren(QWidget):
            if hasattr(widget, 'apply_theme'):
                widget.apply_theme()

    def _apply_layout_direction_initially(self):
        """Set initial layout direction based on settings"""
        direction = Qt.RightToLeft if self.rtl_enabled else Qt.LeftToRight
        QApplication.setLayoutDirection(direction)
        self._apply_layout_direction_recursive(self, direction)

    def _apply_layout_direction_recursive(self, widget, direction):
        """Recursively set layout direction for all child widgets"""
        widget.setLayoutDirection(direction)
        for child in widget.findChildren(QWidget):
            child.setLayoutDirection(direction)

    def show_home(self):
        """Switch to home page view"""
        try:
            self.content_stack.setCurrentWidget(self.home_page)
        except Exception as e:
            logger.error(f"Error showing home page: {str(e)}")

    def show_products(self):
        """Switch to products view"""
        self.content_stack.setCurrentWidget(self.products_widget)

    def show_statistics(self):
        """Switch to statistics view"""
        self.content_stack.setCurrentWidget(self.statistics_widget)

    def show_settings(self):
        """Switch to settings view"""
        self.content_stack.setCurrentWidget(self.settings_widget)

    def show_help(self):
        """Switch to help documentation view"""
        self.content_stack.setCurrentWidget(self.help_widget)

    def show_notifications(self):
        """Show notifications panel"""
        QMessageBox.information(self, self.translator.t("notifications"),
                                self.translator.t("popout_notifications"))

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

    def on_search_entered(self):
        """Handle search queries"""
        search_text = self.top_bar.search_widget.search_edit.text().strip()
        if search_text:
            self.show_products()
            self.products_widget.highlight_product(search_text)

    def exit_app(self):
        """Close the application"""
        self.close()

    def update_language(self, new_lang):
        """Change the application language"""
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            # Save settings
            is_rtl = (new_lang == 'he')
            self.settings_db.save_setting('rtl', str(is_rtl).lower())
            self.settings_db.save_setting('language', new_lang)

            # Update state
            self.current_language = new_lang
            self.rtl_enabled = is_rtl

            # Get the updated shared translator
            self.translator = get_translator(new_lang)

            # Apply direction changes
            direction = Qt.RightToLeft if is_rtl else Qt.LeftToRight
            QApplication.setLayoutDirection(direction)
            self._apply_layout_direction_recursive(self, direction)

            # Refresh theme and translations
            self.apply_theme()
            self._full_ui_refresh()

        except Exception as e:
            logger.error(f"Language update error: {str(e)}")
            QMessageBox.critical(self, self.translator.t("error"),
                                self.translator.t('settings_save_error'))
        finally:
            QApplication.restoreOverrideCursor()

    def _full_ui_refresh(self):
        """Refresh all UI components after language change"""
        # Update all widgets with translations
        self.header.update_translations()
        self.top_bar.update_translations()
        self.footer.update_translations()
        self.home_page.update_translations()
        self.products_widget.update_translations()
        self.statistics_widget.update_translations()
        self.settings_widget.update_translations()
        self.help_widget.update_translations()

        # Update parts navigation if it has the method
        if hasattr(self.parts_navigation_widget, 'update_translations'):
            self.parts_navigation_widget.update_translations()

        # Force layout update
        self.updateGeometry()
        QApplication.processEvents()

    def closeEvent(self, event):
        """Handle application closing"""
        try:
            # Close database connections
            self.parts_db.close_connection()
            self.settings_db.close()

            # Clean up resources
            self.top_bar.deleteLater()
            self.content_stack.deleteLater()

            # Process pending events
            QApplication.processEvents()

            import gc
            gc.collect()  # Force garbage collection

            event.accept()
        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}")
            sys.exit(1)

    def show_parts(self):
        """Open the parts navigation system"""
        try:
            self.content_stack.setCurrentWidget(self.parts_navigation_widget)
        except Exception as e:
            logger.error(f"Error showing parts navigation: {str(e)}")
            QMessageBox.warning(self, self.translator.t("parts_button"),
                                f"Could not load parts navigation: {str(e)}")

    def show_web_search(self):
        """Open web search for car parts"""
        # You'll need to implement this feature
        QMessageBox.information(self, self.translator.t("web_search_button"),
                               self.translator.t("search_options"))

    def apply_theme_to_all(self):
        """Apply current theme to all components"""
        try:
            # Apply theme to main window
            self.apply_theme()

            # Apply theme to all widgets that support it
            widgets_with_theme = [
                self.header,
                self.top_bar,
                self.home_page,
                self.footer,
                self.products_widget,
                self.statistics_widget,
                self.settings_widget,
                self.help_widget,
                self.parts_navigation_widget
            ]

            for widget in widgets_with_theme:
                if hasattr(widget, 'apply_theme'):
                    widget.apply_theme()
        except Exception as e:
            logger.error(f"Error applying theme to all components: {str(e)}")

    def set_current_user(self, username):
        """Set the current logged-in username and update displays"""
        self.current_username = username

        # Update home page if it exists
        if hasattr(self, 'home_page') and self.home_page:
            self.home_page.update_user(username)

    def simulate_resize(self):
        """Utility method to test responsive design by simulating window resizing"""
        # Save current size
        current_size = self.size()

        # Test at 80% of current size
        self.resize(int(current_size.width() * 0.8), int(current_size.height() * 0.8))
        QApplication.processEvents()

        # Test at 120% of current size
        self.resize(int(current_size.width() * 1.2), int(current_size.height() * 1.2))
        QApplication.processEvents()

        # Restore original size
        self.resize(current_size)
        QApplication.processEvents()

    def resizeEvent(self, event):
        """Handle window resize events with improved scaling behavior"""
        super().resizeEvent(event)

        # Let top bar handle responsive adjustments through its own resize event system
        # No need to explicitly call any methods, Qt's event system will handle this