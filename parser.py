import sqlite3
import pandas as pd
import re
import os
import logging
from datetime import datetime
import json
import unicodedata
import itertools

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("car_parts_parser.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class CarPartsDatabase:
    def __init__(self, db_path='database.db'):
        """Initialize the database connection"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def connect(self):
        """Connect to the database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {str(e)}")
            return False

    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """Create necessary database tables"""
        try:
            # Main parts table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parcode TEXT,
                name TEXT NOT NULL,
                category TEXT,
                subcategory TEXT,
                car_models TEXT,
                year_from INTEGER,
                year_until INTEGER,
                location TEXT,
                side TEXT,
                size TEXT,
                oe_number TEXT,
                brand TEXT,
                compatible_models TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # Engine codes table (for better parsing)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS engine_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                manufacturer TEXT,
                displacement REAL,
                fuel_type TEXT,
                description TEXT
            )
            ''')

            # Car models reference table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS car_models_ref (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hebrew_name TEXT NOT NULL,
                english_name TEXT NOT NULL,
                manufacturer TEXT,
                model TEXT,
                aliases TEXT
            )
            ''')

            # Parts categories reference
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories_ref (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                hebrew_name TEXT NOT NULL,
                english_name TEXT NOT NULL,
                parent_category TEXT
            )
            ''')

            # Insert engine codes data
            self.populate_engine_codes()

            # Insert car models reference data
            self.populate_car_models_ref()

            # Insert categories reference data
            self.populate_categories_ref()

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error creating tables: {str(e)}")
            self.conn.rollback()
            return False

    def populate_engine_codes(self):
        """Populate engine codes table with reference data"""
        # Check if table already has data
        self.cursor.execute("SELECT COUNT(*) FROM engine_codes")
        count = self.cursor.fetchone()[0]
        if count > 0:
            return

        # Engine codes data - focusing on codes mentioned in the file
        engine_codes = [
            ("CBZ", "Volkswagen", 1.2, "Petrol", "1.2 TSI engine used in Skoda, VW, Seat"),
            ("CJZ", "Volkswagen", 1.2, "Petrol", "1.2 TSI engine used in Skoda, VW, Seat"),
            ("CAX", "Volkswagen", 1.4, "Petrol", "1.4 TSI engine used in Skoda, VW, Seat"),
            ("CAV", "Volkswagen", 1.4, "Petrol", "1.4 TSI engine used in Skoda, VW, Seat"),
            ("BMY", "Volkswagen", 1.4, "Petrol", "1.4 TSI engine used in Skoda, VW, Seat"),
            ("BTS", "Volkswagen", 1.6, "Petrol", "1.6 MPI engine used in Skoda, VW"),
            ("BSE", "Volkswagen", 1.6, "Petrol", "1.6 MPI engine used in Skoda, VW"),
            ("CDA", "Volkswagen", 1.8, "Petrol", "1.8 TSI engine used in Skoda, VW, Audi"),
            ("CJS", "Volkswagen", 1.8, "Petrol", "1.8 TSI engine used in Skoda, VW, Audi"),
            ("BLR", "Volkswagen", 2.0, "Petrol", "2.0 FSI engine used in Skoda, VW, Audi"),
            ("BLX", "Volkswagen", 2.0, "Petrol", "2.0 FSI engine used in Skoda, VW, Audi"),
            ("BLY", "Volkswagen", 2.0, "Petrol", "2.0 FSI engine used in Skoda, VW, Audi"),
            ("AXW", "Volkswagen", 2.0, "Petrol", "2.0 FSI engine used in Skoda, VW, Audi")
        ]

        for code, manufacturer, displacement, fuel_type, description in engine_codes:
            self.cursor.execute('''
            INSERT INTO engine_codes (code, manufacturer, displacement, fuel_type, description)
            VALUES (?, ?, ?, ?, ?)
            ''', (code, manufacturer, displacement, fuel_type, description))

    def populate_car_models_ref(self):
        """Populate car models reference table"""
        # Check if table already has data
        self.cursor.execute("SELECT COUNT(*) FROM car_models_ref")
        count = self.cursor.fetchone()[0]
        if count > 0:
            return

        # Car models reference data with Hebrew names, English names, and aliases
        car_models = [
            ("מזדה 3", "Mazda 3", "Mazda", "3", "מזדה3"),
            ("מזדה 6", "Mazda 6", "Mazda", "6", "מזדה6"),
            ("CX5", "Mazda CX-5", "Mazda", "CX-5", "CX-5,מזדה CX5"),
            ("פוקוס", "Ford Focus", "Ford", "Focus", ""),
            ("קורולה", "Toyota Corolla", "Toyota", "Corolla", "טויוטה קורולה"),
            ("יאריס", "Toyota Yaris", "Toyota", "Yaris", "טויוטה יאריס"),
            ("אוקטביה", "Skoda Octavia", "Skoda", "Octavia", "סקודה אוקטביה"),
            ("רפיד", "Skoda Rapid", "Skoda", "Rapid", "סקודה רפיד"),
            ("פביה", "Skoda Fabia", "Skoda", "Fabia", "סקודה פביה"),
            ("סופרב", "Skoda Superb", "Skoda", "Superb", "סקודה סופרב"),
            ("פולו", "Volkswagen Polo", "Volkswagen", "Polo", "וולקסווגן פולו"),
            ("גולף", "Volkswagen Golf", "Volkswagen", "Golf", "וולקסווגן גולף"),
            ("פאסט", "Volkswagen Passat", "Volkswagen", "Passat", "פסאט,וולקסווגן פסאט"),
            ("קאדי", "Volkswagen Caddy", "Volkswagen", "Caddy", "וולקסווגן קאדי"),
            ("ג'טה", "Volkswagen Jetta", "Volkswagen", "Jetta", "וולקסווגן ג'טה"),
            ("טיגואן", "Volkswagen Tiguan", "Volkswagen", "Tiguan", "וולקסווגן טיגואן"),
            ("טוסון", "Hyundai Tucson", "Hyundai", "Tucson", "יונדאי טוסון"),
            ("I10", "Hyundai i10", "Hyundai", "i10", "יונדאי I10,יונדאי i10"),
            ("I20", "Hyundai i20", "Hyundai", "i20", "יונדאי I20,יונדאי i20"),
            ("I25", "Hyundai i25", "Hyundai", "i25", "יונדאי I25,יונדאי i25"),
            ("I30", "Hyundai i30", "Hyundai", "i30", "יונדאי I30,יונדאי i30"),
            ("I35", "Hyundai i35", "Hyundai", "i35", "יונדאי I35,יונדאי i35"),
            ("אקסנט", "Hyundai Accent", "Hyundai", "Accent", "יונדאי אקסנט"),
            ("גטס", "Hyundai Getz", "Hyundai", "Getz", "יונדאי גטס"),
            ("אלנטרה", "Hyundai Elantra", "Hyundai", "Elantra", "יונדאי אלנטרה"),
            ("סונטה", "Hyundai Sonata", "Hyundai", "Sonata", "יונדאי סונטה"),
            ("סנטה פה", "Hyundai Santa Fe", "Hyundai", "Santa Fe", "יונדאי סנטה פה"),
            ("IX35", "Hyundai ix35", "Hyundai", "ix35", "יונדאי IX35"),
            ("B4", "Subaru Legacy B4", "Subaru", "Legacy", "סובארו B4"),
            ("XV", "Subaru XV", "Subaru", "XV", "סובארו XV"),
            ("סיויק", "Honda Civic", "Honda", "Civic", "הונדה סיויק"),
            ("לנסר", "Mitsubishi Lancer", "Mitsubishi", "Lancer", "מיצובישי לנסר"),
            ("אאוטלנדר", "Mitsubishi Outlander", "Mitsubishi", "Outlander", "מיצובישי אאוטלנדר"),
            ("SX4", "Suzuki SX4", "Suzuki", "SX4", "סוזוקי SX4"),
            ("סוויפט", "Suzuki Swift", "Suzuki", "Swift", "סוזוקי סוויפט"),
            ("ויטרה", "Suzuki Vitara", "Suzuki", "Vitara", "סוזוקי ויטרה"),
            ("ספלאש", "Suzuki Splash", "Suzuki", "Splash", "סוזוקי ספלאש"),
            ("ליאנה", "Suzuki Liana", "Suzuki", "Liana", "סוזוקי ליאנה"),
            ("ספורטאג", "Kia Sportage", "Kia", "Sportage", "קיה ספורטאג"),
            ("סיד", "Kia Ceed", "Kia", "Ceed", "קיה סיד"),
            ("פיקנטו", "Kia Picanto", "Kia", "Picanto", "קיה פיקנטו"),
            ("ריו", "Kia Rio", "Kia", "Rio", "קיה ריו"),
            ("סורנטו", "Kia Sorento", "Kia", "Sorento", "קיה סורנטו"),
            ("קשקאי", "Nissan Qashqai", "Nissan", "Qashqai", "ניסאן קשקאי"),
            ("מיקרה", "Nissan Micra", "Nissan", "Micra", "ניסאן מיקרה"),
            ("גוק", "Nissan Juke", "Nissan", "Juke", "ניסאן גוק,ג'וק"),
            ("קליאו", "Renault Clio", "Renault", "Clio", "רנו קליאו"),
            ("מגאן", "Renault Megane", "Renault", "Megane", "רנו מגאן"),
            ("פלואנס", "Renault Fluence", "Renault", "Fluence", "רנו פלואנס"),
            ("קנגו", "Renault Kangoo", "Renault", "Kangoo", "רנו קנגו"),
            ("ברלינגו", "Citroen Berlingo", "Citroen", "Berlingo", "סיטרואן ברלינגו"),
            ("C4", "Citroen C4", "Citroen", "C4", "סיטרואן C4"),
            ("C3", "Citroen C3", "Citroen", "C3", "סיטרואן C3"),
            ("היילקס", "Toyota Hilux", "Toyota", "Hilux", "טויוטה היילקס"),
            ("לנדקרוזר", "Toyota Land Cruiser", "Toyota", "Land Cruiser", "טויוטה לנדקרוזר"),
            ("ויגו", "Toyota Hilux Vigo", "Toyota", "Hilux Vigo", "טויוטה ויגו"),
            ("דימקס", "Isuzu D-Max", "Isuzu", "D-Max", "איסוזו דימקס"),
            ("ראב 4", "Toyota RAV4", "Toyota", "RAV4", "טויוטה ראב 4")
        ]

        for hebrew, english, manufacturer, model, aliases in car_models:
            self.cursor.execute('''
            INSERT INTO car_models_ref (hebrew_name, english_name, manufacturer, model, aliases)
            VALUES (?, ?, ?, ?, ?)
            ''', (hebrew, english, manufacturer, model, aliases))

    def populate_categories_ref(self):
        """Populate categories reference table"""
        # Check if table already has data
        self.cursor.execute("SELECT COUNT(*) FROM categories_ref")
        count = self.cursor.fetchone()[0]
        if count > 0:
            return

        # Categories reference data with Hebrew names and English translations
        categories = [
            ("פ.אויר", "Air Filter", None),
            ("פ.שמן", "Oil Filter", None),
            ("פ.דלק", "Fuel Filter", None),
            ("פ.סולר", "Diesel Filter", "Fuel Filter"),
            ("פ.מזגן", "AC Filter", None),
            ("דסקיות", "Brake Discs", None),
            ("צלחות", "Brake Discs", None),
            ("רפידות", "Brake Pads", None),
            ("בולם", "Shock Absorber", None),
            ("מייצב", "Stabilizer", None),
            ("ג.מייצב", "Stabilizer Link", "Stabilizer"),
            ("ז.מייצב", "Stabilizer Arm", "Stabilizer"),
            ("משולש", "Control Arm", None),
            ("נשם", "Air Vent", None),
            ("אטם", "Gasket", None),
            ("אטם ראש", "Head Gasket", "Gasket"),
            ("אטם קולר", "Oil Cooler Gasket", "Gasket"),
            ("אטם מכסה שסטומים", "Valve Cover Gasket", "Gasket"),
            ("מ.מים", "Water Pump", None),
            ("צינור מים", "Water Hose", None),
            ("צינור עליון", "Upper Hose", "Water Hose"),
            ("צינור תחתון", "Lower Hose", "Water Hose"),
            ("טרמוסטט", "Thermostat", None),
            ("פלגים", "Spark Plugs", None),
            ("כוהל", "Ignition Coil", None),
            ("רצוע", "Belt", None),
            ("גלגלת", "Pulley", None),
            ("PK", "Belt", None),
            ("ח.הצתה", "Ignition Module", None),
            ("ח.חמצן", "Oxygen Sensor", None),
            ("קדמי", "Front", None),
            ("אחורי", "Rear", None),
            ("ימין", "Right", None),
            ("שמאל", "Left", None),
            ("ז.הגה", "Steering Arm", None),
            ("ז.פרונט", "Front Arm", None),
            ("זרוע הגה", "Steering Arm", None),
            ("קמשפט", "Camshaft", None),
            ("צלב", "Universal Joint", None),
            ("צריה", "CV Joint", None),
            ("פעמון צריה", "CV Boot", "CV Joint"),
            ("בוקסה", "Bushing", None),
            ("בית מצערת", "Throttle Body", None),
            ("יוניט", "Sensor Unit", None),
            ("חיישן", "Sensor", None),
            ("דרם אחורי", "Rear Drum", None),
            ("מיסב בולם", "Strut Bearing", None),
            ("ת.בולם", "Strut Mount", None),
            ("מותח", "Tensioner", None),
            ("גלגל תנופה", "Flywheel", None),
            ("רדיאטור", "Radiator", None),
            ("מיכל עיבוי", "Expansion Tank", None),
            ("סליל כרית אויר", "Airbag Spiral Cable", None),
            ("מחזיר שמן", "Oil Seal", None),
            ("קולר שמן", "Oil Cooler", None),
            ("מ.שמן", "Oil Pump", None),
            ("מ.דלק", "Fuel Pump", None),
            ("מכסה טיימינג", "Timing Cover", None),
            ("סט טיימינג", "Timing Belt Kit", None),
            ("ברז חימום", "Heating Valve", None),
            ("בורג קמשפט", "Camshaft Bolt", None)
        ]

        for hebrew, english, parent in categories:
            self.cursor.execute('''
            INSERT INTO categories_ref (hebrew_name, english_name, parent_category)
            VALUES (?, ?, ?)
            ''', (hebrew, english, parent))

    def extract_year_info(self, name):
        """Extract year information from the name"""
        year_from = None
        year_until = None

        # Find "from year" (מ followed by 2 digits)
        from_match = re.search(r'מ(\d{1,2})', name)
        if from_match:
            year = int(from_match.group(1))
            # Assuming 2 digit year format, convert to full year
            if year < 50:  # Arbitrary cutoff
                year_from = 2000 + year
            else:
                year_from = 1900 + year

        # Find "until year" (עד followed by digits)
        until_match = re.search(r'עד(\d{1,2})', name)
        if until_match:
            year = int(until_match.group(1))
            # Convert to full year
            if year < 50:
                year_until = 2000 + year
            else:
                year_until = 1900 + year

        return year_from, year_until

    def extract_side(self, name):
        """Extract side information (right/left) from the name"""
        if 'ימין' in name or 'ימ' in name:
            return 'Right'
        elif 'שמאל' in name or 'שמ' in name:
            return 'Left'
        return None

    def extract_location(self, name):
        """Extract location information (front/rear) from the name"""
        if 'קדמי' in name or 'קד' in name:
            return 'Front'
        elif 'אחורי' in name or 'אח' in name:
            return 'Rear'
        return None

    def identify_category(self, name):
        """Identify the category of the part based on name using the reference table"""
        try:
            # First, get all categories from the reference table
            self.cursor.execute("SELECT hebrew_name, english_name FROM categories_ref")
            categories = self.cursor.fetchall()

            # Sort categories by length of Hebrew name (descending) to match longer patterns first
            categories.sort(key=lambda x: len(x[0]), reverse=True)

            for hebrew, english in categories:
                if hebrew in name:
                    return english

            # Additional pattern matching for PK items (belts)
            if re.search(r'\d+PK', name):
                return 'Belt'

            return 'Unknown'
        except Exception as e:
            logger.error(f"Error identifying category: {str(e)}")
            return 'Unknown'

    def identify_subcategory(self, name, category):
        """Identify subcategory based on name and main category using the reference table"""
        try:
            # Get potential subcategories from the reference table
            self.cursor.execute("""
                SELECT hebrew_name, english_name 
                FROM categories_ref 
                WHERE parent_category = ?
            """, (category,))

            subcategories = self.cursor.fetchall()

            # Sort subcategories by length of Hebrew name (descending) to match longer patterns first
            subcategories.sort(key=lambda x: len(x[0]), reverse=True)

            for hebrew, english in subcategories:
                if hebrew in name:
                    return english

            # Custom subcategory logic based on the name and category
            if category == 'Air Filter' and 'מנוע' in name:
                return 'Engine Air Filter'
            elif category == 'Air Filter' and 'תא' in name:
                return 'Cabin Air Filter'
            elif category == 'Brake Discs':
                if 'מחורר' in name:
                    return 'Perforated Disc'
                elif 'חירוץ' in name:
                    return 'Grooved Disc'

            return None
        except Exception as e:
            logger.error(f"Error identifying subcategory: {str(e)}")
            return None

    def identify_car_models(self, name):
        """Identify car models mentioned in the name using reference table"""
        try:
            # Get all car models from the reference table
            self.cursor.execute("SELECT hebrew_name, english_name, aliases FROM car_models_ref")
            models = self.cursor.fetchall()

            # Sort models by length of Hebrew name (descending) to match longer patterns first
            models.sort(key=lambda x: len(x[0]), reverse=True)

            identified_models = []
            for hebrew, english, aliases in models:
                # Check if the Hebrew name is in the part name
                if hebrew in name:
                    identified_models.append(english)
                    continue

                # Check aliases too if available
                if aliases:
                    alias_list = aliases.split(',')
                    for alias in alias_list:
                        if alias and alias in name:
                            identified_models.append(english)
                            break

            return ', '.join(identified_models) if identified_models else None
        except Exception as e:
            logger.error(f"Error identifying car models: {str(e)}")
            return None

    def extract_engine_info(self, name):
        """Extract engine code information from the name"""
        try:
            # Get all engine codes from the reference table
            self.cursor.execute("SELECT code, manufacturer, displacement, fuel_type FROM engine_codes")
            engine_codes = self.cursor.fetchall()

            matched_engines = []
            for code, manufacturer, displacement, fuel_type in engine_codes:
                if code in name:
                    matched_engines.append({
                        'code': code,
                        'manufacturer': manufacturer,
                        'displacement': displacement,
                        'fuel_type': fuel_type
                    })

            # Also check for displacement mentioned directly in the name (e.g., 1.6, 2.0)
            displacement_match = re.search(r'(\d\.\d)', name)
            if displacement_match:
                displacement = displacement_match.group(1)
                matched_engines.append({
                    'code': None,
                    'manufacturer': None,
                    'displacement': float(displacement),
                    'fuel_type': None
                })

            return matched_engines if matched_engines else None
        except Exception as e:
            logger.error(f"Error extracting engine info: {str(e)}")
            return None

    def extract_parcode(self, name):
        """Extract part code if available in the name"""
        try:
            # Look for common part code formats (alphanumeric patterns)
            parcode_match = re.search(r'[A-Z0-9]{5,12}', name)
            if parcode_match:
                return parcode_match.group(0)

            # OE Numbers pattern (typically includes dashes or dots)
            oe_match = re.search(r'[A-Z0-9]{2,8}[\.-][A-Z0-9]{2,8}[\.-]?[A-Z0-9]{1,8}', name)
            if oe_match:
                return oe_match.group(0)

            return None
        except Exception as e:
            logger.error(f"Error extracting parcode: {str(e)}")
            return None

    def extract_size_info(self, name):
        """Extract size information from the name"""
        try:
            # Look for measurements like "70 ממ" (70 mm)
            size_match = re.search(r'(\d+)\s*ממ', name)
            if size_match:
                return f"{size_match.group(1)} mm"

            # Look for PK belt sizes like "6PK1200"
            belt_match = re.search(r'(\d+PK\s*\d+)', name)
            if belt_match:
                return belt_match.group(1)

            return None
        except Exception as e:
            logger.error(f"Error extracting size info: {str(e)}")
            return None

    def process_parts_data(self, parts_list):
        """Process a list of part names and insert into the database"""
        try:
            for name in parts_list:
                # Skip empty lines
                if not name or name.isspace():
                    continue

                # Extract all information
                category = self.identify_category(name)
                subcategory = self.identify_subcategory(name, category)
                side = self.extract_side(name)
                location = self.extract_location(name)
                year_from, year_until = self.extract_year_info(name)
                car_models = self.identify_car_models(name)
                parcode = self.extract_parcode(name)
                size = self.extract_size_info(name)

                # Get engine information
                engine_info = self.extract_engine_info(name)
                engine_notes = None
                if engine_info:
                    engine_notes_list = []
                    for engine in engine_info:
                        if engine['code']:
                            engine_notes_list.append(
                                f"Engine: {engine['code']} ({engine['displacement']}L {engine['fuel_type']})")
                        elif engine['displacement']:
                            engine_notes_list.append(f"Engine Displacement: {engine['displacement']}L")

                    if engine_notes_list:
                        engine_notes = "; ".join(engine_notes_list)

                # Insert into database
                self.cursor.execute('''
                INSERT INTO parts (parcode, name, category, subcategory, car_models, 
                                year_from, year_until, location, side, size, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (parcode, name, category, subcategory, car_models,
                      year_from, year_until, location, side, size, engine_notes))

            self.conn.commit()
            logger.info(f"Successfully processed {len(parts_list)} parts.")
            return True
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error processing parts data: {str(e)}")
            return False

    def load_data_from_file(self, file_path):
        """Load data from a text file and process it"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                parts_list = [line.strip() for line in file.readlines()]

            return self.process_parts_data(parts_list)
        except Exception as e:
            logger.error(f"Error loading data from file: {str(e)}")
            return False

    def load_data_from_excel(self, file_path):
        """Load data from an Excel file and process it"""
        try:
            df = pd.read_excel(file_path)

            # Check if 'name' column exists
            if 'name' not in df.columns:
                logger.error("Required column 'name' not found in Excel file")
                return False

            # Extract part names list
            parts_list = df['name'].dropna().tolist()

            return self.process_parts_data(parts_list)
        except Exception as e:
            logger.error(f"Error loading data from Excel file: {str(e)}")
            return False

    def search_parts(self, search_term=None, category=None, car_model=None, year=None, location=None, side=None):
        """Search for parts in the database with various filters"""
        try:
            query = "SELECT * FROM parts WHERE 1=1"
            params = []

            if search_term:
                query += " AND name LIKE ?"
                params.append(f"%{search_term}%")

            if category:
                query += " AND category = ?"
                params.append(category)

            if car_model:
                query += " AND car_models LIKE ?"
                params.append(f"%{car_model}%")

            if year:
                query += " AND (year_from IS NULL OR year_from <= ?) AND (year_until IS NULL OR year_until >= ?)"
                params.append(year)
                params.append(year)

            if location:
                query += " AND location = ?"
                params.append(location)

            if side:
                query += " AND side = ?"
                params.append(side)

            self.cursor.execute(query, params)
            results = self.cursor.fetchall()

            return results
        except Exception as e:
            logger.error(f"Error searching parts: {str(e)}")
            return []

    def get_all_categories(self):
        """Get all available categories"""
        try:
            self.cursor.execute("SELECT DISTINCT category FROM parts WHERE category IS NOT NULL ORDER BY category")
            categories = self.cursor.fetchall()
            return [category[0] for category in categories]
        except Exception as e:
            logger.error(f"Error getting categories: {str(e)}")
            return []

    def get_all_car_models(self):
        """Get all available car models"""
        try:
            # This is complex because car_models is stored as comma-separated list
            self.cursor.execute("SELECT car_models FROM parts WHERE car_models IS NOT NULL")
            model_lists = self.cursor.fetchall()

            # Flatten and split all model lists
            all_models = []
            for models in model_lists:
                if models[0]:
                    all_models.extend(models[0].split(', '))

            # Remove duplicates and sort
            unique_models = sorted(list(set(all_models)))
            return unique_models
        except Exception as e:
            logger.error(f"Error getting car models: {str(e)}")
            return []

    def get_years_range(self):
        """Get min and max years from the database"""
        try:
            self.cursor.execute(
                "SELECT MIN(year_from), MAX(year_until) FROM parts WHERE year_from IS NOT NULL AND year_until IS NOT NULL")
            min_year, max_year = self.cursor.fetchone()
            return min_year, max_year
        except Exception as e:
            logger.error(f"Error getting years range: {str(e)}")
            return None, None

    def export_to_json(self, output_file):
        """Export the entire database to a JSON file"""
        try:
            self.cursor.execute("""
                SELECT id, parcode, name, category, subcategory, car_models, 
                       year_from, year_until, location, side, size, notes
                FROM parts
            """)
            columns = [column[0] for column in self.cursor.description]
            results = []

            for row in self.cursor.fetchall():
                results.append(dict(zip(columns, row)))

            with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)

            logger.info(f"Successfully exported {len(results)} parts to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            return False


def generate_statistics(self):
    """Generate statistics about the database"""
    try:
        stats = {}

        # Total number of parts
        self.cursor.execute("SELECT COUNT(*) FROM parts")
        stats['total_parts'] = self.cursor.fetchone()[0]

        # Parts per category
        self.cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM parts 
                WHERE category IS NOT NULL
                GROUP BY category 
                ORDER BY count DESC
            """)
        stats['parts_per_category'] = {row[0]: row[1] for row in self.cursor.fetchall()}

        # Parts per car model (this is more complex due to comma separated values)
        # We'll get a rough estimate by counting occurrences of each model
        car_models = self.get_all_car_models()
        model_counts = {}
        for model in car_models:
            self.cursor.execute("""
                    SELECT COUNT(*) FROM parts 
                    WHERE car_models LIKE ?
                """, (f'%{model}%',))
            model_counts[model] = self.cursor.fetchone()[0]

        # Sort by count descending and take top 10
        stats['top_car_models'] = dict(sorted(model_counts.items(), key=lambda x: x[1], reverse=True)[:10])

        # Parts with years information
        self.cursor.execute("SELECT COUNT(*) FROM parts WHERE year_from IS NOT NULL OR year_until IS NOT NULL")
        stats['parts_with_year_info'] = self.cursor.fetchone()[0]

        # Parts with location info (front/rear)
        self.cursor.execute("SELECT COUNT(*) FROM parts WHERE location IS NOT NULL")
        stats['parts_with_location'] = self.cursor.fetchone()[0]

        # Parts with side info (left/right)
        self.cursor.execute("SELECT COUNT(*) FROM parts WHERE side IS NOT NULL")
        stats['parts_with_side'] = self.cursor.fetchone()[0]

        # Parts with part code
        self.cursor.execute("SELECT COUNT(*) FROM parts WHERE parcode IS NOT NULL")
        stats['parts_with_parcode'] = self.cursor.fetchone()[0]

        return stats
    except Exception as e:
        logger.error(f"Error generating statistics: {str(e)}")
        return {}


