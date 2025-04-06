# db_config.py
"""Database configuration settings for the car parts database."""

# Database connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'CousinsBusiness321$',
    'database': 'car_parts_system'
}

# Connection pool settings
POOL_CONFIG = {
    'pool_size': 10,
    'pool_name': 'car_parts_pool',
    'connect_timeout': 10,  # seconds
    'pool_reset_session': True
}