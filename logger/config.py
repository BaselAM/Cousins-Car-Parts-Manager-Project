"""
Logging system configuration.
"""
import os
from pathlib import Path

# Base paths
APP_ROOT = Path(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
LOG_DIR = APP_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Files
DEFAULT_LOG_FILE = LOG_DIR / "app.log"
ERROR_LOG_FILE = LOG_DIR / "error.log"
DEBUG_LOG_FILE = LOG_DIR / "debug.log"

# Rotation settings
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 5

# Format strings
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DETAILED_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s - %(message)s"
CONSOLE_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Log levels for different modules
MODULE_LEVELS = {
    "database": "INFO",
    "gui": "INFO",
    "widgets": "INFO",
    "translations": "INFO",
    "themes": "INFO",
    "car_chat": "DEBUG",  # Add this line for chat logging
}