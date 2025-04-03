# --- ui_utils.py ---

from PyQt5.QtWidgets import (QPushButton, QLabel, QLineEdit, QSpinBox,
                             QDoubleSpinBox, QComboBox, QWidget, QFormLayout,
                             QHBoxLayout, QVBoxLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QColor

from themes import get_color # Assuming themes.py exists and provides get_color
from resource_manager import ResourceManager
import constants # Import the constants

# --- Button Creation ---

def create_button(text_key, translator, icon_name=None, tooltip_key=None, style_type=None, object_name=None, parent=None):
    """Creates a QPushButton with standard settings."""
    button = QPushButton(translator.t(text_key), parent)
    button.setCursor(Qt.PointingHandCursor)

    if icon_name:
        button.setIcon(ResourceManager.get_icon(icon_name))

    if tooltip_key:
        button.setToolTip(translator.t(tooltip_key))

    if object_name:
        button.setObjectName(object_name)

    # Apply specific styling based on type
    apply_button_style(button, style_type)

    return button

def apply_button_style(button, style_type):
    """Applies predefined styles to a button."""
    style_sheet = ""
    if style_type == constants.STYLE_PRIMARY:
        highlight_color = get_color('highlight', '#3498db') # Provide default fallback
        bg_color = get_color('background', '#ffffff')
        text_color = QColor(bg_color) # Text color contrasts with highlight

        style_sheet = f"""
            QPushButton#{button.objectName()} {{
                background-color: {highlight_color};
                color: {text_color.name()};
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton#{button.objectName()}:hover {{
                background-color: {QColor(highlight_color).lighter(110).name()};
            }}
            QPushButton#{button.objectName()}:pressed {{
                background-color: {QColor(highlight_color).darker(110).name()};
            }}
            QPushButton#{button.objectName()}:disabled {{
                background-color: {QColor(highlight_color).lighter(150).name()};
                color: {QColor(text_color).darker(110).name()};
            }}
        """
    elif style_type == constants.STYLE_DANGER:
        danger_color = get_color('danger', '#e74c3c') # Provide default fallback
        text_color = get_color('danger_text', '#ffffff')

        style_sheet = f"""
            QPushButton#{button.objectName()} {{
                background-color: {danger_color};
                color: {text_color};
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 5px;
            }}
            QPushButton#{button.objectName()}:hover {{
                background-color: {QColor(danger_color).lighter(110).name()};
            }}
            QPushButton#{button.objectName()}:pressed {{
                background-color: {QColor(danger_color).darker(110).name()};
            }}
             QPushButton#{button.objectName()}:disabled {{
                background-color: {QColor(danger_color).lighter(150).name()};
                color: {QColor(text_color).darker(110).name()};
            }}
        """
    # Add more styles (e.g., SECONDARY) if needed, or rely on base dialog QSS
    else:
         # Rely on the default QSS from ElegantDialog or Qt
         pass

    if style_sheet:
        # Append to existing stylesheet if any, otherwise set it
        existing_style = button.styleSheet()
        button.setStyleSheet(existing_style + "\n" + style_sheet)


# --- Form Row Creation ---

def create_form_row(layout, label_key, translator, widget, is_required=False):
    """Adds a label and a widget to a QFormLayout."""
    label_text = translator.t(label_key)
    if is_required:
        label = QLabel(f"{label_text} *:")
        # Optional: Make required label bold visually
        font = label.font()
        font.setBold(True)
        label.setFont(font)
    else:
        label = QLabel(f"{label_text}:")

    label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
    layout.addRow(label, widget)
    return label, widget # Return them if needed for direct access


# --- Input Widget Creation ---

def create_line_edit(placeholder_key, translator, parent=None):
    """Creates a QLineEdit with a translated placeholder."""
    widget = QLineEdit(parent)
    widget.setPlaceholderText(translator.t(placeholder_key))
    return widget

def create_spin_box(min_val, max_val, default_val, parent=None):
    """Creates a QSpinBox with predefined settings."""
    widget = QSpinBox(parent)
    widget.setRange(min_val, max_val)
    widget.setValue(default_val)
    widget.setButtonSymbols(QSpinBox.UpDownArrows)
    return widget

def create_double_spin_box(min_val, max_val, default_val, decimals=2, prefix=None, parent=None):
    """Creates a QDoubleSpinBox with predefined settings."""
    widget = QDoubleSpinBox(parent)
    widget.setRange(min_val, max_val)
    widget.setValue(default_val)
    widget.setDecimals(decimals)
    if prefix:
        widget.setPrefix(prefix)
    widget.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
    # Avoid BetterDoubleSpinBox unless absolutely necessary and well-tested
    return widget


# --- Validation Feedback ---

_error_timers = {} # Keep track of timers to avoid conflicts

def show_validation_error(widget, message_container_layout, message_key, translator, duration=3000):
    """Highlights a widget and shows a temporary error message."""
    # Highlight widget
    original_stylesheet = widget.styleSheet()
    widget.setStyleSheet(original_stylesheet + "; border: 2px solid red;")

    # Create and show error label
    error_color = get_color('status_error_text', '#C62828') # Default red
    error_label = QLabel(translator.t(message_key))
    error_label.setStyleSheet(f"color: {error_color}; font-weight: bold; padding: 5px 0;")
    # Insert near the top, e.g., after a title (index 1 typically) or at index 0
    insert_index = 1 if message_container_layout.count() > 0 else 0
    message_container_layout.insertWidget(insert_index, error_label)

    # --- Timer to remove error ---
    widget_id = id(widget) # Use widget's ID as key

    # If there's an existing timer for this widget, stop it
    if widget_id in _error_timers:
        _error_timers[widget_id].stop()
        # Find and remove old error label if it exists (might be tricky if layout changed)
        # This part is complex, simpler to just let the new timer handle cleanup.

    def clear_error():
        # Check if widget still exists and error_label hasn't been manually removed
        try:
            if widget and error_label and error_label.parent():
                widget.setStyleSheet(original_stylesheet) # Restore original style
                error_label.deleteLater() # Safely remove the label
            if widget_id in _error_timers:
                del _error_timers[widget_id] # Clean up timer entry
        except RuntimeError: # Catch errors if widgets were deleted prematurely
             if widget_id in _error_timers:
                del _error_timers[widget_id]

    # Start a new timer
    timer = QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(clear_error)
    timer.start(duration)
    _error_timers[widget_id] = timer # Store the new timer


# --- Layout Helpers ---

def create_button_box(buttons, alignment=Qt.AlignRight, spacing=10):
    """Creates a standard horizontal layout for buttons."""
    layout = QHBoxLayout()
    layout.setSpacing(spacing)
    if alignment == Qt.AlignLeft:
        for button in buttons:
            layout.addWidget(button)
        layout.addStretch(1)
    elif alignment == Qt.AlignRight:
        layout.addStretch(1)
        for button in buttons:
            layout.addWidget(button)
    else: # Center alignment (approximate)
        layout.addStretch(1)
        for button in buttons:
            layout.addWidget(button)
        layout.addStretch(1)
    return layout