"""
User database management for the Abu Mukh Car Parts system.
Handles user authentication, profile management, and security.
"""
import os
import sqlite3
import hashlib
import logging
from pathlib import Path

logger = logging.getLogger('UsersDB')


class UsersDB:
    """Manages user authentication and profile data."""

    def __init__(self, db_path=None):
        """Initialize the user database connection."""
        if db_path is None:
            # Use default path in the database directory
            db_dir = Path(__file__).parent
            db_path = db_dir / 'users.db'

        self.db_path = str(db_path)
        self.connection = None

        # Initialize the database
        self._connect()
        self._check_schema_version()
        self._create_tables()
        self._seed_initial_users()

    def _connect(self):
        """Establish connection to the database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
            logger.info(f"Connected to user database at {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise

    def _check_schema_version(self):
        """Check if database schema needs to be updated."""
        try:
            cursor = self.connection.cursor()

            # Check if users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            table_exists = cursor.fetchone() is not None

            if table_exists:
                # Check if password_hash column exists
                try:
                    cursor.execute("SELECT password_hash FROM users LIMIT 1")
                except sqlite3.OperationalError:
                    # Column doesn't exist, need to update schema
                    logger.warning("Outdated schema detected - upgrading users table...")

                    # Check if the old schema had 'password' column instead
                    try:
                        cursor.execute("SELECT password FROM users LIMIT 1")
                        # It has old 'password' column, perform migration
                        self._migrate_password_to_hash()
                    except sqlite3.OperationalError:
                        # No password column either, drop and recreate
                        logger.warning("Users table schema incompatible - recreating table...")
                        cursor.execute("DROP TABLE users")
                        self.connection.commit()
        except Exception as e:
            logger.error(f"Error checking schema version: {e}")

    def _migrate_password_to_hash(self):
        """Migrate from old password column to password_hash and salt."""
        try:
            cursor = self.connection.cursor()

            # Backup existing users
            cursor.execute("CREATE TABLE users_backup AS SELECT * FROM users")

            # Drop old table
            cursor.execute("DROP TABLE users")
            self.connection.commit()

            # New table will be created by _create_tables()
            logger.info("Backup created and old users table dropped for migration")
        except sqlite3.Error as e:
            logger.error(f"Error during schema migration: {e}")
            raise

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            cursor = self.connection.cursor()

            # Users table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                full_name TEXT,
                email TEXT,
                role TEXT,
                last_login TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
            ''')

            # User settings table for preferences
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                theme TEXT,
                language TEXT,
                rtl BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            ''')

            # Login history for security
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                success BOOLEAN,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
            ''')

            self.connection.commit()
            logger.info("Database tables created successfully")
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {e}")
            raise

    def _seed_initial_users(self):
        """Create initial users if the database is empty."""
        try:
            cursor = self.connection.cursor()

            # Check if users table is empty
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]

            if count == 0:
                # Create the three required users with password "123"
                initial_users = [
                    ("sabea", "Sabea Abu Mukh", "admin"),
                    ("fahed", "Fahed Abu Mukh", "manager"),
                    ("raed", "Raed Abu Mukh", "employee")
                ]

                for username, full_name, role in initial_users:
                    # Generate a random salt for each user
                    salt = os.urandom(32).hex()
                    # Hash the password "123" with the salt
                    password_hash = self._hash_password("123", salt)

                    cursor.execute(
                        "INSERT INTO users (username, password_hash, salt, full_name, role) VALUES (?, ?, ?, ?, ?)",
                        (username, password_hash, salt, full_name, role)
                    )

                    # Get the user_id of the inserted user
                    user_id = cursor.lastrowid

                    # Create default settings for the user
                    cursor.execute(
                        "INSERT INTO user_settings (user_id, theme, language) VALUES (?, ?, ?)",
                        (user_id, "classic", "en")
                    )

                self.connection.commit()
                logger.info("Initial users created: sabea, fahed, raed (password: 123)")
        except sqlite3.Error as e:
            logger.error(f"Error seeding initial users: {e}")
            raise

    def _hash_password(self, password, salt):
        """Hash a password with the given salt using SHA-256."""
        password_bytes = password.encode('utf-8')
        salt_bytes = bytes.fromhex(salt)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password_bytes, salt_bytes, 100000)
        return hash_obj.hex()


    def authenticate(self, username, password):
        """
        Authenticate a user with username and password.
        Returns user data if successful, None otherwise.
        """
        try:
            cursor = self.connection.cursor()

            # Get user record
            cursor.execute(
                "SELECT id, username, password_hash, salt, full_name, role FROM users WHERE username = ? AND is_active = 1",
                (username,)
            )
            user = cursor.fetchone()

            if not user:
                logger.warning(f"Authentication attempt for non-existent user: {username}")
                return None

            # Hash the provided password with the stored salt
            calculated_hash = self._hash_password(password, user['salt'])

            # Check if the hash matches
            if calculated_hash == user['password_hash']:
                # Update last login time
                cursor.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (user['id'],)
                )

                # Record successful login
                cursor.execute(
                    "INSERT INTO login_history (user_id, success) VALUES (?, 1)",
                    (user['id'],)
                )

                self.connection.commit()

                # Get user settings
                cursor.execute(
                    "SELECT theme, language, rtl FROM user_settings WHERE user_id = ?",
                    (user['id'],)
                )
                settings = cursor.fetchone() or {'theme': 'classic', 'language': 'en', 'rtl': 0}

                # Prepare user data to return
                user_data = {
                    'id': user['id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'role': user['role'],
                    'settings': {
                        'theme': settings['theme'],
                        'language': settings['language'],
                        'rtl': bool(settings['rtl'])
                    }
                }

                logger.info(f"User {username} authenticated successfully")
                return user_data
            else:
                # Record failed login attempt
                cursor.execute(
                    "INSERT INTO login_history (user_id, success) VALUES (?, 0)",
                    (user['id'],)
                )
                self.connection.commit()

                logger.warning(f"Failed authentication attempt for user: {username}")
                return None

        except sqlite3.Error as e:
            logger.error(f"Authentication error: {e}")
            return None

    def change_password(self, username, current_password, new_password):
        """
        Change a user's password after verifying the current password.
        Returns True if successful, False otherwise.
        """
        try:
            # First authenticate with current password
            user_data = self.authenticate(username, current_password)
            if not user_data:
                logger.warning(f"Password change failed: Invalid current password for {username}")
                return False, "Current password is incorrect"

            cursor = self.connection.cursor()

            # Get user's salt
            cursor.execute("SELECT id, salt FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if not user:
                return False, "User not found"

            # Use the same salt but generate new hash
            new_hash = self._hash_password(new_password, user['salt'])

            # Update the password
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_hash, user['id'])
            )

            self.connection.commit()
            logger.info(f"Password changed successfully for user: {username}")
            return True, "Password changed successfully"

        except sqlite3.Error as e:
            logger.error(f"Error changing password: {e}")
            return False, f"Database error: {str(e)}"

    def get_user_settings(self, username):
        """Get user settings for the specified username."""
        try:
            cursor = self.connection.cursor()

            cursor.execute("""
                SELECT s.theme, s.language, s.rtl 
                FROM user_settings s
                JOIN users u ON s.user_id = u.id
                WHERE u.username = ?
            """, (username,))

            settings = cursor.fetchone()

            if settings:
                return {
                    'theme': settings['theme'],
                    'language': settings['language'],
                    'rtl': bool(settings['rtl'])
                }
            else:
                return {'theme': 'classic', 'language': 'en', 'rtl': False}

        except sqlite3.Error as e:
            logger.error(f"Error retrieving user settings: {e}")
            return {'theme': 'classic', 'language': 'en', 'rtl': False}

    def update_user_settings(self, username, settings):
        """Update settings for the specified user."""
        try:
            cursor = self.connection.cursor()

            # Get user ID
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()

            if not user:
                return False, "User not found"

            # Update settings
            cursor.execute("""
                UPDATE user_settings 
                SET theme = ?, language = ?, rtl = ?
                WHERE user_id = ?
            """, (
                settings.get('theme', 'classic'),
                settings.get('language', 'en'),
                1 if settings.get('rtl', False) else 0,
                user['id']
            ))

            self.connection.commit()
            return True, "Settings updated successfully"

        except sqlite3.Error as e:
            logger.error(f"Error updating user settings: {e}")
            return False, f"Database error: {str(e)}"

    def close(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Database connection closed")