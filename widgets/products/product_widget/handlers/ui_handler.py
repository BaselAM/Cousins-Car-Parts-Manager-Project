import os
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QLineEdit, QToolButton, QWidget, QSizePolicy,
                             QFrame, QGraphicsDropShadowEffect, QApplication, QAction, QWidgetAction)
from PyQt5.QtGui import QIcon, QColor, QFont, QPalette, QLinearGradient, QBrush, QPainter, QPixmap
from PyQt5.QtCore import Qt, QSize, QPoint, QRect, QCoreApplication

# Direct imports from theme system
from themes import get_color, get_size, get_font_size
from widgets.products.components.status_bar import StatusBar
from widgets.products.product_table import ProductsTable


class PremiumTitleLabel(QLabel):
    """Custom label with premium styling - Optimized for performance"""

    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setObjectName("premiumTitleLabel")
        self.setAlignment(Qt.AlignCenter)

        # Create an elegant font
        font = QFont("Segoe UI", 15)
        font.setWeight(QFont.Medium)  # Not too bold for elegance
        font.setLetterSpacing(QFont.AbsoluteSpacing, 1.2)  # Subtle letter spacing
        self.setFont(font)

        # Ensure label has enough height
        self.setMinimumHeight(40)

        # Make sure text color is set properly
        self.is_dark_theme = False  # Will be set in updateStyle
        self.updateStyle()

    def updateStyle(self):
        # Detect theme type for proper styling
        bg_color = QColor(get_color('background'))
        self.is_dark_theme = bg_color.lightness() < 128

        # Let the paint event handle the custom drawing
        self.update()

    def forceThemeRefresh(self):
        """Optimized refresh of the label's appearance"""
        self.is_dark_theme = QColor(get_color('background')).lightness() < 128
        self.update()  # Just request a repaint, no geometry calculations

    def paintEvent(self, event):
        """Optimized painting for premium look"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()

        # Create a simpler background - avoid complex gradients
        if self.is_dark_theme:
            # Dark theme - single color background instead of gradient
            bg_color = QColor(35, 35, 35)
            border_color = QColor(80, 80, 80)
            text_color = QColor(255, 255, 255)
        else:
            # Light theme - single color background
            bg_color = QColor(245, 245, 245)
            border_color = QColor(210, 210, 210)
            text_color = QColor(60, 60, 60)

        # Fill background
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 4, 4)

        # Draw subtle border
        painter.setPen(border_color)
        painter.drawRoundedRect(rect.adjusted(0, 0, -1, -1), 4, 4)

        # Draw text
        painter.setPen(text_color)
        painter.setFont(self.font())
        painter.drawText(rect, Qt.AlignCenter, self.text())

        painter.end()


class UIHandler:
    """Handles the UI setup and theme for the Products Widget"""

    def __init__(self, widget, translator):
        self.widget = widget
        self.translator = translator

        # --- UI components ---
        self.title_label = None
        self.buttons_frame = None
        self.add_btn = None
        self.select_toggle = None
        self.remove_btn = None
        self.filter_btn = None
        self.clear_filter_btn = None
        self.export_btn = None
        self.print_btn = None
        self.loading_indicator = None
        self.search_input = None
        self.search_clear_btn = None
        self.product_table = None
        self.status_bar = None
        self.barcode_btn = None  # Added barcode button reference

    def _create_icon(self, icon_name):
        """Helper to create QIcon, potentially handling missing files."""
        path = os.path.join("resources", icon_name)
        if os.path.exists(path):
            return QIcon(path)
        else:
            print(f"Warning: Icon not found at {path}")
            return QIcon()

    def setup_ui(self):
        """Set up the UI components with improved layout and features."""
        self.widget.setObjectName("productsContainer")

        main_layout = QVBoxLayout(self.widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)  # Restored normal spacing between main components

        # --- Premium Title ---
        self.title_label = PremiumTitleLabel(self.translator.t('products_table'))

        # Add subtle drop shadow for depth - use lighter shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(6)  # Reduced from 10
        shadow.setColor(QColor(0, 0, 0, 20))  # Reduced opacity from 25
        shadow.setOffset(0, 2)
        self.title_label.setGraphicsEffect(shadow)

        main_layout.addWidget(self.title_label)

        # --- Buttons Frame ---
        self.buttons_frame = QFrame()
        self.buttons_frame.setObjectName("buttonsFrame")
        self.buttons_frame.setFrameShape(QFrame.StyledPanel)
        self.buttons_frame.setFrameShadow(QFrame.Raised)

        buttons_layout = QVBoxLayout(self.buttons_frame)
        buttons_layout.setContentsMargins(10, 12, 10, 12)
        buttons_layout.setSpacing(10)

        # Action buttons
        top_panel_layout = QHBoxLayout()
        top_panel_layout.setSpacing(8)

        # Left-aligned buttons
        self.add_btn = QPushButton(self.translator.t('add_product'))
        self.add_btn.setIcon(self._create_icon("add_icon.png"))
        self.add_btn.setCursor(Qt.PointingHandCursor)
        top_panel_layout.addWidget(self.add_btn)

        self.select_toggle = QPushButton(self.translator.t('select_button'))
        self.select_toggle.setIcon(self._create_icon("select_icon.png"))
        self.select_toggle.setCheckable(True)
        self.select_toggle.setCursor(Qt.PointingHandCursor)
        self.select_toggle.setObjectName("selectToggleButton")
        top_panel_layout.addWidget(self.select_toggle)

        self.remove_btn = QPushButton(self.translator.t('remove'))
        self.remove_btn.setIcon(self._create_icon("delete_icon.png"))
        self.remove_btn.setCursor(Qt.PointingHandCursor)
        self.remove_btn.setEnabled(False)
        top_panel_layout.addWidget(self.remove_btn)

        self.filter_btn = QPushButton(self.translator.t('filter_button'))
        self.filter_btn.setIcon(self._create_icon("filter_icon.png"))
        self.filter_btn.setCursor(Qt.PointingHandCursor)
        self.filter_btn.setObjectName("filterButton")
        top_panel_layout.addWidget(self.filter_btn)

        # Add Clear Filter next to Filter button (initially hidden)
        self.clear_filter_btn = QToolButton()
        self.clear_filter_btn.setIcon(self._create_icon("clear_filter_icon.png"))
        self.clear_filter_btn.setToolTip(self.translator.t('clear_filters_tooltip'))
        self.clear_filter_btn.setCursor(Qt.PointingHandCursor)
        self.clear_filter_btn.setObjectName("clearFilterButton")
        self.clear_filter_btn.setVisible(False)
        top_panel_layout.addWidget(self.clear_filter_btn)

        self.export_btn = QPushButton(self.translator.t('export'))
        self.export_btn.setIcon(self._create_icon("export_icon.png"))
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setEnabled(False)
        top_panel_layout.addWidget(self.export_btn)

        # Add print button with enhanced tooltip
        self.print_btn = QPushButton(self.translator.t('print'))
        self.print_btn.setIcon(self._create_icon("print_icon.png"))
        try:
            # Use a more generic tooltip if translation isn't available
            tooltip = self.translator.t('print_with_preview_tooltip')
        except:
            tooltip = "Print with preview and customization options"
        self.print_btn.setToolTip(tooltip)
        self.print_btn.setCursor(Qt.PointingHandCursor)
        self.print_btn.setObjectName("printButton")
        top_panel_layout.addWidget(self.print_btn)

        top_panel_layout.addStretch(1)

        # Loading Indicator
        self.loading_indicator = QLabel("⏳")
        self.loading_indicator.setObjectName("loadingIndicator")
        self.loading_indicator.setVisible(False)
        self.loading_indicator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        top_panel_layout.addWidget(self.loading_indicator, 0, Qt.AlignRight | Qt.AlignVCenter)
        top_panel_layout.addSpacing(10)

        # Refresh Button
        self.refresh_btn = QPushButton(self.translator.t('refresh'))
        self.refresh_btn.setIcon(self._create_icon("refresh_icon.png"))
        self.refresh_btn.setCursor(Qt.PointingHandCursor)
        top_panel_layout.addWidget(self.refresh_btn)

        buttons_layout.addLayout(top_panel_layout)

        # --- Completely Simplified Search Bar ---
        # Direct layout with no nested containers
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(8, 8, 8, 8)
        search_layout.setSpacing(18)  # Increased spacing between elements

        # Search label
        search_label = QLabel(self.translator.t('search_products') + ":")
        search_label.setObjectName("searchLabel")
        search_font = QFont("Segoe UI", 11)
        search_font.setWeight(QFont.Bold)
        search_label.setFont(search_font)
        search_layout.addWidget(search_label)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText(self.translator.t('search_placeholder'))
        self.search_input.setMinimumHeight(40)

        # We'll set up the search icon in apply_theme to make it theme-aware
        # For now, just set up a placeholder left padding for the icon
        self.search_input.setTextMargins(38, 0, 0, 0)  # Larger left margin for the bigger icon

        # Add shadow to search input
        search_shadow = QGraphicsDropShadowEffect()
        search_shadow.setBlurRadius(10)
        search_shadow.setColor(QColor(0, 0, 0, 40))
        search_shadow.setOffset(1, 2)
        self.search_input.setGraphicsEffect(search_shadow)

        # Add right margin to search input with padding
        self.search_input.setStyleSheet("padding-right: 10px;")

        search_layout.addWidget(self.search_input, 1)

        # Add extra spacing between search input and barcode button
        search_layout.addSpacing(5)  # Additional explicit spacing

        # Barcode button - directly in the layout
        self.barcode_btn = QToolButton()
        self.barcode_btn.setObjectName("barcodeButton")
        self.barcode_btn.setCursor(Qt.PointingHandCursor)
        self.barcode_btn.setFixedSize(46, 46)  # Keep the same size for button container

        # We'll set the barcode icon in apply_theme with its color based on the theme
        try:
            tooltip = self.translator.t('barcode:scan_barcode_tooltip')
        except:
            tooltip = "Scan Barcode"
        self.barcode_btn.setToolTip(tooltip)

        # Add shadow to barcode button
        barcode_shadow = QGraphicsDropShadowEffect()
        barcode_shadow.setBlurRadius(10)
        barcode_shadow.setColor(QColor(0, 0, 0, 40))
        barcode_shadow.setOffset(1, 2)
        self.barcode_btn.setGraphicsEffect(barcode_shadow)

        search_layout.addWidget(self.barcode_btn, 0, Qt.AlignTop)

        # Add search layout directly to buttons layout
        buttons_layout.addLayout(search_layout)

        # Add the buttons frame to main layout
        main_layout.addWidget(self.buttons_frame)

        # --- Table ---
        self.product_table = ProductsTable(self.translator, self.widget)
        self.product_table.setObjectName("productTable")

        # Create a container for the table with margin offset
        table_container = QWidget()
        table_container.setObjectName("tableContainer")
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, -16, 0, 0)  # Increased negative top margin to lift table closer
        table_layout.addWidget(self.product_table)

        main_layout.addWidget(table_container, 1)

        # --- Status Bar ---
        self.status_bar = StatusBar()
        self.status_bar.setObjectName("statusBar")
        main_layout.addWidget(self.status_bar)

        # Apply theme
        self.apply_theme()

        return {
            'add_btn': self.add_btn,
            'select_toggle': self.select_toggle,
            'remove_btn': self.remove_btn,
            'filter_btn': self.filter_btn,
            'clear_filter_btn': self.clear_filter_btn,
            'export_btn': self.export_btn,
            'print_btn': self.print_btn,
            'refresh_btn': self.refresh_btn,
            'search_input': self.search_input,
            'product_table': self.product_table,
            'status_bar': self.status_bar,
        }

    def apply_theme(self):
        """Optimized theme application using the theme system colors."""
        if hasattr(self.widget, '_is_closing') and self.widget._is_closing:
            return

        # Get basic colors directly from theme system
        bg_color = get_color('background')
        text_color = get_color('text')
        card_bg = get_color('card_bg')
        border_color = get_color('border')
        button_color = get_color('button')
        button_hover = get_color('button_hover')
        button_pressed = get_color('button_pressed')
        highlight_color = get_color('highlight')
        accent_color = get_color('accent', highlight_color)
        input_bg = get_color('input_bg', card_bg)

        # Update title style - use the optimized refresh method
        if self.title_label is not None:
            self.title_label.forceThemeRefresh()

        # Theme direct colors for appearance
        is_dark_theme = QColor(bg_color).lightness() < 128

        # Standard border radius from theme
        border_radius = get_size("border_radius_medium", 8)

        # Button frame styling
        buttons_bg = card_bg

        # Disabled text color
        disabled_text = get_color('text_disabled', QColor(text_color).lighter(130).name() if is_dark_theme
        else QColor(text_color).darker(130).name())

        # Create the stylesheet with the new colors
        style = f"""
            QWidget {{
                color: {text_color};
                font-family: "Segoe UI", "Arial", sans-serif;
                font-size: 14px;
            }}

            #productsContainer {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {border_radius}px;
                padding: 0px;
            }}

            /* === Buttons Frame === */
            #buttonsFrame {{
                background-color: {buttons_bg};
                border: 1px solid {border_color};
                border-radius: {border_radius}px;
                margin: 0px 0px 8px 0px;
            }}

            /* === Buttons === */
            QPushButton {{
                background-color: {button_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 6px 12px;
                margin: 2px;
                font-size: 14px;
                min-height: 28px;
                text-align: center;
                icon-size: 16px;
            }}

            QPushButton:hover {{
                background-color: {button_hover};
                border: 1px solid {accent_color};
            }}

            QPushButton:pressed {{
                background-color: {button_pressed};
                border: 1px solid {accent_color};
                padding: 7px 12px 5px 12px;
            }}

            QPushButton:disabled {{
                background-color: {card_bg};
                color: {disabled_text};
                border: 1px solid {border_color};
            }}

            /* Toggle button */
            QPushButton:checked, QPushButton#selectToggleButton:checked {{
                background-color: {highlight_color};
                color: {get_color('highlight_text', '#FFFFFF')};
                border: 1px solid {QColor(highlight_color).darker(120).name()};
                font-weight: bold;
            }}

            QPushButton:checked:hover, QPushButton#selectToggleButton:checked:hover {{
                background-color: {QColor(highlight_color).lighter(110).name()};
                border-color: {highlight_color};
            }}

            /* Filter button */
            QPushButton#filterButton[filterActive="true"] {{
                background-color: {accent_color};
                color: {get_color('highlight_text', '#FFFFFF')};
                border: 1px solid {QColor(accent_color).darker(120).name()};
                font-weight: bold;
            }}

            QPushButton#filterButton[filterActive="true"]:hover {{
                background-color: {QColor(accent_color).lighter(110).name()};
                border-color: {accent_color};
            }}

            /* Tool buttons */
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
                padding: 3px 2px 1px 2px;
            }}

            /* === Search Elements === */
            #searchLabel {{
    color: {text_color};
    font-size: 14px;
    font-weight: bold;       /* Make the text bold */
    padding-right: 5px;
    border: none;            /* Remove any border/frame */
    background: transparent; /* Ensure the background is transparent */
    margin: 0;               /* Remove any extra margin */
}}

            /* Elegant Search Input */
            QLineEdit#searchInput {{
    background-color: {input_bg};
    color: {text_color};
    border: 2px solid {QColor(highlight_color).darker(110).name()};
    border-radius: 8px;
    padding: 8px 12px 8px 50px;  /* Further increased left padding for even larger icon */
    padding-right: 16px;  /* Additional right padding */
    font-size: 15px;
    min-height: 40px;
    letter-spacing: 0.3px;
}}

            QLineEdit#searchInput:focus {{
                border: 2px solid {highlight_color};
                background-color: {QColor(input_bg).lighter(105).name()};
            }}

            QLineEdit#searchInput::placeholder {{
                color: {disabled_text};
                letter-spacing: 0.5px;
            }}

            /* Elegant Barcode Button */
            QToolButton#barcodeButton {{
    background-color: transparent;  /* Makes the background transparent */
    border: none;                   /* Removes the border/frame */
    border-radius: 8px;
    padding: 3px;
    min-height: 46px;
    min-width: 46px;
}}

            QToolButton#barcodeButton:hover {{
                background-color: {button_hover};
                border: 2px solid {highlight_color};
            }}

            QToolButton#barcodeButton:pressed {{
                background-color: {button_pressed};
                border: 2px solid {highlight_color};
                padding: 9px 7px 7px 9px;
            }}

            QToolButton#clearFilterButton {{
                background-color: {card_bg};
                border: 1px solid {border_color};
                padding: 4px;
                margin-left: -5px;
                border-top-left-radius: 0px;
                border-bottom-left-radius: 0px;
                border-left: none;
            }}

            QToolButton#clearFilterButton:hover {{
                background-color: {button_hover};
                border-color: {border_color};
            }}

            /* Loading indicator */
            #loadingIndicator {{
                color: {accent_color};
                font-size: 18px;
                font-weight: bold;
                padding: 0 5px;
            }}

            /* Status bar */
            #statusBar {{
                margin-top: 5px;
            }}
        """

        # Apply the stylesheet to the main widget
        self.widget.setStyleSheet(style)

        # Apply theme to product table - one component at a time to avoid blocking
        if self.product_table:
            self.product_table.apply_theme()

        # Set up the status bar theme
        if self.status_bar:
            theme_status = {
                "success": {"bg": get_color('success'),
                            "border": QColor(get_color('success')).darker(130).name(),
                            "text": bg_color},
                "error": {"bg": get_color('error'),
                          "border": QColor(get_color('error')).darker(130).name(),
                          "text": bg_color},
                "warning": {"bg": get_color('warning'),
                            "border": QColor(get_color('warning')).darker(130).name(),
                            "text": QColor(bg_color).darker(150).name()},
                "info": {"bg": highlight_color,
                         "border": QColor(highlight_color).darker(130).name(),
                         "text": bg_color}
            }
            self.status_bar.set_theme(theme_status)

        # Update buttons frame directly
        if self.buttons_frame:
            self.buttons_frame.setStyleSheet(f"""
                background-color: {buttons_bg};
                border: 1px solid {border_color};
                border-radius: {border_radius}px;
            """)

        # Add theme-aware colored search icon with increased size (14% larger)
        if hasattr(self, 'search_input') and self.search_input:
            try:
                # Find the search icon file
                search_icon_path = None
                icon_paths = [
                    os.path.join("resources", "search_icon.png"),
                    os.path.join("resources", "icons", "search_icon.png"),
                    os.path.join(".", "resources", "search_icon.png"),
                    os.path.join("..", "resources", "search_icon.png")
                ]

                for path in icon_paths:
                    if os.path.exists(path):
                        search_icon_path = path
                        break

                if search_icon_path:
                    # Load the icon as a pixmap
                    pixmap = QPixmap(search_icon_path)
                    if not pixmap.isNull():
                        # Create a colored version based on theme
                        colored_pixmap = QPixmap(pixmap.size())
                        colored_pixmap.fill(Qt.transparent)

                        painter = QPainter(colored_pixmap)
                        painter.setRenderHint(QPainter.Antialiasing)
                        painter.setRenderHint(QPainter.SmoothPixmapTransform)
                        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                        painter.drawPixmap(0, 0, pixmap)
                        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)

                        # Choose color based on theme
                        if is_dark_theme:
                            # Use white for dark themes
                            painter.fillRect(colored_pixmap.rect(), QColor(255, 255, 255))
                        else:
                            # Use black for light themes
                            painter.fillRect(colored_pixmap.rect(), QColor(0, 0, 0))

                        painter.end()

                        # Create icon from colored pixmap and set it as action
                        search_icon = QIcon(colored_pixmap)

                        # Remove any existing actions
                        for action in self.search_input.actions():
                            self.search_input.removeAction(action)

                        # Add the colored icon as an action with 14% larger size (around 21-22px)
                        search_action = self.search_input.addAction(search_icon, QLineEdit.LeadingPosition)

                        # Set larger icon size for QLineEdit action
                        # Since we can't directly set the icon size for a QLineEdit action,
                        # we adjust the textMargins to accommodate the larger icon
                        self.search_input.setTextMargins(38, 0, 0, 0)
                else:
                    # Fallback to emoji if icon not found
                    self.search_input.setTextMargins(45, 0, 0, 0)
                    search_label = QLabel("🔍")
                    search_label.setAlignment(Qt.AlignCenter)
                    search_label.setFixedSize(45, 40)
                    search_label.setStyleSheet("font-size: 24px;")
                    search_action = QWidgetAction(self.search_input)
                    search_action.setDefaultWidget(search_label)
                    self.search_input.addAction(search_action, QLineEdit.LeadingPosition)
            except Exception as e:
                print(f"Error updating search icon: {e}")
                # Fallback to basic left padding
                self.search_input.setTextMargins(38, 0, 0, 0)

        # Update barcode button icon with theme-aware coloring and larger size (14% larger)
        if hasattr(self, 'barcode_btn') and self.barcode_btn:
            try:
                # Find the barcode icon file
                barcode_icon = None
                icon_paths = [
                    os.path.join("resources", "barcode.png"),
                    os.path.join("resources", "icons", "barcode.png"),
                    os.path.join(".", "resources", "barcode.png"),
                    os.path.join("..", "resources", "barcode.png")
                ]

                for path in icon_paths:
                    if os.path.exists(path):
                        # Load the icon as a pixmap
                        pixmap = QPixmap(path)
                        if not pixmap.isNull():
                            # Create a colored version based on theme
                            colored_pixmap = QPixmap(pixmap.size())
                            colored_pixmap.fill(Qt.transparent)

                            painter = QPainter(colored_pixmap)
                            painter.setRenderHint(QPainter.Antialiasing)
                            painter.setRenderHint(QPainter.SmoothPixmapTransform)
                            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                            painter.drawPixmap(0, 0, pixmap)
                            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)

                            # Choose color based on theme
                            if is_dark_theme:
                                # Use white for dark themes
                                painter.fillRect(colored_pixmap.rect(), QColor(255, 255, 255))
                            else:
                                # Use black for light themes
                                painter.fillRect(colored_pixmap.rect(), QColor(0, 0, 0))

                            painter.end()

                            # Create icon from colored pixmap with 14% larger size
                            # Original size was 22px, 14% larger is about 25px
                            self.barcode_btn.setIcon(QIcon(colored_pixmap))
                            self.barcode_btn.setIconSize(QSize(36, 36))  # 14% larger than 22px
                            break

                # Fallback to text if no icon could be loaded
                if self.barcode_btn.icon().isNull():
                    self.barcode_btn.setText("📊")
                    self.barcode_btn.setStyleSheet("font-size: 20px;")  # Larger emoji (was 18px)
            except Exception as e:
                print(f"Error updating barcode icon: {e}")
                self.barcode_btn.setText("📊")  # Fallback to text emoji
                self.barcode_btn.setStyleSheet("font-size: 20px;")  # Larger emoji

        # Update search and barcode shadow effects
        if hasattr(self, 'search_input') and self.search_input:
            try:
                search_shadow = QGraphicsDropShadowEffect()
                search_shadow.setBlurRadius(10)
                search_shadow.setColor(QColor(0, 0, 0, 40))
                search_shadow.setOffset(1, 2)
                self.search_input.setGraphicsEffect(search_shadow)
            except Exception as e:
                print(f"Error updating search shadow: {e}")

        if hasattr(self, 'barcode_btn') and self.barcode_btn:
            try:
                barcode_shadow = QGraphicsDropShadowEffect()
                barcode_shadow.setBlurRadius(10)
                barcode_shadow.setColor(QColor(0, 0, 0, 40))
                barcode_shadow.setOffset(1, 2)
                self.barcode_btn.setGraphicsEffect(barcode_shadow)
            except Exception as e:
                print(f"Error updating barcode button shadow: {e}")
    def update_filter_button_style(self, active):
        """Update filter button appearance and visibility of clear button."""
        self.filter_btn.setProperty("filterActive", active)
        self.clear_filter_btn.setVisible(active)

        # Only update the specific buttons that changed
        self.filter_btn.style().unpolish(self.filter_btn)
        self.filter_btn.style().polish(self.filter_btn)
        self.clear_filter_btn.style().unpolish(self.clear_filter_btn)
        self.clear_filter_btn.style().polish(self.clear_filter_btn)

    def show_loading_indicator(self, show):
        """Show or hide the loading indicator."""
        if self.loading_indicator:
            self.loading_indicator.setVisible(show)

    def update_translations(self):
        """Update translations for all text elements."""
        # Update title
        if hasattr(self, 'title_label'):
            self.title_label.setText(self.translator.t('products_table'))

        # Buttons
        self.add_btn.setText(self.translator.t('add_product'))
        self.select_toggle.setText(self.translator.t('select_button'))
        self.remove_btn.setText(self.translator.t('remove'))
        self.filter_btn.setText(self.translator.t('filter_button'))
        self.clear_filter_btn.setToolTip(self.translator.t('clear_filters_tooltip'))
        self.export_btn.setText(self.translator.t('export'))
        self.print_btn.setText(self.translator.t('print'))
        try:
            tooltip = self.translator.t('print_with_preview_tooltip')
            self.print_btn.setToolTip(tooltip)
        except:
            # Don't change the tooltip if translation isn't available
            pass
        self.refresh_btn.setText(self.translator.t('refresh'))

        # Search label - find by object name
        search_label = self.widget.findChild(QLabel, "searchLabel")
        if search_label:
            search_label.setText(self.translator.t('search_products') + ":")

        # Search input placeholder
        if hasattr(self, 'search_input') and self.search_input:
            self.search_input.setPlaceholderText(self.translator.t('search_placeholder'))

        # Barcode button tooltip
        if hasattr(self, 'barcode_btn') and self.barcode_btn:
            try:
                self.barcode_btn.setToolTip(self.translator.t('barcode:scan_barcode_tooltip'))
            except:
                self.barcode_btn.setToolTip("Scan Barcode")

        # Table Headers
        if hasattr(self, 'product_table') and self.product_table:
            self.product_table.update_headers()

    def connect_barcode_button(self, callback):
        """Connect the barcode button to the callback function"""
        if hasattr(self, 'barcode_btn') and self.barcode_btn is not None:
            try:
                print("Connecting barcode button to callback function")

                # Properly disconnect any existing connections
                try:
                    if self.barcode_btn.receivers(self.barcode_btn.clicked) > 0:
                        self.barcode_btn.clicked.disconnect()
                except Exception:
                    pass  # Ignore disconnect errors

                # Connect the button click signal to the callback
                self.barcode_btn.clicked.connect(callback)
                print("Barcode button successfully connected")
            except Exception as e:
                print(f"Failed to connect barcode button: {e}")
                import traceback
                traceback.print_exc()