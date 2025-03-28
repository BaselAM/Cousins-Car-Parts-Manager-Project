#!/usr/bin/env python3
"""
Script to test and verify the car parts database after import.
Shows statistics about the database entries.
"""

import logging
import sqlite3
from collections import Counter
from database.car_parts_db import CarPartsDB

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_script')


def show_db_statistics(db):
    """Show various statistics about the database entries."""
    try:
        # Count total parts
        total_count = db.count_parts()
        logger.info(f"Total parts in database: {total_count}")

        # Get all parts
        all_parts = db.get_all_parts()
        if not all_parts:
            logger.warning("No parts found in database")
            return

        # Analyze categories
        categories = Counter()
        for part in all_parts:
            categories[part[1]] += 1  # category is at index 1

        logger.info("\nCategory distribution:")
        for category, count in categories.most_common():
            percentage = (count / total_count) * 100
            logger.info(f"  {category}: {count} parts ({percentage:.1f}%)")

        # Analyze car brands
        car_brands = Counter()
        for part in all_parts:
            car_brands[part[2]] += 1  # car_name is at index 2

        logger.info("\nCar brand distribution:")
        for brand, count in car_brands.most_common(15):  # Top 15 brands
            percentage = (count / total_count) * 100
            logger.info(f"  {brand}: {count} parts ({percentage:.1f}%)")

        # Analyze models (sample for top brands)
        logger.info("\nModel distribution for top brands:")
        for brand, _ in car_brands.most_common(5):  # Top 5 brands
            models = Counter()
            for part in all_parts:
                if part[2] == brand:  # If car_name matches brand
                    models[part[3]] += 1  # model is at index 3

            logger.info(f"\n  {brand} models:")
            for model, count in models.most_common(5):  # Top 5 models for each brand
                brand_total = car_brands[brand]
                percentage = (count / brand_total) * 100
                logger.info(f"    {model}: {count} parts ({percentage:.1f}% of {brand})")

        # Show sample entries
        logger.info("\nSample database entries:")
        for i, part in enumerate(all_parts[:5]):  # First 5 entries
            logger.info(f"\nEntry {i + 1}:")
            logger.info(f"  ID: {part[0]}")
            logger.info(f"  Category: {part[1]}")
            logger.info(f"  Car Brand: {part[2]}")
            logger.info(f"  Model: {part[3]}")
            logger.info(f"  Product Name: {part[4]}")
            logger.info(f"  Quantity: {part[5]}")
            logger.info(f"  Price: {part[6]}")
            logger.info(f"  Last Updated: {part[7]}")

    except sqlite3.Error as e:
        logger.error(f"Database error: {str(e)}")
    except Exception as e:
        logger.error(f"Error analyzing database: {str(e)}")


def search_examples(db):
    """Demonstrate search functionality with examples."""
    logger.info("\nSearch Examples:")

    # Search by brand
    search_term = "מזדה"  # Mazda in Hebrew
    results = db.search_parts(search_term)
    logger.info(f"\nSearch for '{search_term}' returned {len(results)} results")

    if results:
        logger.info("First 3 results:")
        for part in results[:3]:
            logger.info(f"  {part[4]}")  # product_name

    # Search by part type
    search_term = "פ.אויר"  # Air filter in Hebrew
    results = db.search_parts(search_term)
    logger.info(f"\nSearch for '{search_term}' returned {len(results)} results")

    if results:
        logger.info("First 3 results:")
        for part in results[:3]:
            logger.info(f"  {part[4]}")  # product_name

    # Search by model
    search_term = "I30"  # Hyundai i30
    results = db.search_parts(search_term)
    logger.info(f"\nSearch for '{search_term}' returned {len(results)} results")

    if results:
        logger.info("First 3 results:")
        for part in results[:3]:
            logger.info(f"  {part[4]}")  # product_name


def suggest_autocomplete(db):
    """Test the autocomplete function."""
    logger.info("\nAutocompletion Examples:")

    test_terms = ["פ.אויר", "דסקיות", "מזדה", "אוקטביה"]

    for term in test_terms:
        suggestions = db.search_products_starting_with(term)
        logger.info(f"\nAutocomplete suggestions for '{term}':")
        for suggestion in suggestions:
            logger.info(f"  {suggestion}")


def main():
    """Main function."""
    logger.info("Starting database test and analysis")

    try:
        # Create database connection
        db = CarPartsDB()
        logger.info("Connected to database")

        # Show database statistics
        show_db_statistics(db)

        # Demonstrate search functionality
        search_examples(db)

        # Test autocomplete
        suggest_autocomplete(db)

    except Exception as e:
        logger.error(f"Error: {str(e)}")
    finally:
        if 'db' in locals():
            db.close_connection()
            logger.info("Database connection closed")


if __name__ == "__main__":
    main()