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

    # In gui/event_handlers.py - modify the handle_close_event method
    def handle_close_event(self, event):
        """Handle application closing with improved connection reuse."""
        try:
            # Store reference to existing database connection
            existing_db_connection = getattr(self, 'parts_db', None)

            # Capture view manager and parts navigation references
            view_manager = getattr(self.parent, 'view_manager', None)
            parts_nav = None
            if view_manager:
                parts_nav = getattr(view_manager, 'parts_navigation_widget', None)

            # Step 1: Disable UI to prevent further user actions
            if hasattr(self.parent, 'setEnabled'):
                self.parent.setEnabled(False)

            # Step 2: Cleanup navigation widget if it exists
            if parts_nav:
                try:
                    if hasattr(parts_nav, 'cleanup_resources'):
                        # Pass the existing connection to avoid creating a new one
                        parts_nav.cleanup_resources(existing_db_connection)
                    elif hasattr(parts_nav, 'cleanup_animations'):
                        parts_nav.cleanup_animations()
                except Exception as e:
                    logger.error(f"Error cleaning up parts navigation: {e}")

            # Process events to allow Qt to handle deletions
            QApplication.processEvents()

            # Step 3: Close database connections - only once at the end
            try:
                if existing_db_connection:
                    logger.info("Closing database connection...")
                    existing_db_connection.close_connection()
            except Exception as e:
                logger.error(f"Error closing parts database: {e}")

            # Close settings DB
            try:
                if hasattr(self, 'settings_db') and self.settings_db:
                    self.settings_db.close()
            except Exception as e:
                logger.error(f"Error closing settings database: {e}")

            # Accept the event to allow the application to close
            event.accept()

        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}")
            # Still accept the event to allow shutdown
            event.accept()