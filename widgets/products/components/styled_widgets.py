"""
styled_widgets.py - Library of premium styled widgets for consistent UI.

This module provides enhanced, theme-aware UI components that automatically
use the application's theme colors while providing a more refined appearance
than the standard Qt widgets.
"""
from PyQt5.QtWidgets import (QPushButton, QRadioButton, QCheckBox,
                             QComboBox, QLabel, QLineEdit, QSpinBox,
                             QDoubleSpinBox, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from themes import get_color


class StyledPushButton(QPushButton):
    """Enhanced push button with hover effects and theme integration."""

    def __init__(self, text, is_primary=False, parent=None):
        super().__init__(text, parent)
        self.is_primary = is_primary
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        bg_color = get_color('background')
        accent_color = get_color('accent', get_color('highlight', '#3f83f1'))
        border_color = get_color('border')

        if self.is_primary:
            # Primary button (filled style)
            self.setStyleSheet(f"""
                QPushButton {{
                    color: {bg_color};
                    background-color: {accent_color};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 13px;
                    min-height: 34px;
                }}

                QPushButton:hover {{
                    background-color: {QColor(accent_color).darker(110).name()};
                }}

                QPushButton:pressed {{
                    background-color: {QColor(accent_color).darker(130).name()};
                }}

                QPushButton:disabled {{
                    background-color: {QColor(accent_color).lighter(150).name()};
                    color: {QColor(bg_color).darker(110).name()};
                }}
            """)
        else:
            # Secondary button (outline style)
            self.setStyleSheet(f"""
                QPushButton {{
                    color: {text_color};
                    background-color: {get_color('button')};
                    border: 1px solid {border_color};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    min-height: 34px;
                }}

                QPushButton:hover {{
                    background-color: {get_color('button_hover')};
                    border: 1px solid {accent_color};
                }}

                QPushButton:pressed {{
                    background-color: {get_color('button_pressed')};
                    border: 1px solid {accent_color};
                }}

                QPushButton:disabled {{
                    color: {QColor(text_color).lighter(160).name()};
                    border: 1px solid {QColor(border_color).lighter(110).name()};
                    background-color: {QColor(get_color('button')).darker(105).name()};
                }}
            """)


class StyledRadioButton(QRadioButton):
    """Custom styled radio button with elegant indicator styling"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        accent_color = get_color('accent', get_color('highlight', '#3f83f1'))
        bg_color = get_color('background')

        # Elegant styling for the radio button indicator only
        self.setStyleSheet(f"""
            QRadioButton {{
                color: {text_color};
                font-size: 13px;
                spacing: 10px;
                padding: 4px;
            }}

            QRadioButton:checked {{
                font-weight: bold;
            }}

            QRadioButton::indicator {{
                width: 22px;
                height: 22px;
                border-radius: 11px;
                border: 2px solid {QColor(text_color).lighter(130).name()};
                background-color: {bg_color};
            }}

            QRadioButton::indicator:hover {{
                border: 2px solid {accent_color};
            }}

            QRadioButton::indicator:checked {{
                border: 2px solid {accent_color};
                background-color: {bg_color};
            }}

            QRadioButton::indicator:checked {{
                image: url(data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB3aWR0aD0iMTJweCIgaGVpZ2h0PSIxMnB4IiB2aWV3Qm94PSIwIDAgMTIgMTIiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgIDxjaXJjbGUgZmlsbD0iIzNmODNmMSIgY3g9IjYiIGN5PSI2IiByPSI1Ii8+Cjwvc3ZnPg==);
            }}
        """)


class StyledCheckBox(QCheckBox):
    """Custom styled checkbox with hover effects"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        accent_color = get_color('accent', get_color('highlight', '#3f83f1'))
        bg_color = get_color('background')

        # Custom style with hover effects
        self.setStyleSheet(f"""
            QCheckBox {{
                color: {text_color};
                font-size: 13px;
                spacing: 8px;
                padding: 4px 2px;
                border-radius: 4px;
            }}

            QCheckBox:hover {{
                background-color: {QColor(accent_color).lighter(180).name()};
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {QColor(text_color).lighter(130).name()};
                background-color: {bg_color};
            }}

            QCheckBox::indicator:unchecked:hover {{
                border: 2px solid {accent_color};
            }}

            QCheckBox::indicator:checked {{
                background-color: {accent_color};
                border: 2px solid {accent_color};
                image: url(data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB3aWR0aD0iMTJweCIgaGVpZ2h0PSIxMnB4IiB2aWV3Qm94PSIwIDAgMTIgMTIiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgIDxwYXRoIGZpbGw9IndoaXRlIiBkPSJNOSAzbDIgMi00IDYtNC0yIDEuNS0yLjVMMTAgMnoiLz4KPC9zdmc+);
            }}

            QCheckBox::indicator:checked:hover {{
                background-color: {QColor(accent_color).darker(110).name()};
                border: 2px solid {QColor(accent_color).darker(110).name()};
            }}
        """)


class StyledComboBox(QComboBox):
    """Custom styled combobox with hover effects"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        bg_color = get_color('background')
        accent_color = get_color('accent', get_color('highlight', '#3f83f1'))
        border_color = get_color('border', QColor(text_color).lighter(150).name())

        # Custom style with hover effects
        self.setStyleSheet(f"""
            QComboBox {{
                color: {text_color};
                background-color: {QColor(bg_color).darker(105).name()};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 5px 10px;
                min-width: 6em;
                font-size: 13px;
            }}

            QComboBox:hover {{
                border: 1px solid {accent_color};
            }}

            QComboBox:focus {{
                border: 1px solid {accent_color};
            }}

            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: none;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}

            QComboBox::down-arrow {{
                image: none;
                width: 8px;
                height: 8px;
                background-color: {text_color};
                border-radius: 4px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 0px;
                selection-background-color: {accent_color};
                selection-color: {bg_color};
                outline: none;
            }}

            QComboBox QAbstractItemView::item {{
                min-height: 24px;
                padding: 4px 8px;
                color: {text_color};
            }}

            QComboBox QAbstractItemView::item:selected {{
                background-color: {accent_color};
                color: {bg_color};
            }}
        """)


class StyledLineEdit(QLineEdit):
    """Enhanced line edit with refined styling"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        bg_color = get_color('card_bg', get_color('background'))
        border_color = get_color('border')
        accent_color = get_color('accent', get_color('highlight'))

        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 8px;
                font-size: 13px;
                min-height: 18px;
                selection-background-color: {accent_color};
            }}

            QLineEdit:focus {{
                border: 2px solid {accent_color};
            }}

            QLineEdit:disabled {{
                background-color: {QColor(bg_color).darker(105).name()};
                color: {QColor(text_color).lighter(130).name()};
            }}
        """)


class StyledSpinBox(QSpinBox):
    """Enhanced spin box with refined styling"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setButtonSymbols(QSpinBox.UpDownArrows)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        bg_color = get_color('card_bg', get_color('background'))
        border_color = get_color('border')
        accent_color = get_color('accent', get_color('highlight'))
        button_color = get_color('button')

        self.setStyleSheet(f"""
            QSpinBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 4px 4px 4px 8px;
                font-size: 13px;
                min-height: 30px;
                selection-background-color: {accent_color};
            }}

            QSpinBox:focus {{
                border: 2px solid {accent_color};
            }}

            QSpinBox::up-button, QSpinBox::down-button {{
                subcontrol-origin: border;
                width: 20px;
                border-left: 1px solid {border_color};
                background-color: {button_color};
            }}

            QSpinBox::up-button {{
                subcontrol-position: top right;
                border-top-right-radius: 4px;
                border-bottom: 1px solid {border_color};
            }}

            QSpinBox::down-button {{
                subcontrol-position: bottom right;
                border-bottom-right-radius: 4px;
            }}

            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {get_color('button_hover')};
            }}

            QSpinBox:disabled {{
                background-color: {QColor(bg_color).darker(105).name()};
                color: {QColor(text_color).lighter(130).name()};
            }}
        """)


