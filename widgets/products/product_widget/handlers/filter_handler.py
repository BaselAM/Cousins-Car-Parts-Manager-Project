class FilterHandler:
    """Handles product filtering functionality"""

    def __init__(self, translator):
        self.translator = translator
        self.last_filter_settings = {
            "category": "",
            "name": "",
            "car_name": "",
            "model": "",
            "min_price": None,
            "max_price": None,
            "stock_status": None
        }

    def get_last_filter_settings(self):
        """Get the last filter settings used"""
        return self.last_filter_settings.copy()

    def save_filter_settings(self, settings):
        """Save the current filter settings"""
        self.last_filter_settings = settings.copy()

    def reset_filters(self):
        """Reset filters to default values"""
        self.last_filter_settings = {
            "category": "",
            "name": "",
            "brand": "",
            "model": "",
            "min_price": None,
            "max_price": None,
            "stock_status": None
        }

    def filter_products(self, all_products, filters):
        """
        Filter products based on criteria

        Args:
            all_products: List of all products
            filters: Dictionary of filter settings

        Returns:
            tuple: (filtered_products, message)
        """
        try:
            # Import translations functions only when needed to avoid circular imports
            try:
                from translations.data_translations import translate_category, translate_brand, \
                    translate_compatible_models
                translations_available = True
            except ImportError:
                translations_available = False

            filtered = []
            for prod in all_products:
                # Extract fields with proper error handling
                category = prod[1] if len(prod) > 1 and prod[1] else ""
                product_name = prod[2] if len(prod) > 2 and prod[2] else ""
                quantity = 0
                if len(prod) > 3 and prod[3] is not None:
                    try:
                        quantity = int(prod[3])
                    except (ValueError, TypeError):
                        quantity = 0

                price = 0.0
                if len(prod) > 4 and prod[4] is not None:
                    try:
                        price = float(prod[4])
                    except (ValueError, TypeError):
                        price = 0.0

                compatible_models = prod[6] if len(prod) > 6 and prod[6] else ""

                # Extract brand and model from compatible_models field
                brands = set()
                models = set()
                if compatible_models:
                    entries = compatible_models.split(',')
                    for entry in entries:
                        entry = entry.strip()
                        if ':' in entry:
                            brand, model = entry.split(':', 1)
                            brands.add(brand.strip().lower())
                            models.add(model.strip().lower())
                        else:
                            # Handle case where there's no colon separator
                            brands.add(entry.lower())

                # Add translated values to the sets if translations are available
                translated_category = ""
                if translations_available and category:
                    try:
                        translated_category = translate_category(category, 'he').lower()
                    except Exception as e:
                        print(f"Error translating category for filter: {e}")

                translated_brands = set()
                if translations_available and brands:
                    for brand in brands:
                        try:
                            translated_brands.add(translate_brand(brand, 'he').lower())
                        except Exception as e:
                            print(f"Error translating brand for filter: {e}")

                # Check category - match either original or translated value
                if filters["category"]:
                    category_filter = filters["category"].lower()
                    if (category_filter not in category.lower() and
                            (not translated_category or category_filter not in translated_category)):
                        continue

                # Check product name
                if filters["name"] and filters["name"].lower() not in product_name.lower():
                    continue

                # Check brand - match either original or translated values
                if filters["brand"]:
                    brand_filter = filters["brand"].lower()
                    if (not any(brand_filter in brand.lower() for brand in brands) and
                            not any(brand_filter in brand.lower() for brand in translated_brands) and
                            brand_filter not in compatible_models.lower()):
                        continue

                # Check model
                if filters["model"] and not any(filters["model"].lower() in model.lower() for model in models):
                    # If no models match, also check if the model might be in the full compatible_models string
                    if filters["model"].lower() not in compatible_models.lower():
                        continue

                # Check price range
                if filters["min_price"] is not None and price < filters["min_price"]:
                    continue
                if filters["max_price"] is not None and price > filters["max_price"]:
                    continue

                # Check stock status
                if filters["stock_status"] == "in_stock" and quantity <= 0:
                    continue
                if filters["stock_status"] == "out_of_stock" and quantity > 0:
                    continue

                filtered.append(prod)

            message = self.translator.t('filter_results').format(
                count=len(filtered),
                total=len(all_products)
            )
            return filtered, message

        except Exception as e:
            print("Error filtering products:", e)
            import traceback
            print(traceback.format_exc())
            return all_products, self.translator.t('filter_error')