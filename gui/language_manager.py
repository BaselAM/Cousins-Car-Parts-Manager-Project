# gui/language_manager.py
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMessageBox
from translations import get_translator
from logger import get_logger

logger = get_logger(__name__)


class GUILanguageManager:
    """
    Manages language and translation changes.
    Handles updating UI components when language changes.
    """

    def __init__(self, parent, translator, settings_db):
        """
        Initialize the language manager.

        Args:
            parent: The main GUI instance
            translator: Current translator object
            settings_db: Database connection for settings
        """
        self.parent = parent
        self.translator = translator
        self.settings_db = settings_db

    def update_language(self, new_lang):
        """
        Change the application language.

        Args:
            new_lang: The new language code to switch to
        """
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)

            # Save settings
            is_rtl = (new_lang == 'he')
            self.settings_db.save_setting('rtl', str(is_rtl).lower())
            self.settings_db.save_setting('language', new_lang)

            # Update parent state
            self.parent.current_language = new_lang
            self.parent.rtl_enabled = is_rtl

            # Get the updated shared translator
            self.translator = get_translator(new_lang)
            self.parent.translator = self.translator

            # Apply direction changes through layout manager
            if hasattr(self.parent, 'layout_manager'):
                self.parent.layout_manager.update_layout_direction(is_rtl)

            # Refresh theme and translations
            if hasattr(self.parent, 'theme_manager'):
                self.parent.theme_manager.apply_theme()

            self._full_ui_refresh()

        except Exception as e:
            logger.error(f"Language update error: {str(e)}")
            QMessageBox.critical(self.parent, self.translator.t("error"),
                                 self.translator.t('settings_save_error'))
        finally:
            QApplication.restoreOverrideCursor()

    def _full_ui_refresh(self):
        """Refresh all UI components after language change"""
        # Use UI builder to update components if available
        if hasattr(self.parent, 'ui_builder') and self.parent.ui_builder:
            self.parent.ui_builder.update_all_components()
        else:
            # Fallback manual refresh of all components
            self._update_components_manually()

        # Force layout update
        self.parent.updateGeometry()
        QApplication.processEvents()

    def _update_components_manually(self):
        """Update all components manually if UI builder is not available"""
        # Update main components if they exist
        if hasattr(self.parent, 'header'):
            self.parent.header.update_translations()

        if hasattr(self.parent, 'top_bar'):
            self.parent.top_bar.update_translations()

        if hasattr(self.parent, 'footer'):
            self.parent.footer.update_translations()

        # Update views through view manager
        if hasattr(self.parent, 'view_manager'):
            self.parent.view_manager.update_translations()