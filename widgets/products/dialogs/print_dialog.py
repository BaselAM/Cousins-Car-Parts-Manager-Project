from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QCheckBox, QGroupBox, QRadioButton, QButtonGroup,
                             QComboBox, QSpacerItem, QSizePolicy, QMessageBox,
                             QWidget, QGridLayout, QFrame, QApplication)
from PyQt5.QtCore import Qt, QSize, QPoint
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QPalette, QCursor
from themes import get_color


class StyledRadioButton(QRadioButton):
    """Custom styled radio button with elegant indicator styling"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        accent_color = get_color('accent', get_color('highlight', '#3f83f1'))
        bg_color = get_color('background')

        # Elegant styling for the radio button indicator only
        self.setStyleSheet(f"""
            QRadioButton {{
                color: {text_color};
                font-size: 13px;
                spacing: 10px;
                padding: 4px;
            }}

            QRadioButton:checked {{
                font-weight: bold;
            }}

            QRadioButton::indicator {{
                width: 22px;
                height: 22px;
                border-radius: 11px;
                border: 2px solid {QColor(text_color).lighter(130).name()};
                background-color: {bg_color};
            }}

            QRadioButton::indicator:hover {{
                border: 2px solid {accent_color};
            }}

            QRadioButton::indicator:checked {{
                border: 2px solid {accent_color};
                background-color: {bg_color};
            }}

            QRadioButton::indicator:checked {{
                image: url(data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB3aWR0aD0iMTJweCIgaGVpZ2h0PSIxMnB4IiB2aWV3Qm94PSIwIDAgMTIgMTIiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgIDxjaXJjbGUgZmlsbD0iIzNmODNmMSIgY3g9IjYiIGN5PSI2IiByPSI1Ii8+Cjwvc3ZnPg==);
            }}
        """)


class StyledCheckBox(QCheckBox):
    """Custom styled checkbox with hover effects"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        accent_color = get_color('accent', get_color('highlight', '#3f83f1'))
        bg_color = get_color('background')

        # Custom style with hover effects
        self.setStyleSheet(f"""
            QCheckBox {{
                color: {text_color};
                font-size: 13px;
                spacing: 8px;
                padding: 4px 2px;
                border-radius: 4px;
            }}

            QCheckBox:hover {{
                background-color: {QColor(accent_color).lighter(180).name()};
            }}

            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {QColor(text_color).lighter(130).name()};
                background-color: {bg_color};
            }}

            QCheckBox::indicator:unchecked:hover {{
                border: 2px solid {accent_color};
            }}

            QCheckBox::indicator:checked {{
                background-color: {accent_color};
                border: 2px solid {accent_color};
                image: url(data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPHN2ZyB3aWR0aD0iMTJweCIgaGVpZ2h0PSIxMnB4IiB2aWV3Qm94PSIwIDAgMTIgMTIiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgIDxwYXRoIGZpbGw9IndoaXRlIiBkPSJNOSAzbDIgMi00IDYtNC0yIDEuNS0yLjVMMTAgMnoiLz4KPC9zdmc+);
            }}

            QCheckBox::indicator:checked:hover {{
                background-color: {QColor(accent_color).darker(110).name()};
                border: 2px solid {QColor(accent_color).darker(110).name()};
            }}
        """)


