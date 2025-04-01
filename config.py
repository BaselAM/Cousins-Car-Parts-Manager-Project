"""
Centralized configuration for the Abu Mukh Car Parts Management System.
Defines application-wide constants and paths to ensure consistency.
"""
import os
import sys
from pathlib import Path
import logging

# Set up logger
from logger import get_logger
logger = get_logger(__name__)

# Define application root directory - use different methods to ensure robustness
try:
    # Method 1: Using __file__ of the config module
    APP_ROOT = Path(__file__).resolve().parent

    # Validate that this directory contains expected subdirectories
    expected_dirs = ["database", "translations", "resources", "widgets"]
    found_dirs = [d for d in expected_dirs if (APP_ROOT / d).exists()]

    if len(found_dirs) < 2:  # If less than half of expected directories exist
        # Method 2: Try to find the app root by climbing up
        # This helps when running from a different directory
        current_dir = Path(os.getcwd()).resolve()
        for _ in range(3):  # Check up to 3 parent directories
            # Check if key directories exist
            if all((current_dir / d).exists() for d in ["database", "translations"]):
                APP_ROOT = current_dir
                break
            current_dir = current_dir.parent

    # Log the determined application root
    logger.info(f"Determined application root: {APP_ROOT}")

except Exception as e:
    # Fallback to current working directory if all else fails
    logger.error(f"Error determining application root: {e}")
    APP_ROOT = Path(os.getcwd()).resolve()
    logger.warning(f"Falling back to current directory as app root: {APP_ROOT}")

# Define standard directories
RESOURCE_DIR = APP_ROOT / "resources"
DATABASE_DIR = APP_ROOT / "database"
TRANSLATIONS_DIR = APP_ROOT / "translations"
TRANSLATIONS_DATA_DIR = TRANSLATIONS_DIR / "data"
WIDGETS_DIR = APP_ROOT / "widgets"
LOG_DIR = APP_ROOT / "logs"

# Create necessary directories if they don't exist
for path in [RESOURCE_DIR, DATABASE_DIR, TRANSLATIONS_DIR, TRANSLATIONS_DATA_DIR, LOG_DIR]:
    if not path.exists():
        try:
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {path}")
        except Exception as e:
            logger.warning(f"Could not create directory {path}: {e}")

# Database file paths
SETTINGS_DB_PATH = DATABASE_DIR / "settings.db"
USERS_DB_PATH = DATABASE_DIR / "users.db"
PARTS_DB_PATH = DATABASE_DIR / "car_parts.db"
NOTIFICATIONS_DB_PATH = DATABASE_DIR / "notifications.db"

# Application version and metadata
APP_VERSION = "1.0.0"
APP_NAME = "Abu Mukh Car Parts"
APP_AUTHOR = "Basel A.M"

# Ensure resource paths can be resolved when packaged
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    RESOURCE_DIR = Path(sys._MEIPASS) / "resources"
    logger.info(f"Running as frozen application, resources at: {RESOURCE_DIR}")

# Add app root to Python path to simplify imports
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))
    logger.info(f"Added {APP_ROOT} to Python path")

# Helper function to get resource paths
def get_resource_path(resource_name):
    """
    Get the absolute path to a resource file.

    Args:
        resource_name: Name of the resource file (e.g., "icons/add_icon.png")

    Returns:
        Path: Absolute path to the resource
    """
    path = RESOURCE_DIR / resource_name
    if not path.exists():
        logger.warning(f"Resource not found: {path}")
    return path