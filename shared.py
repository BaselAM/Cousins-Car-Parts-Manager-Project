from pathlib import Path

# Define SCRIPT_DIR as the directory where this file resides.
SCRIPT_DIR = Path(__file__).resolve().parent

DB_DIR = SCRIPT_DIR / "database"
SETTINGS_DB = DB_DIR / "settings.db"
PARTS_DB = DB_DIR / "car_parts.db"