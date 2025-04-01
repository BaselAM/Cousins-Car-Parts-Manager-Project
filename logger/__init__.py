"""
Logging system for Abu Mukh Car Parts Management System.

Provides a consistent, configurable logging interface throughout the application.
"""
import logging
import os
import sys
from typing import Optional, Dict

from .config import MODULE_LEVELS, LOG_DIR
from .handlers import (get_console_handler, get_file_handler,
                       get_error_file_handler, get_debug_file_handler)
from .filters import ModuleFilter, ExcludeFilter, SensitiveDataFilter

# Track initialization state
_logger_initialized = False


def initialize_logging(level: str = "INFO", config_file: Optional[str] = None) -> None:
    """
    Initialize the logging system.

    Args:
        level: Default logging level
        config_file: Optional path to logging configuration file
    """
    global _logger_initialized

    if _logger_initialized:
        return

    # Fix for Windows console encoding issues with non-ASCII characters
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')

    # Create log directory if it doesn't exist
    os.makedirs(LOG_DIR, exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level))

    # Apply filters to root logger
    root_logger.addFilter(SensitiveDataFilter())

    # Add handlers to root logger
    root_logger.addHandler(get_console_handler())
    root_logger.addHandler(get_file_handler())
    root_logger.addHandler(get_error_file_handler())

    if level == "DEBUG":
        root_logger.addHandler(get_debug_file_handler())

    # Configure module-specific loggers
    for module, module_level in MODULE_LEVELS.items():
        module_logger = logging.getLogger(module)
        module_logger.setLevel(getattr(logging, module_level))

    # Mark as initialized
    _logger_initialized = True

    # Log initialization
    root_logger.info(f"Logging system initialized (level: {level})")
    root_logger.info(f"Log files directory: {LOG_DIR}")

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name (typically __name__)

    Returns:
        logging.Logger: Configured logger for the module
    """
    # Initialize if not already done
    if not _logger_initialized:
        initialize_logging()

    return logging.getLogger(name)


def set_log_level(name: str, level: str) -> None:
    """
    Set the log level for a specific module.

    Args:
        name: Module name
        level: New log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))


