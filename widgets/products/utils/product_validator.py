from logger import get_logger


class ProductValidator:
    """Product data validator with support for manufacturer and original fields."""

    def __init__(self, translator):
        """Initialize with a translator for error messages."""
        self.translator = translator
        # Initialize logger
        self.logger = get_logger("product_validator")

    @staticmethod
    def safe_strip(value):
        """Safely strip whitespace from a value, handling None values.

        Args:
            value: Any value that might be None or needs stripping

        Returns:
            Stripped string or empty string if None
        """
        if value is None:
            return ""
        try:
            return str(value).strip()
        except Exception:
            return ""

    def sanitize_product_data(self, data):
        """
        Sanitize all product data fields to ensure proper formatting.
        Now includes support for manufacturer and original fields.

        Args:
            data (dict): Product data from dialog or other source

        Returns:
            dict: Sanitized data dictionary
        """
        # Create a copy to avoid modifying original
        sanitized = data.copy() if data else {}

        # Field type conversion and sanitization
        try:
            # String fields - strip whitespace and ensure they're strings
            string_fields = ['category', 'product_name', 'compatible_models', 'manufacturer', 'parcode']
            for field in string_fields:
                if field in sanitized:
                    sanitized[field] = self.safe_strip(sanitized[field])

            # Numeric fields - convert to appropriate numeric types
            if 'quantity' in sanitized:
                try:
                    sanitized['quantity'] = int(sanitized['quantity'])
                except (ValueError, TypeError):
                    sanitized['quantity'] = 0

            if 'price' in sanitized:
                try:
                    sanitized['price'] = float(sanitized['price'])
                except (ValueError, TypeError):
                    sanitized['price'] = 0.0

            # Boolean fields
            if 'is_original' in sanitized:
                sanitized['original'] = bool(sanitized['is_original'])
                # Keep is_original for UI consistency
                sanitized['is_original'] = bool(sanitized['is_original'])

            # Handle missing fields with defaults
            if 'category' not in sanitized or not sanitized['category']:
                sanitized['category'] = "Other Parts"

            if 'manufacturer' not in sanitized:
                sanitized['manufacturer'] = ""

            if 'original' not in sanitized and 'is_original' not in sanitized:
                sanitized['original'] = False
                sanitized['is_original'] = False

            # Log sanitized data for debugging
            self.logger.debug(f"Sanitized product data: {str(sanitized)}")

        except Exception as e:
            self.logger.error(f"Error sanitizing product data: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

        return sanitized

    def validate_product(self, data):
        """
        Validate product data for required fields and data format.
        Now includes validation for manufacturer and original fields.

        Args:
            data (dict): Product data (preferably already sanitized)

        Returns:
            tuple: (is_valid, error_message)
                - is_valid (bool): True if validation passed
                - error_message (str): Translated error message if validation failed
        """
        # Required fields check
        if not data.get('product_name'):
            error_msg = self.translator.t('name_required')
            self.logger.warning(f"Validation failed: {error_msg}")
            return False, error_msg

        # Type validation
        try:
            # Verify quantity is an integer
            quantity = data.get('quantity')
            if quantity is not None and not isinstance(quantity, int):
                try:
                    int(quantity)
                except (ValueError, TypeError):
                    error_msg = self.translator.t('invalid_quantity')
                    self.logger.warning(f"Validation failed: {error_msg}")
                    return False, error_msg

            # Verify price is a float or int
            price = data.get('price')
            if price is not None and not isinstance(price, (float, int)):
                try:
                    float(price)
                except (ValueError, TypeError):
                    error_msg = self.translator.t('invalid_price')
                    self.logger.warning(f"Validation failed: {error_msg}")
                    return False, error_msg

            # Verify original is a boolean
            is_original = data.get('original')
            if is_original is not None and not isinstance(is_original, bool):
                if not isinstance(is_original, (int, bool)):
                    error_msg = self.translator.t('invalid_original', "Invalid value for Original field")
                    self.logger.warning(f"Validation failed: {error_msg}")
                    return False, error_msg

            # Log successful validation
            self.logger.debug(f"Product validation passed for: {data.get('product_name', 'unnamed product')}")
            return True, ""

        except Exception as e:
            self.logger.error(f"Exception during product validation: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            error_msg = self.translator.t('validation_error')
            return False, error_msg

    def format_data_for_display(self, data):
        """
        Format product data for display in UI components.
        Handles manufacturer and original fields.

        Args:
            data (dict): Product data

        Returns:
            dict: Formatted data for display
        """
        display_data = {}

        try:
            # Handle basic fields
            if 'product_name' in data:
                display_data['product_name'] = self.safe_strip(data['product_name'])

            if 'category' in data:
                display_data['category'] = self.safe_strip(data['category'])

            if 'quantity' in data:
                display_data['quantity'] = str(data['quantity'])

            if 'price' in data:
                display_data['price'] = f"{data['price']:.2f}"

            if 'compatible_models' in data:
                display_data['compatible_models'] = self.safe_strip(data['compatible_models'])

            # Handle manufacturer field
            if 'manufacturer' in data:
                display_data['manufacturer'] = self.safe_strip(data['manufacturer'])

            # Handle original field - convert to Yes/No for display
            if 'original' in data or 'is_original' in data:
                is_original = data.get('original', data.get('is_original', False))
                display_data['original'] = self.translator.t('yes') if is_original else self.translator.t('no')

            # Include parcode if available
            if 'parcode' in data:
                display_data['parcode'] = self.safe_strip(data['parcode'])

        except Exception as e:
            self.logger.error(f"Error formatting data for display: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())

        return display_data