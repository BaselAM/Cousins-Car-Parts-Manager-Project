from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from widgets.workers import DatabaseWorker
import mysql.connector
import threading


class ProductLoader(QObject):
    """Handles loading product data with elegant performance optimization."""

    # Signals
    products_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    loading_started = pyqtSignal()  # New signal for UI feedback

    # Class-level semaphore to limit concurrent connections
    _worker_semaphore = threading.Semaphore(2)  # Allow up to 2 concurrent workers

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.worker_thread = None
        self._default_sort_column = 2  # Product name column
        self._default_sort_order = 0  # Ascending
        self._recent_products = []  # Track recently added/updated products

    def load_products(self, is_closing=False):
        """Load products with elegant visual feedback."""
        if is_closing:
            return

        # Emit signal that loading has started (for UI feedback)
        self.loading_started.emit()

        # Store current sort and selection state
        self._save_current_view_state()

        # Don't start a new worker if we can't acquire the semaphore
        if not self._worker_semaphore.acquire(blocking=False):
            self.error_occurred.emit("Operation in progress, please wait")
            return

        try:
            # Cancel any running thread
            if self.worker_thread and self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread.wait(500)

            # Start new worker
            self.worker_thread = DatabaseWorker(self.db, "load")

            # Connect signals with proper cleanup
            def on_finished(result):
                self._worker_semaphore.release()
                # Preserve recent products for highlighting
                self._tag_recent_products(result)
                self.products_loaded.emit(result)

            def on_error(error_msg):
                self._worker_semaphore.release()
                self.error_occurred.emit(error_msg)

            self.worker_thread.finished.connect(on_finished)
            self.worker_thread.error.connect(on_error)
            self.worker_thread.start()

        except Exception as e:
            self._worker_semaphore.release()
            self.error_occurred.emit(f"Loading error: {str(e)}")

    # Add this to your product_loader.py file

    def load_single_product(self, product_id):
        """Load a single product without triggering cascading updates."""
        # Exit early if we're already loading this product
        if hasattr(self, '_loading_product_id') and self._loading_product_id == product_id:
            print(f"Prevented duplicate load for product {product_id}")
            return None

        self._loading_product_id = product_id

        try:
            # Just fetch the product directly
            product = self.db.get_part(product_id)
            if not product:
                self._loading_product_id = None
                return None

            # Mark as recent for highlighting
            self._add_recent_product(product_id)

            # Signal just once with this product
            self.products_loaded.emit([product])

            # Reset the flag after a short delay
            QTimer.singleShot(500, lambda: setattr(self, '_loading_product_id', None))

            return product
        except Exception as e:
            self._loading_product_id = None
            print(f"Error in load_single_product: {e}")
            return None

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
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait(1000)


