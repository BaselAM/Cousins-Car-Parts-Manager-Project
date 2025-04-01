import os # For potentially better path handling
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QLineEdit, QToolButton, QWidget, QSizePolicy) # Added QToolButton, QWidget, QSizePolicy
from PyQt5.QtGui import QIcon, QColor, QPixmap # Added QPixmap
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint # Added more imports

from themes import get_color
# Assuming StatusBar is in components
from widgets.products.components.status_bar import StatusBar
# Assuming ProductsTable is separate
from widgets.products.product_table import ProductsTable
# Consider using a dedicated spinner widget if available/needed
# from widgets.components.spinner import SpinnerWidget


class UIHandler:
    """Handles the UI setup and theme for the Products Widget"""

    def __init__(self, widget, translator):
        self.widget = widget
        self.translator = translator

        # --- UI components ---
        self.add_btn: QPushButton = None
        self.select_toggle: QPushButton = None
        self.remove_btn: QPushButton = None
        self.filter_btn: QPushButton = None
        self.clear_filter_btn: QToolButton = None # New: Clear filter button
        self.export_btn: QPushButton = None
        self.refresh_btn: QPushButton = None
        self.loading_indicator: QLabel = None # New: Loading indicator (can be a custom widget)
        self.search_input: QLineEdit = None
        self.search_clear_btn: QToolButton = None # New: Clear search button
        self.product_table: ProductsTable = None
        self.status_bar: StatusBar = None
        # ---

    def _create_icon(self, icon_name):
        """Helper to create QIcon, potentially handling missing files."""
        # Consider using resource files (.qrc) for better packaging
        path = os.path.join("resources", icon_name)
        if os.path.exists(path):
            return QIcon(path)
        else:
            print(f"Warning: Icon not found at {path}")
            # Return a default empty icon or handle appropriately
            return QIcon()

    def setup_ui(self):
        """Set up the UI components with improved layout and features."""
        self.widget.setObjectName("productsContainer")

        main_layout = QVBoxLayout(self.widget)
        # Reduced margins slightly for a tighter look, increased spacing
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12) # Slightly less spacing than before

        # --- Top Panel (Buttons and Refresh/Loading) ---
        top_panel_layout = QHBoxLayout()
        top_panel_layout.setSpacing(8) # Reduced spacing between buttons

        # Left-aligned buttons
        self.add_btn = QPushButton(self.translator.t('add_product'))
        self.add_btn.setIcon(self._create_icon("add_icon.png"))
        # self.add_btn.setIconSize(QSize(18, 18)) # Size controlled by stylesheet/padding now
        self.add_btn.setCursor(Qt.PointingHandCursor)
        top_panel_layout.addWidget(self.add_btn)

        self.select_toggle = QPushButton(self.translator.t('select_button'))
        self.select_toggle.setIcon(self._create_icon("select_icon.png"))
        # self.select_toggle.setIconSize(QSize(18, 18))
        self.select_toggle.setCheckable(True)
        self.select_toggle.setCursor(Qt.PointingHandCursor)
        self.select_toggle.setObjectName("selectToggleButton") # For specific styling if needed
        top_panel_layout.addWidget(self.select_toggle)

        self.remove_btn = QPushButton(self.translator.t('remove'))
        self.remove_btn.setIcon(self._create_icon("delete_icon.png"))
        # self.remove_btn.setIconSize(QSize(18, 18))
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        self.remove_btn.setEnabled(False) # Start disabled
        top_panel_layout.addWidget(self.remove_btn)

        self.filter_btn = QPushButton(self.translator.t('filter_button'))
        self.filter_btn.setIcon(self._create_icon("filter_icon.png"))
        # self.filter_btn.setIconSize(QSize(18, 18))
        self.filter_btn.setCursor(Qt.PointingHandCursor)
        self.filter_btn.setObjectName("filterButton") # For active state styling
        top_panel_layout.addWidget(self.filter_btn)

        # Add Clear Filter next to Filter button (initially hidden)
        self.clear_filter_btn = QToolButton()
        self.clear_filter_btn.setIcon(self._create_icon("clear_filter_icon.png")) # Use a specific icon
        self.clear_filter_btn.setToolTip(self.translator.t('clear_filters_tooltip'))
        self.clear_filter_btn.setCursor(Qt.PointingHandCursor)
        self.clear_filter_btn.setObjectName("clearFilterButton")
        self.clear_filter_btn.setVisible(False) # Start hidden
        top_panel_layout.addWidget(self.clear_filter_btn)


        self.export_btn = QPushButton(self.translator.t('export'))
        self.export_btn.setIcon(self._create_icon("export_icon.png"))
        # self.export_btn.setIconSize(QSize(18, 18))
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setEnabled(False) # Start disabled (or enabled if export always allowed)
        top_panel_layout.addWidget(self.export_btn)

        top_panel_layout.addStretch(1) # Push remaining items to the right

        # Loading Indicator (Simple Text/Icon Label) - Initially Hidden
        # For a GIF/animation, you might use QMovie on the QLabel
        self.loading_indicator = QLabel("⏳") # Use an icon or text
        self.loading_indicator.setObjectName("loadingIndicator")
        self.loading_indicator.setVisible(False) # Start hidden
        self.loading_indicator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        top_panel_layout.addWidget(self.loading_indicator, 0, Qt.AlignRight | Qt.AlignVCenter)
        top_panel_layout.addSpacing(10) # Space before refresh button

        # Refresh Button
        self.refresh_btn = QPushButton(self.translator.t('refresh'))
        self.refresh_btn.setIcon(self._create_icon("refresh_icon.png"))
        # self.refresh_btn.setIconSize(QSize(18, 18))
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        top_panel_layout.addWidget(self.refresh_btn)

        main_layout.addLayout(top_panel_layout)

        # --- Search Box with Clear Button ---
        search_container = QWidget() # Container for better layout control
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        search_label = QLabel(self.translator.t('search_products') + ":") # Add colon
        search_layout.addWidget(search_label)

        # LineEdit and Clear Button horizontally stacked
        search_input_container = QWidget()
        search_input_layout = QHBoxLayout(search_input_container)
        search_input_layout.setContentsMargins(0, 0, 0, 0)
        search_input_layout.setSpacing(0) # No space between input and clear button

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.translator.t('search_placeholder'))
        self.search_input.setObjectName("searchInput")
        search_input_layout.addWidget(self.search_input, 1) # Takes most space

        self.search_clear_btn = QToolButton()
        self.search_clear_btn.setIcon(self._create_icon("clear_text_icon.png")) # Specific clear icon
        self.search_clear_btn.setCursor(Qt.PointingHandCursor)
        self.search_clear_btn.setObjectName("searchClearButton")
        self.search_clear_btn.setVisible(False) # Show only when text exists
        # Style the clear button to look integrated
        search_input_layout.addWidget(self.search_clear_btn)

        search_layout.addWidget(search_input_container, 1) # Add the combined input+clear

        # Connect signals for clear button visibility
        self.search_input.textChanged.connect(
            lambda text: self.search_clear_btn.setVisible(bool(text))
        )
        self.search_clear_btn.clicked.connect(self.search_input.clear)

        main_layout.addWidget(search_container)


        # --- Table Setup ---
        self.product_table = ProductsTable(self.translator, self.widget) # Pass widget as parent
        main_layout.addWidget(self.product_table, 1) # Table takes expanding space

        # --- Status Bar ---
        self.status_bar = StatusBar()
        self.status_bar.setObjectName("statusBar")
        main_layout.addWidget(self.status_bar)

        # Apply initial theme after all widgets are created
        self.apply_theme()

        # Connect signals that UIHandler manages directly
        # self.select_toggle.toggled.connect(self.update_select_button_style) # Removed - handled by stylesheet

        return {
            'add_btn': self.add_btn,
            'select_toggle': self.select_toggle,
            'remove_btn': self.remove_btn,
            'filter_btn': self.filter_btn,
            'clear_filter_btn': self.clear_filter_btn, # Return new button
            'export_btn': self.export_btn,
            'refresh_btn': self.refresh_btn,
            'search_input': self.search_input,
            # 'search_clear_btn': self.search_clear_btn, # Not usually needed externally
            'product_table': self.product_table,
            'status_bar': self.status_bar,
            # 'loading_indicator': self.loading_indicator # Return if needed externally
        }

    def apply_theme(self):
        """Apply theme to all UI components using stylesheets."""
        if hasattr(self.widget, '_is_closing') and self.widget._is_closing:
            return

        bg_color = get_color('background')
        text_color = get_color('text')
        card_bg = get_color('card_bg') # Used for disabled state
        border_color = get_color('border')
        button_color = get_color('button')
        button_hover = get_color('button_hover')
        button_pressed = get_color('button_pressed')
        highlight_color = get_color('highlight')
        accent_color = get_color('accent', highlight_color) # Fallback to highlight
        input_bg = get_color('input_bg')
        input_bg_focus = QColor(input_bg).lighter(105).name()
        success_color = get_color('success')
        error_color = get_color('error')
        warning_color = get_color('warning')
        info_color = highlight_color # Use highlight for info background

        # Use QColor for alpha modification
        border_highlight = QColor(highlight_color)
        border_highlight.setAlpha(150) # ~60% opacity
        border_highlight_str = border_highlight.name(QColor.HexArgb)

        accent_border = QColor(accent_color)
        accent_border.setAlpha(120) # ~47% opacity
        accent_border_str = accent_border.name(QColor.HexArgb)

        is_dark_theme = QColor(bg_color).lightness() < 128
        disabled_text_color = QColor(text_color).lighter(130).name() if is_dark_theme else QColor(text_color).darker(130).name()


        style = f"""
            QWidget {{
                color: {text_color};
                font-family: "Segoe UI", "Arial", sans-serif; /* Added fallbacks */
                font-size: 14px;
            }}
            #productsContainer {{
                background-color: {bg_color};
                /* Use a less prominent border */
                border: 1px solid {border_color};
                border-radius: 8px; /* Slightly smaller radius */
                padding: 0px; /* Let layout handle margins */
            }}

            /* === Push Buttons === */
            QPushButton {{
                background-color: {button_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px; /* Slightly smaller radius */
                padding: 6px 12px; /* Reduced padding */
                margin: 2px; /* Reduced margin */
                font-size: 14px; /* Match base font size */
                font-weight: normal; /* Normal weight for most buttons */
                min-height: 28px; /* Ensure consistent height */
                /* min-width removed - let content decide width */
                text-align: center;
                icon-size: 16px; /* Consistent icon size */
            }}
             /* Specific bold buttons if needed */
            QPushButton#addButton, QPushButton#refreshButton {{
                 font-weight: bold;
             }}
            QPushButton:hover {{
                background-color: {button_hover};
                border: 1px solid {accent_color}; /* Use accent color on hover */
            }}
            QPushButton:pressed {{
                background-color: {button_pressed};
                border: 1px solid {accent_color};
                padding: 7px 12px 5px 12px; /* Shift down slightly */
            }}
            QPushButton:disabled {{
                background-color: {card_bg};
                color: {disabled_text_color};
                border: 1px solid {border_color};
            }}
            /* Style for the toggle button when checked */
            QPushButton:checked, QPushButton#selectToggleButton:checked {{
                background-color: {highlight_color};
                color: {bg_color}; /* High contrast text */
                border: 1px solid {QColor(highlight_color).darker(120).name()};
                font-weight: bold;
            }}
            QPushButton:checked:hover, QPushButton#selectToggleButton:checked:hover {{
                 background-color: {QColor(highlight_color).lighter(110).name()};
                 border-color: {highlight_color};
             }}

            /* Style for filter button when active (using dynamic property) */
            QPushButton#filterButton[filterActive="true"] {{
                background-color: {accent_color};
                color: {bg_color};
                border: 1px solid {QColor(accent_color).darker(120).name()};
                font-weight: bold;
            }}
             QPushButton#filterButton[filterActive="true"]:hover {{
                  background-color: {QColor(accent_color).lighter(110).name()};
                  border-color: {accent_color};
              }}

            /* === Tool Buttons (Clear Filter, Clear Search) === */
            QToolButton {{
                background-color: transparent;
                border: none;
                padding: 2px;
                margin: 0px;
                border-radius: 4px;
                icon-size: 16px;
            }}
            QToolButton:hover {{
                background-color: {button_hover};
            }}
            QToolButton:pressed {{
                background-color: {button_pressed};
                padding: 3px 2px 1px 2px; /* Shift */
            }}
             /* Specific style for clear search button (inside line edit) */
            QToolButton#searchClearButton {{
                 margin: 0 2px 0 0; /* Margin on right */
                 padding: 4px; /* Adjust padding for alignment */
                 border-radius: 10px; /* Round */
             }}
             /* Make clear filter button blend more with regular buttons */
             QToolButton#clearFilterButton {{
                  background-color: {card_bg};
                  border: 1px solid {border_color};
                  padding: 4px;
                  margin-left: -5px; /* Overlap slightly with filter button */
                  border-top-left-radius: 0px;
                  border-bottom-left-radius: 0px;
                  border-left: none; /* Remove left border */
              }}
             QToolButton#clearFilterButton:hover {{
                  background-color: {button_hover};
                  border-color: {border_color};
              }}


            /* === Search Input === */
            QLabel {{
                /* font-weight: bold; */ /* Removed bold from default label */
                padding-top: 4px; /* Align better with LineEdit */
            }}
            QLineEdit#searchInput {{
                background-color: {input_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 6px 8px; /* Adjusted padding */
                /* Reserve space for the clear button (adjust value as needed) */
                padding-right: 28px;
                font-size: 14px;
            }}
            QLineEdit#searchInput:focus {{
                border: 1px solid {highlight_color};
                /* background-color: {input_bg_focus}; */ /* Subtle focus bg change */
            }}

            /* === Loading Indicator === */
            #loadingIndicator {{
                color: {accent_color};
                font-size: 18px; /* Make icon slightly larger */
                font-weight: bold;
                padding: 0 5px;
            }}

            /* === Status Bar (Handled by its own theme method) === */
            /* Styles for status bar itself if needed, e.g., margins */
            #statusBar {{
                 margin-top: 5px;
             }}
        """
        self.widget.setStyleSheet(style)

        # Apply theme to children that need it
        self.product_table.apply_theme()

        # Set up the status bar theme configuration
        theme_status = {
            "success": {"bg": success_color, "border": QColor(success_color).darker(130).name(), "text": bg_color},
            "error": {"bg": error_color, "border": QColor(error_color).darker(130).name(), "text": bg_color},
            "warning": {"bg": warning_color, "border": QColor(warning_color).darker(130).name(), "text": QColor(bg_color).darker(150).name()}, # Darker text on warning
            "info": {"bg": info_color, "border": QColor(info_color).darker(130).name(), "text": bg_color}
        }
        self.status_bar.set_theme(theme_status)

    # This method is no longer needed as the stylesheet handles :checked state
    # def update_select_button_style(self, checked):
    #    pass # Handled by :checked pseudo-state in stylesheet

    def update_filter_button_style(self, active):
        """Update filter button appearance and visibility of clear button."""
        self.filter_btn.setProperty("filterActive", active)
        self.clear_filter_btn.setVisible(active)

        # Re-polish style for the filter button and clear button
        self.filter_btn.style().unpolish(self.filter_btn)
        self.filter_btn.style().polish(self.filter_btn)
        self.clear_filter_btn.style().unpolish(self.clear_filter_btn)
        self.clear_filter_btn.style().polish(self.clear_filter_btn)


    def show_loading_indicator(self, show):
        """Show or hide the loading indicator."""
        if self.loading_indicator:
            self.loading_indicator.setVisible(show)
            # Optional: Add animation if using QMovie or custom widget


    def update_translations(self):
        """Update translations for all text elements."""
        # Buttons
        self.add_btn.setText(self.translator.t('add_product'))
        self.select_toggle.setText(self.translator.t('select_button'))
        self.remove_btn.setText(self.translator.t('remove'))
        self.filter_btn.setText(self.translator.t('filter_button'))
        self.clear_filter_btn.setToolTip(self.translator.t('clear_filters_tooltip'))
        self.export_btn.setText(self.translator.t('export'))
        self.refresh_btn.setText(self.translator.t('refresh'))

        # Search
        # Assuming the search label is part of the layout but not stored as self.search_label
        search_label_widget = self.search_input.parent().layout().itemAt(0).widget()
        if isinstance(search_label_widget, QLabel):
            search_label_widget.setText(self.translator.t('search_products') + ":")

        self.search_input.setPlaceholderText(self.translator.t('search_placeholder'))

        # Table Headers
        self.product_table.update_headers()

        # Potentially update Status Bar text if it holds persistent translated text (unlikely)