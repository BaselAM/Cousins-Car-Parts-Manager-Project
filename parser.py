#!/usr/bin/env python3
"""
Advanced Car Parts Database Generator (Simplified Version)

This script processes a text file containing car part names in Hebrew/English
and creates a structured SQLite database with enhanced parsing capabilities.
All data is stored in a single comprehensive table for simplicity.

Features:
- Distinguishes between positions and drive types (4x4, 4x2)
- Provides accuracy scores for parsed data
- Enhanced pattern recognition for better extraction
- Single table design for ease of use
"""

import re
import sqlite3
import os
import math

# Part type mapping Hebrew to English
PART_TYPE_MAP = {
    'פ.אויר': 'Air Filter',
    'פ.שמן': 'Oil Filter',
    'פ.דלק': 'Fuel Filter',
    'פ.סולר': 'Diesel Filter',
    'פ.מזגן': 'A/C Filter',
    'פ.גיר': 'Transmission Filter',
    'רדיאטור': 'Radiator',
    'מ.מים': 'Water Pump',
    'מאוורר': 'Fan',
    'דסקיות': 'Brake Discs',
    'צלחות': 'Brake Rotors',
    'רפידות': 'Brake Pads',
    'נעליים': 'Brake Shoes',
    'ח.בלם': 'Brake Sensor',
    'בולם': 'Shock Absorber',
    'משולש': 'Control Arm',
    'ת.משולש': 'Control Arm Bushing',
    'ת.בולם': 'Shock Mount',
    'ג.מייצב': 'Stabilizer Bar',
    'מ.מייצב': 'Stabilizer Link',
    'סט טיימינג': 'Timing Belt Kit',
    'סט מצמד': 'Clutch Kit',
    'סט רצועות': 'Belt Kit',
    'ציריה': 'CV Axle',
    'טרמוסטט': 'Thermostat',
    'מיכל עיבוי': 'Expansion Tank',
    'אטם ראש': 'Head Gasket',
    'אטם מכסה': 'Cover Gasket',
    'רצועת': 'Belt',
    'רצועה': 'Belt',
    'צינור': 'Hose',
    'פלגים': 'Spark Plugs',
    'פלנץ': 'Flange',
    'מותח': 'Tensioner',
    'נשם': 'Breather',
    'יוניט': 'Sensor Unit',
    'חיישן': 'Sensor',
    'ח.קראנק': 'Crankshaft Sensor',
    'מחזיר שמן': 'Oil Seal',
    'מחבר': 'Connector',
    'ז.הגה': 'Steering Arm',
    'קצה הגה': 'Tie Rod End',
    'זרוע': 'Arm',
    'קולר': 'Cooler',
    'מסרק הגה': 'Steering Rack',
    'מיסב': 'Bearing',
    'נאבה': 'Hub',
    'פעמון': 'CV Joint Boot',
    'ת.מנוע': 'Engine Mount',
    'ת.גיר': 'Transmission Mount',
    'כוהל': 'Throttle Body',
    'מכסה': 'Cap',
    'פקק': 'Plug',
    'בית': 'Housing',
    'קרטר': 'Oil Pan',
    'דרם': 'Drum',
    'שיפטר': 'Shifter',
    'סליל': 'Coil',
    'תושבת': 'Bracket',
    'פולי': 'Pulley',
    'אטם': 'Gasket',
    'גלגלת': 'Wheel',
    'כבל': 'Cable',
    'ממיר': 'Converter',
    'מזלג': 'Fork',
    'ידית': 'Handle',
    'מייסב': 'Bearing'
}

# Position mapping Hebrew to English
POSITION_MAP = {
    'קדמי': 'Front',
    'אחורי': 'Rear',
    'ימין': 'Right',
    'שמאל': 'Left',
    'עליון': 'Upper',
    'תחתון': 'Lower'
}

# Drive type mapping
DRIVE_TYPE_MAP = {
    '4x4': 'Four-wheel drive',
    '4x2': 'Two-wheel drive'
}

# Car manufacturers mapping
CAR_MANUFACTURERS = {
    'יונדאי': 'Hyundai',
    'קיה': 'Kia',
    'טויוטה': 'Toyota',
    'הונדה': 'Honda',
    'מזדה': 'Mazda',
    'מרצדס': 'Mercedes',
    'ב.מ.וו': 'BMW',
    'אאודי': 'Audi',
    'פורד': 'Ford',
    'סקודה': 'Skoda',
    'סיטרואן': 'Citroen',
    'פיאט': 'Fiat',
    'רנו': 'Renault',
    'פיג\'ו': 'Peugeot',
    'סוזוקי': 'Suzuki',
    'ניסאן': 'Nissan',
    'מיצובישי': 'Mitsubishi',
    'פולקסווגן': 'Volkswagen',
    'שברולט': 'Chevrolet',
    'דאצ\'יה': 'Dacia',
    'סובארו': 'Subaru',
    'וולוו': 'Volvo',
    'אופל': 'Opel',
    'לקסוס': 'Lexus'
}

