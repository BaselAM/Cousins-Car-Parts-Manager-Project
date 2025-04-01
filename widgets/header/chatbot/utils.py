"""
Utility functions and classes for the car chat module.
"""

from PyQt5.QtCore import QObject, pyqtSignal
from logger import get_logger

# Replace the current logger with your custom logger
logger = get_logger("car_chat")

def debug_log(message):
    """Log debug messages using the application's logger system"""
    logger.debug(message)

def is_dark_theme():
    """Determine if the current theme is dark based on background color"""
    try:
        import themes
        bg_color = themes.get_color('card_bg')
        bg_color = bg_color.lstrip('#')
        r, g, b = tuple(int(bg_color[i:i + 2], 16) for i in (0, 2, 4))
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return brightness < 128
    except Exception as e:
        logger.error(f"Error determining theme: {e}")
        return False

# Signal bridge for thread safety
class SignalBridge(QObject):
    """Thread-safe signal bridge for communication between threads"""
    update_signal = pyqtSignal(str, bool)
    remove_thinking_signal = pyqtSignal()
    api_error_signal = pyqtSignal(str, str)  # Error message, error type