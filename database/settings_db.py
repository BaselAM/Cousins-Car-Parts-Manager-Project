# settings_db.py
import sqlite3
from pathlib import Path
from config import SETTINGS_DB_PATH

class SettingsDB:
    def __init__(self):
        self.db_path = SETTINGS_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.create_table()

    def connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.execute("PRAGMA foreign_keys = ON")

    def create_table(self):
        self.connect()
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS settings 
            (key TEXT PRIMARY KEY, value TEXT)
        ''')

        # Default settings for all possible keys
        defaults = [
            ('language', 'en'),
            ('rtl', 'false'),
            ('theme_index', '0'),
            ('backup_interval', '0'),
            ('low_stock_threshold', '10'),
            ('default_currency', 'ILS'),
            ('auto_restock', 'true'),
            ('primary_color', '#2980b9'),
            ('secondary_color', '#3498db'),
            # New Bartender settings with empty defaults
            ('bartender_labels_folder', ''),
            ('bartender_executable', '')
        ]

        self.conn.executemany(
            'INSERT OR IGNORE INTO settings VALUES (?, ?)',
            defaults
        )
        self.conn.commit()

    def save_setting(self, key, value):
        self.connect()
        self.conn.execute(
            'INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)',
            (key, value)
        )
        self.conn.commit()

    def get_setting(self, key, default=None):
        self.connect()
        cursor = self.conn.execute(
            'SELECT value FROM settings WHERE key=?',
            (key,)
        )
        result = cursor.fetchone()
        return result[0] if result else default

    def get_all_settings(self):
        self.connect()
        cursor = self.conn.execute('SELECT key, value FROM settings')
        return {row[0]: row[1] for row in cursor.fetchall()}

    def get_rtl_setting(self):
        return self.get_setting('rtl', 'false') == 'true'

    def close(self):
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None