"""
Reusable search components for product search interfaces.

This module provides common search components that can be shared across
different parts of the application to ensure consistent behavior and
avoid code duplication.
"""
from PyQt5.QtCore import (Qt, QSize, pyqtSignal, QEvent, QTimer, QPoint)
from PyQt5.QtWidgets import (QLineEdit, QListWidget, QListWidgetItem,
                             QAbstractItemView, QApplication,
                             QGraphicsDropShadowEffect)
from PyQt5.QtGui import QColor, QTextCursor

FILTER_ICON_SVG = '''
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
</svg>
'''

SORT_ICON_SVG = '''
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
  <line x1="21" y1="10" x2="3" y2="10"></line>
  <line x1="21" y1="6" x2="3" y2="6"></line>
  <line x1="21" y1="14" x2="3" y2="14"></line>
  <line x1="21" y1="18" x2="3" y2="18"></line>
</svg>
'''



# Try to import theme functions - handle gracefully if not available
try:
    from themes import get_color, get_size, get_font_size
    from themes.core import _current_theme
except ImportError:
    # Simple fallback theme functions
    def get_color(name):
        colors = {
            'background': '#F5F5F5',
            'card_bg': '#FFFFFF',
            'text': '#333333',
            'title': '#111111',
            'secondary_text': '#666666',
            'border': '#DDDDDD',
            'highlight': '#3A7BDF',
            'input_bg': '#FFFFFF',
            'button': '#3A7BDF',
            'button_hover': '#2A5CBF',
            'button_pressed': '#1A4CAF',
            'success': '#4CAF50',
            'selected': '#E3F2FD',
            'shadow': '#00000033'
        }
        return colors.get(name, '#FFFFFF')


    def get_size(name):
        sizes = {
            'padding': 10,
            'margin': 10,
            'border_radius': 5,
            'border_radius_small': 3,
            'border_radius_medium': 5,
            'tiny': 4,
            'small': 8,
            'medium': 16,
            'large': 24
        }
        return sizes.get(name, 10)


    def get_font_size(name):
        sizes = {
            'small': 10,
            'medium': 12,
            'regular': 14,
            'large': 16,
            'title': 20
        }
        return sizes.get(name, 14)


    _current_theme = "light"

# Try to import the custom scrollbar
try:
    from widgets.common.scroll_bar import EnhancedScrollBar
except ImportError:
    # If not available, we'll just use the default scrollbar
    pass

# Try to import logger - handle gracefully if not available
try:
    from logger import get_logger

    logger = get_logger('widgets.search_components')
except ImportError:
    # Simple fallback logger
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('widgets.search_components')



