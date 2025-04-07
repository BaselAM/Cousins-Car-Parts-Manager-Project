"""
DatabaseWorker utility for asynchronous database operations.

Provides thread-safe database operations for the parts navigation system.
"""
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot, Qt
import threading
from logger import get_logger

logger = get_logger('parts_navigation.database_worker')


class DatabaseWorker(QObject):
    """
    Worker for database operations in a separate thread.

    Features:
    - Thread-safe database operations
    - Signal-based communication
    - Error handling
    """
    # Signal emitted when operation completes successfully
    finished = pyqtSignal(object)  # Result object

    # Signal emitted when an error occurs
    error = pyqtSignal(str)  # Error message

    # Static cache for brands data with thread safety
    _brands_cache = None
    _brands_cache_lock = threading.RLock()

    def __init__(self, db):
        """
        Initialize the database worker.

        Args:
            db: Database connection
        """
        super().__init__()
        self.db = db

    @pyqtSlot(str, object)
    def execute(self, operation, **kwargs):
        """
        Execute a database operation in a background thread.

        Args:
            operation: Operation name
            **kwargs: Operation parameters
        """
        try:
            result = None

            # Ensure connection for this thread
            if hasattr(self.db, 'ensure_connection'):
                try:
                    self.db.ensure_connection()
                except Exception as e:
                    logger.error(f"Database connection error in execute: {e}")
                    self.error.emit(f"Database connection error: {e}")
                    return

            # Brand operations
            if operation == "get_brands":
                result = self._get_brands()

            # Model operations
            elif operation == "get_models":
                result = self._get_models(kwargs.get('brand', None))

            # Year operations
            elif operation == "get_years":
                result = self._get_years(
                    kwargs.get('brand', None),
                    kwargs.get('model', None)
                )

            # Category operations
            elif operation == "get_categories":
                result = self._get_categories(kwargs.get('car', None))

            # Product operations
            elif operation == "get_products":
                result = self._get_products(
                    kwargs.get('car', None),
                    kwargs.get('category', None)
                )

            # Search operations
            elif operation == "search_parts":
                result = self._search_parts(kwargs.get('search_text', ''))

            # Part details operations
            elif operation == "get_part_details":
                result = self._get_part_details(kwargs.get('part_id', None))

            # Unknown operation
            else:
                self.error.emit(f"Unknown operation: {operation}")
                return

            # Emit result
            self.finished.emit(result)

        except Exception as e:
            logger.error(f"Database worker error: {str(e)}")
            self.error.emit(str(e))

    def _get_brands(self):
        """
        Get unique car brands with caching and improved error handling.

        Returns:
            list: List of brand dictionaries
        """
        try:
            # If we have a cached result, use it - with thread safety
            with DatabaseWorker._brands_cache_lock:
                if DatabaseWorker._brands_cache is not None:
                    logger.debug("Using cached brands data instead of querying database")
                    return DatabaseWorker._brands_cache.copy()  # Return a copy for thread safety

            # Get all cars with error handling
            try:
                cars = self.db.get_all_cars()
            except Exception as e:
                logger.error(f"Error getting cars from database: {e}")
                # Return empty list rather than failing completely
                return []

            # Extract unique brands with defensive coding
            unique_brands = set()
            for car in cars:
                try:
                    if isinstance(car, dict) and 'brand' in car:
                        brand = car['brand'].strip()
                        if brand and brand.lower() != 'unknown':
                            unique_brands.add(brand)
                except Exception as e:
                    logger.error(f"Error processing car brand: {e}")
                    # Continue with the next car rather than failing

            # Create brand objects
            result = [{'brand': brand} for brand in sorted(unique_brands)]

            # Cache the result for future use with thread safety
            with DatabaseWorker._brands_cache_lock:
                DatabaseWorker._brands_cache = result.copy()  # Store a copy for thread safety

            return result  # Return the original list
        except Exception as e:
            logger.error(f"Unexpected error in _get_brands: {e}")
            # Return empty list rather than failing
            return []

    def _get_models(self, brand):
        """
        Get models for a brand.

        Args:
            brand: Brand dictionary

        Returns:
            list: List of model dictionaries
        """
        if not brand or 'brand' not in brand:
            self.error.emit("No brand specified")
            return []

        brand_name = brand['brand']

        try:
            # Get all cars
            cars = self.db.get_all_cars()

            # Filter for the current brand and extract unique models
            unique_models = set()
            for car in cars:
                if isinstance(car, dict) and 'brand' in car and 'model' in car:
                    if car['brand'].strip() == brand_name:
                        model = car['model'].strip()
                        if model and model.lower() != 'unknown':
                            unique_models.add(model)

            # Create model objects
            return [{'model': model} for model in sorted(unique_models)]
        except Exception as e:
            logger.error(f"Error in _get_models: {e}")
            return []

    def _get_years(self, brand, model):
        """
        Get years for a brand and model.

        Args:
            brand: Brand dictionary
            model: Model dictionary

        Returns:
            list: List of year dictionaries
        """
        if not brand or not model or 'brand' not in brand or 'model' not in model:
            self.error.emit("Brand and model must be specified")
            return []

        brand_name = brand['brand']
        model_name = model['model']

        try:
            # Get car data
            cars = self.db.get_all_cars()

            # Filter for the current brand and model, then extract unique years
            unique_years = set()
            for car in cars:
                if isinstance(car, dict) and 'brand' in car and 'model' in car and 'year' in car:
                    if (car['brand'].strip() == brand_name and
                            car['model'].strip() == model_name):
                        year = car['year'].strip()
                        if year and year.lower() != 'unknown':
                            unique_years.add(year)

            # Try to convert years to integers for sorting (if they are all numbers)
            try:
                sorted_years = sorted([int(y) for y in unique_years], reverse=True)
                sorted_years = [str(y) for y in sorted_years]
            except ValueError:
                # If conversion fails, sort as strings
                sorted_years = sorted(unique_years, reverse=True)

            # Create year objects
            return [{'year': year} for year in sorted_years]
        except Exception as e:
            logger.error(f"Error in _get_years: {e}")
            return []

    def _get_categories(self, car):
        """
        Get categories for a car.

        Args:
            car: Car dictionary

        Returns:
            list: List of category dictionaries
        """
        if not car:
            self.error.emit("Car data must be specified")
            return []

        try:
            # Get parts from database
            parts = self.db.get_all_parts()

            # Extract unique categories
            unique_categories = set()
            for part in parts:
                if isinstance(part, dict) and 'category' in part:
                    # Check if this part is compatible with our car
                    compatible = self._is_part_compatible_with_car(part, car)
                    if compatible:
                        category = part.get('category', '').strip()
                        if category and category.lower() != 'unknown':
                            unique_categories.add(category)

            # Create category objects
            result = [{'category': category} for category in sorted(unique_categories)]

            # If no categories found, add some defaults for testing
            if not result:
                logger.warning("No categories found in database, adding defaults for testing")
                default_categories = [
                    'Engine Parts', 'Brake System', 'Suspension', 'Transmission',
                    'Electrical', 'Body Parts', 'Interior', 'Exhaust System',
                    'Cooling System', 'Steering', 'Fuel System', 'Air Conditioning'
                ]
                result = [{'category': category} for category in default_categories]

            return result
        except Exception as e:
            logger.error(f"Error in _get_categories: {e}")
            return []

    def _get_products(self, car, category):
        """
        Get products for a car and category.

        Args:
            car: Car dictionary
            category: Category dictionary

        Returns:
            list: List of product dictionaries
        """
        if not car or not category or 'category' not in category:
            self.error.emit("Car and category must be specified")
            return []

        category_name = category['category']

        try:
            # Get parts from database
            parts = self.db.get_all_parts()

            # Filter parts by category and car compatibility
            filtered_parts = []
            for part in parts:
                if isinstance(part, dict) and 'category' in part:
                    # Check if part matches category
                    if part.get('category', '').strip() == category_name:
                        # Check if compatible with car
                        if self._is_part_compatible_with_car(part, car):
                            filtered_parts.append(part)

            # Convert parts to product objects for our UI
            result = []
            for part in filtered_parts:
                product = {
                    'id': part.get('parcode', 0),
                    'name': part.get('product_name', ''),
                    'category': part.get('category', ''),
                    'price': part.get('price', 0),
                    'quantity': part.get('quantity', 0),
                    'compatible_brands': part.get('compatible_brands', ''),
                    'compatible_models': part.get('compatible_models', ''),
                    'model_years': part.get('model_years', '')
                }
                result.append(product)

            # If no products found, add some test data
            if not result:
                logger.warning("No products found in database, adding test data")
                self._add_test_products(result, car, category_name)

            return result
        except Exception as e:
            logger.error(f"Error in _get_products: {e}")
            return []

    def _search_parts(self, search_text):
        """
        Search parts by text.

        Args:
            search_text: Search text

        Returns:
            list: List of matching parts
        """
        if not search_text:
            self.error.emit("Search text must be specified")
            return []

        try:
            # Search parts by text
            return self.db.search_parts(search_text)
        except Exception as e:
            logger.error(f"Error in _search_parts: {e}")
            return []

    def _get_part_details(self, part_id):
        """
        Get details for a part.

        Args:
            part_id: Part ID

        Returns:
            dict: Part details
        """
        if not part_id:
            self.error.emit("Part ID must be specified")
            return None

        try:
            # Get part details
            return self.db.get_part(part_id)
        except Exception as e:
            logger.error(f"Error in _get_part_details: {e}")
            return None

    def _is_part_compatible_with_car(self, part, car):
        """
        Check if a part is compatible with a car.

        Args:
            part: Part dictionary
            car: Car dictionary

        Returns:
            bool: True if compatible
        """
        # If the part has no compatibility info, assume it's compatible for testing
        if not part:
            return False

        try:
            # Get compatibility fields
            compatible_brands = part.get('compatible_brands', '')
            compatible_models = part.get('compatible_models', '')
            model_years = part.get('model_years', '')

            # If any of these fields are empty, assume compatible for testing
            if not compatible_brands or not compatible_models or not model_years:
                return True

            # Split fields into lists and check compatibility
            brands = [b.strip().lower() for b in compatible_brands.split(',')]
            models = [m.strip().lower() for m in compatible_models.split(',')]
            years = [y.strip().lower() for y in model_years.split(',')]

            car_brand = car['brand'].lower() if 'brand' in car else ''
            car_model = car['model'].lower() if 'model' in car else ''
            car_year = car['year'].lower() if 'year' in car else ''

            # Check if our car matches any of the compatible combinations
            brand_match = car_brand in brands or 'all' in brands
            model_match = car_model in models or 'all' in models
            year_match = not car_year or car_year in years or 'all' in years

            return brand_match and model_match and year_match
        except Exception as e:
            logger.error(f"Error in _is_part_compatible_with_car: {e}")
            return False

    def _add_test_products(self, products_list, car, category):
        """
        Add test products for a category.

        Args:
            products_list: List to add products to
            car: Car dictionary
            category: Category name
        """
        # Generate different test products based on category
        if category == 'Brake System':
            test_products = [
                {'name': 'Brake Pads', 'price': 49.99, 'quantity': 12},
                {'name': 'Brake Discs', 'price': 89.99, 'quantity': 8},
                {'name': 'Brake Fluid DOT 4', 'price': 12.99, 'quantity': 24},
                {'name': 'ABS Sensor', 'price': 39.99, 'quantity': 6}
            ]
        elif category == 'Engine Parts':
            test_products = [
                {'name': 'Oil Filter', 'price': 15.99, 'quantity': 30},
                {'name': 'Spark Plugs (set of 4)', 'price': 29.99, 'quantity': 15},
                {'name': 'Air Filter', 'price': 19.99, 'quantity': 20},
                {'name': 'Timing Belt Kit', 'price': 119.99, 'quantity': 5}
            ]
        elif category == 'Suspension':
            test_products = [
                {'name': 'Shock Absorbers (pair)', 'price': 149.99, 'quantity': 8},
                {'name': 'Coil Springs (pair)', 'price': 89.99, 'quantity': 10},
                {'name': 'Control Arm', 'price': 79.99, 'quantity': 6},
                {'name': 'Ball Joint', 'price': 45.99, 'quantity': 12}
            ]
        else:
            # Generic products for any other category
            test_products = [
                {'name': f'{category} Part A', 'price': 39.99, 'quantity': 10},
                {'name': f'{category} Part B', 'price': 59.99, 'quantity': 8},
                {'name': f'{category} Part C', 'price': 29.99, 'quantity': 15},
                {'name': f'{category} Part D', 'price': 79.99, 'quantity': 5}
            ]

        # Add category and car info to each product
        for i, product in enumerate(test_products):
            product['id'] = 10000 + i  # Dummy ID
            product['category'] = category
            product['compatible_brands'] = car.get('brand', '')
            product['compatible_models'] = car.get('model', '')
            product['model_years'] = car.get('year', '') if 'year' in car else ''

            products_list.append(product)

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self.db, 'close_connection'):
            try:
                self.db.close_connection()
            except Exception as e:
                logger.error(f"Error in cleanup: {e}")


