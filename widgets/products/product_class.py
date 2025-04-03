# products_class.py (Enhanced Version)

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
    def __init__(self, translator, db, parent=None):
        super().__init__(parent)
        self._is_closing = False
        self.translator = translator
        self.db = db

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

        # Connect to status bar state changes
        self.status_bar.state_changed.connect(self._handle_status_bar_state_change)

        # Initialize search timer
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

    def toggle_selection_mode(self, checked):
        """Toggle product selection mode"""
        # *** Pass arguments YOUR SelectionHandler expects ***
        success, message = self.selection_handler.toggle_selection_mode(checked)

        # Original error handling and status messages
        if not success:
            self.status_bar.show_message(message, "error")
            self.select_toggle.blockSignals(True)
            self.select_toggle.setChecked(False)
            self.select_toggle.blockSignals(False)
            # Original code called apply_theme here, keep if needed by your styling logic
            self.ui_handler.apply_theme()
        elif message:
            self.status_bar.show_message(message, "info")
        else:
            # Use Optional Chaining or check if not None if status_bar can be None
            if self.status_bar: self.status_bar.clear()

        # Original button state update logic (remains unchanged)
        # Note: This logic might not be fully robust as it doesn't react to
        # selection changes within the mode, but keeping it as per original.
        if self.remove_btn:
            self.remove_btn.setEnabled(checked)
        if self.export_btn:
            self.export_btn.setEnabled(checked)

    def on_cell_changed(self, row, column):
        """Handle cell value changes"""
        # Comprehensive guard conditions
        if (hasattr(self, '_updating_ui') and self._updating_ui or
                hasattr(self, '_updating_cell') and self._updating_cell or
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
                self.status_bar.show_message(message, "success", 3000)
        except Exception as e:
            print(f"Cell change error: {e}")
        finally:
            self._updating_cell = False

    def show_filter_dialog(self):
        """Show filter dialog"""
        # Keep original implementation
        dialog = FilterDialog(self.translator, self)
        dialog.initialize_from_saved_settings(
            self.filter_handler.get_last_filter_settings())

        if dialog.exec_() == QDialog.Accepted:
            filters = dialog.get_filters()
            self.filter_handler.save_filter_settings(filters)
            self.apply_filters(filters)

    def apply_filters(self, filters):
        """Apply filters to products"""
        # Keep original implementation
        filtered_products, message = self.filter_handler.filter_products(
            self.product_manager.get_products(),
            filters
        )
        self.product_table.update_table_data(filtered_products)
        self.status_bar.show_message(message, "info")
        # NOTE: This original version does NOT update the filter button style

    def delete_selected_products(self):
        """Delete selected products"""
        # Keep original implementation (Verify DeleteOperation arguments)
        self.delete_operation.delete_selected_products(
            self.select_toggle.isChecked(),
            self.product_table
        )

    def export_products(self):
        """Export products to CSV"""
        # Keep original implementation (Verify ExportOperation arguments)
        self.export_operation.export_to_csv(
            self.product_table,
            self.product_manager.get_products()
        )

    def load_products(self):
        """Load products from database"""
        # Keep original implementation
        self.status_bar.show_message(self.translator.t('loading_products'), "info")
        # NOTE: This original version does NOT use the loading indicator from UIHandler
        self.product_loader.load_products(self._is_closing)

        # Reset filter settings when loading all products (Original Structure)
        self.filter_handler.reset_filters()
        # NOTE: This original version does NOT update the filter button style

    @pyqtSlot(list)
    def handle_loaded_products(self, products):
        """Handle loaded products with elegant organization and visual feedback."""
        # Keep original implementation
        try:
            is_single_update = len(products) == 1 and self.product_manager.get_products()
            view_state = {}
            if hasattr(self.product_loader, 'get_view_state'):
                view_state = self.product_loader.get_view_state()

            sort_column = view_state.get('sort_column', 2)
            sort_order = view_state.get('sort_order', 0)
            recent_products = view_state.get('recent_products', [])

            if is_single_update:
                product = products[0]
                product_id = product['parcode'] if isinstance(product, dict) else product[0]
                self.product_manager.update_or_add_product(product_id, product)
                product_name = product['product_name'] if isinstance(product, dict) else product[2]
                table = self.product_table.table
                found_row = -1
                for row in range(table.rowCount()):
                    id_item = table.item(row, 0)
                    if id_item and id_item.text() == str(product_id):
                        found_row = row
                        break
                was_sorting_enabled = table.isSortingEnabled()
                table.setSortingEnabled(False)
                if found_row >= 0:
                    if hasattr(self.product_table, 'update_single_product'):  # Check if method exists
                        self.product_table.update_single_product(product)
                    else:  # Fallback to remove/add if method missing
                        table.removeRow(found_row)
                        if hasattr(self.product_table, 'append_product'): self.product_table.append_product(product)
                    if hasattr(self.product_table, '_apply_recent_styling'):  # Check if method exists
                        self.product_table._apply_recent_styling(
                            found_row if hasattr(self.product_table, 'update_single_product') else 0)
                else:
                    if hasattr(self.product_table, 'append_product'):  # Check if method exists
                        self.product_table.append_product(product)
                        if hasattr(self.product_table, '_apply_recent_styling'):  # Check if method exists
                            self.product_table._apply_recent_styling(0)
                    else:  # Fallback: reload all
                        self.product_manager.set_products(products)
                        self.product_table.update_table_data(self.product_manager.get_products())

                if was_sorting_enabled:
                    table.setSortingEnabled(True)
                    table.sortByColumn(sort_column, sort_order)

                updated = product_id in [p['parcode'] if isinstance(p, dict) else p[0]
                                         for p in self.product_manager.get_products()
                                         if p != product]  # Original logic for message
                self.status_bar.show_message(
                    self.translator.t('product_updated') if updated else self.translator.t('product_added'),
                    "success"
                )
                if hasattr(self.product_table, 'highlight_product'):  # Check method exists
                    self.product_table.highlight_product(product_name)
            else:
                self.product_manager.set_products(products)
                self.product_table.update_table_data(products)
                table = self.product_table.table
                table.setSortingEnabled(True)
                table.sortByColumn(sort_column, sort_order)
                if recent_products:
                    most_recent_id = recent_products[0]
                    product_name_to_highlight = None
                    for product in products:
                        try:
                            p_id = str(product['parcode'] if isinstance(product, dict) else product[0])
                            if str(p_id) == str(most_recent_id):
                                product_name_to_highlight = product['product_name'] if isinstance(product, dict) else \
                                product[2]
                                break
                        except (IndexError, KeyError, TypeError):
                            continue
                    if product_name_to_highlight and hasattr(self.product_table, 'highlight_product'):
                        QTimer.singleShot(200, lambda name=product_name_to_highlight:
                        self.product_table.highlight_product(name))

                self.status_bar.show_message(
                    self.translator.t('products_loaded').format(count=len(products)),
                    "success"
                )
                # Schedule column adjustment after products load
                QTimer.singleShot(100, self._adjust_table_columns)
        except Exception as e:
            print(f"Load error: {e}")
            import traceback
            print(traceback.format_exc())
            # NOTE: Original code didn't necessarily call self.show_error here
            self.status_bar.show_message(self.translator.t('load_error'), "error")

    def on_product_added(self, product_id):
        """Called after a product is added or updated"""
        # Keep original implementation
        QTimer.singleShot(100, lambda: self._highlight_product(product_id))

    def on_products_deleted(self, deleted_ids):
        """Called after products are deleted"""
        # Keep original implementation
        self.product_manager.remove_products_by_ids(deleted_ids)
        self.load_products()
        # NOTE: Original didn't have success message here

    def _highlight_product(self, product_id):
        """Highlight a product in the table"""
        # Keep original implementation
        if product_id is None: return
        try:
            highlighted = False
            if hasattr(self.product_table, 'highlight_row_by_id'):
                highlighted = self.product_table.highlight_row_by_id(str(product_id))
            if not highlighted and hasattr(self.product_table, 'highlight_product'):
                # Original fallback attempt might require product name, skipping complex lookup
                pass
                # self.product_table.highlight_product(str(product_id)) # Original fallback?

            loaded_message = self.translator.t('products_loaded').format(
                count=len(self.product_manager.get_products()))
            self.status_bar.show_message(loaded_message, "info", 5000)
        except Exception as e:
            print(f"Error highlighting product: {e}")

    def cancel_status_timer(self):
        """Cancel the status bar's auto-hide timer"""
        # Keep original implementation
        if hasattr(self.status_bar, 'cancel_auto_hide'):
            self.status_bar.cancel_auto_hide()

    def show_error(self, message):
        """Show error message"""
        # Keep original implementation
        if self._is_closing:
            return
        self.status_bar.show_message(message, "error")

    def highlight_product(self, search_text):
        """Highlight a product in the table"""
        # Keep original implementation
        if not self.product_table or not hasattr(self.product_table, 'highlight_product'): return False
        return self.product_table.highlight_product(search_text)

    def update_translations(self):
        """Update all translations in the UI"""
        # Keep original implementation
        self.ui_handler.update_translations()

    def closeEvent(self, event):
        """Handle widget close event"""
        # Keep original implementation
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
        self.print_btn.clicked.connect(self.print_products)  # Single print button with integrated preview
        self.refresh_btn.clicked.connect(self.load_products)

        # self.search_timer connected in __init__
        self.search_input.textChanged.connect(self._on_search_input_changed)

        self.product_table.cellChanged.connect(self.on_cell_changed)

        self.select_toggle.clicked.connect(self.cancel_status_timer)
        self.refresh_btn.clicked.connect(self.cancel_status_timer)

        self.product_loader.products_loaded.connect(self.handle_loaded_products)
        self.product_loader.error_occurred.connect(self.show_error)

        # Connect delete_operation signal if available
        if hasattr(self.delete_operation, 'products_deleted'):
            self.delete_operation.products_deleted.connect(self.on_products_deleted)

    def _on_search_input_changed(self, text):
        """Handle search input changes with delay to improve performance"""
        # Keep original implementation
        if self.search_timer.isActive():
            self.search_timer.stop()

        search_text = text.strip()

        if hasattr(self, '_updating_ui') and self._updating_ui:
            return

        if search_text:
            self.search_timer.start(250)
        else:
            # If search is cleared, show all products (Original logic reloaded from manager)
            if hasattr(self, '_updating_ui') and self._updating_ui: return  # Guard added
            try:
                self._updating_ui = True
                self.product_table.table.blockSignals(True)
                self.product_table.update_table_data(self.product_manager.get_products())
                self.product_table.table.blockSignals(False)
                # Reset highlights if possible
                if hasattr(self.product_table, '_reset_cell_formatting'): self.product_table._reset_cell_formatting()
                self.status_bar.clear()
            finally:
                self._updating_ui = False

    def _delayed_search(self):
        """Perform search after delay to avoid searching on every keystroke"""
        # Keep original implementation
        search_text = self.search_input.text().strip()
        if not search_text:
            # If search is cleared (Original logic reloaded from manager)
            if hasattr(self, '_updating_ui') and self._updating_ui: return  # Guard added
            try:
                self._updating_ui = True
                self.product_table.update_table_data(self.product_manager.get_products())
                # Reset highlights if possible
                if hasattr(self.product_table, '_reset_cell_formatting'): self.product_table._reset_cell_formatting()
                self.status_bar.clear()
            finally:
                self._updating_ui = False
        else:
            self.on_search(search_text)

    def on_search(self, text):
        """Handle search with optimized performance"""
        # Skip if already in update mode
        if hasattr(self, '_updating_ui') and self._updating_ui:
            return

        try:
            self._updating_ui = True

            # Filter products
            filtered_products, message = self.search_handler.search_products(
                self.product_manager.get_products(),
                text
            )

            # Block signals during update
            with SignalBlocker(self.product_table.table):
                self.product_table.update_table_data(filtered_products)

                # Highlight if needed
                if text.strip() and hasattr(self.product_table, 'highlight_matching_text'):
                    self.product_table.highlight_matching_text(text)

            # Show message if applicable
            if message:
                self.status_bar.show_message(message, "info")
            else:
                self.status_bar.clear()

        finally:
            self._updating_ui = False

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