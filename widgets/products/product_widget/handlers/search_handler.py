class SearchHandler:
    """
    Simplified search handler that only checks if search terms exist in product barcode or name.
    """

    def __init__(self, translator):
        self.translator = translator
        self.last_search_term = ""

    def search_products(self, products, search_term):
        """
        Simple search for products where search term appears in barcode or product name

        Args:
            products: List of products to search
            search_term: Search term

        Returns:
            tuple: (filtered_products, message)
        """
        search_term = search_term.strip().lower()
        self.last_search_term = search_term

        if not search_term:
            return products, None

        # Split search term into words for multi-word search
        search_words = search_term.split()

        # Filter products that match search criteria
        filtered_products = []

        for product in products:
            if self._product_matches_search(product, search_words, search_term):
                filtered_products.append(product)

        # Prepare message
        if filtered_products:
            message = self.translator.t('search_results_found').format(
                count=len(filtered_products),
                term=search_term
            )
        else:
            message = self.translator.t('no_search_results').format(term=search_term)

        return filtered_products, message

    def _product_matches_search(self, product, search_words, full_search_term):
        """
        Check if a product matches search criteria with tolerance for word order

        Args:
            product: Product to check (dict or tuple)
            search_words: List of search words (lowercase)
            full_search_term: Complete search term for exact matching

        Returns:
            bool: True if product matches search criteria, False otherwise
        """
        try:
            # Handle dict format
            if isinstance(product, dict):
                barcode = str(product.get('parcode', '')).lower()
                product_name = str(product.get('product_name', '')).lower()
            # Handle tuple format
            else:
                # Assuming index 0 is id/barcode and index 2 is product_name based on original code
                barcode = str(product[0]).lower() if len(product) > 0 else ''
                product_name = str(product[2]).lower() if len(product) > 2 else ''

            # Check barcode - exact match or contains full search term
            if barcode == full_search_term or full_search_term in barcode:
                return True

            # Check product name with more tolerance
            # First try exact match of the whole search phrase
            if full_search_term in product_name:
                return True

            # Then check if all individual words appear in product name
            if all(word in product_name for word in search_words):
                return True

            return False

        except Exception as e:
            print(f"Error matching product: {e}")
            return False

    def get_last_search_term(self):
        """Get the last search term"""
        return self.last_search_term

    def clear_last_search(self):
        """Clear the last search term"""
        self.last_search_term = ""

    # Keep this method for compatibility but simplify its implementation
    def advanced_search(self, products, criteria):
        """
        Simplified advanced search - just uses the basic search for compatibility

        Args:
            products: List of products
            criteria: Dict of field:value pairs to search for

        Returns:
            tuple: (filtered_products, message)
        """
        if not criteria or not products:
            return products, None

        # Just use any non-empty criteria as search terms
        search_terms = []
        for value in criteria.values():
            if value:
                search_terms.append(str(value).lower())

        # Join the terms and use the standard search
        combined_term = " ".join(search_terms)
        if combined_term:
            return self.search_products(products, combined_term)
        else:
            return products, None