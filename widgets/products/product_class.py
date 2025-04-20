# products_class.py (Enhanced Version)
import inspect
import traceback
import logging

from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.QtCore import QTimer, pyqtSlot, QEvent, Qt

# Create module logger
logger = logging.getLogger(__name__)

# Assuming original imports were correct for the first version
from .product_widget.core.product_loader import ProductLoader
from .product_widget.core.product_manager import ProductManager
from .product_widget.handlers.ui_handler import UIHandler  # Assumes this UIHandler uses stylesheets for :checked state
from .product_widget.handlers.search_handler import SearchHandler
from .product_widget.handlers.filter_handler import FilterHandler
from .product_widget.handlers.edit_handler import EditHandler
from .product_widget.handlers.selection_handler import SelectionHandler
from .product_widget.operations.add_operation import AddOperation
from .product_widget.operations.delete_operation import DeleteOperation
from .product_widget.operations.export_operation import ExportOperation
from .product_widget.operations.print_operation import PDFPrintOperation  # New import
# Add this after your other imports
from widgets.products.components.barcode_scanner_button import BarcodeScannerButton

from .utils import ProductValidator
from .dialogs import FilterDialog, DeleteConfirmationDialog, AddProductDialog


class SignalBlocker:
    """Context manager to block signals during UI operations"""

    def __init__(self, *widgets):
        self.widgets = widgets
        self.states = {}

    def __enter__(self):
        # Store and block signals for all widgets
        for widget in self.widgets:
            if widget is not None:
                self.states[widget] = widget.signalsBlocked()
                widget.blockSignals(True)
        return self

    def __exit__(self, *args):
        # Restore original signal blocking state
        for widget, state in self.states.items():
            widget.blockSignals(state)