# Common car models in Hebrew and English
CAR_MODELS = [
    'אוקטביה', 'לנסר', 'קורולה', 'גולף', 'פאסאט', 'ג\'טה', 'פולו', 'ג\'וק', 'מיקרה',
    'IX35', 'I20', 'I30', 'I35', 'I25', 'I10', 'I800', 'CX5', 'B4', 'B3', 'XV',
    'אקסנט', 'גטס', 'פורסטר', 'לנדקרוזר', 'לגסי', 'אוריס', 'פוקוס', 'פיאסטה',
    'מונדאו', 'קליאו', 'מגאן', 'לוגאן', 'דוסטר', 'סנדרו', '308', '208', '207',
    '206', '3008', 'C3', 'C4', 'ספורטאג', 'סורנטו', 'סנטה פה', 'טוסון', 'רומסטר',
    'פביה', 'סופרב', 'קודיאק', 'ויגו', 'דימקס', 'היילקס', 'ראב 4', 'קרניבל',
    'פיקנטו', 'ריו', 'אוטלנדר', 'אקורד', 'סיויק', 'ברלינגו', 'קשקאי', 'A4',
    'A5', 'A6', 'A7', 'A8', 'Q5', 'Q7', 'Q8', 'T5', 'T6', 'קרפטר', 'ספרינטר',
    'גרנד קופה', 'סיד', 'ליאנה', 'פלואנס', 'קאדי', 'טיגואן', 'קנגו', 'ויאנו',
    'ויטו', 'קפצור', 'טראפיק', 'טרנזיט', 'אלנטרה', 'איוניק', 'נירו', 'קונה',
    'ספייס סטאר', 'אטראז', 'לנטיס', 'טרייטון', 'סיריון', 'טראקס', 'מוקה',
    'טרברס', 'קבטיבה', 'ויטרה', 'איגניס', 'בלנו', 'סוויפט', 'ראם', 'סילברדו'
]

# Engine code prefixes (common for VW, Audi, Skoda, etc.)
ENGINE_CODE_PREFIXES = [
    'CAX', 'CDA', 'CBZ', 'CJS', 'BTS', 'BSE', 'BLR', 'CAV', 'CJZ', 'CNC', 'CJE',
    'CJX', 'CAY', 'CRM', 'CGG', 'BMY', 'BLX', 'BLY', 'AXW', 'CRC'
]


def extract_car_models(text):
    """
    Extract car models from a given text with improved pattern matching and disambiguation

    Args:
        text: Text to extract car models from

    Returns:
        Dictionary with manufacturers, models, and all car references with confidence scores
    """
    # Creating specific patterns with word boundaries
    brand_patterns = {brand: re.compile(r'\b{0}\b'.format(re.escape(brand))) for brand in CAR_MANUFACTURERS.keys()}
    model_patterns = {model: re.compile(r'\b{0}\b'.format(re.escape(model))) for model in CAR_MODELS}

    # Engine code patterns - to help disambiguate from car models
    engine_code_pattern = re.compile(r'\b([A-Z]{2,4}[0-9]?)\b')
    engine_codes = set()

    # First identify possible engine codes to avoid misclassifying them as car models
    for match in engine_code_pattern.finditer(text):
        code = match.group(1)
        # Only consider it an engine code if it matches known patterns or contexts
        if code in ENGINE_CODE_PREFIXES or re.search(r'{0}\s+\d+\.\d+'.format(re.escape(code)), text):
            engine_codes.add(code)

    # Extract manufacturers with confidence scores
    manufacturers = []
    for brand, pattern in brand_patterns.items():
        if pattern.search(text):
            # Higher confidence if context words are also present
            confidence = 0.8
            # Check for model numbers after brand name
            if re.search(r'{0}\s+\d'.format(re.escape(brand)), text):
                confidence = 0.95

            manufacturers.append({
                'hebrew': brand,
                'english': CAR_MANUFACTURERS[brand],
                'confidence': confidence,
                'type': 'manufacturer'
            })

    # Extract models with confidence scores
    models = []
    for model, pattern in model_patterns.items():
        if pattern.search(text):
            # Skip if this matches a known engine code
            if model in engine_codes:
                continue

            # Default confidence
            confidence = 0.75

            # When model is referenced with a year, it's very likely a car model
            if re.search(r'{0}\s+מ\d{{2}}'.format(re.escape(model)), text) or re.search(
                    r'מ\d{{2}}\s+{0}'.format(re.escape(model)), text):
                confidence = 0.9

            # Higher confidence if it's a number/letter combo like I30, IX35
            if re.match(r'[A-Z]+\d+', model):
                confidence = 0.8

                # Check for Subaru specific models like XV, B3, B4
                if model in ['XV', 'B3', 'B4']:
                    # Look for Subaru context
                    if 'סובארו' in text or 'אימפרזה' in text or 'פורסטר' in text:
                        confidence = 0.9
                    else:
                        # These can be ambiguous - lower confidence if without context
                        confidence = 0.6

            # Higher confidence if it's a complete match with a manufacturer
            for brand in CAR_MANUFACTURERS.keys():
                if brand in text and model in text:
                    confidence = 0.9
                    break

            models.append({
                'name': model,
                'confidence': confidence,
                'type': 'model'
            })

    # Attempt to resolve car model-year associations
    year_patterns = [
        # Model followed by year: SX4 מ15
        (re.compile(r'(\b[A-Za-z0-9]+\b)\s+מ(\d{2})'), 0.9),
        # Year followed by model: מ15 SX4
        (re.compile(r'מ(\d{2})\s+(\b[A-Za-z0-9]+\b)'), 0.85),
        # Double association: 1.4 מ15 SX4 פ.אויר + ויטרה 1.4 מ15
        (re.compile(r'מ(\d{2})\s+(\b[A-Za-z0-9]+\b).+?(\b[A-Za-z0-9]+\b)\s+מ(\d{2})'), 0.95)
    ]

    car_year_associations = []

    for pattern, conf in year_patterns:
        for match in pattern.finditer(text):
            if len(match.groups()) == 2:  # Simple pattern
                model, year = match.groups() if match.group(1).isalnum() else (match.group(2), match.group(1))
                car_year_associations.append({
                    'model': model,
                    'year': "20{0}".format(year),
                    'confidence': conf
                })
            elif len(match.groups()) == 4:  # Complex pattern with multiple models
                model1, year1, model2, year2 = match.groups()
                car_year_associations.append({
                    'model': model1,
                    'year': "20{0}".format(year1),
                    'confidence': conf
                })
                car_year_associations.append({
                    'model': model2,
                    'year': "20{0}".format(year2),
                    'confidence': conf
                })

    # Remove duplicates from models and keep highest confidence
    unique_models = {}
    for model in models:
        name = model['name']
        if name not in unique_models or model['confidence'] > unique_models[name]['confidence']:
            unique_models[name] = model

    clean_models = list(unique_models.values())

    # Combine all car references
    all_refs = []
    for m in manufacturers:
        all_refs.append({
            'name': m['hebrew'],
            'type': 'manufacturer',
            'confidence': m['confidence']
        })

    for m in clean_models:
        all_refs.append({
            'name': m['name'],
            'type': 'model',
            'confidence': m['confidence']
        })

    return {
        'manufacturers': manufacturers,
        'models': clean_models,
        'all': all_refs,
        'car_year_associations': car_year_associations
    }


