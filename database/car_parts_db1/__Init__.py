"""
Car Parts Database Module - Thread-safe database handler for car parts inventory.

This package provides functionality for managing a car parts inventory database
with MySQL backend, connection pooling, and transaction management.

Example usage:
    from car_parts_db import CarPartsDB

    # Create a database connection
    db = CarPartsDB()

    # Add a part
    db.add_part("Brakes", "Disc Brake", quantity=10, price=99.99)

    # Use a transaction
    with db.transaction():
        db.update_part(1, quantity=15)
        db.update_part(2, price=49.99)
"""

# Import the main class for direct access
from database.car_parts_db import CarPartsDB

# Import custom exceptions
from .db_connection import DatabaseConnectionError

# Define what gets imported with "from car_parts_db import *"
__all__ = [
    'CarPartsDB',
    'DatabaseConnectionError',
]

# Package metadata
__version__ = '1.0.0'