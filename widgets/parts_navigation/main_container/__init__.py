"""
Premium parts navigation package for the car parts system.

This module provides a hierarchical navigation system for selecting car parts
through a step-by-step process with a premium iOS-inspired design:
1. Select a car brand
2. Select a car model
3. Select a model year
4. Select a part category
5. Select a specific product
6. Configure product details
7. View final part information

The main entry point is the PremiumPartsNavigation class, which manages
the entire navigation process with elegant animations and styling.
"""
# Import the main container for easy access
from .premium_parts_navigation import PartsNavigationContainer

# Legacy container for backward compatibility


# Export only what's needed for external use
__all__ = ['PartsNavigationContainer']