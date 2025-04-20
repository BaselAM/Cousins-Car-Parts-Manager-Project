"""
Database synchronization module for the car parts application.

This module provides a centralized way for widgets to notify each other
about database changes, ensuring all views remain consistent.
"""
from PyQt5.QtCore import QObject, pyqtSignal
from logger import get_logger

# Get a logger for this module
logger = get_logger("database_sync")


class DatabaseSyncManager(QObject):
    """
    Singleton manager that handles synchronization of database changes across widgets.

    Widgets can connect to these signals to be notified when database operations occur:
    - product_added: When a product is added to the database
    - product_updated: When a product is updated
    - product_deleted: When a product is deleted
    - products_loaded: When products are loaded from the database
    """
    # Singleton instance
    _instance = None

    # Signals for database operations
    product_added = pyqtSignal(object)  # Emitted with new product ID/data
    product_updated = pyqtSignal(object)  # Emitted with updated product ID/data
    product_deleted = pyqtSignal(object)  # Emitted with deleted product ID
    products_loaded = pyqtSignal()  # Emitted when products are loaded

    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(DatabaseSyncManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the sync manager."""
        if self._initialized:
            return

        super().__init__()
        self._initialized = True
        self._listeners = []
        logger.info("Database sync manager initialized")

    # Enhanced emit methods for database_sync.py

    def emit_product_added(self, product_data):
        """Emit signal when a product is added with improved debugging."""
        logger.debug(f"Emitting product_added signal for product: {product_data}")

        # Print more detailed log for debugging
        print(f"\n===== DATABASE SYNC: PRODUCT ADDED =====")
        print(f"Product Name: {product_data.get('product_name')}")
        print(f"Product ID: {product_data.get('id')}")
        print(f"Parcode: {product_data.get('parcode')}")
        print(f"Current listeners: {len(self._listeners)}")

        # Emit the signal
        self.product_added.emit(product_data)

        print("Signal emitted - checking if received by listeners...")

    def emit_product_updated(self, product_data):
        """Emit signal when a product is updated with improved debugging."""
        logger.debug(f"Emitting product_updated signal for product: {product_data}")

        # Print more detailed log for debugging
        print(f"\n===== DATABASE SYNC: PRODUCT UPDATED =====")
        print(f"Product Name: {product_data.get('product_name')}")
        print(f"Product ID: {product_data.get('id')}")
        print(f"Parcode: {product_data.get('parcode')}")
        print(f"Current listeners: {len(self._listeners)}")

        # Emit the signal
        self.product_updated.emit(product_data)

        print("Signal emitted - checking if received by listeners...")

    def emit_product_deleted(self, product_id):
        """Emit signal when a product is deleted with improved debugging."""
        logger.debug(f"Emitting product_deleted signal for product ID: {product_id}")

        # Print more detailed log for debugging
        print(f"\n===== DATABASE SYNC: PRODUCT DELETED =====")
        print(f"Product ID: {product_id}")
        print(f"Current listeners: {len(self._listeners)}")

        # Emit the signal
        self.product_deleted.emit(product_id)

        print("Signal emitted - checking if received by listeners...")

    def emit_products_loaded(self):
        """Emit signal when products are loaded with improved debugging."""
        logger.debug("Emitting products_loaded signal")

        # Print more detailed log for debugging
        print(f"\n===== DATABASE SYNC: PRODUCTS LOADED =====")
        print(f"Current listeners: {len(self._listeners)}")

        # Emit the signal
        self.products_loaded.emit()

        print("Signal emitted - checking if received by listeners...")

    def register_listener(self, widget):
        """Register a widget as a listener for database change events."""
        if widget not in self._listeners:
            self._listeners.append(widget)
            logger.debug(f"Registered listener: {widget.__class__.__name__}")

    def unregister_listener(self, widget):
        """Unregister a widget from database change events."""
        if widget in self._listeners:
            self._listeners.remove(widget)
            logger.debug(f"Unregistered listener: {widget.__class__.__name__}")


# Create the global instance
db_sync_manager = DatabaseSyncManager()