def analyze_data_quality(self):
    """Analyze data quality and identify potential issues"""
    try:
        issues = {
            'missing_category': [],
            'missing_car_models': [],
            'unusual_formats': [],
            'potential_duplicates': []
        }

        # Find parts with missing category
        self.cursor.execute("""
                SELECT id, name FROM parts 
                WHERE category IS NULL OR category = 'Unknown'
                LIMIT 100
            """)
        issues['missing_category'] = [(row[0], row[1]) for row in self.cursor.fetchall()]

        # Find parts with missing car model info
        self.cursor.execute("""
                SELECT id, name FROM parts 
                WHERE car_models IS NULL
                LIMIT 100
            """)
        issues['missing_car_models'] = [(row[0], row[1]) for row in self.cursor.fetchall()]

        # Find parts with unusual formats (e.g., extremely long names)
        self.cursor.execute("""
                SELECT id, name FROM parts 
                WHERE LENGTH(name) > 50
                LIMIT 100
            """)
        issues['unusual_formats'] = [(row[0], row[1]) for row in self.cursor.fetchall()]

        # Find potential duplicates (parts with very similar names)
        self.cursor.execute("""
                SELECT p1.id, p1.name, p2.id, p2.name
                FROM parts p1
                JOIN parts p2 ON p1.id < p2.id
                WHERE p1.name LIKE '%' || substr(p2.name, 1, LENGTH(p2.name) * 0.7) || '%'
                OR p2.name LIKE '%' || substr(p1.name, 1, LENGTH(p1.name) * 0.7) || '%'
                LIMIT 100
            """)
        issues['potential_duplicates'] = [(row[0], row[1], row[2], row[3]) for row in self.cursor.fetchall()]

        return issues
    except Exception as e:
        logger.error(f"Error analyzing data quality: {str(e)}")
        return {}


