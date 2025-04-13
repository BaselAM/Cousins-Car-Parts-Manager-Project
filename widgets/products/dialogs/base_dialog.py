"""
Enhanced base dialog with premium styling.

This module provides a consistent premium dialog experience across the application by
using the styled widget library and implementing refined appearance features.
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFrame,
                             QGraphicsDropShadowEffect, QSpacerItem,
                             QSizePolicy)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QIcon

from themes import get_color
from widgets.products.components.styled_widgets import StyledPushButton


class ElegantDialog(QDialog):
    """Base class for all elegant dialogs with premium styling and animations."""

    def __init__(self, translator, parent=None, title="Dialog"):
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.t(title) if title else "Dialog")
        self.setMinimumWidth(450)
        self.setMinimumHeight(300)

        # Set window flags for modern look
        self.setWindowFlags(self.windowFlags() | Qt.WindowCloseButtonHint)

        # Setup main layout with proper spacing
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(15)

        # Add drop shadow for premium feel
        self._add_drop_shadow()

        # Apply default theming
        self.apply_theme()

    def _add_drop_shadow(self):
        """Add subtle drop shadow to dialog for depth"""
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 70))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

    def apply_theme(self):
        """Apply theme colors to dialog with premium styling"""
        bg_color = get_color('background')
        text_color = get_color('text')
        border_color = get_color('border')

        # Determine if using dark theme
        is_dark_theme = QColor(bg_color).lightness() < 128
        shadow_opacity = "0.3" if is_dark_theme else "0.15"

        # Main dialog style
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 10px;
                font-family: 'Segoe UI', sans-serif;
            }}

            QLabel {{
                color: {text_color};
                font-size: 14px;
            }}

            QFrame[frameShape="4"] {{ /* HLine */
                background-color: {border_color};
                max-height: 1px;
                border: none;
            }}

            QFrame[frameShape="5"] {{ /* VLine */
                background-color: {border_color};
                max-width: 1px;
                border: none;
            }}
        """)

    def add_separator(self):
        """Add a horizontal separator line to the dialog"""
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setMaximumHeight(1)
        self.main_layout.addWidget(separator)
        return separator

    def create_button_layout(self, primary_button=None, secondary_button=None,
                             other_buttons=None, centered=False):
        """
        Create a standard button layout for the dialog.

        Args:
            primary_button: The main action button (styled as primary)
            secondary_button: The secondary action button
            other_buttons: List of additional buttons to include
            centered: Whether to center the buttons instead of right-aligning

        Returns:
            The button layout that was added to the dialog
        """
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        if other_buttons:
            for button in other_buttons:
                button_layout.addWidget(button)

        if centered:
            button_layout.addStretch(1)

        if secondary_button:
            button_layout.addWidget(secondary_button)

        if primary_button:
            button_layout.addWidget(primary_button)

        if not centered:
            button_layout.addStretch(1)

        self.main_layout.addLayout(button_layout)
        return button_layout

    def create_action_buttons(self, ok_text=None, cancel_text=None):
        """
        Create standard OK and Cancel buttons.

        Args:
            ok_text: Text for the OK button (default: "OK")
            cancel_text: Text for the Cancel button (default: "Cancel")

        Returns:
            Tuple of (ok_button, cancel_button)
        """
        ok_text = ok_text or self.translator.t('ok')
        cancel_text = cancel_text or self.translator.t('cancel')

        ok_button = StyledPushButton(ok_text, is_primary=True)
        ok_button.setObjectName("okButton")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)

        cancel_button = StyledPushButton(cancel_text)
        cancel_button.setObjectName("cancelButton")
        cancel_button.clicked.connect(self.reject)

        return ok_button, cancel_button