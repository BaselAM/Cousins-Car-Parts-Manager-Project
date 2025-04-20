"""
Barcode scanner adapter for the Smart Search Widget.
"""

from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel

# Try to import theme and logger modules - handle gracefully if not available
try:
    from logger import get_logger
    logger = get_logger('widgets.smart_search_widget.components.barcode_adapter')
except ImportError:
    # Simple fallback logger if the standard logger is unavailable
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('widgets.smart_search_widget.components.barcode_adapter')

# Try to import barcode scanner dialog
try:
    from widgets.products.components.barcode_scanner_button import ScanningDialog
except ImportError:
    # Simple fallback if the ScanningDialog is unavailable
    class ScanningDialog(QDialog):
        """Fallback scanning dialog if the standard one is unavailable."""
        barcode_scanned = pyqtSignal(str)

        def __init__(self, parent=None, translator=None):
            super().__init__(parent)
            self.translator = translator
            self.setWindowTitle("Scan Barcode")
            self.setFixedSize(300, 200)

            layout = QVBoxLayout(self)
            label = QLabel("Barcode scanner not available", self)
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)


class BarcodeDialogAdapter:
    """Adapter to bridge translation systems between our app and the barcode scanner dialog."""

    @staticmethod
    def create_dialog(parent, translator):
        """
        Create a barcode scanning dialog with proper translator handling.

        Args:
            parent: Parent widget for the dialog
            translator: Translation object for localization

        Returns:
            QDialog: Configured dialog instance
        """
        try:
            # Create a translator adapter that handles the expected _translate method's usage
            class TranslatorAdapter:
                def __init__(self, real_translator):
                    self.real_translator = real_translator

                def t(self, key):
                    """Single-argument t method that will work with the ScanningDialog"""
                    # In barcode scanner dialog, keys are in format "barcode:key"
                    # If key doesn't contain ":", add the "barcode:" prefix
                    if ":" not in key:
                        key = f"barcode:{key}"
                    return self.real_translator.t(key)

            # Create adapter with original translator
            adapted_translator = TranslatorAdapter(translator)

            # Create dialog with adapted translator
            dialog = ScanningDialog(parent, adapted_translator)
            return dialog
        except Exception as e:
            logger.error(f"Error creating barcode dialog: {e}")
            # Fall back to a simple dialog
            dialog = QDialog(parent)
            dialog.setWindowTitle(translator.t('scan_barcode_tooltip'))
            dialog.setFixedSize(300, 200)

            layout = QVBoxLayout(dialog)
            label = QLabel(translator.t('barcode_scanner_not_available',
                                      "Barcode scanner not available"), dialog)
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)

            return dialog