class StyledDoubleSpinBox(QDoubleSpinBox):
    """Enhanced double spin box with refined styling"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        bg_color = get_color('card_bg', get_color('background'))
        border_color = get_color('border')
        accent_color = get_color('accent', get_color('highlight'))
        button_color = get_color('button')

        self.setStyleSheet(f"""
            QDoubleSpinBox {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 4px 4px 4px 8px;
                font-size: 13px;
                min-height: 30px;
                selection-background-color: {accent_color};
            }}

            QDoubleSpinBox:focus {{
                border: 2px solid {accent_color};
            }}

            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                subcontrol-origin: border;
                width: 20px;
                border-left: 1px solid {border_color};
                background-color: {button_color};
            }}

            QDoubleSpinBox::up-button {{
                subcontrol-position: top right;
                border-top-right-radius: 4px;
                border-bottom: 1px solid {border_color};
            }}

            QDoubleSpinBox::down-button {{
                subcontrol-position: bottom right;
                border-bottom-right-radius: 4px;
            }}

            QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {get_color('button_hover')};
            }}

            QDoubleSpinBox:disabled {{
                background-color: {QColor(bg_color).darker(105).name()};
                color: {QColor(text_color).lighter(130).name()};
            }}
        """)


class StyledGroupBox(QGroupBox):
    """Custom styled group box with modern appearance"""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        bg_color = get_color('background')
        card_bg = get_color('card_bg', QColor(bg_color).lighter(110).name())
        border_color = get_color('border', QColor(text_color).lighter(150).name())

        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                margin-top: 1.1em;
                padding: 10px;
                background-color: {card_bg};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                top: -0.5em;
                padding: 0 5px;
                background-color: {bg_color};
            }}
        """)


class StyledTitleLabel(QLabel):
    """Large title label with appropriate styling"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        font = self.font()
        font.setPointSize(16)
        font.setBold(True)
        self.setFont(font)
        self.setAlignment(Qt.AlignCenter)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        self.setStyleSheet(f"color: {text_color};")


class StyledSubtitleLabel(QLabel):
    """Subtitle label with appropriate styling"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        font = self.font()
        font.setPointSize(12)
        self.setFont(font)
        self.setAlignment(Qt.AlignCenter)
        self._update_style()

    def _update_style(self):
        text_color = get_color('secondary_text', get_color('text'))
        self.setStyleSheet(f"color: {QColor(text_color).lighter(130).name()};")