def extract_years(text):
    """
    Extract years from text with improved accuracy

    Args:
        text: Text to extract years from

    Returns:
        Dictionary with from_year, to_year and confidence
    """
    years = {}
    confidence = 0.0
    matched_patterns = 0

    # Pattern for "from year": מ09 (from 2009)
    from_match = re.search(r'מ(\d{2})', text)
    if from_match:
        years['from_year'] = int("20{0}".format(from_match.group(1)))
        confidence += 0.4
        matched_patterns += 1

    # Pattern for "to year": עד 12 (until 2012)
    to_match = re.search(r'עד\s*(\d{2})', text)
    if to_match:
        years['to_year'] = int("20{0}".format(to_match.group(1)))
        confidence += 0.4
        matched_patterns += 1

    # Pattern for year range: 06-08 (2006-2008)
    range_match = re.search(r'(\d{2})-(\d{2})', text)
    if range_match:
        # Don't overwrite if we already have more specific patterns
        if 'from_year' not in years:
            years['from_year'] = int("20{0}".format(range_match.group(1)))
        if 'to_year' not in years:
            years['to_year'] = int("20{0}".format(range_match.group(2)))
        confidence += 0.3
        matched_patterns += 1

    # Validate years
    current_year = 2025  # Using current year as reference
    if 'from_year' in years and years['from_year'] > current_year:
        confidence -= 0.2
    if 'to_year' in years and years['to_year'] > current_year:
        confidence -= 0.2

    # If both from and to years are present, make sure from < to
    if 'from_year' in years and 'to_year' in years:
        if years['from_year'] > years['to_year']:
            confidence -= 0.3
        else:
            confidence += 0.1

    # Normalize confidence for number of matched patterns
    if matched_patterns > 0:
        # Ensure confidence is between 0 and 1
        years['confidence'] = min(max(confidence, 0.0), 1.0)
    else:
        years['confidence'] = 0.0

    return years


def extract_drive_type(text):
    """
    Extract drive type (4x4, 4x2) information

    Args:
        text: Product description text

    Returns:
        Dictionary with drive type and confidence
    """
    result = {'drive_type': None, 'confidence': 0.0, 'drive_description': None}

    # Look for drive type patterns
    for drive_type, description in DRIVE_TYPE_MAP.items():
        if drive_type in text:
            result['drive_type'] = drive_type
            result['drive_description'] = description

            # Higher confidence if it's at the beginning or clearly separated
            if re.search(r'^\s*{0}'.format(re.escape(drive_type)), text) or re.search(
                    r'\s+{0}\s+'.format(re.escape(drive_type)), text):
                result['confidence'] = 0.9
            else:
                result['confidence'] = 0.7

            # Even higher if it appears with relevant context like "היילקס", "ויגו", etc.
            if any(model in text for model in ['היילקס', 'ויגו', 'דימקס', 'ראב 4', 'לנדקרוזר']):
                result['confidence'] = min(result['confidence'] + 0.1, 1.0)

            break

    return result


def extract_part_type(text):
    """
    Extract part type with improved accuracy

    Args:
        text: Product description text

    Returns:
        Dictionary with Hebrew and English part type and confidence
    """
    result = {
        'hebrew_type': None,
        'english_type': None,
        'confidence': 0.0
    }

    # First check for PK belts (high confidence)
    pk_match = re.search(r'(\d+)PK\s+\d+', text)
    if pk_match:
        result['hebrew_type'] = "{0}PK".format(pk_match.group(1))
        result['english_type'] = "{0}-Rib V-Belt".format(pk_match.group(1))
        result['confidence'] = 0.95
        return result

    # Then check for multiple part types
    found_types = []

    for hebrew, english in PART_TYPE_MAP.items():
        if hebrew in text:
            # Calculate position in text (earlier mentions are more likely to be correct)
            position = text.find(hebrew) / len(text)

            # Calculate confidence based on position and specificity
            confidence = 0.7 - (position * 0.2)

            # Boost confidence for longer, more specific terms
            if len(hebrew) > 4:
                confidence += 0.1

            # Boost confidence if it's at the beginning of the text
            if text.startswith(hebrew) or text.find(hebrew) < 5:
                confidence += 0.1

            found_types.append({
                'hebrew_type': hebrew,
                'english_type': english,
                'confidence': min(confidence, 0.95)  # Cap at 0.95
            })

    # If multiple types found, pick the one with highest confidence
    if found_types:
        found_types.sort(key=lambda x: x['confidence'], reverse=True)
        return found_types[0]

    return result


