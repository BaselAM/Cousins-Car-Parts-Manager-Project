"""
Bartender label integration module for finding, previewing and printing
label files directly from the application.
"""
import os
import subprocess
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QMessageBox, QInputDialog, QFileDialog, QDialog, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton, QSpinBox
)
from logger import get_logger

logger = get_logger(__name__)


class BartenderManager(QObject):
    """Manager class for Bartender integration"""

    printing_complete = pyqtSignal(bool, str)  # Success, message

    def __init__(self, settings_db=None, translator=None):
        super().__init__()
        self.settings_db = settings_db
        self.translator = translator
        self.bartender_path = None
        self.labels_folder = None
        self.load_settings()

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def load_settings(self):
        """Load Bartender settings from the database"""
        if self.settings_db:
            self.labels_folder = self.settings_db.get_setting('bartender_labels_folder', '')
            self.bartender_path = self.settings_db.get_setting('bartender_executable', '')

    def save_settings(self, labels_folder, bartender_path=None):
        """Save Bartender settings to the database"""
        if self.settings_db:
            self.settings_db.save_setting('bartender_labels_folder', labels_folder)
            self.labels_folder = labels_folder

            if bartender_path:
                self.settings_db.save_setting('bartender_executable', bartender_path)
                self.bartender_path = bartender_path

    def find_label_file(self, product_name):
        """Find a label file that matches the product name"""
        if not self.labels_folder or not os.path.exists(self.labels_folder):
            return None

        # Normalize product name for file matching
        normalized_name = product_name.lower().replace(' ', '_')

        # List of possible extensions for Bartender files
        btw_extensions = ['.btw', '.BTW', '.btw.xml']

        # Look for exact match with various extensions
        for ext in btw_extensions:
            exact_match = os.path.join(self.labels_folder, f"{normalized_name}{ext}")
            if os.path.exists(exact_match):
                return exact_match

        # If no exact match, look for files containing the product name
        for filename in os.listdir(self.labels_folder):
            file_base = os.path.splitext(filename)[0].lower()
            if normalized_name in file_base:
                return os.path.join(self.labels_folder, filename)

        # No matching file found
        return None

    def preview_label(self, product_name):
        """Preview a label in Bartender"""
        label_file = self.find_label_file(product_name)

        if not label_file:
            QMessageBox.warning(
                None,
                self._translate("error", "Error"),
                self._translate("no_label_found", f"No label file found for {product_name}"),
                buttons=QMessageBox.Ok
            )
            return False

        if not self.bartender_path or not os.path.exists(self.bartender_path):
            QMessageBox.warning(
                None,
                self._translate("error", "Error"),
                self._translate("bartender_not_configured", "Bartender executable path not configured in settings"),
                buttons=QMessageBox.Ok
            )
            return False

        try:
            # Launch Bartender with the file
            subprocess.Popen([self.bartender_path, label_file])
            return True
        except Exception as e:
            logger.error(f"Error previewing label: {str(e)}")
            QMessageBox.critical(
                None,
                self._translate("error", "Error"),
                self._translate("preview_error", f"Error previewing label: {str(e)}"),
                buttons=QMessageBox.Ok
            )
            return False

    def print_label(self, product_name, quantity=1):
        """Print a label directly"""
        label_file = self.find_label_file(product_name)

        if not label_file:
            error_msg = self._translate("no_label_found", f"No label file found for {product_name}")
            self.printing_complete.emit(False, error_msg)
            return False

        if not self.bartender_path or not os.path.exists(self.bartender_path):
            error_msg = self._translate("bartender_not_configured",
                                        "Bartender executable path not configured in settings")
            self.printing_complete.emit(False, error_msg)
            return False

        try:
            # Use Bartender command line to print
            # Note: Actual command line parameters may vary based on Bartender version
            cmd = [
                self.bartender_path,
                "/P",  # Print command
                f"/C={quantity}",  # Number of copies
                label_file
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0:
                logger.error(f"Printing error: {stderr}")
                self.printing_complete.emit(
                    False,
                    self._translate("print_error", f"Error printing label: {stderr}")
                )
                return False

            self.printing_complete.emit(
                True,
                self._translate("print_success", f"Successfully printed {quantity} labels")
            )
            return True

        except Exception as e:
            logger.error(f"Error printing label: {str(e)}")
            self.printing_complete.emit(
                False,
                self._translate("print_error", f"Error printing label: {str(e)}")
            )
            return False

    def select_labels_folder(self):
        """Open dialog to select the labels folder"""
        folder = QFileDialog.getExistingDirectory(
            None,
            self._translate("select_labels_folder", "Select Labels Folder"),
            self.labels_folder or os.path.expanduser("~")
        )

        if folder:
            self.save_settings(folder)
            return folder
        return None

    def select_bartender_executable(self):
        """Open dialog to select the Bartender executable"""
        file_filter = "Executable files (*.exe);;All files (*.*)"

        file_path, _ = QFileDialog.getOpenFileName(
            None,
            self._translate("select_bartender_exe", "Select Bartender Executable"),
            self.bartender_path or os.path.expanduser("~"),
            file_filter
        )

        if file_path:
            self.save_settings(self.labels_folder, file_path)
            return file_path
        return None


class PrintDialog(QDialog):
    """Dialog for setting print options"""

    def __init__(self, product_name, translator=None, parent=None):
        super().__init__(parent)
        self.product_name = product_name
        self.translator = translator
        self.setup_ui()

    def _translate(self, key, default):
        """Get translated text with fallback."""
        if self.translator and hasattr(self.translator, 't'):
            return self.translator.t(key)
        return default

    def setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle(self._translate("print_label", f"Print Label: {self.product_name}"))
        self.setMinimumWidth(350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)

        # Information label
        info_label = QLabel(self._translate("print_copies", "Select number of copies to print:"))
        layout.addWidget(info_label)

        # Quantity selector
        quantity_layout = QHBoxLayout()
        quantity_layout.addWidget(QLabel(self._translate("copies", "Copies:")))

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(999)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setFixedHeight(30)
        quantity_layout.addWidget(self.quantity_spin)
        layout.addLayout(quantity_layout)

        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_btn = QPushButton(self._translate("cancel", "Cancel"))
        self.print_btn = QPushButton(self._translate("print", "Print"))
        self.print_btn.setDefault(True)

        self.cancel_btn.clicked.connect(self.reject)
        self.print_btn.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.print_btn)

        layout.addLayout(button_layout)

    def get_quantity(self):
        """Get the selected quantity"""
        return self.quantity_spin.value()