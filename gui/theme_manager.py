# gui/theme_manager.py
from PyQt5.QtWidgets import QWidget
from themes import get_color
from logger import get_logger

logger = get_logger(__name__)


class GUIThemeManager:
    """
    Manages theme application throughout the application.
    Handles theme changes and ensures consistency across all components.
    """

    def __init__(self, parent):
        """
        Initialize the theme manager.

        Args:
            parent: The main GUI instance
        """
        self.parent = parent

    def apply_theme(self):
        """Apply current theme to main window and components"""
        try:
            # Get theme colors
            bg_color = get_color('background')
            text_color = get_color('text')

            # Apply to main window
            self.parent.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {bg_color};
                }}
                QWidget {{
                    color: {text_color};
                    font-family: 'Segoe UI', sans-serif;
                }}
            """)

            # Apply theme to all components that support it
            self._apply_theme_to_all()

        except Exception as e:
            logger.error(f"Error applying theme: {str(e)}")

    def _apply_theme_to_all(self):
        """Apply current theme to all components"""
        try:
            # Get all widgets with apply_theme method
            widgets_with_theme = self._get_themed_widgets()

            # Apply theme to each widget
            for widget in widgets_with_theme:
                if hasattr(widget, 'apply_theme'):
                    widget.apply_theme()

            # Apply to all findable widgets
            for widget in self.parent.findChildren(QWidget):
                if hasattr(widget, 'apply_theme'):
                    widget.apply_theme()

        except Exception as e:
            logger.error(f"Error applying theme to components: {str(e)}")

    def _get_themed_widgets(self):
        """Get list of widgets that need theme application"""
        themed_widgets = []

        # Add header components
        if hasattr(self.parent, 'ui_builder'):
            builder = self.parent.ui_builder
            if hasattr(builder, 'header'):
                themed_widgets.append(builder.header)
            if hasattr(builder, 'top_bar'):
                themed_widgets.append(builder.top_bar)
            if hasattr(builder, 'footer'):
                themed_widgets.append(builder.footer)

        # Add view components
        if hasattr(self.parent, 'view_manager'):
            view_manager = self.parent.view_manager
            themed_widgets.extend([
                view_manager.home_page,
                view_manager.products_widget,
                view_manager.statistics_widget,
                view_manager.settings_widget,
                view_manager.help_widget
            ])

        return [w for w in themed_widgets if w is not None]