def extract_position(text):
    """
    Extract position information with confidence score

    Args:
        text: Product description text

    Returns:
        Dictionary with position and confidence
    """
    positions = []
    total_confidence = 0.0

    for hebrew, english in POSITION_MAP.items():
        if hebrew in text:
            # Base confidence
            confidence = 0.6

            # Boost for clear boundaries
            if re.search(r'\b{0}\b'.format(re.escape(hebrew)), text):
                confidence += 0.2

            # Context-specific boosts
            if hebrew in ['קדמי', 'אחורי'] and any(term in text for term in
                                                   ['דסקיות', 'צלחות', 'בולם', 'משולש']):
                confidence += 0.2

            if hebrew in ['ימין', 'שמאל'] and any(term in text for term in
                                                  ['משולש', 'בולם', 'ת.מנוע', 'קצה הגה']):
                confidence += 0.2

            positions.append({
                'position': english,
                'confidence': min(confidence, 0.95)
            })
            total_confidence += confidence

    if not positions:
        return {'position': None, 'confidence': 0.0}

    # Sort by confidence
    positions.sort(key=lambda x: x['confidence'], reverse=True)

    # Join positions, starting with the highest confidence ones
    position_text = '/'.join([p['position'] for p in positions])

    # Average confidence adjusted for number of positions found
    avg_confidence = min(total_confidence / len(positions), 0.95)
    if len(positions) > 1:
        avg_confidence = min(avg_confidence + 0.05, 0.95)  # Bonus for multiple matching positions

    return {
        'position': position_text,
        'confidence': avg_confidence,
        'details': positions
    }


def extract_dimensions(text):
    """
    Extract dimensions with improved pattern matching

    Args:
        text: Product description text

    Returns:
        Dictionary with dimension information and confidence
    """
    # PK belts with lengths
    pk_belt_match = re.search(r'\d+PK\s+(\d+)', text)
    if pk_belt_match:
        return {
            'value': pk_belt_match.group(1),
            'unit': 'mm',
            'type': 'length',
            'confidence': 0.95
        }

    # Specific dimension mentions with mm
    dimension_match = re.search(r'(\d+)\s*מ"מ|(\d+)\s*ממ', text)
    if dimension_match:
        value = dimension_match.group(1) or dimension_match.group(2)
        return {
            'value': value,
            'unit': 'mm',
            'type': 'dimension',
            'confidence': 0.9
        }

    # Diameters for brake discs
    diameter_match = re.search(r'קוטר\s*(\d+)', text)
    if diameter_match:
        return {
            'value': diameter_match.group(1),
            'unit': 'mm',
            'type': 'diameter',
            'confidence': 0.9
        }

    # Engine sizes
    engine_size_match = re.search(r'\b(\d+\.\d+)\b', text)
    if engine_size_match:
        size = engine_size_match.group(1)
        confidence = 0.7

        # Higher confidence if in valid engine size range
        if 0.5 <= float(size) <= 6.0:
            confidence = 0.85

        # Even higher if mentioned with engine-related terms
        if any(term in text for term in ['נפח', 'מנוע', 'CDA', 'CJS', 'BTS']):
            confidence = 0.95

        return {
            'value': size,
            'unit': 'L',
            'type': 'engine displacement',
            'confidence': confidence
        }

    return None


