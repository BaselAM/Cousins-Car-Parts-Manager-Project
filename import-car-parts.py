#!/usr/bin/env python3
"""
Complete car parts database import system.
Features:
- Multiple car brands and models per product
- Specialized columns for year ranges, drive types, and engine info
- Comprehensive category detection
- Detailed metadata extraction
"""

import os
import sys
import re
import time
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('import_script')

# Expanded category mappings with more detailed part types
CATEGORY_MAPPINGS = {
    'Air Filter': ['פ.אויר'],
    'Oil Filter': ['פ.שמן'],
    'AC Filter': ['פ.מזגן'],
    'Fuel Filter': ['פ.סולר', 'פ.דלק'],
    'Brake Discs': ['דסקיות'],
    'Brake Plates': ['צלחות'],
    'Shock Absorber': ['בולם'],
    'Drive Shaft': ['ציריה'],
    'Radiator': ['רדיאטור'],
    'Water Pump': ['מ.מים'],
    'Timing Belt Kit': ['טיימינג', 'שרשרת טיימינג', 'תזמון', 'סט טיימינג', 'קיט טיימינג'],
    'Spark Plugs': ['פלגים'],
    'Suspension Parts': ['מ.מייצב', 'ג.מייצב', 'משולש', 'ת.משולש', 'בוקסה', 'ז.מתלה'],
    'Coolant Reservoir': ['מיכל עיבוי', 'כוהל'],
    'Clutch Kit': ['מצמד', 'סט מצמד'],
    'Gasket': ['אטם'],
    'Belts': ['רצועה', 'רצועות', 'סט רצועות'],
    'Hoses': ['צינור'],
    'Bearings': ['מיסב'],
    'Engine Mount': ['ת.מנוע'],
    'Steering Parts': ['הגה', 'ז.הגה', 'קצה הגה', 'מסרק הגה', 'זרוע הגה'],
    'Sensors': ['חיישן', 'סליל', 'יוניט', 'סנסור', 'ח.חמצן', 'ח.קראנק', 'ח.בלם'],
    'Brake Pads': ['רפידות'],
    'Thermostat': ['טרמוסטט', 'פלנץ טרמוסטט'],
    'Ignition System': ['ח.הצתה', 'ת.הצתה', 'מערכת הצתה', 'קויל'],
    'Oil Cooler': ['קולר שמן'],
    'Gear Parts': ['ת.גיר', 'תושבת גיר', 'פ.גיר', 'קולר גיר'],
    'Wheel Hub': ['נאבה'],
    'Brake Drums': ['דרם'],
    'Stabilizer Bar': ['מוט מייצב'],
    'Cooling System': ['מאוורר', 'מאורר', 'ראלי'],
    'Tensioner': ['מותח'],
    'Crankshaft': ['ח.קראנק'],
    'Seal': ['מחזיר שמן', 'פעמון'],
    'Battery': ['פ.סוללה'],
    'Turbo Parts': ['צ.טורבו', 'אנטרקולר'],
    'Transmission Mount': ['ת.גיר'],
    'Fuel Pump': ['משאבת דלק'],
    'Other Parts': []
}

# Pattern for extracting years and engine sizes
YEAR_PATTERN = re.compile(r'מ(\d\d)')  # מ + 2 digits for year (e.g., מ13 = 2013)
YEAR_RANGE_PATTERN = re.compile(r'(\d\d)-(\d\d)')  # e.g., 09-12
TILL_YEAR_PATTERN = re.compile(r'עד (\d\d)')  # עד + 2 digits for "till year" (e.g., עד 12)
ENGINE_DISPLACEMENT_PATTERN = re.compile(r'\d\.\d')  # e.g., 1.6, 2.0, etc.
DRIVE_TYPE_PATTERN = re.compile(r'4x4|4x2')  # 4x4 or 4x2 drive types
SIDE_PATTERN = re.compile(r'ימין|שמאל')  # Right or Left side
POSITION_PATTERN = re.compile(r'קדמי|אחורי')  # Front or Back position
ENGINE_TYPE_PATTERN = re.compile(r'דיזל|בנזין|היברידי|היבריד')  # Diesel, Gasoline, Hybrid