# Use the original class signature (add type hints only if they were in the original)
class ProductsWidget(QWidget):
    """
    Enhanced product management widget with improved search functionality and performance.
    Provides an elegant, intuitive interface for managing product inventory.
    """

    def __init__(self, translator, db, parent=None):
        super().__init__(parent)
        self._is_closing = False
        self.translator = translator
        self.db = db

        # State flags for better control flow
        self._updating_ui = False
        self._updating_cell = False
        self._is_search_refresh = False
        self._search_in_progress = False

        # Initialize validator
        self.validator = ProductValidator(translator)

        # Initialize UI handler
        self.ui_handler = UIHandler(self, translator)
        ui_components = self.ui_handler.setup_ui()

        # Store UI components
        self.add_btn = ui_components['add_btn']
        self.select_toggle = ui_components['select_toggle']
        self.remove_btn = ui_components['remove_btn']
        self.filter_btn = ui_components['filter_btn']
        self.clear_filter_btn = ui_components['clear_filter_btn']
        self.export_btn = ui_components['export_btn']
        self.print_btn = ui_components['print_btn']
        self.refresh_btn = ui_components['refresh_btn']
        self.search_input = ui_components['search_input']
        self.product_table = ui_components['product_table']
        self.status_bar = ui_components['status_bar']

        # Safely share status_bar with product_table for barcode scanning feedback
        if hasattr(self, 'product_table') and self.product_table:
            self.product_table.status_bar = self.status_bar
        if hasattr(self.ui_handler, 'connect_barcode_button'):
            self.ui_handler.connect_barcode_button(self.show_barcode_scanner)

        # Add barcode scanner button
        self._setup_barcode_scanner()

        # Connect to status bar state changes
        self.status_bar.state_changed.connect(self._handle_status_bar_state_change)

        # Initialize search timer with optimized delay
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._delayed_search)

        # Apply theme
        self.ui_handler.apply_theme()

        # Initialize core components
        self.product_manager = ProductManager(db)
        self.product_loader = ProductLoader(db, self)

        # Initialize handlers
        self.search_handler = SearchHandler(translator)
        self.filter_handler = FilterHandler(translator)
        self.edit_handler = EditHandler(translator, db)
        self.selection_handler = SelectionHandler(translator, self.product_table, self.ui_handler)

        # Initialize operations
        self.add_operation = AddOperation(self, translator, db, self.validator, self.status_bar)
        self.delete_operation = DeleteOperation(self, translator, db, self.status_bar)
        self.export_operation = ExportOperation(self, translator, self.status_bar)
        self.print_operation = PDFPrintOperation(self, translator, self.status_bar)

        # Connect signals
        self._connect_signals()

        # Load products after initialization
        QTimer.singleShot(100, self.load_products)

        # Modify the handle_loaded_products method to emit signals

    def handle_loaded_products(self, products):
        """Handle loaded products with elegant organization and visual feedback."""
        try:
            is_single_update = len(products) == 1 and self.product_manager.get_products()

            # Get view state
            view_state = {}
            if hasattr(self.product_loader, 'get_view_state'):
                view_state = self.product_loader.get_view_state()

            sort_column = view_state.get('sort_column', 2)
            sort_order = view_state.get('sort_order', 0)
            recent_products = view_state.get('recent_products', [])

            if is_single_update:
                # Handle single product update or addition
                self._handle_single_product_update(products[0], sort_column, sort_order)
            else:
                # Handle full product list update
                self._handle_bulk_products_update(products, sort_column, sort_order, recent_products)

            # Reset search refresh flag after products are loaded
            self._is_search_refresh = False

            # Notify other widgets that products were loaded if this was not triggered by sync
            if not hasattr(self, '_processing_sync_event') or not self._processing_sync_event:
                try:
                    from utils.database_sync import db_sync_manager
                    db_sync_manager.emit_products_loaded()
                except Exception as e:
                    logger.error(f"Error emitting products_loaded signal: {e}")

        except Exception as e:
            # Reset the search refresh flag in case of error
            self._is_search_refresh = False
            logger.error(f"Error loading products: {e}")
            self.status_bar.show_message(
                self.translate('load_error', "Error loading products"),
                "error"
            )

        # Modify the on_product_added method to emit signals

    def on_product_added(self, product_id):
        """Called after a product is added or updated"""
        # Highlight the product after a short delay
        QTimer.singleShot(100, lambda: self._highlight_product(product_id))

        # Notify other widgets about the addition
        if not hasattr(self, '_processing_sync_event') or not self._processing_sync_event:
            try:
                from utils.database_sync import db_sync_manager
                db_sync_manager.emit_product_added(product_id)
            except Exception as e:
                logger.error(f"Error emitting product_added signal: {e}")

        # Modify the on_products_deleted method to emit signals

    def on_products_deleted(self, deleted_ids):
        """Called after products are deleted"""
        self.product_manager.remove_products_by_ids(deleted_ids)
        self.load_products()

        # Notify other widgets about the deletion
        if not hasattr(self, '_processing_sync_event') or not self._processing_sync_event:
            try:
                from utils.database_sync import db_sync_manager
                for product_id in deleted_ids:
                    db_sync_manager.emit_product_deleted(product_id)
            except Exception as e:
                logger.error(f"Error emitting product_deleted signal: {e}")

        # Modify the on_cell_changed method to emit signals for updates

    def on_cell_changed(self, row, column):
        """Handle cell value changes"""
        # Comprehensive guard conditions
        if (hasattr(self, '_updating_ui') and self._updating_ui or
                hasattr(self, '_updating_cell') and self._updating_cell or
                hasattr(self, '_search_in_progress') and self._search_in_progress or
                hasattr(self, '_is_search_refresh') and self._is_search_refresh or
                self.product_table.table.signalsBlocked()):
            return

        try:
            self._updating_cell = True
            # Rest of your existing code...
            success, product_id, field, new_value, message = self.edit_handler.handle_cell_change(
                row, column, self.product_table.table, self.product_manager.get_products()
            )

            if success:
                # Update in-memory product data
                self.product_manager.update_product_in_memory(product_id, field, new_value, column)

                # Show the message with high priority
                self.show_status_message(message, "success", priority=70)

                # Notify other widgets about the update
                if not hasattr(self, '_processing_sync_event') or not self._processing_sync_event:
                    try:
                        from utils.database_sync import db_sync_manager
                        db_sync_manager.emit_product_updated(product_id)
                    except Exception as e:
                        logger.error(f"Error emitting product_updated signal: {e}")
        except Exception as e:
            logger.error(f"Error handling cell change: {e}")
        finally:
            self._updating_cell = False

        # Modify the closeEvent method to disconnect from sync manager

    def closeEvent(self, event):
        """Handle widget close event"""
        try:
            self._is_closing = True

            # Disconnect from sync manager
            self.disconnect_from_sync_manager()

            if hasattr(self.product_loader, 'cleanup'):
                self.product_loader.cleanup()
            self.product_manager.clear()
        except Exception as e:
            logger.error(f"Error during close event: {e}")
        event.accept()

    def _setup_barcode_scanner(self):
        """Set up the barcode scanner button connection only, not creating a duplicate button"""
        try:
            # Just create the signal handler but don't add a visual button
            # This maintains the barcode scanning functionality without a duplicate button
            from widgets.products.components.barcode_scanner_button import BarcodeScannerButton

            # Create an "invisible" handler just for the signals and functionality
            self.barcode_scanner = BarcodeScannerButton(self, self.translator)
            self.barcode_scanner.setVisible(False)  # Make sure it's not visible
            self.barcode_scanner.setFixedSize(0, 0)  # Zero size
            logger.debug("Barcode scanner button successfully connected")
        except Exception as e:
            logger.error(f"Error setting up barcode scanner: {e}")
            self.barcode_scanner = None

    def _delayed_search(self):
        """Perform search after delay to avoid searching on every keystroke"""
        search_text = self.search_input.text().strip()

        # Guard against recursion and concurrent updates
        if hasattr(self, '_updating_ui') and self._updating_ui:
            return

        try:
            self._updating_ui = True
            self._is_search_refresh = True  # Mark as search operation
            self._search_in_progress = True

            if not search_text:
                # If search is cleared, reset to show all products
                self._reset_to_all_products()
            else:
                # Process the search
                self.on_search(search_text)
        finally:
            self._updating_ui = False
            self._search_in_progress = False
            # Note: _is_search_refresh is reset after products are loaded

    def _ensure_highlights_cleared(self):
        """Ensure all highlights are properly cleared after search is reset"""
        # Double-check that highlighting is removed
        if hasattr(self.product_table, '_reset_cell_formatting'):
            self.product_table._reset_cell_formatting()

        # Additionally reset any font changes
        try:
            if hasattr(self.product_table, 'table'):
                table = self.product_table.table
                for row in range(table.rowCount()):
                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        if item:
                            # Check if font is bold and reset it
                            font = item.font()
                            if font.bold():
                                font.setBold(False)
                                item.setFont(font)
        except Exception as e:
            logger.error(f"Error clearing highlights: {e}")

    def _highlight_exact_match(self, product, search_text):
        """Highlight and focus an exact match in the search results"""
        try:
            # Get the ID based on product type
            if isinstance(product, dict):
                product_id = product.get('id')
                product_name = product.get('product_name', '')
            else:  # Tuple
                product_id = product[0] if len(product) > 0 else None
                product_name = product[2] if len(product) > 2 else ''

            if product_id:
                # Auto-select the matching product
                QTimer.singleShot(100, lambda: self.product_table.highlight_row_by_id(str(product_id)))

                # Show a helpful message
                self.status_bar.show_message(
                    self.translate(
                        'exact_match_found',
                        f"Found exact match: {product_name}"
                    ).format(name=product_name),
                    "success",
                    3000
                )
        except Exception as e:
            logger.error(f"Error highlighting exact match: {e}")

    def _reset_search_flags(self):
        """Reset search-related flags after operations are complete"""
        self._is_search_refresh = False
        self._search_in_progress = False

    @pyqtSlot(list)
    def handle_loaded_products(self, products):
        """Handle loaded products with elegant organization and visual feedback."""
        try:
            is_single_update = len(products) == 1 and self.product_manager.get_products()

            # Get view state
            view_state = {}
            if hasattr(self.product_loader, 'get_view_state'):
                view_state = self.product_loader.get_view_state()

            sort_column = view_state.get('sort_column', 2)
            sort_order = view_state.get('sort_order', 0)
            recent_products = view_state.get('recent_products', [])

            if is_single_update:
                # Handle single product update or addition
                self._handle_single_product_update(products[0], sort_column, sort_order)
            else:
                # Handle full product list update
                self._handle_bulk_products_update(products, sort_column, sort_order, recent_products)

            # Reset search refresh flag after products are loaded
            self._is_search_refresh = False

        except Exception as e:
            # Reset the search refresh flag in case of error
            self._is_search_refresh = False
            logger.error(f"Error loading products: {e}")
            self.status_bar.show_message(
                self.translate('load_error', "Error loading products"),
                "error"
            )

    def _handle_single_product_update(self, product, sort_column, sort_order):
        """Handle update or addition of a single product"""
        product_id = product['parcode'] if isinstance(product, dict) else product[0]
        self.product_manager.update_or_add_product(product_id, product)
        product_name = product['product_name'] if isinstance(product, dict) else product[2]
        table = self.product_table.table

        # Find if product already exists in table
        found_row = -1
        for row in range(table.rowCount()):
            id_item = table.item(row, 0)
            if id_item and id_item.text() == str(product_id):
                found_row = row
                break

        # Save current sort state and disable sorting
        was_sorting_enabled = table.isSortingEnabled()
        table.setSortingEnabled(False)

        # Update or add the product
        if found_row >= 0:
            # Product exists - update it
            if hasattr(self.product_table, 'update_single_product'):
                self.product_table.update_single_product(product)
            else:
                # Fallback: remove and add
                table.removeRow(found_row)
                if hasattr(self.product_table, 'append_product'):
                    self.product_table.append_product(product)

            # Apply styling to highlight updated product
            if hasattr(self.product_table, '_apply_recent_styling'):
                row_to_style = found_row if hasattr(self.product_table, 'update_single_product') else 0
                self.product_table._apply_recent_styling(row_to_style)
        else:
            # Product is new - add it
            if hasattr(self.product_table, 'append_product'):
                self.product_table.append_product(product)
                if hasattr(self.product_table, '_apply_recent_styling'):
                    self.product_table._apply_recent_styling(0)
            else:
                # Fallback: reload all
                self.product_manager.set_products([product])
                self.product_table.update_table_data(self.product_manager.get_products())

        # Restore sorting
        if was_sorting_enabled:
            table.setSortingEnabled(True)
            table.sortByColumn(sort_column, sort_order)

        # Determine if this was an update or addition
        updated = product_id in [p['parcode'] if isinstance(p, dict) else p[0]
                                 for p in self.product_manager.get_products()
                                 if p != product]

        # Only show update message if this was not triggered by search
        if not self._is_search_refresh:
            message_key = 'product_updated' if updated else 'product_added'
            fallback = f"Product '{product_name}' {'updated' if updated else 'added'} successfully"

            self.status_bar.show_message(
                self.translate(message_key, fallback).format(name=product_name),
                "success"
            )

        # Highlight the product
        if hasattr(self.product_table, 'highlight_product'):
            self.product_table.highlight_product(product_name)

    def _handle_bulk_products_update(self, products, sort_column, sort_order, recent_products):
        """Handle update of multiple products (typically all products)"""
        # Update data model and table
        self.product_manager.set_products(products)
        self.product_table.update_table_data(products)

        # Apply sorting
        table = self.product_table.table
        table.setSortingEnabled(True)
        table.sortByColumn(sort_column, sort_order)

        # Highlight most recent product if available
        if recent_products:
            self._highlight_recent_product(products, recent_products[0])

        # Show products loaded message - but not during search operations
        if not self._search_in_progress:
            self.status_bar.show_message(
                self.translate(
                    'products_loaded',
                    f"Showing {len(products)} products"
                ).format(count=len(products)),
                "success"
            )

        # Adjust columns after load
        QTimer.singleShot(100, self._adjust_table_columns)

    def _highlight_recent_product(self, products, recent_id):
        """Find and highlight the most recently modified product"""
        product_name_to_highlight = None

        for product in products:
            try:
                p_id = str(product['parcode'] if isinstance(product, dict) else product[0])
                if str(p_id) == str(recent_id):
                    product_name_to_highlight = product['product_name'] if isinstance(product, dict) else product[2]
                    break
            except (IndexError, KeyError, TypeError):
                continue

        if product_name_to_highlight and hasattr(self.product_table, 'highlight_product'):
            QTimer.singleShot(200, lambda name=product_name_to_highlight:
            self.product_table.highlight_product(name))

    def toggle_selection_mode(self, checked):
        """Toggle product selection mode"""
        # Pass arguments YOUR SelectionHandler expects
        success, message = self.selection_handler.toggle_selection_mode(checked)

        # Error handling and status messages
        if not success:
            self.status_bar.show_message(message, "error")
            self.select_toggle.blockSignals(True)
            self.select_toggle.setChecked(False)
            self.select_toggle.blockSignals(False)
            # Apply theme if needed
            self.ui_handler.apply_theme()
        elif message:
            self.status_bar.show_message(message, "info")
        else:
            if self.status_bar:
                self.status_bar.clear()

        # Button state update
        if self.remove_btn:
            self.remove_btn.setEnabled(checked)
        if self.export_btn:
            self.export_btn.setEnabled(checked)

    def apply_filters(self, filters):
        """Apply filters to products"""
        filtered_products, message = self.filter_handler.filter_products(
            self.product_manager.get_products(),
            filters
        )
        self.product_table.update_table_data(filtered_products)
        self.status_bar.show_message(message, "info")

    def export_products(self):
        """Export products to CSV"""
        self.export_operation.export_to_csv(
            self.product_table,
            self.product_manager.get_products()
        )

    def load_products(self):
        """Load products from database"""
        self.status_bar.show_message(
            self.translate('loading_products', "Loading products..."),
            "info"
        )
        self.product_loader.load_products(self._is_closing)

        # Reset filter settings when loading all products
        self.filter_handler.reset_filters()


    def _highlight_product(self, product_id):
        """Highlight a product in the table"""
        if product_id is None:
            return

        try:
            highlighted = False
            if hasattr(self.product_table, 'highlight_row_by_id'):
                highlighted = self.product_table.highlight_row_by_id(str(product_id))

            if not highlighted and hasattr(self.product_table, 'highlight_product'):
                # Skip complex fallback, it's mentioned as optional in the comments
                pass

            loaded_message = self.translate(
                'products_loaded',
                f"Showing {len(self.product_manager.get_products())} products"
            ).format(count=len(self.product_manager.get_products()))

            self.status_bar.show_message(loaded_message, "info", 5000)
        except Exception as e:
            logger.error(f"Error highlighting product: {e}")

    def cancel_status_timer(self):
        """Cancel the status bar's auto-hide timer"""
        if hasattr(self.status_bar, 'cancel_auto_hide'):
            self.status_bar.cancel_auto_hide()

    def show_error(self, message):
        """Show error message"""
        if self._is_closing:
            return
        self.status_bar.show_message(message, "error")

    def highlight_product(self, search_text):
        """Highlight a product in the table"""
        if not self.product_table or not hasattr(self.product_table, 'highlight_product'):
            return False
        return self.product_table.highlight_product(search_text)

    def update_translations(self):
        """Update all translations in the UI"""
        self.ui_handler.update_translations()

    def translate(self, key, default=None):
        """Safely translate a key with fallback"""
        try:
            if hasattr(self.translator, 'has_translation'):
                # If there's a method to check translations
                if self.translator.has_translation(key):
                    return self.translator.t(key)
                else:
                    if default:
                        return default
                    return self.translator.t(key)  # Fall back to key itself
            else:
                # Just try to get the translation directly
                result = self.translator.t(key)
                if result == key and default:  # Many translators return the key if not found
                    return default
                return result
        except Exception as e:
            logger.error(f"Translation error for key '{key}': {e}")
            return default if default else key

    def _handle_add_button_click(self):
        """Handle add button click with proper translation"""
        # Get properly translated text
        add_preparing_text = self.translate('add:preparing', "Opening add product form...")

        # First show status message
        self.show_status_message(
            add_preparing_text,
            "add",
            priority=85
        )

        # Then show the dialog
        self.add_operation.show_add_dialog()


    def _handle_status_bar_state_change(self, is_expanded):
        """Handle status bar expansion/collapse by updating layouts"""
        if not is_expanded:  # Only need to adjust when collapsing
            # First immediate adjustment
            if hasattr(self, 'product_table') and self.product_table:
                self.product_table.adjust_column_widths()

            # Second adjustment after animation completes
            animation_duration = getattr(self.status_bar, 'animation_duration', 300)
            QTimer.singleShot(animation_duration + 50, self._delayed_column_adjustment)

    def _delayed_column_adjustment(self):
        """Adjust columns again after animation should be complete"""
        if hasattr(self, 'product_table') and self.product_table:
            self.product_table.adjust_column_widths()

    def _adjust_table_columns(self):
        """Adjust table column widths after status bar animation completes"""
        if hasattr(self, 'product_table') and self.product_table:
            QTimer.singleShot(50, self.product_table.adjust_column_widths)

    def resizeEvent(self, event):
        """Handle resize events for the widget"""
        super().resizeEvent(event)

        # Update column widths when widget resizes
        if hasattr(self, 'product_table') and self.product_table:
            # Use delayed execution to ensure layout is settled
            QTimer.singleShot(0, self.product_table.adjust_column_widths)

    def handle_theme_change(self):
        """Handle theme changes from the application level"""
        if hasattr(self, 'ui_handler'):
            # Temporarily disable signal handling to prevent side effects
            self._updating_ui = True
            try:
                # Force a complete theme refresh
                self.ui_handler.apply_theme()

                # Ensure all styling is updated
                self.update()

                # Process events to ensure theme is applied
                from PyQt5.QtCore import QCoreApplication
                QCoreApplication.processEvents()
            finally:
                self._updating_ui = False

    def print_products(self):
        """Print products table with integrated preview"""
        self.print_operation.print_table(
            self.product_table,
            self.product_manager.get_products(),
            self.select_toggle.isChecked()
        )

    def on_barcode_scanned(self, barcode, format=None):
        """Handle scanned barcode by updating search input and triggering search"""
        if not barcode:
            return

        try:
            # Set the barcode in the search input
            self.search_input.setText(barcode)

            # Cancel any active search timer
            if self.search_timer.isActive():
                self.search_timer.stop()

            # Immediately perform the search instead of waiting for timer
            self.on_search(barcode)

            # Show feedback message with proper translation
            message = self.translate(
                'barcode:barcode_scanned',
                f"Barcode scanned: {barcode}"
            ).format(barcode=barcode)

            # Add format if available
            if format and format != "Unknown":
                message += f" ({format})"

            self.status_bar.show_message(message, "success", 3000)

            # Focus on the product table after search
            if self.product_table and hasattr(self.product_table, 'table'):
                self.product_table.table.setFocus()
        except Exception as e:
            logger.error(f"Error processing barcode scan: {e}")
            # Error message with translation
            error_message = self.translate(
                'barcode:barcode_scan_error',
                "Error processing barcode"
            )

            self.status_bar.show_message(error_message, "error")

    # Add these new methods to your ProductsWidget class

    # UPDATE the _reset_to_all_products method
    def _reset_to_all_products(self):
        """Reset the view to show all products when search is cleared"""
        # Ensure search flags are correctly set
        self._is_search_refresh = True
        self._search_in_progress = True

        # First reset all cell formatting BEFORE updating the table data
        if hasattr(self.product_table, '_reset_cell_formatting'):
            self.product_table._reset_cell_formatting()

        # Update the table with all products
        self.product_table.update_table_data(self.product_manager.get_products())

        # After table update, ensure all styling is reset
        QTimer.singleShot(50, self._ensure_highlights_cleared)

        # Clear search state
        if hasattr(self.search_handler, 'clear_last_search'):
            self.search_handler.clear_last_search()

        # Show standard all products message with priority
        count = len(self.product_manager.get_products())
        if count > 0:
            self.show_status_message(
                self.translate('products_loaded', f"Showing all {count} products").format(count=count),
                "info",
                priority=30  # Lower priority
            )
        else:
            if hasattr(self.status_bar, 'clear'):
                self.status_bar.clear()

    # UPDATE the on_cell_changed method


    def _on_search_input_changed(self, text):
        """Handle search input changes with delay to improve performance"""
        # Reset timer if already running
        if self.search_timer.isActive():
            self.search_timer.stop()

        search_text = text.strip()

        # Skip if already updating UI
        if hasattr(self, '_updating_ui') and self._updating_ui:
            return

        # Mark as search operation
        self._is_search_refresh = True
        # Also set search in progress flag
        self._search_in_progress = True

        if search_text:
            # Start timer for non-empty searches
            self.search_timer.start(250)
        else:
            # For empty search text, immediately reset to show all products
            try:
                self._updating_ui = True
                self._reset_to_all_products()
            finally:
                self._updating_ui = False
                # Use a timer to reset the flags after all operations complete
                QTimer.singleShot(300, self._reset_search_flags)

    def on_search(self, text):
        """
        Perform priority-based search with enhanced user feedback.
        Search results are sorted by relevance rather than just inclusion.
        """
        # Initialize the variable before the try block to avoid reference errors
        was_already_updating = False

        # Skip if already in update mode
        if hasattr(self, '_updating_ui') and self._updating_ui and not self._search_in_progress:
            return

        try:
            # Set state flags
            was_already_updating = hasattr(self, '_updating_ui') and self._updating_ui
            if not was_already_updating:
                self._updating_ui = True

            self._is_search_refresh = True  # Mark as search operation
            self._search_in_progress = True
            search_text = text.strip()

            # Don't search if the text is too short (unless it's a number, which could be a part ID)
            if len(search_text) < 2 and not search_text.isdigit():
                # REMOVED: Don't show "search term too short" message
                return

            # Detect search patterns
            is_part_code_search = (
                    search_text.isdigit() or
                    (search_text[0].upper() == 'P' and len(search_text) > 1) or
                    any(c.isalpha() and c.isupper() for c in search_text)
            )
            is_multi_word = ' ' in search_text and len(search_text.split()) > 1
            should_refresh = is_part_code_search or len(search_text) > 3 or is_multi_word

            # Refresh data for important searches
            if should_refresh and hasattr(self.product_loader, 'load_products_silent'):
                try:
                    # Display searching indicator with high priority
                    self.show_status_message(
                        self.translate('searching', "Searching..."),
                        "info",
                        priority=70  # Higher priority for search operations
                    )
                    # Refresh products from database for important searches
                    self.product_loader.load_products_silent()
                except Exception as e:
                    logger.error(f"Error refreshing products for search: {e}")

            # Filter products using priority-based search
            filtered_products, _ = self.search_handler.search_products(
                self.product_manager.get_products(),
                search_text
            )

            # Update table with filtered results
            with SignalBlocker(self.product_table.table):
                self.product_table.update_table_data(filtered_products)

                # Highlight matching text
                if search_text and hasattr(self.product_table, 'highlight_matching_text'):
                    self.product_table.highlight_matching_text(search_text)

            # Always show search results message
            if filtered_products:
                self.show_status_message(
                    self.translate(
                        'search_results_found',
                        f"Found {len(filtered_products)} results for '{search_text}'"
                    ).format(count=len(filtered_products), term=search_text),
                    "info",
                    priority=50  # Medium priority
                )
            else:
                self.show_status_message(
                    self.translate(
                        'no_search_results',
                        f"No results found for '{search_text}'"
                    ).format(term=search_text),
                    "info",
                    priority=50  # Medium priority
                )

            # Special handling for exact part code matches
            if is_part_code_search and len(filtered_products) == 1:
                self._highlight_exact_match(filtered_products[0], search_text)

        except Exception as e:
            logger.error(f"Error during search: {e}")
            self.show_status_message(
                self.translate('search_error', "Error during search"),
                "error",
                priority=100  # High priority for errors
            )
        finally:
            # Only reset updating flag if we set it
            if not was_already_updating:
                self._updating_ui = False
            # Note: _is_search_refresh is reset after products are loaded

    def _connect_signals(self):
        """Connect all signals for the widget with enhanced status bar feedback"""
        # Action buttons with status feedback
        self.add_btn.clicked.connect(self._handle_add_button_click)

        self.select_toggle.toggled.connect(self.toggle_selection_mode)

        self.remove_btn.clicked.connect(lambda: (
            self.show_status_message(
                self.translate('delete:preparing', "Preparing to delete products..."),
                "delete",
                priority=85
            ),
            self.delete_selected_products()
        ))

        self.filter_btn.clicked.connect(lambda: (
            self.show_status_message(
                self.translate('filter:preparing', "Opening filter options..."),
                "filter",
                priority=75
            ),
            self.show_filter_dialog()
        ))

        self.clear_filter_btn.clicked.connect(lambda: self.filter_handler.reset_filters())

        self.export_btn.clicked.connect(lambda: (
            self.show_status_message(
                self.translate('export:preparing', "Preparing to export products..."),
                "export",
                priority=70
            ),
            self.export_products()
        ))

        self.print_btn.clicked.connect(lambda: (
            self.show_status_message(
                self.translate('print:preparing', "Preparing print options..."),
                "print",
                priority=75
            ),
            self.print_products()
        ))

        self.refresh_btn.clicked.connect(self.load_products)

        # Connect barcode scanner signal with status feedback
        if hasattr(self, 'barcode_scanner'):
            self.barcode_scanner.barcode_scanned.connect(self.on_barcode_scanned)

        # Search related connections
        self.search_input.textChanged.connect(self._on_search_input_changed)
        self.product_table.cellChanged.connect(self.on_cell_changed)

        # Status bar related
        self.select_toggle.clicked.connect(self.cancel_status_timer)
        self.refresh_btn.clicked.connect(self.cancel_status_timer)

        # Product loader connections
        self.product_loader.products_loaded.connect(self.handle_loaded_products)
        self.product_loader.error_occurred.connect(self.show_error)

        # Connect delete operation signal if available
        if hasattr(self.delete_operation, 'products_deleted'):
            self.delete_operation.products_deleted.connect(self.on_products_deleted)

        logger.debug("All signals connected")

    # Add this utility method for showing status messages
    def show_status_message(self, message, type="info", duration=None, priority=None):
        """
        Centralized method to show status messages with optional priority.
        This uses either the enhanced status bar or falls back to the standard one.
        """
        if not hasattr(self, 'status_bar') or self.status_bar is None:
            return

        # Check if we're closing to avoid showing messages during shutdown
        if hasattr(self, '_is_closing') and self._is_closing:
            return

        # Show the message with priority if supported
        try:
            if hasattr(self.status_bar, 'show_action_feedback') and type in [
                "barcode", "add", "filter", "print", "export", "delete", "select"
            ]:
                # Use the new action-specific feedback
                self.status_bar.show_action_feedback(type, message)
            elif hasattr(self.status_bar, 'show_message'):
                # Check if the status bar supports priority
                if 'priority' in inspect.signature(self.status_bar.show_message).parameters:
                    self.status_bar.show_message(message, type, duration, priority)
                else:
                    # Fall back to standard show_message
                    self.status_bar.show_message(message, type, duration)
        except Exception as e:
            logger.error(f"Error showing status message: {e}")

    # These are the updated method implementations that integrate with the enhanced StatusBar
    # to keep it open until dialogs close

    # First, let's modify the show_barcode_scanner method
    def show_barcode_scanner(self):
        """Show the barcode scanner dialog with proper status bar integration"""
        try:
            # Start dialog action in status bar
            if hasattr(self.status_bar, 'start_dialog_action'):
                self.status_bar.start_dialog_action(
                    "barcode",
                    self.translate('barcode:initiating_scan', "Preparing barcode scanner...")
                )
            else:
                # Fallback for older status bar
                self.status_bar.show_message(
                    self.translate('barcode:initiating_scan', "Preparing barcode scanner..."),
                    "barcode"
                )

            # Try to import the dialog class
            try:
                from widgets.products.components.barcode_scanner_button import ScanningDialog
            except ImportError:
                try:
                    from .components.barcode_scanner_button import ScanningDialog
                except ImportError:
                    # Final fallback attempt
                    try:
                        from components.barcode_scanner_button import ScanningDialog
                    except ImportError:
                        # Show error in status bar and end dialog action
                        logger.error("Barcode scanning module not available")
                        if hasattr(self.status_bar, 'end_dialog_action'):
                            self.status_bar.end_dialog_action(
                                self.translate('barcode:scan_error', "Barcode scanning module not available")
                            )
                        else:
                            self.status_bar.show_message(
                                self.translate('barcode:scan_error', "Barcode scanning module not available"),
                                "error"
                            )
                        return

            # Create and show the dialog
            dialog = ScanningDialog(self, self.translator)

            # Connect the signal
            dialog.barcode_scanned.connect(
                lambda barcode: self.on_barcode_scanned(barcode, "Scanned")
            )

            # Show the dialog as modal
            result = dialog.exec_()

            # End dialog action in status bar with appropriate message
            if hasattr(self.status_bar, 'end_dialog_action'):
                if result == QDialog.Accepted:
                    self.status_bar.end_dialog_action(
                        self.translate('barcode:scan_complete', "Barcode scanning completed")
                    )
                else:
                    self.status_bar.end_dialog_action(
                        self.translate('barcode:scan_cancelled', "Barcode scanning cancelled")
                    )
            else:
                # Fallback for older status bar
                self.status_bar.show_message(
                    self.translate('barcode:scan_complete', "Barcode scanning completed"),
                    "success" if result == QDialog.Accepted else "info"
                )

        except Exception as e:
            logger.error(f"Error showing barcode scanner: {e}")
            # End dialog action with error message
            if hasattr(self.status_bar, 'end_dialog_action'):
                self.status_bar.end_dialog_action(
                    self.translate('barcode:scan_error', "Error showing barcode scanner")
                )
            else:
                self.status_bar.show_message(
                    self.translate('barcode:scan_error', "Error showing barcode scanner"),
                    "error"
                )

    def handle_filter_button_press(self):
        """Handles filter button press: translates message and calls start_dialog_action."""
        try:
            filter_key = "filter:preparing"
            translated_message = self.translate(filter_key, "Opening filter options...")  # Use translate helper

            # Call start_dialog_action directly
            if hasattr(self.status_bar, 'start_dialog_action'):
                self.status_bar.start_dialog_action("filter", translated_message)
            else:  # Fallback
                self.status_bar.show_message(translated_message, "filter")

            # Now show the dialog
            self.show_filter_dialog()
        except Exception as e:
            logger.error(f"Error handling filter button press: {e}")
            if hasattr(self.status_bar, 'end_dialog_action'):
                self.status_bar.end_dialog_action(self.translate('dialog_error', "Error opening dialog"))

    # Now update the show_filter_dialog method
    def show_filter_dialog(self):
        """Show filter dialog with immediate collapse on cancel"""
        # Start dialog action in status bar
        if hasattr(self.status_bar, 'start_dialog_action'):
            self.status_bar.start_dialog_action(
                "filter",
                self.translate('filter:preparing', "Opening filter options...")
            )
        else:
            # Fallback for older status bar
            self.status_bar.show_message(
                self.translate('filter:preparing', "Opening filter options..."),
                "filter"
            )

        # Create the dialog
        dialog = FilterDialog(self.translator, self)
        dialog.initialize_from_saved_settings(
            self.filter_handler.get_last_filter_settings())

        # Show the dialog
        result = dialog.exec_()

        # Process result
        if result == QDialog.Accepted:
            filters = dialog.get_filters()
            self.filter_handler.save_filter_settings(filters)
            self.apply_filters(filters)

            # End dialog action with success message
            if hasattr(self.status_bar, 'end_dialog_action'):
                filter_count = sum(1 for value in filters.values() if value)
                if filter_count > 0:
                    self.status_bar.end_dialog_action(
                        self.translate('filter:applied', f"Applied {filter_count} filters")
                    )
                else:
                    self.status_bar.end_dialog_action(
                        self.translate('filter:no_filters', "No filters applied")
                    )
        else:
            # User cancelled the dialog - IMMEDIATELY collapse with NO message
            if hasattr(self.status_bar, 'force_collapse'):
                self.status_bar.force_collapse()  # Most direct approach
            elif hasattr(self.status_bar, 'end_dialog_action'):
                self.status_bar.end_dialog_action("")  # Empty string to avoid showing message
            else:
                self.status_bar.clear()  # Fallback to simple clear

    # Let's modify the add operation to integrate with the enhanced status bar
    def _handle_dialog_result(self, dialog, result):
        """Processes the data if the dialog was accepted and updates status bar."""
        if result == QDialog.Accepted:
            try:
                data = dialog.get_data()
                if data:
                    # Check if we have a parcode/barcode and log it
                    if 'parcode' in data:
                        logger.debug(f"Dialog returned parcode: {data['parcode']}")
                    elif 'barcode' in data:
                        # If it's still called 'barcode' in the dialog, rename it to 'parcode'
                        data['parcode'] = data.pop('barcode')
                        logger.debug(f"Renamed barcode to parcode: {data['parcode']}")

                    # Initiate the process of adding/updating the product
                    product_id = self.process_add_product(data)

                    # Get translations using parent's translate method if available
                    success_msg = "Product added successfully"
                    fail_msg = "Failed to add product"

                    if hasattr(self.parent, 'translate'):
                        success_msg = self.parent.translate('product_added_success', "Product added successfully")
                        fail_msg = self.parent.translate('product_add_failed', "Failed to add product")
                    elif hasattr(self.translator, 't'):
                        success_msg_translated = self.translator.t('product_added_success')
                        if success_msg_translated != 'product_added_success':
                            success_msg = success_msg_translated

                        fail_msg_translated = self.translator.t('product_add_failed')
                        if fail_msg_translated != 'product_add_failed':
                            fail_msg = fail_msg_translated

                    # End dialog action with appropriate message
                    if hasattr(self.parent.status_bar, 'end_dialog_action'):
                        if product_id:
                            self.parent.status_bar.end_dialog_action(success_msg)
                        else:
                            self.parent.status_bar.end_dialog_action(fail_msg)
                else:
                    # Get error message translation
                    error_msg = "Error retrieving product data"
                    if hasattr(self.parent, 'translate'):
                        error_msg = self.parent.translate('data_error', "Error retrieving product data")
                    elif hasattr(self.translator, 't'):
                        error_msg_translated = self.translator.t('data_error')
                        if error_msg_translated != 'data_error':
                            error_msg = error_msg_translated

                    if hasattr(self.parent.status_bar, 'end_dialog_action'):
                        self.parent.status_bar.end_dialog_action(error_msg)
                    else:
                        # Fallback for older status bar
                        if self.status_bar:
                            self.status_bar.show_message(error_msg, "warning", 5000)
            except Exception as e:
                logger.error(f"Error handling dialog result: {e}")
                # Get error message translation
                error_msg = "Error adding product"
                data_error_msg = "Error processing product data"

                if hasattr(self.parent, 'translate'):
                    error_msg = self.parent.translate('add_product_error', "Error adding product")
                    data_error_msg = self.parent.translate('data_error', "Error processing product data")
                elif hasattr(self.translator, 't'):
                    error_translated = self.translator.t('add_product_error')
                    if error_translated != 'add_product_error':
                        error_msg = error_translated

                    data_error_translated = self.translator.t('data_error')
                    if data_error_translated != 'data_error':
                        data_error_msg = data_error_translated

                # End dialog action with error message
                if hasattr(self.parent.status_bar, 'end_dialog_action'):
                    self.parent.status_bar.end_dialog_action(error_msg)
                else:
                    # Fallback for older status bar
                    if self.status_bar:
                        self.status_bar.show_message(data_error_msg, "error")
        else:
            # Handle dialog cancellation/rejection
            # Get cancel message translation
            cancel_msg = "Add product cancelled"
            if hasattr(self.parent, 'translate'):
                cancel_msg = self.parent.translate('add_cancelled', "Add product cancelled")
            elif hasattr(self.translator, 't'):
                cancel_translated = self.translator.t('add_cancelled')
                if cancel_translated != 'add_cancelled':
                    cancel_msg = cancel_translated

            # End dialog action in status bar
            if hasattr(self.parent.status_bar, 'end_dialog_action'):
                self.parent.status_bar.end_dialog_action(cancel_msg)
            elif self.status_bar:
                self.status_bar.clear()

    # Update the AddOperation.show_add_dialog method
    def show_add_dialog(self):
        """Creates and shows the 'Add Product' dialog with status bar integration."""
        try:
            # Get the proper translation directly from the parent widget that has the translator
            add_preparing_text = "Opening add product form..."
            if hasattr(self.parent, 'translate'):
                # Use parent's translate method which has proper error handling
                add_preparing_text = self.parent.translate('add:preparing', "Opening add product form...")
            elif hasattr(self.translator, 't'):
                # Fallback to direct translator usage
                add_preparing_text = self.translator.t('add:preparing')
                if add_preparing_text == 'add:preparing':  # If translation failed and returned the key
                    add_preparing_text = "Opening add product form..."

            # Start dialog action in parent's status bar
            if hasattr(self.parent, 'status_bar') and hasattr(self.parent.status_bar, 'start_dialog_action'):
                self.parent.status_bar.start_dialog_action(
                    "add",
                    add_preparing_text
                )
            else:
                # Fallback for older status bar
                if self.status_bar:
                    self.status_bar.show_message(
                        add_preparing_text,
                        "add"
                    )

            # Use the enhanced dialog with new fields
            dialog = AddProductDialog(self.translator, self.parent)

            # Connect the finished signal to handle the result *after* the dialog closes
            # The finished signal emits an integer result code (Accepted or Rejected)
            dialog.finished.connect(lambda result: self._handle_dialog_result(dialog, result))

            # Use open() for a non-modal dialog or exec_() for a modal one
            dialog.open()
        except Exception as e:
            logger.error(f"Error showing add dialog: {e}")
            # Get error message translation
            error_msg = "Error showing dialog"
            if hasattr(self.parent, 'translate'):
                error_msg = self.parent.translate('dialog_error', "Error showing dialog")
            elif hasattr(self.translator, 't'):
                error_msg_translated = self.translator.t('dialog_error')
                if error_msg_translated != 'dialog_error':
                    error_msg = error_msg_translated

            # End dialog action with error
            if hasattr(self.parent, 'status_bar') and hasattr(self.parent.status_bar, 'end_dialog_action'):
                self.parent.status_bar.end_dialog_action(error_msg)
            else:
                # Fallback for older status bar
                if self.status_bar:
                    self.status_bar.show_message(error_msg, "error")

    # Update the delete_selected_products method
    def delete_selected_products(self):
        """Delete selected products with status bar integration"""
        if not self.select_toggle.isChecked():
            self.status_bar.show_message(
                self.translate('select_mode_required', "Selection mode must be enabled to delete items"),
                "warning"
            )
            return

        # Start dialog action in status bar
        if hasattr(self.status_bar, 'start_dialog_action'):
            self.status_bar.start_dialog_action(
                "delete",
                self.translate('delete:preparing', "Preparing to delete products...")
            )
        else:
            # Fallback for older status bar
            self.status_bar.show_message(
                self.translate('delete:preparing', "Preparing to delete products..."),
                "delete"
            )

        # Get selected rows data
        product_details = self.product_table.get_selected_rows_data()
        if not product_details:
            # End dialog action with appropriate message
            if hasattr(self.status_bar, 'end_dialog_action'):
                self.status_bar.end_dialog_action(
                    self.translate('no_rows_selected', "No products selected for deletion")
                )
            else:
                self.status_bar.show_message(
                    self.translate('no_rows_selected', "No products selected for deletion"),
                    "warning"
                )
            return

        # Create the confirmation dialog
        dialog = DeleteConfirmationDialog(
            products=product_details,
            translator=self.translator,
            parent=self
        )

        # Show the dialog
        result = dialog.exec_()

        if result == QDialog.Accepted:
            # User confirmed deletion - proceed with deletion operation
            # This will be handled by the DeleteOperation class which will
            # show appropriate success messages

            # First fetch all products to find database IDs matching the parcodes
            all_products = self.db.get_all_parts()

            # Map parcodes to database IDs
            db_id_map = {}
            for product in all_products:
                if isinstance(product, dict):
                    if 'parcode' in product and 'id' in product:
                        parcode = str(product['parcode'])
                        db_id_map[parcode] = product['id']
                else:
                    # Tuple format - assuming parcode is at position 15 and id at position 0
                    if len(product) > 15:
                        parcode = str(product[15])
                        db_id = product[0]
                        db_id_map[parcode] = db_id
                    # Try other potential formats
                    elif hasattr(product, 'parcode') and hasattr(product, 'id'):
                        parcode = str(product.parcode)
                        db_id_map[parcode] = product.id

            # Convert selected parcodes to database IDs for deletion
            products_to_delete = []
            for parcode, name in product_details:
                if str(parcode) in db_id_map:
                    products_to_delete.append((db_id_map[str(parcode)], name))

            # Perform the deletion with database IDs
            deleted_ids = self.delete_operation._perform_deletion(products_to_delete)

            if deleted_ids:
                # End dialog action with success message
                if hasattr(self.status_bar, 'end_dialog_action'):
                    self.status_bar.end_dialog_action(
                        self.translate('items_deleted', "Successfully deleted {count} items").format(
                            count=len(deleted_ids))
                    )
                else:
                    self.status_bar.show_message(
                        self.translate('items_deleted', "Successfully deleted {count} items").format(
                            count=len(deleted_ids)),
                        "success"
                    )

                # Signal parent to reload products after a delay
                QTimer.singleShot(1500, lambda: self.on_products_deleted(deleted_ids))
            else:
                # End dialog action with error message
                if hasattr(self.status_bar, 'end_dialog_action'):
                    self.status_bar.end_dialog_action(
                        self.translate('delete_failed', "Failed to delete products")
                    )
                else:
                    self.status_bar.show_message(
                        self.translate('delete_failed', "Failed to delete products"),
                        "error"
                    )
        else:
            # User cancelled deletion
            # End dialog action with cancelled message
            if hasattr(self.status_bar, 'end_dialog_action'):
                self.status_bar.end_dialog_action(
                    self.translate('delete_cancelled', "Delete operation cancelled")
                )
            else:
                self.status_bar.clear()  # Just clear the status bar

    def connect_to_sync_manager(self):
        """Connect to the database sync manager to receive change notifications."""
        try:
            # Import here to avoid circular imports
            from utils.database_sync import db_sync_manager

            # Register with sync manager
            db_sync_manager.register_listener(self)

            # Connect signals to refresh methods
            db_sync_manager.product_added.connect(self._handle_product_added)
            db_sync_manager.product_updated.connect(self._handle_product_updated)
            db_sync_manager.product_deleted.connect(self._handle_product_deleted)
            db_sync_manager.products_loaded.connect(self._handle_products_loaded)

            logger.info("ProductsWidget connected to database sync manager")
        except Exception as e:
            logger.error(f"Error connecting to sync manager: {e}")

    def disconnect_from_sync_manager(self):
        """Disconnect from the database sync manager."""
        try:
            from utils.database_sync import db_sync_manager

            # Disconnect signals
            db_sync_manager.product_added.disconnect(self._handle_product_added)
            db_sync_manager.product_updated.disconnect(self._handle_product_updated)
            db_sync_manager.product_deleted.disconnect(self._handle_product_deleted)
            db_sync_manager.products_loaded.disconnect(self._handle_products_loaded)

            # Unregister from sync manager
            db_sync_manager.unregister_listener(self)

            logger.info("ProductsWidget disconnected from database sync manager")
        except Exception as e:
            logger.error(f"Error disconnecting from sync manager: {e}")

    def _handle_product_added(self, product_data):
        """Handle notification that a product was added in another widget."""
        logger.debug(f"ProductsWidget notified of product addition: {product_data}")
        if not hasattr(self, '_processing_sync_event'):
            self._processing_sync_event = True
            try:
                # Refresh products from database
                self.load_products()

                # Show feedback in status bar
                self.show_status_message(
                    self.translate('product_added', "Product added in another view, refreshed"),
                    "info"
                )
            finally:
                self._processing_sync_event = False

    def _handle_product_updated(self, product_data):
        """Handle notification that a product was updated in another widget."""
        logger.debug(f"ProductsWidget notified of product update: {product_data}")
        if not hasattr(self, '_processing_sync_event'):
            self._processing_sync_event = True
            try:
                # Refresh products from database
                self.load_products()

                # Show feedback in status bar
                self.show_status_message(
                    self.translate('product_updated', "Product updated in another view, refreshed"),
                    "info"
                )
            finally:
                self._processing_sync_event = False

    def _handle_product_deleted(self, product_id):
        """Handle notification that a product was deleted in another widget."""
        logger.debug(f"ProductsWidget notified of product deletion: {product_id}")
        if not hasattr(self, '_processing_sync_event'):
            self._processing_sync_event = True
            try:
                # Refresh products from database
                self.load_products()

                # Show feedback in status bar
                self.show_status_message(
                    self.translate('product_deleted', "Product deleted in another view, refreshed"),
                    "info"
                )
            finally:
                self._processing_sync_event = False

    def _handle_products_loaded(self):
        """Handle notification that products were loaded in another widget."""
        logger.debug("ProductsWidget notified of products loaded event")
        if not hasattr(self, '_processing_sync_event'):
            self._processing_sync_event = True
            try:
                # Refresh products from database
                self.load_products()
            finally:
                self._processing_sync_event = False

    # Add this to the __init__ method at the end after everything is initialized
    # self.connect_to_sync_manager()