def suggest_improvements(self, part_id):
    """Suggest improvements for a specific part"""
    try:
        self.cursor.execute("""
                SELECT id, name, category, car_models, year_from, year_until, location, side, parcode
                FROM parts WHERE id = ?
            """, (part_id,))
        part = self.cursor.fetchone()

        if not part:
            return {"error": f"Part with ID {part_id} not found"}

        part_dict = {
            "id": part[0],
            "name": part[1],
            "category": part[2],
            "car_models": part[3],
            "year_from": part[4],
            "year_until": part[5],
            "location": part[6],
            "side": part[7],
            "parcode": part[8]
        }

        suggestions = []

        # Check for missing category
        if not part[2] or part[2] == 'Unknown':
            suggestions.append("Missing category - consider reviewing the name for category identification")

        # Check for missing car model
        if not part[3]:
            suggestions.append("Missing car model information - consider adding car model details")

        # Check for missing year information
        if not part[4] and not part[5]:
            suggestions.append("Missing year information - consider adding year range")

        # Check for missing location for parts that typically have it
        location_categories = ['Brake Discs', 'Brake Pads', 'Shock Absorber']
        if part[2] in location_categories and not part[6]:
            suggestions.append("Missing location (front/rear) for a part that typically has this information")

        # Check for missing side information for parts that typically have it
        side_categories = ['Shock Absorber', 'Control Arm', 'Steering Arm']
        if part[2] in side_categories and not part[7]:
            suggestions.append("Missing side (left/right) for a part that typically has this information")

        # Check for missing part code
        if not part[8]:
            suggestions.append("Missing part code - consider adding OE or manufacturer part number")

        return {
            "part": part_dict,
            "suggestions": suggestions,
            "has_issues": len(suggestions) > 0
        }
    except Exception as e:
        logger.error(f"Error suggesting improvements: {str(e)}")
        return {"error": str(e)}


