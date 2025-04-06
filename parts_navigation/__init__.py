"""
Parts Navigation Package

A premium step-by-step navigation system for selecting car parts with elegant
styling and smooth animations.
"""
# Import with error handling
try:
    from .parts_navigation_container import PartsNavigationContainer
    # Export only the main container class for simplicity
    __all__ = ['PartsNavigationContainer']
except ImportError as e:
    import sys
    # Create a placeholder class
    class PartsNavigationContainer:
        """Placeholder for when the real implementation is not available"""
        def __init__(self, *args, **kwargs):
            pass

        def cleanup_animations(self):
            pass

    # Export the placeholder
    __all__ = ['PartsNavigationContainer']

    # Log the error but don't crash
    print(f"Warning: Parts navigation module not fully loaded: {e}", file=sys.stderr)