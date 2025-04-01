"""
Parts navigation package for the car parts system.

This module provides a hierarchical navigation system for selecting car parts
through a step-by-step process:
1. Select a car brand
2. Select a car model
3. Select a model year
4. Select a part category
5. Select a specific product
6. Configure product details
7. View final part information

The main entry point is the PartsNavigationContainer class, which manages
the entire navigation process.
"""
# Import the main container for easy access
from .main_container import PartsNavigationContainer

# Export only what's needed for external use
__all__ = ['PartsNavigationContainer']