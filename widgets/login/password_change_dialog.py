"""
Password change dialog for Abu Mukh Car Parts Management System.
Allows users to change their password with current password verification.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel,
    QDialogButtonBox, QMessageBox, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import logging

from themes import get_color

logger = logging.getLogger('password_dialog')


class PasswordChangeDialog(QDialog):
    """Dialog for changing user passwords."""

    def __init__(self, username, users_db, translator, parent=None):
        super().__init__(parent)
        self.username = username
        self.users_db = users_db
        self.translator = translator

        self.setWindowTitle(self.translator.t('login:change_password'))
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Setup dialog UI components."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title_label = QLabel(self.translator.t('login:change_password'))
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Form for password fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        # Current password field
        self.current_password = QLineEdit()
        self.current_password.setPlaceholderText(self.translator.t('login:current_password_placeholder'))
        self.current_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow(self.translator.t('login:current_password') + ":", self.current_password)

        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        form_layout.addRow("", separator)

        # New password field
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText(self.translator.t('login:new_password_placeholder'))
        self.new_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow(self.translator.t('login:new_password') + ":", self.new_password)

        # Confirm new password field
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText(self.translator.t('login:confirm_password_placeholder'))
        self.confirm_password.setEchoMode(QLineEdit.Password)
        form_layout.addRow(self.translator.t('login:confirm_password') + ":", self.confirm_password)

        layout.addLayout(form_layout)

        # Password strength indicator (optional)
        self.strength_label = QLabel("")
        layout.addWidget(self.strength_label)

        # Error message area
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.change_password)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Connect password field to update strength indicator
        self.new_password.textChanged.connect(self.update_password_strength)

    def apply_theme(self):
        """Apply theme to dialog components."""
        bg_color = get_color('background')
        text_color = get_color('text')
        accent_color = get_color('accent')

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                color: {text_color};
            }}
            QLabel {{
                color: {text_color};
            }}
            QLineEdit {{
                background-color: {get_color('input_bg', '#2a2a2a')};
                border: 2px solid {get_color('border', '#3a3a3a')};
                border-radius: 6px;
                padding: 8px 10px;
                color: {text_color};
            }}
            QLineEdit:focus {{
                border: 2px solid {accent_color};
            }}
            QPushButton {{
                background-color: {get_color('button', '#0d6efd')};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {get_color('button_hover', '#0b5ed7')};
            }}
            QPushButton:pressed {{
                background-color: {get_color('button_pressed', '#0a58ca')};
            }}
        """)

    def update_password_strength(self):
        """Update the password strength indicator."""
        password = self.new_password.text()

        if not password:
            self.strength_label.setText("")
            return

        # Simple password strength calculation
        strength = 0
        checks = [
            len(password) >= 8,  # Length at least 8
            any(c.isdigit() for c in password),  # Contains digit
            any(c.isupper() for c in password),  # Contains uppercase
            any(c.islower() for c in password),  # Contains lowercase
            any(not c.isalnum() for c in password)  # Contains special char
        ]

        strength = sum(checks)

        # Set strength text and color based on score
        if strength == 0:
            self.strength_label.setText(self.translator.t('login:password_very_weak'))
            self.strength_label.setStyleSheet("color: #e74c3c;")  # Red
        elif strength == 1:
            self.strength_label.setText(self.translator.t('login:password_weak'))
            self.strength_label.setStyleSheet("color: #e67e22;")  # Orange
        elif strength == 2:
            self.strength_label.setText(self.translator.t('login:password_medium'))
            self.strength_label.setStyleSheet("color: #f1c40f;")  # Yellow
        elif strength == 3:
            self.strength_label.setText(self.translator.t('login:password_strong'))
            self.strength_label.setStyleSheet("color: #2ecc71;")  # Green
        else:
            self.strength_label.setText(self.translator.t('login:password_very_strong'))
            self.strength_label.setStyleSheet("color: #27ae60;")  # Dark Green

    def change_password(self):
        """Handle password change logic."""
        current_password = self.current_password.text()
        new_password = self.new_password.text()
        confirm_password = self.confirm_password.text()

        # Validate inputs
        if not current_password:
            self.error_label.setText(self.translator.t('login:current_password_required'))
            self.current_password.setFocus()
            return

        if not new_password:
            self.error_label.setText(self.translator.t('login:new_password_required'))
            self.new_password.setFocus()
            return

        if new_password != confirm_password:
            self.error_label.setText(self.translator.t('login:passwords_dont_match'))
            self.confirm_password.setFocus()
            return

        if len(new_password) < 3:
            self.error_label.setText(self.translator.t('login:password_too_short'))
            self.new_password.setFocus()
            return

        # Try to change password
        success, message = self.users_db.change_password(
            self.username, current_password, new_password
        )

        if success:
            QMessageBox.information(
                self,
                self.translator.t('login:password_changed'),
                self.translator.t('login:password_change_success')
            )
            self.accept()
        else:
            self.error_label.setText(message)