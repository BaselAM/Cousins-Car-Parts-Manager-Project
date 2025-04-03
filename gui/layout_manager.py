# gui/layout_manager.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget


class GUILayoutManager:
    """
    Manages layout direction and RTL support.
    Handles direction changes and applying them throughout the application.
    """

    def __init__(self, parent, rtl_enabled=False):
        """
        Initialize the layout manager.

        Args:
            parent: The main GUI instance
            rtl_enabled: Boolean indicating if RTL layout is enabled
        """
        self.parent = parent
        self.rtl_enabled = rtl_enabled

    def apply_layout_direction_initially(self):
        """Set initial layout direction based on settings"""
        direction = Qt.RightToLeft if self.rtl_enabled else Qt.LeftToRight
        QApplication.setLayoutDirection(direction)
        self._apply_layout_direction_recursive(self.parent, direction)

    def update_layout_direction(self, is_rtl):
        """
        Update layout direction throughout the application.

        Args:
            is_rtl: Boolean indicating if RTL layout should be enabled
        """
        self.rtl_enabled = is_rtl
        direction = Qt.RightToLeft if is_rtl else Qt.LeftToRight
        QApplication.setLayoutDirection(direction)
        self._apply_layout_direction_recursive(self.parent, direction)

    def _apply_layout_direction_recursive(self, widget, direction):
        """
        Recursively set layout direction for all child widgets.

        Args:
            widget: The parent widget
            direction: Qt.LeftToRight or Qt.RightToLeft
        """
        widget.setLayoutDirection(direction)
        for child in widget.findChildren(QWidget):
            child.setLayoutDirection(direction)