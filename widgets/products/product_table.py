from PyQt5.QtWidgets import (QAbstractItemView, QHeaderView,
                             QTableWidget, QTableWidgetItem, QFrame, QVBoxLayout,
                             QWidget, QAbstractButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor
from themes import get_color
from .components.table_delegates import ThemedNumericDelegate, ThemedItemDelegate
from translations.car_parts_info_translations import translate_category, translate_compatible_models


class ProductsTable(QFrame):
    """Enhanced table widget for products with proper styling"""

    cellChanged = pyqtSignal(int, int)  # Row, column

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.setObjectName("tableContainer")

        # Setup layout with no margins for better scrollbar alignment
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
        layout.setSpacing(0)  # Remove spacing

        # Create table widget
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.update_headers()

        # Hide vertical header completely - this removes row numbers
        self.table.verticalHeader().setVisible(False)

        # Try to hide the corner button if we can find it
        try:
            corner_button = self.table.findChild(QAbstractButton)
            if corner_button:
                corner_button.hide()
        except:
            pass  # Ignore any errors

        # Set row height to make cells larger
        self.table.verticalHeader().setDefaultSectionSize(40)  # Taller rows

        # Custom column widths instead of stretch
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)

        # Configure selection and interaction behavior
        self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.cellChanged.connect(self._on_cell_changed)
        self.table.setAlternatingRowColors(True)

        # Set edit triggers - make it easier to enter edit mode
        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked |
            QAbstractItemView.EditKeyPressed
        )

        # Modern scrollbar configuration
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollMode(
            QAbstractItemView.ScrollPerPixel)  # Smooth scrolling
        self.table.setHorizontalScrollMode(
            QAbstractItemView.ScrollPerPixel)  # Smooth scrolling

        # Remove grid for a sleeker look
        self.table.setShowGrid(False)

        # Disable the corner button - safely try another approach
        try:
            self.table.setCornerButtonEnabled(False)
        except:
            pass  # Ignore any errors if this method doesn't exist

        # Apply themed delegates for elegant editing experience
        self.item_delegate = ThemedItemDelegate()
        self.numeric_delegate = ThemedNumericDelegate()

        # Apply delegates to different column types
        self.table.setItemDelegateForColumn(1, self.item_delegate)  # Category
        self.table.setItemDelegateForColumn(2, self.item_delegate)  # Product name
        self.table.setItemDelegateForColumn(3, self.item_delegate)  # Compatible models (FIXED)
        self.table.setItemDelegateForColumn(4, self.numeric_delegate)  # Quantity
        self.table.setItemDelegateForColumn(5, self.numeric_delegate)  # Price
        # Add table to layout
        layout.addWidget(self.table)

        # Apply initial styling
        self.apply_theme()

    def update_headers(self):
        """Update table headers with current translations"""
        headers = [
            self.translator.t('id'),
            self.translator.t('category'),
            self.translator.t('product_name'),
            self.translator.t('compatible_models'),
            self.translator.t('quantity'),
            self.translator.t('price')
        ]
        self.table.setHorizontalHeaderLabels(headers)

    def _on_cell_changed(self, row, column):
        """Internal handler for cell changes that emits the public signal"""
        self.cellChanged.emit(row, column)

    def update_table_data(self, products):
        """Update table with the given products data"""
        try:
            # Save current scroll position
            scroll_value = self.table.verticalScrollBar().value()

            self.table.blockSignals(True)
            self.table.setSortingEnabled(False)

            # Set the row count
            self.table.setRowCount(len(products))

            # Populate the data row by row
            for row, prod in enumerate(products):
                try:
                    # ID column (non-editable) - parcode is at index 0
                    id_item = QTableWidgetItem(str(prod[0]))
                    id_item.setFlags(id_item.flags() ^ Qt.ItemIsEditable)
                    id_item.setTextAlignment(Qt.AlignCenter)  # Center align ID
                    self.table.setItem(row, 0, id_item)

                    category_text = str(prod[1]) if len(prod) > 1 and prod[1] not in [None, ""] else "-"
                    try:
                        # Translate category
                        category_text = translate_category(category_text, self.translator.language)
                    except Exception as e:
                        print(f"Error translating category: {e}")
                    category_item = QTableWidgetItem(category_text)
                    category_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.table.setItem(row, 1, category_item)

                    # Product name - left align - product_name is at index 2
                    name_text = str(prod[2]) if len(prod) > 2 and prod[2] not in [None, ""] else "-"
                    name_item = QTableWidgetItem(name_text)
                    name_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.table.setItem(row, 2, name_item)

                    models_text = str(prod[6]) if len(prod) > 6 and prod[6] not in [None, ""] else "-"
                    try:
                        # Translate compatible models
                        models_text = translate_compatible_models(models_text, self.translator.language)
                    except Exception as e:
                        print(f"Error translating models: {e}")
                    models_item = QTableWidgetItem(models_text)
                    models_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                    self.table.setItem(row, 3, models_item)

                    # Quantity - center align - quantity is at index 3
                    qty_value = "0"
                    if len(prod) > 3 and prod[3] is not None:
                        try:
                            qty_value = str(int(prod[3]))
                        except (ValueError, TypeError):
                            qty_value = "0"
                    qty_item = QTableWidgetItem(qty_value)
                    qty_item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, 4, qty_item)

                    # Price - right align - price is at index 4

                    price_value = "0.00"
                    if len(prod) > 4 and prod[4] is not None:
                        try:
                            price_value = f"{float(prod[4]):.2f}"
                        except (ValueError, TypeError):
                            price_value = "0.00"
                    price_item = QTableWidgetItem(price_value)
                    price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.table.setItem(row, 5, price_item)

                except Exception as e:
                    print(f"Error processing row {row}: {e}")
                    # Create empty cells for this row to avoid table corruption
                    for col in range(6):  # Now 6 columns
                        self.table.setItem(row, col, QTableWidgetItem("-"))

            # Re-enable sorting and signals after all data is loaded
            self.table.setSortingEnabled(True)
            self.table.blockSignals(False)

            # Restore scroll position if possible
            self.table.verticalScrollBar().setValue(
                min(scroll_value, self.table.verticalScrollBar().maximum()))

            return True
        except Exception as e:
            print(f"Error updating table: {e}")
            import traceback
            print(traceback.format_exc())
            return False

    def adjust_column_widths(self):
        """Set custom column widths based on data importance"""
        # Total width calculation (approximate)
        total_width = self.width() - 40  # Subtract scrollbar width and some padding

        # Column width distribution (percentages)
        # ID: 8%, Category: 12%, Product Name: 32%, Compatible Models: 28%, Qty: 10%, Price: 10%
        col_widths = [8, 12, 32, 28, 10, 10]  # Made price column smaller

        # Apply the widths
        for i, width_percent in enumerate(col_widths):
            width = int(total_width * width_percent / 100)
            self.table.setColumnWidth(i, width)

    def set_selection_mode(self, enable_multi_select):
        """Toggle between single cell and multi-row selection modes"""
        if enable_multi_select:
            # Enable row selection mode
            self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.table.setSelectionMode(QAbstractItemView.MultiSelection)
            self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        else:
            # Restore normal mode
            self.table.setSelectionBehavior(QAbstractItemView.SelectItems)
            self.table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.table.setEditTriggers(QAbstractItemView.DoubleClicked |
                                       QAbstractItemView.EditKeyPressed)
            self.table.clearSelection()

    def get_selected_rows_data(self):
        """Get data from selected rows for deletion

        Returns:
            list: List of tuples (id, name) for selected rows
        """
        selected_rows = self.table.selectionModel().selectedRows()
        product_details = []

        for index in selected_rows:
            row = index.row()
            try:
                id_item = self.table.item(row, 0)
                name_item = self.table.item(row, 1)  # Now name is in column 1
                if id_item and name_item and id_item.text().isdigit():
                    product_details.append((
                        int(id_item.text()),
                        name_item.text() or self.translator.t('unnamed_product')
                    ))
            except Exception as e:
                print(f"Error parsing row {row}: {e}")

        return product_details

    def highlight_product(self, search_text):
        """Scroll to and highlight matching product"""
        search_text = search_text.lower()
        for row in range(self.table.rowCount()):
            product_item = self.table.item(row, 4)
            if product_item and search_text in product_item.text().lower():
                self.table.scrollToItem(product_item)
                self.table.blockSignals(True)
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item:
                        item.setBackground(QColor(get_color('highlight')))
                        item.setForeground(QColor(get_color('background')))
                self.table.blockSignals(False)
                return True
        return False

    def apply_theme(self):
        """Apply current theme to table with enhanced styling"""
        bg_color = get_color('background')
        text_color = get_color('text')
        border_color = get_color('border')
        highlight_color = get_color('highlight')
        secondary_color = get_color('secondary')

        # Table styling with refined cell appearance
        table_style = f"""
            QTableWidget {{
                background-color: {bg_color};
                alternate-background-color: {secondary_color};
                gridline-color: {border_color};
                border: 2px solid {border_color};
                border-radius: 6px;
                font-size: 14px;
            }}
            QTableWidget::item {{
                padding: 0px;
                border: none;
            }}
            QHeaderView::section {{
                background-color: {get_color('header')};
                color: {text_color};
                padding: 10px;
                border: none;
                border-right: 1px solid {border_color};
                font-weight: bold;
                font-size: 15px;
            }}
            QTableWidget::item:selected {{
                background-color: {highlight_color};
                color: {bg_color};
            }}
            /* Completely removes focus indicators */
            QTableView:focus {{
                outline: none;
            }}
            QTableView::item:focus {{
                outline: none;
                border: none;
            }}
            /* Smoother hover effect */
            QTableWidget::item:hover:!selected {{
                background-color: {highlight_color}25;
            }}

            /* Modern scrollbar styling */
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background: {get_color('button')};
                min-height: 30px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {highlight_color};
            }}
            QScrollBar::add-line:vertical, 
            QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, 
            QScrollBar::sub-page:vertical {{
                background: transparent;
                height: 0px;
                width: 0px;
            }}
            QScrollBar:horizontal {{
                background: transparent;
                height: 8px;
                margin: 0px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal {{
                background: {get_color('button')};
                min-width: 30px;
                border-radius: 4px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background: {highlight_color};
            }}
            QScrollBar::add-line:horizontal, 
            QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal, 
            QScrollBar::sub-page:horizontal {{
                background: transparent;
                height: 0px;
                width: 0px;
            }}
            /* Corner styling */
            QScrollBar::corner {{
                background: {bg_color};
                border: none;
            }}
            QHeaderView {{ 
                background-color: {bg_color}; 
            }}
        """
        self.table.setStyleSheet(table_style)

        # BLOCK SIGNALS DURING VISUAL UPDATE
        self.table.blockSignals(True)
        try:
            # Update existing items' colors without triggering changes
            text_qcolor = QColor(text_color)
            for row in range(self.table.rowCount()):
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and item.foreground().color() != text_qcolor:
                        item.setForeground(text_qcolor)
        finally:
            self.table.blockSignals(False)

        # Background fallbacks
        self.table.viewport().setStyleSheet(f"background: {bg_color};")
        for child in self.table.findChildren(QWidget):
            child.setStyleSheet(f"background-color: {bg_color}; border: none;")

    def resizeEvent(self, event):
        """Handle resize events to adjust column widths"""
        super().resizeEvent(event)
        self.adjust_column_widths()


