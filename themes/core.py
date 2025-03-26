"""Core theme functionality."""
import logging
from contextlib import contextmanager
from PyQt5.QtGui import QColor
from .definitions import THEMES

# Set up a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Current theme tracking
_current_theme = "classic"


def set_theme(theme_name):
    """Change the current theme.

    Args:
        theme_name (str): Name of the theme to set. Must exist in THEMES dictionary.
    """
    global _current_theme
    _current_theme = theme_name if theme_name in THEMES else "classic"


def get_color(color_key, fallback=None):
    """Retrieve a theme color value using a key, with an optional fallback.

    Args:
        color_key (str): The color key to look up in the current theme
        fallback (str, optional): Fallback color if key isn't found

    Returns:
        str: Hex color code or fallback value
    """
    try:
        return THEMES[_current_theme][color_key]
    except KeyError:
        logger.warning("Color key '%s' not found in theme '%s'. Using fallback.", color_key, _current_theme)
        return fallback if fallback is not None else QColor(0, 0, 0)


@contextmanager
def temp_theme(theme_name):
    """Temporarily change theme for a code block.

    Usage:
        with temp_theme("dark"):
            # Code using dark theme here
    """
    original = _current_theme
    set_theme(theme_name)
    try:
        yield
    finally:
        set_theme(original)