# Significantly expanded car brand mappings
CAR_BRAND_MAPPINGS = {
    'Mazda': ['מזדה', 'BT-50', 'BT50', 'B2500', 'לנטיס', 'למטיס', '626'],
    'Skoda': ['אוקטביה', 'סקודה', 'פביה', 'סופרב', 'רומסטר', 'קודיאק', 'רפיד', 'יטי', 'קארוק'],
    'Hyundai': ['יונדאי', 'I10', 'I20', 'I25', 'I30', 'I35', 'I800', 'IX35', 'איוניק', 'טוסון',
                'סנטה פה', 'אקסנט', 'גטס', 'אלנטרה', 'סונטה', 'H350', 'וולסטר', 'סטאריה'],
    'Kia': ['קיה', 'ספורטאג', 'סיד', 'ריו', 'פיקנטו', 'קרניבל', 'סורנטו', 'נירו', 'סטוניק', 'סטאריה'],
    'Toyota': ['טויוטה', 'קורולה', 'יאריס', 'ראב 4', 'לנדקרוזר', 'קאמרי', 'היילקס', 'אוונסיס',
               'ויגו', 'CHR', 'ורסו', 'הייס', 'פריוס', 'אוריס', 'קינג'],
    'Volkswagen': ['פולו', 'גולף', 'טיגואן', 'פסאט', 'קאדי', 'טווארג', 'ג\'טה', 'גטה', 'T5', 'T6', 'אמארוק', 'TGE'],
    'Mercedes': ['מרצדס', 'ויטו', 'ויאנו', 'ספרינטר', 'CLA', 'GLA', 'GLE', 'קלאס', 'ECLASS'],
    'BMW': ['ב.מ.וו', 'סדרה 1', 'סדרה 2', 'סדרה 3', 'סדרה 5', 'סדרה 7', 'X1', 'X3', 'X5', 'X6'],
    'Peugeot': ['פיגו', '107', '207', '208', '301', '307', '308', '3008', '5008', '508'],
    'Citroen': ['סיטרואן', 'ברלינגו', 'C1', 'C3', 'C4', 'C5', 'פיקסו', 'גמפי'],
    'Renault': ['רנו', 'קליאו', 'מגאן', 'פלואנס', 'קנגו', 'גרנד קופה', 'קפצור', 'טראפיק'],
    'Ford': ['פורד', 'פוקוס', 'פיאסטה', 'מונדיאו', 'טרנזיט', 'אדג'],
    'Seat': ['סיאט', 'איביזה', 'לאון', 'אטקה', 'ארונה', 'קופרה', 'פורמנטור'],
    'Mitsubishi': ['מיצובישי', 'לנסר', 'אאוטלנדר', 'פגירו', 'טרייטון', 'אווטלנדר', 'גרנדיס',
                   'אקליפס', 'ס.לנסר', 'מגנום'],
    'Suzuki': ['סוזוקי', 'ויטרה', 'ליאנה', 'סוויפט', 'בלינו', 'איגניס', 'SX4', 'ספלאש',
               'קרוסאובר', 'ג.ויטרה', 'בלנו', 'באלנו', 'ג.ויטרה', 'גימיני'],
    'Honda': ['הונדה', 'סיויק', 'אקורד', 'CRV', 'FRV', 'HRV'],
    'Nissan': ['ניסאן', 'קשקאי', 'גוק', 'אקסטרייל', 'מיקרה', 'טידה', 'סנטרה', 'נבארה',
               'NV200', 'אלמרה', 'נוט', 'NV300', 'מורנו'],
    'Chevrolet': ['שברולט', 'קרוז', 'ספארק', 'מליבו', 'אוואו', 'סוניק', 'קפטיבה', 'טראוורס',
                  'טרייל בלייזר', 'סילברדו', 'אקווינוקס', 'אפלנדר', 'לה קרוס', 'אימפלה'],
    'Daihatsu': ['דייהטסו', 'סיריון', 'טריוס'],
    'Audi': ['אודי', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'Q2', 'Q3', 'Q5', 'Q7', 'Q8', 'RS', 'RS3', 'RS7', 'S3'],
    'Fiat': ['פיאט', 'פונטו', 'דובלו', 'פנדה', '500', 'טיפו', 'דוקטו', 'פ.פונטו', 'ג.פונטו',
             'בוקסר', 'בראבו', 'קובו', 'טיפו'],
    'Opel': ['אופל', 'אסטרה', 'קורסה', 'אינסנגניה', 'מוקה', 'אינסגניה'],
    'Subaru': ['סובארו', 'B3', 'B4', 'XV', 'פורסטר', 'אמפרזה', 'אמפריזה', 'לגאסי'],
    'Isuzu': ['איסוזו', 'דימקס', 'טרופר', 'טרנו', 'וינר'],
    'Volvo': ['וולוו', 'S40', 'S60', 'S70', 'S80', 'XC60', 'XC40'],
    'Jeep': ['ג\'יפ', 'גרנד צירוקי', 'רינגלר', 'צירוקי'],
    'Dodge': ['דודג', 'ראם'],
    'MG': ['MG', 'MG350', 'ZS'],
    'Cadillac': ['קדילק', 'קאדילק', 'XT5'],
    'Chery': ['צ\'רי', 'CHERY', 'צירי'],
    'GMC': ['GMC'],
    'Alfa Romeo': ['אלפא', 'מיטו', 'סטלביו'],
    'Iveco': ['איווקו'],
    'Daewoo': ['דאו'],
    'Lexus': ['לקסוס'],
    'Porsche': ['פורשה', 'פורש'],
    'Ssangyong': ['סאנגיונג', 'סאניונג', 'האנטר', 'הנטר'],
    'BYD': ['BYD'],
    'Tesla': ['טסלה'],
    'Jaguar': ['יגואר'],
    'Land Rover': ['לנד רובר', 'ריינגר'],
    'Mini': ['מיני', 'מיניקופר'],
    'Geely': ['ג\'ילי', 'גילי', 'גיאומטרי'],
    'GAZ': ['גאז'],
    'Dacia': ['דאציה', 'דאסטר'],
    'Lada': ['לאדה'],
    'Other': []
}

