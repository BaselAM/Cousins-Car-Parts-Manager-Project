import csv
import os
from logger import get_logger

# Get a logger for this module
logger = get_logger("data_exporter")

def export_to_csv(file_path, headers, data):
    """Export data to CSV file with improved error handling

    Args:
        file_path: Path to save the CSV file
        headers: List of column headers
        data: List of rows (each row is a list of values)

    Returns:
        bool: Success status
    """
    try:
        # Add .csv extension if not present
        if not file_path.endswith('.csv'):
            file_path += '.csv'

        # Ensure the directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Validate input parameters
        if not headers:
            logger.error("Cannot export with empty headers")
            return False

        if not data:
            logger.warning("Exporting empty data set")
            # Continue with export to create at least a headers-only file

        # Create the CSV file
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write headers
            writer.writerow(headers)

            # Write data with safe handling of row length mismatches
            for i, row in enumerate(data):
                # Make sure each row matches the header length
                if len(row) != len(headers):
                    logger.warning(f"Row {i} has {len(row)} values, expected {len(headers)}. Padding with empty values.")
                    # Pad shorter rows with empty strings, truncate longer ones
                    row_adjusted = (row + [''] * len(headers))[:len(headers)]
                    writer.writerow(row_adjusted)
                else:
                    writer.writerow(row)

        logger.info(f"Successfully exported {len(data)} rows to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Export error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False