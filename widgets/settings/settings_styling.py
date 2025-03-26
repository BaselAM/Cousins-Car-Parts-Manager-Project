from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsOpacityEffect

from themes import get_color


class SettingsStyling:
    """Handles styling and animation for the settings widget"""

    @staticmethod
    def apply_theme(widget, theme_names, theme_combo):
        """Apply theme styling to the settings widget."""
        current_theme = theme_names[theme_combo.currentIndex()]
        text_color = get_color('text')
        primary_color = get_color('primary')
        border_color = get_color('border')
        button_color = get_color('button')
        success_color = get_color('success')

        base_style = f"""
            QWidget {{
                background-color: {primary_color};
                color: {text_color};
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }}
            #settingsContainer {{
                border: 1px solid {border_color};
                border-radius: 10px;
            }}
            #settingsHeader {{
                background-color: {primary_color};
            }}
            #settingsTitle {{
                font-size: 20px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            QGroupBox {{
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 20px;
            }}
            QGroupBox::title {{
                padding: 0 8px;
                font-weight: bold;
                font-size: 15px;
            }}
            QFormLayout {{
                margin: 8px;
                spacing: 10px;
            }}
            QLabel {{
                padding: 2px 0;
            }}
            QLineEdit, QComboBox, QSpinBox {{
                background-color: {get_color('input_bg')};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 8px 12px;
                min-height: 18px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border: 2px solid {success_color};
            }}
            QPushButton {{
                background-color: {button_color};
                border: none;
                border-radius: 20px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {button_color};
                opacity: 0.8;
            }}
            QPushButton:pressed {{
                background-color: {success_color};
            }}
            QScrollBar:vertical {{
                background: {QColor(primary_color).lighter(110).name() if current_theme != "dark" else QColor(primary_color).darker(105).name()};
                width: 12px;
                margin: 2px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: {QColor(button_color).lighter(120).name() if current_theme == "dark" else button_color};
                min-height: 30px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: {get_color('button_hover')};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: {QColor(primary_color).lighter(110).name() if current_theme == "dark" else QColor(primary_color).darker(105).name()};
                border-radius: 6px;
            }}
        """
        widget.setStyleSheet(base_style)

    @staticmethod
    def refresh_scrollbar(scroll_area, theme_names, theme_combo):
        """Refresh scrollbar styling and behavior."""
        if scroll_area:
            scroll_area.widget().updateGeometry()
            scroll_area.updateGeometry()
            scroll_area.verticalScrollBar().setValue(0)
            current_theme = theme_names[theme_combo.currentIndex()]
            is_dark = current_theme == "dark"
            primary_color = get_color('primary')
            button_color = get_color('button')
            button_hover = get_color('button_hover')
            scrollbar_style = f"""
                QScrollBar:vertical {{
                    background: transparent;
                    width: 14px;
                    margin: 2px;
                    border-radius: 7px;
                }}
                QScrollBar::handle:vertical {{
                    background: {QColor(button_color).lighter(120).name() if is_dark else button_color};
                    min-height: 30px;
                    border-radius: 7px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background: {button_hover};
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}
                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: {QColor(primary_color).lighter(110).name() if is_dark else QColor(primary_color).darker(105).name()};
                    border-radius: 7px;
                }}
            """
            scroll_area.verticalScrollBar().setStyleSheet(scrollbar_style)
            content_widget = scroll_area.widget()
            if content_widget:
                content_widget.setMinimumHeight(scroll_area.height() + 50)

    @staticmethod
    def add_entrance_animation(widget):
        """Add a fade-in animation to the widget."""
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0)
        fade_animation = QPropertyAnimation(opacity_effect, b"opacity")
        fade_animation.setDuration(300)
        fade_animation.setStartValue(0)
        fade_animation.setEndValue(1)
        fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        QTimer.singleShot(100, fade_animation.start)

        # Store reference to prevent garbage collection
        widget.fade_animation = fade_animation