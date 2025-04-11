from PyQt5.QtWidgets import QPushButton, QSizePolicy, QInputDialog
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QIcon
import os


class CompatibleBarcodeButton(QPushButton):
    """A QPushButton-based barcode scanner button compatible with standard layouts"""
    barcode_scanned = pyqtSignal(str, str)

    def __init__(self, parent=None, translator=None):
        super().__init__(parent)
        self.translator = translator
        self.setObjectName("barcodeButton")
        self.setToolTip(self._translate("barcode:scan_barcode", "Scan Barcode"))

        # Match other buttons' appearance
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Try to load icon
        try:
            icon_paths = ["resources/barcode.png", "resources/icons/barcode.png", "../resources/barcode.png"]
            icon_loaded = False

            for path in icon_paths:
                if os.path.exists(path):
                    self.setIcon(QIcon(path))
                    icon_loaded = True
                    break

            if not icon_loaded:
                self.setText("🔍")
        except Exception as e:
            print(f"Icon loading error: {e}")
            self.setText("🔍")

        # Connect to show dialog
        self.clicked.connect(self._show_scan_dialog)

    def _translate(self, key, default):
        """Get translated text with fallback"""
        if self.translator and hasattr(self.translator, 't'):
            try:
                return self.translator.t(key)
            except:
                pass
        return default

    def _show_scan_dialog(self):
        """Show the scanning dialog"""
        try:
            # Import the original ScanningDialog
            from widgets.products.components.barcode_scanner_button import ScanningDialog
            dialog = ScanningDialog(self.parent(), self.translator)
            dialog.barcode_scanned.connect(lambda barcode: self.barcode_scanned.emit(barcode, "Scanned"))
            dialog.exec_()
        except Exception as e:
            print(f"Error showing scan dialog: {e}")
            # Fallback - simple text input
            barcode, ok = QInputDialog.getText(
                self.parent(),
                self._translate("barcode:enter_barcode", "Enter Barcode"),
                self._translate("barcode:enter_barcode_prompt", "Enter barcode:"),
            )
            if ok and barcode:
                self.barcode_scanned.emit(barcode, "Manual")