"""
Components for the Smart Search Widget.
"""

from .product_card import ProductCard
from .floating_action_button import FloatingActionButton
from .duplicate_dialog import DuplicateProductDialog
from .barcode_adapter import BarcodeDialogAdapter, ScanningDialog

__all__ = [
    'ProductCard',
    'FloatingActionButton',
    'DuplicateProductDialog',
    'BarcodeDialogAdapter',
    'ScanningDialog'
]