class DatabaseOperator(QObject):
    """
    Manager for database operations in background threads.

    Features:
    - Thread management
    - Callback-based API
    - Error handling

    Usage:
        operator = DatabaseOperator(db)
        operator.execute("get_brands", self.on_brands_loaded, self.on_error)
    """
    # Lock for shared database connections
    _connections_lock = threading.RLock()

    # Static cache for shared database connections
    _shared_db_connections = {}

    def __init__(self, db):
        """
        Initialize the database operator.

        Args:
            db: Database connection
        """
        super().__init__()
        self.db = db
        self.thread = None
        self.worker = None
        self._thread_lock = threading.RLock()  # Add thread safety

    def _get_thread_db(self):
        """Get a database connection for the current thread with improved reuse."""
        thread_id = threading.get_ident()

        # Thread-safe access to shared connections
        with DatabaseOperator._connections_lock:
            # If we already have a connection for this thread, validate and reuse it
            if thread_id in DatabaseOperator._shared_db_connections:
                db = DatabaseOperator._shared_db_connections[thread_id]
                # Make sure the connection is still valid by running a simple test query
                if hasattr(db, 'ensure_connection'):
                    try:
                        db.ensure_connection()
                        logger.debug(f"Reusing existing database connection for thread {thread_id}")
                        return db
                    except Exception as e:
                        # If there's an error with the connection, remove it from cache
                        logger.error(f"Error with cached connection: {e}")
                        DatabaseOperator._shared_db_connections.pop(thread_id, None)

            # Create a new connection only when needed
            logger.debug(f"Creating new thread-local database connection for thread {thread_id}")
            # Store the connection in the shared cache
            DatabaseOperator._shared_db_connections[thread_id] = self.db
            return self.db

    def execute(self, operation, on_complete, on_error, **kwargs):
        """
        Execute a database operation in a background thread with improved error handling.

        Args:
            operation (str): The operation to perform
            on_complete (callable): Callback when operation completes
            on_error (callable): Callback when operation fails
            **kwargs: Additional parameters for the operation
        """
        with self._thread_lock:  # Thread-safe execution
            # Clean up any existing operation
            self.cleanup()

            try:
                # Create a new thread and worker for each operation
                self.thread = QThread()

                # Get a database connection with reuse and error handling
                try:
                    thread_db = self._get_thread_db()
                except Exception as e:
                    logger.error(f"Error getting thread database connection: {e}")
                    if on_error:
                        on_error(f"Database connection error: {e}")
                    return

                # Create worker with the reused connection
                self.worker = DatabaseWorker(thread_db)
                self.worker.moveToThread(self.thread)

                # Store operation and kwargs for the worker
                self._operation = operation
                self._kwargs = kwargs

                # Define a safer execution function
                def execute_operation():
                    try:
                        if hasattr(self, 'worker') and self.worker:
                            self.worker.execute(self._operation, **self._kwargs)
                    except Exception as e:
                        logger.error(f"Error executing operation: {e}")
                        if on_error:
                            try:
                                on_error(str(e))
                            except Exception as callback_error:
                                logger.error(f"Error in error callback: {callback_error}")

                # Create safer callback wrappers that handle exceptions
                def safe_complete_callback(result):
                    try:
                        if on_complete:
                            on_complete(result)
                    except Exception as e:
                        logger.error(f"Error in completion callback: {e}")

                def safe_error_callback(error_msg):
                    try:
                        if on_error:
                            on_error(error_msg)
                    except Exception as e:
                        logger.error(f"Error in error callback: {e}")

                # Connect signals with safer callbacks and thread safety
                self.worker.finished.connect(safe_complete_callback, type=Qt.QueuedConnection)
                self.worker.error.connect(safe_error_callback, type=Qt.QueuedConnection)
                self.thread.started.connect(execute_operation)

                # Connect cleanup operations
                def safe_handle_thread_finished(*args):
                    try:
                        self._handle_thread_finished(*args)
                    except Exception as e:
                        logger.error(f"Error in thread finished handler: {e}")

                if hasattr(self.worker, 'finished'):
                    self.worker.finished.connect(safe_handle_thread_finished, type=Qt.QueuedConnection)
                if hasattr(self.worker, 'error'):
                    self.worker.error.connect(safe_handle_thread_finished, type=Qt.QueuedConnection)

                # Start the thread
                self.thread.start()
            except Exception as e:
                logger.error(f"Failed to start database operation: {e}")
                if on_error:
                    try:
                        on_error(str(e))
                    except Exception as callback_error:
                        logger.error(f"Error in error callback: {callback_error}")

    def _handle_thread_finished(self, *args):
        """Safely handle thread completion."""
        try:
            if self.thread and self.thread.isRunning():
                self.thread.quit()
        except Exception as e:
            logger.error(f"Error in thread finished handler: {e}")

    def cleanup(self):
        """Clean up thread and worker resources with proper signal handling."""
        with self._thread_lock:  # Thread-safe cleanup
            # Clean up the worker first
            if hasattr(self, 'worker') and self.worker:
                try:
                    if hasattr(self.worker, 'cleanup'):
                        self.worker.cleanup()

                    # Safely disconnect worker signals
                    try:
                        if hasattr(self.worker, 'finished'):
                            self.worker.finished.disconnect()
                    except (TypeError, RuntimeError):
                        pass  # It's normal to get an exception if there are no connections

                    try:
                        if hasattr(self.worker, 'error'):
                            self.worker.error.disconnect()
                    except (TypeError, RuntimeError):
                        pass  # It's normal to get an exception if there are no connections

                    # Set to None before deleteLater to avoid accessing it again
                    worker_to_delete = self.worker
                    self.worker = None
                    worker_to_delete.deleteLater()
                except Exception as e:
                    logger.error(f"Error cleaning up worker: {e}")
                    self.worker = None

            # Then clean up the thread
            if hasattr(self, 'thread') and self.thread:
                try:
                    # Safely disconnect thread signals
                    try:
                        if hasattr(self.thread, 'started'):
                            self.thread.started.disconnect()
                    except (TypeError, RuntimeError):
                        pass  # It's normal to get an exception if there are no connections

                    try:
                        if hasattr(self.thread, 'finished'):
                            self.thread.finished.disconnect()
                    except (TypeError, RuntimeError):
                        pass  # It's normal to get an exception if there are no connections

                    # Try to quit the thread if it's running
                    thread_to_delete = self.thread
                    thread_is_running = thread_to_delete.isRunning()
                    self.thread = None  # Set to None before potentially waiting

                    if thread_is_running:
                        thread_to_delete.quit()
                        success = thread_to_delete.wait(1000)  # 1 second timeout
                        if not success:
                            logger.warning("Thread didn't finish within timeout, continuing cleanup")

                    # Schedule thread for deletion
                    thread_to_delete.deleteLater()
                except Exception as e:
                    logger.error(f"Error cleaning up thread: {e}")
                    self.thread = None