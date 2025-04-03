# gui/__init__.py
# Makes the gui folder a proper Python package that exports the main GUI class

from .gui_main import GUI

__all__ = ['GUI']