class PartsDataProcessor:
    """Helper class to process raw parts data"""

    def __init__(self, db_manager=None):
        """Initialize with a database manager"""
        self.db_manager = db_manager or CarPartsDatabase()
        if not self.db_manager.conn:
            self.db_manager.connect()
            self.db_manager.create_tables()

    def normalize_hebrew_text(self, text):
        """Normalize Hebrew text by removing diacritics and standardizing characters"""
        if not text:
            return text

        # Normalize Unicode characters
        text = unicodedata.normalize('NFKD', text)

        # Replace final forms with regular forms in Hebrew
        replacements = {
            'ך': 'כ',
            'ם': 'מ',
            'ן': 'נ',
            'ף': 'פ',
            'ץ': 'צ'
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)

        return text

    def clean_part_name(self, name):
        """Clean and standardize a part name"""
        if not name:
            return name

        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name).strip()

        # Normalize Hebrew text
        name = self.normalize_hebrew_text(name)

        # Remove BTW suffix (בטיפול) often added to part names
        name = re.sub(r'btw$', '', name, flags=re.IGNORECASE).strip()

        return name

    def preprocess_parts_list(self, parts_list):
        """Preprocess a list of part names"""
        return [self.clean_part_name(name) for name in parts_list if name and not name.isspace()]

    def batch_process_file(self, file_path):
        """Process a file in batches to avoid memory issues"""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as file:
                    parts_list = [self.clean_part_name(line.strip()) for line in file if line.strip()]

                # Process in batches of 100
                batch_size = 100
                for i in range(0, len(parts_list), batch_size):
                    batch = parts_list[i:i + batch_size]
                    self.db_manager.process_parts_data(batch)
                    logger.info(f"Processed batch {i // batch_size + 1} ({len(batch)} parts)")

            elif file_ext in ['.xlsx', '.xls']:
                # Process Excel file in chunks
                chunk_size = 100
                for chunk in pd.read_excel(file_path, chunksize=chunk_size):
                    if 'name' in chunk.columns:
                        parts_list = chunk['name'].dropna().apply(self.clean_part_name).tolist()
                        if parts_list:
                            self.db_manager.process_parts_data(parts_list)
                            logger.info(f"Processed {len(parts_list)} parts from Excel")

            return True
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            return False

    def suggest_categories_for_unknown(self):
        """Try to suggest categories for parts with unknown category"""
        try:
            self.db_manager.cursor.execute("""
                SELECT id, name FROM parts 
                WHERE category IS NULL OR category = 'Unknown'
            """)
            unknown_parts = self.db_manager.cursor.fetchall()

            suggestions = {}
            for part_id, part_name in unknown_parts:
                # Try to find similar parts with known categories
                self.db_manager.cursor.execute("""
                    SELECT category, COUNT(*) as count 
                    FROM parts 
                    WHERE category IS NOT NULL AND category != 'Unknown'
                    AND (
                        name LIKE ? OR
                        ? LIKE CONCAT('%', name, '%')
                    )
                    GROUP BY category
                    ORDER BY count DESC
                    LIMIT 3
                """, (f"%{part_name}%", part_name))

                similar_categories = self.db_manager.cursor.fetchall()

                if similar_categories:
                    suggestions[part_id] = {
                        "part_name": part_name,
                        "suggested_categories": [{"category": cat, "count": count} for cat, count in similar_categories]
                    }

            return suggestions
        except Exception as e:
            logger.error(f"Error suggesting categories: {str(e)}")
            return {}

    def identify_unique_engine_codes(self):
        """Identify all unique engine codes in the parts data"""
        try:
            # First, extract all engine codes from part names
            self.db_manager.cursor.execute("SELECT name FROM parts")
            part_names = [row[0] for row in self.db_manager.cursor.fetchall()]

            # Common engine code pattern is usually 3-4 uppercase letters
            engine_code_pattern = re.compile(r'\b[A-Z]{3,4}\b')

            all_codes = []
            for name in part_names:
                matches = engine_code_pattern.findall(name)
                all_codes.extend(matches)

            # Count occurrences of each code
            code_counts = {}
            for code in all_codes:
                if code not in code_counts:
                    code_counts[code] = 0
                code_counts[code] += 1

            # Filter out codes that appear very rarely (likely not engine codes)
            threshold = 3  # Minimum appearances to be considered an engine code
            potential_engine_codes = {code: count for code, count in code_counts.items() if count >= threshold}

            # Sort by frequency (most common first)
            sorted_codes = sorted(potential_engine_codes.items(), key=lambda x: x[1], reverse=True)

            return sorted_codes
        except Exception as e:
            logger.error(f"Error identifying engine codes: {str(e)}")
            return []

    def detect_patterns_in_names(self):
        """Detect common patterns in part names to improve parsing"""
        try:
            # Get all part names
            self.db_manager.cursor.execute("SELECT name FROM parts")
            part_names = [row[0] for row in self.db_manager.cursor.fetchall()]

            # Initialize pattern counters
            patterns = {
                'year_format_מ': 0,  # Format: מ15 (from 2015)
                'year_format_עד': 0,  # Format: עד09 (until 2009)
                'location_format_prefix': 0,  # Format: קדמי/אחורי at beginning
                'location_format_suffix': 0,  # Format: קדמי/אחורי at end
                'side_format_prefix': 0,  # Format: ימין/שמאל at beginning
                'side_format_suffix': 0,  # Format: ימין/שמאל at end
                'car_model_prefix': 0,  # Car model at beginning
                'car_model_suffix': 0,  # Car model at end
                'with_engine_code': 0,  # Contains engine code
                'with_dimensions': 0,  # Contains dimensions (like mm)
                'with_pk_format': 0  # Belt format like 6PK1200
            }

            for name in part_names:
                # Check year formats
                if re.search(r'מ\d{1,2}', name):
                    patterns['year_format_מ'] += 1
                if re.search(r'עד\d{1,2}', name):
                    patterns['year_format_עד'] += 1

                # Check location formats
                if re.match(r'^(קדמי|אחורי)', name):
                    patterns['location_format_prefix'] += 1
                if re.search(r'(קדמי|אחורי)$', name):
                    patterns['location_format_suffix'] += 1

                # Check side formats
                if re.match(r'^(ימין|שמאל)', name):
                    patterns['side_format_prefix'] += 1
                if re.search(r'(ימין|שמאל)$', name):
                    patterns['side_format_suffix'] += 1

                # Check for engine codes (3-4 uppercase letters)
                if re.search(r'\b[A-Z]{3,4}\b', name):
                    patterns['with_engine_code'] += 1

                # Check for dimensions
                if re.search(r'\d+\s*ממ', name):
                    patterns['with_dimensions'] += 1

                # Check for PK format
                if re.search(r'\d+PK\s*\d+', name):
                    patterns['with_pk_format'] += 1

                # Car model checks would need to use the reference data from car_models_ref

            # Calculate percentages
            total_parts = len(part_names)
            pattern_percentages = {key: (count / total_parts) * 100 for key, count in patterns.items()}

            return {
                'raw_counts': patterns,
                'percentages': pattern_percentages,
                'total_analyzed': total_parts
            }
        except Exception as e:
            logger.error(f"Error detecting patterns: {str(e)}")
            return {}


