"""Theme management system for the application.

This module provides theme management, color retrieval, and styling functions.
"""
from PyQt5.QtGui import QColor

from .definitions import THEMES, SIZE, FONT_SIZE, BASE_UNIT
from .core import (
    set_theme, get_color, temp_theme, logger,
    get_size, get_font_size, get_base_unit
)
from .styling import apply_enhanced_borders, apply_dialog_theme

# Export the API
__all__ = [
    'THEMES', 'SIZE', 'FONT_SIZE', 'BASE_UNIT',
    'set_theme', 'get_color', 'temp_theme',
    'get_size', 'get_font_size', 'get_base_unit',
    'apply_enhanced_borders', 'apply_dialog_theme'
]