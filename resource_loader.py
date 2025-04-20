"""
Resource loader utility for the Abu Mukh Car Parts application.
Provides consistent resource loading in both development and executable environments.
"""
import os
import sys
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ResourceLoader:
    """Utility class for loading application resources consistently"""

    def __init__(self):
        # Determine base path based on whether we're frozen or not
        if getattr(sys, 'frozen', False):
            # Running as executable
            self.base_path = Path(sys._MEIPASS)
        else:
            # Running in development
            self.base_path = Path(os.path.dirname(os.path.abspath(__file__)))

        # Set up resource directories
        self.resource_dir = self.base_path / 'resources'
        self.icons_dir = self.resource_dir

        # Log resource paths
        logger.info(f"Base path: {self.base_path}")
        logger.info(f"Resource directory: {self.resource_dir}")

        # Check if resource directory exists
        if not self.resource_dir.exists():
            logger.warning(f"Resource directory not found: {self.resource_dir}")

    def get_resource_path(self, relative_path):
        """
        Get absolute path to a resource file.

        Args:
            relative_path: Relative path to the resource (e.g., "icons/add_icon.png")

        Returns:
            Path: Absolute path to the resource
        """
        # Handle different path formats
        if isinstance(relative_path, str):
            # Remove leading slashes or backslashes that might cause issues
            relative_path = relative_path.lstrip('/\\')

            # Build the full path
            full_path = self.resource_dir / relative_path
        else:
            # If it's already a Path object
            full_path = self.resource_dir / relative_path

        if not full_path.exists():
            logger.warning(f"Resource not found: {full_path}")

        return full_path

    def get_icon_path(self, icon_name):
        """
        Get absolute path to an icon file.

        Args:
            icon_name: Name of the icon file (e.g., "add_icon.png")

        Returns:
            str: Absolute path to the icon as a string (for PyQt compatibility)
        """
        # Make sure we append .png if it's not already there
        if not icon_name.lower().endswith(('.png', '.jpg', '.svg')):
            icon_name = f"{icon_name}.png"

        icon_path = self.icons_dir / icon_name

        if not icon_path.exists():
            logger.warning(f"Icon not found: {icon_path}")
            # Return a fallback icon path if available
            fallback_icon = self.icons_dir / "default_icon.png"
            if fallback_icon.exists():
                logger.info(f"Using fallback icon: {fallback_icon}")
                return str(fallback_icon)

        return str(icon_path)


# Create a singleton instance
_resource_loader = ResourceLoader()


# Convenience functions
def get_resource_path(relative_path):
    """Get absolute path to a resource file"""
    return _resource_loader.get_resource_path(relative_path)


def get_icon_path(icon_name):
    """Get absolute path to an icon file"""
    return _resource_loader.get_icon_path(icon_name)