# Expanded car model mappings
CAR_MODEL_MAPPINGS = {
    'Mazda': {
        '2': ['מזדה 2'],
        '3': ['מזדה 3'],
        '5': ['מזדה 5'],
        '6': ['מזדה 6'],
        'CX-5': ['CX5'],
        'CX-30': ['CX30', 'CX-30'],
        'BT-50': ['BT-50', 'BT50'],
        'B2500': ['B2500'],
        'Lantis': ['לנטיס', 'למטיס'],
        '626': ['626']
    },
    'Skoda': {
        'Octavia': ['אוקטביה'],
        'Fabia': ['פביה'],
        'Superb': ['סופרב'],
        'Roomster': ['רומסטר'],
        'Kodiaq': ['קודיאק'],
        'Rapid': ['רפיד'],
        'Yeti': ['יטי'],
        'Karoq': ['קארוק']
    },
    'Hyundai': {
        'i10': ['I10'],
        'i20': ['I20'],
        'i25': ['I25'],
        'i30': ['I30'],
        'i35': ['I35'],
        'i800': ['I800'],
        'ix35': ['IX35'],
        'Tucson': ['טוסון'],
        'Santa Fe': ['סנטה פה'],
        'Accent': ['אקסנט'],
        'Getz': ['גטס'],
        'Ioniq': ['איוניק'],
        'Elantra': ['אלנטרה'],
        'Sonata': ['סונטה'],
        'Kona': ['קונה'],
        'H350': ['H350'],
        'Veloster': ['וולסטר'],
        'Staria': ['סטאריה']
    },
    'Toyota': {
        'Corolla': ['קורולה'],
        'Yaris': ['יאריס'],
        'RAV4': ['ראב 4'],
        'Land Cruiser': ['לנדקרוזר'],
        'Camry': ['קאמרי'],
        'Hilux': ['היילקס'],
        'Vigo': ['ויגו'],
        'Avensis': ['אוונסיס'],
        'CHR': ['CHR'],
        'Verso': ['ורסו'],
        'Auris': ['אוריס'],
        'Prius': ['פריוס'],
        'Hiace': ['הייס'],
        'King': ['קינג']
    },
    'Nissan': {
        'Qashqai': ['קשקאי'],
        'Juke': ['גוק'],
        'X-Trail': ['אקסטרייל'],
        'Micra': ['מיקרה'],
        'Tiida': ['טידה'],
        'Sentra': ['סנטרה'],
        'Navara': ['נבארה'],
        'NV200': ['NV200'],
        'Almera': ['אלמרה'],
        'Note': ['נוט'],
        'NV300': ['NV300'],
        'Murano': ['מורנו']
    },
    'Kia': {
        'Sportage': ['ספורטאג'],
        'Ceed': ['סיד'],
        'Rio': ['ריו'],
        'Picanto': ['פיקנטו'],
        'Carnival': ['קרניבל'],
        'Sorento': ['סורנטו'],
        'Niro': ['נירו'],
        'Stonic': ['סטוניק'],
        'Forte': ['פורטה'],
        'Optima': ['אופטימה']
    },
    'Volkswagen': {
        'Polo': ['פולו'],
        'Golf': ['גולף'],
        'Tiguan': ['טיגואן'],
        'Passat': ['פסאט'],
        'Caddy': ['קאדי'],
        'Touareg': ['טווארג'],
        'Jetta': ['ג\'טה', 'גטה'],
        'Transporter': ['T5', 'T6'],
        'Amarok': ['אמארוק'],
        'TGE': ['TGE']
    },
    'Mitsubishi': {
        'Lancer': ['לנסר', 'ס.לנסר'],
        'Outlander': ['אאוטלנדר', 'אווטלנדר'],
        'Pajero': ['פגירו', 'פג\'רו'],
        'Triton': ['טרייטון'],
        'Grandis': ['גרנדיס'],
        'Eclipse': ['אקליפס'],
        'Magnum': ['מגנום']
    },
    'Suzuki': {
        'Vitara': ['ויטרה', 'ג.ויטרה'],
        'Baleno': ['בלינו', 'בלנו', 'באלנו'],
        'Swift': ['סוויפט'],
        'Ignis': ['איגניס'],
        'SX4': ['SX4', 'קרוסאובר'],
        'Splash': ['ספלאש'],
        'Grand Vitara': ['ג.ויטרה'],
        'Jimny': ['גימיני']
    },
    'Ford': {
        'Focus': ['פוקוס'],
        'Fiesta': ['פיאסטה'],
        'Mondeo': ['מונדיאו'],
        'Transit': ['טרנזיט'],
        'Edge': ['אדג']
    },
    'Isuzu': {
        'D-Max': ['דימקס'],
        'Trooper': ['טרופר'],
        'Turbo': ['טרנו', 'וינר']
    },
    'Subaru': {
        'Impreza': ['אמפרזה', 'אמפריזה'],
        'Legacy': ['לגאסי'],
        'Forester': ['פורסטר'],
        'XV': ['XV'],
        'B3': ['B3'],
        'B4': ['B4']
    }
}