def extract_engine_info(text):
    """
    Extract engine-related information with improved disambiguation from car models

    Args:
        text: Product description text

    Returns:
        Dictionary with engine code, size and confidence
    """
    result = {
        'engine_code': None,
        'engine_size': None,
        'confidence': 0.0
    }

    # Priority match with known engine code patterns
    for prefix in ENGINE_CODE_PREFIXES:
        if prefix in text:
            # Check it's an actual code, not part of another word
            if re.search(r'\b{0}\b'.format(re.escape(prefix)), text):
                result['engine_code'] = prefix
                result['confidence'] = 0.9

                # Check if it's clearly in an engine context
                if re.search(r'{0}\s+\d+\.\d+'.format(re.escape(prefix)), text) or re.search(
                        r'\d+\.\d+\s+{0}'.format(re.escape(prefix)), text):
                    result['confidence'] = 0.95

                # Higher confidence if known to be problematic with car models
                if prefix in ['B3', 'B4', 'XV']:
                    # Only if strong engine context (like right before or after displacement)
                    if re.search(r'{0}\s+\d+\.\d+'.format(re.escape(prefix)), text) or re.search(
                            r'\d+\.\d+\s+{0}'.format(re.escape(prefix)), text):
                        result['confidence'] = 0.95
                    else:
                        # Otherwise be more cautious with these ambiguous codes
                        result['confidence'] = 0.7

                break

    # Look for other engine codes if none found yet
    if not result['engine_code']:
        # Look for standard engine code pattern (but not when it's likely a car model)
        engine_code_match = re.search(r'\b([A-Z]{2,4}[0-9]?)\b', text)
        if engine_code_match:
            code = engine_code_match.group(1)
            # Exclude common non-engine terms and car models
            if code not in ['ABS', 'VRS', 'GMT', 'LED', 'SX4', 'I20', 'I30', 'I35', 'I10', 'I25', 'CX5']:
                result['engine_code'] = code

                # Base confidence
                result['confidence'] = 0.6

                # Higher confidence if it's near engine size
                if re.search(r'{0}\s+\d+\.\d+'.format(re.escape(code)), text) or re.search(
                        r'\d+\.\d+\s+{0}'.format(re.escape(code)), text):
                    result['confidence'] = 0.8

    # Extract engine size with context validation
    engine_size_matches = list(re.finditer(r'\b(\d+\.\d+)\b', text))
    if engine_size_matches:
        # Multiple engine sizes could be mentioned - choose the most likely one
        best_size = None
        best_confidence = 0.0

        for match in engine_size_matches:
            size = match.group(1)
            float_size = float(size)

            # Only consider if in plausible range
            if 0.5 <= float_size <= 6.0:
                # Start with base confidence
                confidence = 0.6

                # Context check - is this clearly an engine size?
                pos = match.start()
                context_before = text[max(0, pos - 20):pos]
                context_after = text[match.end():min(len(text), match.end() + 20)]

                # Check for engine-related terms
                if any(term in context_before + context_after for term in ['נפח', 'מנוע', 'ליטר']):
                    confidence += 0.2

                # If near an engine code, much higher confidence
                if result['engine_code'] and (
                        result['engine_code'] in context_before[-15:] or
                        result['engine_code'] in context_after[:15]):
                    confidence += 0.3

                # For sizes that match common engine displacements, higher confidence
                if float_size in [1.0, 1.2, 1.3, 1.4, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.5, 2.7, 3.0, 3.5, 4.0, 5.0, 6.0]:
                    confidence += 0.1

                # Update best match if this is higher confidence
                if confidence > best_confidence:
                    best_size = size
                    best_confidence = confidence

        if best_size:
            result['engine_size'] = best_size
            # Update overall confidence
            if result['confidence'] < best_confidence:
                result['confidence'] = best_confidence

    return result


def calculate_overall_accuracy(parsed_data):
    """
    Calculate overall accuracy score based on individual confidence scores

    Args:
        parsed_data: Dictionary with parsed data and confidence scores

    Returns:
        Overall accuracy score (0.0-1.0)
    """
    # Weights for different elements
    weights = {
        'part_type': 0.25,
        'car_models': 0.20,
        'position': 0.15,
        'drive_type': 0.15,
        'years': 0.10,
        'dimensions': 0.10,
        'engine_info': 0.05
    }

    # Get confidences with defaults
    confidences = {
        'part_type': parsed_data.get('part_type_confidence', 0.0),
        'car_models': parsed_data.get('car_models_confidence', 0.0),
        'position': parsed_data.get('position_confidence', 0.0),
        'drive_type': parsed_data.get('drive_type_confidence', 0.0),
        'years': parsed_data.get('years_confidence', 0.0),
        'dimensions': parsed_data.get('dimensions_confidence', 0.0),
        'engine_info': parsed_data.get('engine_info_confidence', 0.0)
    }

    # Calculate weighted average
    weighted_sum = 0.0
    for key in weights:
        weighted_sum += weights[key] * confidences[key]

    total_weight = sum(weights.values())

    # Add bonus for number of elements successfully extracted
    elements_found = 0
    for conf in confidences.values():
        if conf > 0.5:
            elements_found += 1

    coverage_bonus = (elements_found / len(weights)) * 0.1

    accuracy = (weighted_sum / total_weight) + coverage_bonus

    # Ensure it's between 0 and 1
    return min(max(accuracy, 0.0), 1.0)


