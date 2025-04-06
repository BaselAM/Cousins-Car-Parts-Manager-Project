# gui/event_handlers.py

import sys
import gc
from PyQt5.QtWidgets import QApplication
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
        Handle application closing.

        Args:
            event: The close event to handle
        """
        try:
            # First clean up any parts navigation threads/animations
            if hasattr(self.parent, 'view_manager') and \
                    hasattr(self.parent.view_manager, 'parts_navigation_widget') and \
                    self.parent.view_manager.parts_navigation_widget:

                parts_nav = self.parent.view_manager.parts_navigation_widget
                if hasattr(parts_nav, 'cleanup_animations'):
                    parts_nav.cleanup_animations()

            # Process events to complete any pending operations
            QApplication.processEvents()

            # Close database connections
            self.parts_db.close_connection()
            self.settings_db.close()

            # Clean up resources
            if hasattr(self.parent, 'ui_builder') and hasattr(self.parent.ui_builder, 'top_bar'):
                self.parent.ui_builder.top_bar.deleteLater()

            if hasattr(self.parent, 'content_stack'):
                self.parent.content_stack.deleteLater()

            # Process pending events
            QApplication.processEvents()

            # Force garbage collection
            gc.collect()

            event.accept()
        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}")
            sys.exit(1)