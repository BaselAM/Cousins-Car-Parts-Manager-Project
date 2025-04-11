class ProductManager:
    """Manages product data in memory"""

    def __init__(self, db):
        self.db = db
        self.products = []
        self.filtered_products = []

    def set_products(self, products):
        """Set all products"""
        self.products = products

    def get_products(self):
        """Get all products"""
        return self.products

    def clear(self):
        """Clear product data"""
        self.products = []
        self.filtered_products = []

    def update_product_in_memory(self, product_id, field, new_value, column=None):
        """
        Update a product in memory after editing

        Args:
            product_id: Database ID of the product
            field: Database field name that was updated
            new_value: New value for the field
            column: Table column index (optional)
        """
        try:
            # First update the in-memory product if it exists
            updated = False

            # Look for the product in our in-memory collection
            for i, product in enumerate(self.products):
                if isinstance(product, dict):
                    if product.get('id') == product_id:
                        self.products[i][field] = new_value
                        updated = True
                        break
                else:  # Tuple format
                    # Find the tuple index corresponding to the field
                    if product[0] == product_id:  # index 0 should be 'id'
                        # Create a dict to help map field names to tuple indices
                        # Create a dict to help map field names to tuple indices
                        field_indices = {
                            'id': 0,
                            'product_name': 2,  # Updated indices after category removal
                            'quantity': 3,
                            'price': 4,
                            'manufacturer': 14  # Changed from 'compatible_models': 6
                        }

                        if field in field_indices:
                            # Convert tuple to list for modification
                            product_list = list(product)
                            product_list[field_indices[field]] = new_value
                            self.products[i] = tuple(product_list)
                            updated = True
                        break

            # If we couldn't find and update the product in memory,
            # refresh it from the database
            if not updated:
                # Get fresh data from database
                fresh_product = self.db.get_part(product_id)
                if fresh_product:
                    # Add or replace in our products list
                    self.update_or_add_product(product_id, fresh_product)
                    print(f"Refreshed product {product_id} from database")
                else:
                    print(f"Warning: Could not find product {product_id} in database after edit")
        except Exception as e:
            print(f"Error updating product in memory: {e}")
            import traceback
            print(traceback.format_exc())

    def update_or_add_product(self, product_id, product):
        """
        Update a product if it exists, or add it if it doesn't

        Args:
            product_id: ID of the product
            product: Product data (dict or tuple)
        """
        found = False
        # Try to update existing product
        for i, p in enumerate(self.products):
            if isinstance(p, dict) and p.get('id') == product_id:
                self.products[i] = product
                found = True
                break
            elif not isinstance(p, dict) and len(p) > 0 and p[0] == product_id:
                self.products[i] = product
                found = True
                break

        # Add product if not found
        if not found:
            self.products.append(product)

        return not found  # Return True if added, False if updated

    def remove_products_by_ids(self, product_ids):
        """
        Remove products with matching IDs

        Args:
            product_ids: List of product IDs to remove
        """
        if not product_ids:
            return

        to_keep = []
        for product in self.products:
            if isinstance(product, dict):
                if product.get('id') not in product_ids:
                    to_keep.append(product)
            else:  # Tuple format
                if product[0] not in product_ids:
                    to_keep.append(product)

        self.products = to_keep