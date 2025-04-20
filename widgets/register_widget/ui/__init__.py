"""
UI components for the register widget.
"""

from .enhanced_scroll_bar import EnhancedScrollBar
from .dialogs import (
    CustomDialog, InfoDialog, WarningDialog,
    ErrorDialog, SuccessDialog, ConfirmationDialog
)
from .quantity_selector import QuantitySelector
from .cart import CartItem, CartWidget
from .product import ProductDetailCard
from .enhanced_search  import EnhancedSearchBox

# Import from our new shared search components module instead of enhanced_search
from search_components import SearchEdit, SearchDropdown
# Define EnhancedSearchBox from the refactored enhanced_search.py
from .enhanced_search import EnhancedSearchBox
# For backward compatibility, export the old names
FixedSearchDropdown = SearchDropdown
FixedSearchEdit = SearchEdit

from .empty_state import EmptyStateWidget

__all__ = [
    'EnhancedScrollBar',
    'CustomDialog', 'InfoDialog', 'WarningDialog',
    'ErrorDialog', 'SuccessDialog', 'ConfirmationDialog',
    'QuantitySelector',
    'CartItem', 'CartWidget',
    'ProductDetailCard',
    'EnhancedSearchBox',
    'EnhancedSearchBox', 'FixedSearchDropdown', 'FixedSearchEdit',
    'EmptyStateWidget'
]