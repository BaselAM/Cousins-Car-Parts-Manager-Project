"""
Enhanced Smart Search Widget for Car Parts Management System with fixed search dropdown.

Provides an intuitive search interface with a reliable dropdown implementation,
refined card-based result display, advanced multi-word search across product fields,
product duplication functionality, and barcode scanning capability.
"""

import os

from PyQt5.QtCore import (Qt, QSize, pyqtSignal, QTimer, QPropertyAnimation,
                          QEasingCurve, QRect, QPoint, QObject, QByteArray)
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QScrollArea, QFrame,
                             QToolButton, QMessageBox, QDialog, QFormLayout,
                             QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
                             QApplication, QGraphicsDropShadowEffect)
from PyQt5.QtGui import (QIcon, QFont, QColor, QPixmap, QPainter)
from PyQt5.QtSvg import QSvgRenderer

# Import our shared search components
from search_components import SearchEdit, SearchDropdown

# Import components from the components directory
from .components.product_card import ProductCard
from .components.floating_action_button import FloatingActionButton
from .components.duplicate_dialog import DuplicateProductDialog
from .components.barcode_adapter import BarcodeDialogAdapter

# Import utility functions
from .utils.search_utls import product_matches_search

# Try to import theme and logger modules - handle gracefully if not available
try:
    from themes import get_color, get_size, get_font_size, apply_dialog_theme, get_current_theme
    from themes.core import _current_theme
    from logger import get_logger

    logger = get_logger('widgets.smart_search_widget')
except ImportError:
    # Simple fallback logger if the standard logger is unavailable
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('widgets.smart_search_widget')


    # Fallback theme functions
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
            'shadow': '#00000033',
            'secondary': '#E0E0E0',
            'button_disabled': '#CCCCCC',
            'text_disabled': '#999999'
        }
        return colors.get(name, '#FFFFFF')


    def get_size(name):
        sizes = {
            'padding': 10,
            'margin': 10,
            'border_radius': 5,
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


    # Fallback apply_dialog_theme function
    def apply_dialog_theme(dialog, title):
        pass  # Just a placeholder, styling will be applied manually

    # Fallback get_current_theme
    def get_current_theme():
        return _current_theme


class ButtonAnimator(QObject):
    """Class to apply smooth animations to toggle buttons."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.animations = {}

    def setup_animation(self, button):
        """Set up animations for a button."""
        # Create animation for background color
        color_anim = QPropertyAnimation(button, b"background-color")
        color_anim.setDuration(150)  # 150ms duration for smooth transition
        color_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Create animation for size
        size_anim = QPropertyAnimation(button, b"geometry")
        size_anim.setDuration(100)  # 100ms for size bounce
        size_anim.setEasingCurve(QEasingCurve.OutBack)  # Bouncy effect

        # Store animations
        self.animations[button] = {
            'color': color_anim,
            'size': size_anim
        }

    def animate_press(self, button):
        """Animate button press."""
        if button not in self.animations:
            self.setup_animation(button)

        # Get current geometry
        geom = button.geometry()

        # Set up size animation for press (scale down slightly)
        size_anim = self.animations[button]['size']
        size_anim.setStartValue(geom)
        size_anim.setEndValue(QRect(
            geom.x() + 1,
            geom.y() + 1,
            geom.width() - 2,
            geom.height() - 2
        ))

        # Start animation
        size_anim.start()

    def animate_release(self, button):
        """Animate button release."""
        if button not in self.animations:
            return

        # Get current geometry
        geom = button.geometry()

        # Set up size animation for release (back to normal)
        size_anim = self.animations[button]['size']
        size_anim.setStartValue(geom)
        size_anim.setEndValue(QRect(
            geom.x() - 1,
            geom.y() - 1,
            geom.width() + 2,
            geom.height() + 2
        ))

        # Start animation
        size_anim.start()


class SlideIndicatorToggle(QWidget):
    """A modern toggle button group with a sliding indicator."""

    toggled = pyqtSignal(str)  # Signal when a button is toggled

    def __init__(self, options=None, parent=None):
        super().__init__(parent)
        self.options = options or []
        self.buttons = []
        self.current_index = 0
        self.init_ui()

    def init_ui(self):
        """Initialize the UI with modern styling."""
        # Main layout
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(3, 3, 3, 3)
        self.main_layout.setSpacing(2)

        # Container
        self.setObjectName("modernToggleGroup")
        self.setFixedHeight(36)

        # Create buttons
        for i, option in enumerate(self.options):
            btn = QPushButton(option['text'])
            btn.setObjectName(f"toggleOption_{i}")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=i: self.handle_toggle(idx))
            self.buttons.append(btn)
            self.main_layout.addWidget(btn)

        # Set first button as checked by default
        if self.buttons:
            self.buttons[0].setChecked(True)

        # Create sliding indicator
        self.indicator = QFrame(self)
        self.indicator.setObjectName("slideIndicator")
        self.indicator.setFixedHeight(30)

        # Apply styles
        self.apply_styles()

        # Position indicator initially
        QTimer.singleShot(0, self.update_indicator_position)

    def apply_styles(self):
        """Apply modern styles to components."""
        # Container style
        self.setStyleSheet("""
            QWidget#modernToggleGroup {
                background-color: #3A7BDF;
                border-radius: 8px;
                padding: 3px;
            }

            /* Button base style */
            QPushButton {
                background-color: transparent;
                color: rgba(255, 255, 255, 0.75);
                border: none;
                border-radius: 6px;
                padding: 0px 12px;
                font-size: 13px;
                font-weight: 500;
                letter-spacing: 0.3px;
                min-height: 30px;
                text-align: center;
            }

            /* Active button */
            QPushButton:checked {
                color: white;
                font-weight: 600;
            }

            /* Hover state */
            QPushButton:hover:!checked {
                color: rgba(255, 255, 255, 0.9);
            }

            /* Pressed state */
            QPushButton:pressed {
                color: white;
            }

            /* Sliding indicator */
            QFrame#slideIndicator {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 6px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)

    def update_indicator_position(self):
        """Update the position of the sliding indicator based on the selected button."""
        if not self.buttons:
            return

        # Get the currently checked button
        checked_btn = None
        for i, btn in enumerate(self.buttons):
            if btn.isChecked():
                checked_btn = btn
                self.current_index = i
                break

        if not checked_btn:
            return

        # Get button geometry
        geo = checked_btn.geometry()

        # Create the indicator if it doesn't exist
        if not hasattr(self, 'indicator') or not self.indicator:
            self.indicator = QFrame(self)
            self.indicator.setObjectName("slideIndicator")
            self.indicator.setFixedHeight(geo.height() - 6)
            self.indicator.show()
            self.indicator.raise_()

        # Position indicator
        self.indicator.setGeometry(
            geo.x(),
            geo.y() + 3,  # Small vertical adjustment
            geo.width(),
            geo.height() - 6  # Slightly shorter than the button
        )

        # Ensure indicator is visible and on top
        self.indicator.show()
        self.indicator.raise_()

    def handle_toggle(self, index):
        """Handle button toggling with smooth animation."""
        # Uncheck all other buttons
        for i, btn in enumerate(self.buttons):
            btn.setChecked(i == index)

        # Animate the indicator
        if hasattr(self, 'indicator') and self.indicator:
            # Get target button geometry
            target_geo = self.buttons[index].geometry()

            # Create animation
            anim = QPropertyAnimation(self.indicator, b"geometry")
            anim.setDuration(200)
            anim.setEasingCurve(QEasingCurve.OutCubic)

            # Set end geometry
            anim.setEndValue(QRect(
                target_geo.x(),
                target_geo.y() + 3,  # Small vertical adjustment
                target_geo.width(),
                target_geo.height() - 6  # Slightly shorter than the button
            ))

            # Start animation
            anim.start()

        # Emit the signal with the option value
        self.toggled.emit(self.options[index]['value'])

    def set_active(self, value):
        """Set the active toggle by value."""
        for i, option in enumerate(self.options):
            if option['value'] == value:
                self.handle_toggle(i)
                break