# Engine codes mapping
ENGINE_CODE_MAPPINGS = {
    'CBZ': 'Volkswagen/Skoda 1.2 TSI',
    'CJZ': 'Volkswagen/Skoda 1.2 TSI',
    'BSE': 'Volkswagen/Skoda 1.6',
    'BTS': 'Volkswagen/Skoda 1.6',
    'CAX': 'Volkswagen/Skoda 1.4 TSI',
    'CAV': 'Volkswagen/Skoda 1.4 TSI',
    'CDA': 'Volkswagen/Skoda 1.8 TSI',
    'CJS': 'Volkswagen/Skoda 1.8 TSI',
    'BLR': 'Volkswagen/Skoda 2.0 FSI',
    'BMY': 'Volkswagen/Skoda 1.4 TSI',
    'CJJ': 'Volkswagen/Skoda 1.4',
    'CNC': 'Volkswagen/Skoda 2.0 TSI',
    'CJX': 'Volkswagen/Skoda 2.0 TSI',
    'BLX': 'Volkswagen/Skoda 2.0 FSI',
    'BLY': 'Volkswagen/Skoda 2.0 FSI',
    'AXW': 'Volkswagen/Skoda 2.0 FSI',
    'CRM': 'Volkswagen/Skoda Diesel',
    'TDI': 'Volkswagen/Skoda Diesel'
}


