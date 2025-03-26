"""Theme management system for the application.

This module provides theme management, color retrieval, and styling functions.
"""
from PyQt5.QtGui import QColor

from .definitions import THEMES
from .core import set_theme, get_color, temp_theme, logger
from .styling import apply_enhanced_borders, apply_dialog_theme

# Make sure the old API is fully preserved
__all__ = [
    'THEMES', 'set_theme', 'get_color', 'temp_theme',
    'apply_enhanced_borders', 'apply_dialog_theme'
]