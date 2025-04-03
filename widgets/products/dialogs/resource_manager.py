# --- resource_manager.py ---

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import os
import logging # Use logging instead of print for warnings

# Setup basic logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

class ResourceManager:
    _icons = {}
    _pixmaps = {}
    _base_path = "resources" # Define base path once

    @staticmethod
    def _get_resource_path(name, suffix=".png"):
        """Constructs the full path to the resource."""
        # Allow specifying suffix directly in name (e.g., "logo.svg")
        if '.' in name:
             filename = name
        else:
             filename = f"{name}{suffix}"
        return os.path.join(ResourceManager._base_path, filename)

    @staticmethod
    def get_icon(name):
        """Get cached icon or load if not available. Returns default QIcon on failure."""
        if name not in ResourceManager._icons:
            path = ResourceManager._get_resource_path(name, "_icon.png")
            if os.path.exists(path):
                ResourceManager._icons[name] = QIcon(path)
                # logging.debug(f"Loaded icon: {path}") # Optional: Log successful loads
            else:
                logging.warning(f"Icon resource not found: {path}. Returning empty icon.")
                ResourceManager._icons[name] = QIcon() # Return empty QIcon
        return ResourceManager._icons[name]

    @staticmethod
    def get_pixmap(name, width=None, height=None):
        """Get cached pixmap or load if not available. Returns default QPixmap on failure."""
        # Use tuple for key elements for clarity
        key = (name, width, height)
        if key not in ResourceManager._pixmaps:
            # Assume .png if no extension, adjust suffix logic as needed
            path = ResourceManager._get_resource_path(name, ".png" if '.' not in name else '')
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull() and width and height:
                    pixmap = pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                elif pixmap.isNull():
                     logging.warning(f"Failed to load pixmap data from: {path}. Returning empty pixmap.")
                     pixmap = QPixmap() # Create empty if load failed
                ResourceManager._pixmaps[key] = pixmap
                # logging.debug(f"Loaded pixmap: {path}") # Optional: Log successful loads
            else:
                logging.warning(f"Pixmap resource not found: {path}. Returning empty pixmap.")
                ResourceManager._pixmaps[key] = QPixmap() # Return empty QPixmap
        return ResourceManager._pixmaps[key]

    @staticmethod
    def preload_common_resources():
        """Preload commonly used resources at app startup"""
        # Use constants defined elsewhere if available
        common_icons = [
            'save', 'cancel', 'clear', 'delete', 'filter', 'reset', 'warning',
            'question', 'error', 'info', 'print', 'export', 'check', 'add', # Add any others
            'edit', 'search', 'up', 'down', 'left', 'right'
        ]
        logging.info("Preloading common icons...")
        for icon_name in common_icons:
            ResourceManager.get_icon(icon_name)
        logging.info("Icon preloading complete.")
        # Preload pixmaps if needed
        # ResourceManager.get_pixmap("logo", 100, 50)

# Example usage:
if __name__ == '__main__':
    # This block won't run when imported, but is useful for testing
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv) # Need an app context for QIcon/QPixmap
    ResourceManager.preload_common_resources()
    save_icon = ResourceManager.get_icon('save')
    non_existent_icon = ResourceManager.get_icon('non_existent')
    print(f"Save Icon is null: {save_icon.isNull()}")
    print(f"Non-existent Icon is null: {non_existent_icon.isNull()}")

    warning_pixmap = ResourceManager.get_pixmap('warning', 32, 32)
    print(f"Warning Pixmap is null: {warning_pixmap.isNull()}")
    # sys.exit(app.exec_()) # Keep event loop running if needed for visual test