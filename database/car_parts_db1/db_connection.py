"""Database connection management module"""
import mysql.connector
from mysql.connector import pooling
import threading
import time
import logging


class DatabaseConnectionError(Exception):
    """Exception raised for database connection issues"""
    pass


class ConnectionManager:
    """Manages database connections with connection pooling"""

    def __init__(self, config, logger=None, pool_settings=None):
        """Initialize with database config and optional pool settings

        Args:
            config (dict): Database connection configuration
            logger (Logger, optional): Logger instance
            pool_settings (dict, optional): Connection pool settings
        """
        self.logger = logger or logging.getLogger('database.connection')
        self.config = config
        self.pool_settings = pool_settings or {}

        # Thread-local storage for connections
        self.local = threading.local()
        self.lock = threading.RLock()

        # Create connection pool
        self.pool = self._create_connection_pool()

    def _create_connection_pool(self):
        """Create a connection pool with configurable settings"""
        try:
            # Get pool configuration from pool_settings
            pool_config = {
                'pool_name': self.pool_settings.get('pool_name', 'car_parts_pool'),
                'pool_size': self.pool_settings.get('pool_size', 10),
                'pool_reset_session': self.pool_settings.get('pool_reset_session', True),
                'connect_timeout': self.pool_settings.get('connect_timeout', 10),
                'use_pure': True,  # Use pure Python implementation for thread safety
            }

            # Merge with the database connection config
            # We need to create a copy to avoid modifying the original
            connection_config = self.config.copy()

            # Create the pool config by combining connection settings and pool settings
            mysql_pool_config = {**connection_config}

            # Add the pool-specific settings
            for key, value in pool_config.items():
                mysql_pool_config[key] = value

            # Create the pool
            pool = mysql.connector.pooling.MySQLConnectionPool(**mysql_pool_config)
            self.logger.info(
                f"Created connection pool '{pool_config['pool_name']}' with size {pool_config['pool_size']}")
            return pool

        except mysql.connector.Error as e:
            self.logger.error(f"Error creating connection pool: {str(e)}")
            raise DatabaseConnectionError(f"Failed to create connection pool: {str(e)}")

    @property
    def connection(self):
        """Get the current thread's database connection"""
        self.ensure_connection()
        return self.local.conn

    @property
    def cursor(self):
        """Get the current thread's database cursor"""
        self.ensure_connection()
        return self.local.cursor

    def ensure_connection(self):
        """Ensure this thread has a valid connection"""
        with self.lock:
            # Check if we need a new connection
            needs_new_connection = False

            if not hasattr(self.local, 'conn') or self.local.conn is None:
                needs_new_connection = True
            else:
                try:
                    # Test connection with minimal impact query
                    self.local.cursor.execute("SELECT 1")
                    self.local.cursor.fetchall()
                except Exception as e:
                    self.logger.debug(f"Connection check failed: {e}, reconnecting")
                    needs_new_connection = True

            # If connection is OK, just return
            if not needs_new_connection:
                return

            # We need a new connection - try up to 3 times
            max_retries = 3
            retry_count = 0

            while retry_count < max_retries:
                try:
                    # Close the old connection
                    self._close_connection()

                    # Get a new connection from the pool
                    self.local.conn = self.pool.get_connection()
                    self.local.cursor = self.local.conn.cursor(dictionary=True)
                    self.local.in_transaction = False

                    thread_id = threading.get_ident()
                    self.logger.debug(f"Thread {thread_id}: New database connection established")
                    return

                except Exception as e:
                    retry_count += 1
                    self.logger.warning(f"Connection attempt {retry_count}/{max_retries} failed: {e}")
                    time.sleep(0.5)  # Add a small delay between retries

            # All retries failed - last attempt with direct connection
            try:
                # Direct connection (not from pool)
                self.local.conn = mysql.connector.connect(**self.config)
                self.local.cursor = self.local.conn.cursor(dictionary=True)
                self.local.in_transaction = False

                thread_id = threading.get_ident()
                self.logger.warning(f"Thread {thread_id}: Using direct database connection after pool failures")
            except Exception as direct_error:
                self.logger.error(f"All connection attempts failed: {direct_error}")
                raise DatabaseConnectionError("Unable to establish database connection") from direct_error

    def _close_connection(self):
        """Close the connection for the current thread"""
        if hasattr(self.local, 'cursor') and self.local.cursor:
            try:
                self.local.cursor.close()
            except Exception as e:
                self.logger.warning(f"Error closing cursor: {e}")
            self.local.cursor = None

        if hasattr(self.local, 'conn') and self.local.conn:
            try:
                # Check if there's an active transaction
                if hasattr(self.local, 'in_transaction') and self.local.in_transaction:
                    try:
                        self.local.conn.rollback()
                        self.logger.warning("Rolling back transaction during connection close")
                    except Exception as e:
                        self.logger.warning(f"Error rolling back transaction during close: {e}")

                # Close the connection
                self.local.conn.close()
                self.local.conn = None
                self.local.in_transaction = False
            except Exception as e:
                self.logger.warning(f"Error closing connection: {e}")
                self.local.conn = None
                self.local.in_transaction = False