class DatabaseManager:
    """Database manager for car parts database"""

    def __init__(self, db_path=None):
        """
        Initialize the database manager.

        Args:
            db_path (str, optional): Path to the database file
        """
        # If no db_path provided, use the default location
        if db_path is None:
            # Use current directory as default
            self.db_path = "database/car_parts.db"
        else:
            self.db_path = db_path

        self.conn = None
        self.cursor = None

        # Connect to the database
        self.connect()

    def connect(self):
        """Connect to the database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database at {self.db_path}")

            # Check if the table exists and has the needed columns
            self.check_and_update_schema()

        except sqlite3.Error as e:
            logger.error(f"Database connection error: {str(e)}")
            raise

    def check_and_update_schema(self):
        """Check if the table exists and has the needed columns"""
        try:
            # Check if parts table exists
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parts'")
            table_exists = self.cursor.fetchone() is not None

            if not table_exists:
                # Create table with enhanced schema including parcode instead of id
                self.cursor.execute('''
                CREATE TABLE parts (
                    parcode INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER DEFAULT 0,
                    price REAL DEFAULT 0.0,
                    compatible_brands TEXT,
                    compatible_models TEXT,
                    model_years TEXT,
                    drive_type TEXT,
                    engine_info TEXT,
                    position TEXT,
                    side TEXT,
                    engine_type TEXT,
                    last_updated TIMESTAMP DEFAULT (datetime('now','localtime'))
                )
                ''')
                self.conn.commit()
                logger.info("Created new parts table with enhanced schema")
                return

            # Rest of your existing code...
        except sqlite3.Error as e:
            logger.error(f"Error checking/updating schema: {str(e)}")
            raise

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def add_part(self, category, product_name, quantity=0, price=0.0, **kwargs):
        """Add a new part to the database."""
        try:
            from datetime import datetime

            # Build the column and value lists
            columns = ['category', 'product_name', 'quantity', 'price']
            values = [category, product_name, quantity, price]

            for key, value in kwargs.items():
                columns.append(key)
                values.append(value)

            # Add current timestamp explicitly
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            columns.append('last_updated')
            values.append(current_time)

            # Build the SQL query
            column_str = ', '.join(columns)
            placeholders = ', '.join(['?'] * len(values))

            self.cursor.execute(f'''
            INSERT INTO parts 
            ({column_str})
            VALUES ({placeholders})
            ''', values)

            self.conn.commit()
            return self.cursor.lastrowid

        except sqlite3.Error as e:
            logger.error(f"Error adding part: {str(e)}")
            return None

    def update_part(self, part_id, **kwargs):
        """
        Update a part in the database.

        Args:
            part_id (int): ID of the part to update
            **kwargs: Fields to update and their values

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not kwargs:
                return False

            set_clause = ', '.join([f"{k} = ?" for k in kwargs.keys()])
            set_clause += ", last_updated = CURRENT_TIMESTAMP"

            values = list(kwargs.values()) + [part_id]

            self.cursor.execute(f'''
            UPDATE parts 
            SET {set_clause}
            WHERE id = ?
            ''', values)

            self.conn.commit()
            return self.cursor.rowcount > 0

        except sqlite3.Error as e:
            logger.error(f"Error updating part {part_id}: {str(e)}")
            return False

    def get_all_parts(self):
        """
        Get all parts from the database.

        Returns:
            list: List of parts
        """
        try:
            self.cursor.execute("SELECT * FROM parts ORDER BY id")
            return self.cursor.fetchall()

        except sqlite3.Error as e:
            logger.error(f"Error getting parts: {str(e)}")
            return []

    def count_parts(self):
        """
        Count the number of parts in the database.

        Returns:
            int: Number of parts
        """
        try:
            self.cursor.execute("SELECT COUNT(*) FROM parts")
            return self.cursor.fetchone()[0]

        except sqlite3.Error as e:
            logger.error(f"Error counting parts: {str(e)}")
            return 0

    def search_parts(self, search_term):
        """
        Search for parts in the database.

        Args:
            search_term (str): Search term

        Returns:
            list: List of matching parts
        """
        try:
            query_columns = [
                'product_name', 'category', 'compatible_brands', 'compatible_models',
                'model_years', 'drive_type', 'engine_info', 'position', 'side', 'engine_type'
            ]

            conditions = " OR ".join([f"{col} LIKE ?" for col in query_columns])
            params = [f'%{search_term}%'] * len(query_columns)

            self.cursor.execute(f"SELECT * FROM parts WHERE {conditions}", params)

            return self.cursor.fetchall()

        except sqlite3.Error as e:
            logger.error(f"Error searching parts: {str(e)}")
            return []

    def get_column_names(self):
        """
        Get the column names of the parts table.

        Returns:
            list: List of column names
        """
        try:
            self.cursor.execute("PRAGMA table_info(parts)")
            return [row[1] for row in self.cursor.fetchall()]

        except sqlite3.Error as e:
            logger.error(f"Error getting column names: {str(e)}")
            return []

    def begin_transaction(self):
        """Begin a transaction"""
        self.conn.execute("BEGIN TRANSACTION")

    def commit_transaction(self):
        """Commit the current transaction"""
        self.conn.commit()

    def rollback_transaction(self):
        """Roll back the current transaction"""
        self.conn.rollback()


def determine_category(product_name):
    """
    Determine the category of a product based on its name.

    Args:
        product_name (str): The product name in Hebrew

    Returns:
        str: The English category name
    """
    for category, terms in CATEGORY_MAPPINGS.items():
        for term in terms:
            if term in product_name:
                return category

    return 'Other Parts'


def find_all_car_brands(product_name):
    """Find all car brands mentioned in the product name."""
    brands = []
    found_brands = set()  # Track which brands we've already found

    # Check for brands
    for brand_id, terms in CAR_BRAND_MAPPINGS.items():
        for term in terms:
            if term in product_name and brand_id != 'Other' and brand_id not in found_brands:
                brands.append((brand_id, term))
                found_brands.add(brand_id)  # Add to the set so we don't duplicate

    # If no brands found, return "Other"
    if not brands:
        brands.append(('Other', 'Other'))

    return brands


