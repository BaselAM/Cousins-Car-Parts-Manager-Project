"""
Translation module with backward compatibility.
"""
import logging
import json
from pathlib import Path

# Configure logging
logger = logging.getLogger('translations')
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Import the original Translator for backward compatibility
try:
    from translator import Translator as OriginalTranslator, TRANSLATIONS
except ImportError:
    logger.warning("Could not import original Translator - creating empty version")

    # Create a minimal version if it can't be imported
    TRANSLATIONS = {}


    class OriginalTranslator:
        def __init__(self, language='en'):
            self.language = language

        def t(self, key):
            return key

        def set_language(self, language):
            self.language = language


class EnhancedTranslator(OriginalTranslator):
    """
    Enhanced translator that extends the original with file-based translations.
    """

    def __init__(self, language='en'):
        super().__init__(language)
        self._file_translations = {}
        self._load_translation_files()

    def _load_translation_files(self):
        """Load all translation files from data directory."""
        data_dir = Path(__file__).parent / 'data'
        if data_dir.exists():
            logger.info(f"Loading translation files from {data_dir}")
            for file_path in data_dir.glob('*.json'):
                namespace = file_path.stem
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        self._file_translations[namespace] = json.load(f)
                    logger.info(f"Loaded translations for '{namespace}' from {file_path}")
                except Exception as e:
                    logger.error(f"Failed to load translations from {file_path}: {e}")

    def t(self, key, **kwargs):
        """Enhanced translation with namespace support and JSON fallback."""
        namespace = None
        lookup_key = key

        # Handle namespace:key format
        if ':' in key:
            parts = key.split(':', 1)# type: ignore
            namespace = parts[0]# type: ignore
            lookup_key = parts[1]# type: ignore

            # Try namespace-specific translations
            if namespace in self._file_translations:
                if lookup_key in self._file_translations[namespace]:
                    translations = self._file_translations[namespace][lookup_key]
                    if self.language in translations:
                        result = translations[self.language]
                        # Apply placeholders if any
                        if kwargs and '{' in result:
                            try:
                                return result.format(**kwargs)
                            except KeyError:
                                return result
                        return result

        # Try all JSON translations (without namespace)
        for ns, translations in self._file_translations.items():
            if lookup_key in translations:
                if self.language in translations[lookup_key]:
                    result = translations[lookup_key][self.language]
                    # Apply placeholders if any
                    if kwargs and '{' in result:
                        try:
                            return result.format(**kwargs)
                        except KeyError:
                            return result
                    return result

        # Fall back to original translator
        return super().t(key)


# Create a default instance for importing
default_translator = EnhancedTranslator()

# Export the necessary classes
__all__ = ['EnhancedTranslator', 'default_translator']