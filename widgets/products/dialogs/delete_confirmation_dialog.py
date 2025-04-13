"""
Enhanced delete confirmation dialog using the new styled widgets system.

This dialog confirms with the user before deleting selected products.
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QColor

from themes import get_color
from widgets.products.dialogs.base_dialog import ElegantDialog
from widgets.products.components.styled_widgets import StyledPushButton, StyledTitleLabel


class DeleteConfirmationDialog(ElegantDialog):
    """An elegant confirmation dialog for deleting products with premium styling."""

    def __init__(self, products, translator, parent=None):
        super().__init__(translator, parent, title='confirm_delete')
        self.products = products
        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog UI with styled widgets"""
        # Warning icon and title
        title_layout = QHBoxLayout()
        warning_icon = QLabel()
        icon_path = "resources/warning_icon.png"
        try:
            warning_icon.setPixmap(QIcon(icon_path).pixmap(48, 48))
        except:
            # Fallback to emoji if icon not found
            warning_icon.setText("⚠️")
            warning_icon.setStyleSheet("font-size: 32px;")

        warning_icon.setFixedSize(48, 48)
        warning_label = StyledTitleLabel(self.translator.t('confirm_delete'))

        title_layout.addWidget(warning_icon)
        title_layout.addWidget(warning_label, 1)
        self.main_layout.addLayout(title_layout)

        # Confirmation message
        msg = self.translator.t('delete_confirmation').format(count=len(self.products))
        confirmation_label = QLabel(msg)
        confirmation_label.setWordWrap(True)
        self.main_layout.addWidget(confirmation_label)

        # List of products to delete (if not too many)
        if len(self.products) <= 10:
            products_frame = QFrame()
            products_frame.setFrameShape(QFrame.StyledPanel)
            bg_color = get_color('card_bg', get_color('background'))
            products_frame.setStyleSheet(f"background-color: {bg_color}; border-radius: 8px; padding: 8px;")
            products_layout = QVBoxLayout(products_frame)

            for pid, name in self.products:
                product_label = QLabel(f"• {name} (ID: {pid})")
                products_layout.addWidget(product_label)

            self.main_layout.addWidget(products_frame)
        else:
            # Just show count for many products
            count_label = QLabel(
                self.translator.t('items_selected').format(count=len(self.products)))
            count_label.setAlignment(Qt.AlignCenter)
            count_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            self.main_layout.addWidget(count_label)

        # Add separator before buttons
        self.add_separator()

        # Create buttons with appropriate styling
        cancel_btn = StyledPushButton(self.translator.t('cancel'))
        if not QIcon("resources/cancel_icon.png").isNull():
            cancel_btn.setIcon(QIcon("resources/cancel_icon.png"))
        cancel_btn.clicked.connect(self.reject)

        # Style delete button as a danger button
        delete_btn_text = self.translator.t('yes_btn').format(count=len(self.products))
        delete_btn = StyledPushButton(delete_btn_text)
        if not QIcon("resources/delete_icon.png").isNull():
            delete_btn.setIcon(QIcon("resources/delete_icon.png"))
        delete_btn.clicked.connect(self.accept)

        # Apply custom danger styling to delete button
        danger_color = get_color('error', "#f44336")  # Red color for danger
        danger_text = "#ffffff"  # White text

        delete_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {danger_color};
                color: {danger_text};
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 5px;
                min-height: 34px;
            }}
            QPushButton:hover {{
                background-color: {QColor(danger_color).lighter(110).name()};
            }}
            QPushButton:pressed {{
                background-color: {QColor(danger_color).darker(110).name()};
            }}
        """)

        # Add buttons to layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(delete_btn)

        self.main_layout.addLayout(button_layout)