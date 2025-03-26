"""
Enhanced translator with backward compatibility and file-based translation support.
"""
import os
import json
import logging
from functools import lru_cache
from typing import Dict, Optional, List, cast

# Configure logger
logger = logging.getLogger('translations')

# Import original translations or create empty dict if not available
try:
    # Try to import from original location first (for backwards compatibility)
    from translator import TRANSLATIONS as ORIGINAL_TRANSLATIONS
except ImportError:
    try:
        # Then try from our new location
        from .core_data import TRANSLATIONS as ORIGINAL_TRANSLATIONS
    except ImportError:
        logger.warning("Could not import TRANSLATIONS dictionary - using empty dictionary")
        ORIGINAL_TRANSLATIONS = {}

# Define a type alias for translation dictionaries.
# Each key maps to a dict of language code (str) to translation (str).
TranslationDict = Dict[str, Dict[str, str]]


class TranslationProvider:
    """Manages translation data from multiple sources."""

    def __init__(self):
        # Core translations should follow the TranslationDict structure.
        self._core_translations: TranslationDict = cast(TranslationDict, ORIGINAL_TRANSLATIONS)
        self._file_translations: Dict[str, TranslationDict] = {}  # File-based translations have higher priority
        self._namespaces: Dict[str, str] = {}  # Track which file each namespace came from

    def load_translation_file(self, file_path: str, namespace: Optional[str] = None) -> bool:
        """Load translations from a JSON file into a specific namespace."""
        if namespace is None:
            # Explicitly annotate parts as List[str]
            parts: List[str] = os.path.basename(file_path).split('.')
            namespace = parts[0] if parts else "" # type: ignore
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Assume JSON file is structured as a TranslationDict.
                    translations = json.load(f)
                    self._file_translations[namespace] = cast(TranslationDict, translations)
                    self._namespaces[namespace] = file_path
                    logger.info(f"Loaded translations for namespace '{namespace}' from {file_path}")
                    return True
            else:
                logger.warning(f"Translation file not found: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to load translations from {file_path}: {e}")
            return False

    def get_translation(self, key: str, language: str, namespace: Optional[str] = None) -> Optional[str]:
        """Get translation from either file-based or core translations."""
        # Try namespace-specific translations first if specified.
        if namespace is not None and namespace in self._file_translations:
            translations: TranslationDict = self._file_translations[namespace]
            trans_dict: Dict[str, str] = translations.get(key, {})
            if language in trans_dict:
                return trans_dict[language]

        # If no namespace is provided, search through all file-based translations.
        if namespace is None:
            for ns, translations in self._file_translations.items():
                trans_dict: Dict[str, str] = translations.get(key, {})
                if language in trans_dict:
                    return trans_dict[language]

        # Finally, fall back to core translations.
        trans_dict: Dict[str, str] = self._core_translations.get(key, {})
        if language in trans_dict:
            return trans_dict[language]

        return None

    @staticmethod
    def get_available_namespaces(self) -> list:
        """Get list of all available translation namespaces."""
        return list(self._file_translations.keys())


# Global provider instance
_provider = TranslationProvider()


class Translator:
    """
    Enhanced translator with backward compatibility.
    Maintains the same interface as the original Translator while adding new capabilities.
    """

    def __init__(self, language: str = 'en'):
        self.language = language
        self.fallback_language = 'en'

    def set_language(self, language: str):
        """Change the current language."""
        self.language = language
        # Clear cache when language changes.
        if hasattr(self, '_t_cached'):
            self._t_cached.cache_clear()

    @property
    @lru_cache(maxsize=1)
    def _t_cached(self):
        """Create a cached translation function."""
        @lru_cache(maxsize=1024)
        def _cached_translate(key: str, **kwargs) -> str:
            return self._translate(key, **kwargs)
        return _cached_translate

    def _translate(self, key: str, **kwargs) -> str:
        """Internal translation function with placeholder support."""
        # Parse namespace if present (format: "namespace:key")
        namespace = None
        lookup_key = key

        if ':' in key:
            parts = key.split(':', 1) # type: ignore
            if len(parts) == 2:
                namespace, lookup_key = parts

        # Get translation.
        translation = _provider.get_translation(lookup_key, self.language, namespace)

        # Fall back to default language if needed.
        if translation is None and self.language != self.fallback_language:
            translation = _provider.get_translation(lookup_key, self.fallback_language, namespace)

        # Use key as fallback.
        if translation is None:
            if namespace:
                logger.warning(f"Missing translation for '{namespace}:{lookup_key}' in '{self.language}'")
            else:
                logger.warning(f"Missing translation for '{key}' in '{self.language}'")
            return lookup_key

        # Apply placeholders if any.
        if kwargs and '{' in translation:
            try:
                return translation.format(**kwargs)
            except KeyError as e:
                logger.error(f"Invalid placeholder in translation for '{key}': {e}")
                return translation

        return translation

    def t(self, key: str, **kwargs) -> str:
        """
        Get translation for a key with placeholder replacement.
        Maintains the same interface as the original t() method.
        """
        return self._t_cached(key, **kwargs)

    def has_translation(self, key: str, language: Optional[str] = None) -> bool:
        """Check if a translation exists for a key."""
        lang = language or self.language
        namespace = None

        if ':' in key:
            parts = key.split(':', 1) # type: ignore
            if len(parts) == 2:
                namespace, key = parts

        return _provider.get_translation(key, lang, namespace) is not None

    @staticmethod
    def get_namespaces() -> list:
        """Get all available translation namespaces."""
        return _provider.get_available_namespaces(_provider)


def load_translation_file(file_path: str, namespace: Optional[str] = None) -> bool:
    """
    Load a translation file.

    Example:
        load_translation_file('translations/data/products.json', 'products')
    """
    return _provider.load_translation_file(file_path, namespace)
