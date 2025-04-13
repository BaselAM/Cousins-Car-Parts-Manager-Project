"""
Enhanced print settings dialog with stacked widget and text direction support.
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QFrame,
                             QWidget, QGridLayout, QButtonGroup, QSizePolicy,
                             QSpacerItem, QApplication, QStackedWidget)
from PyQt5.QtCore import Qt, QSize, QPoint, QRect
from PyQt5.QtGui import QPixmap, QColor, QPainter, QFont

from themes import get_color
from widgets.products.dialogs.base_dialog import ElegantDialog
from widgets.products.components.styled_widgets import (
    StyledRadioButton, StyledCheckBox, StyledComboBox,
    StyledPushButton, StyledGroupBox, StyledTitleLabel, StyledSubtitleLabel,
    StyledLineEdit
)
from database.settings_db import SettingsDB


class PrintIcon(QWidget):
    """Custom print icon widget for the dialog header with enhanced preview capabilities"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(42, 42)

        # Settings to display in the icon
        self.show_date = True
        self.show_header = True
        self.rtl_mode = False

    def update_settings(self, show_date, show_header, rtl_mode):
        """Update the icon to reflect current settings"""
        self.show_date = show_date
        self.show_header = show_header
        self.rtl_mode = rtl_mode
        self.update()  # Trigger repaint

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get colors from theme
        accent_color = QColor(get_color('accent', get_color('highlight', '#3f83f1')))
        bg_color = QColor(get_color('background'))
        text_color = QColor(get_color('text', '#333333'))

        # Draw printer icon
        painter.setPen(Qt.NoPen)
        painter.setBrush(accent_color)

        # Printer body
        painter.drawRoundedRect(6, 14, 30, 20, 3, 3)

        # Paper tray
        painter.drawRoundedRect(10, 8, 22, 6, 2, 2)

        # Paper output
        painter.setBrush(QColor(get_color('background')))
        painter.drawRoundedRect(12, 20, 18, 8, 2, 2)

        # Control panel
        painter.setBrush(QColor(get_color('background')))
        painter.drawRect(30, 18, 3, 3)

        # Paper
        paper_color = QColor(255, 255, 255)
        painter.setBrush(paper_color)
        paper_rect = QRect(14, 2, 14, 10)
        painter.drawRect(paper_rect)

        # Add detail to the paper based on settings
        painter.setPen(QColor(150, 150, 150))

        # Tiny text area to represent document
        inner_rect = paper_rect.adjusted(1, 1, -1, -1)

        # Header if enabled - show as a bold line at the top
        if self.show_header:
            header_rect = QRect(inner_rect.left(), inner_rect.top(), inner_rect.width(), 2)
            painter.fillRect(header_rect, QColor(180, 180, 180))

        # Date if enabled - show as a small line on the appropriate side
        if self.show_date:
            date_y = inner_rect.top() + 3
            date_width = inner_rect.width() * 0.7

            if self.rtl_mode:
                # Right-aligned date for RTL mode
                date_x = inner_rect.right() - date_width
            else:
                # Left-aligned date for LTR mode
                date_x = inner_rect.left()

            painter.drawLine(date_x, date_y, date_x + date_width, date_y)

        # Text lines to represent content
        line_spacing = 1
        start_y = inner_rect.top() + (5 if self.show_header else 2)

        for i in range(3):
            line_y = start_y + (i * line_spacing)
            if self.rtl_mode:
                # Right to left text lines
                line_width = inner_rect.width() * (0.8 - (i * 0.2))
                line_x = inner_rect.right() - line_width
            else:
                # Left to right text lines
                line_width = inner_rect.width() * (0.8 - (i * 0.2))
                line_x = inner_rect.left()

            painter.drawLine(line_x, line_y, line_x + line_width, line_y)


