"""
Quantity selector component with mode-aware styling.
"""
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSpinBox
from PyQt5.QtGui import QColor, QCursor

from themes import get_color


class QuantitySelector(QWidget):
    """A custom quantity selector with +/- buttons and a spinbox that's aware of transaction mode."""

    quantity_changed = pyqtSignal(int)

    def __init__(self, parent=None, initial_value=1, min_value=1, max_value=999, mode="view"):
        super().__init__(parent)
        self.min_value = min_value
        self.max_value = max_value
        self.mode = mode  # "view", "sell", or "supply"
        self.setup_ui(initial_value)

    def setup_ui(self, initial_value):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Minus button
        self.minus_btn = QPushButton("-")
        self.minus_btn.setFixedSize(36, 36)
        self.minus_btn.setObjectName("quantityButton")
        self.minus_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.minus_btn.clicked.connect(self.decrease_quantity)

        # Quantity spinbox
        self.spinbox = QSpinBox()
        self.spinbox.setMinimum(self.min_value)
        self.spinbox.setMaximum(self.max_value)
        self.spinbox.setValue(initial_value)
        self.spinbox.setFixedHeight(36)
        self.spinbox.setMinimumWidth(60)
        self.spinbox.setAlignment(Qt.AlignCenter)
        self.spinbox.valueChanged.connect(self.on_quantity_changed)

        # Plus button
        self.plus_btn = QPushButton("+")
        self.plus_btn.setFixedSize(36, 36)
        self.plus_btn.setObjectName("quantityButton")
        self.plus_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.plus_btn.clicked.connect(self.increase_quantity)

        # Add widgets to layout
        layout.addWidget(self.minus_btn)
        layout.addWidget(self.spinbox)
        layout.addWidget(self.plus_btn)

        # Apply styling
        self.apply_styling()

    def apply_styling(self):
        """Apply consistent styling to the quantity selector."""
        button_style = f"""
            QPushButton#quantityButton {{
                background-color: {get_color('button')};
                color: {get_color('text')};
                border-radius: 6px;
                font-weight: bold;
                font-size: 18px;
            }}

            QPushButton#quantityButton:hover {{
                background-color: {get_color('button_hover')};
            }}

            QPushButton#quantityButton:pressed {{
                background-color: {get_color('button_pressed')};
            }}

            QSpinBox {{
                background-color: {get_color('input_bg')};
                color: {get_color('text')};
                border: 1px solid {get_color('border')};
                border-radius: 6px;
                padding: 2px 8px;
                font-size: 16px;
            }}

            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0;
                height: 0;
                border: none;
            }}
        """
        self.setStyleSheet(button_style)

    def increase_quantity(self):
        """Increase the quantity by 1."""
        current = self.spinbox.value()
        self.spinbox.setValue(current + 1)

    def decrease_quantity(self):
        """Decrease the quantity by 1."""
        current = self.spinbox.value()
        if current > self.min_value:
            self.spinbox.setValue(current - 1)

    def on_quantity_changed(self, value):
        """Emit signal when quantity changes."""
        self.quantity_changed.emit(value)

    def get_quantity(self):
        """Get the current quantity value."""
        return self.spinbox.value()

    def set_quantity(self, value):
        """Set the quantity value."""
        self.spinbox.setValue(value)

    def set_mode(self, mode, current_stock=None):
        """Set the transaction mode and adjust limits accordingly.

        Args:
            mode (str): 'view', 'sell', or 'supply'
            current_stock (int, optional): Current stock level, used for 'sell' mode
        """
        self.mode = mode

        # Adjust limits based on mode
        if mode == "sell" and current_stock is not None:
            # In sell mode, can't sell more than current stock
            max_value = max(1, current_stock)
            self.spinbox.setMaximum(max_value)

            # If current value exceeds stock, adjust it
            if self.spinbox.value() > max_value:
                self.spinbox.setValue(max_value)

            # Apply sell mode styling
            self.setObjectName("sellModeSelector")

        elif mode == "supply":
            # In supply mode, can add large quantities
            self.spinbox.setMaximum(999)

            # Apply supply mode styling
            self.setObjectName("supplyModeSelector")

        else:  # "view" mode
            # In view mode, use the default max value
            self.spinbox.setMaximum(self.max_value)

            # Apply default styling
            self.setObjectName("viewModeSelector")

        # Apply mode-specific styling
        self.update_mode_styling()

    def update_mode_styling(self):
        """Apply visual styling based on current mode."""
        base_style = self.styleSheet()

        # Remove any previous mode styling
        base_style = base_style.replace("#sellModeSelector {", "#ignoreThis {")
        base_style = base_style.replace("#supplyModeSelector {", "#ignoreThis {")
        base_style = base_style.replace("#viewModeSelector {", "#ignoreThis {")

        # Add mode-specific styles
        error_color = QColor(get_color('error', '#F44336'))
        highlight_color = QColor(get_color('highlight', '#2196F3'))

        if self.mode == "sell":
            border_color = error_color
            extra_style = f"""
                #sellModeSelector QSpinBox {{
                    border: 2px solid {border_color.name()};
                }}

                #sellModeSelector QPushButton#quantityButton {{
                    border: 1px solid {border_color.name()};
                }}
            """
        elif self.mode == "supply":
            border_color = highlight_color
            extra_style = f"""
                #supplyModeSelector QSpinBox {{
                    border: 2px solid {border_color.name()};
                }}

                #supplyModeSelector QPushButton#quantityButton {{
                    border: 1px solid {border_color.name()};
                }}
            """
        else:  # view mode
            extra_style = ""

        # Apply the updated style
        self.setStyleSheet(base_style + extra_style)