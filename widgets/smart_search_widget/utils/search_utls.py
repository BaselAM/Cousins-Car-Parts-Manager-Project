"""
Search utility functions for Smart Search Widget.
"""

# Try to import theme and logger modules - handle gracefully if not available
try:
    from logger import get_logger
    logger = get_logger('widgets.smart_search_widget.utils')
except ImportError:
    # Simple fallback logger if the standard logger is unavailable
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('widgets.smart_search_widget.utils')

def product_matches_search(product, search_text, search_words):
    """
    Check if a product matches the search text.

    Args:
        product: Product dictionary or tuple to check
        search_text: Complete search string (lowercase)
        search_words: Search string split into individual words

    Returns:
        bool: True if product matches search criteria, False otherwise
    """
    # Get product details to check against
    if isinstance(product, dict):
        parcode = str(product.get('parcode', '')).lower()
        product_name = str(product.get('product_name', '')).lower()
        category = str(product.get('category', '')).lower()
    else:  # tuple
        parcode = str(product[0]).lower() if len(product) > 0 else ''
        product_name = str(product[2]).lower() if len(product) > 2 else ''
        category = str(product[1]).lower() if len(product) > 1 else ''

    # 1. Check parcode (exact match or contains)
    if parcode == search_text or search_text in parcode:
        return True

    # 2. Check if entire search text appears in product name or category
    if search_text in product_name or search_text in category:
        return True

    # 3. Check if all individual words appear in the name or category
    if len(search_words) > 1:
        all_words_found = True
        for word in search_words:
            if word not in product_name and word not in category:
                all_words_found = False
                break
        if all_words_found:
            return True

    return False