class PrintSettingsDialog(ElegantDialog):
    """Dialog for configuring print settings that uses the enhanced base dialog"""

    def __init__(self, translator, parent=None, business_details=None):
        # Get system language for text direction
        self.settings_db = SettingsDB()
        self.system_language = self.settings_db.get_setting('language', 'en')
        self.is_rtl_system = self.system_language == 'he' or self.settings_db.get_rtl_setting()

        super().__init__(translator, parent, title='print_settings')
        self.setMinimumWidth(480)
        self.setMinimumHeight(450)

        # Default business details if none provided
        self.business_details = business_details or {
            'name': "חלקי חילוף אבו מוך",
            'name_en': "Abu Mukh Car Parts",
            'address': "באקה אל גרבייה, ביר באקה",
            'phone': "046077888",
            'tax_id': "123456789",
            'logo_path': None  # Path to logo if available
        }

        # Setup the UI components
        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog UI components"""
        # --- Dialog title and icon (shown on both pages) ---
        header_layout = QHBoxLayout()

        # Icon
        self.print_icon = PrintIcon()
        header_layout.addWidget(self.print_icon)

        # Title and subtitle
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        self.title_label = StyledTitleLabel(self.translator.t('print_settings'))

        self.subtitle_label = StyledSubtitleLabel(self.translator.t('print_setup_description')
                                                  if hasattr(self.translator, 't') and callable(
            getattr(self.translator, 't'))
                                                  else "Configure how you want to print your products.")

        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch(1)

        self.main_layout.addLayout(header_layout)

        # Separator line
        self.add_separator()

        # --- Stacked widget for pages ---
        self.stacked_widget = QStackedWidget()

        # Create main settings page
        self.main_page = QWidget()
        self.setup_main_page()

        # Create business details page
        self.details_page = QWidget()
        self.setup_details_page()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.details_page)

        # Add stacked widget to main layout
        self.main_layout.addWidget(self.stacked_widget)

        # Separator before buttons
        self.add_separator()

        # Create button layout - these will be shown on both pages
        self.preview_button = StyledPushButton(self.translator.t('preview_and_print'), True)
        self.cancel_button = StyledPushButton(self.translator.t('cancel'))

        self.preview_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.create_button_layout(
            primary_button=self.preview_button,
            secondary_button=self.cancel_button
        )

        # Initialize preview
        self.update_preview()

    def setup_main_page(self):
        """Set up the main settings page"""
        main_layout = QHBoxLayout(self.main_page)
        main_layout.setSpacing(15)

        # Left column - settings
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(12)

        # Print scope options
        scope_group = StyledGroupBox(self.translator.t('print_scope'))
        scope_layout = QVBoxLayout(scope_group)
        scope_layout.setSpacing(6)
        scope_layout.setContentsMargins(10, 10, 10, 10)

        self.print_all_radio = StyledRadioButton(self.translator.t('print_all_products'))
        self.print_selected_radio = StyledRadioButton(self.translator.t('print_selected_products'))
        self.print_filtered_radio = StyledRadioButton(self.translator.t('print_filtered_products'))

        # Create button group for radio buttons
        self.scope_group = QButtonGroup(self)
        self.scope_group.addButton(self.print_all_radio, 0)
        self.scope_group.addButton(self.print_selected_radio, 1)
        self.scope_group.addButton(self.print_filtered_radio, 2)

        # Default to "All Products"
        self.print_all_radio.setChecked(True)

        # Set tooltips
        self.print_all_radio.setToolTip(self.translator.t('print_all_tooltip')
                                        if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                                        else "Print all products in the database")
        self.print_selected_radio.setToolTip(self.translator.t('print_selected_tooltip')
                                             if hasattr(self.translator, 't') and callable(
            getattr(self.translator, 't'))
                                             else "Print only the products you've selected")
        self.print_filtered_radio.setToolTip(self.translator.t('print_filtered_tooltip')
                                             if hasattr(self.translator, 't') and callable(
            getattr(self.translator, 't'))
                                             else "Print products that match your current filter")

        scope_layout.addWidget(self.print_all_radio)
        scope_layout.addWidget(self.print_selected_radio)
        scope_layout.addWidget(self.print_filtered_radio)
        settings_layout.addWidget(scope_group)

        # Page options
        options_group = StyledGroupBox(self.translator.t('print_options'))
        options_layout = QGridLayout(options_group)
        options_layout.setColumnStretch(1, 1)
        options_layout.setVerticalSpacing(10)
        options_layout.setHorizontalSpacing(15)
        options_layout.setContentsMargins(10, 10, 10, 10)

        # Paper size selection
        paper_label = QLabel(self.translator.t('paper_size'))
        paper_label.setToolTip(self.translator.t('paper_size_tooltip')
                               if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                               else "Select the paper size for printing")
        self.paper_size_combo = StyledComboBox()
        self.paper_size_combo.addItems(['A4', 'Letter', 'Legal'])

        options_layout.addWidget(paper_label, 0, 0)
        options_layout.addWidget(self.paper_size_combo, 0, 1)

        # Orientation selection
        orientation_label = QLabel(self.translator.t('orientation'))
        orientation_label.setToolTip(self.translator.t('orientation_tooltip')
                                     if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                                     else "Choose between portrait (vertical) or landscape (horizontal) orientation")
        self.orientation_combo = StyledComboBox()
        self.orientation_combo.addItems([
            self.translator.t('portrait'),
            self.translator.t('landscape')
        ])

        options_layout.addWidget(orientation_label, 1, 0)
        options_layout.addWidget(self.orientation_combo, 1, 1)

        # Checkboxes for additional options
        self.print_header_check = StyledCheckBox(self.translator.t('print_header'))
        self.print_header_check.setToolTip(self.translator.t('print_header_tooltip')
                                           if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                                           else "Include a header with the report title")
        self.print_header_check.setChecked(True)

        options_layout.addWidget(self.print_header_check, 2, 0, 1, 2)

        self.print_date_check = StyledCheckBox(self.translator.t('print_date'))
        self.print_date_check.setToolTip(self.translator.t('print_date_tooltip')
                                         if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                                         else "Include the current date in the report")
        self.print_date_check.setChecked(True)

        options_layout.addWidget(self.print_date_check, 3, 0, 1, 2)

        # RTL mode option - default to system language setting
        self.rtl_mode_check = StyledCheckBox(self.translator.t('rtl_mode')
                                             if hasattr(self.translator, 't') and callable(
            getattr(self.translator, 't'))
                                             else "RTL Mode (Right-to-Left)")
        self.rtl_mode_check.setToolTip(self.translator.t('rtl_mode_tooltip')
                                       if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                                       else "Enable right-to-left layout for Hebrew or Arabic text")
        # Set default based on system language
        self.rtl_mode_check.setChecked(self.is_rtl_system)

        options_layout.addWidget(self.rtl_mode_check, 4, 0, 1, 2)

        settings_layout.addWidget(options_group)

        # Button to navigate to business details page
        self.details_button = StyledPushButton(self.translator.t('business_details')
                                              if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                                              else "Business Details")
        self.details_button.setIcon(self.style().standardIcon(QApplication.style().SP_ArrowForward))
        self.details_button.clicked.connect(self.show_details_page)

        settings_layout.addWidget(self.details_button)
        settings_layout.addStretch(1)

        # Right column - preview illustration
        preview_layout = QVBoxLayout()

        # Preview widget
        preview_frame = QFrame()
        preview_frame.setFrameShape(QFrame.StyledPanel)
        preview_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {QColor(get_color('background')).lighter(110).name()};
                border: 1px solid {get_color('border')};
                border-radius: 10px;
            }}
        """)
        preview_frame.setMinimumWidth(160)

        # Add document preview illustration
        preview_frame_layout = QVBoxLayout(preview_frame)
        preview_frame_layout.setContentsMargins(5, 5, 5, 5)

        # Paper icon (simplified)
        self.doc_preview = QLabel()
        self.doc_preview.setAlignment(Qt.AlignCenter)
        self.doc_preview.setMinimumHeight(180)

        preview_frame_layout.addWidget(self.doc_preview)
        preview_layout.addWidget(preview_frame)
        preview_layout.addStretch(1)

        # Connect preview update signals
        self.orientation_combo.currentIndexChanged.connect(self.update_preview)
        self.paper_size_combo.currentIndexChanged.connect(self.update_preview)
        self.print_header_check.toggled.connect(self.update_preview)
        self.print_date_check.toggled.connect(self.update_preview)
        self.rtl_mode_check.toggled.connect(self.update_preview)

        # Add layouts to main page - layout stays the same regardless of language
        main_layout.addLayout(settings_layout, 7)  # 70% width for settings
        main_layout.addLayout(preview_layout, 3)   # 30% width for preview

    def setup_details_page(self):
        """Set up the business details page"""
        details_layout = QVBoxLayout(self.details_page)

        # Header with back button
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 10)

        # Back button
        self.back_button = StyledPushButton(self.translator.t('back')
                                            if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                                            else "Back")
        self.back_button.setIcon(self.style().standardIcon(QApplication.style().SP_ArrowBack))
        self.back_button.clicked.connect(self.show_main_page)

        # Page title
        details_title = QLabel(self.translator.t('business_details')
                              if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                              else "Business Details")
        font = details_title.font()
        font.setPointSize(12)
        font.setBold(True)
        details_title.setFont(font)

        # Layout stays the same regardless of language
        header_layout.addWidget(self.back_button)
        header_layout.addWidget(details_title)
        header_layout.addStretch()

        details_layout.addWidget(header_widget)

        # Business details form
        form_group = StyledGroupBox("")  # No title needed since we have the header
        form_layout = QGridLayout(form_group)
        form_layout.setVerticalSpacing(12)
        form_layout.setHorizontalSpacing(15)
        form_layout.setContentsMargins(15, 15, 15, 15)

        # Hebrew name
        name_label = QLabel(self.translator.t('business_name')
                          if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                          else "Business Name (Hebrew)")
        self.name_edit = StyledLineEdit()
        self.name_edit.setText(self.business_details.get('name', ''))
        # Always RTL for Hebrew text regardless of system language
        self.name_edit.setLayoutDirection(Qt.RightToLeft)

        # English name
        name_en_label = QLabel(self.translator.t('business_name_en')
                             if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                             else "Business Name (English)")
        self.name_en_edit = StyledLineEdit()
        self.name_en_edit.setText(self.business_details.get('name_en', ''))
        # Always LTR for English text regardless of system language
        self.name_en_edit.setLayoutDirection(Qt.LeftToRight)

        # Address
        address_label = QLabel(self.translator.t('business_address')
                             if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                             else "Address")
        self.address_edit = StyledLineEdit()
        self.address_edit.setText(self.business_details.get('address', ''))
        # Set layout direction based on system language (content is likely mixed)
        self.address_edit.setLayoutDirection(Qt.RightToLeft if self.is_rtl_system else Qt.LeftToRight)

        # Phone
        phone_label = QLabel(self.translator.t('business_phone')
                           if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                           else "Phone Number")
        self.phone_edit = StyledLineEdit()
        self.phone_edit.setText(self.business_details.get('phone', ''))
        # Phone numbers read LTR even in RTL languages
        self.phone_edit.setLayoutDirection(Qt.LeftToRight)

        # Tax ID
        tax_id_label = QLabel(self.translator.t('business_tax_id')
                            if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                            else "Tax ID")
        self.tax_id_edit = StyledLineEdit()
        self.tax_id_edit.setText(self.business_details.get('tax_id', ''))
        # Tax ID numbers read LTR even in RTL languages
        self.tax_id_edit.setLayoutDirection(Qt.LeftToRight)

        # Add form elements - layout stays the same regardless of language
        form_layout.addWidget(name_label, 0, 0)
        form_layout.addWidget(self.name_edit, 0, 1)

        form_layout.addWidget(name_en_label, 1, 0)
        form_layout.addWidget(self.name_en_edit, 1, 1)

        form_layout.addWidget(address_label, 2, 0)
        form_layout.addWidget(self.address_edit, 2, 1)

        form_layout.addWidget(phone_label, 3, 0)
        form_layout.addWidget(self.phone_edit, 3, 1)

        form_layout.addWidget(tax_id_label, 4, 0)
        form_layout.addWidget(self.tax_id_edit, 4, 1)

        # Set column stretch
        form_layout.setColumnStretch(1, 1)  # Fields get more space

        # Add form to layout
        details_layout.addWidget(form_group)
        details_layout.addStretch(1)

        # Add help text at the bottom
        help_text = QLabel(self.translator.t('business_details_help')
                          if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                          else "These details will appear on your printed documents.")
        help_text.setStyleSheet(f"color: {get_color('secondary_text', get_color('text'))};")
        details_layout.addWidget(help_text)

    def show_details_page(self):
        """Switch to the business details page"""
        self.stacked_widget.setCurrentWidget(self.details_page)
        self.details_button.setEnabled(False)

    def show_main_page(self):
        """Switch back to the main settings page"""
        self.stacked_widget.setCurrentWidget(self.main_page)
        self.details_button.setEnabled(True)

    def update_preview(self):
        """Update the preview illustration based on current settings"""
        # First update the printer icon to reflect current settings
        self.print_icon.update_settings(
            self.print_date_check.isChecked(),
            self.print_header_check.isChecked(),
            self.rtl_mode_check.isChecked()
        )

        # Create a pixmap to draw on
        pixmap = QPixmap(150, 180)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get colors for preview
        bg_color = QColor(get_color('background'))
        text_color = QColor(get_color('text'))
        accent_color = QColor(get_color('accent', get_color('highlight', '#3f83f1')))

        # Draw paper
        paper_color = QColor(255, 255, 255, 245)  # Slightly transparent white
        painter.setPen(Qt.NoPen)
        painter.setBrush(paper_color)

        # Adjust aspect ratio based on orientation and paper size
        is_landscape = self.orientation_combo.currentIndex() == 1
        paper_size = self.paper_size_combo.currentText()

        if is_landscape:
            # Landscape orientation
            paper_width = 140
            if paper_size == 'A4':
                paper_height = 90
            elif paper_size == 'Legal':
                paper_height = 80
            else:  # Letter
                paper_height = 100

            # Draw landscape paper
            painter.drawRoundedRect(5, 45, paper_width, paper_height, 4, 4)

            # Shadow effect
            shadow = QColor(0, 0, 0, 30)
            painter.setBrush(shadow)
            painter.drawRoundedRect(8, 48, paper_width, paper_height, 4, 4)
        else:
            # Portrait orientation
            paper_height = 160  # Reduced
            if paper_size == 'A4':
                paper_width = 114
            elif paper_size == 'Legal':
                paper_width = 100
                paper_height = 170
            else:  # Letter
                paper_width = 127

            # Draw portrait paper
            painter.drawRoundedRect(pixmap.width() / 2 - paper_width / 2, 10, paper_width, paper_height, 4, 4)

            # Shadow effect
            shadow = QColor(0, 0, 0, 30)
            painter.setBrush(shadow)
            painter.drawRoundedRect(pixmap.width() / 2 - paper_width / 2 + 3, 13, paper_width, paper_height, 4, 4)

        # Draw content preview on paper
        painter.setPen(QColor(150, 150, 150, 200))  # Light gray for text simulation

        rtl_mode = self.rtl_mode_check.isChecked()

        if is_landscape:
            content_x = 15
            content_y = 55
            content_width = paper_width - 20

            # Header if enabled - make it more prominent
            if self.print_header_check.isChecked():
                header_y = content_y + 10
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(180, 180, 180))
                painter.drawRect(content_x, header_y, content_width, 12)

                # Add "title" text to header
                painter.setPen(QColor(255, 255, 255))
                font = painter.font()
                font.setPointSize(6)
                painter.setFont(font)
                header_text = "Inventory Report"
                if rtl_mode:
                    painter.drawText(content_x + content_width - 50, header_y + 9, header_text)
                else:
                    painter.drawText(content_x + 10, header_y + 9, header_text)

                content_y += 24
                painter.setPen(QColor(150, 150, 150, 200))

            # Date if enabled - make it more prominent
            if self.print_date_check.isChecked():
                date_y = content_y
                date_width = 50

                # Draw date placeholder with text
                if rtl_mode:
                    painter.drawText(content_x + content_width - date_width, date_y, "תאריך: ")
                else:
                    painter.drawText(content_x, date_y, "Date: ")

                content_y += 12

            # Table header
            painter.setPen(QColor(180, 180, 180))
            painter.setBrush(QColor(230, 230, 230))
            painter.drawRect(content_x, content_y, content_width, 14)

            # Draw header text placeholder
            painter.setPen(QColor(100, 100, 100))
            header_y = content_y + 10
            col_width = content_width / 5

            # Show column headers based on RTL mode
            if rtl_mode:
                # RTL column headers (right to left)
                cols = ["סה״כ", "מחיר", "כמות", "שם", "מקט"]
                for i, col in enumerate(cols):
                    painter.drawText(content_x + content_width - (i + 0.7) * col_width, header_y, col)
            else:
                # LTR column headers (left to right)
                cols = ["ID", "Name", "Qty", "Price", "Total"]
                for i, col in enumerate(cols):
                    painter.drawText(content_x + i * col_width + 5, header_y, col)

            content_y += 14
            painter.setPen(QColor(150, 150, 150, 200))

            # Table grid
            row_height = 10
            row_spacing = 12
            rows = 3

            # Draw table grid lines
            for i in range(rows):
                y = content_y + (i * row_spacing)
                painter.drawLine(content_x, y, content_x + content_width, y)

                # Draw row content (different direction based on RTL)
                if rtl_mode:
                    # RTL table rows
                    painter.drawLine(content_x + 10, y + 5, content_x + 50, y + 5)
                else:
                    # LTR table rows
                    painter.drawLine(content_x + content_width - 50, y + 5, content_x + content_width - 10, y + 5)

            # Vertical grid lines
            if rtl_mode:
                cols = [0.2, 0.4, 0.65, 0.85]
            else:
                cols = [0.15, 0.35, 0.6, 0.8]

            for col_pct in cols:
                x = content_x + (content_width * col_pct)
                painter.drawLine(x, content_y - 14, x, content_y + (rows * row_spacing))
        else:
            # Portrait layout
            content_x = pixmap.width() / 2 - paper_width / 2 + 10
            content_y = 20
            content_width = paper_width - 20

            # Header if enabled - make it more prominent
            if self.print_header_check.isChecked():
                header_y = content_y + 8
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(180, 180, 180))
                painter.drawRect(content_x, header_y, content_width, 12)

                # Add "title" text to header
                painter.setPen(QColor(255, 255, 255))
                font = painter.font()
                font.setPointSize(6)
                painter.setFont(font)
                header_text = "Inventory Report"
                if rtl_mode:
                    painter.drawText(content_x + content_width - 50, header_y + 9, header_text)
                else:
                    painter.drawText(content_x + 10, header_y + 9, header_text)

                content_y += 22
                painter.setPen(QColor(150, 150, 150, 200))

            # Date if enabled - make it more prominent
            if self.print_date_check.isChecked():
                date_y = content_y

                # Draw date placeholder with text
                if rtl_mode:
                    painter.drawText(content_x + content_width - 40, date_y, "תאריך: ")
                else:
                    painter.drawText(content_x, date_y, "Date: ")

                content_y += 12

            # Table header
            painter.setPen(QColor(180, 180, 180))
            painter.setBrush(QColor(230, 230, 230))
            painter.drawRect(content_x, content_y, content_width, 14)

            # Draw header text placeholder
            painter.setPen(QColor(100, 100, 100))
            header_y = content_y + 10
            col_width = content_width / 4

            # Show column headers based on RTL mode
            if rtl_mode:
                # RTL column headers (right to left)
                cols = ["סה״כ", "מחיר", "כמות", "שם"]
                for i, col in enumerate(cols):
                    painter.drawText(content_x + content_width - (i + 0.7) * col_width, header_y, col)
            else:
                # LTR column headers (left to right)
                cols = ["Name", "Qty", "Price", "Total"]
                for i, col in enumerate(cols):
                    painter.drawText(content_x + i * col_width + 5, header_y, col)

            content_y += 14
            painter.setPen(QColor(150, 150, 150, 200))

            # Table grid
            row_height = 8
            row_spacing = 10
            rows = 6

            # Draw table grid lines
            for i in range(rows):
                y = content_y + (i * row_spacing)
                painter.drawLine(content_x, y, content_x + content_width, y)

                # Draw row content (different direction based on RTL)
                if rtl_mode:
                    # RTL table rows
                    painter.drawLine(content_x + 8, y + 4, content_x + 40, y + 4)
                else:
                    # LTR table rows
                    painter.drawLine(content_x + content_width - 40, y + 4, content_x + content_width - 8, y + 4)

            # Vertical grid lines
            if rtl_mode:
                cols = [0.25, 0.5, 0.75]
            else:
                cols = [0.25, 0.5, 0.75]

            for col_pct in cols:
                x = content_x + (content_width * col_pct)
                painter.drawLine(x, content_y - 14, x, content_y + (rows * row_spacing))

        painter.end()

        # Set the pixmap to the label
        self.doc_preview.setPixmap(pixmap)

    def get_settings(self):
        """Get the selected print settings"""
        settings = {
            'scope': self.scope_group.checkedId(),
            'paper_size': self.paper_size_combo.currentText(),
            'orientation': self.orientation_combo.currentIndex(),  # 0=Portrait, 1=Landscape
            'print_header': self.print_header_check.isChecked(),
            'print_date': self.print_date_check.isChecked(),
            'rtl_mode': self.rtl_mode_check.isChecked(),  # Setting for RTL mode
            'business_details': {
                'name': self.name_edit.text(),
                'name_en': self.name_en_edit.text(),
                'address': self.address_edit.text(),
                'phone': self.phone_edit.text(),
                'tax_id': self.tax_id_edit.text(),
                'logo_path': self.business_details.get('logo_path')  # Keep existing logo path
            }
        }
        return settings

    def showEvent(self, event):
        """Center the dialog when it's shown"""
        super().showEvent(event)
        # Center the dialog on the screen immediately when shown
        self.centerOnScreen()

    def centerOnScreen(self):
        """Center the dialog on the screen"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)