def main():
    """Main function to run the program"""
    logger.info("Car Parts Database Parser Starting...")

    db = CarPartsDatabase()
    db.connect()
    db.create_tables()

    processor = PartsDataProcessor(db)

    # Check for btw_filenames.txt in the resources directory
    file_path = 'resources/btw_filenames.txt'
    if os.path.exists(file_path):
        logger.info(f"Found parts data file at {file_path}")
        processor.batch_process_file(file_path)
    else:
        logger.warning(f"Parts data file not found at {file_path}")
        # Create sample data for testing
        sample_parts = [
            "פ.אויר מזדה 3 מ13",
            "פ.שמן טויוטה קורולה מ08",
            "בולם קדמי ימין אוקטביה מ05",
            "דסקיות אחורי I30 מ12",
            "דסקיות קדמי פוקוס מ06",
            "פ.מזגן יונדאי I35 מ11",
            "רפידות קדמי קשקאי מ14",
            "אטם ראש מנוע סובארו XV מ12"
        ]
        db.process_parts_data(sample_parts)

    # Display statistics
    stats = db.generate_statistics()
    logger.info("Database Statistics:")
    logger.info(f"Total parts: {stats.get('total_parts', 0)}")
    logger.info(f"Parts with year info: {stats.get('parts_with_year_info', 0)}")
    logger.info(f"Parts with location info: {stats.get('parts_with_location', 0)}")
    logger.info(f"Parts with side info: {stats.get('parts_with_side', 0)}")

    top_categories = list(stats.get('parts_per_category', {}).items())[:5]
    logger.info("Top 5 Categories:")
    for category, count in top_categories:
        logger.info(f"  {category}: {count} parts")

    # Export to JSON for further analysis
    db.export_to_json('car_parts_database_export.json')

    logger.info("Car Parts Database Parser Complete")
    db.close()


if __name__ == "__main__":
    main()
