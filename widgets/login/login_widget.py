"""
Enhanced login widget for Abu Mukh Car Parts Management System.
Supports multiple users, password management, and user profiles.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel,
    QMessageBox, QFrame, QHBoxLayout, QCheckBox, QSpacerItem, QSizePolicy,
    QApplication, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPropertyAnimation, QEasingCurve
from pathlib import Path
import time
import logging

from themes import get_color, set_theme, THEMES
from translations import EnhancedTranslator
from .password_change_dialog import PasswordChangeDialog
from database.users_db import UsersDB
from database.settings_db import SettingsDB

logger = logging.getLogger('login_widget')


class LoginWidget(QWidget):
    """
    Enhanced login widget with user database integration,
    remember me functionality, and password management.
    """
    # Signals
    login_successful = pyqtSignal(dict)  # Emits user data on successful login

    def __init__(self, translator=None, parent=None):
        super().__init__(parent)
        self.translator = translator if translator is not None else EnhancedTranslator('en')
        self.users_db = UsersDB()
        self.current_user = None

        # Load theme from settings
        try:
            settings_db = SettingsDB()
            theme_name = settings_db.get_setting('theme', 'classic')
            set_theme(theme_name)
            settings_db.close()
        except Exception as e:
            logger.error(f"Error loading theme setting: {e}")

        # Setup UI
        self.setWindowTitle(self.translator.t('login:window_title'))
        self.resize(450, 500)
        self.setup_ui()
        self.apply_theme()

        # Remember me functionality
        self.remembered_username = self._load_remembered_username()
        if self.remembered_username:
            self.username_edit.setText(self.remembered_username)
            self.remember_me_checkbox.setChecked(True)
            self.password_edit.setFocus()

    def setup_ui(self):
        """Setup the login user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)  # Increased spacing for a more airy feel

        # Logo section
        self._setup_logo_section(main_layout)

        # Login form section
        self._setup_login_form(main_layout)

        # Additional options section
        self._setup_additional_options(main_layout)

        # Status message area
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("margin-top: 5px;")
        main_layout.addWidget(self.status_label)

        # Connect signals
        self.login_button.clicked.connect(self.login)
        self.password_edit.returnPressed.connect(self.login)
        self.username_edit.returnPressed.connect(lambda: self.password_edit.setFocus())

    def _setup_logo_section(self, parent_layout):
        """Setup the logo and title section."""
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(0, 0, 0, 10)  # Added bottom margin

        # Try to load logo image
        logo_path = Path(__file__).parent.parent.parent / "resources/logo.png"
        if logo_path.exists():
            logo_label = QLabel()
            pixmap = QPixmap(str(logo_path))
            logo_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            logo_layout.addWidget(logo_label)

        # Title and subtitle
        title_layout = QVBoxLayout()
        title_layout.setSpacing(5)  # Tighter spacing between title and subtitle

        title_label = QLabel("Abu Mukh Car Parts")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_font = QFont("Segoe UI", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setObjectName("titleLabel")

        subtitle_label = QLabel(self.translator.t('login:login_subtitle'))
        subtitle_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        subtitle_font = QFont("Segoe UI", 12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setObjectName("subtitleLabel")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        logo_layout.addLayout(title_layout)

        parent_layout.addLayout(logo_layout)

        # Add a separator line - more subtle
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Plain)  # Changed to Plain for a cleaner look
        separator.setObjectName("separator")
        parent_layout.addWidget(separator)

    def _setup_login_form(self, parent_layout):
        """Setup the login form with username and password fields."""
        form_layout = QFormLayout()
        form_layout.setSpacing(20)  # Increased spacing
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Username field
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText(self.translator.t('login:username_placeholder'))
        self.username_edit.setMinimumHeight(50)
        self.username_edit.setObjectName("loginInput")

        # Password field
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText(self.translator.t('login:password_placeholder'))
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setMinimumHeight(50)
        self.password_edit.setObjectName("loginInput")

        # Add drop shadow to input fields for a modern look
        for widget in [self.username_edit, self.password_edit]:
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 25))
            shadow.setOffset(0, 2)
            widget.setGraphicsEffect(shadow)

        # Add form fields with labels
        form_layout.addRow(self.translator.t('login:username_label') + ":", self.username_edit)
        form_layout.addRow(self.translator.t('login:password_label') + ":", self.password_edit)

        parent_layout.addLayout(form_layout)

        # Remember me checkbox
        self.remember_me_checkbox = QCheckBox(self.translator.t('login:remember_me'))
        self.remember_me_checkbox.setStyleSheet("margin: 5px 0;")
        parent_layout.addWidget(self.remember_me_checkbox)

        # Login button
        self.login_button = QPushButton(self.translator.t('login:login_button'))
        self.login_button.setMinimumHeight(55)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setObjectName("loginButton")

        # Add shadow effect to button
        button_shadow = QGraphicsDropShadowEffect()
        button_shadow.setBlurRadius(20)
        button_shadow.setColor(QColor(0, 0, 0, 50))
        button_shadow.setOffset(0, 4)
        self.login_button.setGraphicsEffect(button_shadow)

        parent_layout.addWidget(self.login_button)

    def _setup_additional_options(self, parent_layout):
        """Setup additional options like forgot password, etc."""
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0, 10, 0, 0)  # Added top margin

        # Forgot password button (styled as a link)
        self.forgot_password_btn = QPushButton(self.translator.t('login:forgot_password'))
        self.forgot_password_btn.setFlat(True)
        self.forgot_password_btn.setCursor(Qt.PointingHandCursor)
        self.forgot_password_btn.setObjectName("linkButton")
        self.forgot_password_btn.clicked.connect(self.show_password_reset)

        options_layout.addWidget(self.forgot_password_btn)
        options_layout.addStretch()

        parent_layout.addLayout(options_layout)

    def apply_theme(self):
        """Apply styling and theme to the login widget."""
        # Get colors from theme system
        bg_color = get_color('background')
        text_color = get_color('text')
        button_color = get_color('button')
        button_hover = get_color('button_hover')
        button_pressed = get_color('button_pressed')
        input_bg = get_color('input_bg')
        border_color = get_color('border')
        highlight_color = get_color('highlight')
        accent_color = get_color('accent')
        title_color = get_color('title')

        # Create slightly darker/lighter variations of background for depth
        theme_name = [k for k, v in THEMES.items() if v.get('background') == bg_color]
        is_dark_theme = theme_name and theme_name[0] in ['dark', 'classic'] or bg_color.startswith('#0') or bg_color.startswith('#1') or bg_color.startswith('#2')

        # Calculate input background with proper contrast
        if is_dark_theme:
            # For dark themes, make input slightly lighter
            input_overlay = "rgba(255, 255, 255, 0.05)"
            shadow_color = "rgba(0, 0, 0, 0.3)"
            hover_overlay = "rgba(255, 255, 255, 0.1)"
        else:
            # For light themes, make input slightly darker
            input_overlay = "rgba(0, 0, 0, 0.03)"
            shadow_color = "rgba(0, 0, 0, 0.1)"
            hover_overlay = "rgba(0, 0, 0, 0.05)"

        # Apply stylesheet
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                color: {text_color};
                font-family: 'Segoe UI', 'SF Pro Display', 'Inter', sans-serif;
            }}
            
            QLabel {{
                font-size: 14px;
                font-weight: normal;
                color: {text_color};
            }}
            
            #titleLabel {{
                color: {title_color};
                font-weight: bold;
            }}
            
            #subtitleLabel {{
                color: {text_color};
                opacity: 0.7;
            }}
            
            #separator {{
                background-color: {border_color};
                max-height: 1px;
                opacity: 0.5;
                margin: 8px 0;
                border: none;
            }}
            
            #loginInput {{
                background-color: {input_bg};
                color: {text_color};
                border: none;
                border-radius: 14px;
                padding: 12px 16px;
                font-size: 14px;
                selection-background-color: {highlight_color};
            }}
            
            #loginInput:focus {{
                background-color: {input_bg};
                border: 1px solid {highlight_color};
            }}
            
            #loginInput::placeholder {{
                color: {text_color};
                opacity: 0.4;
            }}
            
            #loginButton {{
                background-color: {button_color};
                color: white;
                border: none;
                border-radius: 14px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                letter-spacing: 0.5px;
            }}
            
            #loginButton:hover {{
                background-color: {button_hover};
            }}
            
            #loginButton:pressed {{
                background-color: {button_pressed};
            }}
            
            QPushButton:disabled {{
                background-color: {button_color};
                opacity: 0.5;
            }}
            
            #linkButton {{
                background-color: transparent;
                color: {highlight_color};
                font-weight: normal;
                text-decoration: none;
                border-radius: 8px;
                padding: 6px 10px;
                box-shadow: none;
            }}
            
            #linkButton:hover {{
                color: {accent_color};
                background-color: {hover_overlay};
            }}
            
            QCheckBox {{
                font-size: 14px;
                spacing: 8px;
                color: {text_color};
            }}
            
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
                border: 1px solid {border_color};
                border-radius: 7px;
                background-color: {input_bg};
            }}
            
            QCheckBox::indicator:hover {{
                border: 1px solid {highlight_color};
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {highlight_color};
                border: 1px solid {highlight_color};
                image: none;
            }}
            
            QCheckBox::indicator:checked:hover {{
                background-color: {accent_color};
                border: 1px solid {accent_color};
            }}
        """)

        # Set status label colors based on theme
        self.status_label.setStyleSheet(f"""
            color: {get_color('error', '#F6465D')};
            margin-top: 5px;
        """)

    def login(self):
        """Handle login authentication."""
        self.status_label.setText("")
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        if not username or not password:
            self.status_label.setText(self.translator.t('login:fields_required'))
            return

        # Try to authenticate
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            user_data = self.users_db.authenticate(username, password)

            if user_data:
                # Handle remember me
                if self.remember_me_checkbox.isChecked():
                    self._save_remembered_username(username)
                else:
                    self._clear_remembered_username()

                self.current_user = user_data
                self.status_label.setText(self.translator.t('login:login_successful'))
                self.status_label.setStyleSheet(f"color: {get_color('success', '#0ECB81')}; margin-top: 5px;")

                # Emit successful login signal with user data
                self.login_successful.emit(user_data)
            else:
                self.status_label.setText(self.translator.t('login:invalid_credentials'))
                self.password_edit.clear()
                self.password_edit.setFocus()

        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            self.status_label.setText(self.translator.t('login:system_error'))
        finally:
            QApplication.restoreOverrideCursor()

    def show_password_reset(self):
        """Display the password reset dialog."""
        username = self.username_edit.text().strip()

        if not username:
            QMessageBox.information(
                self,
                self.translator.t('login:password_reset'),
                self.translator.t('login:enter_username_first')
            )
            self.username_edit.setFocus()
            return

        dialog = PasswordChangeDialog(
            username,
            self.users_db,
            self.translator,
            self
        )

        if dialog.exec_():
            self.status_label.setText(self.translator.t('login:password_reset_success'))
            self.status_label.setStyleSheet(f"color: {get_color('success', '#0ECB81')}; margin-top: 5px;")
            self.password_edit.clear()
            self.password_edit.setFocus()

    def _save_remembered_username(self, username):
        """Save the remembered username to settings."""
        try:
            from database.settings_db import SettingsDB
            settings_db = SettingsDB()
            settings_db.save_setting('remembered_username', username)
            settings_db.close()
        except Exception as e:
            logger.error(f"Error saving remembered username: {e}")

    def _clear_remembered_username(self):
        """Clear the remembered username from settings."""
        try:
            from database.settings_db import SettingsDB
            settings_db = SettingsDB()
            settings_db.save_setting('remembered_username', '')
            settings_db.close()
        except Exception as e:
            logger.error(f"Error clearing remembered username: {e}")

    def _load_remembered_username(self):
        """Load the remembered username from settings."""
        try:
            from database.settings_db import SettingsDB
            settings_db = SettingsDB()
            username = settings_db.get_setting('remembered_username', '')
            settings_db.close()
            return username
        except Exception as e:
            logger.error(f"Error loading remembered username: {e}")
            return ''

    def update_translations(self):
        """Update all translatable text in the UI."""
        self.setWindowTitle(self.translator.t('login:window_title'))

        # Update form labels and placeholders
        form_layout = None
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if isinstance(item.layout(), QFormLayout):
                form_layout = item.layout()
                break

        if form_layout:
            # Update username row
            username_label = form_layout.itemAt(0, QFormLayout.LabelRole).widget()
            username_label.setText(self.translator.t('login:username_label') + ":")
            self.username_edit.setPlaceholderText(self.translator.t('login:username_placeholder'))

            # Update password row
            password_label = form_layout.itemAt(1, QFormLayout.LabelRole).widget()
            password_label.setText(self.translator.t('login:password_label') + ":")
            self.password_edit.setPlaceholderText(self.translator.t('login:password_placeholder'))

        # Update other UI elements
        self.remember_me_checkbox.setText(self.translator.t('login:remember_me'))
        self.login_button.setText(self.translator.t('login:login_button'))
        self.forgot_password_btn.setText(self.translator.t('login:forgot_password'))

        # Find and update subtitle
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if isinstance(item.layout(), QHBoxLayout):
                for j in range(item.layout().count()):
                    sub_item = item.layout().itemAt(j)
                    if isinstance(sub_item.layout(), QVBoxLayout):
                        # This should be the title/subtitle layout
                        if sub_item.layout().count() >= 2:
                            subtitle = sub_item.layout().itemAt(1).widget()
                            if isinstance(subtitle, QLabel):
                                subtitle.setText(self.translator.t('login:login_subtitle'))