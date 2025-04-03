import os
import tempfile
import subprocess
from PyQt5.QtWidgets import QMessageBox, QDialog
from PyQt5.QtCore import Qt

# Import reportlab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, LETTER, LEGAL, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Import the dialog from print_dialog.py
from widgets.products.dialogs.print_dialog import PrintSettingsDialog


# Helper function for cell formatting
def format_cell(text, alignment="LEFT"):
    """Format cell text with proper alignment padding"""
    if not text:
        return ""

    # Add extra space for alignment
    if alignment == "RIGHT":
        return text + "  "
    elif alignment == "LEFT":
        return "  " + text
    else:
        return text


class PDFPrintOperation:
    """Handles printing the product table with PDF generation and preview"""

    def __init__(self, parent_widget, translator, status_bar):
        self.parent = parent_widget
        self.translator = translator
        self.status_bar = status_bar
        self.temp_dir = None
        self.temp_pdf = None
        self.bidi_support = False

        # Try to import bidi
        try:
            import bidi.algorithm
            self.bidi_support = True
        except ImportError:
            try:
                import pip
                pip.main(['install', 'python-bidi'])
                import bidi.algorithm
                self.bidi_support = True
            except:
                print("Could not install bidi support")

        # Try to register basic Hebrew-compatible fonts
        try:
            self.register_fonts()
        except Exception as e:
            print(f"Warning: Could not register fonts: {e}")

    def register_fonts(self):
        """Register fonts that support Hebrew characters"""
        # Common system fonts that might support Hebrew
        font_paths = {
            'Arial': [
                # Windows paths
                "C:/Windows/Fonts/arial.ttf",
                "C:/Windows/Fonts/ARIAL.TTF",
                # macOS paths
                "/Library/Fonts/Arial.ttf",
                # Linux paths
                "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf"
            ],
            'DejaVuSans': [
                # Linux
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                # Windows (if installed)
                "C:/Windows/Fonts/DejaVuSans.ttf",
                # macOS
                "/Library/Fonts/DejaVuSans.ttf"
            ],
            'Tahoma': [
                # Windows
                "C:/Windows/Fonts/tahoma.ttf",
                "C:/Windows/Fonts/TAHOMA.TTF"
            ],
            'David': [
                # Windows (Hebrew font)
                "C:/Windows/Fonts/david.ttf",
                "C:/Windows/Fonts/DAVID.TTF"
            ],
            'Miriam': [
                # Windows (Hebrew font)
                "C:/Windows/Fonts/miriam.ttf",
                "C:/Windows/Fonts/MIRIAM.TTF"
            ]
        }

        # Try to register fonts
        self.registered_fonts = []

        for font_name, paths in font_paths.items():
            for path in paths:
                if os.path.exists(path):
                    try:
                        pdfmetrics.registerFont(TTFont(font_name, path))
                        self.registered_fonts.append(font_name)
                        print(f"Registered font: {font_name} from {path}")
                        break  # Success, move to next font
                    except Exception as e:
                        print(f"Could not register {font_name} from {path}: {e}")

        # If no suitable font was found, register a default built-in font
        if not self.registered_fonts:
            print("No suitable Hebrew fonts found. Using built-in fonts.")
            self.registered_fonts = ['Helvetica']  # Fallback to built-in

        print(f"Available fonts for PDF: {self.registered_fonts}")

    def print_table(self, product_table, all_products, select_mode_enabled=False):
        """
        Generate PDF, show preview, and handle printing.
        """
        try:
            table = product_table.table

            # Verify we have data to print
            if table.rowCount() == 0:
                self.status_bar.show_message(
                    self.translator.t('no_data_to_print'),
                    "warning"
                )
                return False

            # Create settings dialog
            dialog = PrintSettingsDialog(self.translator, self.parent)

            # Only enable selected option if in select mode and rows are selected
            has_selection = False
            if select_mode_enabled:
                selected_rows = product_table.get_selected_rows_data()
                has_selection = len(selected_rows) > 0

            dialog.print_selected_radio.setEnabled(has_selection)
            if not has_selection:
                dialog.print_all_radio.setChecked(True)

            # Show the dialog
            result = dialog.exec_()

            if result == QDialog.Accepted:
                # Get settings
                settings = dialog.get_settings()

                # Get data to print
                data_to_print = self._get_data_to_print(product_table, all_products, settings)

                # Create temporary directory for the PDF
                if self.temp_dir:
                    try:
                        if self.temp_pdf and os.path.exists(self.temp_pdf):
                            os.unlink(self.temp_pdf)
                        os.rmdir(self.temp_dir)
                    except:
                        pass

                self.temp_dir = tempfile.mkdtemp()
                self.temp_pdf = os.path.join(self.temp_dir, "products_report.pdf")

                # Generate PDF
                success = self._generate_pdf(data_to_print, product_table, settings)

                if success:
                    # Open PDF with default viewer
                    self._open_pdf()
                    self.status_bar.show_message(
                        self.translator.t('print_success'),
                        "success"
                    )
                    return True
                else:
                    self.status_bar.show_message(
                        self.translator.t('print_error'),
                        "error"
                    )
                    return False

            return False

        except Exception as e:
            print(f"Print error: {e}")
            import traceback
            print(traceback.format_exc())
            self.status_bar.show_message(
                self.translator.t('print_error'),
                "error"
            )
            return False

    def _open_pdf(self):
        """Open the generated PDF with the default PDF viewer"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(self.temp_pdf)
            elif os.name == 'posix':  # macOS, Linux
                if 'darwin' in os.uname()[0].lower():  # macOS
                    subprocess.call(('open', self.temp_pdf))
                else:  # Linux
                    subprocess.call(('xdg-open', self.temp_pdf))
        except Exception as e:
            print(f"Error opening PDF: {e}")
            QMessageBox.warning(
                self.parent,
                self.translator.t('error'),
                self.translator.t('error_opening_pdf') + f": {str(e)}"
            )

    def _process_hebrew_text(self, text):
        """Process Hebrew text for correct RTL display"""
        if not text or not self.bidi_support:
            return text

        # Check if text contains Hebrew characters (Unicode range 0x0590-0x05FF)
        has_hebrew = any(0x0590 <= ord(c) <= 0x05FF for c in text)
        if has_hebrew:
            try:
                # Process with bidi algorithm
                import bidi.algorithm
                bidi_text = bidi.algorithm.get_display(text)
                return bidi_text
            except Exception as e:
                print(f"Error processing Hebrew text: {e}")

        return text

    def _generate_pdf(self, products, product_table, settings):
        """Generate a PDF report using reportlab with improved Hebrew and RTL handling"""
        try:
            # Determine if RTL mode is enabled
            rtl_mode = settings.get('rtl_mode', False)

            # Choose a font that supports Hebrew (prefer Hebrew-specific fonts if available)
            hebrew_fonts = ['David', 'Miriam', 'Arial', 'Tahoma', 'DejaVuSans']
            base_font = None

            for font in hebrew_fonts:
                if font in self.registered_fonts:
                    base_font = font
                    break

            if not base_font:
                base_font = self.registered_fonts[0] if self.registered_fonts else 'Helvetica'

            # Get column headers (process for RTL)
            headers = []
            header_data = []
            columns = range(product_table.table.columnCount())

            # If RTL mode, we need to reverse the column order in the PDF
            if rtl_mode:
                columns = reversed(list(columns))

            for col in columns:
                header_item = product_table.table.horizontalHeaderItem(col)
                if header_item:
                    header_text = header_item.text()
                    # Process header text for RTL
                    header_text = self._process_hebrew_text(header_text)
                    headers.append(header_text)
                    header_data.append(col)  # Store original column index
                else:
                    headers.append(f"Column {col}")
                    header_data.append(col)

            # Determine page size
            if settings['paper_size'] == 'A4':
                page_size = A4
            elif settings['paper_size'] == 'Letter':
                page_size = LETTER
            elif settings['paper_size'] == 'Legal':
                page_size = LEGAL
            else:
                page_size = A4

            # Apply orientation
            if settings['orientation'] == 1:  # Landscape
                page_size = landscape(page_size)

            # Create document
            doc = SimpleDocTemplate(
                self.temp_pdf,
                pagesize=page_size,
                rightMargin=0.5 * inch,
                leftMargin=0.5 * inch,
                topMargin=0.5 * inch,
                bottomMargin=0.5 * inch
            )

            # Create content elements
            elements = []

            # Create styles
            styles = getSampleStyleSheet()

            # Create style for title
            title_style = ParagraphStyle(
                'HebrewTitle',
                parent=styles['Heading1'],
                fontName=base_font,
                alignment=1,  # Center alignment
                fontSize=18
            )

            # Create style for date
            date_style = ParagraphStyle(
                'HebrewDate',
                parent=styles['Normal'],
                fontName=base_font,
                alignment=2 if not rtl_mode else 0,  # Right alignment (or left in RTL)
                fontSize=10
            )

            # Add title if needed
            if settings['print_header']:
                title_text = self._process_hebrew_text(self.translator.t('products_report'))
                title = Paragraph(title_text, title_style)
                elements.append(title)
                elements.append(Spacer(1, 0.25 * inch))

            # Add date if needed
            if settings['print_date']:
                from datetime import datetime
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
                date = Paragraph(date_str, date_style)
                elements.append(date)
                elements.append(Spacer(1, 0.25 * inch))

            # Prepare data for table with RTL text processing
            table_data = []

            # Add headers
            table_data.append(headers)

            # Process and add product rows
            for product in products:
                row = []
                row_data = {}

                # First extract all the data
                if isinstance(product, dict):
                    # Extract data from dict format
                    row_data = {
                        0: str(product.get('parcode', '')),
                        1: self._process_hebrew_text(str(product.get('category', ''))),
                        2: self._process_hebrew_text(str(product.get('product_name', ''))),
                        3: self._process_hebrew_text(str(product.get('compatible_models', ''))),
                        4: str(product.get('quantity', '0')),
                        5: f"{float(product.get('price', 0.0)):.2f}"
                    }
                else:
                    # Handle tuple format
                    try:
                        row_data = {
                            0: str(product[0]) if len(product) > 0 else '',
                            1: self._process_hebrew_text(str(product[1] or '')) if len(product) > 1 else '',
                            2: self._process_hebrew_text(str(product[2] or '')) if len(product) > 2 else '',
                            3: self._process_hebrew_text(str(product[6] or '')) if len(product) > 6 else '',
                            4: str(product[3] or '0') if len(product) > 3 else '0',
                            5: f"{float(product[4] or 0.0):.2f}" if len(product) > 4 else '0.00'
                        }
                    except Exception as e:
                        print(f"Error processing product row: {e}")
                        # Provide default values for error case
                        row_data = {i: '' for i in range(6)}
                        row_data[4] = '0'
                        row_data[5] = '0.00'

                # Now add the data to the row in the correct order based on RTL mode
                # header_data contains the column indices in the order we want to display them
                for col_idx in header_data:
                    row.append(row_data.get(col_idx, ''))

                table_data.append(row)

            # Calculate column widths based on page size
            page_width, page_height = page_size
            available_width = page_width - inch  # Account for margins

            # Fixed column widths for better control
            if rtl_mode:
                # For RTL, we reverse the column order
                col_widths = [
                    available_width * 0.15,  # Price - 15%
                    available_width * 0.10,  # Qty - 10%
                    available_width * 0.25,  # Models - 25%
                    available_width * 0.25,  # Name - 25%
                    available_width * 0.15,  # Category - 15%
                    available_width * 0.10,  # ID - 10%
                ]
            else:
                # Standard LTR column order
                col_widths = [
                    available_width * 0.10,  # ID - 10%
                    available_width * 0.15,  # Category - 15%
                    available_width * 0.25,  # Name - 25%
                    available_width * 0.25,  # Models - 25%
                    available_width * 0.10,  # Qty - 10%
                    available_width * 0.15,  # Price - 15%
                ]

            # Process table data with formatting for better alignment and handle long text
            name_col_idx = 2 if not rtl_mode else 3  # Identify the name column index
            models_col_idx = 3 if not rtl_mode else 2  # Identify the models column index

            for row_idx in range(1, len(table_data)):  # Skip header
                if rtl_mode:
                    # RTL mode - reversed columns
                    # Price - right align
                    table_data[row_idx][0] = format_cell(table_data[row_idx][0], "RIGHT")
                    # Qty - right align
                    table_data[row_idx][1] = format_cell(table_data[row_idx][1], "RIGHT")
                    # Text columns - right align for Hebrew
                    table_data[row_idx][2] = format_cell(table_data[row_idx][2], "RIGHT")
                    table_data[row_idx][3] = format_cell(table_data[row_idx][3], "RIGHT")
                    table_data[row_idx][4] = format_cell(table_data[row_idx][4], "RIGHT")
                    # ID - center
                    table_data[row_idx][5] = format_cell(table_data[row_idx][5], "CENTER")
                else:
                    # Standard LTR mode
                    # ID - center
                    table_data[row_idx][0] = format_cell(table_data[row_idx][0], "CENTER")
                    # Text columns - left align
                    table_data[row_idx][1] = format_cell(table_data[row_idx][1], "LEFT")
                    table_data[row_idx][2] = format_cell(table_data[row_idx][2], "LEFT")
                    table_data[row_idx][3] = format_cell(table_data[row_idx][3], "LEFT")
                    # Numeric columns - right align
                    table_data[row_idx][4] = format_cell(table_data[row_idx][4], "RIGHT")
                    table_data[row_idx][5] = format_cell(table_data[row_idx][5], "RIGHT")

                # Specially handle long product names and models by converting them to Paragraph objects
                # for automatic text wrapping
                for col_idx in [name_col_idx, models_col_idx]:
                    text = table_data[row_idx][col_idx]
                    if len(text) > 20:  # Only create Paragraphs for longer text
                        align = 'right' if rtl_mode else 'left'
                        para_style = ParagraphStyle(
                            f'Cell_{row_idx}_{col_idx}',
                            fontName=base_font,
                            fontSize=10,
                            alignment=2 if align == 'right' else 0,
                            leading=12,  # Line spacing
                            spaceAfter=1,
                        )
                        # Create paragraph for long text - this enables proper wrapping
                        table_data[row_idx][col_idx] = Paragraph(text, para_style)

            # Create table with updated data and enable splitting long words
            table = Table(table_data, colWidths=col_widths, repeatRows=1, splitByRow=True)

            # Prepare table style with dynamic alignments based on RTL mode
            style_commands = [
                # Header style
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), base_font),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),

                # Data rows
                ('FONTNAME', (0, 1), (-1, -1), base_font),
                ('FONTSIZE', (0, 1), (-1, -1), 10),

                # Enable word wrap for text columns
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align text to top of cell when wrapping
                ('WORDWRAP', (0, 0), (-1, -1), True),  # Enable word wrapping for all cells

                # Grid lines
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),

                # Padding - increased to allow more space for wrapped text
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]

            # Add column-specific alignments based on RTL mode
            if rtl_mode:
                # RTL mode alignments
                style_commands.extend([
                    # Column-specific alignments for RTL
                    ('ALIGN', (0, 1), (0, -1), 'RIGHT'),  # Price (rightmost column in RTL)
                    ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Qty
                    ('ALIGN', (2, 1), (4, -1), 'RIGHT'),  # Text columns (Models, Name, Category)
                    ('ALIGN', (5, 1), (5, -1), 'CENTER'),  # ID (leftmost column in RTL)
                ])
            else:
                # LTR mode alignments (original)
                style_commands.extend([
                    # Column-specific alignments for LTR
                    ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID
                    ('ALIGN', (1, 1), (3, -1), 'LEFT'),  # Text columns (Category, Name, Models)
                    ('ALIGN', (4, 1), (5, -1), 'RIGHT'),  # Numeric columns (Qty, Price)
                ])

            style = TableStyle(style_commands)
            table.setStyle(style)
            elements.append(table)

            # Build the document
            doc.build(elements)

            return True

        except Exception as e:
            print(f"Error generating PDF: {e}")
            import traceback
            print(traceback.format_exc())
            return False

    def _get_data_to_print(self, product_table, all_products, settings):
        """Get data to print based on scope settings"""
        scope = settings['scope']
        data_to_print = []

        if scope == 0:  # All products
            # Get all visible products (respecting current filter/search)
            data_to_print = product_table.get_current_view_data()
        elif scope == 1:  # Selected products
            # Get only selected products
            selected_data = product_table.get_selected_rows_data()
            for product_id, _ in selected_data:
                for product in all_products:
                    # Handle both dict and tuple product formats
                    if isinstance(product, dict) and product.get('parcode') == product_id:
                        data_to_print.append(product)
                    elif not isinstance(product, dict) and len(product) > 0 and product[0] == product_id:
                        data_to_print.append(product)
        elif scope == 2:  # Filtered products (already filtered in the table)
            data_to_print = product_table.get_current_view_data()

        return data_to_print