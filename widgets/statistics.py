from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from themes import get_color  # Import theme function



class StatisticsWidget(QWidget):
    def __init__(self, translator):
        super().__init__()
        self.setObjectName("statisticsContainer")  # Added for CSS styling
        self.translator = translator
        self.setup_ui()
        self.apply_theme()  # Apply theme on initialization

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        # Graph placeholder
        self.graph_placeholder = QLabel()
        self.graph_placeholder.setFixedHeight(300)
        self.graph_placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.graph_placeholder)

        # Stats info
        self.stats_info = QLabel()
        self.stats_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_info)

        # Refresh button
        self.refresh_button = QPushButton()
        self.refresh_button.clicked.connect(lambda: print("Refreshing statistics..."))
        layout.addWidget(self.refresh_button, alignment=Qt.AlignCenter)

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
        self.title_label.setStyleSheet(f"""
            {label_style}
            font-size: 24px;
            font-weight: bold;
            border-width: 2px;
            background-color: {get_color('primary')};
        """)

        # Graph placeholder
        self.graph_placeholder.setStyleSheet(f"""
            {label_style}
            font-size: 18px;
            border-style: dashed;
        """)

        # Stats info
        self.stats_info.setStyleSheet(f"""
            {label_style}
            font-size: 16px;
            border-top: none;
        """)

        # Refresh button
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
        self.refresh_button.setStyleSheet(btn_style)

    def update_translations(self):
        """Update text content from translations"""
        self.title_label.setText(self.translator.t('statistics_button'))
        self.graph_placeholder.setText(self.translator.t('graph_placeholder'))
        self.stats_info.setText(self.translator.t('stats_info'))
        self.refresh_button.setText(self.translator.t('refresh_statistics'))