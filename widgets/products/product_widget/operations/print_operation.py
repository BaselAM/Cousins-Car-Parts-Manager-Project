import os
import tempfile
import subprocess
import logging
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox, QDialog
from PyQt5.QtCore import Qt

# Import reportlab components
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, LETTER, LEGAL, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, Frame, PageBreak, PageTemplate, BaseDocTemplate
from reportlab.platypus.flowables import HRFlowable

# Import the dialog from print_dialog.py
from widgets.products.dialogs.print_dialog import PrintSettingsDialog

# Initialize logger
logger = logging.getLogger(__name__)


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


# Custom flowable for signature field
class SignatureField(Flowable):
    """A custom flowable that creates a signature field line with a label."""

    def __init__(self, label, width=200, height=40):
        Flowable.__init__(self)
        self.label = label
        self.width = width
        self.height = height

    def draw(self):
        # Draw signature line
        self.canv.setStrokeColor(colors.black)
        self.canv.setLineWidth(0.5)
        self.canv.line(0, 15, self.width - 50, 15)

        # Draw label
        self.canv.setFont("David", 10)
        self.canv.drawRightString(self.width, 5, self.label)


# Custom class to represent monetary amounts
class MoneyFlowable(Flowable):
    """A custom flowable to display monetary amounts with currency symbol."""

    def __init__(self, amount, currency="₪", width=100, height=20, font_name="David", font_size=10):
        Flowable.__init__(self)
        self.amount = amount
        self.currency = currency
        self.width = width
        self.height = height
        self.font_name = font_name
        self.font_size = font_size

    def draw(self):
        # Format the amount
        formatted = f"{float(self.amount):.2f}"

        # Draw currency symbol and amount
        self.canv.setFont(self.font_name, self.font_size)
        self.canv.drawRightString(self.width, 0, f"{self.currency}{formatted}")


# Custom flowable for official document seal/watermark
class OfficialSealFlowable(Flowable):
    """Creates an official-looking seal or watermark for the document."""

    def __init__(self, width=100, height=100, opacity=0.1, process_hebrew_func=None, business_name=None):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.opacity = opacity
        self.process_hebrew_func = process_hebrew_func
        self.business_name = business_name or "חלקי חילוף אבו מוך"  # Default value if none provided

    def draw(self):
        # Save canvas state to restore it later
        self.canv.saveState()

        # Set transparency
        self.canv.setFillAlpha(self.opacity)

        # Set color - traditional official seal color
        self.canv.setFillColor(colors.navy)

        # Draw outer circle
        self.canv.setStrokeColor(colors.navy)
        self.canv.setLineWidth(2)
        self.canv.circle(self.width / 2, self.height / 2, self.width / 2 - 5, stroke=1, fill=0)

        # Draw inner circle
        self.canv.circle(self.width / 2, self.height / 2, self.width / 2 - 15, stroke=1, fill=0)

        # Add text around the circle - handle Hebrew text properly
        self.canv.setFont("David", 12)

        # Use the business name for the seal
        seal_text = self.business_name
        if self.process_hebrew_func:
            # Process the full text once if needed
            seal_text = self.process_hebrew_func(seal_text)

        # Draw the text in the center without trying to place around circle
        # This is simpler and more reliable for showing the company name
        self.canv.drawCentredString(self.width / 2, self.height / 2, seal_text)

        # Restore canvas state
        self.canv.restoreState()


