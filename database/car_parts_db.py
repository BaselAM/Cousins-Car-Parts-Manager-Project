import mysql.connector
from mysql.connector import pooling
import threading
from logger import get_logger
from datetime import datetime


class CarPartsDB:
    """Thread-safe database handler for car parts inventory with MySQL backend"""

    def __init__(self, config=None):
        # Use the centralized logging configuration instead of creating a new logger
        self.logger = get_logger('database.car_parts_db')

        # Default MySQL configuration
        if config is None:
            self.config = {
                'host': 'localhost',
                'user': 'root',
                'password': 'CousinsBusiness321$',
                'database': 'car_parts_system'
            }
        else:
            self.config = config

        # Thread-local storage for connections
        self.local = threading.local()
        self.lock = threading.RLock()  # Reentrant lock for thread safety

        # Set initial transaction state tracking
        self.local.in_transaction = False

        # Connection pool
        self.pool = self._create_connection_pool()

        # Initialize main thread connection
        self.connect()
        self.logger.info(f"Initialized database connection to {self.config['host']}")

    def _create_connection_pool(self):
        """Create a connection pool for MySQL"""
        try:
            pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="car_parts_pool",
                pool_size=10,  # Increased from 5
                pool_reset_session=True,  # Reset session variables when returning to pool
                **self.config
            )
            return pool
        except mysql.connector.Error as e:
            self.logger.error(f"Error creating connection pool: {str(e)}")
            raise

    def connect(self):
        """Create a thread-local database connection"""
        try:
            # Close existing connection for this thread if it exists
            self.close_connection()

            # Get connection from pool
            self.local.conn = self.pool.get_connection()
            self.local.cursor = self.local.conn.cursor(dictionary=True)

            # Initialize transaction state
            self.local.in_transaction = False

            # Create table if needed
            self.create_table()

            thread_id = threading.get_ident()
            self.logger.info(f"Thread {thread_id}: Database connection established")

        except mysql.connector.Error as e:
            self.logger.error(f"Connection error: {str(e)}")
            raise

    def create_table(self):
        """Create table with enhanced schema if it doesn't exist"""
        # Updated to match the actual database schema with id as primary key
        query = '''
        CREATE TABLE IF NOT EXISTS parts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(255) NOT NULL,
            product_name VARCHAR(255) NOT NULL,
            quantity INT DEFAULT 0,
            price DECIMAL(10, 2) DEFAULT 0.0,
            compatible_brands TEXT,
            compatible_models TEXT,
            model_years TEXT,
            drive_type VARCHAR(50),
            engine_info TEXT,
            position VARCHAR(50),
            side VARCHAR(50),
            engine_type VARCHAR(100),
            original TINYINT(1) DEFAULT 0,
            manufacturer VARCHAR(255),
            parcode VARCHAR(255) NOT NULL,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        '''
        self.execute_query(query)

    def close_connection(self):
        """Close the connection for the current thread"""
        if hasattr(self.local, 'cursor') and self.local.cursor:
            try:
                self.local.cursor.close()
            except Exception as e:
                self.logger.warning(f"Error closing cursor: {e}")
            self.local.cursor = None

        if hasattr(self.local, 'conn') and self.local.conn:
            try:
                # Make sure any transaction is rolled back before closing
                if hasattr(self.local, 'in_transaction') and self.local.in_transaction:
                    try:
                        self.rollback_transaction()
                    except Exception as e:
                        self.logger.warning(f"Error rolling back transaction during close: {e}")

                # Now close the connection
                self.local.conn.close()

                # Important: Set to None after closing
                self.local.conn = None
                self.local.in_transaction = False
            except Exception as e:
                self.logger.warning(f"Error closing connection: {e}")
                self.local.conn = None
                self.local.in_transaction = False

    def ensure_connection(self):
        """Ensure this thread has a valid connection without disrupting transactions"""
        # First, check if we need a new connection
        needs_new_connection = False

        if not hasattr(self.local, 'conn') or self.local.conn is None:
            needs_new_connection = True
        else:
            try:
                # Test connection with minimal impact query
                self.local.cursor.execute("SELECT 1")
                self.local.cursor.fetchall()  # Consume the result
            except Exception as e:
                self.logger.debug(f"Connection check failed: {e}, reconnecting")
                needs_new_connection = True

        # If connection is OK, just return
        if not needs_new_connection:
            return

        # We need a new connection
        try:
            # Check if we're in a transaction before closing
            was_in_transaction = False
            if hasattr(self.local, 'in_transaction'):
                was_in_transaction = self.local.in_transaction

            # Close the old connection
            self.close_connection()

            # Get a new connection from the pool
            self.local.conn = self.pool.get_connection()
            self.local.cursor = self.local.conn.cursor(dictionary=True)
            self.local.in_transaction = False

            thread_id = threading.get_ident()
            self.logger.info(f"Thread {thread_id}: New database connection established")

            # Log warning if we lost a transaction
            if was_in_transaction:
                self.logger.warning("Lost transaction during connection refresh")

        except Exception as e:
            self.logger.warning(f"Pool get_connection failed: {e}, falling back to direct connect")
            # Fall back to creating a new direct connection
            try:
                # Direct connection (not from pool)
                self.local.conn = mysql.connector.connect(**self.config)
                self.local.cursor = self.local.conn.cursor(dictionary=True)
                self.local.in_transaction = False

                thread_id = threading.get_ident()
                self.logger.info(f"Thread {thread_id}: Direct database connection established")
            except Exception as direct_error:
                self.logger.error(f"Direct connection also failed: {direct_error}")
                raise

    def ensure_transaction_state(self, desired_state='ready'):
        """
        Ensure the connection is in the desired transaction state

        Args:
            desired_state: Either 'ready' (no transaction) or 'active' (transaction started)
        """
        with self.lock:
            self.ensure_connection()

            current_state = hasattr(self.local, 'in_transaction') and self.local.in_transaction

            # If we want 'ready' state (no transaction) but one is active
            if desired_state == 'ready' and current_state:
                try:
                    self.commit_transaction()
                except Exception as e:
                    self.logger.warning(f"Error committing transaction during state change: {e}")
                    try:
                        self.rollback_transaction()
                    except:
                        pass

            # If we want 'active' state (transaction started) but none is active
            elif desired_state == 'active' and not current_state:
                self.begin_transaction()

    def execute_query(self, query, params=(), fetch_all=False, commit=False):
        """
        Execute a query with the thread-local connection

        Args:
            query: SQL query to execute
            params: Parameters for the query
            fetch_all: Whether to fetch and return all results
            commit: Whether to commit after execution

        Returns:
            Query cursor or fetched results if fetch_all is True
        """
        with self.lock:
            self.ensure_connection()
            try:
                self.local.cursor.execute(query, params)

                if commit:
                    self.commit_transaction()

                if fetch_all:
                    return self.local.cursor.fetchall()

                return self.local.cursor

            except mysql.connector.Error as e:
                if "doesn't exist" in str(e) and "table" in str(e).lower():
                    self.create_table()
                    self.local.cursor.execute(query, params)

                    if commit:
                        self.commit_transaction()

                    if fetch_all:
                        return self.local.cursor.fetchall()

                    return self.local.cursor
                else:
                    self.logger.error(f"Database error in execute_query: {e}")
                    # Try reconnecting
                    try:
                        self.connect()
                        self.local.cursor.execute(query, params)

                        if commit:
                            self.commit_transaction()

                        if fetch_all:
                            return self.local.cursor.fetchall()

                        return self.local.cursor
                    except Exception as retry_error:
                        self.logger.error(f"Query retry failed: {retry_error}")
                        raise

    def update_schema_if_needed(self):
        """Check and update database schema if needed"""
        with self.lock:
            self.ensure_connection()
            try:
                # Check if the parts table exists
                self.local.cursor.execute("SHOW TABLES LIKE 'parts'")
                if not self.local.cursor.fetchone():
                    # Table doesn't exist, create it
                    self.create_table()
                    return True

                # Get existing columns
                self.local.cursor.execute("DESCRIBE parts")
                existing_columns = {row['Field'] for row in self.local.cursor.fetchall()}

                # Define the expected columns
                expected_columns = {
                    'id', 'parcode', 'category', 'product_name', 'quantity', 'price',
                    'compatible_brands', 'compatible_models', 'model_years',
                    'drive_type', 'engine_info', 'position', 'side', 'engine_type',
                    'original', 'manufacturer', 'last_updated'
                }

                # Add any missing columns
                missing_columns = expected_columns - existing_columns
                if missing_columns:
                    self.begin_transaction()

                    for column in missing_columns:
                        # Use appropriate data type based on column name
                        if column == 'id' and 'id' not in existing_columns:
                            data_type = 'INT AUTO_INCREMENT PRIMARY KEY'
                        elif column in ('quantity'):
                            data_type = 'INT DEFAULT 0'
                        elif column in ('price'):
                            data_type = 'DECIMAL(10, 2) DEFAULT 0.0'
                        elif column == 'original':
                            data_type = 'TINYINT(1) DEFAULT 0'
                        elif column == 'parcode':
                            data_type = 'VARCHAR(255) NOT NULL'
                        elif column == 'manufacturer':
                            data_type = 'VARCHAR(255)'
                        elif column == 'last_updated':
                            data_type = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
                        else:
                            data_type = 'TEXT'

                        self.local.cursor.execute(f"ALTER TABLE parts ADD COLUMN {column} {data_type}")
                        self.logger.info(f"Added missing column: {column}")

                    self.commit_transaction()

                return True

            except mysql.connector.Error as e:
                self.logger.error(f"Error updating schema: {e}")
                if hasattr(self.local, 'in_transaction') and self.local.in_transaction:
                    self.rollback_transaction()
                return False

    def add_part(self, category, product_name, quantity=0, price=0.0, original=False, manufacturer=None, parcode=None,
                 **kwargs):
        """
        Add a new part with enhanced fields

        Args:
            category: Part category
            product_name: Name of the part
            quantity: Stock quantity
            price: Unit price
            original: Boolean indicating if this is an original manufacturer part
            manufacturer: Name of the part manufacturer
            parcode: Part code or number (string)
            **kwargs: Additional part attributes
        """
        with self.lock:
            self.ensure_transaction_state('ready')  # Ensure no active transaction

            try:
                # Validate inputs and provide defaults for required fields
                if not product_name or product_name.strip() == "":
                    self.logger.error("Cannot add part: product name is required")
                    return False

                # Set defaults for required fields that can't be NULL
                category = category if category and category.strip() else "Other Parts"

                # Generate a default parcode if not provided
                if not parcode:
                    # Create a simple default parcode based on product name and timestamp
                    timestamp = int(datetime.now().timestamp())
                    parcode = f"P{timestamp}"

                # Prepare additional fields
                field_names = ['category', 'product_name', 'quantity', 'price', 'parcode']
                field_values = [category, product_name, quantity, price, parcode]

                # Add the new fields if provided
                if original is not None:
                    field_names.append('original')
                    field_values.append(1 if original else 0)  # Convert to tinyint

                if manufacturer is not None:
                    field_names.append('manufacturer')
                    field_values.append(manufacturer)

                # Add any additional fields from kwargs
                for key, value in kwargs.items():
                    field_names.append(key)
                    field_values.append(value)

                # Convert and validate numeric values
                try:
                    quantity = int(quantity) if quantity is not None else 0
                    price = float(price) if price is not None else 0.0
                except (ValueError, TypeError):
                    self.logger.error("Invalid quantity or price values")
                    quantity = 0
                    price = 0.0

                thread_id = threading.get_ident()
                self.logger.info(f"Thread {thread_id}: Adding part: '{product_name}'")

                # Begin transaction
                self.begin_transaction()

                # Build the query
                fields = ', '.join(field_names)
                placeholders = ', '.join(['%s'] * len(field_values))

                query = f"INSERT INTO parts ({fields}) VALUES ({placeholders})"
                self.local.cursor.execute(query, field_values)

                # Get the ID of the inserted row
                new_id = self.local.cursor.lastrowid
                self.logger.info(f"Created new part with ID: {new_id}")

                # Explicitly commit the transaction
                self.commit_transaction()

                # Verify the part was added by trying to fetch it
                self.local.cursor.execute("SELECT * FROM parts WHERE id = %s", (new_id,))
                result = self.local.cursor.fetchone()

                if result:
                    self.logger.info(f"Successfully verified part was added with ID: {new_id}")
                    return True
                else:
                    self.logger.error(f"Failed to verify part was added with ID: {new_id}")
                    return False

            except mysql.connector.Error as e:
                self.logger.error(f"Database error in add_part: {e}")
                # Try to rollback if there was an error
                if hasattr(self.local, 'in_transaction') and self.local.in_transaction:
                    self.rollback_transaction()
                return False

    def get_part(self, part_id):
        """Get a single part by ID"""
        with self.lock:
            self.ensure_connection()
            try:
                self.local.cursor.execute("SELECT * FROM parts WHERE id = %s", (part_id,))
                return self.local.cursor.fetchone()
            except mysql.connector.Error as e:
                self.logger.error(f"Error fetching part {part_id}: {e}")
                return None

    def get_part_by_parcode(self, parcode):
        """Get a single part by parcode"""
        with self.lock:
            self.ensure_connection()
            try:
                self.local.cursor.execute("SELECT * FROM parts WHERE parcode = %s", (parcode,))
                return self.local.cursor.fetchone()
            except mysql.connector.Error as e:
                self.logger.error(f"Error fetching part with parcode {parcode}: {e}")
                return None

    def search_parts(self, search_term=''):
        """Search parts by any field (enhanced)"""
        with self.lock:
            self.ensure_connection()

            # Get all text columns for searching
            self.local.cursor.execute("DESCRIBE parts")
            text_columns = [row['Field'] for row in self.local.cursor.fetchall()
                            if 'text' in row['Type'].lower() or 'varchar' in row['Type'].lower()]

            conditions = ' OR '.join([f"{col} LIKE %s" for col in text_columns])
            params = [f'%{search_term}%'] * len(text_columns)

            query = f"SELECT * FROM parts WHERE {conditions}"

            try:
                self.local.cursor.execute(query, params)
                return self.local.cursor.fetchall()
            except mysql.connector.Error as e:
                self.logger.error(f"Search error: {e}")
                return []

    def begin_transaction(self):
        """Begin a transaction in the current thread's connection"""
        with self.lock:
            self.ensure_connection()

            # If already in a transaction, just return
            if hasattr(self.local, 'in_transaction') and self.local.in_transaction:
                thread_id = threading.get_ident()
                self.logger.debug(f"Thread {thread_id}: Transaction already active")
                return True

            try:
                # Start a new transaction
                self.local.conn.start_transaction()
                self.local.in_transaction = True

                thread_id = threading.get_ident()
                self.logger.debug(f"Thread {thread_id}: Transaction started")
                return True

            except mysql.connector.Error as e:
                if "Transaction already in progress" in str(e):
                    # Transaction already exists, mark as in transaction
                    self.local.in_transaction = True
                    self.logger.debug(f"Thread {threading.get_ident()}: Using existing transaction")
                    return True
                else:
                    self.logger.error(f"Error starting transaction: {e}")
                    return False

    def commit_transaction(self):
        """Commit the current transaction"""
        with self.lock:
            if not hasattr(self.local, 'conn') or self.local.conn is None:
                return False

            # Only commit if we're in a transaction
            if not hasattr(self.local, 'in_transaction') or not self.local.in_transaction:
                return True  # Nothing to commit

            try:
                self.local.conn.commit()
                self.local.in_transaction = False

                thread_id = threading.get_ident()
                self.logger.debug(f"Thread {thread_id}: Transaction committed")
                return True

            except mysql.connector.Error as e:
                self.logger.error(f"Error committing transaction: {e}")
                return False

    def rollback_transaction(self):
        """Roll back the current transaction"""
        with self.lock:
            if not hasattr(self.local, 'conn') or self.local.conn is None:
                return False

            # Only roll back if we're in a transaction
            if not hasattr(self.local, 'in_transaction') or not self.local.in_transaction:
                return True  # Nothing to roll back

            try:
                self.local.conn.rollback()
                self.local.in_transaction = False

                thread_id = threading.get_ident()
                self.logger.debug(f"Thread {thread_id}: Transaction rolled back")
                return True

            except mysql.connector.Error as e:
                self.logger.error(f"Error rolling back transaction: {e}")
                return False

    def get_all_parts(self):
        """Get all parts from the database"""
        with self.lock:
            self.ensure_connection()
            try:
                self.local.cursor.execute("SELECT * FROM parts")
                return self.local.cursor.fetchall()
            except mysql.connector.Error as e:
                self.logger.error(f"Error fetching all parts: {e}")
                return []

    def update_part(self, part_id, **kwargs):
        """
        Update a part with the given values

        Args:
            part_id: ID of the part to update
            **kwargs: Fields to update, including 'original' (boolean) and 'manufacturer' (string)
        """
        with self.lock:
            self.ensure_transaction_state('ready')  # Ensure no active transaction

            # Skip empty updates
            if not kwargs:
                return False

            # Convert boolean 'original' to tinyint for database
            if 'original' in kwargs:
                kwargs['original'] = 1 if kwargs['original'] else 0

            try:
                # Begin transaction using proper method
                self.begin_transaction()

                # First verify the part exists
                verify_query = "SELECT COUNT(*) as count FROM parts WHERE id = %s"
                self.local.cursor.execute(verify_query, (part_id,))
                result = self.local.cursor.fetchone()  # Always fetch results

                # If no record found, log and return
                if not result or result['count'] == 0:
                    self.logger.warning(f"No part found with ID: {part_id}")
                    self.rollback_transaction()
                    return False

                # Build the update statement
                set_clauses = []
                params = []
                for key, value in kwargs.items():
                    set_clauses.append(f"{key} = %s")
                    params.append(value)

                # Add the part_id as the last parameter
                params.append(part_id)

                # Execute the update
                query = f"UPDATE parts SET {', '.join(set_clauses)} WHERE id = %s"
                self.local.cursor.execute(query, params)

                # Commit using proper method
                self.commit_transaction()

                # Log success
                self.logger.info(f"Updated part with ID: {part_id}")
                return True

            except mysql.connector.Error as e:
                self.logger.error(f"Error updating part {part_id}: {e}")
                self.rollback_transaction()
                return False

    def delete_part(self, part_id):
        """Delete a part by ID"""
        with self.lock:
            self.ensure_transaction_state('ready')  # Ensure no active transaction

            try:
                # Begin new transaction
                self.begin_transaction()

                # Check if part exists
                self.local.cursor.execute("SELECT COUNT(*) as count FROM parts WHERE id = %s", (part_id,))
                result = self.local.cursor.fetchone()

                if not result or result['count'] == 0:
                    self.logger.warning(f"No part found with ID: {part_id}")
                    self.rollback_transaction()
                    return False

                # Delete the part
                self.local.cursor.execute("DELETE FROM parts WHERE id = %s", (part_id,))
                self.commit_transaction()

                self.logger.info(f"Deleted part with ID: {part_id}")
                return True

            except mysql.connector.Error as e:
                self.logger.error(f"Error deleting part {part_id}: {e}")
                self.rollback_transaction()
                return False

    def delete_parts_batch(self, part_ids):
        """Delete multiple parts in a single transaction"""
        if not part_ids:
            return True

        with self.lock:
            self.ensure_transaction_state('ready')  # Ensure no active transaction

            try:
                # Begin new transaction
                self.begin_transaction()

                # Prepare ID placeholders for SQL
                placeholders = ', '.join(['%s'] * len(part_ids))

                # Delete in a single query
                query = f"DELETE FROM parts WHERE id IN ({placeholders})"
                self.local.cursor.execute(query, part_ids)

                # Commit the transaction
                self.commit_transaction()
                self.logger.info(f"Batch deleted {self.local.cursor.rowcount} parts")
                return True

            except mysql.connector.Error as e:
                self.logger.error(f"Error in batch delete: {e}")
                self.rollback_transaction()
                return False

    def get_part_by_name(self, product_name):
        """Get a part by product name"""
        with self.lock:
            self.ensure_connection()
            try:
                self.local.cursor.execute("SELECT * FROM parts WHERE product_name = %s", (product_name,))
                return self.local.cursor.fetchone()
            except mysql.connector.Error as e:
                self.logger.error(f"Error fetching part by name '{product_name}': {e}")
                return None

    def get_unique_cars(self):
        """Get a list of unique car brands from the database"""
        unique_cars = []
        with self.lock:
            self.ensure_connection()
            try:
                # Simple query to get just the compatible_brands column
                self.local.cursor.execute("""
                    SELECT DISTINCT compatible_brands 
                    FROM parts 
                    WHERE compatible_brands IS NOT NULL AND compatible_brands != ''
                """)

                # Get all results
                results = self.local.cursor.fetchall()
                self.logger.info(f"Found {len(results)} unique car brands in database")

                # Safely process results to strings only
                for row in results:
                    # Handle different result types safely
                    brand = None

                    if isinstance(row, dict):
                        # Dictionary result (MySQL connector with dictionary=True)
                        brand = row.get('compatible_brands', '')
                    elif isinstance(row, (tuple, list)) and len(row) > 0:
                        # Tuple/list result (standard cursor)
                        brand = str(row[0]) if row[0] is not None else ''
                    else:
                        # Some other type - try to convert safely
                        try:
                            brand = str(row)
                        except:
                            continue

                    # Only add non-empty strings that aren't already in the list
                    if brand and brand not in unique_cars:
                        unique_cars.append(brand)

                self.logger.info(f"Processed {len(unique_cars)} unique car brands")

            except mysql.connector.Error as e:
                self.logger.error(f"Error fetching unique cars: {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error in get_unique_cars: {e}")
                import traceback
                self.logger.error(traceback.format_exc())

        return unique_cars  # Always return a list (empty if error)

    def get_all_cars(self):
        """
        Get all unique cars from the database with improved error handling.

        Returns:
            list: A list of car dictionaries with brand, model, and year
        """
        with self.lock:
            self.ensure_connection()
            try:
                # Use a query that explicitly returns the structure we want
                query = """
                SELECT DISTINCT 
                    IF(compatible_brands IS NULL OR compatible_brands = '', 'Unknown', compatible_brands) AS brand,
                    IF(model_years IS NULL OR model_years = '', 'Unknown', model_years) AS year,
                    IF(compatible_models IS NULL OR compatible_models = '', 'Unknown', compatible_models) AS model
                FROM parts 
                WHERE compatible_brands IS NOT NULL AND compatible_brands != ''
                ORDER BY brand, model, year
                """

                self.local.cursor.execute(query)
                results = self.local.cursor.fetchall()

                # Convert to a standard format - list of dictionaries
                cars = []
                brands_processed = set()

                for row in results:
                    # Handle potential missing values
                    brand = row.get('brand', 'Unknown') if isinstance(row, dict) else row[0]
                    year = row.get('year', 'Unknown') if isinstance(row, dict) else row[1]
                    model = row.get('model', 'Unknown') if isinstance(row, dict) else row[2]

                    # Process brands from comma-separated lists
                    for single_brand in str(brand).split(','):
                        single_brand = single_brand.strip()
                        if not single_brand or single_brand.lower() == 'unknown':
                            continue

                        # Create a unique brand identifier to prevent duplicates
                        brand_id = single_brand.lower()
                        if brand_id in brands_processed:
                            continue

                        brands_processed.add(brand_id)

                        # Add to our results
                        cars.append({
                            'brand': single_brand,
                            'model': model,
                            'year': year
                        })

                self.logger.info(f"Found {len(cars)} unique car brands in database")
                self.logger.info(f"Processed {len(brands_processed)} unique car brands")
                return cars

            except Exception as e:
                self.logger.error(f"Error fetching car data: {e}")
                # Return empty list rather than None to prevent cascading errors
                return []

    def get_parts_by_manufacturer(self, manufacturer):
        """Get parts by manufacturer name"""
        with self.lock:
            self.ensure_connection()
            try:
                self.local.cursor.execute("SELECT * FROM parts WHERE manufacturer = %s", (manufacturer,))
                return self.local.cursor.fetchall()
            except mysql.connector.Error as e:
                self.logger.error(f"Error fetching parts by manufacturer '{manufacturer}': {e}")
                return []

    def get_original_parts(self, is_original=True):
        """Get parts filtered by original status"""
        with self.lock:
            self.ensure_connection()
            try:
                # Convert boolean to tinyint for query
                is_original_int = 1 if is_original else 0
                self.local.cursor.execute("SELECT * FROM parts WHERE original = %s", (is_original_int,))
                return self.local.cursor.fetchall()
            except mysql.connector.Error as e:
                self.logger.error(f"Error fetching original parts (is_original={is_original}): {e}")
                return []