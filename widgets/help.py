from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton
from PyQt5.QtCore import Qt
from themes import get_color  # Import for theming



class HelpWidget(QWidget):
    def __init__(self, translator):
        super().__init__()
        self.setObjectName("helpContainer")  # Added for CSS styling
        self.translator = translator
        self.setup_ui()
        self.apply_theme()  # Apply theme on initialization

    def setup_ui(self):
        # Create layout and widgets without styling
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        self.help_title = QLabel()
        self.help_title.setAlignment(Qt.AlignCenter)

        # Description
        self.help_description = QLabel()
        self.help_description.setWordWrap(True)
        self.help_description.setAlignment(Qt.AlignCenter)

        # Grid Layout
        grid = QGridLayout()
        grid.setHorizontalSpacing(30)
        grid.setVerticalSpacing(15)

        self.contact_label = QLabel()
        self.steps_label = QLabel()

        # Buttons
        self.email_btn = QPushButton()
        self.guide_btn = QPushButton()

        # Footer
        self.footer_note = QLabel()
        self.footer_note.setAlignment(Qt.AlignCenter)

        # Add widgets to layout
        grid.addWidget(self.contact_label, 0, 0)
        grid.addWidget(self.steps_label, 0, 1)
        grid.addWidget(self.email_btn, 1, 0)
        grid.addWidget(self.guide_btn, 1, 1)

        layout.addWidget(self.help_title)
        layout.addWidget(self.help_description)
        layout.addLayout(grid)
        layout.addWidget(self.footer_note)

        # Set initial translations
        self.update_translations()

    def apply_theme(self):
        """Apply current theme to all elements"""
        # Common styles
        label_style = f"""
            color: {get_color('text')};
            border: 1px solid {get_color('border')};
            padding: 8px;
            border-radius: 5px;
            background-color: {get_color('secondary')};
        """

        # Title
        self.help_title.setStyleSheet(f"""
            {label_style}
            font-size: 24px;
            font-weight: bold;
            border-width: 2px;
            background-color: {get_color('primary')};
        """)

        # Description
        self.help_description.setStyleSheet(f"""
            {label_style}
            font-size: 16px;
            border-top: none;
        """)

        # Contact and Steps labels
        label_style_simple = f"""
            {label_style}
            font-size: 16px;
            background-color: transparent;
            border: none;
        """
        self.contact_label.setStyleSheet(label_style_simple)
        self.steps_label.setStyleSheet(label_style_simple)

        # Footer
        self.footer_note.setStyleSheet(f"""
            {label_style}
            font-size: 14px;
            font-style: italic;
            border-top: 2px solid {get_color('border')};
            border-bottom: none;
            border-left: none;
            border-right: none;
            background-color: transparent;
        """)

        # Buttons
        btn_style = f"""
            QPushButton {{
                background-color: {get_color('button')};
                color: {get_color('text')};
                border: 1px solid {get_color('border')};
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {get_color('button_hover')};
            }}
            QPushButton:pressed {{
                background-color: {get_color('button_pressed')};
            }}
        """
        self.email_btn.setStyleSheet(btn_style)
        self.guide_btn.setStyleSheet(btn_style)

    def update_translations(self):
        """Update text content from translations"""
        self.help_title.setText(self.translator.t('help_documentation'))
        self.help_description.setText(self.translator.t('help_description'))
        self.contact_label.setText(self.translator.t('contact_support'))
        self.steps_label.setText(self.translator.t('quick_steps'))
        self.email_btn.setText(self.translator.t('email_us'))
        self.guide_btn.setText(self.translator.t('user_guide'))
        self.footer_note.setText(self.translator.t('help_footer_note'))