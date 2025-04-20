"""
Translation module with backward compatibility.
"""
from logger import get_logger

import json
from pathlib import Path
import threading

# Configure logging - simplified with custom logger
logger = get_logger('translations')

# Import directly from the translator module
from .translator import Translator, load_translation_file, load_translations_from_directory

# Global initialization lock and flags
_init_lock = threading.Lock()
_translations_loaded = False
_default_translator = None

def get_translator(language='en'):
    """
    Get the singleton translator instance.
    """
    global _default_translator, _translations_loaded

    # Initialize if needed (thread-safe)
    if not _translations_loaded:
        with _init_lock:
            if not _translations_loaded:
                # Create translator
                _default_translator = Translator(language)

                # Load translations only once
                data_dir = Path(__file__).parent / 'data'
                if data_dir.exists():
                    logger.info(f"Loading translation files from {data_dir}")
                    count = load_translations_from_directory(str(data_dir))
                    logger.info(f"Loaded {count} translation files")

                # Mark as loaded
                _translations_loaded = True

    # Update language if needed
    if _default_translator and _default_translator.language != language:
        _default_translator.set_language(language)

    return _default_translator

# Export the necessary functions
__all__ = ['Translator', 'load_translation_file', 'load_translations_from_directory', 'get_translator']