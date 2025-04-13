# --- Imports ---
import sys
import traceback
# Import necessary PyQt5 components
from PyQt5.QtWidgets import QDialog, QAbstractItemView
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QColor

# --- Configuration ---
# Add project root to the Python path if necessary. Adjust the path based on your actual project structure.
# Example: sys.path.append(r'C:\path\to\your\project\root')

# --- Application Module Imports ---
# Try to import necessary components, provide feedback if imports fail.
try:
    # Assuming these paths are correct relative to the project root or Python path
    from widgets.products.dialogs.themed_meesage import ThemedMessageDialog
    # Use the enhanced dialog with new fields
    from widgets.products.dialogs.add_product_dialog import AddProductDialog
    from themes import get_color
except ImportError as import_error:
    print(f"FATAL IMPORT ERROR in add_operation.py: {import_error}")
    print("Please ensure the project structure and Python path are correct.")
    # Exit or raise if essential components are missing
    raise SystemExit(f"Could not import required modules: {import_error}")


class AddOperation:
    """
    Handles the workflow for adding a new product or updating an existing one
    when a duplicate name is found. Integrates with UI elements like dialogs,
    status bar, and product table for a seamless user experience, including
    validation and visual feedback (highlighting).

    Now supports manufacturer and original fields.
    """

    def __init__(self, parent_widget, translator, db, validator, status_bar):
        """
        Initializes the AddOperation handler.

        Args:
            parent_widget: The parent QWidget (likely ProductsWidget).
            translator: The translation object for UI text (used via translator.t(key)).
            db: The database connection object (e.g., CarPartsDB instance).
            validator: The ProductValidator instance.
            status_bar: The status bar widget for displaying messages.
        """
        self.parent = parent_widget
        self.translator = translator
        self.db = db
        self.validator = validator
        self.status_bar = status_bar
        # Duration (ms) for the highlight effect before fading starts
        self._highlight_duration = 3000  # 3 seconds

        # Basic check for required components on parent
        if not all([hasattr(parent_widget, 'product_manager'),
                    hasattr(parent_widget, 'product_table'),
                    hasattr(parent_widget, 'product_loader')]):
            print(
                "Warning: AddOperation initialized without full parent components (manager, table, loader). Some features might be limited.")

    def process_add_product(self, data):
        """
        Validates data, interacts with the database (add or update),
        and triggers UI updates.

        Args:
            data (dict): The product data obtained from the dialog.

        Returns:
            int or None: The product ID if successfully added/updated, otherwise None.
        """
        product_id = None  # Initialize product_id
        try:
            product_name_for_messages = data.get('product_name', self.translator.t('unknown_product'))
            print(f"Processing product: '{product_name_for_messages}'")

            # Store the original parcode before sanitization
            original_parcode = data.get('parcode', '')
            print(f"Original parcode from dialog: '{original_parcode}'")

            # Store manufacturer and is_original before sanitization
            original_manufacturer = data.get('manufacturer', '')
            is_original = data.get('is_original', False)
            print(f"Original manufacturer: '{original_manufacturer}', Is original: {is_original}")

            # 1. Sanitize and Validate Data
            sanitized_data = self.validator.sanitize_product_data(data)

            # Re-add or ensure parcode is preserved after sanitization
            if original_parcode:
                sanitized_data['parcode'] = original_parcode
                print(f"Preserved parcode after sanitization: '{sanitized_data.get('parcode')}'")

            # Re-add manufacturer and is_original to sanitized data
            sanitized_data['manufacturer'] = original_manufacturer
            # Database uses 'original' field name (note the difference from our 'is_original')
            sanitized_data['original'] = is_original
            print(f"Added manufacturer and original status to sanitized data")

            is_valid, error_msg = self.validator.validate_product(sanitized_data)

            if not is_valid:
                print(f"Validation failed: {error_msg}")
                if self.status_bar:
                    # error_msg is already translated by the validator
                    self.status_bar.show_message(error_msg, "error")
                return None  # Stop processing

            product_name = sanitized_data['product_name']

            # 2. Check if Product Already Exists (by name)
            print(f"Checking for existing product: '{product_name}'")
            existing = self.db.get_part_by_name(product_name)

            # 3. Handle Existing Product (Update Path)
            if existing:
                print(f"Found existing product: ID {existing.get('parcode', 'N/A')}")
                # Confirm Overwrite with User
                # Translate title and message (using format for name)
                title = self.translator.t('overwrite_title')
                message = self.translator.t('overwrite_message').format(name=product_name)
                confirm = ThemedMessageDialog.confirm(
                    title, message, parent=self.parent, icon_type="question"
                )

                if confirm:
                    print(f"User confirmed overwrite for '{product_name}'.")
                    product_id = existing['parcode']  # Assuming parcode exists if existing is True

                    # Ensure parcode is preserved in the update
                    if original_parcode:
                        sanitized_data['parcode'] = original_parcode

                    # Perform Database Update
                    success = self.db.update_part(product_id, **sanitized_data)
                    if not success:
                        print(f"ERROR: Database update failed for product ID: {product_id}")
                        raise Exception(f"Failed to update existing product with ID: {product_id}")

                    print(f"Database update successful for ID: {product_id}")

                    # Fetch Updated Data for UI consistency
                    updated_product = self.db.get_part(product_id)
                    if not updated_product:
                        print(f"ERROR: Failed to fetch updated product data after update for ID: {product_id}")
                        # Show warning, UI might lag until next refresh
                        warning_msg = self.translator.t('product_updated_fetch_error').format(name=product_name)
                        if self.status_bar: self.status_bar.show_message(warning_msg, "warning", 5000)
                    else:
                        # Update In-Memory Store & UI Table
                        if hasattr(self.parent, 'product_manager'):
                            self.parent.product_manager.update_or_add_product(product_id, updated_product)
                        if hasattr(self.parent, 'product_table'):
                            self.parent.product_table.update_single_product(updated_product)

                        # Show success message (translate and format)
                        success_message = self.translator.t('product_updated').format(name=product_name)
                        if self.status_bar: self.status_bar.show_message(success_message, "success", 4000)

                    # Mark as Recent
                    if hasattr(self.parent, 'product_loader'):
                        self.parent.product_loader._add_recent_product(product_id)

                    # Trigger Highlight Animation
                    QTimer.singleShot(150, lambda pid=product_id: self._ensure_product_visible(pid))
                    return product_id

                else:
                    # User cancelled the overwrite
                    print(f"User cancelled overwrite for '{product_name}'.")
                    if self.status_bar:
                        # Translate cancellation message
                        cancel_msg = self.translator.t('update_cancelled')
                        self.status_bar.show_message(cancel_msg, "info", 3000)
                    return None

            # 4. Handle New Product (Add Path)
            else:
                print(f"No existing product found for '{product_name}'. Proceeding with add.")

                # Make sure the parcode is passed directly to db.add_part
                # First ensure parcode is in sanitized_data
                if original_parcode:
                    sanitized_data['parcode'] = original_parcode
                    print(f"Using custom parcode for new product: '{sanitized_data['parcode']}'")

                # Perform Database Insert
                # Include manufacturer and original fields
                success = self.db.add_part(
                    category=sanitized_data.get('category', ''),
                    product_name=sanitized_data.get('product_name', ''),
                    quantity=sanitized_data.get('quantity', 0),
                    price=sanitized_data.get('price', 0.0),
                    original=sanitized_data.get('original', False),
                    manufacturer=sanitized_data.get('manufacturer', ''),
                    parcode=sanitized_data.get('parcode', ''),
                    compatible_models=sanitized_data.get('compatible_models', '')
                )

                if not success:
                    print(f"ERROR: Database add failed for product '{product_name}'.")
                    raise Exception("Failed to add new product to the database")

                print(f"Database add successful for '{product_name}'.")

                # Verify and Get New Product Data (including ID)
                # Try to verify by parcode first if we have it, otherwise by name
                if original_parcode:
                    verify_product = self.db.get_part_by_parcode(original_parcode)
                    if not verify_product:
                        print(f"Warning: Could not find product by parcode '{original_parcode}'. Trying by name.")
                        verify_product = self.db.get_part_by_name(product_name)
                else:
                    verify_product = self.db.get_part_by_name(product_name)

                if not verify_product:
                    print(f"CRITICAL ERROR: Could not verify product '{product_name}' after successful add!")
                    raise Exception("Product verification failed after supposedly successful add")

                product_id = verify_product['id']  # Use ID for internal references
                parcode = verify_product['parcode']  # Get the actual parcode used
                print(f"Verified new product. ID: {product_id}, Parcode: {parcode}")

                # Update In-Memory Store & UI Table
                if hasattr(self.parent, 'product_manager'):
                    self.parent.product_manager.update_or_add_product(product_id, verify_product)
                if hasattr(self.parent, 'product_table'):
                    self.parent.product_table.append_product(verify_product)

                # Mark as Recent
                if hasattr(self.parent, 'product_loader'):
                    self.parent.product_loader._add_recent_product(product_id)

                # Show Success Message (translate and format)
                success_message = self.translator.t('product_added').format(name=product_name)
                if self.status_bar:
                    self.status_bar.show_message(success_message, "success", 4000)

                # Trigger Highlight Animation
                QTimer.singleShot(150, lambda pid=product_id: self._ensure_product_visible(pid))
                return product_id

        # 5. General Error Handling
        except Exception as e:
            print(f"ERROR: Exception during product processing for '{product_name_for_messages}': {e}")
            import traceback
            traceback.print_exc()
            if self.status_bar:
                # Translate generic error message
                error_text = self.translator.t('add_update_error').format(error=str(e))
                self.status_bar.show_message(error_text, "error")
            return None  # Indicate failure


    def _ensure_product_visible(self, product_id):
        """
        Scrolls the product table to make the specified product ID visible
        and initiates the highlight animation.
        """
        print(f"Ensuring visibility for product ID: {product_id}")
        if product_id is None:
            print("Warning: _ensure_product_visible called with None product_id.")
            return

        table_widget = None
        try:
            if not hasattr(self.parent, 'product_table') or not self.parent.product_table:
                print("Warning: Parent widget lacks 'product_table'. Cannot ensure visibility.")
                return
            table_widget = self.parent.product_table.table
            if not table_widget:
                print("Warning: 'product_table' object has no 'table' attribute.")
                return

            found_row = -1
            for row in range(table_widget.rowCount()):
                id_item = table_widget.item(row, 0)
                if id_item and id_item.text() == str(product_id):
                    found_row = row
                    print(f"Found product ID {product_id} at row {row}.")
                    break

            if found_row < 0:
                print(f"Warning: Product ID {product_id} not found in table. Cannot scroll or highlight.")
                return

            item_to_scroll = table_widget.item(found_row, 0)
            if item_to_scroll:
                print(f"Scrolling to row {found_row}.")
                table_widget.scrollToItem(item_to_scroll, QAbstractItemView.PositionAtCenter)
            else:
                print(f"Warning: Item at row {found_row}, col 0 not found for scrolling.")

            if found_row < table_widget.rowCount():
                print(f"Applying highlight animation to row {found_row}.")
                self._apply_elegant_highlight(found_row)
            else:
                print(f"Warning: Row {found_row} became invalid before highlight could start.")

        except Exception as e:
            print(f"ERROR: Failed to ensure product visibility (ID: {product_id}): {e}")
            traceback.print_exc()

    def _apply_elegant_highlight(self, row):
        """
        Applies an animated background highlight effect to the specified row.
        Handles signal blocking during item modification.
        """
        print(f"Initiating highlight animation for row: {row}")
        table = None
        try:
            if not hasattr(self.parent, 'product_table') or not self.parent.product_table:
                print("Warning: Parent widget lacks 'product_table'. Cannot apply highlight.")
                return
            table = self.parent.product_table.table
            if not table:
                print("Warning: 'product_table' object has no 'table' attribute.")
                return

            if row < 0 or row >= table.rowCount():
                print(f"Warning: Invalid row index ({row}) passed to _apply_elegant_highlight.")
                return

            initial_highlight_color = QColor(get_color('success'))
            text_color_default = QColor(get_color('text'))  # Store default text color
            initial_highlight_color.setAlpha(180)

            # --- Apply Initial Highlight State (Signals Blocked) ---
            table.blockSignals(True)
            print(f"Applying initial highlight, signals blocked for row {row}.")
            try:
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item:
                        item.setBackground(initial_highlight_color)
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)
                        # Optional: Set initial text color if needed for contrast
                        # item.setForeground(QColor(get_color('background'))) # Example
            except Exception as initial_highlight_err:
                print(f"ERROR applying initial highlight for row {row}: {initial_highlight_err}")
            finally:
                table.blockSignals(False)
                print(f"Initial highlight applied, signals unblocked for row {row}.")

            # --- Nested Function for Fade Animation Steps ---
            def fade_step(color_to_fade, alpha):
                if not table or row >= table.rowCount():
                    print(f"Animation stopped: Row {row} became invalid or table disappeared.")
                    return

                table.blockSignals(True)
                try:
                    if alpha <= 0:
                        print(f"Fade complete for row {row}. Restoring default style.")
                        # Restore default styling
                        bg_color = QColor(get_color('background'))
                        secondary_color = QColor(get_color('secondary'))
                        row_bg = secondary_color if row % 2 else bg_color
                        text_qcolor = QColor(get_color('text'))  # Use stored default

                        for col in range(table.columnCount()):
                            item = table.item(row, col)
                            if item:
                                item.setBackground(row_bg)
                                item.setForeground(text_qcolor)
                                font = item.font()
                                font.setBold(False)
                                item.setFont(font)
                        return  # End animation

                    current_alpha = max(0, int(alpha))
                    color_to_fade.setAlpha(current_alpha)

                    for col in range(table.columnCount()):
                        item = table.item(row, col)
                        if item:
                            item.setBackground(color_to_fade)
                            # Optional: Adjust text color during fade if needed for readability
                            # current_text_color = text_color_default if current_alpha < 80 else QColor(get_color('background'))
                            # item.setForeground(current_text_color)

                except Exception as fade_err:
                    print(f"ERROR during fade step for row {row}, alpha {alpha}: {fade_err}")
                finally:
                    table.blockSignals(False)

                # --- Schedule Next Step --- (Faster Fade)
                QTimer.singleShot(100, lambda: fade_step(color_to_fade, alpha - 15))

            # --- Start the Fade Sequence ---
            animation_color = QColor(get_color('success'))  # Base color for fading
            print(f"Starting fade timer for row {row} after {self._highlight_duration}ms.")
            QTimer.singleShot(self._highlight_duration, lambda: fade_step(animation_color, 160))  # Start fade

        except Exception as e:
            print(f"ERROR: Failed to apply elegant highlight to row {row}: {e}")
            traceback.print_exc()
            if table is not None and hasattr(table, 'signalsBlocked') and table.signalsBlocked():
                print(f"Ensuring signals are unblocked after error for row {row}.")
                table.blockSignals(False)

    # This is a focused fix for the AddOperation class
    # to ensure the dialog correctly signals the status bar when it closes

    # Fix for show_add_dialog method in AddOperation class
    def show_add_dialog(self):
        """Creates and shows the 'Add Product' dialog with status bar integration."""
        try:
            # Start dialog action in parent's status bar
            if hasattr(self.parent, 'status_bar') and hasattr(self.parent.status_bar, 'start_dialog_action'):
                self.parent.status_bar.start_dialog_action(
                    "add",
                    self.translator.t('add:preparing')  # Remove the second positional argument
                )
                print("Started add dialog action in status bar")
            else:
                # Fallback for older status bar
                if self.status_bar:
                    self.status_bar.show_message(
                        self.translator.t('add:preparing'),  # Remove the second positional argument
                        "add"
                    )

            # Use the enhanced dialog with new fields
            dialog = AddProductDialog(self.translator, self.parent)

            # Connect the finished signal to handle the result *after* the dialog closes
            dialog.finished.connect(lambda result: self._handle_dialog_result(dialog, result))

            # Use exec_() for a modal dialog to ensure we don't return until dialog closes
            dialog.exec_()

            # If dialog.exec_() has returned, the dialog has closed
            print("Add dialog has closed")

        except Exception as e:
            print(f"ERROR: Failed to create or show AddProductDialog: {e}")
            import traceback
            traceback.print_exc()

            # End dialog action with error
            if hasattr(self.parent, 'status_bar') and hasattr(self.parent.status_bar, 'end_dialog_action'):
                self.parent.status_bar.end_dialog_action(
                    self.translator.t('dialog_error')  # Remove the second positional argument
                )
            else:
                # Fallback for older status bar
                if self.status_bar:
                    self.status_bar.show_message(
                        self.translator.t('dialog_error'),  # Remove the second positional argument
                        "error"
                    )

    # Similar changes needed in _handle_dialog_result method
    def _handle_dialog_result(self, dialog, result):
        """Processes the data if the dialog was accepted, immediately collapses on cancel"""
        print(f"Dialog result: {result}")

        if result == QDialog.Accepted:
            print("Add Product Dialog Accepted.")
            try:
                data = dialog.get_data()
                if data:
                    # Process the product data...
                    product_id = self.process_add_product(data)

                    # End dialog action with appropriate message
                    if hasattr(self.parent, 'status_bar') and hasattr(self.parent.status_bar, 'end_dialog_action'):
                        if product_id:
                            self.parent.status_bar.end_dialog_action(
                                self.translator.t('product_added_success')
                            )
                        else:
                            self.parent.status_bar.end_dialog_action(
                                self.translator.t('product_add_failed')
                            )
                        print("Ended add dialog action in status bar")
                    else:
                        # Fallback
                        if self.status_bar:
                            # Already showing success message in process_add_product
                            pass
                else:
                    print("Warning: Dialog accepted, but no data retrieved.")
                    if hasattr(self.parent, 'status_bar') and hasattr(self.parent.status_bar, 'end_dialog_action'):
                        self.parent.status_bar.end_dialog_action(
                            self.translator.t('data_error')
                        )
                    else:
                        # Fallback
                        if self.status_bar:
                            self.status_bar.show_message(
                                self.translator.t('data_error'),
                                "warning"
                            )
            except Exception as e:
                print(f"ERROR: Failed to process dialog result data: {e}")
                import traceback
                traceback.print_exc()

                # End dialog action with error message
                if hasattr(self.parent, 'status_bar') and hasattr(self.parent.status_bar, 'end_dialog_action'):
                    self.parent.status_bar.end_dialog_action(
                        self.translator.t('add_product_error')
                    )
                else:
                    # Fallback
                    if self.status_bar:
                        self.status_bar.show_message(
                            self.translator.t('data_error'),
                            "error"
                        )
        else:
            # Handle dialog cancellation/rejection - IMMEDIATELY collapse with NO message
            print("Add Product Dialog Rejected/Cancelled.")

            # Handle both parent and local status bar scenarios
            if hasattr(self.parent, 'status_bar'):
                status_bar = self.parent.status_bar
                if hasattr(status_bar, 'force_collapse'):
                    status_bar.force_collapse()  # Most direct approach
                elif hasattr(status_bar, 'end_dialog_action'):
                    status_bar.end_dialog_action("")  # Empty string to avoid showing message
                else:
                    status_bar.clear()  # Fallback to simple clear
            elif self.status_bar:
                if hasattr(self.status_bar, 'force_collapse'):
                    self.status_bar.force_collapse()
                elif hasattr(self.status_bar, 'end_dialog_action'):
                    self.status_bar.end_dialog_action("")
                else:
                    self.status_bar.clear()