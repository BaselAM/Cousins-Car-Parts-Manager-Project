"""
Custom dialog components with enhanced styling and functionality.
"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QCursor

from themes import get_color, get_size, get_font_size


class CustomDialog(QDialog):
    """A beautifully styled custom dialog that integrates with the theme system."""

    def __init__(self, title, message, icon_type="info", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.CustomizeWindowHint)
        self.setMinimumWidth(400)

        # Set up the UI
        self.setup_ui(title, message, icon_type)
        self.apply_styling()

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

    def setup_ui(self, title, message, icon_type):
        """Set up the dialog UI with an elegant layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Header area with icon and title
        header_layout = QHBoxLayout()

        # Icon label
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(48, 48)

        # Set appropriate icon based on type
        icon_path = None
        if icon_type == "info":
            icon_path = "resources/info_icon.png"
            fallback_emoji = "ℹ️"
            self.icon_color = QColor(get_color('highlight', '#2196F3'))
        elif icon_type == "warning":
            icon_path = "resources/warning_icon.png"
            fallback_emoji = "⚠️"
            self.icon_color = QColor(get_color('warning', '#FFC107'))
        elif icon_type == "error":
            icon_path = "resources/error_icon.png"
            fallback_emoji = "❌"
            self.icon_color = QColor(get_color('error', '#F44336'))
        elif icon_type == "success":
            icon_path = "resources/success_icon.png"
            fallback_emoji = "✅"
            self.icon_color = QColor(get_color('success', '#4CAF50'))
        elif icon_type == "question":
            icon_path = "resources/question_icon.png"
            fallback_emoji = "❓"
            self.icon_color = QColor(get_color('highlight', '#2196F3'))

        # Try to load icon, use emoji as fallback
        if icon_path:
            try:
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    self.icon_label.setPixmap(pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.icon_label.setText(fallback_emoji)
                    font = self.icon_label.font()
                    font.setPointSize(24)
                    self.icon_label.setFont(font)
            except:
                self.icon_label.setText(fallback_emoji)
                font = self.icon_label.font()
                font.setPointSize(24)
                self.icon_label.setFont(font)
        else:
            self.icon_label.setText(fallback_emoji)
            font = self.icon_label.font()
            font.setPointSize(24)
            self.icon_label.setFont(font)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setObjectName("dialogTitle")
        font = self.title_label.font()
        font.setPointSize(get_font_size("xlarge"))
        font.setBold(True)
        self.title_label.setFont(font)

        # Add to header layout
        header_layout.addWidget(self.icon_label)
        header_layout.addSpacing(16)
        header_layout.addWidget(self.title_label, 1)

        # Message label with larger font
        self.message_label = QLabel(message)
        self.message_label.setObjectName("dialogMessage")
        self.message_label.setWordWrap(True)
        font = self.message_label.font()
        font.setPointSize(get_font_size("large"))
        self.message_label.setFont(font)

        # Button layout
        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(1)

        # Add components to main layout
        layout.addLayout(header_layout)
        layout.addWidget(self.message_label)
        layout.addStretch(1)
        layout.addLayout(self.button_layout)

    def apply_styling(self):
        """Apply elegant styling to the dialog."""
        # Get theme colors
        bg_color = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        button_color = get_color('button')
        button_hover = get_color('button_hover')
        highlight_color = get_color('highlight')
        highlight_color_lighter = QColor(highlight_color).lighter(110).name()
        highlight_color_darker = QColor(highlight_color).darker(110).name()
        error_color = get_color('error')
        error_color_lighter = QColor(error_color).lighter(110).name()
        error_color_darker = QColor(error_color).darker(110).name()
        success_color = get_color('success')
        success_color_lighter = QColor(success_color).lighter(110).name()
        success_color_darker = QColor(success_color).darker(110).name()

        # Create style sheet
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: {get_size('border_radius_large')}px;
            }}

            #dialogTitle {{
                color: {text_color};
            }}

            #dialogMessage {{
                color: {text_color};
                margin: 10px 0;
            }}

            QPushButton {{
                background-color: {button_color};
                color: {text_color};
                border: none;
                border-radius: {get_size('border_radius_medium')}px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: {get_font_size('medium')}px;
                min-width: 100px;
                min-height: 40px;
            }}

            QPushButton:hover {{
                background-color: {button_hover};
            }}

            QPushButton:pressed {{
                background-color: {get_color('button_pressed')};
            }}

            QPushButton#primaryButton {{
                background-color: {highlight_color};
                color: {get_color('highlight_text', '#FFFFFF')};
            }}

            QPushButton#primaryButton:hover {{
                background-color: {highlight_color_lighter};
            }}

            QPushButton#primaryButton:pressed {{
                background-color: {highlight_color_darker};
            }}

            QPushButton#dangerButton {{
                background-color: {error_color};
                color: white;
            }}

            QPushButton#dangerButton:hover {{
                background-color: {error_color_lighter};
            }}

            QPushButton#dangerButton:pressed {{
                background-color: {error_color_darker};
            }}

            QPushButton#successButton {{
                background-color: {success_color};
                color: white;
            }}

            QPushButton#successButton:hover {{
                background-color: {success_color_lighter};
            }}

            QPushButton#successButton:pressed {{
                background-color: {success_color_darker};
            }}
        """)

    def add_button(self, text, role="normal", is_default=False, callback=None):
        """Add a button to the dialog with appropriate styling."""
        button = QPushButton(text)
        button.setCursor(QCursor(Qt.PointingHandCursor))

        # Set button style based on role
        if role == "primary":
            button.setObjectName("primaryButton")
        elif role == "danger":
            button.setObjectName("dangerButton")
        elif role == "success":
            button.setObjectName("successButton")

        # Set as default button if specified
        if is_default:
            button.setDefault(True)

        # Connect callback if provided
        if callback:
            button.clicked.connect(callback)

        # Add to button layout
        self.button_layout.addWidget(button)
        return button


class InfoDialog(CustomDialog):
    """Information dialog with a single OK button."""

    def __init__(self, title, message, parent=None):
        super().__init__(title, message, "info", parent)
        self.ok_button = self.add_button("OK", "primary", True, self.accept)


class WarningDialog(CustomDialog):
    """Warning dialog with a single OK button."""

    def __init__(self, title, message, parent=None):
        super().__init__(title, message, "warning", parent)
        self.ok_button = self.add_button("OK", "primary", True, self.accept)


class ErrorDialog(CustomDialog):
    """Error dialog with a single OK button."""

    def __init__(self, title, message, parent=None):
        super().__init__(title, message, "error", parent)
        self.ok_button = self.add_button("OK", "primary", True, self.accept)


class SuccessDialog(CustomDialog):
    """Success dialog with a single OK button."""

    def __init__(self, title, message, parent=None):
        super().__init__(title, message, "success", parent)
        self.ok_button = self.add_button("OK", "success", True, self.accept)


class ConfirmationDialog(CustomDialog):
    """Confirmation dialog with Yes and No buttons."""

    def __init__(self, title, message, yes_text="Yes", no_text="No", parent=None):
        super().__init__(title, message, "question", parent)

        # Add No button (closes with reject)
        self.no_button = self.add_button(no_text, "normal", False, self.reject)

        # Add Yes button (closes with accept)
        self.yes_button = self.add_button(yes_text, "primary", True, self.accept)