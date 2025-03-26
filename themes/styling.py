"""Theme styling application functions."""
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QColor, QIcon
from .core import get_color


def apply_enhanced_borders():
    """Apply enhanced borders to all widgets"""
    # Define the style with stronger borders
    enhanced_border_style = """
        /* Enhanced borders for QFrame */
        QFrame {
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        /* Enhanced borders for card-like containers */
        QFrame#appGridContainer, QWidget#settingsContainer, QWidget#partsContainer, 
        QWidget#productsContainer, QWidget#statsContainer, QWidget#searchContainer {
            border: 2px solid rgba(200, 200, 200, 0.3);
            border-radius: 8px;
            padding: 5px;
        }

        /* Enhanced tab widgets */
        QTabWidget::pane {
            border: 2px solid rgba(200, 200, 200, 0.3);
            border-radius: 5px;
        }

        /* Settings widget specific enhancements */
        QWidget#settingsContainer {
            border: 3px solid rgba(64, 158, 255, 0.5);
            border-radius: 10px;
        }

        /* Group boxes with better defined borders */
        QGroupBox {
            border: 2px solid rgba(200, 200, 200, 0.25);
            border-radius: 6px;
            margin-top: 20px;
            font-weight: bold;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 10px;
        }
    """

    # Apply the enhanced border style to the application
    app = QApplication.instance()
    if app and isinstance(app, QApplication):
        app.setStyleSheet(app.styleSheet() + enhanced_border_style)


def apply_dialog_theme(dialog, title="", icon_path=None, min_width=400):
    """Apply consistent theme styling to any dialog

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

    # Apply elegant styling with theme colors
    dialog.setStyleSheet(f"""
        QDialog {{
            background-color: {get_color('background')};
            border: 2px solid {get_color('border')};
            border-radius: 8px;
        }}
        QLabel {{
            color: {get_color('text')};
            font-size: 14px;
        }}
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background-color: {get_color('input_bg')};
            color: {get_color('text')};
            border: 1px solid {get_color('border')};
            border-radius: 4px;
            padding: 8px;
            font-size: 14px;
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {get_color('highlight')};
        }}
        QPushButton {{
            background-color: {get_color('button')};
            color: {get_color('text')};
            border: 1px solid {get_color('border')};
            border-radius: 5px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: bold;
            min-width: 100px;
        }}
        QPushButton:hover {{
            background-color: {get_color('button_hover')};
            border: 1px solid {get_color('highlight')};
        }}
        QPushButton:pressed {{
            background-color: {get_color('button_pressed')};
            border: 2px solid {get_color('highlight')};
        }}
        QPushButton#primaryButton {{
            background-color: {get_color('highlight')};
            color: white;
            border: none;
        }}
        QPushButton#primaryButton:hover {{
            background-color: {QColor(get_color('highlight')).darker(115).name()};
        }}
        QScrollArea {{
            border: 1px solid {get_color('border')};
            background-color: {get_color('card_bg')};
            border-radius: 4px;
        }}
        QGroupBox {{
            background-color: {get_color('card_bg')};
            border: 1px solid {get_color('border')};
            border-radius: 6px;
            margin-top: 16px;
            font-weight: bold;
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top center;
            padding: 0 5px;
        }}
    """)

    return dialog