def find_all_car_models(product_name, brands):
    """Find all car models mentioned in the product name for the given brands."""
    models = []
    found_models = set()  # Track which brand:model pairs we've already found

    # Check for specific model names for each brand
    for brand_id, _ in brands:
        if brand_id in CAR_MODEL_MAPPINGS:
            for model_id, model_terms in CAR_MODEL_MAPPINGS[brand_id].items():
                for term in model_terms:
                    if term in product_name and (brand_id, model_id) not in found_models:
                        models.append((brand_id, model_id, term))
                        found_models.add((brand_id, model_id))  # Add to set to prevent duplicates

    # If no models found, use generic model
    if not models and brands:
        models.append((brands[0][0], "Generic Model", "Generic"))

    return models


def extract_model_years(product_name, brand_model_pairs=None):
    """
    Extract model years for all mentioned models in the product name.
    """
    years = {}

    if not brand_model_pairs:
        # No models identified, just extract general years
        general_years = []
        for match in YEAR_PATTERN.findall(product_name):
            general_years.append(f"From 20{match}")
        for match in YEAR_RANGE_PATTERN.findall(product_name):
            general_years.append(f"20{match[0]}-20{match[1]}")
        for match in TILL_YEAR_PATTERN.findall(product_name):
            general_years.append(f"Until 20{match}")

        if general_years:
            years['general'] = general_years
        return years

    # For each model, scan the entire product name for nearby year patterns
    for brand, model, term in brand_model_pairs:
        # Find all year patterns in the product name
        year_matches = [(m.group(1), m.start(), m.end()) for m in re.finditer(YEAR_PATTERN, product_name)]
        range_matches = [(f"{m.group(1)}-{m.group(2)}", m.start(), m.end()) for m in
                         re.finditer(YEAR_RANGE_PATTERN, product_name)]
        till_matches = [(m.group(1), m.start(), m.end()) for m in re.finditer(TILL_YEAR_PATTERN, product_name)]

        # Find all occurrences of this model term
        model_positions = []
        start_pos = 0
        while True:
            pos = product_name.find(term, start_pos)
            if pos < 0:
                break
            model_positions.append((pos, pos + len(term)))
            start_pos = pos + 1

        # Find the closest year pattern to each model mention
        for model_start, model_end in model_positions:
            closest_year = None
            closest_distance = float('inf')
            year_value = None

            # Check each year pattern for proximity to this model mention
            for year, start, end in year_matches:
                # Calculate distance (prioritize years after model mentions)
                if start > model_end:
                    distance = start - model_end  # Year is after model
                else:
                    distance = model_start - end  # Year is before model

                if 0 <= distance < closest_distance and distance < 15:  # Only consider if reasonably close
                    closest_distance = distance
                    closest_year = year
                    year_value = f"From 20{year}"

            # Check range patterns
            for year_range, start, end in range_matches:
                if start > model_end:
                    distance = start - model_end
                else:
                    distance = model_start - end

                if 0 <= distance < closest_distance and distance < 15:
                    closest_distance = distance
                    closest_year = year_range
                    year_value = f"20{year_range.split('-')[0]}-20{year_range.split('-')[1]}"

            # Check till patterns
            for year, start, end in till_matches:
                if start > model_end:
                    distance = start - model_end
                else:
                    distance = model_start - end

                if 0 <= distance < closest_distance and distance < 15:
                    closest_distance = distance
                    closest_year = year
                    year_value = f"Until 20{year}"

            # Store the year for this model if found
            if closest_year is not None:
                years[(brand, model)] = year_value

    return years


def extract_drive_type(product_name):
    """
    Extract drive type information (4x4, 4x2) from the product name.

    Args:
        product_name (str): The product name in Hebrew

    Returns:
        str: Drive type or None if not found
    """
    drive_match = DRIVE_TYPE_PATTERN.search(product_name)
    if drive_match:
        return drive_match.group(0)
    return None


def extract_engine_info(product_name):
    """
    Extract engine information from the product name.

    Args:
        product_name (str): The product name in Hebrew

    Returns:
        str: Engine info or None if not found
    """
    engine_info = []

    # Look for engine displacement (e.g., 1.6, 2.0)
    displacement_matches = ENGINE_DISPLACEMENT_PATTERN.findall(product_name)
    if displacement_matches:
        engine_info.extend([f"{match}L" for match in displacement_matches])

    # Look for engine codes (e.g., CBZ, CJS)
    for code, description in ENGINE_CODE_MAPPINGS.items():
        if code in product_name:
            engine_info.append(f"{code} ({description})")

    return ", ".join(engine_info) if engine_info else None