class PDFPrintOperation:
    """Handles printing the product table with PDF generation and preview for Israeli inventory documents"""

    def __init__(self, parent_widget, translator, status_bar):
        self.parent = parent_widget
        self.translator = translator
        self.status_bar = status_bar
        self.temp_dir = None
        self.temp_pdf = None
        self.bidi_support = False

        # Default Business details - will be overridden by dialog input
        self.business_details = {
            'name': "חלקי חילוף אבו מוך",
            'name_en': "Abu Mukh Car Parts",
            'address': "באקה אל גרבייה, ביר באקה",
            'phone': "046077888",
            'tax_id': "123456789",
            'logo_path': None  # Path to logo if available
        }

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
                logger.warning("Could not install bidi support")

        # Try to register basic Hebrew-compatible fonts
        try:
            self.register_fonts()
        except Exception as e:
            logger.warning(f"Could not register fonts: {e}")

    def register_fonts(self):
        """Register fonts that support Hebrew characters"""
        # Get a logger for this module
        logger = logging.getLogger(__name__)

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
                        logger.debug(f"Registered font: {font_name} from {path}")
                        break  # Success, move to next font
                    except Exception as e:
                        logger.warning(f"Could not register {font_name} from {path}: {e}")

        # If no suitable font was found, register a default built-in font
        if not self.registered_fonts:
            logger.warning("No suitable Hebrew fonts found. Using built-in fonts.")
            self.registered_fonts = ['Helvetica']  # Fallback to built-in

        logger.info(f"Available fonts for PDF: {self.registered_fonts}")

    def print_table(self, product_table, all_products, select_mode_enabled=False):
        """
        Generate PDF, show preview, and handle printing.
        """
        try:
            table = product_table.table

            # Verify we have data to print
            if table.rowCount() == 0:
                # Fix translator call
                try:
                    error_message = self.translator.t('no_data_to_print')
                except:
                    error_message = "No data to print"

                # End dialog action with error message
                if hasattr(self.status_bar, 'end_dialog_action'):
                    self.status_bar.end_dialog_action(error_message)
                else:
                    self.status_bar.show_message(error_message, "warning")
                return False

            # Create settings dialog with current business details
            dialog = PrintSettingsDialog(self.translator, self.parent, self.business_details)

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
                # Get settings including business details
                settings = dialog.get_settings()

                # Update our business details with the ones from the dialog
                self.business_details = settings.get('business_details', self.business_details)

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
                self.temp_pdf = os.path.join(self.temp_dir, "inventory_report.pdf")

                # Generate PDF
                success = self._generate_pdf(data_to_print, product_table, settings)

                if success:
                    # Open PDF with default viewer
                    self._open_pdf()

                    # Fix translator call
                    try:
                        success_message = self.translator.t('print_success')
                    except:
                        success_message = "PDF generated successfully"

                    # Use end_dialog_action for success case
                    if hasattr(self.status_bar, 'end_dialog_action'):
                        self.status_bar.end_dialog_action(success_message)
                    else:
                        self.status_bar.show_message(success_message, "success")
                    return True
                else:
                    # Fix translator call
                    try:
                        error_message = self.translator.t('print_error')
                    except:
                        error_message = "Error generating PDF"

                    # Use end_dialog_action for error case
                    if hasattr(self.status_bar, 'end_dialog_action'):
                        self.status_bar.end_dialog_action(error_message)
                    else:
                        self.status_bar.show_message(error_message, "error")
                    return False
            else:
                # User cancelled the dialog - IMMEDIATELY collapse with NO message
                if hasattr(self.status_bar, 'force_collapse'):
                    self.status_bar.force_collapse()  # Most direct approach
                elif hasattr(self.status_bar, 'end_dialog_action'):
                    self.status_bar.end_dialog_action("")  # Empty string to avoid showing message
                else:
                    self.status_bar.clear()  # Fallback to simple clear
                return False

        except Exception as e:
            logger.error(f"Print error: {e}")
            import traceback
            logger.error(traceback.format_exc())

            # Fix translator call and use end_dialog_action for exception case
            try:
                error_message = self.translator.t('print_error')
            except:
                error_message = "Error generating PDF"

            if hasattr(self.status_bar, 'end_dialog_action'):
                self.status_bar.end_dialog_action(error_message)
            else:
                self.status_bar.show_message(error_message, "error")
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
            logger.error(f"Error opening PDF: {e}")

            # Fix translator calls
            try:
                error_title = self.translator.t('error')
            except:
                error_title = "Error"

            try:
                error_message = self.translator.t('error_opening_pdf')
            except:
                error_message = "Error opening PDF file"

            QMessageBox.warning(
                self.parent,
                error_title,
                error_message + f": {str(e)}"
            )

    def _safe_translate(self, key, default=None):
        """Safely translate a key with fallback."""
        try:
            return self.translator.t(key)
        except Exception:
            return default if default is not None else key

    def _process_hebrew_text(self, text):
        """Process Hebrew text for correct RTL display"""
        if not text or not self.bidi_support:
            return text

        # First clean any existing control characters
        text = self._clean_text_for_pdf(text)

        # Check if text contains Hebrew characters
        has_hebrew = any(0x0590 <= ord(c) <= 0x05FF for c in text)
        if not has_hebrew:
            return text  # No Hebrew, just return as is

        try:
            import bidi.algorithm
            # Process pure Hebrew text with bidi algorithm
            return bidi.algorithm.get_display(text)
        except Exception as e:
            logger.error(f"Error processing Hebrew text: {e}")

        # Fallback to original text if processing fails
        return text

    def _get_data_to_print(self, product_table, all_products, settings):
        """Get data to print based on scope settings, with updated column structure"""
        scope = settings['scope']
        data_to_print = []

        if scope == 0:  # All products
            # Get all visible products (respecting current filter/search)
            data_to_print = product_table.get_current_view_data()
            logger.info(f"Printing all visible products: {len(data_to_print)} items")
            # Log first few products to debug
            for i, prod in enumerate(data_to_print[:3]):
                if isinstance(prod, dict):
                    logger.debug(f"Sample product {i + 1}: {prod.get('product_name', 'NO NAME')}")
                else:
                    logger.debug(f"Sample product {i + 1}: {prod[1] if len(prod) > 1 else 'NO NAME'}")
        elif scope == 1:  # Selected products
            # Get only selected products
            selected_data = product_table.get_selected_rows_data()
            logger.info(f"Selected products: {len(selected_data)} items")

            # Find matching products in full list
            for parcode, name in selected_data:
                logger.debug(f"Looking for selected product: {parcode} - {name}")
                for product in all_products:
                    # Handle both dict and tuple formats
                    if isinstance(product, dict) and str(product.get('parcode', '')) == str(parcode):
                        data_to_print.append(product)
                        break
                    elif not isinstance(product, dict) and len(product) > 0 and str(product[0]) == str(parcode):
                        data_to_print.append(product)
                        break
        elif scope == 2:  # Filtered products
            data_to_print = product_table.get_current_view_data()
            logger.info(f"Printing filtered products: {len(data_to_print)} items")

        return data_to_print

    def _generate_pdf(self, products, product_table, settings):
        """Generate a PDF report in the format of an official Israeli inventory count document"""
        try:
            # Determine if RTL mode is enabled - for Hebrew documents, default to True
            rtl_mode = settings.get('rtl_mode', True)

            # Choose a font that supports Hebrew - prefer David for official docs
            hebrew_fonts = ['David', 'Miriam', 'Arial', 'Tahoma', 'DejaVuSans']
            base_font = None

            for font in hebrew_fonts:
                if font in self.registered_fonts:
                    base_font = font
                    break

            if not base_font:
                base_font = self.registered_fonts[0] if self.registered_fonts else 'Helvetica'

            # Define which columns we want in the PDF
            # These are the indexes in the product table
            # 0: Parcode/Barcode, 1: Name, 2: Quantity, 3: Price
            # We'll add a calculated column: 4: Total Value (qty * price)
            pdf_columns = [0, 1, 2, 3]

            # Get column headers for our selected columns
            headers = []

            # Column headers for the official inventory document
            # For RTL Hebrew document with extra "Total Value" column
            if rtl_mode:
                headers = [
                    self._process_hebrew_text("סה״כ שווי"),  # Total Value
                    self._process_hebrew_text("מחיר"),  # Price
                    self._process_hebrew_text("כמות"),  # Quantity
                    self._process_hebrew_text("שם חלק"),  # Part Name
                    self._process_hebrew_text("מקט")  # Barcode/Parcode
                ]
            else:
                # LTR version
                headers = [
                    "Barcode/ID",
                    "Part Name",
                    "Quantity",
                    "Price",
                    "Total Value"
                ]

            # Determine page size (A4 is standard for Israeli documents)
            page_size = A4

            # Apply orientation
            if settings['orientation'] == 1:  # Landscape
                page_size = landscape(page_size)

            # Create custom document with page templates for header/footer
            class InventoryDocTemplate(BaseDocTemplate):
                def __init__(self, filename, **kwargs):
                    BaseDocTemplate.__init__(self, filename, **kwargs)
                    self.inventory_date = kwargs.get('inventory_date', datetime.now().strftime("%d/%m/%Y"))
                    self.business_details = kwargs.get('business_details', {})
                    self.rtl_mode = kwargs.get('rtl_mode', True)
                    self.base_font = kwargs.get('base_font', 'David')
                    self.inventory_total = 0.0
                    self.doc_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{datetime.now().strftime('%H%M')}"

            # Create the document
            doc = InventoryDocTemplate(
                self.temp_pdf,
                pagesize=page_size,
                rightMargin=1.5 * cm,
                leftMargin=1.5 * cm,
                topMargin=2.5 * cm,
                bottomMargin=2.5 * cm,
                inventory_date=datetime.now().strftime("%d/%m/%Y"),
                business_details=self.business_details,
                rtl_mode=rtl_mode,
                base_font=base_font
            )

            # Define frames and page templates
            # Create a frame for the content
            content_frame = Frame(
                doc.leftMargin,
                doc.bottomMargin,
                doc.width,
                doc.height,
                id='normal'
            )

            # Define a function to add headers and footers to each page
            def header_footer(canvas, doc):
                """Add consistent header and footer to each page"""
                canvas.saveState()

                # Add document number with proper formatting for RTL
                canvas.setFont(base_font, 9)
                doc_number = doc.doc_number

                if rtl_mode:
                    # In RTL mode, handle document number differently
                    # First draw the document number label in Hebrew
                    label_text = self._process_hebrew_text("מספר מסמך:")
                    canvas.drawString(doc.leftMargin, doc.height + doc.bottomMargin + 20, label_text)

                    # Then draw the actual document number separately (not reversed)
                    canvas.drawString(doc.leftMargin + 80, doc.height + doc.bottomMargin + 20, doc_number)
                else:
                    doc_number_text = f"Document #: {doc_number}"
                    canvas.drawRightString(doc.width + doc.leftMargin, doc.height + doc.bottomMargin + 20,
                                           doc_number_text)

                # Draw the header if enabled
                if settings.get('print_header', True):
                    canvas.setFont(base_font, 14)
                    if rtl_mode:
                        header_text = self._process_hebrew_text("רשימת מלאי")
                        canvas.drawRightString(doc.width + doc.leftMargin,
                                               doc.height + doc.bottomMargin + 10,
                                               header_text)
                    else:
                        header_text = "Inventory Report"
                        canvas.drawString(doc.leftMargin,
                                          doc.height + doc.bottomMargin + 10,
                                          header_text)

                # Add border around the page for official look
                canvas.setStrokeColor(colors.black)
                canvas.setLineWidth(0.5)
                canvas.rect(
                    doc.leftMargin - 5,
                    doc.bottomMargin - 5,
                    doc.width + 10,
                    doc.height + 10
                )

                # Add page numbers in the footer
                canvas.setFont(base_font, 9)
                page_num = canvas.getPageNumber()

                if rtl_mode:
                    text = f"{page_num} {self._process_hebrew_text('עמוד')}"
                    canvas.drawString(doc.width + doc.leftMargin - 50, doc.bottomMargin - 20, text)
                else:
                    text = f"Page {page_num}"
                    canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 20, text)

                # Add date to footer
                if settings.get('print_date', True):
                    today = datetime.now().strftime("%d/%m/%Y")
                    if rtl_mode:
                        date_text = f"{today} :{self._process_hebrew_text('תאריך')}"
                        canvas.drawString(doc.leftMargin, doc.bottomMargin - 20, date_text)
                    else:
                        date_text = f"Date: {today}"
                        canvas.drawString(doc.leftMargin, doc.bottomMargin - 20, date_text)

                canvas.restoreState()

            # Create a page template
            page_template = PageTemplate(
                id='default',
                frames=[content_frame],
                onPage=header_footer
            )

            # Add the template to the document
            doc.addPageTemplates([page_template])

            # Create styles
            styles = getSampleStyleSheet()

            # Style for document title
            title_style = ParagraphStyle(
                'HebrewTitle',
                parent=styles['Heading1'],
                fontName=base_font,
                alignment=2 if rtl_mode else 1,  # Right for RTL, Center for LTR
                fontSize=18,
                leading=22,
                borderWidth=1,
                borderColor=colors.black,
                borderPadding=5,
                backColor=colors.whitesmoke
            )

            # Style for business name
            business_style = ParagraphStyle(
                'HebrewBusiness',
                parent=styles['Heading2'],
                fontName=base_font,
                alignment=2 if rtl_mode else 0,  # Right for RTL, Left for LTR
                fontSize=14,
                leading=16
            )

            # Style for section headers
            section_style = ParagraphStyle(
                'HebrewSection',
                parent=styles['Heading3'],
                fontName=base_font,
                alignment=2 if rtl_mode else 0,  # Right for RTL, Left for LTR
                fontSize=12,
                leading=14,
                borderWidth=0,
                borderColor=colors.black,
                borderRadius=3,
                borderPadding=2,
                backColor=colors.lightgrey
            )

            # Style for regular text
            text_style = ParagraphStyle(
                'HebrewText',
                parent=styles['Normal'],
                fontName=base_font,
                alignment=2 if rtl_mode else 0,  # Right for RTL, Left for LTR
                fontSize=10,
                leading=12
            )

            # Create content elements
            elements = []

            # --- START HEADER SECTION ---

            # Add official-looking mini-seal to the document - use business name from settings
            business_name = self.business_details.get('name', "") if rtl_mode else self.business_details.get('name_en',
                                                                                                             "")
            seal = OfficialSealFlowable(
                width=80,
                height=80,
                opacity=0.1,
                process_hebrew_func=self._process_hebrew_text,
                business_name=business_name
            )
            elements.append(seal)
            elements.append(Spacer(1, 0.2 * cm))

            # Document title - "Inventory Count Document" in Hebrew with formal styling
            title_text = self._process_hebrew_text("רשימת ספירת מלאי") if rtl_mode else "Inventory Count List"
            title = Paragraph(title_text, title_style)
            elements.append(title)

            # Add business details from the dialog
            if rtl_mode:
                business_name = self._process_hebrew_text(self.business_details.get('name', ""))
                business_address = self._process_hebrew_text(self.business_details.get('address', ""))
            else:
                business_name = self.business_details.get('name_en', "")
                business_address = self.business_details.get('address', "")

            elements.append(Spacer(1, 0.2 * cm))
            elements.append(Paragraph(business_name, business_style))
            elements.append(Spacer(1, 0.1 * cm))

            # Business details in a uniform format
            business_info = []
            if rtl_mode:
                business_info = [
                    f"{self._process_hebrew_text('כתובת')}: {business_address}",
                    f"{self._process_hebrew_text('טלפון')}: {self.business_details.get('phone', '')}",
                    f"{self._process_hebrew_text('מס׳ עוסק מורשה')}: {self.business_details.get('tax_id', '')}"
                ]
            else:
                business_info = [
                    f"Address: {business_address}",
                    f"Phone: {self.business_details.get('phone', '')}",
                    f"Tax ID: {self.business_details.get('tax_id', '')}"
                ]

            for info_line in business_info:
                elements.append(Paragraph(info_line, text_style))

            elements.append(Spacer(1, 0.5 * cm))

            # Add inventory details section
            current_date = datetime.now().strftime("%d/%m/%Y")
            current_year = datetime.now().year
            fiscal_year = f"{current_year}/{current_year + 1}"

            inventory_info = []
            if rtl_mode:
                inventory_info = [
                    f"{self._process_hebrew_text('תאריך ספירה')}: {current_date}",
                    f"{self._process_hebrew_text('שנת מס')}: {fiscal_year}",
                    # Removed "מספר דף: 1" as requested
                ]
            else:
                inventory_info = [
                    f"Inventory Date: {current_date}",
                    f"Fiscal Year: {fiscal_year}",
                    # Removed "Page Number: 1" as requested
                ]

            # Add a section header with more official styling
            inventory_section_header = self._process_hebrew_text("פרטי הספירה") if rtl_mode else "Inventory Details"
            section_paragraph = Paragraph(inventory_section_header, section_style)

            # Create a table for the section header to make it look more official
            section_table = Table([[section_paragraph]], colWidths=[doc.width])
            section_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT' if rtl_mode else 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ]))

            elements.append(section_table)
            elements.append(Spacer(1, 0.2 * cm))

            for info_line in inventory_info:
                elements.append(Paragraph(info_line, text_style))

            elements.append(Spacer(1, 0.3 * cm))

            # Add regulatory reference note with official look
            regulatory_note = (
                self._process_hebrew_text("בהתאם לתקנות מס הכנסה (ניהול פנקסי חשבונות), התשל״ו-1976")
                if rtl_mode else
                "In accordance with Income Tax Regulations (Management of Accounting Records), 1976"
            )

            regulatory_style = ParagraphStyle(
                'RegulatoryNote',
                parent=text_style,
                alignment=2 if rtl_mode else 0,
                fontName=base_font,
                fontSize=8,
                leading=10,
                textColor=colors.navy  # Changed from dark_blue to navy
            )

            elements.append(Paragraph(regulatory_note, regulatory_style))
            elements.append(Spacer(1, 0.5 * cm))

            # Add divider before table
            elements.append(HRFlowable(
                width="100%",
                thickness=1,
                color=colors.black,
                spaceAfter=0.5 * cm
            ))

            # --- END HEADER SECTION ---

            # --- START TABLE SECTION ---

            # Prepare data for table with RTL text processing
            table_data = []

            # Add headers
            table_data.append(headers)

            # Process and add product rows
            total_inventory_value = 0.0  # To calculate the total inventory value

            logger.info(f"Processing {len(products)} products for the PDF table")

            for product in products:
                row = []
                row_data = {}

                # We know the data is in tuple format from debug output:
                # The tuple structure is: (id, category, product_name, quantity, price, ...)

                # Extract ID/parcode from position 0
                parcode = str(product[0]) if len(product) > 0 else ''

                # Extract product name from position 2
                raw_name = str(product[2]) if len(product) > 2 else ''

                # Extract quantity from position 3
                try:
                    qty = int(product[3]) if len(product) > 3 and product[3] is not None else 0
                except (ValueError, TypeError):
                    qty = 0

                # Extract price from position 4
                try:
                    price = float(product[4]) if len(product) > 4 and product[4] is not None else 0.0
                except (ValueError, TypeError):
                    price = 0.0

                # Process Hebrew name if needed
                # Process mixed Hebrew/Latin name for correct display
                name = raw_name

                # Calculate total value
                total_value = qty * price

                # Format numeric values
                qty_str = str(qty)
                price_str = f"{price:.2f}"
                total_value_str = f"{total_value:.2f}"

                # Add to running total
                total_inventory_value += total_value

                # Map to row data
                row_data = {
                    0: parcode,  # Parcode/ID
                    1: name,  # Name
                    3: qty_str,  # Quantity
                    4: price_str,  # Price
                    5: total_value_str  # Total Value (calculated)
                }

                # Now add the data to the row in the correct order
                if rtl_mode:
                    # For RTL, we use: Total Value, Price, Quantity, Name, Parcode
                    row = [
                        row_data.get(5, '0.00'),  # Total Value
                        row_data.get(4, '0.00'),  # Price
                        row_data.get(3, '0'),  # Quantity
                        row_data.get(1, ''),  # Name
                        row_data.get(0, '')  # Parcode
                    ]
                else:
                    # For LTR: Parcode, Name, Quantity, Price, Total Value
                    row = [
                        row_data.get(0, ''),  # Parcode
                        row_data.get(1, ''),  # Name
                        row_data.get(3, '0'),  # Quantity
                        row_data.get(4, '0.00'),  # Price
                        row_data.get(5, '0.00')  # Total Value
                    ]

                table_data.append(row)

            # Store the total for the document
            doc.inventory_total = total_inventory_value

            # Calculate column widths based on page size
            page_width, page_height = page_size
            available_width = page_width - 3 * cm  # Account for margins

            # Column widths for official inventory document
            # Adjust for the 5 columns including the Total Value column
            if rtl_mode:
                # For RTL document: Total, Price, Qty, Name, Parcode
                col_widths = [
                    available_width * 0.18,  # Total Value - 18%
                    available_width * 0.15,  # Price - 15%
                    available_width * 0.12,  # Qty - 12%
                    available_width * 0.40,  # Name - 40%
                    available_width * 0.15,  # Parcode - 15%
                ]
            else:
                # For LTR document: Parcode, Name, Qty, Price, Total
                col_widths = [
                    available_width * 0.15,  # Parcode - 15%
                    available_width * 0.40,  # Name - 40%
                    available_width * 0.12,  # Qty - 12%
                    available_width * 0.15,  # Price - 15%
                    available_width * 0.18,  # Total Value - 18%
                ]

            # Find the name column index
            name_col_idx = 3 if rtl_mode else 1  # Name column index based on RTL mode

            # Process all rows - ensure names are always formatted as paragraphs
            for row_idx in range(1, len(table_data)):  # Skip header
                # Always create Paragraph for product name, regardless of length
                # Clean the text of any control characters
                # Process the text for correct display
                text = self._process_mixed_text(str(table_data[row_idx][name_col_idx]))

                # Create paragraph style with proper alignment
                para_style = ParagraphStyle(
                    f'Cell_{row_idx}_{name_col_idx}',
                    fontName=base_font,
                    fontSize=10,
                    alignment=2 if rtl_mode else 0,  # Right for RTL, Left for LTR
                    leading=12,  # Line spacing
                    spaceAfter=1
                )

                # Always convert name to Paragraph with cleaned text
                table_data[row_idx][name_col_idx] = Paragraph(text, para_style)

                # Standard cell formatting for other columns
                if rtl_mode:
                    table_data[row_idx][0] = format_cell(table_data[row_idx][0], "RIGHT")  # Total Value
                    table_data[row_idx][1] = format_cell(table_data[row_idx][1], "RIGHT")  # Price
                    table_data[row_idx][2] = format_cell(table_data[row_idx][2], "RIGHT")  # Qty
                    # Name is already handled as Paragraph
                    table_data[row_idx][4] = format_cell(table_data[row_idx][4], "CENTER")  # Parcode
                else:
                    table_data[row_idx][0] = format_cell(table_data[row_idx][0], "CENTER")  # Parcode
                    # Name is already handled as Paragraph
                    table_data[row_idx][2] = format_cell(table_data[row_idx][2], "RIGHT")  # Qty
                    table_data[row_idx][3] = format_cell(table_data[row_idx][3], "RIGHT")  # Price
                    table_data[row_idx][4] = format_cell(table_data[row_idx][4], "RIGHT")  # Total Value

            # Create table with updated data and enable splitting long words
            table = Table(table_data, colWidths=col_widths, repeatRows=1, splitByRow=True)

            # Prepare table style with dynamic alignments based on RTL mode - more official looking
            style_commands = [
                # Header style - bolder header for official look
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), base_font),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),  # Stronger border for whole table
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),  # Grid lines for all cells

                # Data rows
                ('FONTNAME', (0, 1), (-1, -1), base_font),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('WORDWRAP', (0, 0), (-1, -1), True),

                # Alternating row colors for better readability
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.whitesmoke]),

                # Padding - increased to allow more space for wrapped text
                ('TOPPADDING', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),

                # Inner grid lines
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),

                # Bottom line of header - make it thicker
                ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),
            ]

            # Add column-specific alignments based on RTL mode
            if rtl_mode:
                # RTL mode alignments
                style_commands.extend([
                    ('ALIGN', (0, 1), (0, -1), 'RIGHT'),  # Total Value
                    ('ALIGN', (1, 1), (1, -1), 'RIGHT'),  # Price
                    ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # Quantity
                    ('ALIGN', (3, 1), (3, -1), 'RIGHT'),  # Name
                    ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Parcode
                ])
            else:
                # LTR mode alignments
                style_commands.extend([
                    ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Parcode
                    ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Name
                    ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # Quantity
                    ('ALIGN', (3, 1), (3, -1), 'RIGHT'),  # Price
                    ('ALIGN', (4, 1), (4, -1), 'RIGHT'),  # Total Value
                ])

            style = TableStyle(style_commands)
            table.setStyle(style)
            elements.append(table)

            # --- END TABLE SECTION ---

            # --- START FOOTER SECTION ---

            elements.append(Spacer(1, 0.5 * cm))

            # Summary section with total inventory value
            formatted_total = f"{total_inventory_value:.2f}"

            # Add divider before summary
            elements.append(HRFlowable(
                width="100%",
                thickness=1,
                color=colors.black,
                spaceAfter=0.5 * cm
            ))

            # Total value summary with official styling
            total_label = self._process_hebrew_text("סך הכל שווי מלאי:") if rtl_mode else "Total Inventory Value:"

            # Create a table for the total value to make it look more official
            total_value_data = [[
                total_label,
                f"₪{formatted_total}"
            ]]

            total_table = Table(total_value_data, colWidths=[doc.width * 0.7, doc.width * 0.3])
            total_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), colors.whitesmoke),
                ('BACKGROUND', (1, 0), (1, 0), colors.whitesmoke),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (0, 0), 'RIGHT' if rtl_mode else 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), base_font),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ]))

            elements.append(total_table)
            elements.append(Spacer(1, 1 * cm))

            # Signature section with official look
            signature_section_text = self._process_hebrew_text("אישורים") if rtl_mode else "Authorizations"

            # Create section header for signatures
            signature_section = Paragraph(signature_section_text, section_style)
            signature_table = Table([[signature_section]], colWidths=[doc.width])
            signature_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT' if rtl_mode else 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
            ]))

            elements.append(signature_table)
            elements.append(Spacer(1, 0.5 * cm))

            # Create a table for signature fields for better alignment and more official look
            sig_data = []
            if rtl_mode:
                sig_data = [
                    [
                        self._process_hebrew_text("חתימת מנהל:"),
                        "",
                        self._process_hebrew_text("חתימת סופר המלאי:")
                    ],
                    ["_" * 20, "", "_" * 20],
                    [
                        self._process_hebrew_text("תפקיד:"),
                        "",
                        self._process_hebrew_text("תפקיד:")
                    ],
                    ["_" * 20, "", "_" * 20],
                    [
                        self._process_hebrew_text("תאריך:"),
                        "",
                        self._process_hebrew_text("תאריך:")
                    ],
                    ["_" * 20, "", "_" * 20],
                ]
            else:
                sig_data = [
                    [
                        "Inventory Taker Signature:",
                        "",
                        "Manager Signature:"
                    ],
                    ["_" * 20, "", "_" * 20],
                    [
                        "Position:",
                        "",
                        "Position:"
                    ],
                    ["_" * 20, "", "_" * 20],
                    [
                        "Date:",
                        "",
                        "Date:"
                    ],
                    ["_" * 20, "", "_" * 20],
                ]

            # Make the middle column wider for spacing
            sig_table = Table(sig_data, colWidths=[150, 60, 150])
            sig_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), base_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT' if rtl_mode else 'LEFT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT' if rtl_mode else 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 1), (0, -1), 0.5, colors.lightgrey),  # Light grid for signature lines
                ('GRID', (2, 1), (2, -1), 0.5, colors.lightgrey),  # Light grid for signature lines
            ]))

            elements.append(sig_table)

            # Add stamp/seal placeholder box
            stamp_label = self._process_hebrew_text("חותמת") if rtl_mode else "Stamp/Seal"
            stamp_box_data = [
                [stamp_label],
                [""],
                [""],
                [""]
            ]

            stamp_box = Table(stamp_box_data, colWidths=[100], rowHeights=[15, 25, 25, 25])
            stamp_box.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), base_font),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
            ]))

            # Position stamp box to the right or left based on RTL
            stamp_pos_table = Table([["", stamp_box]], colWidths=[doc.width - 110, 100])
            if rtl_mode:
                stamp_pos_table = Table([[stamp_box, ""]], colWidths=[100, doc.width - 110])

            elements.append(Spacer(1, 0.5 * cm))
            elements.append(stamp_pos_table)

            # Add final legal disclaimer with official styling
            elements.append(Spacer(1, 1 * cm))
            disclaimer = (
                self._process_hebrew_text("מסמך זה מהווה דוח רשמי של רשימת מלאי לצרכי דיווח למס הכנסה ומע\"מ")
                if rtl_mode else
                "This document constitutes an official inventory report for income tax and VAT reporting purposes"
            )

            disclaimer_style = ParagraphStyle(
                'Disclaimer',
                parent=styles['Normal'],
                fontName=base_font,
                alignment=1,  # Center alignment
                fontSize=9,
                leading=11,
                textColor=colors.navy,  # Changed from dark_blue to navy
                borderWidth=0.5,
                borderColor=colors.lightgrey,
                borderPadding=5,
                borderRadius=3
            )

            elements.append(Paragraph(disclaimer, disclaimer_style))

            # --- END FOOTER SECTION ---

            # Build the document
            doc.build(elements)
            logger.info("Israeli inventory count PDF document built successfully")
            return True

        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _process_mixed_text(self, text):
        """
        Process mixed Hebrew and Latin text for correct display in PDF.
        Handles the directionality properly for mixed content.
        """
        if not text:
            return text

        # Check if we have any Hebrew characters
        has_hebrew = any(0x0590 <= ord(c) <= 0x05FF for c in text)
        if not has_hebrew:
            return text  # No Hebrew, return as is

        try:
            import bidi.algorithm

            # For mixed content in a predominantly RTL context,
            # we need to process it with bidi algorithm
            # This ensures the text appears in the correct order
            return bidi.algorithm.get_display(text)

        except Exception as e:
            logger.error(f"Error processing mixed text: {e}")
            return text

    def _clean_text_for_pdf(self, text):
        """
        Clean text for PDF by removing any existing bidirectional control characters
        that might cause problems in ReportLab.
        """
        if not text:
            return text

        # Remove common bidirectional control characters that might be present
        control_chars = [
            '\u200E',  # LRM - LEFT-TO-RIGHT MARK
            '\u200F',  # RLM - RIGHT-TO-LEFT MARK
            '\u202A',  # LRE - LEFT-TO-RIGHT EMBEDDING
            '\u202B',  # RLE - RIGHT-TO-LEFT EMBEDDING
            '\u202C',  # PDF - POP DIRECTIONAL FORMATTING
            '\u202D',  # LRO - LEFT-TO-RIGHT OVERRIDE
            '\u202E'  # RLO - RIGHT-TO-LEFT OVERRIDE
        ]

        result = text
        for char in control_chars:
            result = result.replace(char, '')

        return result