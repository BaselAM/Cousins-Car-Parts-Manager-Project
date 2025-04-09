"""
Standalone test script to verify BarcodeScannerButton works outside your application context.
Updated version that doesn't require the test_import function.
"""
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import Qt

# This will help diagnose import issues
print(f"Python version: {sys.version}")
print(f"sys.path: {sys.path}")

try:
    # Try to import using your project's structure
    print("Attempting to import BarcodeScannerButton...")
    from widgets.products.components.barcode_scanner_button import BarcodeScannerButton
    print("BarcodeScannerButton imported successfully!")
except ImportError as e:
    print(f"Import error: {e}")
    print("Failed to import the BarcodeScannerButton class")
    sys.exit(1)

# Create a simple translator mock to replicate your app's translator
class TranslatorMock:
    def t(self, key):
        translations = {
            'scan_barcode_tooltip': 'Scan Barcode',
            'scan_barcode': 'Scan Barcode',
            'enter_barcode': 'Enter a barcode:',
        }
        return translations.get(key, key)

    def has_translation(self, key):
        translations = {
            'scan_barcode_tooltip': True,
            'scan_barcode': True,
            'enter_barcode': True,
        }
        return translations.get(key, False)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Barcode Scanner Button Test")
        self.setGeometry(100, 100, 400, 200)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)

        # Add instructions
        instructions = QLabel("Click the barcode button below:")
        instructions.setAlignment(Qt.AlignCenter)
        layout.addWidget(instructions)

        # Create a translator mock
        self.translator = TranslatorMock()

        # Create the barcode scanner button
        try:
            print("Creating BarcodeScannerButton...")
            self.barcode_button = BarcodeScannerButton(self, self.translator)

            # Try connecting to the signal, handling both possible signal types
            try:
                self.barcode_button.barcode_scanned.connect(self.on_barcode_scanned)
                print("Connected to barcode_scanned signal successfully")
            except TypeError as e:
                print(f"Signal connection error: {e}")
                print("Trying alternate signal signature...")
                # Try a different signal signature if the first fails
                try:
                    self.barcode_button.barcode_scanned[str, str].connect(self.on_barcode_scanned_str_str)
                    print("Connected to barcode_scanned[str, str] signal")
                except Exception as e2:
                    print(f"Second signal connection attempt failed: {e2}")

            layout.addWidget(self.barcode_button)
            print("BarcodeScannerButton added to layout successfully")
        except Exception as e:
            print(f"Error creating button: {e}")
            import traceback
            print(traceback.format_exc())
            error_label = QLabel(f"Error: {str(e)}")
            layout.addWidget(error_label)

        # Add a result label
        self.result_label = QLabel("No barcode scanned yet")
        self.result_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.result_label)

    def on_barcode_scanned(self, result):
        """Handle barcode scanned signal with flexible parameter types"""
        print(f"Barcode received: {result}")

        # Handle different possible result types
        if isinstance(result, dict):
            barcode = result.get('barcode', 'Unknown')
            format_type = result.get('format', 'Unknown')
        elif isinstance(result, tuple) and len(result) >= 2:
            barcode, format_type = result[0], result[1]
        else:
            # Assume it's a string or some other type
            barcode = str(result)
            format_type = "Unknown"

        self.result_label.setText(f"Scanned: {barcode} ({format_type})")

    def on_barcode_scanned_str_str(self, barcode, format_type):
        """Alternative handler for str,str signal signature"""
        print(f"Barcode received via str,str signal: {barcode}, {format_type}")
        self.result_label.setText(f"Scanned: {barcode} ({format_type})")

if __name__ == "__main__":
    # Enable exception hooks to catch any unhandled exceptions
    def exception_hook(exctype, value, traceback):
        print(f"Unhandled exception: {exctype}, {value}")
        import traceback as tb
        tb.print_exception(exctype, value, traceback)
        sys.exit(1)

    sys.excepthook = exception_hook

    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())