class SearchDropdown(QListWidget):
    """
    A dropdown list for search suggestions with improved visibility and focus handling.
    Can be used across different search components in the application.
    """

    def __init__(self, parent=None):
        # Create with a parent but use Tool window type instead of Popup
        super().__init__(parent)
        self.search_edit = parent

        # Use Qt.Tool instead of Qt.Popup for better focus behavior
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)

        # Critical attributes for preventing focus capture
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFocusPolicy(Qt.NoFocus)
        self.setAttribute(Qt.WA_X11DoNotAcceptFocus, True)
        self.setAttribute(Qt.WA_QuitOnClose, False)

        # Set selection behavior
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Set mouse tracking for hover effects
        self.setMouseTracking(True)

        # Connect signals
        self.itemClicked.connect(self.item_selected)

        # Configure appearance
        self.setMaximumHeight(300)
        self.setMinimumWidth(200)
        self.hide()

        # Install filter on parent application to handle outside clicks
        QApplication.instance().installEventFilter(self)

        # Apply theme styling
        self.apply_theme()

    def apply_theme(self):
        """Apply current theme styling to the dropdown."""
        # Try to use custom scrollbar if available
        try:
            self.setVerticalScrollBar(EnhancedScrollBar(Qt.Vertical))
        except:
            # Use default scrollbar with custom styling
            pass

        is_dark = _current_theme in ["dark", "classic"]

        background_color = get_color('card_bg')
        text_color = get_color('text')
        hover_color = get_color('secondary', QColor(get_color('highlight')).lighter(180).name())
        selected_color = get_color('highlight')
        border_color = get_color('border')

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(get_size('small'))
        shadow.setColor(QColor(get_color('shadow')))
        shadow.setOffset(2, 2)
        self.setGraphicsEffect(shadow)

        # Apply styling with theme colors
        self.setStyleSheet(f"""
            QListWidget {{
                background-color: {background_color};
                border: 1px solid {border_color};
                border-radius: {get_size('border_radius')}px;
                padding: {get_size('padding')}px;
                outline: none;
            }}

            QListWidget::item {{
                padding: {get_size('small')}px {get_size('medium')}px;
                border-radius: {get_size('tiny')}px;
                color: {text_color};
            }}

            QListWidget::item:selected {{
                background-color: {selected_color};
                color: white;
            }}

            QListWidget::item:hover:!selected {{
                background-color: {hover_color};
            }}

            /* Modern Elegant Scrollbar styling */
            QScrollBar:vertical {{
                background-color: transparent;
                width: 8px;
                margin: 2px 2px 2px 2px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical {{
                background-color: {get_color('secondary_text')}80; /* 50% opacity */
                min-height: 40px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {get_color('highlight')};
                min-height: 40px;
            }}

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                height: 0px;
                background: none;
            }}

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """)

    # Override these focus-related events to prevent the dropdown from ever taking focus
    def focusInEvent(self, event):
        """Override to prevent focus acquisition"""
        if self.search_edit:
            self.search_edit.setFocus()
        event.ignore()  # Important: Ignore the event to prevent default focus behavior

    def eventFilter(self, obj, event):
        """Handle global events"""
        # Close dropdown when clicking outside
        if event.type() == QEvent.MouseButtonPress and self.isVisible():
            if not self.geometry().contains(event.globalPos()):
                self.hide()
                return True  # Event handled
        return False  # Let other events proceed normally

    def item_selected(self, item):
        """Handle item selection and notify parent."""
        if not item or not self.search_edit:
            return

        text = item.text()

        # Get all products with this name directly from item data
        products = item.data(Qt.UserRole + 1)  # Contains all products with the selected name

        # Hide dropdown first to prevent visual artifacts
        self.hide()

        # Important: Block signals during text change to prevent recursive updates
        self.search_edit.blockSignals(True)
        self.search_edit.setText(text)
        self.search_edit.blockSignals(False)

        # Give focus back to search edit
        self.search_edit.setFocus()

        # Notify parent of selection
        if hasattr(self.search_edit, 'on_item_selected'):
            self.search_edit.on_item_selected(text, products)

    def mousePressEvent(self, event):
        """Handle clicks on the dropdown without stealing focus"""
        # Find item under mouse
        item = self.itemAt(event.pos())
        if item:
            # Select item and trigger selection handler
            self.setCurrentItem(item)
            self.item_selected(item)
        else:
            # If clicked on empty space, hide dropdown
            self.hide()
            self.search_edit.setFocus()

        # Don't call super().mousePressEvent to avoid focus change
        # But mark the event as accepted
        event.accept()

    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        # Return focus to search edit
        QTimer.singleShot(0, lambda: self.search_edit.setFocus() if self.search_edit else None)

    def position_dropdown(self):
        """Position the dropdown below the search edit."""
        if not self.search_edit:
            return

        # Calculate position to place dropdown below search edit
        parent_rect = self.search_edit.rect()
        global_point = self.search_edit.mapToGlobal(QPoint(0, parent_rect.height()))

        # Handle screen boundaries
        screen_rect = QApplication.desktop().availableGeometry(self.search_edit)
        dropdown_height = min(self.count() * 30 + 10, self.maximumHeight())

        # If dropdown would go below screen bottom, position it above the search edit
        if global_point.y() + dropdown_height > screen_rect.bottom():
            global_point.setY(global_point.y() - dropdown_height - parent_rect.height())

        # Ensure the dropdown doesn't extend beyond the screen width
        if global_point.x() + self.search_edit.width() > screen_rect.right():
            global_point.setX(screen_rect.right() - self.search_edit.width())

        self.move(global_point)
        self.setFixedWidth(self.search_edit.width())


