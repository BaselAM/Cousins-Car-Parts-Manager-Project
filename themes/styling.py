"""Theme styling application functions for modern, sleek UI."""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor, QIcon
from .core import get_color, get_size


def apply_enhanced_borders():
    """Apply modern, sleek borders and styling to all widgets"""
    # Define the style with more refined borders and modern elements
    enhanced_modern_style = """
        /* Base styling improvements */
        * {
            font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', sans-serif;
        }
        
        /* Subtle transitions for interactive elements */
        QPushButton, QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox, QSlider::handle {
            transition: background-color 0.2s, border 0.2s;
        }
        
        /* Modern frames with subtle borders */
        QFrame {
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 6px;
        }

        /* Modern card-like containers with subtle shadows */
        QFrame#appGridContainer, QWidget#settingsContainer, QWidget#partsContainer, 
        QWidget#productsContainer, QWidget#statsContainer, QWidget#searchContainer {
            border: 1px solid rgba(200, 200, 200, 0.15);
            border-radius: 8px;
            padding: 12px;
            background-color: rgba(255, 255, 255, 0.03);
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
        }

        /* Modern tab widgets */
        QTabWidget::pane {
            border: 1px solid rgba(200, 200, 200, 0.15);
            border-radius: 6px;
            background-color: rgba(255, 255, 255, 0.02);
            top: -1px; /* overlaps with the tab bar */
        }
        
        QTabBar::tab {
            background-color: transparent;
            border-bottom: 2px solid transparent;
            padding: 8px 16px;
            margin-right: 4px;
        }
        
        QTabBar::tab:selected {
            border-bottom: 2px solid rgba(64, 158, 255, 0.8);
        }
        
        QTabBar::tab:hover:!selected {
            border-bottom: 2px solid rgba(64, 158, 255, 0.3);
        }

        /* Settings widget with premium feel */
        QWidget#settingsContainer {
            border: 1px solid rgba(64, 158, 255, 0.2);
            border-radius: 10px;
            background-color: rgba(64, 158, 255, 0.05);
            padding: 16px;
        }

        /* Modern group boxes */
        QGroupBox {
            border: 1px solid rgba(200, 200, 200, 0.15);
            border-radius: 8px;
            margin-top: 24px;
            font-weight: 500;
            background-color: rgba(255, 255, 255, 0.02);
            padding-top: 4px;
            padding-bottom: 8px;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 16px;
            color: rgba(255, 255, 255, 0.9);
        }
        
        /* Modern scrollbars */
        QScrollBar:vertical {
            border: none;
            background: rgba(255, 255, 255, 0.03);
            width: 8px;
            border-radius: 4px;
            margin: 0;
        }

        QScrollBar::handle:vertical {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        
        /* Horizontal scrollbar */
        QScrollBar:horizontal {
            border: none;
            background: rgba(255, 255, 255, 0.03);
            height: 8px;
            border-radius: 4px;
        }

        QScrollBar::handle:horizontal {
            background: rgba(255, 255, 255, 0.2);
            border-radius: 4px;
            min-width: 20px;
        }

        QScrollBar::handle:horizontal:hover {
            background: rgba(255, 255, 255, 0.3);
        }

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
    """

    # Apply the enhanced modern style to the application
    app = QApplication.instance()
    if app and isinstance(app, QApplication):
        app.setStyleSheet(app.styleSheet() + enhanced_modern_style)


def apply_dialog_theme(dialog, title="", icon_path=None, min_width=400):
    """Apply modern, sleek theme styling to any dialog

    Args:
        dialog: The dialog to style
        title (str, optional): Window title
        icon_path (str, optional): Path to window icon
        min_width (int, optional): Minimum dialog width

    Returns:
        The styled dialog for method chaining
    """
    # Set basic properties
    if title:
        dialog.setWindowTitle(title)
    if icon_path:
        dialog.setWindowIcon(QIcon(icon_path))
    dialog.setMinimumWidth(min_width)

    # Apply modern styling with theme colors
    dialog.setStyleSheet(f"""
        QDialog {{
            background-color: {get_color('background')};
            border: 1px solid {get_color('border')};
            border-radius: 10px;
        }}
        
        QLabel {{
            color: {get_color('text')};
            font-size: 14px;
            font-weight: 400;
            padding: 4px 0;
        }}
        
        QLabel[heading="true"] {{
            font-size: 18px;
            font-weight: 500;
            margin-bottom: 16px;
        }}
        
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background-color: {get_color('input_bg')};
            color: {get_color('text')};
            border: 1px solid {get_color('border')};
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 14px;
            selection-background-color: {get_color('highlight')};
        }}
        
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {get_color('highlight')};
            background-color: {QColor(get_color('input_bg')).lighter(110).name()};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 24px;
        }}
        
        QComboBox::down-arrow {{
            image: url(down-arrow.png);
            width: 12px;
            height: 12px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {get_color('card_bg')};
            border: 1px solid {get_color('border')};
            border-radius: 6px;
            selection-background-color: {get_color('highlight')};
            outline: none;
        }}
        
        QPushButton {{
            background-color: {get_color('button')};
            color: {get_color('text')};
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: 500;
            min-width: 100px;
        }}
        
        QPushButton:hover {{
            background-color: {get_color('button_hover')};
        }}
        
        QPushButton:pressed {{
            background-color: {get_color('button_pressed')};
        }}
        
        QPushButton:disabled {{
            background-color: {get_color('button_disabled')};
            color: {get_color('text_disabled')};
        }}
        
        QPushButton#primaryButton {{
            background-color: {get_color('highlight')};
            color: {get_color('highlight_text')};
        }}
        
        QPushButton#primaryButton:hover {{
            background-color: {QColor(get_color('highlight')).lighter(110).name()};
        }}
        
        QPushButton#primaryButton:pressed {{
            background-color: {QColor(get_color('highlight')).darker(110).name()};
        }}
        
        QPushButton#secondaryButton {{
            background-color: transparent;
            color: {get_color('highlight')};
            border: 1px solid {get_color('highlight')};
        }}
        
        QPushButton#secondaryButton:hover {{
            background-color: rgba(255, 255, 255, 0.05);
        }}
        
        QCheckBox, QRadioButton {{
            color: {get_color('text')};
            spacing: 8px;
            padding: 4px 0;
        }}
        
        QCheckBox::indicator, QRadioButton::indicator {{
            width: 18px;
            height: 18px;
        }}
        
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
            background-color: {get_color('highlight')};
            border: 1px solid {get_color('highlight')};
        }}
        
        QScrollArea {{
            border: 1px solid {get_color('border')};
            background-color: {get_color('card_bg')};
            border-radius: 6px;
        }}
        
        QGroupBox {{
            background-color: {get_color('card_bg')};
            border: 1px solid {get_color('border')};
            border-radius: 8px;
            margin-top: 20px;
            font-weight: 500;
            padding: 16px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 10px;
            color: {get_color('text')};
        }}
    """)

    return dialog


