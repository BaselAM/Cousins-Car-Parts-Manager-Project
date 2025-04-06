"""
DatabaseWorker utility for asynchronous database operations.

Provides thread-safe database operations for the parts navigation system.
"""
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
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

    # Static cache for brands data
    _brands_cache = None

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
                self.db.ensure_connection()

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
        Get unique car brands with caching.

        Returns:
            list: List of brand dictionaries
        """
        # If we have a cached result, use it
        if DatabaseWorker._brands_cache is not None:
            logger.debug("Using cached brands data instead of querying database")
            return DatabaseWorker._brands_cache

        # Get all cars
        cars = self.db.get_all_cars()

        # Extract unique brands
        unique_brands = set()
        for car in cars:
            if isinstance(car, dict) and 'brand' in car:
                brand = car['brand'].strip()
                if brand and brand.lower() != 'unknown':
                    unique_brands.add(brand)

        # Create brand objects
        result = [{'brand': brand} for brand in sorted(unique_brands)]

        # Cache the result for future use
        DatabaseWorker._brands_cache = result

        return result

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

        # Search parts by text
        return self.db.search_parts(search_text)

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

        # Get part details
        return self.db.get_part(part_id)

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
            self.db.close_connection()


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

    def _get_thread_db(self):
        """Get a database connection for the current thread with reuse."""
        thread_id = threading.get_ident()

        # If we already have a connection for this thread, reuse it
        if thread_id in DatabaseOperator._shared_db_connections:
            db = DatabaseOperator._shared_db_connections[thread_id]
            # Make sure the connection is still valid
            if hasattr(db, 'ensure_connection'):
                try:
                    db.ensure_connection()
                    logger.debug(f"Reusing existing database connection for thread {thread_id}")
                    return db
                except Exception:
                    # If there's an error with the connection, remove it and create a new one
                    DatabaseOperator._shared_db_connections.pop(thread_id, None)

        # Create a new connection for this thread
        if hasattr(self.db, 'ensure_connection'):
            # If this is a connection that supports thread-local connections,
            # call ensure_connection to get a valid connection for this thread
            self.db.ensure_connection()
            DatabaseOperator._shared_db_connections[thread_id] = self.db
            logger.debug(f"Created new thread-local database connection for thread {thread_id}")
            return self.db
        else:
            # For other types of connections, just return the original
            return self.db

    def execute(self, operation, on_complete, on_error, **kwargs):
        """
        Execute a database operation in a background thread with improved shutdown safety.

        Args:
            operation (str): The operation to perform
            on_complete (callable): Callback when operation completes
            on_error (callable): Callback when operation fails
            **kwargs: Additional parameters for the operation
        """
        # Clean up any existing operation
        self.cleanup()

        try:
            # Create a new thread and worker for each operation
            self.thread = QThread()

            # Get a database connection with reuse
            thread_db = self._get_thread_db()

            # Create worker with the reused connection
            self.worker = DatabaseWorker(thread_db)
            self.worker.moveToThread(self.thread)

            # Store operation and kwargs for the worker
            self._operation = operation
            self._kwargs = kwargs

            # Define a safer execution function that checks if worker still exists
            def execute_operation():
                if hasattr(self, 'worker') and self.worker:
                    try:
                        self.worker.execute(self._operation, **self._kwargs)
                    except Exception as e:
                        logger.error(f"Error executing operation: {e}")
                        if on_error:
                            on_error(str(e))

            # Connect signals with better error handling
            self.worker.finished.connect(on_complete)
            self.worker.error.connect(on_error)
            self.thread.started.connect(execute_operation)
            self.worker.finished.connect(self.thread.quit)
            self.worker.error.connect(self.thread.quit)
            self.thread.finished.connect(self.cleanup)

            # Start the thread
            self.thread.start()
        except Exception as e:
            logger.error(f"Failed to start database operation: {e}")
            if on_error:
                on_error(str(e))

    def cleanup(self):
        """Clean up thread and worker resources with proper signal handling."""
        # Clean up the worker first
        if hasattr(self, 'worker') and self.worker:
            try:
                if hasattr(self.worker, 'cleanup'):
                    self.worker.cleanup()

                # Safely disconnect worker signals without checking receivers
                if hasattr(self.worker, 'finished'):
                    try:
                        # Just try to disconnect all connections
                        self.worker.finished.disconnect()
                    except (TypeError, RuntimeError):
                        # It's normal to get an exception if there are no connections
                        pass

                if hasattr(self.worker, 'error'):
                    try:
                        self.worker.error.disconnect()
                    except (TypeError, RuntimeError):
                        pass

                self.worker.deleteLater()
            except Exception as e:
                logger.error(f"Error cleaning up worker: {e}")
            finally:
                self.worker = None

        # Then clean up the thread
        if hasattr(self, 'thread') and self.thread:
            try:
                # Safely disconnect thread signals
                if hasattr(self.thread, 'started'):
                    try:
                        self.thread.started.disconnect()
                    except (TypeError, RuntimeError):
                        pass

                if hasattr(self.thread, 'finished'):
                    try:
                        self.thread.finished.disconnect()
                    except (TypeError, RuntimeError):
                        pass

                if self.thread.isRunning():
                    self.thread.quit()
                    success = self.thread.wait(1000)  # 1 second timeout
                    if not success:
                        logger.warning("Thread didn't finish within timeout, continuing cleanup")

                self.thread.deleteLater()
            except Exception as e:
                logger.error(f"Error cleaning up thread: {e}")
            finally:
                self.thread = None