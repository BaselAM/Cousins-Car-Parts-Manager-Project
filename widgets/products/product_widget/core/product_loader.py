from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from utils.database_worker import DatabaseOperator  # Import the universal DatabaseOperator
import mysql.connector
import threading


class ProductLoader(QObject):
    """Handles loading product data with elegant performance optimization."""

    # Signals
    products_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    loading_started = pyqtSignal()  # New signal for UI feedback

    # Class-level semaphore to limit concurrent operations
    _operation_semaphore = threading.Semaphore(2)  # Allow up to 2 concurrent operations

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        # Create the database operator instead of individual workers
        self.db_operator = DatabaseOperator(db)
        self._default_sort_column = 2  # Product name column
        self._default_sort_order = 0  # Ascending
        self._recent_products = []  # Track recently added/updated products
        self._is_loading = False

    def load_products(self, is_closing=False):
        """Load products with elegant visual feedback."""
        if is_closing:
            return

        # Prevent duplicate operations
        if self._is_loading:
            return

        # Emit signal that loading has started (for UI feedback)
        self.loading_started.emit()

        # Store current sort and selection state
        self._save_current_view_state()

        # Don't start a new operation if we can't acquire the semaphore
        if not self._operation_semaphore.acquire(blocking=False):
            self.error_occurred.emit("Operation in progress, please wait")
            return

        # Mark as loading
        self._is_loading = True

        try:
            # Use the DatabaseOperator to execute the operation
            self.db_operator.execute(
                "get_all_parts",  # Operation name
                self._on_products_loaded,  # Success callback
                self._on_operation_error,  # Error callback
                force_refresh=True  # Optional parameter
            )
        except Exception as e:
            self._operation_semaphore.release()
            self._is_loading = False
            self.error_occurred.emit(f"Loading error: {str(e)}")

    def _on_products_loaded(self, products):
        """Handle loaded products."""
        # Release semaphore and reset loading flag
        self._operation_semaphore.release()
        self._is_loading = False

        if products:
            # Preserve recent products for highlighting
            self._tag_recent_products(products)
            # Emit the loaded products
            self.products_loaded.emit(products)
        else:
            # Handle empty result
            self.products_loaded.emit([])

    def _on_operation_error(self, error_message):
        """Handle operation errors."""
        # Release semaphore and reset loading flag
        self._operation_semaphore.release()
        self._is_loading = False
        # Emit the error
        self.error_occurred.emit(error_message)

    def load_single_product(self, product_id):
        """Load a single product without triggering cascading updates."""
        # Exit early if we're already loading this product
        if hasattr(self, '_loading_product_id') and self._loading_product_id == product_id:
            print(f"Prevented duplicate load for product {product_id}")
            return None

        # Don't start a new operation if we can't acquire the semaphore
        if not self._operation_semaphore.acquire(blocking=False):
            self.error_occurred.emit("Operation in progress, please wait")
            return None

        self._loading_product_id = product_id

        try:
            # Use the DatabaseOperator to execute the operation
            self.db_operator.execute(
                "get_part_details",  # Operation name
                self._on_single_product_loaded,  # Success callback
                self._on_single_product_error,  # Error callback
                part_id=product_id  # Required parameter
            )

            # Return a placeholder - actual result will come through the callback
            return None
        except Exception as e:
            self._operation_semaphore.release()
            self._loading_product_id = None
            print(f"Error in load_single_product: {e}")
            return None

    def _on_single_product_loaded(self, product):
        """Handle loaded single product."""
        # Release semaphore
        self._operation_semaphore.release()

        if not product:
            self._loading_product_id = None
            return

        # Mark as recent for highlighting
        product_id = product.get('parcode', None)
        if product_id:
            self._add_recent_product(product_id)

        # Signal just once with this product
        self.products_loaded.emit([product])

        # Reset the flag after a short delay
        QTimer.singleShot(500, lambda: setattr(self, '_loading_product_id', None))

    def _on_single_product_error(self, error_message):
        """Handle single product load error."""
        # Release semaphore and reset loading ID
        self._operation_semaphore.release()
        self._loading_product_id = None
        # Emit the error
        self.error_occurred.emit(error_message)

    def _save_current_view_state(self):
        """Save table view state for consistent experience."""
        try:
            parent = self.parent()
            if parent and hasattr(parent, 'product_table') and hasattr(parent.product_table, 'table'):
                table = parent.product_table.table
                header = table.horizontalHeader()

                # Only update if a valid sort is set
                if header.sortIndicatorSection() >= 0:
                    self._default_sort_column = header.sortIndicatorSection()
                    self._default_sort_order = header.sortIndicatorOrder()
        except Exception as e:
            print(f"Error saving view state: {e}")

    def get_view_state(self):
        """Return current view settings for consistency."""
        return {
            'sort_column': self._default_sort_column,
            'sort_order': self._default_sort_order,
            'recent_products': self._recent_products.copy()
        }

    def _add_recent_product(self, product_id):
        """Track a product as recently added/updated."""
        # Maintain maximum of 5 recent products
        if product_id not in self._recent_products:
            self._recent_products.insert(0, product_id)
            self._recent_products = self._recent_products[:5]

    def _tag_recent_products(self, products):
        """Tag products that should be highlighted as recent."""
        for product in products:
            if isinstance(product, dict):
                product_id = product.get('parcode')
                if product_id in self._recent_products:
                    # Add a flag for the UI to recognize recent products
                    product['_is_recent'] = True
            elif isinstance(product, (list, tuple)) and len(product) > 0:
                product_id = product[0]
                if product_id in self._recent_products:
                    # For tuple products, we can't tag them directly
                    # The UI will need to check against the recent_products list
                    pass

    def clear_recent_products(self):
        """Clear the list of recent products."""
        self._recent_products = []

    def emergency_reload(self):
        """Emergency reload of products when normal loading fails."""
        print("Emergency reload initiated")
        try:
            # Save current sort before emergency reload
            self._save_current_view_state()

            import gc
            gc.collect()

            # Ensure we have a fresh connection from the pool
            if hasattr(self.db, 'ensure_connection'):
                self.db.ensure_connection()

            products = self.db.get_all_parts()
            print(f"Loaded {len(products)} products directly from database")
            self.products_loaded.emit(products)
            return products
        except mysql.connector.Error as mysql_err:
            print(f"MySQL error during emergency reload: {mysql_err}")
            import traceback
            print(traceback.format_exc())
            self.error_occurred.emit(f"Database error: {str(mysql_err)}")
            return []
        except Exception as e:
            print(f"Emergency reload failed: {e}")
            import traceback
            print(traceback.format_exc())
            self.error_occurred.emit(f"Emergency reload failed: {str(e)}")
            return []

    def cleanup(self):
        """Clean up resources before closing."""
        if hasattr(self, 'db_operator'):
            self.db_operator.cleanup()