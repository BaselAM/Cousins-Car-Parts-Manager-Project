"""Simple event system for theme changes."""
from PyQt5.QtCore import QObject, pyqtSignal


class ThemeEventManager(QObject):
    """Manages theme change events for the application."""

    # Signal emitted when theme changes, with theme name
    theme_changed = pyqtSignal(str)

    def notify_theme_change(self, theme_name):
        """Notify all connected widgets about a theme change."""
        self.theme_changed.emit(theme_name)


# Create a singleton instance for app-wide use
theme_event_manager = ThemeEventManager()