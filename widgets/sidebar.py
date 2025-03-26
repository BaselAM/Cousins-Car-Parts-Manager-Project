from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt
from themes import get_color  # Import only the required function



class SidebarWidget(QWidget):
    def __init__(self, translator, button_actions):
        super().__init__()
        self.translator = translator
        self.setup_ui(button_actions)
        self.apply_theme()

    def setup_ui(self, button_actions):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(2)

        self.buttons = {}
        for btn_id, text in [
            ('products_button', self.translator.t('products_button')),
            ('statistics_button', self.translator.t('statistics_button')),
            ('settings_button', self.translator.t('settings_button')),
            ('help_button', self.translator.t('help_button')),
            ('exit_button', self.translator.t('exit_button'))
        ]:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(button_actions[btn_id])
            self.buttons[btn_id] = btn
            layout.addWidget(btn)

        layout.addStretch()

    def apply_theme(self):
        sidebar_style = f"""
            QPushButton {{
                background-color: {get_color('sidebar_button')};
                color: {get_color('text')};
                border: none;
                padding: 15px 20px;
                margin: 8px 0;
                text-align: center;
                font-weight: bold;
                font-size: 16px;
                border-radius: 8px;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: {get_color('button_hover')};
            }}
            QPushButton:pressed {{
                background-color: {get_color('button_pressed')};
            }}
        """
        for btn in self.buttons.values():
            btn.setStyleSheet(sidebar_style)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.setStyleSheet(f"""
            background-color: {get_color('sidebar_bg')};
            border-right: 1px solid {get_color('border')};
        """)
    def update_translations(self):
        for key, btn in self.buttons.items():
            btn.setText(self.translator.t(key))