def highlight_matching_text(self, search_text):
    """
    Highlight cells containing the search text

    Args:
        search_text: Text to highlight in the table
    """
    if not search_text:
        return

    search_text = search_text.lower()

    # Reset any previous formatting
    self._reset_cell_formatting()

    from PyQt5.QtGui import QBrush, QColor
    from themes import get_color

    # Get highlight color with reduced opacity for better readability
    highlight_color = QColor(get_color('highlight'))
    highlight_color.setAlpha(120)  # 47% opacity for subtle highlighting
    highlight_brush = QBrush(highlight_color)

    matching_rows = []

    # Search all table content
    for row in range(self.table.rowCount()):
        row_has_match = False
        for col in range(1, self.table.columnCount()):  # Skip ID column
            item = self.table.item(row, col)
            if item:
                cell_text = item.text().lower()
                if search_text in cell_text:
                    # Highlight this cell
                    item.setBackground(highlight_brush)
                    row_has_match = True

        if row_has_match:
            matching_rows.append(row)

    # If we found any matches, scroll to the first one
    if matching_rows:
        self.table.scrollToItem(self.table.item(matching_rows[0], 0))


def _reset_cell_formatting(self):
    """Reset all cell formatting to default"""
    from PyQt5.QtGui import QBrush, QColor
    from themes import get_color

    bg_color = QColor(get_color('background'))
    secondary_color = QColor(get_color('secondary'))
    text_color = QColor(get_color('text'))

    for row in range(self.table.rowCount()):
        # Determine row background (alternating colors)
        row_bg = secondary_color if row % 2 else bg_color

        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setBackground(QBrush(row_bg))
                item.setForeground(QBrush(text_color))