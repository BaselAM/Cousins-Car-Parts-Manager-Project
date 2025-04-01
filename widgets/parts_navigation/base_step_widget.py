"""
Base class for all navigation step widgets.
Provides common functionality and standardized interfaces.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from themes import get_color
from logger import get_logger

logger = get_logger('parts_navigation.base')

class BaseStepWidget(QWidget):
    """Base class for all navigation step widgets."""

    # Signal emitted when this step is completed
    step_completed = pyqtSignal(dict)

    def __init__(self, translator, db, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.db = db
        self.step_data = {}  # Data for this step
        self.is_loading = False

        # Configure responsive sizing - make the widget expand to fill space
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set generous minimum size for a better default appearance
        self.setMinimumWidth(850)

        self.setup_ui()
        self.apply_theme()

    def sizeHint(self):
        """Override to provide a better default size."""
        return QSize(950, 600)

    def setup_ui(self):
        """Initialize and arrange UI elements. Override in subclasses."""
        self.main_layout = QVBoxLayout(self)
        # Use generous margins for a more spacious layout
        self.main_layout.setContentsMargins(25, 25, 25, 25)
        self.main_layout.setSpacing(20)

        # Title
        self.title = QLabel()
        self.title.setObjectName("stepTitle")
        self.title.setAlignment(Qt.AlignCenter)

        # Make title larger and bolder
        font = self.title.font()
        font.setPointSize(font.pointSize() + 2)
        font.setBold(True)
        self.title.setFont(font)

        self.main_layout.addWidget(self.title)

        # Loading indicator
        self.loading_frame = QFrame()
        loading_layout = QVBoxLayout(self.loading_frame)
        self.loading_label = QLabel(self.translator.t('loading'))
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setObjectName("loadingLabel")

        # Make loading text larger
        font = self.loading_label.font()
        font.setPointSize(font.pointSize() + 2)
        font.setBold(True)
        self.loading_label.setFont(font)

        loading_layout.addWidget(self.loading_label)
        self.main_layout.addWidget(self.loading_frame)
        self.loading_frame.hide()

        # Help text at bottom
        self.help_text = QLabel()
        self.help_text.setObjectName("helpText")
        self.help_text.setAlignment(Qt.AlignCenter)
        self.help_text.setWordWrap(True)

        # Make help text more visible
        font = self.help_text.font()
        font.setPointSize(font.pointSize() + 1)
        self.help_text.setFont(font)

        self.main_layout.addWidget(self.help_text)

    def apply_theme(self):
        """Apply current theme. Override in subclasses for custom styling."""
        bg_color = get_color('background')
        card_bg = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        highlight = get_color('highlight')

        self.setStyleSheet(f"""
            #stepTitle {{
                color: {text_color};
                font-size: 22px;  /* Increased from 18px */
                font-weight: bold;
                margin-bottom: 18px;  /* Increased from 10px */
                padding: 5px;
            }}
            
            QLabel {{
                color: {text_color};
                font-size: 15px;  /* Increased from 14px */
            }}
            
            #loadingLabel {{
                color: {highlight};
                font-size: 20px;  /* Increased from 16px */
                font-weight: bold;
                padding: 15px;  /* Increased from 10px */
                background-color: {get_color('card_bg')};
                border-radius: 10px;
                border: 1px dashed {highlight};
                margin: 10px 50px;  /* Add some margin for better appearance */
            }}
            
            #helpText {{
                color: {get_color('secondary_text')};
                font-size: 15px;  /* Increased from 13px */
                font-style: italic;
                margin-top: 15px;  /* Increased from 10px */
                padding: 10px;
                background-color: {get_color('card_bg')};
                border-radius: 8px;
                border: 1px solid {get_color('border')};
            }}
        """)

    def update_translations(self):
        """Update all translatable text. Override in subclasses."""
        self.loading_label.setText(self.translator.t('loading'))

    def reset(self):
        """Reset this step's data. Override in subclasses if needed."""
        self.step_data = {}

    def on_show(self):
        """Called when this step is shown. Override in subclasses if needed."""
        pass

    def on_hide(self):
        """Called when this step is hidden. Override in subclasses if needed."""
        pass

    def can_proceed(self):
        """Check if user can proceed to next step. Override in subclasses."""
        return bool(self.step_data)

    def get_step_data(self):
        """Get the data for this step. Override in subclasses if needed."""
        return self.step_data

    def set_previous_step_data(self, data):
        """Set data from previous step. Override in subclasses."""
        pass

    def show_loading(self, show=True):
        """Show or hide the loading indicator"""
        self.is_loading = show
        if show:
            self.loading_frame.show()
        else:
            self.loading_frame.hide()

    def handle_error(self, error_msg):
        """Handle an error in a standardized way"""
        self.show_loading(False)
        logger.error(f"Error in {self.__class__.__name__}: {error_msg}")