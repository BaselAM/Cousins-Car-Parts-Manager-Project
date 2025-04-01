# ============== Force UTF-8 console encoding ==============
import sys
import io
import logging

# Force Windows console to use UTF-8
if sys.platform == 'win32':
    import ctypes

    # Try to set console code page to UTF-8
    try:
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)  # 65001 is the code page for UTF-8
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception as e:
        print(f"Warning: Failed to set console to UTF-8: {e}")

    # Reconfigure stdout and stderr to use UTF-8
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='backslashreplace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='backslashreplace')

# Monkey patch the Python logging StreamHandler to handle UTF-8 properly
original_emit = logging.StreamHandler.emit


def utf8_emit(self, record):
    try:
        msg = self.format(record)
        stream = self.stream

        # Try to write with UTF-8 encoding
        try:
            stream.write(msg + self.terminator)
            self.flush()
        except UnicodeEncodeError:
            # If encoding fails, write directly to the buffer with UTF-8 encoding
            if hasattr(stream, 'buffer'):
                stream.buffer.write((msg + self.terminator).encode('utf-8'))
                self.flush()
            else:
                # Fallback - replace characters that can't be encoded
                stream.write(msg.encode('utf-8', 'replace').decode('utf-8') + self.terminator)
                self.flush()
    except Exception:
        self.handleError(record)


# Replace the original emit method with our UTF-8 aware version
logging.StreamHandler.emit = utf8_emit
# =========================================================

# Now import the custom logging system
from logger import initialize_logging, get_logger

# Initialize logging with desired settings (do this ONCE at program start)
initialize_logging(level="INFO")

# Then get the logger for main
logger = get_logger(__name__)

# Standard imports
from datetime import datetime
from pathlib import Path

# PyQt imports
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer

# App-specific imports
from config import RESOURCE_DIR
from widgets.splash import SplashScreen
from gui import GUI
from widgets.login.login_widget import LoginWidget

# Import the translator function
from translations import get_translator

# Global variables to hold references
login_widget = None
main_gui = None
db_instance = None


def create_db_instance():
    """Create a database instance with proper error handling"""
    try:
        logger.info("Initializing database connection...")
        db = CarPartsDB()
        # Verify the database is accessible
        parts_count = len(db.get_all_parts())
        logger.info(f"Connected to database. Found {parts_count} parts.")
        return db
    except Exception as e:
        error_msg = f"Database connection error: {str(e)}"
        logger.error(error_msg)
        QMessageBox.critical(None, "Database Error", error_msg)
        sys.exit(1)


def cleanup_resources():
    """Properly clean up resources at application exit"""
    logger.info("Cleaning up application resources...")
    try:
        # Close database connections
        if db_instance:
            logger.info("Closing database connection...")
            db_instance.close_connection()

        # Additional cleanup as needed
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")


if __name__ == "__main__":
    # Use current date and time instead of hard-coded value
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Application starting at: {current_time}")
    logger.info(f"Current user: BaselAM")

    QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)
    app = QApplication(sys.argv)

    # Ensure proper cleanup at exit
    app.aboutToQuit.connect(cleanup_resources)

    try:
        # Validate resources
        for fname in ["intro.jpg", "car-icon.jpg", "search_icon.png"]:
            resource_path = RESOURCE_DIR / fname
            if not resource_path.exists():
                raise FileNotFoundError(f"Missing file: {resource_path}")

        # Create resources folder and icons if they don't exist
        resources_dir = RESOURCE_DIR
        if not resources_dir.exists():
            resources_dir.mkdir(exist_ok=True)
            logger.info("Created resources directory")

        # Check for required icon files for ProductsWidget
        required_icons = [
            "add_icon.png", "select_icon.png", "delete_icon.png",
            "filter_icon.png", "export_icon.png", "refresh_icon.png",
            "info_icon.png", "success_icon.png", "error_icon.png",
            "warning_icon.png", "close_icon.png"
        ]

        # Report missing icons but don't fail - the app will still work
        for icon in required_icons:
            if not (resources_dir / icon).exists():
                logger.warning(f"Missing icon file: {icon}")

        # Import database here to avoid circular imports
        from database.car_parts_db import CarPartsDB

        # Initialize database once and share the instance
        db_instance = create_db_instance()

        # Initialize a translator with default language 'en'
        translator = get_translator('en')

        # Show splash screen
        splash = SplashScreen()
        splash.show()

        # Pre-create the main GUI with shared database instance
        main_gui = GUI(car_parts_db=db_instance)
        main_gui.hide()

        # Create the login widget with the translator
        login_widget = LoginWidget(translator=translator)
        login_widget.hide()  # start hidden


        # When login is successful, close the login widget and show the main GUI
        def on_login(username):
            logger.info(f"User logged in: {username}")
            login_widget.close()
            main_gui.set_current_user(username)
            main_gui.show()


        # Suppress linter warning for unresolved attribute reference on the signal
        # noinspection PyUnresolvedReferences
        login_widget.login_successful.connect(on_login)


        # After the splash, show the login widget
        def show_login():
            splash.close()
            login_widget.show()


        QTimer.singleShot(2000, show_login)

        exit_code = app.exec_()
        sys.exit(exit_code)

    except Exception as e:
        logger.critical(f"Fatal error: {str(e)}", exc_info=True)
        QMessageBox.critical(None, "Fatal Error",
                             f"An unrecoverable error occurred: {str(e)}")
        sys.exit(1)