# gui/event_handlers.py

import sys
import gc

from PyQt5 import sip
from PyQt5.QtWidgets import QApplication, QWidget
from logger import get_logger

logger = get_logger(__name__)


class GUIEventHandler:
    """
    Handles application events like close, resize, etc.
    Manages cleanup and resource handling.
    """

    def __init__(self, parent, parts_db, settings_db):
        """
        Initialize the event handler.

        Args:
            parent: The main GUI instance
            parts_db: Database connection for parts data
            settings_db: Database connection for settings data
        """
        self.parent = parent
        self.parts_db = parts_db
        self.settings_db = settings_db

    def handle_close_event(self, event):
        """
        Handle application closing with improved cleanup sequence.

        Args:
            event: The close event to handle
        """
        try:
            # Capture references first to avoid accessing deleted objects
            view_manager = getattr(self.parent, 'view_manager', None)
            parts_nav = None

            if view_manager:
                parts_nav = getattr(view_manager, 'parts_navigation_widget', None)

            content_stack = getattr(self.parent, 'content_stack', None)
            top_bar = None

            if hasattr(self.parent, 'ui_builder'):
                top_bar = getattr(self.parent.ui_builder, 'top_bar', None)

            # Step 1: Disable UI to prevent further user actions
            if hasattr(self.parent, 'setEnabled'):
                self.parent.setEnabled(False)

            # Step 2: Cleanup navigation widget if it exists
            if parts_nav:
                try:
                    if hasattr(parts_nav, 'cleanup_resources'):
                        parts_nav.cleanup_resources()
                    elif hasattr(parts_nav, 'cleanup_animations'):
                        parts_nav.cleanup_animations()
                except Exception as e:
                    logger.error(f"Error cleaning up parts navigation: {e}")

                # Remove from content stack if it's still there
                if content_stack and parts_nav in content_stack.findChildren(QWidget) and not sip.isdeleted(
                        content_stack):
                    try:
                        index = content_stack.indexOf(parts_nav)
                        if index >= 0:
                            content_stack.removeWidget(parts_nav)
                    except Exception as e:
                        logger.error(f"Error removing widget from stack: {e}")

            # Process events to allow Qt to handle deletions
            QApplication.processEvents()

            # Step 3: Close database connections
            try:
                if hasattr(self, 'parts_db') and self.parts_db:
                    self.parts_db.close_connection()
            except Exception as e:
                logger.error(f"Error closing parts database: {e}")

            try:
                if hasattr(self, 'settings_db') and self.settings_db:
                    self.settings_db.close()
            except Exception as e:
                logger.error(f"Error closing settings database: {e}")

            # Step 4: Carefully clean up UI components
            # Clear the contents of the stack first if it exists and hasn't been deleted
            if content_stack and not sip.isdeleted(content_stack):
                try:
                    # Set current index to 0 to avoid issues with deleted widgets
                    content_stack.setCurrentIndex(0)

                    # Remove all widgets safely
                    for i in range(content_stack.count() - 1, -1, -1):  # Remove in reverse order
                        try:
                            widget = content_stack.widget(i)
                            if widget:
                                content_stack.removeWidget(widget)
                        except Exception as e:
                            logger.error(f"Error removing widget {i} from stack: {e}")
                except Exception as e:
                    logger.error(f"Error clearing content stack: {e}")

            # Process events again to handle removals
            QApplication.processEvents()

            # Step 5: Clean up top bar last, since it might be used by other components
            if top_bar and not sip.isdeleted(top_bar):
                try:
                    top_bar.deleteLater()
                except Exception as e:
                    logger.error(f"Error deleting top bar: {e}")

            # Process events one more time
            QApplication.processEvents()

            # Step 6: Force garbage collection to clean up any remaining references
            gc.collect()

            # Accept the event to allow the application to close
            event.accept()

        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}")
            # Still accept the event to allow shutdown
            event.accept()