from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton


class SimpleStatisticsWidget(QWidget):
    """A minimal statistics widget for testing"""

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.db = None

        # Very simple UI
        layout = QVBoxLayout(self)
        label = QLabel("Statistics Dashboard (Test Version)")
        layout.addWidget(label)

        button = QPushButton("Refresh Data")
        button.clicked.connect(self.refresh_data)
        layout.addWidget(button)

    def setup_database(self, db):
        """Simplified database setup"""
        self.db = db
        print("Database connection set up")

    def refresh_data(self):
        """Simplified refresh method"""
        print("Refresh called")

    def update_translations(self):
        """Stub method for translation updates"""
        pass