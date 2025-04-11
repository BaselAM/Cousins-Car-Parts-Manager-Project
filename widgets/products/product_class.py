# products_class.py (Enhanced Version)
import inspect

from PyQt5.QtWidgets import QWidget, QDialog
from PyQt5.QtCore import QTimer, pyqtSlot, QEvent, Qt

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
from .dialogs import FilterDialog


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

    def _setup_barcode_scanner(self):
        """Set up the barcode scanner button and add to UI"""
        self.barcode_scanner = BarcodeScannerButton(self, self.translator)

        # Find the parent layout containing the existing buttons
        button_container = self.add_btn.parentWidget()
        if button_container and button_container.layout():
            button_layout = button_container.layout()

            # Find add_btn position
            add_btn_index = -1
            for i in range(button_layout.count()):
                if button_layout.itemAt(i).widget() == self.add_btn:
                    add_btn_index = i
                    break

            # Insert after the add button
            if add_btn_index >= 0:
                button_layout.insertWidget(add_btn_index + 1, self.barcode_scanner)
            else:
                # Fallback: just add to the end
                button_layout.addWidget(self.barcode_scanner)

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
            print(f"Error ensuring highlights cleared: {e}")


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
            print(f"Error highlighting exact match: {e}")


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

            print(f"Load error: {e}")
            import traceback
            print(traceback.format_exc())
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

    def show_filter_dialog(self):
        """Show filter dialog"""
        dialog = FilterDialog(self.translator, self)
        dialog.initialize_from_saved_settings(
            self.filter_handler.get_last_filter_settings())

        if dialog.exec_() == QDialog.Accepted:
            filters = dialog.get_filters()
            self.filter_handler.save_filter_settings(filters)
            self.apply_filters(filters)

    def apply_filters(self, filters):
        """Apply filters to products"""
        filtered_products, message = self.filter_handler.filter_products(
            self.product_manager.get_products(),
            filters
        )
        self.product_table.update_table_data(filtered_products)
        self.status_bar.show_message(message, "info")

    def delete_selected_products(self):
        """Delete selected products"""
        self.delete_operation.delete_selected_products(
            self.select_toggle.isChecked(),
            self.product_table
        )

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

    def on_product_added(self, product_id):
        """Called after a product is added or updated"""
        QTimer.singleShot(100, lambda: self._highlight_product(product_id))

    def on_products_deleted(self, deleted_ids):
        """Called after products are deleted"""
        self.product_manager.remove_products_by_ids(deleted_ids)
        self.load_products()

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
            print(f"Error highlighting product: {e}")

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
            print(f"Translation error for key '{key}': {e}")
            return default if default else key

    def closeEvent(self, event):
        """Handle widget close event"""
        try:
            self._is_closing = True
            if hasattr(self.product_loader, 'cleanup'):
                self.product_loader.cleanup()
            self.product_manager.clear()
        except Exception as e:
            print(f"Cleanup error: {e}")
        event.accept()

    def _connect_signals(self):
        """Connect all signals for the widget"""
        self.add_btn.clicked.connect(self.add_operation.show_add_dialog)
        self.select_toggle.toggled.connect(self.toggle_selection_mode)
        self.remove_btn.clicked.connect(self.delete_selected_products)
        self.filter_btn.clicked.connect(self.show_filter_dialog)
        self.clear_filter_btn.clicked.connect(lambda: self.filter_handler.reset_filters())
        self.export_btn.clicked.connect(self.export_products)
        self.print_btn.clicked.connect(self.print_products)
        self.refresh_btn.clicked.connect(self.load_products)

        # Connect barcode scanner signal
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

    def on_barcode_scanned(self, barcode, format):
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

            self.status_bar.show_message(message, "success", 3000)

            # Focus on the product table after search
            if self.product_table and hasattr(self.product_table, 'table'):
                self.product_table.table.setFocus()
        except Exception as e:
            print(f"Error handling barcode scan: {e}")

            # Error message with translation
            error_message = self.translate(
                'barcode:barcode_scan_error',
                "Error processing barcode"
            )

            self.status_bar.show_message(error_message, "error")

    # Add these new methods to your ProductsWidget class

    def show_status_message(self, message, type="info", duration=None, priority=None):
        """
        Centralized method to show status messages with optional priority.
        Use this instead of directly calling status_bar.show_message.
        """
        if not hasattr(self, 'status_bar') or self.status_bar is None:
            return

        # Check if we're closing to avoid showing messages during shutdown
        if hasattr(self, '_is_closing') and self._is_closing:
            return

        # Show the message with priority if supported
        try:
            if hasattr(self.status_bar, 'show_message'):
                # Check if the status bar supports priority
                if 'priority' in inspect.signature(self.status_bar.show_message).parameters:
                    self.status_bar.show_message(message, type, duration, priority)
                else:
                    # Fall back to standard show_message
                    self.status_bar.show_message(message, type, duration)
        except Exception as e:
            print(f"Error showing status message: {e}")

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

    # UPDATE the on_search method
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
                self.show_status_message(
                    self.translate('search_too_short', "Search term is too short"),
                    "info",
                    priority=20  # Low priority
                )
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
                    print(f"Error refreshing search data: {e}")

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
            print(f"Search error: {e}")
            import traceback
            print(traceback.format_exc())
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

    # UPDATE the _on_search_input_changed method
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


    # UPDATE the on_cell_changed method
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
        except Exception as e:
            print(f"Cell change error: {e}")
        finally:
            self._updating_cell = False

    # Make sure to add this import at the top of your file if it's not already there
    import inspect  # For checking method signatures
