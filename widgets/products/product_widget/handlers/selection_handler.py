class SelectionHandler:
    """Handles product selection mode functionality"""

    def __init__(self, translator, product_table, ui_handler):
        self.translator = translator
        self.product_table = product_table
        self.ui_handler = ui_handler

        # Inside SelectionHandler class

    def toggle_selection_mode(self, checked):
            """
            Toggle selection mode for products

            Args:
                checked: Whether selection mode is enabled

            Returns:
                tuple: (success, message)
            """
            try:
                # Set the table's selection behavior
                self.product_table.set_selection_mode(checked)

                # REMOVED -> self.ui_handler.update_select_button_style(checked)
                # The button's visual state is now handled by the stylesheet's :checked rule in UIHandler

                if checked:
                    message = self.translator.t('select_mode_enabled')
                    return True, message  # Return success and enable message
                else:
                    # Return empty string to signal collapse without showing a message
                    return True, ""  # Return success with empty message to trigger collapse

            except Exception as e:
                # Log the error and return failure status
                error_msg = f"{self.translator.t('selection_mode_error')}: {str(e)}"
                print(f"Selection mode error: {error_msg}")
                return False, error_msg