def extract_structured_data(text, print_results=False):
    """
    Extract structured data from a product description text

    Args:
        text: Product description text
        print_results: Whether to print detailed results

    Returns:
        Dictionary with structured data
    """
    text = text.strip()

    # Extract all data with individual confidence scores
    car_info = extract_car_models(text)
    years_info = extract_years(text)
    drive_type_info = extract_drive_type(text)
    part_type_info = extract_part_type(text)
    position_info = extract_position(text)
    dimensions_info = extract_dimensions(text)
    engine_info = extract_engine_info(text)

    # Process car-year associations for better accuracy
    car_models = []
    car_years = {}

    # Add models from car_year_associations with their associated years
    for assoc in car_info.get('car_year_associations', []):
        model = assoc['model']

        # Only include if it's a known car model (not an engine code or random text)
        if any(m['name'] == model for m in car_info.get('models', [])) or model in CAR_MODELS:
            car_models.append(model)
            # Store the year association for this car model
            if model not in car_years:
                car_years[model] = []
            car_years[model].append({
                'year': int(assoc['year']),
                'confidence': assoc['confidence']
            })

    # Add any remaining models that weren't in car_year_associations
    for model_info in car_info.get('models', []):
        model = model_info['name']
        if model not in car_models:
            car_models.append(model)

    # Remove potential engine codes that were incorrectly identified as car models
    # Especially for short codes like B3, B4, XV when not in context with their manufacturer
    filtered_car_models = []
    for model in car_models:
        # Skip if this is a potential engine code without clear context
        if model in ['B3', 'B4', 'CDA', 'CJS', 'CAX'] and model in text:
            # Check if it's used in an engine code context
            if re.search(r'\b{0}\s+\d+\.\d+'.format(re.escape(model)), text) or re.search(
                    r'\d+\.\d+\s+{0}'.format(re.escape(model)), text):
                # This appears to be an engine code reference, not a car model
                continue

            # For B3, B4 check if likely a Subaru model
            if model in ['B3', 'B4']:
                # If no Subaru context but common engine contexts, skip it
                if not ('סובארו' in text or 'אימפרזה' in text or 'פורסטר' in text) and \
                        any(term in text for term in ['נפח', 'מנוע', 'סמ"ק']):
                    continue

            # For XV check if likely a Subaru model
            if model == 'XV':
                # If XV is not clearly associated with Subaru context, be cautious
                if not ('סובארו' in text or 'אימפרזה' in text or 'פורסטר' in text):
                    # Unless it has a strong year association
                    if model not in car_years:
                        continue

        filtered_car_models.append(model)

    # Get manufacturer string if any are found
    manufacturer_str = ""
    if car_info['manufacturers']:
        # Get the manufacturer with highest confidence
        top_manufacturer = sorted(car_info['manufacturers'], key=lambda x: x['confidence'], reverse=True)[0]
        manufacturer_str = "{0} ({1})".format(top_manufacturer['hebrew'], top_manufacturer['english'])

    # Get car models string if any are found (comma separated)
    car_models_str = ", ".join(filtered_car_models) if filtered_car_models else ""

    # Prepare result dictionary
    result = {
        'raw_text': text,

        # Car model information
        'car_models': car_models_str,
        'manufacturer': manufacturer_str,
        'car_models_confidence': max([item['confidence'] for item in car_info['all']]) if car_info['all'] else 0.0,

        # Position and drive type
        'position': position_info['position'],
        'position_confidence': position_info['confidence'],
        'drive_type': drive_type_info['drive_type'],
        'drive_type_description': drive_type_info.get('drive_description'),
        'drive_type_confidence': drive_type_info['confidence'],

        # Part type
        'part_type_hebrew': part_type_info['hebrew_type'],
        'part_type_english': part_type_info['english_type'],
        'part_type_confidence': part_type_info['confidence'],

        # Years
        'from_year': years_info.get('from_year'),
        'to_year': years_info.get('to_year'),
        'years_confidence': years_info.get('confidence', 0.0),

        # Dimensions
        'dimension_value': dimensions_info['value'] if dimensions_info else None,
        'dimension_unit': dimensions_info['unit'] if dimensions_info else None,
        'dimension_type': dimensions_info['type'] if dimensions_info else None,
        'dimensions_confidence': dimensions_info['confidence'] if dimensions_info else 0.0,

        # Engine information
        'engine_code': engine_info['engine_code'],
        'engine_size': engine_info['engine_size'],
        'engine_info_confidence': engine_info['confidence']
    }

    # Calculate overall accuracy score
    result['accuracy'] = calculate_overall_accuracy(result)

    # Print detailed results if requested
    if print_results:
        print("\nAnalyzing: '{0}'".format(text))
        print("=" * 50)

        # Part type
        if result['part_type_english']:
            print("Part Type: {0} ({1})".format(result['part_type_english'], result['part_type_hebrew']))
            print("  ├─ Confidence: {0:.2f}".format(result['part_type_confidence']))
        else:
            print("Part Type: Not detected")

        # Car models and manufacturers
        if result['car_models']:
            print("\nCar Models: {0}".format(result['car_models']))
            print("  ├─ Confidence: {0:.2f}".format(result['car_models_confidence']))
        else:
            print("\nCar Models: None detected")

        if result['manufacturer']:
            print("\nManufacturer: {0}".format(result['manufacturer']))

        # Position and drive type
        if result['position']:
            print("\nPosition: {0}".format(result['position']))
            print("  ├─ Confidence: {0:.2f}".format(result['position_confidence']))

        if result['drive_type']:
            print("\nDrive Type: {0} ({1})".format(result['drive_type'], result['drive_type_description']))
            print("  ├─ Confidence: {0:.2f}".format(result['drive_type_confidence']))

        # Years
        if result.get('from_year') or result.get('to_year'):
            year_str = ""
            if result.get('from_year'):
                year_str += "From {0} ".format(result['from_year'])
            if result.get('to_year'):
                year_str += "To {0}".format(result['to_year'])
            print("\nYears: {0}".format(year_str.strip()))
            print("  ├─ Confidence: {0:.2f}".format(result['years_confidence']))

        # Dimensions
        if result['dimension_value']:
            print("\nDimensions: {0} {1} ({2})".format(result['dimension_value'], result['dimension_unit'],
                                                       result['dimension_type']))
            print("  ├─ Confidence: {0:.2f}".format(result['dimensions_confidence']))

        # Engine information
        if result['engine_code'] or result['engine_size']:
            engine_info = ""
            if result['engine_code']:
                engine_info += "Code: {0} ".format(result['engine_code'])
            if result['engine_size']:
                engine_info += "Size: {0}L".format(result['engine_size'])
            print("\nEngine: {0}".format(engine_info.strip()))
            print("  ├─ Confidence: {0:.2f}".format(result['engine_info_confidence']))

        # Overall accuracy
        print("\nOverall Accuracy: {0:.2f}".format(result['accuracy']))
        print("=" * 50)

    return result


