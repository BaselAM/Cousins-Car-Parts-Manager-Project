"""
Custom handlers for the logging system.
"""
import logging
import logging.handlers
import sys
import io
from .config import (DEFAULT_LOG_FILE, ERROR_LOG_FILE, DEBUG_LOG_FILE,
                     MAX_LOG_SIZE, BACKUP_COUNT)
from .formatters import StandardFormatter, DetailedFormatter, ColoredConsoleFormatter


def get_console_handler():
    """Create and configure a console handler with proper Unicode support."""

    # Define a custom stream handler with UTF-8 support
    class UTF8StreamHandler(logging.StreamHandler):
        def __init__(self, stream=None):
            # Use stdout if no stream is provided
            if stream is None:
                stream = sys.stdout

            # Wrap the stream with UTF-8 encoding if on Windows
            if sys.platform == 'win32' and hasattr(stream, 'buffer'):
                # Create a text wrapper with UTF-8 encoding
                stream = io.TextIOWrapper(stream.buffer,
                                          encoding='utf-8',
                                          errors='backslashreplace')

            super().__init__(stream)

        def emit(self, record):
            try:
                msg = self.format(record)
                stream = self.stream
                # Write with proper error handling
                stream.write(msg + self.terminator)
                self.flush()
            except Exception:
                self.handleError(record)

    # Create our UTF-8 capable handler
    console_handler = UTF8StreamHandler()
    console_handler.setFormatter(ColoredConsoleFormatter())
    return console_handler

def get_file_handler():
    """Create and configure the standard file handler."""
    file_handler = logging.handlers.RotatingFileHandler(
        DEFAULT_LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT
    )
    file_handler.setFormatter(StandardFormatter())
    return file_handler


def get_error_file_handler():
    """Create and configure error file handler."""
    error_handler = logging.handlers.RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(DetailedFormatter())
    return error_handler


def get_debug_file_handler():
    """Create and configure debug file handler."""
    debug_handler = logging.handlers.RotatingFileHandler(
        DEBUG_LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(DetailedFormatter())
    return debug_handler


class DatabaseHandler(logging.Handler):
    """Custom handler that stores logs in database."""

    def __init__(self, db_connection=None):
        super().__init__()
        self.db_connection = db_connection

    def emit(self, record):
        if not self.db_connection:
            return

        try:
            msg = self.format(record)
            # Implementation for storing log in database would go here
            # For example:
            # self.db_connection.execute(
            #     "INSERT INTO logs (timestamp, level, message) VALUES (?, ?, ?)",
            #     (record.created, record.levelname, msg)
            # )
        except Exception:
            self.handleError(record)