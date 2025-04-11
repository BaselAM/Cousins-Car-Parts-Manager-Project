class SearchHandler:
    """
    Advanced search handler with priority-based ranking of results.
    Search results are sorted by relevance based on priorities and match quality.
    """

    def __init__(self, translator):
        self.translator = translator
        self.last_search_term = ""

        # Define field priorities (higher number = higher priority)
        self.field_priorities = {
            # Dictionary field priorities
            'parcode': 100,
            'product_name': 90,
            'manufacturer': 60,  # Changed from 'compatible_models'
            'compatible_brands': 50,
            'id': 30,
            'quantity': 10,
            'price': 10
        }

        # Tuple field indices with priorities
        self.tuple_priorities = {
            0: 30,  # id
            2: 90,  # product_name
            14: 60  # manufacturer (at index 14)
        }

    def search_products(self, products, search_term):
        """
        Advanced search products with priority-based ranking

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

        # Array of tuples: (product, score)
        scored_products = []

        # Process each product
        for product in products:
            score = self._calculate_product_score(product, search_term)
            if score > 0:
                scored_products.append((product, score))

        # Sort by score (descending)
        scored_products.sort(key=lambda x: x[1], reverse=True)

        # Extract just the products
        filtered_products = [p[0] for p in scored_products]

        # Prepare message
        if filtered_products:
            message = self.translator.t('search_results_found').format(
                count=len(filtered_products),
                term=search_term
            )
        else:
            message = self.translator.t('no_search_results').format(term=search_term)

        return filtered_products, message

    def _calculate_product_score(self, product, search_term):
        """
        Calculate a relevance score for a product based on how well it matches the search term

        Args:
            product: Product to check (dict or tuple)
            search_term: Search term (lowercase)

        Returns:
            int: Relevance score (0 = no match, higher = better match)
        """
        score = 0
        exact_match_bonus = 50  # Extra points for exact matches

        try:
            # Handle dict format
            if isinstance(product, dict):
                for field, priority in self.field_priorities.items():
                    if field in product and product[field] is not None:
                        field_value = str(product[field]).lower()

                        # Exact match
                        if field_value == search_term:
                            score += priority + exact_match_bonus

                        # Partial match
                        elif search_term in field_value:
                            # Calculate partial match score based on how much of the field is matched
                            match_percentage = len(search_term) / len(field_value) if len(field_value) > 0 else 0
                            partial_score = priority * match_percentage
                            score += partial_score

                            # Small bonus if match is at start of field
                            if field_value.startswith(search_term):
                                score += priority * 0.2  # 20% bonus

            # Handle tuple format
            else:
                for idx, priority in self.tuple_priorities.items():
                    if idx < len(product) and product[idx] is not None:
                        field_value = str(product[idx]).lower()

                        # Exact match
                        if field_value == search_term:
                            score += priority + exact_match_bonus

                        # Partial match
                        elif search_term in field_value:
                            # Calculate partial match score
                            match_percentage = len(search_term) / len(field_value) if len(field_value) > 0 else 0
                            partial_score = priority * match_percentage
                            score += partial_score

                            # Small bonus if match is at start of field
                            if field_value.startswith(search_term):
                                score += priority * 0.2  # 20% bonus

            # Multi-word search bonus
            if ' ' in search_term:
                search_words = search_term.split()
                # Check if all words appear in product_name
                product_name = product.get('product_name', '').lower() if isinstance(product, dict) else \
                    str(product[2]).lower() if len(product) > 2 else ''

                if all(word in product_name for word in search_words):
                    score += 40  # Bonus for multi-word matches

            return score

        except Exception as e:
            print(f"Error calculating search score: {e}")
            return 0

    def get_last_search_term(self):
        """Get the last search term"""
        return self.last_search_term

    def clear_last_search(self):
        """Clear the last search term"""
        self.last_search_term = ""

    # Optional: Add method to search with multiple criteria
    def advanced_search(self, products, criteria):
        """
        Search with multiple criteria

        Args:
            products: List of products
            criteria: Dict of field:value pairs to search for

        Returns:
            tuple: (filtered_products, message)
        """
        if not criteria or not products:
            return products, None

        scored_products = []

        for product in products:
            score = 0
            matches = 0

            for field, value in criteria.items():
                if not value:  # Skip empty criteria
                    continue

                value = str(value).lower()

                # Get field value based on product type
                if isinstance(product, dict):
                    if field in product:
                        field_value = str(product[field]).lower()
                        priority = self.field_priorities.get(field, 10)
                    else:
                        continue
                else:  # Tuple
                    # Map field name to tuple index
                    field_map = {'id': 0, 'product_name': 2, 'compatible_models': 6}
                    if field in field_map and field_map[field] < len(product):
                        field_value = str(product[field_map[field]]).lower()
                        priority = self.tuple_priorities.get(field_map[field], 10)
                    else:
                        continue

                # Match scoring
                if field_value == value:  # Exact match
                    score += priority * 2
                    matches += 1
                elif value in field_value:  # Partial match
                    score += priority
                    matches += 0.5

            # Only include if at least one criterion matched
            if matches > 0:
                # Bonus for matching multiple criteria
                if matches > 1:
                    score += matches * 20

                scored_products.append((product, score))

        # Sort by score
        scored_products.sort(key=lambda x: x[1], reverse=True)
        filtered_products = [p[0] for p in scored_products]

        # Prepare message
        if filtered_products:
            message = self.translator.t('advanced_search_results').format(count=len(filtered_products))
        else:
            message = self.translator.t('no_search_results').format(term="criteria")

        return filtered_products, message