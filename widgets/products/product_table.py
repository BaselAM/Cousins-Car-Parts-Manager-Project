from PyQt5.QtWidgets import (QAbstractItemView, QHeaderView, QTableWidget,
                             QTableWidgetItem, QFrame, QVBoxLayout, QWidget,
                             QAbstractButton, QLabel)
# Import QTimer for deferred actions
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QItemSelectionModel, QRect

from PyQt5.QtGui import QColor, QBrush, QFont, QPalette
from themes import get_color  # Assuming themes.py provides get_color
from .components.barcode_scanner_button import ScanningDialog
# Assuming components are in a sub-directory 'components'
from .components.table_delegates import ThemedNumericDelegate, ThemedItemDelegate
# Assuming translations are in a specific structure


# Typing imports for hints
from typing import List, Dict, Any, Optional, Tuple, Union
import re


class ProductsTable(QFrame):
    """
    Enhanced table widget for products with improved styling, feedback,
    and usability features. Optimized for performance and reliability.
    Category column has been removed.
    """
    cellChanged = pyqtSignal(int, int)  # Row, column

    # Column Constants for readability and maintenance - UPDATED for category removal
    COL_ID = 0
    COL_NAME = 1
    COL_MANUFACTURER = 2  # Renamed to match its new content
    COL_QTY = 3
    COL_PRICE = 4
    COLUMN_COUNT = 5

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.setObjectName("tableContainer")

        # Add status_bar attribute for barcode scanning feedback
        self.status_bar = None

        # Internal state tracking
        self._previous_selection_mode = False
        self._width_adjusted_once = False
        self._is_updating_table = False
        self._highlight_animation_row = -1
        self._highlight_alpha = 255
        self._highlight_timer = None
        self._highlight_base_color = None
        self._highlight_text_color = None

        # --- Layout ---
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # --- Table Widget ---
        self.table = QTableWidget()
        self.table.setObjectName("productsTableView")
        self.table.setColumnCount(self.COLUMN_COUNT)
        self.update_headers()

        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(38)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)

        # Selection & Interaction
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed
        )
        self.table.setShowGrid(False)

        # Scrolling
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Add connection for barcode scanning on double-click
        self.table.doubleClicked.connect(self.handle_double_click)

        # Corner button - attempt removal
        try:
            corner_button = self.table.findChild(QAbstractButton)
            if corner_button: corner_button.hide()
            self.table.setCornerButtonEnabled(False)
        except AttributeError:
            pass

        # Themed Delegates for editing
        self.item_delegate = ThemedItemDelegate(self.table)
        self.numeric_delegate = ThemedNumericDelegate(self.table)
        self.table.setItemDelegateForColumn(self.COL_NAME, self.item_delegate)
        self.table.setItemDelegateForColumn(self.COL_MANUFACTURER, self.item_delegate)
        self.table.setItemDelegateForColumn(self.COL_QTY, self.numeric_delegate)
        self.table.setItemDelegateForColumn(self.COL_PRICE, self.numeric_delegate)

        # Add table to layout
        layout.addWidget(self.table)

        # --- Empty Table Label ---
        try:
            empty_text = self.translator.t('no_products_found')
            if not empty_text or empty_text == 'no_products_found':
                empty_text = "No products found."
        except Exception as e:
            print(f"Warning: Translation failed for 'no_products_found': {e}")
            empty_text = "No products found."

        self.empty_label = QLabel(empty_text, self.table)
        self.empty_label.setObjectName("emptyTableLabel")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setVisible(False)
        font = self.empty_label.font()
        font.setPointSize(16)
        font.setItalic(True)
        self.empty_label.setFont(font)

        # --- Connections ---
        self.table.cellChanged.connect(self._on_cell_changed)

        # Apply initial styling
        self.apply_theme()

    # Add these methods to your ProductsTable class

    def handle_double_click(self, index):
        """
        Handle double-click on table cells.
        If it's the ID column (parcode), show barcode scanner instead of editor.
        """
        try:
            # Only handle parcode column
            if not index.isValid() or index.column() != self.COL_ID:
                return

            # Prevent default editing for now
            original_edit_triggers = self.table.editTriggers()
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

            # Show the barcode scanner dialog
            try:
                dialog = ScanningDialog(self.window(), self.translator)
                # Use a safe lambda that captures the current row
                current_row = index.row()
                dialog.barcode_scanned.connect(
                    lambda barcode: self.safe_update_parcode(current_row, barcode)
                )
                dialog.exec_()
            except Exception as e:
                print(f"Error showing scanner dialog: {e}")
            finally:
                # Restore original edit triggers
                self.table.setEditTriggers(original_edit_triggers)
        except Exception as e:
            print(f"Double-click handler error: {e}")

    def safe_update_parcode(self, row, barcode):
        """
        Safely update parcode from barcode scanner with error handling
        """
        try:
            # Validate inputs
            if barcode is None or not barcode or row < 0 or row >= self.table.rowCount():
                return

            # Get item safely
            item = self.table.item(row, self.COL_ID)
            if item is None:
                print(f"Error: No item at row {row}, column {self.COL_ID}")
                return

            # Update the cell with the scanned barcode
            old_value = item.text()

            # Safely block signals
            was_blocked = self.table.signalsBlocked()
            self.table.blockSignals(True)

            try:
                # Set the new value
                item.setText(barcode)
            finally:
                # Restore original signal state
                self.table.blockSignals(was_blocked)

            # Trigger cell changed event
            self.cellChanged.emit(row, self.COL_ID)

            # Highlight the change if method exists
            if hasattr(self, '_apply_recent_styling'):
                try:
                    self._apply_recent_styling(row)
                except Exception as style_err:
                    print(f"Styling error: {style_err}")

            # Show status message if available
            if hasattr(self, 'status_bar') and self.status_bar is not None:
                try:
                    message = f"Barcode updated: {barcode}"
                    # Try to get translated message
                    if self.translator:
                        try:
                            message = self.translator.t('barcode:barcode_scanned', barcode=barcode)
                        except:
                            pass
                    self.status_bar.show_message(message, "success", 3000)
                except Exception as status_err:
                    print(f"Status bar error: {status_err}")

            print(f"Updated row {row} parcode from '{old_value}' to '{barcode}'")

        except Exception as e:
            print(f"Safe update error: {e}")
            import traceback
            traceback.print_exc()

    def update_headers(self):
        """Update table headers with current translations."""
        # Updated headers - using manufacturer instead of compatible_models
        headers = [
            self.translator.t('id'),
            self.translator.t('product_name'),
            self.translator.t('manufacturer'),  # Changed from 'compatible_models'
            self.translator.t('quantity'),
            self.translator.t('price')
        ]
        self.table.setHorizontalHeaderLabels(headers)

    def _on_cell_changed(self, row: int, column: int):
        """Internal handler for cell changes that emits the public signal."""
        self.cellChanged.emit(row, column)

    # --- Column Width Management (Enhanced) ---

    def adjust_column_widths(self):
        """Set adaptive column widths based on available space with improved reliability."""
        total_width = self.table.viewport().width()
        if total_width <= 0:
            # Schedule another attempt if the viewport isn't ready yet
            QTimer.singleShot(100, self.adjust_column_widths)
            return

        # Store if this is the first adjustment
        is_first_adjustment = not self._width_adjusted_once
        self._width_adjusted_once = True

        # Try content-based sizing first on initial display
        if is_first_adjustment:
            # Temporarily disable sorting during content-based sizing
            was_sorting_enabled = self.table.isSortingEnabled()
            if was_sorting_enabled:
                self.table.setSortingEnabled(False)

            # Resize based on content
            self.table.resizeColumnsToContents()

            # Get header width hints
            header = self.table.horizontalHeader()
            header_widths = [header.sectionSizeHint(i) for i in range(self.COLUMN_COUNT)]

            # Collect current content-based widths
            content_widths = [max(50, self.table.columnWidth(i), header_widths[i])
                              for i in range(self.COLUMN_COUNT)]

            # Check if content-based widths fit within viewport
            content_total = sum(content_widths)

            if content_total <= total_width * 0.95:  # Only if content fits with small margin
                # Apply content-based widths
                for i, width in enumerate(content_widths):
                    self.table.setColumnWidth(i, width)

                # Restore sorting if needed
                if was_sorting_enabled:
                    self.table.setSortingEnabled(True)
                return

            # Restore sorting if we're falling back to percentage-based
            if was_sorting_enabled:
                self.table.setSortingEnabled(True)

        # Default column percentages - UPDATED (redistributed category's 12%)
        # Original: [8, 12, 30, 25, 10, 15]
        # New: [8, 38, 29, 10, 15]
        col_percents = [24, 26, 25, 10, 15]

        # Calculate minimum width to prevent tiny columns
        min_width = 50

        # Reserve some space for scrollbar if it's visible
        scrollbar_width = 0
        if self.table.verticalScrollBar().isVisible():
            scrollbar_width = self.table.verticalScrollBar().width() + 2

        # Adjust available width for calculations
        available_width = total_width - scrollbar_width

        # Calculate and set widths based on percentages
        total_percent = sum(col_percents)
        remaining_width = available_width

        # Set widths for all but the last column to ensure we don't exceed available space
        for i, percent in enumerate(col_percents[:-1]):
            width = max(min_width, int(available_width * percent / total_percent))
            width = min(width, remaining_width - min_width)  # Ensure we leave space for remaining columns
            self.table.setColumnWidth(i, width)
            remaining_width -= width

        # Give all remaining space to the last column
        last_col = len(col_percents) - 1
        self.table.setColumnWidth(last_col, max(min_width, remaining_width))

    def save_column_widths(self, settings):
        """Saves current column widths to QSettings."""
        if not self.table.isVisible(): return
        try:
            widths = [self.table.columnWidth(i) for i in range(self.COLUMN_COUNT)]
            settings.setValue("productsTable/columnWidths", widths)
            print(f"Saved column widths: {widths}")
        except Exception as e:
            print(f"Error saving column widths: {e}")

    def restore_column_widths(self, settings):
        """Restores column widths from QSettings."""
        try:
            widths = settings.value("productsTable/columnWidths")
            if widths and isinstance(widths, list) and len(widths) == self.COLUMN_COUNT:
                print(f"Restoring column widths: {widths}")
                self.table.blockSignals(True)
                self.table.horizontalHeader().blockSignals(True)
                try:
                    for i, width in enumerate(widths):
                        if isinstance(width, (int, str)) and int(width) > 0:
                            self.table.setColumnWidth(i, int(width))
                        else:
                            print(f"Warning: Invalid saved width for column {i}: {width}. Using default.")
                            self.adjust_column_widths()
                            return False  # Indicate fallback
                finally:
                    self.table.blockSignals(False)
                    self.table.horizontalHeader().blockSignals(False)
                return True
            else:
                print("No valid saved column widths found, using defaults.")
                self.adjust_column_widths()
        except Exception as e:
            print(f"Error restoring column widths: {e}")
            self.adjust_column_widths()
        return False

    # --- Selection and Interaction (Enhanced) ---

    def set_selection_mode(self, enable_multi_select: bool):
        """
        Toggle between single cell and multi-row selection modes with
        improved state preservation.
        """
        # Save current selection state if possible
        preserve_selection = False
        selected_ids = []
        if hasattr(self, '_previous_selection_mode') and self._previous_selection_mode != enable_multi_select:
            preserve_selection = True
            selected_ids = self._save_selection()

        self._previous_selection_mode = enable_multi_select

        # Configure table for the selection mode
        self.table.blockSignals(True)
        try:
            if enable_multi_select:
                self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
                self.table.setSelectionMode(QAbstractItemView.MultiSelection)
                self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            else:
                # End any active editing before changing mode
                if self.table.state() == QAbstractItemView.EditingState:
                    current_index = self.table.currentIndex()
                    if current_index.isValid() and self.table.indexWidget(current_index):
                        self.table.commitData(self.table.indexWidget(current_index))

                self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
                self.table.setSelectionMode(QAbstractItemView.SingleSelection)
                self.table.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)

                # Don't clear selection here unless we can't preserve it
                if not preserve_selection:
                    self.table.clearSelection()
        finally:
            self.table.blockSignals(False)

        # Restore selection if possible and requested
        if preserve_selection and selected_ids:
            QTimer.singleShot(0, lambda: self._restore_selection(selected_ids))

    def get_selected_rows_data(self) -> List[Tuple[str, str]]:
        """
        Get data (Parcode, Name) from selected rows with improved error handling.
        Returns parcodes instead of database IDs.
        """
        selected_rows = self.table.selectionModel().selectedRows()

        # IMPORTANT FIX: Only use current row as fallback when NOT in MultiSelection mode
        # This prevents treating the current row as selected when nothing is actually selected
        # in selection mode
        if not selected_rows and self.table.selectionMode() != QAbstractItemView.MultiSelection:
            current_row = self.table.currentRow()
            if current_row >= 0:
                # Create a mock index for the current row
                model_index = self.table.model().index(current_row, 0)
                if model_index.isValid():
                    selected_rows = [model_index]

        product_details = []

        for index in selected_rows:
            row = index.row()
            try:
                # Now get parcode from first column
                parcode_item = self.table.item(row, self.COL_ID)
                name_item = self.table.item(row, self.COL_NAME)

                if parcode_item and name_item:
                    try:
                        parcode = parcode_item.text()  # Get parcode as string
                        product_name = name_item.text() or self.translator.t('unnamed_product')
                        product_details.append((parcode, product_name))
                    except (ValueError, TypeError):
                        print(f"Warning: Could not parse parcode for selected row {row}")
                else:
                    print(f"Warning: Missing parcode or Name item for selected row {row}")
            except Exception as e:
                print(f"Error processing selected row {row}: {e}")

        return product_details

    def highlight_product(self, search_text: str) -> bool:
        """Improved scroll to and highlight product row by name."""
        if not search_text: return False

        search_text_lower = search_text.lower()
        target_row = -1

        # Find exact match first
        for row in range(self.table.rowCount()):
            product_item = self.table.item(row, self.COL_NAME)
            if product_item and product_item.text().lower() == search_text_lower:
                target_row = row
                break

        # Try partial match if no exact match
        if target_row == -1:
            for row in range(self.table.rowCount()):
                product_item = self.table.item(row, self.COL_NAME)
                if product_item and search_text_lower in product_item.text().lower():
                    target_row = row
                    break

        if target_row != -1:
            # Set current item and scroll properly
            self.table.setCurrentItem(self.table.item(target_row, self.COL_NAME))

            # Better scrolling that ensures visibility
            self.table.scrollToItem(
                self.table.item(target_row, 0),
                QAbstractItemView.ScrollHint.PositionAtCenter
            )

            # Ensure table has focus
            self.table.setFocus()

            # Apply highlight with improved visual effect
            highlight_color = QColor(get_color('accent', get_color('highlight')))
            text_color = QColor(get_color('background'))

            self.table.blockSignals(True)
            try:
                for col in range(self.table.columnCount()):
                    item = self.table.item(target_row, col)
                    if item:
                        item.setBackground(highlight_color)
                        item.setForeground(text_color)
            finally:
                self.table.blockSignals(False)

            return True

        return False

    def highlight_row_by_id(self, product_id: str) -> bool:
        """Scrolls to and highlights the row with the matching product ID."""
        if not product_id:
            return False

        try:
            # Find row with matching ID
            target_row = -1
            for row in range(self.table.rowCount()):
                id_item = self.table.item(row, self.COL_ID)
                if id_item and id_item.text() == product_id:
                    target_row = row
                    break

            if target_row == -1:
                return False

            # Set as current row and scroll to it
            self.table.setCurrentCell(target_row, self.COL_NAME)
            self.table.scrollToItem(
                self.table.item(target_row, 0),
                QAbstractItemView.ScrollHint.PositionAtCenter
            )

            # Apply special styling
            self._apply_recent_styling(target_row)
            return True

        except Exception as e:
            print(f"Error highlighting row by ID {product_id}: {e}")
            return False

    # --- Theming and Styling (Enhanced) ---

    def apply_theme(self):
        """Apply current theme to table with enhanced styling."""
        bg_color = get_color('background')
        text_color = get_color('text')
        border_color = get_color('border')
        highlight_color = get_color('highlight')
        secondary_color = get_color('secondary', QColor(bg_color).lighter(110).name())
        header_bg = get_color('header', QColor(bg_color).lighter(115).name())

        if hasattr(self.item_delegate, 'set_theme_colors'):
            self.item_delegate.set_theme_colors(bg=bg_color, text=text_color, highlight=highlight_color)
        if hasattr(self.numeric_delegate, 'set_theme_colors'):
            self.numeric_delegate.set_theme_colors(bg=bg_color, text=text_color, highlight=highlight_color)

        table_style = f"""
            QTableWidget#productsTableView {{
                background-color: {bg_color};
                alternate-background-color: {secondary_color};
                gridline-color: transparent;
                border: 1px solid {border_color};
                border-radius: 6px;
                font-size: 14px;
            }}
            QTableWidget#productsTableView::item {{
                padding: 5px 8px;
                border: none;
                color: {text_color};
            }}
            QHeaderView::section {{
                background-color: {header_bg};
                color: {text_color};
                padding: 8px 10px;
                border: none;
                border-bottom: 1px solid {border_color};
                border-right: 1px solid {border_color};
                font-weight: bold;
                font-size: 14px;
            }}
            QHeaderView::section:last {{
                 border-right: none;
            }}
            QTableWidget#productsTableView::item:selected {{
                background-color: {highlight_color};
                color: {bg_color};
            }}
            QTableWidget#productsTableView:focus {{ outline: none; }}
            QTableWidget#productsTableView::item:focus {{ outline: none; border: none; }}
            QTableWidget#productsTableView::item:hover:!selected {{
                background-color: {QColor(highlight_color).lighter(160).name()}40;
            }}
            QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0px; border-radius: 4px; }}
            QScrollBar::handle:vertical {{ background: {get_color('button')}; min-height: 30px; border-radius: 4px; }}
            QScrollBar::handle:vertical:hover {{ background: {highlight_color}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: transparent; height: 0px; width: 0px; }}
            QScrollBar:horizontal {{ background: transparent; height: 8px; margin: 0px; border-radius: 4px; }}
            QScrollBar::handle:horizontal {{ background: {get_color('button')}; min-width: 30px; border-radius: 4px; }}
            QScrollBar::handle:horizontal:hover {{ background: {highlight_color}; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; height: 0px; width: 0px; }}
            QScrollBar::corner {{ background: {bg_color}; border: none; }}
            QHeaderView {{ background-color: {bg_color}; }}
        """
        self.table.setStyleSheet(table_style)

        empty_palette = self.empty_label.palette()
        empty_palette.setColor(QPalette.WindowText, QColor(text_color).lighter(130))
        self.empty_label.setPalette(empty_palette)

        # Apply row styling with minimal redraws
        self.table.blockSignals(True)
        try:
            text_qcolor = QColor(text_color)
            for row in range(self.table.rowCount()):
                # Skip styling if no items in row
                if self.table.item(row, 0) is None:
                    continue

                row_bg = QColor(secondary_color) if row % 2 else QColor(bg_color)
                self._apply_row_styling(row, row_bg, text_qcolor)
        finally:
            self.table.blockSignals(False)

        # Ensure viewport has correct background
        self.table.viewport().setStyleSheet(f"background-color: {bg_color};")

    def _apply_row_styling(self, row, bg_color, text_color):
        """Apply styling to all cells in a row efficiently."""
        for col in range(self.COLUMN_COUNT):
            item = self.table.item(row, col)
            if item:
                current_bg = item.background().color()
                current_text = item.foreground().color()

                # Only update if colors don't match (performance optimization)
                if current_bg != bg_color:
                    item.setBackground(bg_color)
                if current_text != text_color:
                    item.setForeground(text_color)

    def resizeEvent(self, event):
        """Handle resize events efficiently."""
        super().resizeEvent(event)
        # Only adjust columns if really needed - avoids unnecessary calculations
        if event.size().width() != event.oldSize().width():
            self.adjust_column_widths()
        # Update empty label position always
        QTimer.singleShot(0, self._update_empty_label_geometry)

    def _update_empty_label_geometry(self):
        """Center the empty label over the table viewport with improved positioning."""
        if not self.empty_label or not self.isVisible():
            return

        # Get the actual viewport area (accounting for headers and scrollbars)
        viewport_rect = self.table.viewport().rect()

        # Get the global position of the viewport
        viewport_global_pos = self.table.viewport().mapToGlobal(viewport_rect.topLeft())

        # Map this global position back to our coordinates
        viewport_local_pos = self.mapFromGlobal(viewport_global_pos)

        # Create a rect in our coordinate system
        adjusted_rect = QRect(
            viewport_local_pos.x(),
            viewport_local_pos.y(),
            viewport_rect.width(),
            viewport_rect.height()
        )

        # Get the label's preferred size
        label_size = self.empty_label.sizeHint()

        # Calculate centered position
        x = adjusted_rect.x() + (adjusted_rect.width() - label_size.width()) // 2
        y = adjusted_rect.y() + (adjusted_rect.height() - label_size.height()) // 3  # Slightly above center

        # Set the geometry ensuring it stays within bounds
        x = max(adjusted_rect.left(), x)
        y = max(adjusted_rect.top(), y)
        width = min(label_size.width(), adjusted_rect.width())
        height = min(label_size.height(), adjusted_rect.height())

        self.empty_label.setGeometry(x, y, width, height)

        # Make sure it's visible and on top
        if self.empty_label.isVisible():
            self.empty_label.raise_()

    def showEvent(self, event):
        """Called when the widget is shown."""
        super().showEvent(event)
        # Ensure layout and empty label positioning is correct
        QTimer.singleShot(0, self._update_empty_label_geometry)
        # Trigger column width adjustment after widget is fully visible
        QTimer.singleShot(100, self.adjust_column_widths)

    # --- Data Handling and Updates (Optimized) ---

    def update_table_data(self, products):
        """Update table efficiently without triggering edit events"""
        # Already being updated - prevent recursion
        if hasattr(self, '_is_updating_table') and self._is_updating_table:
            return False

        self._is_updating_table = True

        # Check if signals are already blocked externally
        externally_blocked = self.table.signalsBlocked()

        try:
            # Save current state
            scroll_value = self.table.verticalScrollBar().value()
            selected_ids = self._save_selection()
            sort_settings = self._get_current_sort()

            # Only block signals if not already blocked
            if not externally_blocked:
                self.table.blockSignals(True)

            # Batch update for better performance
            self.table.setUpdatesEnabled(False)
            self.table.setSortingEnabled(False)

            # Handle empty state
            if not products:
                self.table.setRowCount(0)
                self.empty_label.setVisible(True)
                self._update_empty_label_geometry()
                return True

            # Hide empty label if we have products
            self.empty_label.setVisible(False)

            # Rest of your existing update code...
            current_row_count = self.table.rowCount()
            needed_row_count = len(products)
            self.table.setRowCount(needed_row_count)

            # Update data in all rows
            for row, prod in enumerate(products):
                self._populate_row(row, prod)

            # Re-enable features and restore state
            self.table.setUpdatesEnabled(True)
            self.table.setSortingEnabled(True)

            # Apply sort settings
            if sort_settings['column'] >= 0:
                self.table.horizontalHeader().setSortIndicator(
                    sort_settings['column'], sort_settings['order']
                )

            # Restore scroll and selection after processing events
            QTimer.singleShot(10, lambda: self.table.verticalScrollBar().setValue(scroll_value))
            QTimer.singleShot(20, lambda ids=selected_ids: self._restore_selection(ids))
            QTimer.singleShot(50, self.adjust_column_widths)

            return True

        except Exception as e:
            print(f"Error updating table: {e}")
            import traceback
            print(traceback.format_exc())
            return False

        finally:
            # Only unblock signals if we blocked them (not if they were blocked externally)
            if not externally_blocked:
                self.table.blockSignals(False)
            self._is_updating_table = False

    def update_single_product(self, product: Union[Dict, Tuple]) -> bool:
        """Efficiently update a single product row with minimal redrawing."""
        try:
            # Now using 'id' instead of 'parcode' as the primary key
            product_id_str = str(product['id'] if isinstance(product, dict) else product[0])
        except (IndexError, KeyError, TypeError) as e:
            self._handle_error(e, "update_single_product: invalid product data")
            return False

        # Find the row to update
        row_to_update = -1
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, self.COL_ID)
            if id_item and id_item.text() == product_id_str:
                row_to_update = row
                break

        if row_to_update >= 0:
            # Use minimal updates
            self.table.blockSignals(True)
            try:
                self._populate_row(row_to_update, product)

                # Update row styling efficiently
                bg_color = QColor(get_color('background'))
                secondary_color = QColor(get_color('secondary', QColor(bg_color).lighter(110).name()))
                row_bg = secondary_color if row_to_update % 2 else bg_color
                text_color = QColor(get_color('text'))

                self._apply_row_styling(row_to_update, row_bg, text_color)
            finally:
                self.table.blockSignals(False)
            return True
        return False

    def append_product(self, product: Union[Dict, Tuple]) -> bool:
        """Append a new product to the beginning of the table."""
        try:
            # If table was previously empty, ensure empty label is hidden
            if self.table.rowCount() == 0:
                self.empty_label.setVisible(False)

            # Insert row efficiently
            self.table.insertRow(0)
            self.table.blockSignals(True)
            try:
                self._populate_row(0, product)
                # Apply special styling to emphasize the new product
                self._apply_recent_styling(0, immediate=True)
            finally:
                self.table.blockSignals(False)

            # Ensure column widths are correct
            self.adjust_column_widths()
            # Scroll to make the new row visible
            self.table.scrollToTop()
            return True
        except Exception as e:
            self._handle_error(e, "append_product")
            # Clean up if the row was added but there was an error
            if self.table.rowCount() > 0:
                try:
                    self.table.removeRow(0)
                except Exception:
                    pass

            # Show empty label if table is now empty
            if self.table.rowCount() == 0:
                self.empty_label.setVisible(True)
                self._update_empty_label_geometry()
            return False

    def _populate_row(self, row: int, product: Union[Dict, Tuple]):
        """Efficiently populate a table row with product data, with better error handling.
        Uses parcode in the first column instead of database ID."""
        if row < 0 or row >= self.table.rowCount():
            return

        try:
            is_dict = isinstance(product, dict)

            # --- Parcode (First Column) ---
            # Get parcode value from the product data
            if is_dict:
                # For dictionary format
                parcode_value = str(product.get('parcode', ''))
            else:
                # For tuple format - find the parcode field position
                # Try common positions or search through the tuple
                if len(product) > 15 and isinstance(product[15], str):
                    # Assuming parcode might be at index 15
                    parcode_value = str(product[15])
                elif 'parcode' in dir(product) and hasattr(product, 'parcode'):
                    # If it's a named tuple or has attributes
                    parcode_value = str(product.parcode)
                else:
                    # Fallback: try to find a string that looks like a part code
                    # or use the ID as a last resort
                    parcode_value = str(product[0]) if len(product) > 0 else ''
                    for item in product:
                        if isinstance(item, str) and (len(item) >= 4 or re.match(r'^[A-Z0-9\-]+$', item)):
                            parcode_value = item
                            break

            # Update the parcode item in the first column
            id_item = self.table.item(row, self.COL_ID)
            if not id_item:
                id_item = QTableWidgetItem(parcode_value)
                id_item.setFlags(id_item.flags() | Qt.ItemIsEditable)  # Make parcode editable
                id_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, self.COL_ID, id_item)
            elif id_item.text() != parcode_value:
                id_item.setText(parcode_value)

            # --- Product Name ---
            name_raw = product.get('product_name', '') if is_dict else (product[2] if len(product) > 2 else '')
            name_text = str(name_raw) if name_raw not in [None, ""] else "-"
            name_item = self.table.item(row, self.COL_NAME)
            if not name_item:
                name_item = QTableWidgetItem(name_text)
                name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                name_item.setToolTip(name_text)
                self.table.setItem(row, self.COL_NAME, name_item)
            else:
                name_item.setText(name_text)
                name_item.setToolTip(name_text)

            # --- Manufacturer --- (CHANGED FROM COMPATIBLE MODELS)
            manufacturer_raw = product.get('manufacturer', '') if is_dict else (
                product[14] if len(product) > 14 else '')
            manufacturer_text = str(manufacturer_raw) if manufacturer_raw not in [None, ""] else "-"

            # Use COL_MANUFACTURER instead of COL_MODELS
            manufacturer_item = self.table.item(row, self.COL_MANUFACTURER)
            if not manufacturer_item:
                manufacturer_item = QTableWidgetItem(manufacturer_text)
                manufacturer_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                manufacturer_item.setToolTip(manufacturer_text)
                self.table.setItem(row, self.COL_MANUFACTURER, manufacturer_item)
            else:
                manufacturer_item.setText(manufacturer_text)
                manufacturer_item.setToolTip(manufacturer_text)

            # --- Quantity ---
            qty_raw = product.get('quantity', 0) if is_dict else (product[3] if len(product) > 3 else 0)
            qty_value = "0"
            try:
                qty_value = str(int(qty_raw)) if qty_raw is not None else "0"
            except (ValueError, TypeError):
                qty_value = "0"

            qty_item = self.table.item(row, self.COL_QTY)
            if not qty_item:
                qty_item = QTableWidgetItem(qty_value)
                qty_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, self.COL_QTY, qty_item)
            else:
                qty_item.setText(qty_value)

            # --- Price ---
            price_raw = product.get('price', 0.0) if is_dict else (product[4] if len(product) > 4 else 0.0)
            price_value = "0.00"
            try:
                price_value = f"{float(price_raw):.2f}" if price_raw is not None else "0.00"
            except (ValueError, TypeError):
                price_value = "0.00"

            price_item = self.table.item(row, self.COL_PRICE)
            if not price_item:
                price_item = QTableWidgetItem(price_value)
                price_item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, self.COL_PRICE, price_item)
            else:
                price_item.setText(price_value)

        except Exception as e:
            # Handle cell population errors gracefully
            print(f"Error populating row {row}: {e}")
            import traceback
            print(traceback.format_exc())

            # Create error indicators if needed
            for col in range(self.COLUMN_COUNT):
                err_item = self.table.item(row, col)
                if not err_item:
                    err_item = QTableWidgetItem("Error")
                    err_item.setForeground(QColor("red"))
                    err_item.setFlags(err_item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row, col, err_item)

    # --- Selection state management helpers ---

    def _save_selection(self) -> List[str]:
        """Save current selection IDs with improved error handling."""
        selected_ids = []
        try:
            selection_mode = self.table.selectionMode()
            if selection_mode == QAbstractItemView.MultiSelection:
                indices = self.table.selectionModel().selectedRows()
            else:
                indices = self.table.selectedIndexes()

            processed_rows = set()
            for index in indices:
                row = index.row()
                if row not in processed_rows and row < self.table.rowCount():
                    id_item = self.table.item(row, self.COL_ID)
                    if id_item and id_item.text():
                        selected_ids.append(id_item.text())
                    processed_rows.add(row)
        except Exception as e:
            print(f"Error saving selection: {e}")

        return selected_ids

    def _restore_selection(self, selected_ids: List[str]):
        """Restore selection after table update with improved error handling."""
        if not selected_ids or self.table.rowCount() == 0:
            return

        try:
            self.table.blockSignals(True)

            selection_model = self.table.selectionModel()
            if selection_model:
                selection_model.clear()

            select_mode = self.table.selectionMode()

            # Process in two passes for better UI feedback
            # First pass: find the rows to select
            rows_to_select = []
            for row in range(self.table.rowCount()):
                id_item = self.table.item(row, self.COL_ID)
                if id_item and id_item.text() in selected_ids:
                    rows_to_select.append(row)

                    # Optimization for single selection
                    if select_mode == QAbstractItemView.SingleSelection and len(rows_to_select) > 0:
                        break

            # Second pass: perform the selection
            if rows_to_select:
                for row in rows_to_select:
                    if select_mode == QAbstractItemView.MultiSelection:
                        # In multi-selection mode, select the entire row
                        selection_model.select(
                            self.table.model().index(row, 0),
                            QItemSelectionModel.Select | QItemSelectionModel.Rows
                        )
                    else:
                        # In single selection mode, just select the first matching ID
                        self.table.setCurrentCell(row, self.COL_NAME)
                        break
        except Exception as e:
            print(f"Error restoring selection: {e}")
        finally:
            self.table.blockSignals(False)

    def _get_current_sort(self) -> Dict[str, Any]:
        """Get current sort settings, safely handling edge cases."""
        try:
            header = self.table.horizontalHeader()
            if header:
                return {
                    'column': header.sortIndicatorSection(),
                    'order': header.sortIndicatorOrder()
                }
        except Exception as e:
            print(f"Error getting sort settings: {e}")

        # Default sort settings if we couldn't get the current ones
        return {'column': 1, 'order': 0}  # Default to sorting by name ascending (column 1 now that category is removed)

    # --- Highlighting and Formatting (Optimized) ---

    def highlight_matching_text(self, search_text):
        """
        Highlight cells containing search text with improved visual feedback.
        Enhanced to show the match quality based on search term placement.
        """
        if not search_text:
            self._reset_cell_formatting()
            return

        search_text_lower = search_text.strip().lower()
        search_words = search_text_lower.split() if ' ' in search_text_lower else [search_text_lower]

        # Block signals once for the entire operation
        self.table.blockSignals(True)
        try:
            self._reset_cell_formatting()

            # Create different highlight colors based on match quality
            exact_match_color = QColor(get_color('highlight'))  # Strong highlight for exact matches

            # Partial match colors with varying opacity
            strong_partial_match = QColor(get_color('highlight'))
            strong_partial_match.setAlpha(120)  # More visible for better matches

            weak_partial_match = QColor(get_color('highlight'))
            weak_partial_match.setAlpha(70)  # Less visible for weaker matches

            # Track first match for scrolling
            first_match_row = -1
            best_match_row = -1
            best_match_score = -1

            # Text color for highlighted items
            text_color = QColor(get_color('text'))

            # Search only in relevant columns
            search_columns = [self.COL_NAME, self.COL_MANUFACTURER]

            for row in range(self.table.rowCount()):
                row_score = 0
                row_has_match = False
                row_has_exact_match = False

                for col in search_columns:
                    item = self.table.item(row, col)
                    if not item:
                        continue

                    cell_text = item.text().lower()
                    match_quality = 0

                    # Check for exact matches first
                    if cell_text == search_text_lower:
                        match_quality = 3  # Highest quality
                        row_has_exact_match = True
                        item.setBackground(QBrush(exact_match_color))
                        row_score += 100

                    # Check for starts-with matches (second priority)
                    elif cell_text.startswith(search_text_lower):
                        match_quality = 2  # High quality
                        item.setBackground(QBrush(strong_partial_match))
                        row_score += 50

                    # Check for contains matches (third priority)
                    elif search_text_lower in cell_text:
                        match_quality = 1  # Medium quality
                        item.setBackground(QBrush(weak_partial_match))
                        row_score += 20

                    # Check for multi-word matches (all words appear but not necessarily together)
                    elif len(search_words) > 1 and all(word in cell_text for word in search_words):
                        match_quality = 1  # Medium quality
                        item.setBackground(QBrush(weak_partial_match))
                        row_score += 30

                    # Apply styling based on match quality
                    if match_quality > 0:
                        row_has_match = True
                        item.setForeground(text_color)

                        # Emphasize the matched part with font (for exact or starts-with)
                        if match_quality >= 2:
                            font = item.font()
                            font.setBold(True)
                            item.setFont(font)

                # Track first and best match
                if row_has_match:
                    if first_match_row == -1:
                        first_match_row = row

                    if row_score > best_match_score:
                        best_match_score = row_score
                        best_match_row = row

                    # For exact matches, also highlight the row number in the vertical header
                    if row_has_exact_match and self.table.verticalHeader().isVisible():
                        try:
                            # This assumes the vertical header has items that can be styled
                            header_item = self.table.verticalHeaderItem(row)
                            if header_item:
                                header_font = header_item.font()
                                header_font.setBold(True)
                                header_item.setFont(header_font)
                                header_item.setBackground(QBrush(exact_match_color))
                        except Exception:
                            pass

            # Scroll to the best match if found, or first match otherwise
            if best_match_row != -1:
                target_row = best_match_row
            elif first_match_row != -1:
                target_row = first_match_row
            else:
                return

            # Use deferred scroll to allow UI to update
            QTimer.singleShot(0, lambda row=target_row:
            self.table.scrollToItem(self.table.item(row, 0),
                                    QAbstractItemView.PositionAtCenter))

            # Highlight the entire row of the best match for better visibility
            if best_match_row != -1:
                QTimer.singleShot(50, lambda row=best_match_row: self._highlight_best_match_row(row))

        finally:
            self.table.blockSignals(False)

    def _highlight_best_match_row(self, row):
        """Add subtle highlighting to the best match row for better visibility"""
        try:
            # Apply a subtle background to all cells in the row
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    # Only change background if it hasn't already been highlighted
                    if item.background().color().alpha() < 50:
                        highlight = QColor(get_color('secondary'))
                        highlight.setAlpha(40)  # Very subtle
                        item.setBackground(highlight)

                    # Make the text bold in the name column for emphasis
                    if col == self.COL_NAME:
                        font = item.font()
                        if not font.bold():
                            font.setBold(True)
                            item.setFont(font)

            # Select the row (without changing the current item)
            current_item = self.table.currentItem()
            self.table.selectRow(row)
            if current_item:
                self.table.setCurrentItem(current_item)

        except Exception as e:
            print(f"Error highlighting best match row: {e}")

    def _reset_cell_formatting(self):
        """Reset all cell formatting thoroughly, ensuring ALL highlight styling is removed."""
        # Skip if table is empty
        if self.table.rowCount() == 0:
            return

        bg_color = QColor(get_color('background'))
        secondary_color = QColor(get_color('secondary', QColor(bg_color).lighter(110).name()))
        text_color = QColor(get_color('text'))

        # Block signals for performance
        self.table.blockSignals(True)
        try:
            for row in range(self.table.rowCount()):
                # Determine the correct background color for this row (alternating)
                row_bg = secondary_color if row % 2 else bg_color

                # Apply to all cells in the row
                for col in range(self.COLUMN_COUNT):
                    item = self.table.item(row, col)
                    if item:
                        # Reset background and text color
                        item.setBackground(QBrush(row_bg))
                        item.setForeground(QBrush(text_color))

                        # Reset font properties - ensure bold is removed
                        font = item.font()
                        if font.bold():
                            font.setBold(False)
                            item.setFont(font)

                        # Clear any tooltip that might have been set during search
                        if col != self.COL_NAME and col != self.COL_MANUFACTURER:
                            item.setToolTip("")

            # Reset any header formatting in vertical header
            if self.table.verticalHeader().isVisible():
                for row in range(self.table.rowCount()):
                    header_item = self.table.verticalHeaderItem(row)
                    if header_item:
                        header_item.setBackground(QBrush())  # Clear background
                        font = header_item.font()
                        if font.bold():
                            font.setBold(False)
                            header_item.setFont(font)

            # Ensure any selection is maintained
            self.table.update()

            # Reset any highlight settings in delegates if they exist
            if hasattr(self, 'item_delegate') and hasattr(self.item_delegate, 'set_highlight_row'):
                self.item_delegate.set_highlight_row(None, None)  # Clear any row highlight

            if hasattr(self, 'numeric_delegate') and hasattr(self.numeric_delegate, 'set_highlight_row'):
                self.numeric_delegate.set_highlight_row(None, None)  # Clear any row highlight

        finally:
            self.table.blockSignals(False)

    # --- Visual Highlighting Effects (Improved) ---

    def _reset_row_styling(self, row: int):
        """Reset row styling by removing highlight from delegates."""
        if row < 0 or row >= self.table.rowCount():
            return

        try:
            # Remove highlight from delegates
            self.item_delegate.set_highlight_row(row, None)
            self.numeric_delegate.set_highlight_row(row, None)

            # Reset font boldness
            name_item = self.table.item(row, self.COL_NAME)
            if name_item and name_item.font().bold():
                font = name_item.font()
                font.setBold(False)
                name_item.setFont(font)

            # Force redraw
            self.table.update()
        except Exception as e:
            print(f"Error resetting style for row {row}: {e}")

    # --- Utility Methods ---

    def _handle_error(self, error, context="operation", notify_user=True):
        """
        Consistent error handling for table operations.

        Args:
            error: The exception that occurred
            context: Description of what failed
            notify_user: Whether to show error to user
        """
        error_msg = f"Error in {context}: {str(error)}"
        print(error_msg)

        import traceback
        print(traceback.format_exc())

        # Ensure the table is in a usable state
        if self.table.signalsBlocked():
            self.table.blockSignals(False)

        if not self.table.updatesEnabled():
            self.table.setUpdatesEnabled(True)

        # Optionally display in the empty label
        if notify_user:
            try:
                error_text = self.translator.t('table_error', error_msg[:100] + '...')
            except:
                error_text = f"Table Error: {error_msg[:100]}..."

            self.empty_label.setText(error_text)
            self.empty_label.setVisible(True)
            self.empty_label.raise_()

    def get_current_view_data(self) -> List[Union[Dict, Tuple]]:
        """
        Retrieves the data currently displayed in the table respecting sorting.
        Returns data primarily as tuples reconstructed from table cells.
        Updated to handle modified column structure.
        """
        data = []
        try:
            for row in range(self.table.rowCount()):
                row_items = []
                all_valid = True

                for col in range(self.COLUMN_COUNT):
                    item = self.table.item(row, col)
                    if not item:
                        all_valid = False
                        break
                    row_items.append(item)

                if all_valid:
                    try:
                        p_id = int(row_items[self.COL_ID].text())
                        name = row_items[self.COL_NAME].text()
                        manufacturer = row_items[self.COL_MANUFACTURER].text()  # Changed from COL_MODELS
                        qty = int(row_items[self.COL_QTY].text())
                        price = float(row_items[self.COL_PRICE].text())

                        # Reconstruct tuple with the updated structure:
                        data.append((p_id, "", name, qty, price, "", manufacturer))
                    except (ValueError, TypeError, AttributeError) as e:
                        print(f"Error converting data from table row {row}: {e}")
                else:
                    print(f"Skipping row {row} in get_current_view_data due to missing items.")
        except Exception as e:
            self._handle_error(e, "get_current_view_data", False)

        return data

    def _apply_recent_styling(self, row: int, immediate: bool = False):
        """Apply special styling to a row using delegate highlighting system."""
        if row < 0 or row >= self.table.rowCount():
            return

        try:
            # Cancel any running animations
            if hasattr(self, '_highlight_timer') and self._highlight_timer:
                self._highlight_timer.stop()

            # Store the row being highlighted
            self._highlight_animation_row = row

            # Create amber highlight color with good opacity
            highlight_color = QColor(255, 193, 7, 120)  # Amber with good opacity

            # Apply highlight through delegates instead of item backgrounds
            self.item_delegate.set_highlight_row(row, highlight_color)
            self.numeric_delegate.set_highlight_row(row, highlight_color)

            # Bold the name cell
            name_item = self.table.item(row, self.COL_NAME)
            if name_item:
                font = name_item.font()
                font.setBold(True)
                name_item.setFont(font)

            # Force redraw of the table row
            self.table.update()

            if immediate:
                # Remove highlight immediately if requested
                self._reset_row_styling(row)
            else:
                # Set timer to clear highlight after delay
                self._highlight_timer = QTimer(self)
                self._highlight_timer.setSingleShot(True)
                self._highlight_timer.timeout.connect(lambda: self._reset_row_styling(row))
                self._highlight_timer.start(4000)  # 4 seconds

        except Exception as e:
            self._handle_error(e, "highlight styling", False)
            self._reset_row_styling(row)