class SearchEdit(QLineEdit):
    """
    Enhanced LineEdit with a dropdown for search suggestions and support for external toggle buttons.
    Can be used across different search interfaces in the application.
    """

    search_mode_changed = pyqtSignal(str)  # Signal emitted when search mode changes
    suggestion_update_requested = pyqtSignal(str)  # Signal for delayed suggestion updates

    def __init__(self, parent=None, object_name="searchEdit", min_height=35, translator=None):
        """
        Initialize a search edit with dropdown suggestions.

        Args:
            parent: Parent widget
            object_name: Object name for styling
            min_height: Minimum height of the search edit
            translator: Translator for localization
        """
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setMinimumHeight(min_height)  # Smaller height for more modern look

        # Set maximum height to prevent abnormal growth
        self.setMaximumHeight(min_height + 10)  # Add small buffer for styling

        # Set size policy to prevent stretching
        size_policy = self.sizePolicy()
        size_policy.setVerticalPolicy(size_policy.Fixed)
        self.setSizePolicy(size_policy)

        self.translator = translator

        # Configure for proper bidirectional text support
        self.setLayoutDirection(Qt.LayoutDirectionAuto)
        self.setInputMethodHints(Qt.ImhNone)

        # Create custom dropdown
        self.dropdown = SearchDropdown(self)

        # Connect signals
        self.textChanged.connect(self.on_text_changed)
        self.returnPressed.connect(self.perform_search)

        # Setup delayed suggestion updates to improve typing performance
        self.suggestion_update_requested.connect(self._update_suggestions_delayed)
        self._suggestion_timer = QTimer(self)
        self._suggestion_timer.setSingleShot(True)
        self._suggestion_timer.setInterval(200)  # 200ms delay for better typing experience
        self._suggestion_timer.timeout.connect(self._process_pending_suggestion_update)
        self._pending_suggestion_text = None

        # References to parent widget and data
        self.parent_widget = None

        # Track if we're already processing a text change
        self._processing_text_change = False

        # Track cursor position
        self._last_cursor_position = 0

        # Track search mode - default to product name search
        self.search_mode = 'product_name'  # Can be 'product_name' or 'barcode'

        # Apply theme styling
        self.apply_theme()

    def _translate(self, key, default=""):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            translated = self.translator.t(key)
            return translated if translated != key else default
        return default

    def set_search_mode(self, mode):
        """Set the search mode - can be called by external toggle buttons."""
        if mode not in ('product_name', 'barcode'):
            logger.warning(f"Invalid search mode: {mode}")
            return

        # Only emit signal if the mode has actually changed
        if self.search_mode != mode:
            self.search_mode = mode

            # Update placeholder text based on mode
            if mode == 'product_name':
                self.setPlaceholderText(self._translate('search_by_name_placeholder', "Search by name..."))
            else:
                self.setPlaceholderText(self._translate('search_by_barcode_placeholder', "Search by barcode..."))

            # Emit signal to notify parent of mode change
            self.search_mode_changed.emit(mode)

            # Update suggestions for current text if there is any
            text = self.text().strip()
            if text:
                # Use the delayed suggestion update method
                self.suggestion_update_requested.emit(text)

            # Clear existing text when mode changes
            if self.text():
                self.clear()
                # Also clear results if needed
                if hasattr(self.parent_widget, 'clear_results'):
                    self.parent_widget.clear_results()

    def apply_theme(self):
        """Apply theme styling to the search edit."""
        # Use consistent border radius from theme
        border_radius = get_size('border_radius_medium')

        self.setStyleSheet(f"""
            QLineEdit#{self.objectName()} {{
                background-color: {get_color('input_bg')};
                color: {get_color('text')};
                border: 1px solid {get_color('border')};
                border-radius: {border_radius}px;
                padding: 0px 10px;  /* Reduced vertical padding */
                font-size: {get_font_size('regular')}px;
                min-height: {self.minimumHeight()}px;
                max-height: {self.maximumHeight()}px;
            }}

            QLineEdit#{self.objectName()}:focus {{
                border: 1px solid {get_color('highlight')};
            }}
        """)

    def set_parent_widget(self, widget):
        """Set the parent widget for callbacks."""
        self.parent_widget = widget

    def on_text_changed(self, text):
        """Improved handler for text changes with better bidirectional text support."""
        # Prevent recursive calls
        if self._processing_text_change:
            return

        # Store current cursor position
        self._last_cursor_position = self.cursorPosition()

        # Set processing flag
        self._processing_text_change = True

        try:
            if not self.parent_widget:
                return

            # Clear current results if text is empty
            if not text.strip():
                # Cancel any pending suggestion updates
                self._suggestion_timer.stop()
                self._pending_suggestion_text = None

                # Notify parent to clear results if needed
                if hasattr(self.parent_widget, 'clear_results'):
                    self.parent_widget.clear_results()
                self.dropdown.hide()
                return

            # Request suggestions update with delay for better typing performance
            self.suggestion_update_requested.emit(text)

            # Ensure cursor is properly positioned and visible (fixes bidirectional text issues)
            QTimer.singleShot(0, lambda: self._ensure_cursor_visible())
        finally:
            # Reset flag
            self._processing_text_change = False

    def _ensure_cursor_visible(self):
        """Ensure cursor is properly positioned and visible after text changes."""
        if not self.hasFocus():
            return

        # Get cursor position
        cursor_pos = min(self._last_cursor_position, len(self.text()))

        # Ensure only one cursor is shown by explicitly setting position
        self.blockSignals(True)
        self.setCursorPosition(cursor_pos)
        self.blockSignals(False)

    def _update_suggestions_delayed(self, text):
        """Queue a suggestion update with a delay to improve typing performance."""
        self._pending_suggestion_text = text
        self._suggestion_timer.start()

    def _process_pending_suggestion_update(self):
        """Process the pending suggestion update after the delay."""
        if self._pending_suggestion_text is not None:
            text = self._pending_suggestion_text
            self._pending_suggestion_text = None

            # Actually update suggestions
            self.update_suggestions(text)

            # Restore cursor position to prevent jumping
            cursor_pos = min(self._last_cursor_position, len(self.text()))
            self.setCursorPosition(cursor_pos)

    def keyPressEvent(self, event):
        """Improved key event handler with better bidirectional text support."""
        # Record cursor position before the key is processed
        self._last_cursor_position = self.cursorPosition()

        # Special handling for Backspace and Delete to prevent cursor duplication
        if event.key() in (Qt.Key_Backspace, Qt.Key_Delete):
            # Cancel any pending suggestion updates
            self._suggestion_timer.stop()

            # Handle deletion with special care for bidirectional text
            curr_text = self.text()
            cursor_pos = self.cursorPosition()

            if event.key() == Qt.Key_Backspace and cursor_pos > 0:
                # Remove one character before the cursor
                new_text = curr_text[:cursor_pos-1] + curr_text[cursor_pos:]

                # Block signals during manual text update
                self.blockSignals(True)
                self.setText(new_text)
                self.setCursorPosition(cursor_pos - 1)
                self.blockSignals(False)

                # Manually trigger text changed with correct cursor position
                self.on_text_changed(new_text)
                return

            elif event.key() == Qt.Key_Delete and cursor_pos < len(curr_text):
                # Remove one character after the cursor
                new_text = curr_text[:cursor_pos] + curr_text[cursor_pos+1:]

                # Block signals during manual text update
                self.blockSignals(True)
                self.setText(new_text)
                self.setCursorPosition(cursor_pos)
                self.blockSignals(False)

                # Manually trigger text changed with correct cursor position
                self.on_text_changed(new_text)
                return

        # Cancel any pending suggestion updates when typing
        if event.text():
            self._suggestion_timer.stop()

        # Handle dropdown navigation when visible
        if self.dropdown.isVisible() and event.key() in (Qt.Key_Up, Qt.Key_Down,
                                                        Qt.Key_Enter, Qt.Key_Return,
                                                        Qt.Key_Escape, Qt.Key_Tab):
            current_row = self.dropdown.currentRow()
            item_count = self.dropdown.count()

            if event.key() == Qt.Key_Down:
                # Move selection down or select first item
                if current_row < item_count - 1:
                    self.dropdown.setCurrentRow(current_row + 1)
                elif current_row == -1 and item_count > 0:
                    self.dropdown.setCurrentRow(0)
                return

            elif event.key() == Qt.Key_Up:
                # Move selection up
                if current_row > 0:
                    self.dropdown.setCurrentRow(current_row - 1)
                elif current_row == 0:
                    # Move selection back to search edit
                    self.dropdown.setCurrentRow(-1)
                return

            elif event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Tab):
                # Select current item or perform search
                current_item = self.dropdown.currentItem()
                if current_item:
                    self.dropdown.item_selected(current_item)
                else:
                    self.perform_search()
                return

            elif event.key() == Qt.Key_Escape:
                # Hide dropdown
                self.dropdown.hide()
                return

        # For all other keys, use standard behavior
        super().keyPressEvent(event)

    def update_suggestions(self, search_text):
        """Generate and display search suggestions without duplicate names."""
        if not search_text or not self.parent_widget:
            self.dropdown.clear()
            self.dropdown.hide()
            return

        search_text = search_text.strip().lower()
        # Split search text into individual words
        search_words = search_text.split()

        # Clear previous suggestions
        self.dropdown.clear()

        # Get filtered products - we need to access them from parent widget
        filtered_products = []

        # Different parent widgets might store products differently
        if hasattr(self.parent_widget, 'filtered_products'):
            filtered_products = self.parent_widget.filtered_products

        if not filtered_products:
            self.dropdown.hide()
            return

        # Track unique items to avoid duplicates
        matching_items = {}

        for product in filtered_products:
            # Get product data to check against (handle both dict and tuple formats)
            if isinstance(product, dict):
                product_name = str(product.get('product_name', '')).lower()
                parcode = str(product.get('parcode', '')).lower()
                category = str(product.get('category', '')).lower()
                manufacturer = str(product.get('manufacturer', '')).lower()
            else:  # tuple
                product_name = str(product[2]).lower() if len(product) > 2 else ''
                parcode = str(product[0]).lower() if len(product) > 0 else ''
                category = str(product[1]).lower() if len(product) > 1 else ''
                manufacturer = ''  # Might not be available in tuple format

            # Check based on search mode
            match_found = False

            if self.search_mode == 'product_name':
                # For product name search, match against name and category
                if search_text in product_name or search_text in category:
                    match_found = True
                else:
                    # Check if all search words appear in the product name or category
                    all_words_found = True
                    for word in search_words:
                        if word not in product_name and word not in category:
                            all_words_found = False
                            break
                    match_found = all_words_found

                # For product name mode, group by name
                if match_found:
                    display_text = product['product_name'] if isinstance(product, dict) else product[2]
                    if display_text not in matching_items:
                        matching_items[display_text] = []
                    matching_items[display_text].append(product)

            elif self.search_mode == 'barcode':
                # For barcode search, match only against barcode
                if search_text in parcode:
                    match_found = True

                # For barcode mode, group by barcode
                if match_found:
                    # Use only barcode as display text for barcode mode
                    display_text = product['parcode'] if isinstance(product, dict) else product[0]

                    # No product name, just use the barcode
                    if display_text not in matching_items:
                        matching_items[display_text] = []
                    matching_items[display_text].append(product)

        # No matches found
        if not matching_items:
            self.dropdown.hide()
            return

        # Add unique suggestions to dropdown - limit to 10 for performance
        item_count = 0
        for display_text, products in matching_items.items():
            item = QListWidgetItem(display_text)
            # Store all matching products with this display text as user data
            item.setData(Qt.UserRole, products[0])  # Store the first product
            item.setData(Qt.UserRole + 1, products)  # Store all products
            self.dropdown.addItem(item)

            item_count += 1
            if item_count >= 10:  # Limit suggestions to 10 for better performance
                break

        # Show dropdown if we have items
        if self.dropdown.count() > 0:
            self.dropdown.position_dropdown()
            self.dropdown.setCurrentRow(-1)  # No initial selection
            self.dropdown.show()
        else:
            self.dropdown.hide()

    def perform_search(self):
        """Execute the search using the parent widget's search method."""
        if self.parent_widget:
            self.dropdown.hide()

            # Different parent widgets might have different search methods
            if hasattr(self.parent_widget, '_perform_search'):
                self.parent_widget._perform_search()
            elif hasattr(self.parent_widget, 'submit_search'):
                self.parent_widget.submit_search()
            elif hasattr(self.parent_widget, 'on_search'):
                self.parent_widget.on_search(self.text())

    def on_item_selected(self, text, products):
        """Handle when an item is selected from the dropdown."""
        # Forward to parent widget if it has a handler
        if self.parent_widget:
            if hasattr(self.parent_widget, 'on_item_selected'):
                self.parent_widget.on_item_selected(text, products)
            elif hasattr(self.parent_widget, '_display_results'):
                # For compatibility with SmartSearchWidget
                self.parent_widget.search_results = products
                self.parent_widget._display_results(products)

                # Update results label if needed
                if hasattr(self.parent_widget, 'results_label'):
                    count = len(products)
                    total = len(self.parent_widget.products) if hasattr(self.parent_widget, 'products') else 0
                    self.parent_widget.results_label.setText(
                        f"Found {count} matches for '{text}' (out of {total} products)"
                    )

    def focusOutEvent(self, event):
        """Handle focus lost event."""
        super().focusOutEvent(event)
        # Use delayed check to see if we should hide dropdown
        QTimer.singleShot(100, self._check_focus_for_dropdown)

    def _check_focus_for_dropdown(self):
        """Check if focus is completely lost and hide dropdown if needed."""
        if not self.hasFocus() and not self.dropdown.underMouse():
            # Only hide if focus is not on this widget and mouse is not over dropdown
            self.dropdown.hide()