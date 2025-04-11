class EditHandler:
    """Handles product editing functionality"""

    def __init__(self, translator, db):
        self.translator = translator
        self.db = db

    def handle_cell_change(self, row, column, table, all_products):
        """
        Handle cell change in the product table

        Args:
            row: Row index
            column: Column index
            table: Product table widget
            all_products: List of all products

        Returns:
            tuple: (success, product_id, field, new_value, message)
        """
        if row < 0 or column < 0 or row >= table.rowCount() or column >= table.columnCount():
            return False, None, None, None, None

        try:
            # Get the changed cell
            item = table.item(row, column)
            if not item:
                return False, None, None, None, None

            # Get the ID cell (which contains parcode) - using explicit index 0 instead of COL_ID
            parcode_item = table.item(row, 0)
            if not parcode_item:
                return False, None, None, None, None

            parcode = parcode_item.text()

            # Get the product name for identification
            name_item = table.item(row, 1)  # Product name is in column 1
            product_name = name_item.text() if name_item else ""

            # Find the database ID for this product
            part_id = None
            for product in all_products:
                if isinstance(product, dict):
                    # For regular edits, match by parcode
                    db_parcode = str(product.get('parcode', ''))
                    if db_parcode == parcode:
                        part_id = product.get('id')
                        break

                    # If editing the parcode itself, try matching by product name
                    if column == 0 and product.get('product_name') == product_name:
                        part_id = product.get('id')
                        break

            # If we couldn't find the product, we can't update it
            if part_id is None:
                print(f"Could not find database ID for row {row}")
                return False, None, None, None, None

            # Map columns to fields
            field_map = {
                0: 'parcode',
                1: 'product_name',
                2: 'manufacturer',  # Changed from 'compatible_models'
                3: 'quantity',
                4: 'price'
            }

            field = field_map.get(column)
            if not field:
                return False, None, None, None, None

            new_value = item.text().strip()

            # Ensure non-empty values for required fields
            if new_value == "":
                if field == 'parcode':
                    return False, None, None, None, "Parcode cannot be empty"
                elif field == 'product_name':
                    return False, None, None, None, "Product name cannot be empty"

            # Handle numeric fields
            if field == 'quantity':
                try:
                    new_value = int(new_value)
                except ValueError:
                    new_value = 0
                    table.blockSignals(True)
                    item.setText('0')
                    table.blockSignals(False)
            elif field == 'price':
                try:
                    new_value = float(new_value)
                except ValueError:
                    new_value = 0.0
                    table.blockSignals(True)
                    item.setText('0.0')
                    table.blockSignals(False)

            # Update the database
            update_data = {field: new_value}
            success = self.db.update_part(part_id, **update_data)

            if success:
                # Format display values
                if field == 'quantity':
                    table.blockSignals(True)
                    item.setText(str(int(new_value)))
                    table.blockSignals(False)
                elif field == 'price':
                    table.blockSignals(True)
                    item.setText(f"{float(new_value):.2f}")
                    table.blockSignals(False)

                # Use appropriate message
                if field == 'parcode':
                    try:
                        success_message = self.translator.t('barcode:barcode_updated', barcode=new_value)
                    except:
                        success_message = f"Barcode updated to: {new_value}"
                else:
                    success_message = self.translator.t('product_updated')

                return True, part_id, field, new_value, success_message

            return False, None, None, None, None

        except Exception as e:
            print(f"Error handling cell change: {e}")
            import traceback
            traceback.print_exc()
            return False, None, None, None, None
