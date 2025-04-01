from PyQt5.QtCore import QThread, pyqtSignal
import mysql.connector  # Add this import


class DatabaseWorker(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, db, operation, **kwargs):
        super().__init__()
        self.db = db
        self.operation = operation
        self.kwargs = kwargs

    def run(self):
        """Run the worker thread"""
        try:
            # Ensure we have a connection for this thread
            self.db.ensure_connection()

            if self.operation == "load":
                # Get all products
                products = self.db.get_all_parts()
                self.finished.emit(products)
            # Add other operations as needed

        except Exception as e:
            # Log the error
            print(f"MySQL error in worker thread: {str(e)}")
            import traceback
            error_details = traceback.format_exc()
            print(f"Worker thread error details: {error_details}")
            self.error.emit(f"Database error: {str(e)}")
        finally:
            # Always clean up the connection when done
            try:
                if hasattr(self.db, 'close_connection'):
                    self.db.close_connection()
            except:
                pass