class StyledComboBox(QComboBox):
    """Custom styled combobox with hover effects"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        bg_color = get_color('background')
        accent_color = get_color('accent', get_color('highlight', '#3f83f1'))
        border_color = get_color('border', QColor(text_color).lighter(150).name())

        # Custom style with hover effects
        self.setStyleSheet(f"""
            QComboBox {{
                color: {text_color};
                background-color: {QColor(bg_color).darker(105).name()};
                border: 1px solid {border_color};
                border-radius: 6px;
                padding: 5px 10px;
                min-width: 6em;
                font-size: 13px;
            }}

            QComboBox:hover {{
                border: 1px solid {accent_color};
            }}

            QComboBox:focus {{
                border: 1px solid {accent_color};
            }}

            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: none;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }}

            QComboBox::down-arrow {{
                image: none;
                width: 8px;
                height: 8px;
                background-color: {text_color};
                border-radius: 4px;
            }}

            QComboBox QAbstractItemView {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 0px;
                selection-background-color: {accent_color};
                selection-color: {bg_color};
                outline: none;
            }}

            QComboBox QAbstractItemView::item {{
                min-height: 24px;
                padding: 4px 8px;
                color: {text_color};
            }}

            QComboBox QAbstractItemView::item:selected {{
                background-color: {accent_color};
                color: {bg_color};
            }}
        """)


class StyledButton(QPushButton):
    """Custom styled button with hover and pressed effects"""

    def __init__(self, text, is_primary=False, parent=None):
        super().__init__(text, parent)
        self.is_primary = is_primary
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        bg_color = get_color('background')
        accent_color = get_color('accent', get_color('highlight', '#3f83f1'))

        if self.is_primary:
            # Primary button (filled style)
            self.setStyleSheet(f"""
                QPushButton {{
                    color: {bg_color};
                    background-color: {accent_color};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    font-size: 13px;
                }}

                QPushButton:hover {{
                    background-color: {QColor(accent_color).darker(110).name()};
                }}

                QPushButton:pressed {{
                    background-color: {QColor(accent_color).darker(130).name()};
                }}

                QPushButton:disabled {{
                    background-color: {QColor(accent_color).lighter(150).name()};
                    color: {QColor(bg_color).darker(110).name()};
                }}
            """)
        else:
            # Secondary button (outline style)
            self.setStyleSheet(f"""
                QPushButton {{
                    color: {text_color};
                    background-color: transparent;
                    border: 1px solid {QColor(text_color).lighter(130).name()};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                }}

                QPushButton:hover {{
                    background-color: {QColor(bg_color).darker(110).name()};
                    border: 1px solid {QColor(text_color).lighter(110).name()};
                }}

                QPushButton:pressed {{
                    background-color: {QColor(bg_color).darker(120).name()};
                }}

                QPushButton:disabled {{
                    color: {QColor(text_color).lighter(160).name()};
                    border: 1px solid {QColor(text_color).lighter(160).name()};
                }}
            """)


class StyledGroupBox(QGroupBox):
    """Custom styled group box with modern appearance"""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self._update_style()

    def _update_style(self):
        text_color = get_color('text')
        bg_color = get_color('background')
        border_color = get_color('border', QColor(text_color).lighter(150).name())

        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 14px;
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                margin-top: 1.1em;
                padding: 10px;
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                top: -0.5em;
                padding: 0 5px;
                background-color: {bg_color};
            }}
        """)