def analyze_part_details(text):
    """
    Analyze part details from text (wrapper for extract_structured_data)

    Args:
        text: Part description text

    Returns:
        Dictionary with structured data
    """
    return extract_structured_data(text, print_results=True)


def create_database(db_path, data_lines):
    """
    Create and populate the database with structured data

    Args:
        db_path: Path to the database file
        data_lines: List of text lines to process

    Returns:
        None
    """
    # Delete database if exists
    if os.path.exists(db_path):
        os.remove(db_path)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create a single comprehensive table
    cursor.execute('''
    CREATE TABLE car_parts (
        id INTEGER PRIMARY KEY,
        raw_text TEXT NOT NULL,
        part_type_hebrew TEXT,
        part_type_english TEXT,
        manufacturer TEXT,
        car_models TEXT,
        position TEXT,
        drive_type TEXT,
        drive_type_description TEXT,
        from_year INTEGER,
        to_year INTEGER,
        dimension_value TEXT,
        dimension_unit TEXT,
        dimension_type TEXT,
        engine_code TEXT,
        engine_size TEXT,

        part_type_confidence REAL,
        car_models_confidence REAL,
        position_confidence REAL,
        drive_type_confidence REAL,
        years_confidence REAL,
        dimensions_confidence REAL,
        engine_info_confidence REAL,

        accuracy REAL
    )
    ''')

    # Begin transaction
    conn.execute('BEGIN TRANSACTION')

    # Process each line
    processed_count = 0

    for i, line in enumerate(data_lines):
        part_id = i + 1
        line = line.strip()

        if not line:
            continue

        data = extract_structured_data(line)

        # Insert record into the single table
        cursor.execute('''
        INSERT INTO car_parts (
            id, raw_text, part_type_hebrew, part_type_english, manufacturer, car_models, 
            position, drive_type, drive_type_description, from_year, to_year, 
            dimension_value, dimension_unit, dimension_type, engine_code, engine_size,

            part_type_confidence, car_models_confidence, position_confidence,
            drive_type_confidence, years_confidence, dimensions_confidence,
            engine_info_confidence,

            accuracy
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            part_id,
            data['raw_text'],
            data['part_type_hebrew'],
            data['part_type_english'],
            data['manufacturer'],
            data['car_models'],
            data['position'],
            data['drive_type'],
            data['drive_type_description'],
            data['from_year'],
            data['to_year'],
            data['dimension_value'],
            data['dimension_unit'],
            data['dimension_type'],
            data['engine_code'],
            data['engine_size'],

            data.get('part_type_confidence', 0.0),
            data.get('car_models_confidence', 0.0),
            data.get('position_confidence', 0.0),
            data.get('drive_type_confidence', 0.0),
            data.get('years_confidence', 0.0),
            data.get('dimensions_confidence', 0.0),
            data.get('engine_info_confidence', 0.0),

            data['accuracy']
        ))

        processed_count += 1

        # Log progress
        if processed_count % 500 == 0:
            print("Processed {0} items...".format(processed_count))

    # Create indices for better query performance
    print("Creating indices...")
    cursor.execute('CREATE INDEX idx_parts_type ON car_parts(part_type_english)')
    cursor.execute('CREATE INDEX idx_parts_drive ON car_parts(drive_type)')
    cursor.execute('CREATE INDEX idx_parts_accuracy ON car_parts(accuracy)')
    cursor.execute('CREATE INDEX idx_car_models ON car_parts(car_models)')
    cursor.execute('CREATE INDEX idx_manufacturer ON car_parts(manufacturer)')
    cursor.execute('CREATE INDEX idx_from_year ON car_parts(from_year)')

    # Commit transaction
    conn.commit()

    # Close connection
    conn.close()

    print("Database creation complete. Processed {0} parts.".format(processed_count))


def analyze_test_examples():
    """
    Analyze a set of test examples to validate the parser

    Returns:
        List of analysis results
    """
    test_examples = [
        "+ XV מ12 דסקיות קדמי מ04 B4",
        "1.6 ת.מנוע ימין מזדה 3 מ09",
        "124X דסקיות אחורי אוקטביה מ13",
        "4x4 דימקס מ12 משולש עליון ימין",
        "4x2 ויגו 06-07 דסקיות קדמי",
        "1.8 CDA צינור נשם",
        "CJS 1.8 מיכל עיבוי אוקטביה מ13",
        "I30 + יוניט חום גטס + I20 + אקסנט",
        "6PK 1230 קורולה מ08",
        "T5 פ.מזגן",
        "טוסון מ21",
        "מזדה 3 מ13 נפח 1.5"
    ]

    print("\nTesting parser with sample entries...")

    results = []
    for example in test_examples:
        result = analyze_part_details(example)
        results.append(result)

    return results


def analyze_accuracy_statistics(db_path):
    """
    Analyze accuracy statistics from the database

    Args:
        db_path: Path to the database file

    Returns:
        Dictionary with accuracy statistics
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    stats = {}

    # Overall accuracy distribution
    cursor.execute('''
    SELECT 
        COUNT(*) as total,
        AVG(accuracy) as avg_accuracy,
        MIN(accuracy) as min_accuracy,
        MAX(accuracy) as max_accuracy,
        SUM(CASE WHEN accuracy >= 0.8 THEN 1 ELSE 0 END) as high_accuracy,
        SUM(CASE WHEN accuracy >= 0.6 AND accuracy < 0.8 THEN 1 ELSE 0 END) as medium_accuracy,
        SUM(CASE WHEN accuracy < 0.6 THEN 1 ELSE 0 END) as low_accuracy
    FROM car_parts
    ''')

    row = cursor.fetchone()
    stats['overall'] = {
        'total': row[0],
        'avg_accuracy': row[1],
        'min_accuracy': row[2],
        'max_accuracy': row[3],
        'high_accuracy_count': row[4],
        'high_accuracy_percent': (row[4] / row[0]) * 100 if row[0] > 0 else 0,
        'medium_accuracy_count': row[5],
        'medium_accuracy_percent': (row[5] / row[0]) * 100 if row[0] > 0 else 0,
        'low_accuracy_count': row[6],
        'low_accuracy_percent': (row[6] / row[0]) * 100 if row[0] > 0 else 0,
    }

    # Accuracy by part type
    cursor.execute('''
    SELECT 
        part_type_english,
        COUNT(*) as count,
        AVG(accuracy) as avg_accuracy
    FROM car_parts
    WHERE part_type_english IS NOT NULL
    GROUP BY part_type_english
    ORDER BY count DESC
    LIMIT 10
    ''')

    stats['by_part_type'] = [
        {
            'part_type': row[0],
            'count': row[1],
            'avg_accuracy': row[2]
        }
        for row in cursor.fetchall()
    ]

    # Accuracy by car model (extracting from the car_models text field)
    cursor.execute('''
    SELECT 
        car_models,
        COUNT(*) as count,
        AVG(accuracy) as avg_accuracy
    FROM car_parts
    WHERE car_models IS NOT NULL AND car_models != ''
    GROUP BY car_models
    ORDER BY count DESC
    LIMIT 10
    ''')

    stats['by_car_model'] = [
        {
            'car_model': row[0],
            'count': row[1],
            'avg_accuracy': row[2]
        }
        for row in cursor.fetchall()
    ]

    # Confidence by field
    cursor.execute('''
    SELECT 
        AVG(part_type_confidence) as avg_part_type_confidence,
        AVG(position_confidence) as avg_position_confidence,
        AVG(drive_type_confidence) as avg_drive_type_confidence,
        AVG(years_confidence) as avg_years_confidence,
        AVG(dimensions_confidence) as avg_dimensions_confidence,
        AVG(engine_info_confidence) as avg_engine_info_confidence
    FROM car_parts
    ''')

    row = cursor.fetchone()
    stats['field_confidence'] = {
        'part_type': row[0],
        'position': row[1],
        'drive_type': row[2],
        'years': row[3],
        'dimensions': row[4],
        'engine_info': row[5]
    }

    conn.close()

    return stats


def main():
    """Main function to read file and create database"""
    # File paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, 'resources/btw_filenames.txt')
    db_path = os.path.join(current_dir, 'database/car_parts.db')

    print("Processing file: {0}".format(data_path))
    print("Output database: {0}".format(db_path))

    # Check if the file exists
    if not os.path.exists(data_path):
        print("Error: File {0} not found!".format(data_path))
        print("Please place the btw_filenames.txt file in the same directory as the script.")
        return

    # Read file
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        print("Found {0} parts in the file.".format(len(lines)))
    except Exception as e:
        print("Error reading file: {0}".format(e))
        return

    # Run a quick test on sample entries
    print("\nTesting parser before database creation...")
    test_results = analyze_test_examples()

    # Create database
    print("\nCreating database...")
    try:
        create_database(db_path, lines)
    except Exception as e:
        print("Error creating database: {0}".format(e))
        return

    # Analyze accuracy
    print("\nAnalyzing accuracy statistics...")
    try:
        stats = analyze_accuracy_statistics(db_path)
    except Exception as e:
        print("Error analyzing statistics: {0}".format(e))
        return

    # Print statistics
    print("\nAccuracy Statistics:")
    print("Total parts processed: {0}".format(stats['overall']['total']))
    print("Average accuracy: {0:.2f}".format(stats['overall']['avg_accuracy']))
    print("High accuracy parts (>=0.8): {0:.1f}%".format(stats['overall']['high_accuracy_percent']))
    print("Medium accuracy parts (0.6-0.8): {0:.1f}%".format(stats['overall']['medium_accuracy_percent']))
    print("Low accuracy parts (<0.6): {0:.1f}%".format(stats['overall']['low_accuracy_percent']))

    print("\nTop 5 part types by count:")
    for i, pt in enumerate(stats['by_part_type'][:5]):
        print("{0}. {1}: {2} parts, avg accuracy: {3:.2f}".format(i + 1, pt['part_type'], pt['count'],
                                                                  pt['avg_accuracy']))

    print("\nTop 5 car models by count:")
    for i, cm in enumerate(stats['by_car_model'][:5]):
        print("{0}. {1}: {2} parts, avg accuracy: {3:.2f}".format(i + 1, cm['car_model'], cm['count'],
                                                                  cm['avg_accuracy']))

    print("\nAverage confidence by field:")
    for field, value in stats['field_confidence'].items():
        print("{0}: {1:.2f}".format(field, value))

    print("\nSQLite database created at: {0}".format(db_path))


if __name__ == "__main__":
    main()