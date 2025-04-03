"""Core theme functionality with improved fallback handling."""
import logging
from contextlib import contextmanager
from PyQt5.QtGui import QColor

from .definitions import THEMES, SIZE, FONT_SIZE, BASE_UNIT

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
        # Try to find the key in any theme as a fallback
        for theme_name, theme in THEMES.items():
            if color_key in theme:
                fallback_value = theme[color_key]
                logger.warning(
                    f"Color key '{color_key}' not found in current theme '{_current_theme}', "
                    f"using value from '{theme_name}' theme instead."
                )
                return fallback_value

        # If still not found, use the provided fallback or a default
        logger.warning(
            f"Color key '{color_key}' not found in any theme. Using fallback."
        )
        return fallback if fallback is not None else "#000000"

def get_size(size_key, fallback=None):
    """Retrieve a size constant with improved fallback handling.

    Args:
        size_key (str): The size key to look up
        fallback (int, optional): Fallback size if key isn't found

    Returns:
        int: Size in pixels
    """
    try:
        return SIZE[size_key]
    except KeyError:
        logger.warning(f"Size key '{size_key}' not found. Using fallback.")
        return fallback if fallback is not None else BASE_UNIT

def get_font_size(size_key, fallback=None):
    """Retrieve a font size constant with improved fallback handling.

    Args:
        size_key (str): The font size key to look up
        fallback (int, optional): Fallback font size if key isn't found

    Returns:
        int: Font size in points
    """
    try:
        return FONT_SIZE[size_key]
    except KeyError:
        logger.warning(f"Font size key '{size_key}' not found. Using fallback.")
        return fallback if fallback is not None else FONT_SIZE["regular"]

def get_base_unit():
    """Get the base unit value used for sizing.

    Returns:
        int: Base unit size in pixels
    """
    return BASE_UNIT

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