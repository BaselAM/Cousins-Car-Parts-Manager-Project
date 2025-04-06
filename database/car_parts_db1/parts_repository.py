# ------------------------------------------------------------
# parts_repository.py - Car parts data repository module
# ------------------------------------------------------------
import logging
import threading


class PartsRepository:
    """Repository for working with car parts data"""

    def __init__(self, connection_manager, transaction_manager, logger=None):
        """Initialize with connection and transaction managers"""
        self.connection_manager = connection_manager
        self.transaction_manager = transaction_manager
        self.logger = logger or logging.getLogger('database.parts_repository')
        self.lock = threading.RLock()

    def create_table(self):
        """Create parts table if it doesn't exist"""
        query = '''
        CREATE TABLE IF NOT EXISTS parts (
            parcode INT AUTO_INCREMENT PRIMARY KEY,
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
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        '''
        with self.transaction_manager.transaction():
            self.connection_manager.cursor.execute(query)

    def update_schema_if_needed(self):
        """Check and update database schema if needed"""
        with self.lock:
            cursor = self.connection_manager.cursor

            try:
                # Check if the parts table exists
                cursor.execute("SHOW TABLES LIKE 'parts'")
                if not cursor.fetchone():
                    # Table doesn't exist, create it
                    self.create_table()
                    return True

                # Get existing columns
                cursor.execute("DESCRIBE parts")
                existing_columns = {row['Field'] for row in cursor.fetchall()}

                # Define the expected columns
                expected_columns = {
                    'parcode', 'category', 'product_name', 'quantity', 'price',
                    'compatible_brands', 'compatible_models', 'model_years',
                    'drive_type', 'engine_info', 'position', 'side', 'engine_type',
                    'last_updated'
                }

                # Add any missing columns
                missing_columns = expected_columns - existing_columns
                if missing_columns:
                    with self.transaction_manager.transaction():
                        for column in missing_columns:
                            # Use appropriate data type based on column name
                            if column in ('quantity'):
                                data_type = 'INT DEFAULT 0'
                            elif column in ('price'):
                                data_type = 'DECIMAL(10, 2) DEFAULT 0.0'
                            elif column == 'last_updated':
                                data_type = "TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
                            else:
                                data_type = 'TEXT'

                            cursor.execute(f"ALTER TABLE parts ADD COLUMN {column} {data_type}")
                            self.logger.info(f"Added missing column: {column}")

                return True

            except Exception as e:
                self.logger.error(f"Error updating schema: {e}")
                return False

    def add_part(self, category, product_name, quantity=0, price=0.0, **kwargs):
        """Add a new part with validated fields"""
        with self.lock:
            cursor = self.connection_manager.cursor

            try:
                # Validate inputs
                if not product_name or product_name.strip() == "":
                    self.logger.error("Cannot add part: product name is required")
                    return False

                # Set defaults for required fields
                category = category if category and category.strip() else "Other Parts"

                # Prepare fields and values
                field_names = ['category', 'product_name', 'quantity', 'price']
                field_values = [category, product_name, quantity, price]

                # Get valid columns from the database
                cursor.execute("DESCRIBE parts")
                valid_columns = {row['Field'] for row in cursor.fetchall()}

                # Add valid additional fields from kwargs
                for key, value in kwargs.items():
                    if key in valid_columns:
                        field_names.append(key)
                        field_values.append(value)
                    else:
                        self.logger.warning(f"Skipping invalid column '{key}' during part creation")

                # Convert and validate numeric values
                try:
                    quantity = int(quantity) if quantity is not None else 0
                    price = float(price) if price is not None else 0.0
                except (ValueError, TypeError):
                    self.logger.error("Invalid quantity or price values")
                    quantity = 0
                    price = 0.0

                # Update the values after validation
                for i, name in enumerate(field_names):
                    if name == 'quantity':
                        field_values[i] = quantity
                    elif name == 'price':
                        field_values[i] = price

                # Use transaction context manager
                with self.transaction_manager.transaction():
                    # Build and execute the query
                    fields = ', '.join(field_names)
                    placeholders = ', '.join(['%s'] * len(field_values))
                    query = f"INSERT INTO parts ({fields}) VALUES ({placeholders})"
                    cursor.execute(query, field_values)

                    # Get the ID of the inserted row
                    new_id = cursor.lastrowid
                    self.logger.info(f"Created new part with Parcode: {new_id}")

                # Verify the part was added by trying to fetch it
                cursor.execute("SELECT * FROM parts WHERE parcode = %s", (new_id,))
                result = cursor.fetchone()

                if result:
                    self.logger.info(f"Successfully verified part was added with Parcode: {new_id}")
                    return True
                else:
                    self.logger.error(f"Failed to verify part was added with Parcode: {new_id}")
                    return False

            except Exception as e:
                self.logger.error(f"Error in add_part: {e}")
                return False

    def get_part(self, parcode):
        """Get a single part by parcode"""
        cursor = self.connection_manager.cursor
        try:
            cursor.execute("SELECT * FROM parts WHERE parcode = %s", (parcode,))
            return cursor.fetchone()
        except Exception as e:
            self.logger.error(f"Error fetching part {parcode}: {e}")
            return None

    def get_all_parts(self):
        """Get all parts from the database"""
        cursor = self.connection_manager.cursor
        try:
            cursor.execute("SELECT * FROM parts")
            return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Error fetching all parts: {e}")
            return []

    def search_parts(self, search_term='', limit=100, offset=0, sort_by='product_name', sort_order='ASC'):
        """Search parts with pagination and optimized performance"""
        cursor = self.connection_manager.cursor

        # Validate sort parameters to prevent injection
        valid_sort_columns = {'parcode', 'category', 'product_name', 'quantity', 'price', 'last_updated'}
        if sort_by not in valid_sort_columns:
            sort_by = 'product_name'  # Default if invalid

        if sort_order not in ('ASC', 'DESC'):
            sort_order = 'ASC'  # Default if invalid

        # Empty search returns recent items
        if not search_term:
            query = f"""
                SELECT * FROM parts 
                ORDER BY {sort_by} {sort_order}
                LIMIT %s OFFSET %s
            """
            try:
                cursor.execute(query, (limit, offset))
                return cursor.fetchall()
            except Exception as e:
                self.logger.error(f"Search error: {e}")
                return []

        # With search term, focus on most relevant columns first
        query = f"""
            SELECT * FROM parts 
            WHERE 
                product_name LIKE %s OR 
                category LIKE %s OR
                compatible_brands LIKE %s OR
                compatible_models LIKE %s
            ORDER BY 
                CASE 
                    WHEN product_name LIKE %s THEN 1
                    WHEN category LIKE %s THEN 2
                    WHEN compatible_brands LIKE %s THEN 3
                    WHEN compatible_models LIKE %s THEN 4
                    ELSE 5
                END,
                {sort_by} {sort_order}
            LIMIT %s OFFSET %s
        """

        # Parameters for the LIKE conditions and for the CASE ordering
        search_param = f'%{search_term}%'
        params = [
            search_param, search_param, search_param, search_param,  # For WHERE clause
            search_param, search_param, search_param, search_param,  # For CASE clause
            limit, offset  # For pagination
        ]

        try:
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return []

    def update_part(self, parcode, **kwargs):
        """Update a part with the given values"""
        with self.lock:
            cursor = self.connection_manager.cursor

            # Skip empty updates
            if not kwargs:
                return False

            try:
                # First verify the part exists
                cursor.execute("SELECT COUNT(*) as count FROM parts WHERE parcode = %s", (parcode,))
                result = cursor.fetchone()

                # If no record found, log and return
                if not result or result['count'] == 0:
                    self.logger.warning(f"No part found with parcode: {parcode}")
                    return False

                # Get valid columns from the database
                cursor.execute("DESCRIBE parts")
                valid_columns = {row['Field'] for row in cursor.fetchall()}

                # Filter out invalid column names
                filtered_kwargs = {}
                for key, value in kwargs.items():
                    if key in valid_columns:
                        filtered_kwargs[key] = value
                    else:
                        self.logger.warning(f"Ignoring invalid column name: {key}")

                # If no valid column names, return
                if not filtered_kwargs:
                    self.logger.warning(f"No valid columns to update for parcode: {parcode}")
                    return False

                # Build the update statement with validated fields
                set_clauses = []
                params = []
                for key, value in filtered_kwargs.items():
                    set_clauses.append(f"{key} = %s")
                    params.append(value)

                # Add the parcode as the last parameter
                params.append(parcode)

                # Execute the update within a transaction
                with self.transaction_manager.transaction():
                    query = f"UPDATE parts SET {', '.join(set_clauses)} WHERE parcode = %s"
                    cursor.execute(query, params)

                # Log success
                self.logger.info(f"Updated part with parcode: {parcode}")
                return True

            except Exception as e:
                self.logger.error(f"Error updating part {parcode}: {e}")
                return False

    def delete_part(self, parcode):
        """Delete a part by parcode"""
        with self.lock:
            cursor = self.connection_manager.cursor

            try:
                # Check if part exists
                cursor.execute("SELECT COUNT(*) as count FROM parts WHERE parcode = %s", (parcode,))
                result = cursor.fetchone()

                if not result or result['count'] == 0:
                    self.logger.warning(f"No part found with parcode: {parcode}")
                    return False

                # Delete the part within a transaction
                with self.transaction_manager.transaction():
                    cursor.execute("DELETE FROM parts WHERE parcode = %s", (parcode,))

                self.logger.info(f"Deleted part with parcode: {parcode}")
                return True

            except Exception as e:
                self.logger.error(f"Error deleting part {parcode}: {e}")
                return False

    def delete_parts_batch(self, part_ids):
        """Delete multiple parts in a single transaction"""
        if not part_ids:
            return True

        with self.lock:
            cursor = self.connection_manager.cursor

            try:
                # Prepare ID placeholders for SQL
                placeholders = ', '.join(['%s'] * len(part_ids))

                # Delete in a single query within a transaction
                with self.transaction_manager.transaction():
                    query = f"DELETE FROM parts WHERE parcode IN ({placeholders})"
                    cursor.execute(query, part_ids)

                self.logger.info(f"Batch deleted {cursor.rowcount} parts")
                return True

            except Exception as e:
                self.logger.error(f"Error in batch delete: {e}")
                return False

    def get_part_by_name(self, product_name):
        """Get a part by product name"""
        cursor = self.connection_manager.cursor
        try:
            cursor.execute("SELECT * FROM parts WHERE product_name = %s", (product_name,))
            return cursor.fetchone()
        except Exception as e:
            self.logger.error(f"Error fetching part by name '{product_name}': {e}")
            return None

    def get_unique_cars(self):
        """Get a list of unique car brands from the database"""
        cursor = self.connection_manager.cursor
        unique_cars = []

        try:
            # Query to get just the compatible_brands column
            cursor.execute("""
                SELECT DISTINCT compatible_brands 
                FROM parts 
                WHERE compatible_brands IS NOT NULL AND compatible_brands != ''
            """)

            # Get all results
            results = cursor.fetchall()
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

        except Exception as e:
            self.logger.error(f"Error fetching unique cars: {e}")

        return unique_cars  # Always return a list (empty if error)

    def get_all_cars(self):
        """Get all unique cars from the database with improved error handling"""
        cursor = self.connection_manager.cursor

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

            cursor.execute(query)
            results = cursor.fetchall()

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

            self.logger.info(f"Found {len(cars)} unique car entries in database")
            return cars

        except Exception as e:
            self.logger.error(f"Error fetching car data: {e}")
            # Return empty list rather than None to prevent cascading errors
            return []
