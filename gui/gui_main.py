# gui/gui_main.py
from pathlib import Path
import sys

# Logger setup
from logger import get_logger

logger = get_logger(__name__)

# Third-party imports
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QTime
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QShortcut
from PyQt5.QtWidgets import QMessageBox, QSizePolicy, QStackedWidget
from PyQt5.QtGui import QKeySequence

# Local application imports
from database.car_parts_db import CarPartsDB
from database.settings_db import SettingsDB
from themes import set_theme, get_color
from translations import get_translator
from size_policy import SizePolicyMixin

# Import GUI component managers
from .window_manager import GUIWindowManager
from .view_manager import GUIViewManager
from .ui_builder import GUIBuilder
from .theme_manager import GUIThemeManager
from .layout_manager import GUILayoutManager
from .event_handlers import GUIEventHandler
from .language_manager import GUILanguageManager


class GUI(QMainWindow, SizePolicyMixin):
    """
    Main application window that coordinates all GUI components.
    Delegates specific functionality to specialized manager classes.
    Performance optimized for smooth initialization and theme changes.
    """
    language_changed = pyqtSignal()

    def __init__(self, car_parts_db=None):
        super().__init__()

        # Initialize resize handling flags
        self._in_resize = False
        self._resize_processing = False

        # Set application as visible but disable user interaction initially
        self.setEnabled(False)

        # Initialize databases
        self.settings_db = SettingsDB()
        self.parts_db = car_parts_db if car_parts_db else CarPartsDB()

        # Load theme
        saved_theme = self.settings_db.get_setting('theme', 'classic')
        set_theme(saved_theme)

        # Initialize language and direction
        self.current_language = self.settings_db.get_setting('language', 'en')
        self.rtl_enabled = self.settings_db.get_rtl_setting()
        self.translator = get_translator(self.current_language)

        # Initialize component managers
        self.window_manager = GUIWindowManager(self)
        self.view_manager = GUIViewManager(self, self.translator, self.parts_db)
        self.theme_manager = GUIThemeManager(self)
        self.layout_manager = GUILayoutManager(self, self.rtl_enabled)
        self.event_handler = GUIEventHandler(self, self.parts_db, self.settings_db)
        self.language_manager = GUILanguageManager(self, self.translator, self.settings_db)

        # Setup base UI components
        self.content_stack = None
        self.main_widget = None
        self.main_layout = None

        # Setup the basic window properties first
        self.window_manager.setup_window_properties(self.translator)

        # Setup fullscreen keyboard shortcut
        fullscreen_shortcut = QShortcut(QKeySequence("F11"), self)
        fullscreen_shortcut.activated.connect(self.toggle_fullscreen)

        # Use a timer to defer UI setup until after the window is shown
        # This allows the splash screen to display without UI freezing
        QTimer.singleShot(100, self.setup)

    def setup(self):
        """Initialize the application UI with delayed execution for better performance"""
        try:
            # Setup window properties and size
            self.window_manager.center_window()

            # Preload views and UI components in the background
            QTimer.singleShot(10, self.view_manager.preload_views)

            # Create and configure basic UI structure immediately
            self.ui_builder = GUIBuilder(
                self,
                self.translator,
                self.view_manager,
                self.parts_db
            )
            self.ui_builder.setup_ui()

            # Apply initial minimal theme to make UI visible
            self.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {get_color('background')};
                }}
                QWidget {{
                    color: {get_color('text')};
                    font-family: 'Segoe UI', sans-serif;
                }}
            """)

            # Set initial layout direction
            self.layout_manager.apply_layout_direction_initially()

            # Apply final size adjustments
            self.window_manager.optimize_window_size()
            self.window_manager.center_window()

            # Show home page
            self.show_home()

            # Re-enable user interaction
            self.setEnabled(True)

            # Defer full theme application to improve startup performance
            QTimer.singleShot(500, self._complete_setup)

        except Exception as e:
            logger.error(f"Error in setup: {str(e)}")

    def _complete_setup(self):
        """Complete setup tasks after window is visible"""
        try:
            # Apply theme to all components using the theme manager
            self.theme_manager.apply_theme()

            # Ensure window is perfectly centered with equal margins
            self.window_manager.center_window()
        except Exception as e:
            logger.error(f"Error in _complete_setup: {str(e)}")

    # Navigation methods delegated to view_manager
    def show_home(self):
        """Switch to home page view"""
        try:
            self.view_manager.show_home(self.content_stack)
        except Exception as e:
            logger.error(f"Error showing home page: {str(e)}")

    def show_products(self):
        """Switch to products view"""
        self.view_manager.show_products(self.content_stack)

    def show_statistics(self):
        """Switch to statistics view"""
        self.view_manager.show_statistics(self.content_stack)

    def show_settings(self):
        """Switch to settings view"""
        self.view_manager.show_settings(self.content_stack)

    def show_help(self):
        """Switch to help documentation view"""
        self.view_manager.show_help(self.content_stack)

    def show_parts(self):
        """Open the parts navigation system with safer error handling"""
        try:
            if hasattr(self, 'view_manager') and self.view_manager:
                # Use a safer approach with exception handling
                self.view_manager.show_parts(self.content_stack, self.translator)
            else:
                # Fallback if view_manager is not available
                QMessageBox.information(
                    self,
                    self.translator.t("parts_button") if hasattr(self, 'translator') else "Parts",
                    "Parts navigation is not available at this time."
                )
        except Exception as e:
            logger.error(f"Error in show_parts: {str(e)}")
            # Show a user-friendly message
            QMessageBox.warning(
                self,
                self.translator.t("error") if hasattr(self, 'translator') else "Error",
                f"Could not show parts navigation: {str(e)}"
            )

    def show_register(self):
        """Switch to register view for sales and inventory management"""
        try:
            if hasattr(self, 'view_manager') and self.view_manager:
                logger.info("Showing register view")
                # Pass the content stack to the view manager
                self.view_manager.show_register(self.content_stack)
            else:
                # Fallback if view_manager is not available
                logger.warning("View manager not available for showing register")
                QMessageBox.information(
                    self,
                    self.translator.t("register_button") if hasattr(self, 'translator') else "Register",
                    "Register functionality is not available at this time."
                )
        except Exception as e:
            logger.error(f"Error in show_register: {str(e)}")
            # Show a user-friendly message
            QMessageBox.warning(
                self,
                self.translator.t("error") if hasattr(self, 'translator') else "Error",
                f"Could not show register: {str(e)}"
            )

    def show_web_search(self):
        """Open web search for car parts"""
        self.view_manager.show_web_search(self.translator)

    def show_notifications(self):
        """Show notifications panel"""
        self.view_manager.show_notifications(self.translator)

    def show_chat(self, message=None):
        """Handle chat messages from the chat widget"""
        self.view_manager.show_chat(message)

    def on_search_entered(self):
        """Handle search queries"""
        self.view_manager.on_search_entered(self.ui_builder.top_bar)

    def exit_app(self):
        """Close the application"""
        self.close()

    def update_language(self, new_lang):
        """Change the application language with improved performance"""
        # Disable window to prevent user input during update
        self.setEnabled(False)

        # Use QTimer to defer language update for better UI responsiveness
        QTimer.singleShot(10, lambda: self._perform_language_update(new_lang))

    def _perform_language_update(self, new_lang):
        """Perform actual language update with improved performance"""
        try:
            self.language_manager.update_language(new_lang)
            self.window_manager.center_window()

            # Re-enable the window after update is complete
            self.setEnabled(True)
        except Exception as e:
            logger.error(f"Error updating language: {str(e)}")
            self.setEnabled(True)

    def closeEvent(self, event):
        """Handle application closing"""
        self.event_handler.handle_close_event(event)

    def set_current_user(self, username):
        """Set the current logged-in username and update displays"""
        if hasattr(self.view_manager, 'home_page') and self.view_manager.home_page:
            self.view_manager.home_page.update_user(username)

    def simulate_resize(self):
        """Utility method to test responsive design by simulating window resizing"""
        self.window_manager.simulate_resize()

    def resizeEvent(self, event):
        """Handle window resize events with improved stability"""
        # Skip if we're already handling a resize event
        if self._in_resize:
            # Call parent class method and return
            super().resizeEvent(event)
            return

        try:
            self._in_resize = True
            super().resizeEvent(event)
        finally:
            self._in_resize = False

        # Don't trigger additional actions if we're maximized or in fullscreen
        if self.isMaximized() or self.isFullScreen():
            return

        # Skip additional processing if this is happening too frequently
        # This helps prevent the "vibrating" effect during manual resizing
        if self._resize_processing:
            return

        # Use a single timer to defer re-centering instead of immediate processing
        # This prevents the "bouncing" effect when dragging window edges
        if not hasattr(self, '_resize_timer'):
            self._resize_timer = QTimer(self)
            self._resize_timer.setSingleShot(True)
            self._resize_timer.timeout.connect(self._finish_resize)

        # Restart the timer each time we get a resize event
        self._resize_timer.start(200)  # 200ms delay to wait for the user to finish resizing

        # Let the window manager know this was a manual resize
        if hasattr(self.window_manager, '_was_manually_resized'):
            self.window_manager._was_manually_resized = True

    def _finish_resize(self):
        """Handle resize completion after the user has stopped resizing"""
        try:
            self._resize_processing = True

            # Only run window manager centering if not in a drag operation
            if hasattr(self, 'window_manager'):
                # Skip recentering during resize operations
                # This is key to preventing the vibration issue
                pass
        finally:
            self._resize_processing = False

    # Add this method to properly handle full screen toggle
    def toggle_fullscreen(self):
        """Toggle between fullscreen and normal window states"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

        # Force update the UI after fullscreen toggle
        QTimer.singleShot(100, self._update_after_fullscreen)

    def _update_after_fullscreen(self):
        """Update UI components after fullscreen toggle"""
        # Notify all components that care about window size
        if hasattr(self, 'theme_manager'):
            self.theme_manager.apply_theme()

        # Update the top bar if it exists
        if hasattr(self, 'ui_builder') and hasattr(self.ui_builder, 'top_bar'):
            self.ui_builder.top_bar.update_layout_margins()
            self.ui_builder.top_bar._update_layout_mode()

    def update_theme(self, new_theme):
        """Change the application theme with synchronous updates for visual consistency."""
        try:
            # Show wait cursor for potentially slow operation
            QApplication.setOverrideCursor(Qt.WaitCursor)

            # Disable window to prevent user input during update
            self.setEnabled(False)

            # Save settings
            self.settings_db.save_setting('theme', new_theme)

            # Update current theme
            set_theme(new_theme)

            # Find copyright widget directly
            copyright_widget = None
            for widget in self.findChildren(QWidget):
                if widget.__class__.__name__ == 'CopyrightWidget':
                    copyright_widget = widget
                    break

            # Apply basic theme immediately for visual feedback
            base_style = f"""
                QMainWindow {{
                    background-color: {get_color('background')};
                }}
                QWidget {{
                    color: {get_color('text')};
                    font-family: 'Segoe UI', sans-serif;
                }}
            """
            self.setStyleSheet(base_style)

            # Force synchronous theme updates - no batching
            # First update copyright and critical components
            if copyright_widget and hasattr(copyright_widget, 'apply_theme'):
                copyright_widget.apply_theme()

            # Update all findable widgets immediately
            for widget in self.findChildren(QWidget):
                if hasattr(widget, 'apply_theme'):
                    widget.apply_theme()

            # Update any ProductsWidget instances
            from widgets.products import ProductsWidget
            for widget in self.findChildren(ProductsWidget):
                if hasattr(widget, 'handle_theme_change'):
                    widget.handle_theme_change()

            # Force repaint of all widgets
            self.repaint()
            if self.main_widget:
                self.main_widget.repaint()

            # Re-center window after theme change
            self.window_manager.center_window()

            logger.info("Theme update completed synchronously")

            # Restore cursor and enable window after brief delay
            QTimer.singleShot(100, lambda: QApplication.restoreOverrideCursor())
            QTimer.singleShot(100, lambda: self.setEnabled(True))

        except Exception as e:
            logger.error(f"Theme update error: {str(e)}")
            QApplication.restoreOverrideCursor()
            self.setEnabled(True)

    def _complete_theme_update(self):
        """Complete theme update in the background"""
        try:
            # Apply theme to all components using the theme manager
            self.theme_manager.apply_theme()

            # Update any ProductsWidget instances
            from widgets.products import ProductsWidget
            for widget in self.findChildren(ProductsWidget):
                if hasattr(widget, 'handle_theme_change'):
                    widget.handle_theme_change()

            # Re-center window after theme change
            self.window_manager.center_window()

            logger.info("Theme update completed")

            # Restore cursor and enable window
            QApplication.restoreOverrideCursor()
            self.setEnabled(True)
        except Exception as e:
            logger.error(f"Error completing theme update: {str(e)}")
            QApplication.restoreOverrideCursor()
            self.setEnabled(True)