class SmartSearchWidget(QWidget):
    """
    Enhanced smart search widget with elegant suggestions and product cards display.
    Provides intuitive search with dropdown suggestions and displays results in visually appealing cards.
    Now with product duplication capability and barcode scanning.
    """

    # Signals for product actions
    product_edited = pyqtSignal(dict)  # Emitted when a product is edited
    product_deleted = pyqtSignal(int)  # Emitted when a product is deleted
    product_duplicated = pyqtSignal(dict)  # Emitted when a product is duplicated

    # SVG icons as strings (embedded to avoid file dependencies)
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

    def __init__(self, translator, db, parent=None):
        """
        Initialize smart search widget.

        Args:
            translator: Translator object for localization
            db: Database connection for products
            parent: Parent widget
        """
        super().__init__(parent)
        self.translator = translator
        self.db = db
        self.db_operator = None
        self.products = []
        self.filtered_products = []
        self.search_results = []
        self.current_filter = {}
        self.last_search = None  # Track last search instead of using SearchHandler

        # Track product cards
        self.product_cards = []

        # Set object name for styling
        self.setObjectName("smartSearchWidget")

        # Initialize UI components
        self._init_ui()

        # Set up database connection
        self._setup_database()

        # Connect to theme change events
        try:
            from themes.theme_events import theme_event_manager
            theme_event_manager.theme_changed.connect(self._on_theme_changed)
            logger.debug("Connected to theme change events")
        except Exception as e:
            logger.error(f"Error connecting to theme events: {e}")

        # Apply initial theme
        self.apply_theme()
        self._apply_global_scrollbar_style()

        # Connect to database sync manager
        self.connect_to_sync_manager()

    def _init_ui(self):
        """Initialize the UI components with exact HTML-matching styling."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # Title container
        title_container = QFrame(self)
        title_container.setObjectName("titleContainer")
        title_container.setFixedHeight(60)

        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)

        # Title with elegant typography
        title_label = QLabel(self.translator.t('smart_search_button'), title_container)
        title_label.setObjectName("smartSearchTitle")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_font = QFont()
        title_font.setPointSize(get_font_size('title'))
        title_font.setBold(True)
        title_label.setFont(title_font)

        title_layout.addWidget(title_label)
        title_layout.addStretch(1)

        # Search container
        search_container = QFrame(self)
        search_container.setObjectName("searchContainer")
        search_container.setFrameShape(QFrame.StyledPanel)
        search_container.setMaximumHeight(120)

        # Add shadow to search container
        search_shadow = QGraphicsDropShadowEffect(search_container)
        search_shadow.setBlurRadius(8)
        search_shadow.setColor(QColor(get_color('shadow')))
        search_shadow.setOffset(0, 2)
        search_container.setGraphicsEffect(search_shadow)

        # Single row layout for search container - exactly like the HTML
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(20, 20, 20, 20)
        search_layout.setSpacing(20)  # Match HTML spacing

        # Search edit - wider like in HTML
        self.search_edit = SearchEdit(parent=search_container, object_name="smartSearchEdit", min_height=36)
        self.search_edit.setPlaceholderText(self.translator.t('search_placeholder'))
        self.search_edit.set_parent_widget(self)
        self.search_edit.setClearButtonEnabled(True)

        # Search button - styled exactly like the HTML
        search_button = QPushButton(self.translator.t('search_products'), search_container)
        search_button.setObjectName("searchButton")
        search_button.setFixedSize(100, 36)  # Fixed size to match HTML
        search_button.clicked.connect(self._perform_search)

        # Toggle group container with modern styling
        toggle_group = QFrame(search_container)
        toggle_group.setObjectName("toggleGroup")
        toggle_group.setFixedSize(280, 36)  # Match search button height

        # Add subtle shadow for toggle group
        toggle_shadow = QGraphicsDropShadowEffect(toggle_group)
        toggle_shadow.setBlurRadius(6)
        toggle_shadow.setColor(QColor(0, 0, 0, 30))
        toggle_shadow.setOffset(0, 1)
        toggle_group.setGraphicsEffect(toggle_shadow)

        # Tight layout for toggle group
        toggle_group_layout = QHBoxLayout(toggle_group)
        toggle_group_layout.setSpacing(2)
        toggle_group_layout.setContentsMargins(2, 2, 2, 2)

        # Create product name toggle button
        self.product_name_toggle = QPushButton(self.translator.t('search_by_name'), toggle_group)
        self.product_name_toggle.setObjectName("productNameToggle")
        self.product_name_toggle.setCheckable(True)
        self.product_name_toggle.setChecked(True)
        self.product_name_toggle.setCursor(Qt.PointingHandCursor)

        # Create barcode toggle button
        self.barcode_toggle = QPushButton(self.translator.t('search_by_barcode'), toggle_group)
        self.barcode_toggle.setObjectName("barcodeToggle")
        self.barcode_toggle.setCheckable(True)
        self.barcode_toggle.setCursor(Qt.PointingHandCursor)

        # Add buttons to toggle group layout with equal width
        toggle_group_layout.addWidget(self.product_name_toggle, 1)
        toggle_group_layout.addWidget(self.barcode_toggle, 1)

        # Connect toggle button signals directly to specific handler methods
        self.product_name_toggle.clicked.connect(self._handle_product_name_toggle)
        self.barcode_toggle.clicked.connect(self._handle_barcode_toggle)

        # Add widgets to search layout
        search_layout.addWidget(self.search_edit, 1)  # Stretch factor 1
        search_layout.addWidget(search_button, 0)  # No stretch
        search_layout.addWidget(toggle_group, 0)  # No stretch

        # Search type note below search container
        self.search_type_note = QLabel("", self)
        self.search_type_note.setObjectName("searchTypeNote")
        self.search_type_note.setStyleSheet(f"""
            QLabel#searchTypeNote {{
                color: {get_color('secondary_text')};
                font-size: {get_font_size('small')}px;
                font-style: italic;
                margin-left: 20px;
            }}
        """)

        # Initialize toggle buttons based on current search mode
        current_mode = self.search_edit.search_mode
        self.barcode_toggle.setChecked(current_mode == 'barcode')
        self.product_name_toggle.setChecked(current_mode == 'product_name')

        # Results header
        results_header = QFrame(self)
        results_header.setObjectName("resultsHeader")
        results_header.setMinimumHeight(50)

        results_header_layout = QHBoxLayout(results_header)
        results_header_layout.setContentsMargins(20, 10, 20, 10)

        # Results title and count
        results_title = QLabel(self.translator.t('search_results_title'), results_header)
        results_title.setObjectName("resultsTitle")
        results_title_font = QFont()
        results_title_font.setPointSize(get_font_size('regular'))
        results_title_font.setBold(True)
        results_title.setFont(results_title_font)

        self.results_label = QLabel(self.translator.t('search_results', count=0, total=0), results_header)
        self.results_label.setObjectName("resultsLabel")
        self.results_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        results_header_layout.addWidget(results_title)
        results_header_layout.addWidget(self.results_label)
        results_header_layout.addStretch(1)

        # Options buttons for the header with modern styling
        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)  # Increased spacing

        # Sort button with improved styling
        sort_button = QPushButton(self.translator.t('sort_by_price'), results_header)
        sort_button.setObjectName("sortButton")
        sort_button.clicked.connect(lambda: self._show_sort_dialog() if hasattr(self, '_show_sort_dialog') else None)
        sort_button.setMinimumHeight(36)

        # Filter button with improved styling
        self.filter_button = QPushButton(self.translator.t('filter_button'), results_header)
        self.filter_button.setObjectName("filterButton")
        self.filter_button.clicked.connect(self._show_filter_dialog)
        self.filter_button.setMinimumHeight(36)

        options_layout.addWidget(sort_button)
        options_layout.addWidget(self.filter_button)
        results_header_layout.addLayout(options_layout)

        # Results container
        results_container = QFrame(self)
        results_container.setObjectName("resultsContainer")
        results_container.setContentsMargins(0, 0, 0, 0)

        results_layout = QVBoxLayout(results_container)
        results_layout.setContentsMargins(0, 0, 0, 0)
        results_layout.setSpacing(0)

        # Add results header to results container
        results_layout.addWidget(results_header)
        results_layout.addWidget(self.search_type_note)  # Move note here below header

        # Content container for scroll area
        content_container = QWidget(results_container)
        content_container.setObjectName("contentContainer")

        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Scroll area for results
        scroll_area = QScrollArea(content_container)
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("resultsScrollArea")
        scroll_area.setFrameShape(QFrame.NoFrame)

        # Container for product cards
        self.products_container = QFrame(scroll_area)
        self.products_container.setObjectName("productsContainer")

        # Shadow effect for products container
        products_shadow = QGraphicsDropShadowEffect(self.products_container)
        products_shadow.setBlurRadius(10)
        products_shadow.setColor(QColor(get_color('shadow')))
        products_shadow.setOffset(0, 2)
        self.products_container.setGraphicsEffect(products_shadow)

        # Layout for product cards
        self.products_layout = QVBoxLayout(self.products_container)
        self.products_layout.setContentsMargins(20, 20, 20, 20)
        self.products_layout.setSpacing(16)
        self.products_layout.setAlignment(Qt.AlignTop)

        # Add products container to scroll area
        scroll_area.setWidget(self.products_container)
        content_layout.addWidget(scroll_area)

        # Add content container to results layout
        results_layout.addWidget(content_container, 1)

        # Status footer
        status_container = QFrame(self)
        status_container.setObjectName("statusContainer")
        status_container.setMaximumHeight(50)

        status_layout = QHBoxLayout(status_container)
        status_layout.setContentsMargins(20, 10, 20, 10)

        # Status label
        self.status_label = QLabel(self.translator.t('status_ready'), status_container)
        self.status_label.setObjectName("statusLabel")

        # Refresh button
        refresh_button = QPushButton(self.translator.t('refresh'), status_container)
        refresh_button.setObjectName("refreshButton")
        refresh_button.setMinimumHeight(36)
        refresh_button.clicked.connect(self._refresh_data)

        # Add status label and refresh button to status layout
        status_layout.addWidget(self.status_label, 1)
        status_layout.addWidget(refresh_button)

        # Floating action button (FAB)
        self.fab = QPushButton("+", self)
        self.fab.setObjectName("circularFab")
        self.fab.setToolTip(self.translator.t('duplicate_product'))
        self.fab.clicked.connect(self._show_duplication_dialog)
        self.fab.setDisabled(True)
        self.fab.setFixedSize(60, 60)
        self.fab.hide()  # Initially hide the FAB

        # Add all components to main layout
        main_layout.addWidget(title_container)
        main_layout.addWidget(search_container)
        main_layout.addWidget(results_container, 1)
        main_layout.addWidget(status_container)

        # Initialize search mode to product_name by default
        self.toggle_search_mode('product_name')

        # Setup modern button styling after the UI is fully initialized
        QTimer.singleShot(0, self.setup_modern_header_buttons)

    def _refresh_data(self):
        """Refresh product data from the database with improved debugging."""
        self.status_label.setText(self.translator.t('loading_products'))

        print("\n===== SMART SEARCH: REFRESHING DATA =====")

        if self.db_operator:
            # Add debug statement
            print(f"Using DatabaseOperator to get all parts (force_refresh=True)")

            # Important: Set force_refresh=True to bypass any caching
            self.db_operator.execute(
                "get_all_parts",
                self._on_products_loaded,
                self._on_db_error,
                force_refresh=True
            )
        else:
            # Try direct database access as a fallback
            print(f"DatabaseOperator not available, trying direct database access")
            try:
                if hasattr(self, 'db') and self.db and hasattr(self.db, 'get_all_parts'):
                    parts = self.db.get_all_parts()
                    self._on_products_loaded(parts)
                else:
                    logger.error("Database operator not initialized and direct database access not available")
                    self.status_label.setText(self.translator.t('load_error'))
            except Exception as e:
                logger.error(f"Error refreshing data directly: {e}")
                self.status_label.setText(self.translator.t('load_error'))

    def _handle_product_added(self, product_data):
        """Handle notification that a product was added in another widget."""
        print(f"\n===== SMART SEARCH: PRODUCT ADDED NOTIFICATION =====")
        print(f"Product: {product_data.get('product_name')}")
        print(f"ID: {product_data.get('id')}")
        print(f"Parcode: {product_data.get('parcode')}")

        # Use guard condition to prevent infinite loops - this is important!
        if hasattr(self, '_processing_sync_event') and self._processing_sync_event:
            print("Already processing sync event - skipping to prevent loop")
            return

        self._processing_sync_event = True
        try:
            # Force a complete refresh of data but DO NOT emit signals after refresh
            print("Forcing data refresh (silent)...")
            self._refresh_data_silent()

            # Show feedback in status bar
            if hasattr(self, 'status_label'):
                self.status_label.setText(self.translator.t('product_added', "Product added, view refreshed"))

            print("Data refresh completed")
        except Exception as e:
            print(f"ERROR in product_added handler: {e}")
            import traceback
            print(traceback.format_exc())
        finally:
            self._processing_sync_event = False

    def _handle_product_updated(self, product_data):
        """Handle notification that a product was updated in another widget."""
        print(f"\n===== SMART SEARCH: PRODUCT UPDATED NOTIFICATION =====")
        print(f"Product: {product_data.get('product_name')}")
        print(f"ID: {product_data.get('id')}")
        print(f"Parcode: {product_data.get('parcode')}")
        print(f"New Quantity: {product_data.get('quantity')}")

        # Use guard condition to prevent infinite loops - this is important!
        if hasattr(self, '_processing_sync_event') and self._processing_sync_event:
            print("Already processing sync event - skipping to prevent loop")
            return

        self._processing_sync_event = True
        try:
            # Force a complete refresh of data but DO NOT emit signals after refresh
            print("Forcing data refresh (silent)...")
            self._refresh_data_silent()

            # Also update any displayed products if they match
            # Using search_results instead of current_products
            if hasattr(self, 'search_results') and self.search_results:
                print(f"Checking if updated product is in current search results ({len(self.search_results)} items)")
                for i, product in enumerate(self.search_results):
                    if (product.get('id') == product_data.get('id') or
                            product.get('parcode') == product_data.get('parcode')):
                        print(f"Found product in search results at position {i}, updating...")
                        # Update the product data
                        self.search_results[i] = product_data
                        # Update the display
                        self._display_results(self.search_results)
                        break

            # Show feedback in status bar
            if hasattr(self, 'status_label'):
                self.status_label.setText(
                    self.translator.t('product_updated', "Product updated, view refreshed")
                )

            print("Data refresh completed")
        except Exception as e:
            print(f"ERROR in product_updated handler: {e}")
            import traceback
            print(traceback.format_exc())
        finally:
            self._processing_sync_event = False

    def _handle_product_deleted(self, product_id):
        """Handle notification that a product was deleted in another widget."""
        print(f"\n===== SMART SEARCH: PRODUCT DELETED NOTIFICATION =====")
        print(f"Product ID: {product_id}")

        # Use guard condition to prevent infinite loops - this is important!
        if hasattr(self, '_processing_sync_event') and self._processing_sync_event:
            print("Already processing sync event - skipping to prevent loop")
            return

        self._processing_sync_event = True
        try:
            # Force a complete refresh of data but DO NOT emit signals after refresh
            print("Forcing data refresh (silent)...")
            self._refresh_data_silent()

            # Also remove from search results if present
            # Using search_results instead of current_products
            if hasattr(self, 'search_results') and self.search_results:
                print(f"Checking if deleted product is in current search results")
                new_results = [p for p in self.search_results if p.get('id') != product_id]
                if len(new_results) != len(self.search_results):
                    print(f"Found product in search results, updating display...")
                    self.search_results = new_results
                    self._display_results(new_results)

            # Show feedback in status bar
            if hasattr(self, 'status_label'):
                self.status_label.setText(
                    self.translator.t('product_deleted', "Product deleted, view refreshed")
                )

            print("Data refresh completed")
        except Exception as e:
            print(f"ERROR in product_deleted handler: {e}")
            import traceback
            print(traceback.format_exc())
        finally:
            self._processing_sync_event = False

    def _handle_products_loaded(self):
        """Handle notification that products were loaded in another widget."""
        print(f"\n===== SMART SEARCH: PRODUCTS LOADED NOTIFICATION =====")

        # Use guard condition to prevent infinite loops - this is important!
        if hasattr(self, '_processing_sync_event') and self._processing_sync_event:
            print("Already processing sync event - skipping to prevent loop")
            return

        self._processing_sync_event = True
        try:
            # Force a complete refresh of data but DO NOT emit signals after refresh
            print("Forcing data refresh (silent)...")
            self._refresh_data_silent()
            print("Data refresh completed")
        except Exception as e:
            print(f"ERROR in products_loaded handler: {e}")
            import traceback
            print(traceback.format_exc())
        finally:
            self._processing_sync_event = False

    def _refresh_data_silent(self):
        """Refresh product data from the database without emitting signals."""
        self.status_label.setText(self.translator.t('loading_products'))

        print("\n===== SMART SEARCH: SILENT DATA REFRESH =====")

        # Define the silent callback function
        def silent_callback(products):
            try:
                print(f"Silently loaded {len(products) if products else 0} products from database")

                # Store the products
                self.products = products
                self.filtered_products = products.copy()

                # Update status
                count = len(products) if products else 0
                self.status_label.setText(self.translator.t('products_loaded', count=count))

                # Clear current results if search box is empty
                if not self.search_edit.text().strip():
                    self._clear_results()
                    self.results_label.setText(self.translator.t('search_results', count=0, total=count))
                else:
                    # Re-run the current search with new data
                    print(f"Re-running current search with new data")
                    self._perform_search()

                print("Silent refresh completed - NOT emitting products_loaded signal")
            except Exception as e:
                logger.error(f"Error processing products (silent): {e}")
                self.status_label.setText(self.translator.t('operation_error'))
                print(f"ERROR in silent callback: {e}")
                import traceback
                print(traceback.format_exc())

        # Use database operator if available
        if self.db_operator:
            # Add debug statement
            print(f"Using DatabaseOperator to get all parts (force_refresh=True, silent mode)")

            # Important: Set force_refresh=True to bypass any caching
            self.db_operator.execute(
                "get_all_parts",
                silent_callback,  # Use the local function directly
                self._on_db_error,
                force_refresh=True
            )
        else:
            # Try direct database access as a fallback
            print(f"DatabaseOperator not available, trying direct database access")
            try:
                if hasattr(self, 'db') and self.db and hasattr(self.db, 'get_all_parts'):
                    parts = self.db.get_all_parts()
                    # Call our local callback function with the parts
                    silent_callback(parts)
                else:
                    logger.error("Database operator not initialized and direct database access not available")
                    self.status_label.setText(self.translator.t('load_error'))
            except Exception as e:
                logger.error(f"Error refreshing data directly: {e}")
                self.status_label.setText(self.translator.t('load_error'))

    def _silent_load_product_suggestions(self):
        """Load product suggestions without emitting signals."""
        if not self.db:
            return

        try:
            # Get all products
            products = self.db.get_all_parts()
            print(f"RegisterWidget: Silently loaded {len(products)} products for suggestions")

            # Set products in the enhanced search box
            if hasattr(self.search_box, 'set_filtered_products'):
                self.search_box.set_filtered_products(products)

            # For legacy compatibility, also maintain the suggestions list
            self.product_suggestions = []

            for product in products:
                if isinstance(product, dict):
                    # Add product name
                    name = product.get('product_name')
                    if name and name not in self.product_suggestions:
                        self.product_suggestions.append(name)

                    # Add parcode
                    parcode = product.get('parcode')
                    if parcode and str(parcode) not in self.product_suggestions:
                        self.product_suggestions.append(str(parcode))

                    # Add manufacturer (helps with searching by brand)
                    manufacturer = product.get('manufacturer')
                    if manufacturer and manufacturer not in self.product_suggestions:
                        self.product_suggestions.append(manufacturer)

                    # Add car brands from compatible_brands
                    compatible_brands = product.get('compatible_brands')
                    if compatible_brands:
                        brands = [brand.strip() for brand in str(compatible_brands).split(',')]
                        for brand in brands:
                            if brand and brand not in self.product_suggestions:
                                self.product_suggestions.append(brand)

            # Update suggestions in the search box if the old method is still supported
            if hasattr(self.search_box, 'update_suggestions'):
                self.search_box.update_suggestions(self.product_suggestions)

            print("RegisterWidget: Completed silent product suggestions update")

        except Exception as e:
            print(f"Error silently loading product suggestions: {e}")
            import traceback
            print(traceback.format_exc())

    def _on_products_loaded(self, products):
        """
        Handle products loaded from the database with loop prevention.

        Args:
            products: List of product dictionaries
        """
        try:
            print("\n===== SMART SEARCH: PRODUCTS LOADED =====")

            if products is not None:
                print(f"Loaded {len(products)} products from database")

                # Store the products
                self.products = products
                self.filtered_products = products.copy()

                # Update status
                count = len(products)
                self.status_label.setText(self.translator.t('products_loaded', count=count))

                # Clear current results if search box is empty
                if not self.search_edit.text().strip():
                    self._clear_results()
                    self.results_label.setText(self.translator.t('search_results', count=0, total=count))
                else:
                    # Re-run the current search with new data
                    print(f"Re-running current search with new data")
                    self._perform_search()

                # Only emit products_loaded signal if this was NOT triggered by a sync event
                # This is the critical part to prevent infinite loops
                if not hasattr(self, '_processing_sync_event') or not self._processing_sync_event:
                    try:
                        from utils.database_sync import db_sync_manager
                        print("Emitting products_loaded signal")
                        db_sync_manager.emit_products_loaded()
                    except Exception as e:
                        logger.error(f"Error emitting products_loaded signal: {e}")
                else:
                    print("NOT emitting products_loaded signal - part of sync event")
            else:
                logger.warning("No products returned from database")
                self.status_label.setText(self.translator.t('load_error'))
                print("WARNING: No products returned from database")
        except Exception as e:
            logger.error(f"Error processing products: {e}")
            self.status_label.setText(self.translator.t('operation_error'))
            print(f"ERROR processing products: {e}")
            import traceback
            print(traceback.format_exc())
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

            logger.info("SmartSearchWidget connected to database sync manager")
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

            logger.info("SmartSearchWidget disconnected from database sync manager")
        except Exception as e:
            logger.error(f"Error disconnecting from sync manager: {e}")


    def create_svg_icon(self, svg_content, color="#000000"):
        """Create a QIcon from SVG content with specified color."""
        # Replace the currentColor with the specified color
        colored_svg = svg_content.replace('currentColor', color)

        # Create a renderer for the SVG
        renderer = QSvgRenderer(QByteArray(colored_svg.encode()))

        # Create a pixmap to render to
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)

        # Render the SVG to the pixmap
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()

        # Return an icon from the pixmap
        return QIcon(pixmap)

    def setup_modern_header_buttons(self):
        """Set up modern filter and sort buttons in the header."""
        # Get the existing buttons
        sort_button = self.findChild(QPushButton, "sortButton")
        filter_button = self.filter_button

        # If buttons don't exist yet, find them by text (fallback)
        if not sort_button:
            for button in self.findChildren(QPushButton):
                if "Sort by Price" in button.text():
                    sort_button = button
                    sort_button.setObjectName("sortButton")
                    break

        if not sort_button or not filter_button:
            logger.warning("Could not find sort or filter buttons")
            return

        # Determine icon color based on theme
        is_dark = get_current_theme() in ["dark", "classic"]
        icon_color = "#FFFFFF" if is_dark else "#3A7BDF"

        # Create icons for the buttons
        filter_icon = self.create_svg_icon(self.FILTER_ICON_SVG, icon_color)
        sort_icon = self.create_svg_icon(self.SORT_ICON_SVG, icon_color)

        # Set up filter button - IMPORTANT: Use translator for text
        filter_button.setIcon(filter_icon)
        filter_button.setText("  " + self.translator.t('filter_button'))  # Add space for icon alignment
        filter_button.setObjectName("modernFilterButton")
        filter_button.setCursor(Qt.PointingHandCursor)
        filter_button.setMinimumWidth(100)

        # Set up sort button - IMPORTANT: Use translator for text
        sort_button.setIcon(sort_icon)
        sort_button.setText("  " + self.translator.t('sort_by_price'))  # Add space for icon alignment
        sort_button.setObjectName("modernSortButton")
        sort_button.setCursor(Qt.PointingHandCursor)
        sort_button.setMinimumWidth(120)

        # Apply modern styling based on theme
        if is_dark:
            button_style = f'''
                QPushButton#modernFilterButton, QPushButton#modernSortButton {{
                    background-color: rgba(255, 255, 255, 0.1);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: 500;
                }}

                QPushButton#modernFilterButton:hover, QPushButton#modernSortButton:hover {{
                    background-color: rgba(255, 255, 255, 0.15);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }}

                QPushButton#modernFilterButton:pressed, QPushButton#modernSortButton:pressed {{
                    background-color: rgba(255, 255, 255, 0.2);
                }}
            '''
        else:
            button_style = f'''
                QPushButton#modernFilterButton, QPushButton#modernSortButton {{
                    background-color: rgba(58, 123, 223, 0.08);
                    color: #3A7BDF;
                    border: 1px solid rgba(58, 123, 223, 0.2);
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: 500;
                }}

                QPushButton#modernFilterButton:hover, QPushButton#modernSortButton:hover {{
                    background-color: rgba(58, 123, 223, 0.15);
                    border: 1px solid rgba(58, 123, 223, 0.3);
                }}

                QPushButton#modernFilterButton:pressed, QPushButton#modernSortButton:pressed {{
                    background-color: rgba(58, 123, 223, 0.25);
                }}
            '''

        filter_button.setStyleSheet(button_style)
        sort_button.setStyleSheet(button_style)

    def _update_products_container_theme(self):
        """Update the products container styling and shadow when theme changes."""
        try:
            if hasattr(self, 'products_container') and self.products_container:
                # Update container styling
                self.products_container.setStyleSheet(f"""
                    QFrame#productsContainer {{
                        background-color: {get_color('card_bg')};
                        border: 1px solid {get_color('border')};
                        border-radius: 10px;
                        padding: 8px;
                    }}
                """)

                # Update shadow effect
                shadow_color = QColor(get_color('shadow'))
                shadow = QGraphicsDropShadowEffect(self.products_container)
                shadow.setBlurRadius(10)
                shadow.setColor(shadow_color)
                shadow.setOffset(0, 2)
                self.products_container.setGraphicsEffect(shadow)

                # Force a repaint
                self.products_container.update()
                self.products_container.repaint()

                logger.debug("Products container theme updated")
        except Exception as e:
            logger.error(f"Error updating products container theme: {e}")

    def _on_theme_changed(self, theme_name):
        """Handle theme change event."""
        try:
            logger.debug(f"SmartSearchWidget: Theme changed to {theme_name}")

            # Apply theme to widget
            self.apply_theme()
            self._apply_global_scrollbar_style()

            # Update all product cards
            for card in self.product_cards:
                if hasattr(card, 'apply_theme'):
                    card.apply_theme()

            # Force products container to update shadow and styling
            self._update_products_container_theme()

            logger.debug("Theme applied to SmartSearchWidget and all product cards")
        except Exception as e:
            logger.error(f"Error applying theme change: {e}")

    def apply_theme(self):
        """Apply a hybrid approach using theme colors with custom styling overrides."""
        try:
            # Get basic colors from the theme system
            background_color = get_color('background')
            text_color = get_color('text')
            border_color = get_color('border')
            card_bg_color = get_color('card_bg')
            text_light_color = get_color('secondary_text')
            input_bg_color = get_color('input_bg')

            # Standard button colors from theme
            std_button_color = get_color('button')
            std_button_hover = get_color('button_hover')
            std_button_pressed = get_color('button_pressed')
            std_button_disabled = get_color('button_disabled')

            # Determine current theme for context-specific styling
            current_theme = get_current_theme()
            is_dark = current_theme in ["dark", "classic"]

            # Custom colors for specific elements (regardless of theme)
            primary_blue = "#3A7BDF"
            primary_blue_hover = "#5193FF"
            primary_blue_pressed = "#2A5CBF"
            fab_color = "#FF9800"  # Orange
            fab_hover = "#f57c00"
            fab_pressed = "#ef6c00"

            # Theme-dependent custom colors
            if is_dark:
                secondary_bg = "rgba(70, 70, 90, 0.7)"
                secondary_hover = "rgba(80, 80, 100, 0.8)"
                shadow_color = "rgba(0, 0, 0, 0.25)"
                card_highlight = "rgba(255, 255, 255, 0.05)"
            else:
                secondary_bg = "#F0F4FA"
                secondary_hover = "#E8EDF7"
                shadow_color = "rgba(0, 0, 0, 0.1)"
                card_highlight = "rgba(0, 0, 0, 0.02)"

            # Full comprehensive styling
            self.setStyleSheet(f"""
                /* Main Widget */
                QWidget#smartSearchWidget {{
                    background-color: {background_color};
                    color: {text_color};
                }}

                /* Title Container */
                QFrame#titleContainer {{
                    background-color: transparent;
                    margin-bottom: 10px;
                }}

                QLabel#smartSearchTitle {{
                    color: {text_color};
                    font-size: {get_font_size('title')}px;
                    font-weight: bold;
                }}

                /* Search Container - card-like appearance */
                QFrame#searchContainer {{
                    background-color: {card_bg_color};
                    border: 1px solid {border_color};
                    border-radius: 10px;
                }}

                QLabel#searchTypeNote {{
                    color: {text_light_color};
                    font-size: 13px;
                    font-style: italic;
                    padding-top: 4px;
                }}

                /* Modern search input */
                QLineEdit#smartSearchEdit {{
                    background-color: {input_bg_color};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: 10px;
                    padding: 0px 15px;
                    min-height: 36px;
                    max-height: 36px;
                }}

                QLineEdit#smartSearchEdit:focus {{
                    border: 1px solid {primary_blue};
                }}

                /* CUSTOM: Search Button - always use custom blue */
                QPushButton#searchButton {{
                    background-color: {primary_blue};
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 0px 24px;
                    font-size: 14px;
                    font-weight: 600;
                    min-height: 36px;
                    max-height: 36px;
                    min-width: 100px;
                    max-width: 100px;
                    white-space: nowrap;
                }}

                QPushButton#searchButton:hover {{
                    background-color: {primary_blue_hover};
                }}

                QPushButton#searchButton:pressed {{
                    background-color: {primary_blue_pressed};
                }}

                /* CUSTOM: Toggle Group - elegant gradient background */
                QFrame#toggleGroup {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2A5CBF, stop:1 #3A7BDF);
                    border-radius: 8px;
                    padding: 2px;
                    min-width: 280px;
                    max-width: 280px;
                    min-height: 36px;
                    max-height: 36px;
                }}

                /* Base toggle button styling */
                QPushButton#productNameToggle, 
                QPushButton#barcodeToggle {{
                    background-color: transparent;
                    color: rgba(255, 255, 255, 0.8);
                    border: none;
                    border-radius: 6px;
                    padding: 0px 12px;
                    font-size: 13px;
                    font-weight: 500;
                    letter-spacing: 0.3px;
                    min-height: 32px;
                    max-height: 32px;
                    text-align: center;
                }}

                /* Selected toggle button */
                QPushButton#productNameToggle:checked, 
                QPushButton#barcodeToggle:checked {{
                    background-color: rgba(70, 150, 255, 0.6);
                    color: white;
                    font-weight: 600;
                    border-bottom: 2px solid rgba(255, 255, 255, 0.8);
                }}

                /* Hover effect for unselected buttons */
                QPushButton#productNameToggle:hover:!checked, 
                QPushButton#barcodeToggle:hover:!checked {{
                    background-color: rgba(70, 150, 255, 0.3);
                    color: white;
                }}

                /* Pressed effect */
                QPushButton#productNameToggle:pressed, 
                QPushButton#barcodeToggle:pressed {{
                    background-color: rgba(70, 150, 255, 0.5);
                }}

                /* Results Header - using theme secondary bg */
                QFrame#resultsHeader {{
                    background-color: {secondary_bg};
                    border-bottom: 1px solid {border_color};
                    border-top-left-radius: 10px;
                    border-top-right-radius: 10px;
                }}

                QLabel#resultsTitle {{
                    color: {text_color};
                    font-size: {get_font_size('regular')}px;
                    font-weight: bold;
                }}

                QLabel#resultsLabel {{
                    color: {text_light_color};
                    font-size: {get_font_size('regular')}px;
                    margin-left: 5px;
                }}

                /* Results Container */
                QFrame#resultsContainer {{
                    background-color: transparent;
                }}

                QWidget#contentContainer {{
                    background-color: transparent;
                }}

                /* Products Container */
                QFrame#productsContainer {{
                    background-color: {card_bg_color};
                    border: 1px solid {border_color};
                    border-radius: 10px;
                }}

                /* Status Container */
                QFrame#statusContainer {{
                    background-color: {secondary_bg};
                    border-top: 1px solid {border_color};
                    border-bottom-left-radius: 10px;
                    border-bottom-right-radius: 10px;
                }}

                QLabel#statusLabel {{
                    color: {text_light_color};
                    font-size: {get_font_size('regular')}px;
                }}

                /* Refresh Button - use theme colors */
                QPushButton#refreshButton {{
                    background-color: {secondary_bg};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: 4px;
                    padding: 6px 12px;
                }}

                QPushButton#refreshButton:hover {{
                    background-color: {secondary_hover};
                    border-color: {primary_blue};
                }}

                /* CUSTOM: Circular FAB */
                QPushButton#circularFab {{
                    background-color: {fab_color};
                    color: white;
                    font-size: 28px;
                    font-weight: bold;
                    border-radius: 30px;
                    min-width: 60px;
                    max-width: 60px;
                    min-height: 60px;
                    max-height: 60px;
                    padding: 0px;
                    border: none;
                    text-align: center;
                    qproperty-alignment: AlignCenter;
                }}

                QPushButton#circularFab:hover {{
                    background-color: {fab_hover};
                }}

                QPushButton#circularFab:pressed {{
                    background-color: {fab_pressed};
                }}

                QPushButton#circularFab:disabled {{
                    background-color: {std_button_disabled};
                    color: {text_light_color};
                }}

                /* Modern Scrollbar styling */
                QScrollArea#resultsScrollArea QScrollBar:vertical {{
                    background-color: transparent;
                    width: 8px;
                    margin: 2px 2px 2px 2px;
                    border-radius: 4px;
                }}

                QScrollArea#resultsScrollArea QScrollBar::handle:vertical {{
                    background-color: {text_light_color}80; /* 50% opacity */
                    min-height: 40px;
                    border-radius: 4px;
                }}

                QScrollArea#resultsScrollArea QScrollBar::handle:vertical:hover {{
                    background-color: {std_button_color};
                }}

                QScrollArea#resultsScrollArea QScrollBar::add-line:vertical,
                QScrollArea#resultsScrollArea QScrollBar::sub-line:vertical {{
                    height: 0px;
                    background: none;
                }}

                QScrollArea#resultsScrollArea QScrollBar::add-page:vertical,
                QScrollArea#resultsScrollArea QScrollBar::sub-page:vertical {{
                    background: none;
                }}

                /* No results message */
                QLabel#noResultsLabel {{
                    color: {text_light_color};
                    font-size: {get_font_size('large')}px;
                    font-style: italic;
                    background-color: transparent;
                    border: 1px dashed {border_color};
                    border-radius: 8px;
                    padding: 20px;
                }}
            """)

            # Make sure dropdown element themes are updated
            if hasattr(self, 'search_edit'):
                self.search_edit.apply_theme()
                if hasattr(self.search_edit, 'dropdown'):
                    self.search_edit.dropdown.apply_theme()

            # Update FAB styling
            if hasattr(self, 'fab'):
                self.fab.setToolTip(self.translator.t('duplicate_product'))
                self.fab.setText("+")
                # Apply shadow effect for Material Design look
                shadow = QGraphicsDropShadowEffect(self.fab)
                shadow.setBlurRadius(10)
                shadow.setColor(QColor(0, 0, 0, 80))
                shadow.setOffset(0, 3)
                self.fab.setGraphicsEffect(shadow)

            # Update search type note if present
            if hasattr(self, 'search_type_note'):
                # Update based on search mode and text
                search_text = self.search_edit.text().strip()
                if search_text:
                    if self.search_edit.search_mode == 'barcode':
                        self.search_type_note.setText(f'Searching by exact barcode: "{search_text}"')
                    else:
                        self.search_type_note.setText(f'Searching by exact name: "{search_text}"')
                else:
                    self.search_type_note.setText("")

            # Update product cards styling
            for card in self.product_cards:
                if hasattr(card, 'apply_theme'):
                    card.apply_theme()

            # Special FAB handling for position
            if hasattr(self, 'fab'):
                # Position FAB in bottom right corner
                self.fab.raise_()
                self.fab.move(self.width() - 80, self.height() - 80)

            # Update header buttons with modern styling
            self.setup_modern_header_buttons()

            # Update products container theme
            self._update_products_container_theme()

        except Exception as e:
            logger.error(f"Error applying theme: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def showEvent(self, event):
        """Handle show events for the widget."""
        super().showEvent(event)

        # Make sure the FAB is properly positioned and visible only if needed
        if hasattr(self, 'fab'):
            # Position the FAB
            self.fab.move(self.width() - 80, self.height() - 80)

            # Check if we already have search results
            if hasattr(self, 'product_cards') and self.product_cards:
                self.fab.setEnabled(True)
                self.fab.show()
                self.fab.raise_()
            else:
                # No search results yet - hide the FAB
                self.fab.hide()

            # Set a flag to indicate this widget is now visible
            self._is_visible = True

            # If search edit has focus, check for text and perform search if needed
            if hasattr(self, 'search_edit') and self.search_edit.hasFocus() and self.search_edit.text().strip():
                # Schedule a search after the show event completes
                QTimer.singleShot(0, self._perform_search)

    def hideEvent(self, event):
        """Handle hide events for the widget."""
        super().hideEvent(event)

        # Ensure the FAB is hidden when the widget is hidden
        if hasattr(self, 'fab'):
            self.fab.hide()

    def resizeEvent(self, event):
        """Handle resize events to keep FAB positioned correctly."""
        super().resizeEvent(event)

        # Reposition FAB when widget is resized
        if hasattr(self, 'fab'):
            self.fab.move(self.width() - 80, self.height() - 80)

            # Only show if we have results and the widget is visible
            if self.isVisible() and hasattr(self, 'product_cards') and self.product_cards:
                self.fab.show()
                self.fab.raise_()

    def toggle_search_mode(self, mode):
        """
        Toggle between search modes (product name or barcode).

        Args:
            mode: The search mode to set ('product_name' or 'barcode')
        """
        # Update the search mode in the search edit
        if hasattr(self, 'search_edit') and self.search_edit:
            self.search_edit.search_mode = mode

            # Update placeholder text based on mode
            if mode == 'barcode':
                self.search_edit.setPlaceholderText(self.translator.t('search_by_barcode_placeholder'))
            else:
                self.search_edit.setPlaceholderText(self.translator.t('search_by_name_placeholder'))

        # Update search type note
        if hasattr(self, 'search_type_note') and self.search_type_note:
            search_text = self.search_edit.text().strip()
            if search_text:
                if mode == 'barcode':
                    self.search_type_note.setText(self.translator.t('searching_by_barcode', search_text=search_text))
                else:
                    self.search_type_note.setText(self.translator.t('searching_by_name', search_text=search_text))
            else:
                self.search_type_note.setText("")

        # If we have search text, perform a search with the new mode
        if self.search_edit.text().strip():
            self._perform_search()

    def _handle_product_name_toggle(self):
        """Handle product name toggle button click."""
        if self.product_name_toggle.isChecked():
            # Block signals to prevent recursion
            self.barcode_toggle.blockSignals(True)
            self.barcode_toggle.setChecked(False)
            self.barcode_toggle.blockSignals(False)
            # Update search mode
            self.toggle_search_mode('product_name')
        else:
            # Don't allow both buttons to be unchecked
            self.product_name_toggle.blockSignals(True)
            self.product_name_toggle.setChecked(True)
            self.product_name_toggle.blockSignals(False)

    def _handle_barcode_toggle(self):
        """Handle barcode toggle button click."""
        if self.barcode_toggle.isChecked():
            # Block signals to prevent recursion
            self.product_name_toggle.blockSignals(True)
            self.product_name_toggle.setChecked(False)
            self.product_name_toggle.blockSignals(False)
            # Update search mode
            self.toggle_search_mode('barcode')
        else:
            # Don't allow both buttons to be unchecked
            self.barcode_toggle.blockSignals(True)
            self.barcode_toggle.setChecked(True)
            self.barcode_toggle.blockSignals(False)

    def update_translations(self):
        """Update all translations when language changes."""
        try:
            # Update static text elements
            if hasattr(self, 'search_edit'):
                self.search_edit.setPlaceholderText(self.translator.t('search_placeholder'))

            if hasattr(self, 'filter_button'):
                # Update both text AND tooltip for filter button
                self.filter_button.setToolTip(self.translator.t('filter_button'))
                self.filter_button.setText(self.translator.t('filter_button'))

            # Update sort button
            sort_button = self.findChild(QPushButton, "sortButton")
            if sort_button:
                sort_button.setText(self.translator.t('sort_by_price'))

            if hasattr(self, 'barcode_button'):
                # For icon-only button, just update tooltip
                self.barcode_button.setToolTip(self.translator.t('scan_barcode_tooltip'))

            if hasattr(self, 'status_label'):
                self.status_label.setText(self.translator.t('status_ready'))

            if hasattr(self, 'fab'):
                self.fab.setToolTip(self.translator.t('duplicate_product'))
                # Don't change the + symbol
                self.fab.setText("+")

            # Update toggle button texts while preserving icons
            if hasattr(self, 'barcode_toggle'):
                if self.barcode_toggle.icon().isNull():
                    # Only has text with Unicode icon
                    self.barcode_toggle.setText("▤ " + self.translator.t('search_by_barcode'))
                else:
                    # Has proper icon
                    self.barcode_toggle.setText(self.translator.t('search_by_barcode'))

            if hasattr(self, 'product_name_toggle'):
                if self.product_name_toggle.icon().isNull():
                    # Only has text with Unicode icon
                    self.product_name_toggle.setText("🔍 " + self.translator.t('search_by_name'))
                else:
                    # Has proper icon
                    self.product_name_toggle.setText(self.translator.t('search_by_name'))

            # Update Show More/Less button
            if hasattr(self, 'show_more_button'):
                if self.is_expanded if hasattr(self, 'is_expanded') else False:
                    self.show_more_button.setText(self.translator.t('show_less'))
                else:
                    self.show_more_button.setText(self.translator.t('show_more'))

            # Update results title
            results_title = self.findChild(QLabel, "resultsTitle")
            if results_title:
                results_title.setText(self.translator.t('search_results_title'))

            # Update results label
            if hasattr(self, 'results_label'):
                current_text = self.results_label.text()
                if self.products:
                    # Try to extract current count from text
                    count = 0
                    total = len(self.products)
                    try:
                        # Parse current text to keep count
                        import re
                        match = re.search(r'(\d+)', current_text)
                        if match:
                            count = int(match.group(1))
                    except:
                        # If parsing fails, use 0
                        count = 0

                    self.results_label.setText(
                        self.translator.t('search_results', count=count, total=total)
                    )
                else:
                    self.results_label.setText(
                        self.translator.t('search_results', count=0, total=0)
                    )

            # Update search button if exists
            search_button = self.findChild(QPushButton, "searchButton")
            if search_button:
                search_button.setText(self.translator.t('search_products'))

            # Update refresh button if exists
            refresh_button = self.findChild(QPushButton, "refreshButton")
            if refresh_button:
                refresh_button.setText(self.translator.t('refresh'))

            # Update search type note
            if hasattr(self, 'search_type_note') and hasattr(self, 'search_edit'):
                search_text = self.search_edit.text().strip()
                if search_text:
                    if self.search_edit.search_mode == 'barcode':
                        self.search_type_note.setText(
                            self.translator.t('searching_by_barcode', search_text=search_text)
                        )
                    else:
                        self.search_type_note.setText(
                            self.translator.t('searching_by_name', search_text=search_text)
                        )
                else:
                    self.search_type_note.setText("")

            # Update title label
            title_label = self.findChild(QLabel, "smartSearchTitle")
            if title_label:
                title_label.setText(self.translator.t('smart_search_button'))

            # Update product cards if any exist
            for card in self.product_cards:
                if hasattr(card, 'update_translations'):
                    card.update_translations()
                else:
                    # Cards would need to be recreated with new translations
                    # This is a fallback if cards don't have their own update method
                    pass

            # Refresh the UI to reflect language changes
            self._refresh_data()
        except Exception as e:
            logger.error(f"Error updating translations: {e}")

    def _perform_search(self):
        """Perform search with current search text and filters using exact matching."""
        search_text = self.search_edit.text().strip().lower()
        self.last_search = search_text  # Track the search term

        if not search_text:
            self._clear_results()
            if self.products:
                self.results_label.setText(
                    self.translator.t('search_results', count=0, total=len(self.products))
                )
            return

        try:
            # Find all products matching the search term
            matching_products = []
            search_words = search_text.split()

            for product in self.filtered_products:
                if product_matches_search(product, search_text, search_words):
                    matching_products.append(product)

            # Filter to only exact product name matches
            exact_matches = []
            for product in matching_products:
                # Get product name to check against
                if isinstance(product, dict):
                    product_name = str(product.get('product_name', '')).lower()
                else:  # tuple
                    product_name = str(product[2]).lower() if len(product) > 2 else ''

                # Only include exact matches
                if product_name == search_text:
                    exact_matches.append(product)

            # Update the search results with exact matches only
            self.search_results = exact_matches
            count = len(exact_matches)
            total = len(self.products)

            # Update the results label
            if count == 0:
                self.results_label.setText(
                    f"No exact matches found for '{search_text}' (out of {total} products)"
                )
            else:
                self.results_label.setText(
                    f"Found {count} exact matches for '{search_text}' (out of {total} products)"
                )

            # Display the exact matches
            self._display_results(exact_matches)

            logger.debug(f"Exact match search for '{search_text}' found {count} results")
        except Exception as e:
            logger.error(f"Error performing search: {e}")
            self.status_label.setText(self.translator.t('operation_error'))

    def _show_barcode_scanner(self):
        """Show the barcode scanner dialog."""
        try:
            # Create dialog via adapter
            dialog = BarcodeDialogAdapter.create_dialog(self, self.translator)

            # Connect the signal if it exists
            if hasattr(dialog, 'barcode_scanned'):
                dialog.barcode_scanned.connect(self._handle_barcode_scanned)

            # Show dialog modally
            result = dialog.exec_()

            # If rejected, do nothing
            if result == QDialog.Rejected:
                return
        except Exception as e:
            logger.error(f"Error showing barcode scanner dialog: {e}")
            QMessageBox.critical(
                self,
                self.translator.t('error'),
                self.translator.t('operation_error')
            )

    def _handle_barcode_scanned(self, barcode):
        """
        Handle a scanned barcode.

        Args:
            barcode: The scanned barcode string
        """
        # Set the barcode as the search text
        if hasattr(self, 'search_edit') and self.search_edit:
            self.search_edit.setText(barcode)
            # Perform search
            self._perform_search()

        # Update status
        if hasattr(self, 'status_label') and self.status_label:
            self.status_label.setText(
                self.translator.t('barcode_scanned', barcode=barcode)
            )

        logger.info(f"Barcode scanned: {barcode}")

    def _reset_filters(self, dialog=None):
        """
        Reset all filters.

        Args:
            dialog: Optional filter dialog to close
        """
        self.current_filter = {}
        self.filtered_products = self.products.copy()
        self.last_search = None  # Clear last search

        # Update display
        if self.search_edit.text().strip():
            self._perform_search()
        else:
            self._clear_results()
            if self.products:
                total = len(self.products)
                self.results_label.setText(self.translator.t('search_results', count=0, total=total))

        self.status_label.setText(
            self.translator.t('filter_status', count=len(self.filtered_products), total=len(self.products)))

        # Close dialog if provided
        if dialog:
            dialog.reject()

    def _apply_global_scrollbar_style(self):
        """Apply consistent modern scrollbar styling across the application."""
        try:
            app = QApplication.instance()
            if app:
                app.setStyleSheet(app.styleSheet() + f"""
                    /* Global Modern Scrollbar Style */
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

                    QScrollBar:horizontal {{
                        background-color: transparent;
                        height: 8px;
                        margin: 2px 2px 2px 2px;
                        border-radius: 4px;
                    }}

                    QScrollBar::handle:horizontal {{
                        background-color: {get_color('secondary_text')}80; /* 50% opacity */
                        min-width: 40px;
                        border-radius: 4px;
                    }}

                    QScrollBar::handle:horizontal:hover {{
                        background-color: {get_color('highlight')};
                    }}

                    QScrollBar::add-line:horizontal,
                    QScrollBar::sub-line:horizontal {{
                        width: 0px;
                        background: none;
                    }}

                    QScrollBar::add-page:horizontal,
                    QScrollBar::sub-page:horizontal {{
                        background: none;
                    }}
                """)
        except Exception as e:
            logger.error(f"Error applying global scrollbar style: {e}")

    def _display_results(self, results):
        """
        Display search results as elegant cards with enhanced container styling.

        Args:
            results: List of product dictionaries
        """
        # Clear current content
        self._clear_results()

        # Apply enhanced styling to the products container
        self._update_products_container_theme()

        if not results:
            # No results found - show an elegant message with refined styling
            no_results = QLabel(self.translator.t('no_data_to_export'))
            no_results.setObjectName("noResultsLabel")
            no_results.setAlignment(Qt.AlignCenter)
            no_results.setWordWrap(True)
            no_results.setMargin(40)  # Add more padding

            self.products_layout.addWidget(no_results)

            # Disable AND hide the FAB when no results are shown
            self.fab.setEnabled(False)
            self.fab.hide()
            return

        # Create a container to center the cards
        centered_container = QWidget()
        centered_container.setObjectName("centeredCardsContainer")
        centered_layout = QVBoxLayout(centered_container)
        centered_layout.setContentsMargins(8, 8, 8, 8)
        centered_layout.setAlignment(Qt.AlignHCenter)  # Center-align the cards horizontally
        centered_layout.setSpacing(16)  # Increased spacing between cards for elegant look

        # Reset product cards list
        self.product_cards = []

        # Add each product as an enhanced card to the centered container
        for product in results:
            try:
                card = ProductCard(
                    product,
                    self.translator,
                    self._edit_product,
                    self._delete_product
                )

                # Add to our tracking list
                self.product_cards.append(card)

                # Add cards to the centered container
                centered_layout.addWidget(card)

                # Add some visual space between cards
                if product != results[-1]:  # If not the last item
                    spacer = QFrame()
                    spacer.setFrameShape(QFrame.HLine)
                    spacer.setFrameShadow(QFrame.Sunken)
                    spacer.setMaximumHeight(1)
                    spacer.setStyleSheet(f"""
                        background-color: {get_color('border')}30; /* 30% opacity */
                        margin: 0px 40px;
                    """)
                    centered_layout.addWidget(spacer)
            except Exception as e:
                logger.error(f"Error creating product card: {e}")

        # Add centered container to the main layout
        self.products_layout.addWidget(centered_container)

        # Add a stretch at the end to push all content to the top
        self.products_layout.addStretch(1)

        # Enable and show the FAB when we have results
        self.fab.setEnabled(True)

        # Ensure FAB is properly positioned before showing
        if self.isVisible():
            self.fab.move(self.width() - 80, self.height() - 80)
            self.fab.show()
            self.fab.raise_()  # Make sure it's on top

            # Force immediate processing of show event
            QApplication.processEvents()
        else:
            # If widget isn't visible yet, setup a timer to show FAB after it becomes visible
            QTimer.singleShot(100, self._position_and_show_fab)

    def _position_and_show_fab(self):
        """Position and show the FAB if the widget is visible and has results."""
        if self.isVisible() and hasattr(self, 'product_cards') and self.product_cards:
            # Position the FAB before showing it
            self.fab.move(self.width() - 80, self.height() - 80)
            self.fab.setEnabled(True)
            self.fab.show()
            self.fab.raise_()  # Make sure it's on top

    def _clear_results(self):
        """Clear current search results."""
        # Reset product cards list
        self.product_cards = []

        # Remove all widgets from the layout
        while self.products_layout.count():
            item = self.products_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Disable and hide the FAB when no results are shown
        self.fab.setEnabled(False)
        self.fab.hide()

    def _show_filter_dialog(self):
        """Show dialog for filtering products."""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle(self.translator.t('filter_title'))
            dialog.setMinimumWidth(400)

            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(20, 20, 20, 20)  # More padding
            layout.setSpacing(15)  # More spacing

            # Create filter widgets with better styling
            form_layout = QFormLayout()
            form_layout.setSpacing(12)

            category_filter = QLineEdit()
            category_filter.setPlaceholderText(self.translator.t('category_placeholder'))
            category_filter.setMinimumHeight(35)
            if 'category' in self.current_filter:
                category_filter.setText(self.current_filter['category'])

            min_price = QDoubleSpinBox()
            min_price.setRange(0, 999999.99)
            min_price.setPrefix("$")
            min_price.setSpecialValueText(self.translator.t('no_min_price'))
            min_price.setMinimumHeight(35)
            if 'min_price' in self.current_filter:
                min_price.setValue(self.current_filter['min_price'])

            max_price = QDoubleSpinBox()
            max_price.setRange(0, 999999.99)
            max_price.setPrefix("$")
            max_price.setSpecialValueText(self.translator.t('no_max_price'))
            max_price.setMinimumHeight(35)
            if 'max_price' in self.current_filter:
                max_price.setValue(self.current_filter['max_price'])

            min_quantity = QSpinBox()
            min_quantity.setRange(0, 9999)
            min_quantity.setSpecialValueText(self.translator.t('min'))
            min_quantity.setMinimumHeight(35)
            if 'min_quantity' in self.current_filter:
                min_quantity.setValue(self.current_filter['min_quantity'])

            in_stock_only = QCheckBox(self.translator.t('in_stock_only'))
            if 'in_stock_only' in self.current_filter:
                in_stock_only.setChecked(self.current_filter['in_stock_only'])

            # Add manufacturer filter
            manufacturer_filter = QLineEdit()
            manufacturer_filter.setPlaceholderText(self.translator.t('manufacturer_placeholder'))
            manufacturer_filter.setMinimumHeight(35)
            if 'manufacturer' in self.current_filter:
                manufacturer_filter.setText(self.current_filter['manufacturer'])

            # Add original parts filter
            original_only = QCheckBox(self.translator.t('original_only'))
            if 'original_only' in self.current_filter:
                original_only.setChecked(self.current_filter['original_only'])

            # Add widgets to form
            form_layout.addRow(self.translator.t('category'), category_filter)
            form_layout.addRow(self.translator.t('min'), min_price)
            form_layout.addRow(self.translator.t('max'), max_price)
            form_layout.addRow(self.translator.t('quantity'), min_quantity)
            form_layout.addRow("", in_stock_only)
            form_layout.addRow(self.translator.t('manufacturer'), manufacturer_filter)
            form_layout.addRow("", original_only)

            layout.addLayout(form_layout)

            # Buttons with better styling
            button_layout = QHBoxLayout()
            button_layout.setSpacing(12)

            apply_button = QPushButton(self.translator.t('apply_filter'))
            apply_button.setObjectName("primaryButton")
            apply_button.setMinimumHeight(40)

            reset_button = QPushButton(self.translator.t('reset'))
            reset_button.setMinimumHeight(40)

            cancel_button = QPushButton(self.translator.t('cancel'))
            cancel_button.setMinimumHeight(40)

            button_layout.addWidget(apply_button)
            button_layout.addWidget(reset_button)
            button_layout.addWidget(cancel_button)

            layout.addLayout(button_layout)

            # Connect buttons
            apply_button.clicked.connect(dialog.accept)
            reset_button.clicked.connect(lambda: self._reset_filters(dialog))
            cancel_button.clicked.connect(dialog.reject)

            # Apply elegant styling to dialog
            try:
                apply_dialog_theme(dialog, self.translator.t('filter_title'))
            except Exception as e:
                logger.warning(f"Could not apply dialog theme: {e}")
                # Apply manual dialog styling
                dialog.setStyleSheet(f"""
                    QDialog {{
                        background-color: {get_color('background')};
                        color: {get_color('text')};
                    }}
                    QLabel {{
                        color: {get_color('text')};
                    }}
                    QLineEdit, QSpinBox, QDoubleSpinBox {{
                        background-color: {get_color('input_bg')};
                        color: {get_color('text')};
                        border: 1px solid {get_color('border')};
                        padding: 5px;
                        border-radius: {get_size('tiny')}px;
                    }}
                    QCheckBox {{
                        color: {get_color('text')};
                    }}
                    QPushButton {{
                        background-color: {get_color('secondary')};
                        color: {get_color('text')};
                        border-radius: {get_size('tiny')}px;
                        padding: 8px 16px;
                    }}
                    QPushButton#primaryButton {{
                        background-color: {get_color('button')};
                        color: white;
                    }}
                    QPushButton:hover {{
                        background-color: {get_color('button_hover')};
                    }}
                """)

            # Show dialog and process result
            if dialog.exec_() == QDialog.Accepted:
                # Apply filters
                self.current_filter = {
                    'category': category_filter.text(),
                    'min_price': min_price.value() if min_price.value() > 0 else None,
                    'max_price': max_price.value() if max_price.value() > 0 else None,
                    'min_quantity': min_quantity.value(),
                    'in_stock_only': in_stock_only.isChecked(),
                    'manufacturer': manufacturer_filter.text(),
                    'original_only': original_only.isChecked()
                }

                self._apply_filters()
        except Exception as e:
            logger.error(f"Error showing filter dialog: {e}")
            QMessageBox.critical(
                self,
                self.translator.t('dialog_error'),
                self.translator.t('operation_error')
            )

    def _apply_filters(self):
        """Apply current filters to the product list."""
        try:
            # Start with all products
            filtered = self.products.copy()

            # Apply each filter
            if 'category' in self.current_filter and self.current_filter['category']:
                category = self.current_filter['category'].lower()
                filtered = [p for p in filtered if p.get('category', '').lower().find(category) >= 0]

            if 'min_price' in self.current_filter and self.current_filter['min_price'] is not None:
                min_price = self.current_filter['min_price']
                filtered = [p for p in filtered if p.get('price', 0) >= min_price]

            if 'max_price' in self.current_filter and self.current_filter['max_price'] is not None:
                max_price = self.current_filter['max_price']
                filtered = [p for p in filtered if p.get('price', 0) <= max_price]

            if 'min_quantity' in self.current_filter and self.current_filter['min_quantity'] > 0:
                min_qty = self.current_filter['min_quantity']
                filtered = [p for p in filtered if p.get('quantity', 0) >= min_qty]

            if 'in_stock_only' in self.current_filter and self.current_filter['in_stock_only']:
                filtered = [p for p in filtered if p.get('quantity', 0) > 0]

            # New filters for manufacturer and original
            if 'manufacturer' in self.current_filter and self.current_filter['manufacturer']:
                manufacturer = self.current_filter['manufacturer'].lower()
                filtered = [p for p in filtered if p.get('manufacturer', '').lower().find(manufacturer) >= 0]

            if 'original_only' in self.current_filter and self.current_filter['original_only']:
                filtered = [p for p in filtered if p.get('original', 0) == 1]

            # Update filtered products
            self.filtered_products = filtered

            # Update display
            if self.search_edit.text().strip():
                self._perform_search()
            else:
                self._clear_results()
                if self.products:
                    total = len(self.products)
                    self.results_label.setText(self.translator.t('search_results', count=0, total=total))

            # Update status
            self.status_label.setText(
                self.translator.t('filter_status', count=len(filtered), total=len(self.products))
            )

            logger.debug(f"Applied filters. Results: {len(filtered)} of {len(self.products)}")
        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            self.status_label.setText(self.translator.t('filter_error'))

    def _edit_product(self, product):
        """
        Open dialog to edit a product.

        Args:
            product: Product dictionary to edit
        """
        try:
            # Simple edit dialog - in a real implementation, use a more sophisticated editor
            dialog = QDialog(self)
            dialog.setWindowTitle(self.translator.t('product_details'))
            dialog.setMinimumWidth(450)  # Slightly wider for better appearance

            layout = QFormLayout(dialog)
            layout.setContentsMargins(20, 20, 20, 20)  # More padding
            layout.setSpacing(15)  # More spacing

            # Create edit fields with better styling
            name_edit = QLineEdit(product.get('product_name', ''))
            name_edit.setMinimumHeight(35)

            category_edit = QLineEdit(product.get('category', ''))
            category_edit.setMinimumHeight(35)

            price_edit = QDoubleSpinBox()
            price_edit.setRange(0, 999999.99)
            price_edit.setValue(product.get('price', 0))
            price_edit.setPrefix("$")
            price_edit.setDecimals(2)
            price_edit.setMinimumHeight(35)

            quantity_edit = QSpinBox()
            quantity_edit.setRange(0, 9999)
            quantity_edit.setValue(product.get('quantity', 0))
            quantity_edit.setMinimumHeight(35)

            # Add manufacturer field
            manufacturer_edit = QLineEdit(product.get('manufacturer', ''))
            manufacturer_edit.setMinimumHeight(35)

            # Add original part checkbox
            original_check = QCheckBox()
            original_check.setChecked(bool(product.get('original', False)))

            # Add fields to form
            layout.addRow(self.translator.t('product_name'), name_edit)
            layout.addRow(self.translator.t('category'), category_edit)
            layout.addRow(self.translator.t('price'), price_edit)
            layout.addRow(self.translator.t('quantity'), quantity_edit)
            layout.addRow(self.translator.t('manufacturer'), manufacturer_edit)
            layout.addRow(self.translator.t('original'), original_check)

            # Buttons
            button_layout = QHBoxLayout()
            button_layout.setSpacing(12)

            save_button = QPushButton(self.translator.t('save'))
            save_button.setObjectName("primaryButton")
            save_button.setMinimumHeight(40)

            cancel_button = QPushButton(self.translator.t('cancel'))
            cancel_button.setMinimumHeight(40)

            button_layout.addWidget(save_button)
            button_layout.addWidget(cancel_button)
            layout.addRow("", button_layout)

            # Connect buttons
            save_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)

            # Apply elegant styling to dialog
            try:
                apply_dialog_theme(dialog, self.translator.t('product_details'))
            except Exception as e:
                logger.warning(f"Could not apply dialog theme: {e}")
                # Apply basic styling for the dialog
                dialog.setStyleSheet(f"""
                    QDialog {{
                        background-color: {get_color('background')};
                    }}
                    QLabel {{
                        color: {get_color('text')};
                    }}
                    QLineEdit, QSpinBox, QDoubleSpinBox {{
                        background-color: {get_color('input_bg')};
                        color: {get_color('text')};
                        border: 1px solid {get_color('border')};
                        border-radius: {get_size('tiny')}px;
                        padding: 5px;
                    }}
                    QPushButton {{
                        background-color: {get_color('button')};
                        color: white;
                        border-radius: {get_size('tiny')}px;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        background-color: {get_color('button_hover')};
                    }}
                    QPushButton:pressed {{
                        background-color: {get_color('button_pressed')};
                    }}
                """)

            # Show dialog and process result
            if dialog.exec_() == QDialog.Accepted:
                # Validate
                if not name_edit.text().strip():
                    QMessageBox.warning(
                        self,
                        self.translator.t('validation_error'),
                        self.translator.t('name_required')
                    )
                    return

                # Get product values
                new_product_name = name_edit.text()
                new_category = category_edit.text()
                new_price = price_edit.value()
                new_quantity = quantity_edit.value()
                new_manufacturer = manufacturer_edit.text()
                new_original = original_check.isChecked()

                # Access direct database object through the database operator
                direct_db = None
                if hasattr(self.db_operator, 'db'):
                    direct_db = self.db_operator.db
                elif hasattr(self, 'db'):
                    direct_db = self.db

                if direct_db and hasattr(direct_db, 'update_part'):
                    # Get the parcode value
                    parcode = product.get('parcode')

                    # Find the product by parcode first
                    try:
                        # First we need to find the product ID for this parcode
                        # Get all parts (not ideal but works for small datasets)
                        parts = direct_db.get_all_parts()
                        part_id = None

                        # Find the part with matching parcode
                        for part in parts:
                            if part.get('parcode') == parcode:
                                part_id = part.get('id')
                                break

                        if part_id:
                            # Now update using the numeric ID
                            update_dict = {
                                'product_name': new_product_name,
                                'category': new_category,
                                'price': new_price,
                                'quantity': new_quantity,
                                'manufacturer': new_manufacturer,
                                'original': 1 if new_original else 0
                            }

                            # Update directly using the database
                            success = direct_db.update_part(part_id, **update_dict)

                            if success:
                                self.status_label.setText(self.translator.t('product_updated'))
                                QMessageBox.information(
                                    self,
                                    self.translator.t('success'),
                                    self.translator.t('product_updated')
                                )

                                # Emit signal for product update
                                try:
                                    from utils.database_sync import db_sync_manager
                                    # Create updated product data from original and updates
                                    updated_product_data = product.copy()  # Start with original product
                                    updated_product_data.update(update_dict)  # Apply updates
                                    updated_product_data['id'] = part_id  # Ensure ID is included
                                    db_sync_manager.emit_product_updated(updated_product_data)
                                    logger.debug(f"Emitted product_updated signal for product ID: {part_id}")
                                except Exception as e:
                                    logger.error(f"Error emitting product update signal: {e}")

                                # Refresh the search results
                                self._refresh_data()
                            else:
                                QMessageBox.warning(
                                    self,
                                    self.translator.t('error'),
                                    self.translator.t('operation_failed')
                                )
                        else:
                            QMessageBox.warning(
                                self,
                                self.translator.t('error'),
                                f"Could not find product with parcode: {parcode}"
                            )
                    except Exception as e:
                        logger.error(f"Direct database update error: {e}")
                        QMessageBox.critical(
                            self,
                            self.translator.t('error'),
                            str(e)
                        )
                else:
                    QMessageBox.warning(
                        self,
                        self.translator.t('error'),
                        "Direct database access not available"
                    )
        except Exception as e:
            logger.error(f"Error editing product: {e}")
            QMessageBox.critical(
                self,
                self.translator.t('error'),
                self.translator.t('operation_error')
            )

    def _delete_product(self, product):
        """
        Confirm and delete a product.

        Args:
            product: Product dictionary to delete
        """
        try:
            # Confirm deletion with a more elegant message box
            confirm = QMessageBox.question(
                self,
                self.translator.t('confirm_delete'),
                self.translator.t('delete_confirmation', count=1),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if confirm == QMessageBox.Yes:
                # Access direct database object
                direct_db = None
                if hasattr(self.db_operator, 'db'):
                    direct_db = self.db_operator.db
                elif hasattr(self, 'db'):
                    direct_db = self.db

                if direct_db and hasattr(direct_db, 'delete_part'):
                    # Get the parcode value
                    parcode = product.get('parcode')

                    try:
                        # First we need to find the product ID for this parcode
                        # Get all parts (not ideal but works for small datasets)
                        parts = direct_db.get_all_parts()
                        part_id = None

                        # Find the part with matching parcode
                        for part in parts:
                            if part.get('parcode') == parcode:
                                part_id = part.get('id')
                                break

                        if part_id:
                            # Now delete using the numeric ID
                            success = direct_db.delete_part(part_id)

                            if success:
                                self.status_label.setText(self.translator.t('items_deleted', count=1))
                                # Emit signal for the deleted product
                                self.product_deleted.emit(part_id)

                                # Emit sync signal for product deletion
                                try:
                                    from utils.database_sync import db_sync_manager
                                    db_sync_manager.emit_product_deleted(part_id)
                                    logger.debug(f"Emitted product_deleted signal for product ID: {part_id}")
                                except Exception as e:
                                    logger.error(f"Error emitting product deletion signal: {e}")

                                # Refresh the search results
                                self._refresh_data()
                            else:
                                QMessageBox.warning(
                                    self,
                                    self.translator.t('delete_failed'),
                                    self.translator.t('operation_failed')
                                )
                        else:
                            QMessageBox.warning(
                                self,
                                self.translator.t('delete_failed'),
                                f"Could not find product with parcode: {parcode}"
                            )
                    except Exception as e:
                        logger.error(f"Direct database delete error: {e}")
                        QMessageBox.critical(
                            self,
                            self.translator.t('error'),
                            str(e)
                        )
                else:
                    QMessageBox.warning(
                        self,
                        self.translator.t('error'),
                        "Direct database access not available"
                    )
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            QMessageBox.critical(
                self,
                self.translator.t('error'),
                self.translator.t('operation_error')
            )

    def _show_duplication_dialog(self):
        """Show dialog for duplicating a product from search results."""
        # Use the first product from search results for duplication
        if not self.search_results or len(self.search_results) == 0:
            # No products to duplicate
            QMessageBox.information(
                self,
                self.translator.t('information'),
                self.translator.t('no_products_to_duplicate')
            )
            return

        # Use the first product in the search results
        product_to_duplicate = self.search_results[0]

        try:
            # Create and show the duplication dialog
            dialog = DuplicateProductDialog(product_to_duplicate, self.translator, self)

            if dialog.exec_() == QDialog.Accepted:
                duplicate_data = dialog.get_data()

                # Validate the data
                if not duplicate_data.get('parcode'):
                    QMessageBox.warning(
                        self,
                        self.translator.t('validation_error'),
                        self.translator.t('barcode_required')
                    )
                    return

                # Check if barcode already exists
                direct_db = None
                if hasattr(self.db_operator, 'db'):
                    direct_db = self.db_operator.db
                elif hasattr(self, 'db'):
                    direct_db = self.db

                if direct_db and hasattr(direct_db, 'get_part_by_parcode'):
                    existing_part = direct_db.get_part_by_parcode(duplicate_data.get('parcode'))
                    if existing_part:
                        QMessageBox.warning(
                            self,
                            self.translator.t('validation_error'),
                            self.translator.t('barcode_exists')
                        )
                        return

                # Add the duplicated product to the database
                if direct_db and hasattr(direct_db, 'add_part'):
                    success = direct_db.add_part(
                        category=duplicate_data.get('category'),
                        product_name=duplicate_data.get('product_name'),
                        quantity=duplicate_data.get('quantity'),
                        price=duplicate_data.get('price'),
                        original=duplicate_data.get('original'),
                        manufacturer=duplicate_data.get('manufacturer'),
                        parcode=duplicate_data.get('parcode'),
                        compatible_models=duplicate_data.get('compatible_models'),
                        compatible_brands=duplicate_data.get('compatible_brands')
                    )

                    if success:
                        self.status_label.setText(self.translator.t('product_duplicated'))
                        QMessageBox.information(
                            self,
                            self.translator.t('success'),
                            self.translator.t('product_duplicated')
                        )

                        # Emit signal for duplicated product
                        self.product_duplicated.emit(duplicate_data)

                        # Emit sync signal for product addition
                        try:
                            from utils.database_sync import db_sync_manager
                            # Get the newly added product with its ID
                            new_product = direct_db.get_part_by_parcode(duplicate_data.get('parcode'))
                            if new_product:
                                db_sync_manager.emit_product_added(new_product)
                                logger.debug(
                                    f"Emitted product_added signal for new product ID: {new_product.get('id')}")
                        except Exception as e:
                            logger.error(f"Error emitting product addition signal: {e}")

                        # Refresh the search results
                        self._refresh_data()
                    else:
                        QMessageBox.warning(
                            self,
                            self.translator.t('error'),
                            self.translator.t('operation_failed')
                        )
                else:
                    QMessageBox.warning(
                        self,
                        self.translator.t('error'),
                        "Direct database access not available"
                    )

        except Exception as e:
            logger.error(f"Error showing duplication dialog: {e}")
            QMessageBox.critical(
                self,
                self.translator.t('error'),
                self.translator.t('operation_error')
            )

    def _setup_database(self):
        """Set up the database connection and load initial data."""
        try:
            from utils.database_worker import DatabaseOperator
            self.db_operator = DatabaseOperator(self.db)
            self._refresh_data()
        except Exception as e:
            logger.error(f"Error setting up database connection: {e}")
            self.status_label.setText(self.translator.t('load_error'))


    def _on_db_error(self, error_msg):
        """
        Handle database operation errors.

        Args:
            error_msg: Error message
        """
        logger.error(f"Database error: {error_msg}")
        self.status_label.setText(self.translator.t('load_error'))
        QMessageBox.critical(
            self,
            self.translator.t('error'),
            f"{self.translator.t('load_error')}: {error_msg}"
        )

    def clear_results(self):
        """Clear current search results (used by SearchEdit)."""
        self._clear_results()


    def closeEvent(self, event):
        """Handle widget close event."""
        try:
            # Disconnect from sync manager
            self.disconnect_from_sync_manager()

            # Disconnect from theme events
            try:
                from themes.theme_events import theme_event_manager
                theme_event_manager.theme_changed.disconnect(self._on_theme_changed)
                logger.debug("Disconnected from theme change events")
            except Exception as e:
                logger.error(f"Error disconnecting from theme events: {e}")
        except Exception as e:
            logger.error(f"Error during close event: {e}")
        event.accept()






