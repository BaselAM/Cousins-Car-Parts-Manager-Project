"""
Custom formatters for the logging system.
"""
import logging
from datetime import datetime

from .config import DEFAULT_FORMAT, DETAILED_FORMAT, CONSOLE_FORMAT


class StandardFormatter(logging.Formatter):
    """Standard formatter for general logging."""

    def __init__(self):
        super().__init__(DEFAULT_FORMAT)


class DetailedFormatter(logging.Formatter):
    """Detailed formatter with source location information."""

    def __init__(self):
        super().__init__(DETAILED_FORMAT)


class ColoredConsoleFormatter(logging.Formatter):
    """Formatter that adds color to console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[94m',  # Blue
        'INFO': '\033[92m',  # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',  # Red
        'CRITICAL': '\033[41m\033[97m',  # White on Red background
        'RESET': '\033[0m'  # Reset color
    }

    def __init__(self):
        super().__init__(CONSOLE_FORMAT)

    def format(self, record):
        log_message = super().format(record)
        if record.levelname in self.COLORS and not record.exc_info:
            log_message = f"{self.COLORS[record.levelname]}{log_message}{self.COLORS['RESET']}"
        return log_message