def apply_main_window_theme(window, title="", icon_path=None):
    """Apply modern theme styling to the main application window

    Args:
        window: The main window to style
        title (str, optional): Window title
        icon_path (str, optional): Path to window icon

    Returns:
        The styled window for method chaining
    """
    # Set basic properties
    if title:
        window.setWindowTitle(title)
    if icon_path:
        window.setWindowIcon(QIcon(icon_path))

    # Apply modern styling with theme colors
    window.setStyleSheet(f"""
        QMainWindow {{
            background-color: {get_color('background')};
        }}
        
        QMenuBar {{
            background-color: {get_color('header')};
            color: {get_color('text')};
            border-bottom: 1px solid {get_color('border')};
            padding: 2px 0;
        }}
        
        QMenuBar::item {{
            background: transparent;
            padding: 6px 12px;
            border-radius: 4px;
        }}
        
        QMenuBar::item:selected {{
            background-color: rgba(255, 255, 255, 0.1);
        }}
        
        QMenu {{
            background-color: {get_color('card_bg')};
            color: {get_color('text')};
            border: 1px solid {get_color('border')};
            border-radius: 6px;
            padding: 4px 0;
        }}
        
        QMenu::item {{
            padding: 8px 24px 8px 16px;
        }}
        
        QMenu::item:selected {{
            background-color: {get_color('highlight')};
            color: {get_color('highlight_text')};
        }}
        
        QMenu::separator {{
            height: 1px;
            background-color: {get_color('border')};
            margin: 4px 8px;
        }}
        
        QStatusBar {{
            background-color: {get_color('footer')};
            color: {get_color('secondary_text')};
            border-top: 1px solid {get_color('border')};
            min-height: {get_size('footer_height')}px;
        }}
        
        QToolBar {{
            background-color: {get_color('background')};
            border-bottom: 1px solid {get_color('border')};
            padding: 4px;
            spacing: 4px;
        }}
        
        QToolButton {{
            background-color: transparent;
            border: none;
            border-radius: 4px;
            padding: 4px;
        }}
        
        QToolButton:hover {{
            background-color: rgba(255, 255, 255, 0.1);
        }}
        
        QToolButton:pressed {{
            background-color: rgba(255, 255, 255, 0.05);
        }}
        
        QDockWidget {{
            titlebar-close-icon: url(close.png);
            titlebar-normal-icon: url(undock.png);
        }}
        
        QDockWidget::title {{
            background-color: {get_color('header')};
            padding: 6px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            text-align: center;
        }}
        
        QDockWidget::close-button, QDockWidget::float-button {{
            border: none;
            background: transparent;
            padding: 2px;
            width: 14px;
            height: 14px;
        }}
        
        QHeaderView::section {{
            background-color: {get_color('header')};
            color: {get_color('text')};
            padding: 8px;
            border: none;
            border-right: 1px solid {get_color('border')};
            border-bottom: 1px solid {get_color('border')};
        }}
        
        QTableView, QTreeView, QListView {{
            background-color: {get_color('card_bg')};
            alternate-background-color: {QColor(get_color('card_bg')).lighter(105).name()};
            border: 1px solid {get_color('border')};
            border-radius: 6px;
            gridline-color: {get_color('border')};
            selection-background-color: {get_color('highlight')};
            selection-color: {get_color('highlight_text')};
            outline: none;
        }}
        
        /* Toast/notification styling */
        QFrame#toastMessage {{
            background-color: {get_color('card_bg')};
            border-radius: 6px;
            border: 1px solid {get_color('border')};
            padding: 12px;
        }}
    """)

    return window


def apply_widget_theme(widget, card_style=False):
    """Apply modern theme styling to a widget

    Args:
        widget: The widget to style
        card_style (bool): Whether to apply card-like styling

    Returns:
        The styled widget for method chaining
    """
    style = f"""
        QWidget {{
            background-color: {'transparent' if not card_style else get_color('card_bg')};
            color: {get_color('text')};
        }}
    """

    if card_style:
        style += f"""
            QWidget {{
                border: 1px solid {get_color('border')};
                border-radius: 8px;
                padding: 16px;
                background-color: {get_color('card_bg')};
            }}
        """

    widget.setStyleSheet(style)
    return widget