def extract_position(product_name):
    """
    Extract position information (front, rear) from the product name.

    Args:
        product_name (str): The product name in Hebrew

    Returns:
        str: Position or None if not found
    """
    position_match = POSITION_PATTERN.search(product_name)
    if position_match:
        position = position_match.group(0)
        if position == "קדמי":
            return "Front"
        elif position == "אחורי":
            return "Rear"
    return None


def extract_side(product_name):
    """
    Extract side information (right, left) from the product name.

    Args:
        product_name (str): The product name in Hebrew

    Returns:
        str: Side or None if not found
    """
    side_match = SIDE_PATTERN.search(product_name)
    if side_match:
        side = side_match.group(0)
        if side == "ימין":
            return "Right"
        elif side == "שמאל":
            return "Left"
    return None


def extract_engine_type(product_name):
    """
    Extract engine type (diesel, gasoline, hybrid) from the product name.

    Args:
        product_name (str): The product name in Hebrew

    Returns:
        str: Engine type or None if not found
    """
    type_match = ENGINE_TYPE_PATTERN.search(product_name)
    if type_match:
        engine_type = type_match.group(0)
        if engine_type == "דיזל":
            return "Diesel"
        elif engine_type == "בנזין":
            return "Gasoline"
        elif engine_type in ["היברידי", "היבריד"]:
            return "Hybrid"

    # Also check for diesel indicators in engine codes
    if "TDI" in product_name or "CDI" in product_name:
        return "Diesel"

    return None


