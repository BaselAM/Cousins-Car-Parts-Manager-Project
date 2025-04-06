"""
Enhanced search box component.

A premium search box with clean design and animations for the parts navigation system.
"""
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QSizePolicy, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QColor, QPainter, QPen, QBrush

from themes import get_color


class SearchBox(QFrame):
    """
    A premium search box with elegant animations and styling.

    Features:
    - Clean, iOS-inspired design
    - Animation on focus
    - Premium styling with theme support
    - Optional search button
    """
    # Signal emitted when search text changes
    search_changed = pyqtSignal(str)

    # Signal emitted when search is submitted (Enter or button click)
    search_submitted = pyqtSignal(str)

    def __init__(self, translator, placeholder_key='search_placeholder',
                 label_key='search', show_button=True, parent=None):
        """
        Initialize the search box.

        Args:
            translator: Translator for localization
            placeholder_key: Translation key for placeholder text
            label_key: Translation key for label text
            show_button: Whether to show a search button
            parent: Parent widget
        """
        super().__init__(parent)
        self.translator = translator
        self.placeholder_key = placeholder_key
        self.label_key = label_key
        self.show_button = show_button
        self.is_focused = False

        # Set up UI
        self.setObjectName("searchBoxFrame")

        # Critical size policy adjustment - don't expand vertically
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Set maximum height to prevent excessive vertical size
        self.setMaximumHeight(32)

        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Initialize and arrange UI elements with elegant spacing."""
        # Main layout with minimal margins
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 6, 2)  # Reduced from 8,8,8,8
        layout.setSpacing(6)  # Reduced from 8

        # Search label - make more compact
        self.label = QLabel(self.translator.t(self.label_key))
        self.label.setObjectName("searchLabel")
        self.label.setMaximumWidth(70)  # Limit width
        layout.addWidget(self.label)

        # Search input
        self.input = QLineEdit()
        self.input.setObjectName("searchInput")
        self.input.setPlaceholderText(self.translator.t(self.placeholder_key))
        self.input.setClearButtonEnabled(True)  # Show clear button
        self.input.textChanged.connect(self._on_text_changed)
        self.input.returnPressed.connect(self._on_return_pressed)

        # Limit height to make more compact
        self.input.setMinimumHeight(24)
        self.input.setMaximumHeight(28)

        # Add focus/blur event handling
        self.input.installEventFilter(self)

        layout.addWidget(self.input, 1)  # Takes all available space

        # Search button (optional) - make more compact
        if self.show_button:
            self.button = QPushButton()
            self.button.setObjectName("searchButton")
            self.button.setCursor(Qt.PointingHandCursor)
            self.button.clicked.connect(self._on_button_clicked)

            # Limit button size
            self.button.setMaximumWidth(80)
            self.button.setMaximumHeight(28)

            # Set icon if available
            try:
                self.button.setIcon(QIcon("resources/search_icon.png"))
                self.button.setText("")  # If icon, no text
                self.button.setFixedSize(28, 28)  # Square for icon
            except:
                # Fallback to text
                self.button.setText(self.translator.t('search_button'))

            layout.addWidget(self.button)

    def apply_theme(self):
        """Apply premium styling based on system theme."""
        # Get theme colors
        bg_color = get_color('background', '#0F2942')
        card_bg = get_color('card_bg', '#1E3A5F')
        text_color = get_color('text', '#E2E8F0')
        border_color = get_color('border', '#2C5282')
        highlight = get_color('highlight', '#4299E1')
        secondary_text = get_color('secondary_text', '#A0AEC0')

        # Compute derived colors
        card_bg_lighter = QColor(card_bg).lighter(108).name()
        highlight_lighter = QColor(highlight).lighter(115).name()
        highlight_darker = QColor(highlight).darker(115).name()

        # Set frame styling - much more compact styling
        self.setStyleSheet(f"""
            #searchBoxFrame {{
                background-color: {card_bg_lighter};
                border-radius: 6px;  /* Reduced from 8px */
                border: 1px solid {border_color};
                padding: 1px;  /* Reduced from 2px */
            }}

            #searchBoxFrame:focus-within {{
                border: 1px solid {highlight};
                background-color: {card_bg};
            }}

            #searchLabel {{
                color: {text_color};
                margin-right: 3px;  /* Reduced from 5px */
                font-size: 12px;  /* Reduced from 13px */
            }}

            #searchInput {{
                background-color: transparent;
                color: {text_color};
                border: none;
                font-size: 12px;  /* Reduced from 14px */
                padding: 2px 6px;  /* Reduced from 4px 8px */
                selection-background-color: {highlight_lighter};
                selection-color: {text_color};
                min-height: 22px;  /* Reduced minimum height */
            }}

            #searchInput:focus {{
                border: none;
                outline: none;
            }}

            #searchButton {{
                background-color: {highlight};
                color: white;
                border: none;
                border-radius: 4px;  /* Reduced from 6px */
                padding: 2px 8px;  /* Reduced from 5px 10px */
                font-weight: bold;
                font-size: 11px;  /* Reduced from normal size */
            }}

            #searchButton:hover {{
                background-color: {highlight_lighter};
            }}

            #searchButton:pressed {{
                background-color: {highlight_darker};
            }}
        """)

    def update_translations(self):
        """Update all translatable text with elegant handling."""
        # Update label and placeholder
        self.label.setText(self.translator.t(self.label_key))
        self.input.setPlaceholderText(self.translator.t(self.placeholder_key))

        # Update button if it's text-based
        if self.show_button and not self.button.icon().isNull():
            self.button.setText(self.translator.t('search_button'))

    def _on_text_changed(self, text):
        """Handle text changes."""
        # Emit the signal with the new text
        self.search_changed.emit(text)

    def _on_return_pressed(self):
        """Handle Enter key press."""
        # Emit the search submitted signal
        self.search_submitted.emit(self.input.text())

    def _on_button_clicked(self):
        """Handle search button click."""
        # Emit the search submitted signal
        self.search_submitted.emit(self.input.text())

    def clear(self):
        """Clear the search input."""
        self.input.clear()

    def set_text(self, text):
        """Set the search input text."""
        self.input.setText(text)

    def get_text(self):
        """Get the search input text."""
        return self.input.text()

    def eventFilter(self, obj, event):
        """Filter events for focus effects."""
        if obj == self.input:
            if event.type() == event.FocusIn and not self.is_focused:
                self.is_focused = True
                self._animate_focus(True)
            elif event.type() == event.FocusOut and self.is_focused:
                self.is_focused = False
                self._animate_focus(False)

        return super().eventFilter(obj, event)

    def _animate_focus(self, focus_in):
        """Animate focus state changes."""
        # Start with current border color
        current_color = get_color('border') if not self.is_focused else get_color('highlight')
        target_color = get_color('highlight') if focus_in else get_color('border')

        # Get the frame border
        border_width = 1  # Default border width

        # Create and apply custom animation
        # Note: This would be implemented with a property animation in a full implementation
        # For simplicity, we'll just update the style directly
        if focus_in:
            self.setStyleSheet(self.styleSheet().replace(current_color, target_color))
        else:
            self.setStyleSheet(self.styleSheet().replace(current_color, target_color))

    def paintEvent(self, event):
        """Custom paint event for premium appearance."""
        super().paintEvent(event)

        # Optional: Add custom painting effects here
        # For example, you could add a subtle inner shadow