class PrintIcon(QWidget):
    """Custom print icon widget for the dialog header"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(42, 42)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Get colors from theme
        accent_color = QColor(get_color('accent', get_color('highlight', '#3f83f1')))

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
        paper_color = QColor(get_color('background'))
        paper_color.setAlpha(230)
        painter.setBrush(paper_color)
        painter.drawRect(14, 2, 14, 10)


class PrintSettingsDialog(QDialog):
    """Dialog for configuring print settings"""

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.setWindowTitle(self.translator.t('print_settings'))
        self.setMinimumWidth(480)
        # Reduced height for a more compact dialog
        self.setMinimumHeight(420)

        # Variables for tracking mouse movement for dragging
        self.dragging = False
        self.drag_position = None

        # Main layout with reduced spacing
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)  # Reduced from 20
        main_layout.setContentsMargins(20, 15, 20, 15)  # Reduced vertical margins

        # --- Header section ---
        header_layout = QHBoxLayout()

        # Icon
        self.print_icon = PrintIcon()
        header_layout.addWidget(self.print_icon)

        # Title and subtitle
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)  # Reduced spacing between title and subtitle

        self.title_label = QLabel(self.translator.t('print_settings'))
        title_font = self.title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)

        self.subtitle_label = QLabel(self.translator.t('print_setup_description')
                                     if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                                     else "Configure how you want to print your products.")
        subtitle_font = self.subtitle_label.font()
        subtitle_font.setPointSize(11)
        self.subtitle_label.setFont(subtitle_font)
        text_color = get_color('text')
        subtitle_palette = self.subtitle_label.palette()
        subtitle_palette.setColor(QPalette.WindowText, QColor(text_color).lighter(130))
        self.subtitle_label.setPalette(subtitle_palette)

        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch(1)

        main_layout.addLayout(header_layout)

        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet(f"background-color: {get_color('border')};")
        separator.setMaximumHeight(1)
        main_layout.addWidget(separator)

        # --- Content section ---
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)  # Reduced spacing

        # Left column - settings
        settings_layout = QVBoxLayout()
        settings_layout.setSpacing(10)  # Reduced spacing

        # Print scope options with more compact layout
        scope_group = StyledGroupBox(self.translator.t('print_scope'))
        scope_layout = QVBoxLayout(scope_group)
        scope_layout.setSpacing(6)  # Reduced spacing between radio buttons
        scope_layout.setContentsMargins(10, 10, 10, 10)  # Reduced margins

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
        options_layout.setVerticalSpacing(10)  # Reduced spacing
        options_layout.setHorizontalSpacing(15)
        options_layout.setContentsMargins(10, 10, 10, 10)  # Reduced margins

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

        # RTL mode option
        self.rtl_mode_check = StyledCheckBox(self.translator.t('rtl_mode')
                                             if hasattr(self.translator, 't') and callable(
            getattr(self.translator, 't'))
                                             else "RTL Mode (Right-to-Left)")
        self.rtl_mode_check.setToolTip(self.translator.t('rtl_mode_tooltip')
                                       if hasattr(self.translator, 't') and callable(getattr(self.translator, 't'))
                                       else "Enable right-to-left layout for Hebrew or Arabic text")
        self.rtl_mode_check.setChecked(self._is_hebrew_default())

        options_layout.addWidget(self.rtl_mode_check, 4, 0, 1, 2)

        settings_layout.addWidget(options_group)
        settings_layout.addStretch(1)

        content_layout.addLayout(settings_layout)

        # Right column - preview illustration (simplified)
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
        preview_frame.setMinimumWidth(160)  # Slightly smaller

        # Add document preview illustration
        preview_frame_layout = QVBoxLayout(preview_frame)
        preview_frame_layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins

        # Paper icon (simplified)
        self.doc_preview = QLabel()
        self.doc_preview.setAlignment(Qt.AlignCenter)
        self.doc_preview.setMinimumHeight(180)  # Reduced height

        # Draw a simple document preview
        self._update_preview_illustration()

        preview_frame_layout.addWidget(self.doc_preview)
        preview_layout.addWidget(preview_frame)
        preview_layout.addStretch(1)

        content_layout.addLayout(preview_layout)
        content_layout.setStretch(0, 7)  # Settings get more space
        content_layout.setStretch(1, 3)  # Preview gets less space

        main_layout.addLayout(content_layout)

        # Separator line
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet(f"background-color: {get_color('border')};")
        separator2.setMaximumHeight(1)
        main_layout.addWidget(separator2)

        # --- Footer with buttons ---
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.preview_button = StyledButton(self.translator.t('preview_and_print'), True)
        self.cancel_button = StyledButton(self.translator.t('cancel'), False)

        self.preview_button.setDefault(True)

        button_layout.addWidget(self.preview_button)
        button_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        # Connect signals
        self.preview_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        # Connect preview update signals
        self.orientation_combo.currentIndexChanged.connect(self._update_preview_illustration)
        self.paper_size_combo.currentIndexChanged.connect(self._update_preview_illustration)
        self.print_header_check.toggled.connect(self._update_preview_illustration)
        self.print_date_check.toggled.connect(self._update_preview_illustration)
        self.rtl_mode_check.toggled.connect(self._update_preview_illustration)

        # Center the dialog
        self.centerOnScreen()

        # Apply theme
        self.apply_theme()

    def centerOnScreen(self):
        """Center the dialog on the screen"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def _is_hebrew_default(self):
        """Determine if Hebrew should be the default based on translator language"""
        try:
            if hasattr(self.translator, 'language'):
                return self.translator.language == 'he' or self.translator.language.startswith('he_')
            return False
        except:
            return False

    def _update_preview_illustration(self):
        """Update the preview illustration based on current settings"""
        # Create a pixmap to draw on
        pixmap = QPixmap(150, 180)  # Reduced height
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

            # Header if enabled
            if self.print_header_check.isChecked():
                header_y = content_y + 10
                painter.setBrush(QColor(220, 220, 220))
                painter.drawRect(content_x, header_y, content_width, 10)  # Slightly smaller
                content_y += 22

            # Date if enabled
            if self.print_date_check.isChecked():
                date_y = content_y
                date_width = 50
                painter.drawLine(
                    content_x + (content_width - date_width if rtl_mode else 0),
                    date_y,
                    content_x + (content_width if rtl_mode else date_width),
                    date_y
                )
                content_y += 12

            # Table header
            painter.setPen(QColor(180, 180, 180))
            painter.setBrush(QColor(230, 230, 230))
            painter.drawRect(content_x, content_y, content_width, 12)

            # Table grid - simulate right-to-left if RTL mode is enabled
            row_height = 10
            row_spacing = 12
            rows = 3  # Reduced rows

            # Draw table grid lines
            painter.setPen(QColor(210, 210, 210))
            for i in range(rows):
                y = content_y + 12 + (i * row_spacing)
                painter.drawLine(content_x, y, content_x + content_width, y)

                # Draw row content (different direction based on RTL)
                if rtl_mode:
                    # RTL table rows
                    painter.drawLine(content_x + 10, y + 5, content_x + 50, y + 5)  # Right aligned
                else:
                    # LTR table rows
                    painter.drawLine(content_x + content_width - 50, y + 5, content_x + content_width - 10,
                                     y + 5)  # Left aligned

            # Vertical grid lines - adjust for RTL mode
            if rtl_mode:
                # RTL column layout
                cols = [0.2, 0.4, 0.65, 0.85]
            else:
                # LTR column layout
                cols = [0.15, 0.35, 0.6, 0.8]

            for col_pct in cols:
                x = content_x + (content_width * col_pct)
                painter.drawLine(x, content_y, x, content_y + 12 + (rows * row_spacing))
        else:
            # Portrait layout
            content_x = pixmap.width() / 2 - paper_width / 2 + 10
            content_y = 20
            content_width = paper_width - 20

            # Header if enabled
            if self.print_header_check.isChecked():
                header_y = content_y + 8
                painter.setBrush(QColor(220, 220, 220))
                painter.drawRect(content_x, header_y, content_width, 10)  # Slightly smaller
                content_y += 20

            # Date if enabled
            if self.print_date_check.isChecked():
                date_y = content_y
                date_width = 40
                painter.drawLine(
                    content_x + (content_width - date_width if rtl_mode else 0),
                    date_y,
                    content_x + (content_width if rtl_mode else date_width),
                    date_y
                )
                content_y += 12

            # Table header
            painter.setPen(QColor(180, 180, 180))
            painter.setBrush(QColor(230, 230, 230))
            painter.drawRect(content_x, content_y, content_width, 12)

            # Table grid - simulating right-to-left if RTL mode is enabled
            row_height = 8
            row_spacing = 10
            rows = 6  # Reduced rows

            # Draw table grid lines
            painter.setPen(QColor(210, 210, 210))
            for i in range(rows):
                y = content_y + 12 + (i * row_spacing)
                painter.drawLine(content_x, y, content_x + content_width, y)

                # Draw row content (different direction based on RTL)
                if rtl_mode:
                    # RTL table rows
                    painter.drawLine(content_x + 8, y + 4, content_x + 40, y + 4)  # Right aligned
                else:
                    # LTR table rows
                    painter.drawLine(content_x + content_width - 40, y + 4, content_x + content_width - 8,
                                     y + 4)  # Left aligned

            # Vertical grid lines - adjust for RTL mode
            if rtl_mode:
                # RTL column layout
                cols = [0.25, 0.5, 0.75]
            else:
                # LTR column layout
                cols = [0.25, 0.5, 0.75]

            for col_pct in cols:
                x = content_x + (content_width * col_pct)
                painter.drawLine(x, content_y, x, content_y + 12 + (rows * row_spacing))

        painter.end()

        # Set the pixmap to the label
        self.doc_preview.setPixmap(pixmap)

    def apply_theme(self):
        """Apply current theme to dialog with elegant styling"""
        bg_color = get_color('background')
        text_color = get_color('text')

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {bg_color};
                color: {text_color};
                border-radius: 10px;
                border: 1px solid {get_color('border')};
            }}

            QLabel {{
                color: {text_color};
            }}
        """)

        # Update the preview after theme change
        self._update_preview_illustration()

    def get_settings(self):
        """Get the selected print settings"""
        settings = {
            'scope': self.scope_group.checkedId(),
            'paper_size': self.paper_size_combo.currentText(),
            'orientation': self.orientation_combo.currentIndex(),  # 0=Portrait, 1=Landscape
            'print_header': self.print_header_check.isChecked(),
            'print_date': self.print_date_check.isChecked(),
            'rtl_mode': self.rtl_mode_check.isChecked()  # Setting for RTL mode
        }
        return settings

    def showEvent(self, event):
        """Center the dialog when it's shown"""
        super().showEvent(event)
        # Center the dialog on the screen immediately when shown
        self.centerOnScreen()