def parse_product_list(filename):
    """
    Parse the product list and extract detailed product information.

    Args:
        filename (str): Path to the product list file

    Returns:
        list: List of dictionaries with product information
    """
    products = []

    try:
        with open(filename, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue

                product_name = line

                # Basic product classification
                category = determine_category(product_name)

                # Find all car brands mentioned in the product name
                brands = find_all_car_brands(product_name)

                # Find all models for the brands
                model_pairs = find_all_car_models(product_name, brands)

                # Extract more detailed metadata
                drive_type = extract_drive_type(product_name)
                engine_info = extract_engine_info(product_name)
                position = extract_position(product_name)
                side = extract_side(product_name)
                engine_type = extract_engine_type(product_name)

                # Extract model years, associating with specific models when possible
                model_years_dict = extract_model_years(product_name, model_pairs)

                # Format model years for database storage
                if 'general' in model_years_dict:
                    # General year info (not specific to a model)
                    model_years = ', '.join(model_years_dict['general'])
                else:
                    # Model-specific years
                    model_years_items = []
                    for (brand, model), years in model_years_dict.items():
                        model_years_items.append(f"{brand} {model}: {years}")
                    model_years = ', '.join(model_years_items) if model_years_items else None

                # Create lists of compatible brands and models
                compatible_brands = ','.join([brand[0] for brand in brands])
                compatible_models = ','.join([f"{model[0]}:{model[1]}" for model in model_pairs])

                # Create the product dictionary with all metadata
                product = {
                    'product_name': product_name,
                    'category': category,
                    'compatible_brands': compatible_brands,
                    'compatible_models': compatible_models,
                    'model_years': model_years,
                    'drive_type': drive_type,
                    'engine_info': engine_info,
                    'position': position,
                    'side': side,
                    'engine_type': engine_type
                }

                products.append(product)

        return products

    except Exception as e:
        logger.error(f"Error parsing product list: {str(e)}")
        return []


def import_products_to_db(db, products):
    """
    Import products to the database.

    Args:
        db (DatabaseManager): Database manager instance
        products (list): List of product dictionaries

    Returns:
        int: Number of products successfully imported
    """
    success_count = 0
    error_count = 0

    for i, product in enumerate(products):
        try:
            # Debug output for every 100th product
            if i % 100 == 0:
                logger.info(f"Processing product {i + 1}/{len(products)}: {product['product_name']}")
                logger.info(f"  Category: {product['category']}")
                logger.info(f"  Compatible Brands: {product['compatible_brands']}")
                logger.info(f"  Compatible Models: {product['compatible_models']}")

                if product['model_years']:
                    logger.info(f"  Model Years: {product['model_years']}")
                if product['drive_type']:
                    logger.info(f"  Drive Type: {product['drive_type']}")
                if product['engine_info']:
                    logger.info(f"  Engine Info: {product['engine_info']}")
                if product['position']:
                    logger.info(f"  Position: {product['position']}")
                if product['side']:
                    logger.info(f"  Side: {product['side']}")
                if product['engine_type']:
                    logger.info(f"  Engine Type: {product['engine_type']}")

            # Add the product to the database
            result = db.add_part(
                category=product['category'],
                product_name=product['product_name'],
                quantity=0,
                price=0.0,
                compatible_brands=product['compatible_brands'],
                compatible_models=product['compatible_models'],
                model_years=product['model_years'],
                drive_type=product['drive_type'],
                engine_info=product['engine_info'],
                position=product['position'],
                side=product['side'],
                engine_type=product['engine_type']
            )

            if result:
                success_count += 1
            else:
                error_count += 1
                if error_count <= 5:  # Only log first 5 errors in detail
                    logger.warning(f"Failed to add product: {product['product_name']}")

        except Exception as e:
            error_count += 1
            if error_count <= 5:  # Only log first 5 errors in detail
                logger.error(f"Error adding product {product['product_name']}: {str(e)}")

    if error_count > 5:
        logger.warning(f"Additional {error_count - 5} errors were not shown in detail")

    return success_count


def check_db_values(db):
    """
    Check that values are correctly stored in the database.

    Args:
        db (DatabaseManager): Database manager instance
    """
    logger.info("Checking database values...")

    parts = db.get_all_parts()
    if not parts:
        logger.warning("No parts found in database")
        return

    # Get column names
    columns = db.get_column_names()

    # Check first 5 entries
    for i, part in enumerate(parts[:5]):
        logger.info(f"\nEntry {i + 1}:")
        for j, col_name in enumerate(columns):
            if j < len(part) and part[j] is not None and part[j] != "":
                logger.info(f"  {col_name}: {part[j]}")


def main():
    """Main function to run the import process."""
    logger.info("Starting enhanced car parts import process")

    # Check if the file exists
    btw_filename = "resources/btw_filenames.txt"
    if not os.path.exists(btw_filename):
        logger.error(f"File not found: {btw_filename}")
        return

    # Parse the product list
    logger.info(f"Parsing product list from {btw_filename}")
    products = parse_product_list(btw_filename)
    logger.info(f"Found {len(products)} products in the file")

    # Create database connection
    try:
        db = DatabaseManager()

        # Check if we have existing parts to update
        count = db.count_parts()
        if count > 0:
            logger.info(f"Database already has {count} parts.")
            user_choice = input(
                "Do you want to (1) Clear existing parts and add new ones, or (2) Add new parts without clearing? (1/2): ")

            if user_choice == '1':
                # Clear existing parts and add new ones
                try:
                    db.cursor.execute("DELETE FROM parts")
                    db.conn.commit()
                    logger.info("Cleared existing parts from database")
                except sqlite3.Error as e:
                    logger.error(f"Error clearing database: {str(e)}")
                    return

                # Import products
                start_time = time.time()
                logger.info("Starting import...")

                # Using transaction for better performance
                db.begin_transaction()
                imported_count = import_products_to_db(db, products)
                db.commit_transaction()

                end_time = time.time()
                duration = end_time - start_time

                logger.info(
                    f"Import completed. Added {imported_count} out of {len(products)} products in {duration:.2f} seconds")

            elif user_choice == '2':
                # Add new parts without clearing
                confirmation = input(f"Adding {len(products)} new parts. Continue? (y/n): ")
                if confirmation.lower() != 'y':
                    logger.info("Import cancelled by user")
                    return

                # Import products
                start_time = time.time()
                logger.info("Starting import...")

                # Using transaction for better performance
                db.begin_transaction()
                imported_count = import_products_to_db(db, products)
                db.commit_transaction()

                end_time = time.time()
                duration = end_time - start_time

                logger.info(
                    f"Import completed. Added {imported_count} out of {len(products)} products in {duration:.2f} seconds")

            else:
                logger.info("Invalid choice. Import cancelled.")
                return
        else:
            # No existing parts, just add new ones
            logger.info("Database is empty. Proceeding with import.")

            # Import products
            start_time = time.time()
            logger.info("Starting import...")

            # Using transaction for better performance
            db.begin_transaction()
            imported_count = import_products_to_db(db, products)
            db.commit_transaction()

            end_time = time.time()
            duration = end_time - start_time

            logger.info(
                f"Import completed. Added {imported_count} out of {len(products)} products in {duration:.2f} seconds")

        # Check some values to make sure they were stored correctly
        check_db_values(db)

    except Exception as e:
        logger.error(f"Error during import process: {str(e)}")
    finally:
        if 'db' in locals():
            db.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    main()