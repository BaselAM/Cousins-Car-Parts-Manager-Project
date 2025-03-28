class SearchHandler:
    """Handles product search functionality with improved matching capabilities"""

    def __init__(self, translator):
        self.translator = translator
        # Import translations functions only when needed to avoid circular imports
        try:
            from translations.data_translations import translate_category, translate_brand, translate_compatible_models
            self.translate_category = translate_category
            self.translate_brand = translate_brand
            self.translate_compatible_models = translate_compatible_models
            self.translations_available = True
        except ImportError:
            self.translations_available = False

    def search_products(self, all_products, search_text):
        """
        Search products based on search text with improved matching

        Args:
            all_products: List of all products
            search_text: Text to search for

        Returns:
            tuple: (filtered_products, message)
        """
        search_text = search_text.lower().strip()
        if not search_text:
            return all_products, None

        # Prepare search terms (split by spaces for multi-term search)
        search_terms = search_text.split()

        # Start with all products
        filtered_products = []

        for product in all_products:
            # Skip invalid products
            if not product:
                continue

            # Build a complete searchable text for this product
            searchable_text = self._build_searchable_text(product)

            # Check if ALL search terms appear in this product
            if all(term in searchable_text for term in search_terms):
                filtered_products.append(product)

        if len(filtered_products) < len(all_products):
            message = self.translator.t('search_results').format(
                count=len(filtered_products),
                total=len(all_products)
            )
            return filtered_products, message

        return filtered_products, None

    def _build_searchable_text(self, product):
        """Build a searchable text string from product data including translations"""
        # Get base searchable text from original data
        basic_fields = [
            str(product[1] or "").lower(),  # category
            str(product[2] or "").lower(),  # product_name
            str(product[6] or "").lower(),  # compatible_models
        ]
        searchable_text = " ".join(basic_fields)

        # If translations are available, add translated values to searchable text
        if self.translations_available:
            try:
                # Add translated category
                if product[1]:
                    translated_category = self.translate_category(product[1], 'he').lower()
                    searchable_text += " " + translated_category

                # Add translated compatible_models
                if product[6]:
                    translated_models = self.translate_compatible_models(product[6], 'he').lower()
                    searchable_text += " " + translated_models
            except Exception as e:
                print(f"Error including translations in search: {e}")

        return searchable_text