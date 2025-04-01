"""
Elegant, compact chat settings dialog with refined styling.
"""

import os
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QWidget,
    QGroupBox, QRadioButton, QButtonGroup
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor

from logger import get_logger
from .custom_widgets import ElegantGroupBox, RichTextLabel
from .utils import is_dark_theme

# Get a module-specific logger
logger = get_logger(__name__)

# Import themes module if available
try:
    import themes
except ImportError:
    logger.warning("Themes module not found, using fallback colors")
    # Create a fallback themes module
    class FallbackThemes:
        @staticmethod
        def get_color(name):
            if is_dark_theme():
                colors = {
                    'card_bg': '#1E1E1E',
                    'text': '#FFFFFF',
                    'border': '#444444',
                    'highlight': '#3F51B5',
                    'button': '#3F51B5',
                    'input_bg': '#2D2D2D',
                    'warning': '#F57F17'
                }
            else:
                colors = {
                    'card_bg': '#FFFFFF',
                    'text': '#212121',
                    'border': '#DDDDDD',
                    'highlight': '#3F51B5',
                    'button': '#3F51B5',
                    'input_bg': '#F5F5F5',
                    'warning': '#F57F17'
                }
            return colors.get(name, '#000000')
    themes = FallbackThemes()


class ChatSettingsDialog(QDialog):
    """Dialog for configuring chat settings with elegant design"""

    def __init__(self, parent=None, current_key=None, api_issue=False):
        super().__init__(parent)

        # Initialize variables
        self.api_key = current_key
        self.api_issue = api_issue
        self.use_fallback_mode = False

        # Set up dialog properties
        self.setWindowTitle("Chat Settings")
        self.setMinimumWidth(400)  # Smaller, more compact
        self.setFixedHeight(400)  # Fixed height for compactness
        self.setModal(True)

        # Apply custom styling
        self.apply_elegant_styling()

        # Center on parent window
        self.center_on_parent()

        # Create layout
        self.setup_ui()

        logger.debug("Settings dialog initialized")

    def center_on_parent(self):
        """Center the dialog on the parent window"""
        if self.parent():
            parent_geometry = self.parent().window().frameGeometry()
            center_point = parent_geometry.center()

            # Calculate position to center this dialog on the parent
            frame_geometry = self.frameGeometry()
            frame_geometry.moveCenter(center_point)
            self.move(frame_geometry.topLeft())
            logger.debug("Dialog centered on parent window")

    def apply_elegant_styling(self):
        """Apply refined, elegant styling to the dialog"""
        bg_color = themes.get_color('card_bg')
        text_color = themes.get_color('text')
        border_color = themes.get_color('border')
        highlight_color = themes.get_color('highlight')
        button_color = themes.get_color('button')

        # Make sure text is visible against the background
        input_bg = QColor(bg_color).lighter(
            115).name() if is_dark_theme() else QColor(bg_color).darker(105).name()
        button_text = "#FFFFFF"  # White text for buttons

        # Base dialog styling
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}

            QLabel {{
                color: {text_color};
                font-family: 'Segoe UI', Arial, sans-serif;
            }}

            QLabel[cssClass="title"] {{
                font-size: 16px;
                font-weight: bold;
            }}

            QLabel[cssClass="subtitle"] {{
                font-size: 13px;
                color: {QColor(text_color).lighter(120).name() if is_dark_theme() else QColor(text_color).darker(120).name()};
            }}

            QRadioButton {{
                color: {text_color};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                spacing: 8px;
                padding: 2px;
            }}

            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 1px solid {border_color};
            }}

            QRadioButton::indicator:unchecked {{
                background-color: {bg_color};
            }}

            QRadioButton::indicator:checked {{
                background-color: {highlight_color};
                border: 1px solid {highlight_color};
            }}

            QLineEdit {{
                background-color: {input_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
            }}

            QPushButton {{
                background-color: {button_color};
                color: {button_text};
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 13px;
                min-width: 80px;
            }}

            QPushButton:hover {{
                background-color: {QColor(button_color).lighter(115).name()};
            }}

            QPushButton:pressed {{
                background-color: {QColor(button_color).darker(110).name()};
            }}

            QPushButton#primaryButton {{
                background-color: {highlight_color};
            }}

            QPushButton#primaryButton:hover {{
                background-color: {QColor(highlight_color).lighter(115).name()};
            }}

            QPushButton#secondaryButton {{
                background-color: transparent;
                color: {text_color};
                border: 1px solid {border_color};
            }}

            QPushButton#secondaryButton:hover {{
                background-color: rgba(128, 128, 128, 0.1);
                border: 1px solid {highlight_color};
            }}

            QGroupBox {{
                font-weight: bold;
                margin-top: 14px;
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 10px;
                padding-top: 20px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                background-color: {bg_color};
            }}
        """)

        logger.debug("Applied elegant styling to dialog")

    def setup_ui(self):
        """Set up compact UI with elegant elements"""
        logger.debug("Setting up settings dialog UI")

        # Main layout with smaller margins
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)

        # Header section - more compact
        header_layout = QHBoxLayout()

        # Small icon if available
        icon_label = QLabel()
        icon_path = os.path.join("resources", "chatbot.png")  # Adjust path as needed
        try:
            pixmap = QPixmap(icon_path).scaled(24, 24, Qt.KeepAspectRatio,
                                               Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            header_layout.addWidget(icon_label)
        except:
            logger.warning("Chat icon not found for settings dialog")  # Skip icon if not found

        # Title
        title = QLabel("Chat Assistant Settings")
        title.setProperty("cssClass", "title")
        header_layout.addWidget(title)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Brief description with warning if API issue
        if self.api_issue:
            description = QLabel("API quota exceeded. Choose how to proceed:")
            description.setProperty("cssClass", "subtitle")
            description.setStyleSheet(f"color: {themes.get_color('warning')};")
            logger.warning("Showing settings dialog due to API quota issue")
        else:
            description = QLabel("Configure your chat assistant:")
            description.setProperty("cssClass", "subtitle")

        layout.addWidget(description)

        # Mode selection group
        modes_group = ElegantGroupBox("Operation Mode")
        modes_layout = QVBoxLayout(modes_group)
        modes_layout.setSpacing(8)

        # Local mode option
        self.local_mode_radio = QRadioButton("Built-in car knowledge base")
        self.local_mode_radio.setToolTip("Works offline with no API calls")

        # API mode option
        self.api_mode_radio = QRadioButton("OpenAI API (more advanced)")
        self.api_mode_radio.setToolTip("Requires API key")

        # Create button group
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.local_mode_radio, 1)
        self.mode_group.addButton(self.api_mode_radio, 2)

        # Set default based on current state
        if self.api_issue or not self.api_key:
            self.local_mode_radio.setChecked(True)
            self.use_fallback_mode = True
            logger.debug("Default mode set to local knowledge base")
        else:
            self.api_mode_radio.setChecked(True)
            self.use_fallback_mode = False
            logger.debug("Default mode set to OpenAI API")

        # Connect change event
        self.mode_group.buttonClicked.connect(self.toggle_api_section)

        # Add to group layout
        modes_layout.addWidget(self.local_mode_radio)
        modes_layout.addWidget(self.api_mode_radio)

        layout.addWidget(modes_group)

        # API section
        self.api_section = ElegantGroupBox("API Key")
        api_layout = QVBoxLayout(self.api_section)

        # API key input
        self.key_input = QLineEdit()
        if self.api_key:
            self.key_input.setText(self.api_key)
        self.key_input.setPlaceholderText("Enter your OpenAI API key (sk-...)")

        api_layout.addWidget(self.key_input)

        # Small note on security
        key_note = QLabel("Your API key is stored securely on this device only.")
        key_note.setProperty("cssClass", "subtitle")
        key_note.setStyleSheet("font-size: 11px; font-style: italic;")
        api_layout.addWidget(key_note)

        layout.addWidget(self.api_section)

        # Info section - more compact
        info_label = QLabel(
            "<b>Note:</b> The built-in knowledge base works offline with no limits.")
        info_label.setProperty("cssClass", "subtitle")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # API links section
        links_label = RichTextLabel(
            "<a href='https://platform.openai.com/api-keys'>Get API key</a> | <a href='https://platform.openai.com/billing'>Billing</a>")

        links_label.setStyleSheet("""
            QLabel {
                color: #1E62D0; /* Lighter sapphire blue */
                background: transparent;
                font-size: 12px;
            }
            QLabel a {
                color: #1E62D0;
                text-decoration: none;
            }
            QLabel a:hover {
                color: #1E62D0;
                text-decoration: underline;
            }
        """)
        layout.addWidget(links_label)

        # Add stretch to push buttons to bottom
        layout.addStretch()

        # Button section
        button_layout = QHBoxLayout()

        # Clear key button if key exists
        if self.api_key:
            clear_btn = QPushButton("Clear Key")
            clear_btn.setObjectName("secondaryButton")
            clear_btn.clicked.connect(self.clear_key)
            button_layout.addWidget(clear_btn)
            logger.debug("Added clear key button - API key exists")

        button_layout.addStretch()

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.clicked.connect(self.reject)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.setObjectName("primaryButton")
        save_btn.clicked.connect(self.accept)
        save_btn.setDefault(True)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

        # Initial API section visibility
        self.toggle_api_section()

        logger.debug("Settings dialog UI setup complete")

    def toggle_api_section(self):
        """Show or hide API key section based on selected mode"""
        if hasattr(self, 'api_section') and hasattr(self, 'mode_group'):
            # Show API section only if API mode is selected (id 2)
            show_api = self.mode_group.checkedId() == 2
            self.api_section.setVisible(show_api)
            logger.debug(f"API section visibility set to: {show_api}")

    def clear_key(self):
        """Clear the API key"""
        self.key_input.clear()
        self.local_mode_radio.setChecked(True)
        self.toggle_api_section()
        logger.info("API key cleared from settings dialog")

    def accept(self):
        """Save settings and close"""
        # Determine which mode is selected
        self.use_fallback_mode = (self.mode_group.checkedId() == 1)

        if not self.use_fallback_mode:
            self.api_key = self.key_input.text().strip()
            logger.info("Saving settings: Using OpenAI API mode")
            if not self.api_key:
                logger.warning("API mode selected but no key provided")
        else:
            self.api_key = None
            logger.info("Saving settings: Using local knowledge base mode")

        logger.debug("Settings dialog accepted, closing")
        super().accept()

    def reject(self):
        """Cancel settings changes and close"""
        logger.debug("Settings dialog cancelled, no changes saved")
        super().reject()

    def showEvent(self, event):
        """Ensure dialog is centered when shown"""
        super().showEvent(event)
        self.center_on_parent()