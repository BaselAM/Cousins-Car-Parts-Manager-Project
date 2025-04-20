# ============== Force UTF-8 console encoding ==============
import sys
import io
import logging
import os
from pathlib import Path


# Get absolute path to resources, works for dev and for PyInstaller
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        # Running as executable
        base_path = sys._MEIPASS
    else:
        # Running in development
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


# Force Windows console to use UTF-8
if sys.platform == 'win32':
    import ctypes

    # Try to set console code page to UTF-8
    try:
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)  # 65001 is the code page for UTF-8
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception as e:
        print(f"Warning: Failed to set console to UTF-8: {e}")

    # Reconfigure stdout and stderr to use UTF-8 (only if they exist)
    if hasattr(sys, 'stdout') and sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='backslashreplace')
    if hasattr(sys, 'stderr') and sys.stderr is not None and hasattr(sys.stderr, 'buffer'):
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

# PyQt imports
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QTranslator
from PyQt5.QtGui import QFontDatabase, QFont

# Define resource and translation directories
RESOURCE_DIR = Path(get_resource_path('resources'))
TRANSLATIONS_DIR = Path(get_resource_path('translations'))
TRANSLATIONS_DATA_DIR = TRANSLATIONS_DIR / 'data'

logger.info(f"Resource directory: {RESOURCE_DIR}")
logger.info(f"Translations directory: {TRANSLATIONS_DIR}")
logger.info(f"Translations data directory: {TRANSLATIONS_DATA_DIR}")

# Ensure translations data directory exists (for development mode)
TRANSLATIONS_DATA_DIR.mkdir(exist_ok=True, parents=True)

# Make sure translation system imports use the right paths
# Import the translator function - do this after setting up paths
import translations
from translations.translator import load_translations_from_directory, load_translation_file

# Check if we need to load translations from packaged path
logger.info("Checking for translation files...")
if TRANSLATIONS_DATA_DIR.exists():
    logger.info(f"Found translations data directory: {TRANSLATIONS_DATA_DIR}")
    count = load_translations_from_directory(str(TRANSLATIONS_DATA_DIR))
    logger.info(f"Loaded {count} translation files from data directory")
else:
    logger.warning(f"Translations data directory not found: {TRANSLATIONS_DATA_DIR}")

# App-specific imports
from widgets.splash import SplashScreen
from gui import GUI
from widgets.login.login_widget import LoginWidget

# Global variables to hold references
login_widget = None
main_gui = None
db_instance = None


def load_emoji_fonts():
    """Load and set emoji-compatible fonts"""
    logger.info("Loading emoji fonts...")

    # Register system fonts that support emoji
    system_fonts = ["Segoe UI Emoji", "Noto Color Emoji", "Apple Color Emoji"]

    # Try to find and use an emoji-compatible font
    font = QFont()
    font.setFamily("Segoe UI")  # Base font

    # Try to load custom fonts from resources if available
    emoji_font_dir = RESOURCE_DIR / "fonts"
    if emoji_font_dir.exists():
        for font_file in emoji_font_dir.glob("*.ttf"):
            font_id = QFontDatabase.addApplicationFont(str(font_file))
            if font_id != -1:
                font_families = QFontDatabase.applicationFontFamilies(font_id)
                if font_families:
                    logger.info(f"Loaded font: {font_families[0]}")
                    system_fonts.insert(0, font_families[0])  # Prioritize our bundled font

    # Set font fallbacks for emoji support
    font.setFamilies(system_fonts)
    return font


def create_db_instance():
    """Create a database instance with proper error handling"""
    try:
        logger.info("Initializing database connection...")
        # Import here to avoid circular imports
        from database.car_parts_db import CarPartsDB
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

        # Proper cleanup for parts navigation
        if hasattr(main_gui, 'view_manager') and \
                hasattr(main_gui.view_manager, 'parts_navigation_widget') and \
                main_gui.view_manager.parts_navigation_widget:
            parts_nav = main_gui.view_manager.parts_navigation_widget
            if hasattr(parts_nav, 'cleanup_resources'):
                logger.info("Cleaning up parts navigation resources...")
                parts_nav.cleanup_resources()

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

    # Set emoji font for the entire application
    emoji_font = load_emoji_fonts()
    app.setFont(emoji_font)

    # Ensure proper cleanup at exit
    app.aboutToQuit.connect(cleanup_resources)

    try:
        # Validate resources
        for fname in ["intro.jpg", "car-icon.jpg", "search_icon.png"]:
            resource_path = RESOURCE_DIR / fname
            if not resource_path.exists():
                logger.warning(f"Missing file: {resource_path}")
                # Don't raise exception - we'll continue without these files

        # Create resources folder and icons if they don't exist
        if not RESOURCE_DIR.exists():
            RESOURCE_DIR.mkdir(exist_ok=True)
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
            if not (RESOURCE_DIR / icon).exists():
                logger.warning(f"Missing icon file: {icon}")

        # Initialize database once and share the instance
        db_instance = create_db_instance()

        # Get the translator and set the language
        translator = translations.get_translator('en')
        logger.info(f"Initialized translator with language: {translator.language}")

        # Create a Qt translator for system elements
        qt_translator = QTranslator()
        if translator.language == 'he':
            # Try to load Hebrew Qt translations if they exist
            qt_translation_file = TRANSLATIONS_DIR / "qtbase_he.qm"
            if qt_translation_file.exists():
                qt_translator.load(str(qt_translation_file))
                app.installTranslator(qt_translator)
                logger.info(f"Installed Qt system translator for Hebrew")

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