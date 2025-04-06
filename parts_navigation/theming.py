"""
Theming utilities for the parts navigation system.

This module provides theme-related functions and utilities for consistent
styling across the application.
"""
from PyQt5.QtGui import QFont, QFontDatabase, QColor

from themes import get_color


def load_premium_fonts():
    """
    Load premium fonts for the application.

    Registers SF Pro and similar fonts for a more premium look.
    """
    # In a real application with proper font licensing, we would load actual font files
    # For now, we'll rely on system-similar fonts that approximate the premium feel

    # Try to find and register SF Pro family or similar if available
    font_families = QFontDatabase.families()

    # Check for preferred fonts in this order
    preferred_fonts = [
        "SF Pro Display", "SF Pro Text",  # macOS/iOS
        "Segoe UI", "Segoe UI Variable",  # Windows
        "Roboto", "Google Sans",  # Android/Google
        "Helvetica Neue", "Helvetica",  # Generic premium
        "Arial", "Liberation Sans"  # Universal fallbacks
    ]

    # Log available fonts that match our preferences
    available_premium_fonts = []
    for font in preferred_fonts:
        if any(font.lower() in f.lower() for f in font_families):
            available_premium_fonts.append(font)

    return available_premium_fonts


def generate_stylesheet(colors=None):
    """
    Generate a comprehensive stylesheet with premium styling.

    Args:
        colors: Optional dictionary of colors to override defaults

    Returns:
        str: Complete stylesheet for premium styling
    """
    # Use provided colors or get from theme system
    if not colors:
        colors = {
            'background': get_color('background', '#0F2942'),
            'card_bg': get_color('card_bg', '#1E3A5F'),
            'text': get_color('text', '#E2E8F0'),
            'highlight': get_color('highlight', '#4299E1'),
            'border': get_color('border', '#2C5282'),
            'button': get_color('button', '#3182CE'),
            'button_hover': get_color('button_hover', '#4299E1'),
            'button_pressed': get_color('button_pressed', '#2B6CB0'),
            'button_disabled': get_color('button_disabled', '#718096'),
            'text_disabled': get_color('text_disabled', '#A0AEC0'),
            'secondary_text': get_color('secondary_text', '#A0AEC0')
        }

    # Compute derived colors for enhanced styling
    card_bg_lighter = QColor(colors['card_bg']).lighter(108).name()
    highlight_lighter = QColor(colors['highlight']).lighter(115).name()
    highlight_darker = QColor(colors['highlight']).darker(115).name()

    # Create rgba format for the highlight with transparency
    h_color = QColor(colors['highlight'])
    highlight_trans = f"rgba({h_color.red()}, {h_color.green()}, {h_color.blue()}, 0.2)"

    # Return comprehensive stylesheet with premium styling
    return f"""
        /* Base typography for the whole application */
        * {{
            font-family: "SF Pro Text", "Segoe UI", "Roboto", "Helvetica Neue", "Arial", sans-serif;
        }}

        /* Headings */
        h1, h2, h3, #stepTitle, #partsNavigationTitle {{
            font-family: "SF Pro Display", "Segoe UI", "Roboto", "Helvetica Neue", "Arial", sans-serif;
            font-weight: bold;
            letter-spacing: -0.2px;
        }}

        /* Main containers */
        #partsNavigationContainer {{
            background-color: {colors['background']};
        }}

        #partsContent {{
            background-color: {colors['card_bg']};
            border-radius: 12px;
            border: none;
            padding: 15px;
        }}

        /* Scroll bars with premium styling */
        QScrollBar:vertical {{
            background: {colors['background']};
            width: 14px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background: {colors['border']};
            min-height: 20px;
            border-radius: 7px;
            margin: 2px;
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            background: {colors['background']};
            height: 14px;
            margin: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background: {colors['border']};
            min-width: 20px;
            border-radius: 7px;
            margin: 2px;
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}

        /* Buttons with premium styling */
        QPushButton {{
            background-color: {colors['button']};
            color: {colors['text']};
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 600;
            border: none;
        }}

        QPushButton:hover {{
            background-color: {colors['button_hover']};
        }}

        QPushButton:pressed {{
            background-color: {colors['button_pressed']};
        }}

        QPushButton:disabled {{
            background-color: {colors['button_disabled']};
            color: {colors['text_disabled']};
        }}

        #primaryButton {{
            background-color: {colors['highlight']};
            color: white;
            font-weight: bold;
        }}

        #primaryButton:hover {{
            background-color: {highlight_lighter};
        }}

        #primaryButton:pressed {{
            background-color: {highlight_darker};
        }}

        /* Input elements with premium styling */
        QLineEdit, QComboBox, QSpinBox {{
            background-color: {card_bg_lighter};
            color: {colors['text']};
            border: 1px solid {colors['border']};
            border-radius: 6px;
            padding: 8px;
        }}

        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border: 1px solid {colors['highlight']};
            background-color: {QColor(card_bg_lighter).darker(102).name()};
        }}

        /* Forms with premium styling */
        QLabel {{
            color: {colors['text']};
        }}

        #formLabel {{
            font-weight: bold;
            color: {colors['text']};
        }}

        /* Help text with premium styling */
        #helpText {{
            color: {colors['secondary_text']};
            font-style: italic;
            font-size: 13px;
        }}
    """


def apply_ios_style(widget, colors=None):
    """
    Apply iOS-style design to a specific widget.

    Args:
        widget: The widget to style
        colors: Optional dictionary of colors to override defaults
    """
    # Use provided colors or get from theme system
    if not colors:
        colors = {
            'background': get_color('background', '#0F2942'),
            'card_bg': get_color('card_bg', '#1E3A5F'),
            'text': get_color('text', '#E2E8F0'),
            'highlight': get_color('highlight', '#4299E1'),
            'border': get_color('border', '#2C5282')
        }

    # iOS-style rounded corners, subtle shadows, and clean typography
    widget.setStyleSheet(f"""
        background-color: {colors['card_bg']};
        color: {colors['text']};
        border-radius: 10px;
        border: 1px solid {colors['border']};
    """)

    # Apply SF Pro font if available
    try:
        font = QFont("SF Pro Text", widget.font().pointSize())
        widget.setFont(font)
    except:
        pass  # Use default font if SF Pro is not available


def apply_card_style(widget, colors=None):
    """
    Apply card-style design to a widget.

    Args:
        widget: The widget to style
        colors: Optional dictionary of colors to override defaults
    """
    # Use provided colors or get from theme system
    if not colors:
        colors = {
            'card_bg': get_color('card_bg', '#1E3A5F'),
            'text': get_color('text', '#E2E8F0'),
            'border': get_color('border', '#2C5282')
        }

    # Card style with proper padding, rounded corners, and border
    widget.setStyleSheet(f"""
        background-color: {colors['card_bg']};
        color: {colors['text']};
        border-radius: 10px;
        border: 1px solid {colors['border']};
        padding: 15px;
    """)