from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame,
    QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton, QScrollArea,
    QSizePolicy, QMessageBox, QApplication
)

from themes import set_theme
from .settings_groups import SettingsGroupCreator
from .settings_styling import SettingsStyling


class SettingsWidget(QWidget):
    def __init__(self, translator, on_save, gui, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.gui = gui
        self.on_save_callback = on_save

        # Create the group creator
        self.group_creator = SettingsGroupCreator(translator, self)
        self.theme_names = self.group_creator.theme_names
        self.theme_display_names = self.group_creator.theme_display_names

        self.setup_ui()
        self.load_initial_settings()
        self.apply_theme()
        self.initial_settings = self.get_current_settings()

    def setup_ui(self):
        # Main layout with uniform margins
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # Main container frame for settings
        self.container_frame = QFrame(self)
        self.container_frame.setObjectName("settingsContainer")
        self.container_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container_frame.setMinimumWidth(750)

        container_layout = QVBoxLayout(self.container_frame)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Header section
        self.header = QFrame()
        self.header.setObjectName("settingsHeader")
        self.header.setFixedHeight(60)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        self.settings_title = QLabel(self.translator.t('settings_page'))
        self.settings_title.setObjectName("settingsTitle")
        header_layout.addWidget(self.settings_title)
        container_layout.addWidget(self.header)

        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setObjectName("headerDivider")
        container_layout.addWidget(divider)

        # Scrollable content area
        content_container = QWidget()
        content_container.setObjectName("contentContainer")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("settingsScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content = QWidget()
        content.setObjectName("scrollContent")
        scroll_layout = QVBoxLayout(content)
        scroll_layout.setContentsMargins(10, 10, 25, 10)  # Extra right margin for scrollbar
        scroll_layout.setSpacing(20)

        # Create UI controls
        self.create_controls()

        # Create groups using the SettingsGroupCreator
        self.language_group = self.group_creator.create_language_group(self.language_combo)
        self.appearance_group = self.group_creator.create_appearance_group(self.theme_combo)
        self.technical_group = self.group_creator.create_technical_group(
            self.db_backup_interval,
            self.units_combo,
            self.invoice_template_btn
        )
        self.inventory_group = self.group_creator.create_inventory_group(
            self.low_stock_threshold_input,
            self.default_currency_combo,
            self.auto_restock_checkbox
        )

        scroll_layout.addWidget(self.language_group)
        scroll_layout.addWidget(self.appearance_group)
        scroll_layout.addWidget(self.technical_group)
        scroll_layout.addWidget(self.inventory_group)
        scroll_layout.addStretch()

        content.setLayout(scroll_layout)
        self.scroll_area.setWidget(content)
        content_layout.addWidget(self.scroll_area)
        container_layout.addWidget(content_container, 1)

        # Button panel at bottom
        button_panel = QWidget()
        button_panel.setObjectName("buttonPanel")
        button_panel.setFixedHeight(70)
        btn_layout = QHBoxLayout(button_panel)
        btn_layout.setContentsMargins(20, 10, 20, 10)
        btn_layout.setSpacing(20)

        self.save_btn = QPushButton(self.translator.t('save'))
        self.cancel_btn = QPushButton(self.translator.t('cancel'))
        self.save_btn.setFixedSize(150, 45)
        self.cancel_btn.setFixedSize(150, 45)
        self.save_btn.setObjectName("saveButton")
        self.cancel_btn.setObjectName("cancelButton")

        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.cancel_changes)

        btn_layout.addStretch()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.save_btn)
        container_layout.addWidget(button_panel)

        main_layout.addWidget(self.container_frame)

    def create_controls(self):
        """Create all the control widgets used in groups"""
        # Language controls
        self.language_combo = QComboBox()
        self.language_combo.addItem(self.translator.t('english'), "en")
        self.language_combo.addItem(self.translator.t('hebrew'), "he")

        # Theme controls
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(self.theme_display_names)

        # Technical controls
        self.db_backup_interval = QComboBox()
        self.db_backup_interval.addItems([
            self.translator.t('daily'),
            self.translator.t('weekly'),
            self.translator.t('monthly')
        ])

        self.units_combo = QComboBox()
        self.units_combo.addItems([
            self.translator.t('metric_system'),
            self.translator.t('imperial_system')
        ])

        self.invoice_template_btn = QPushButton(self.translator.t('select_invoice_template'))
        self.invoice_template_btn.setFixedHeight(40)
        self.invoice_template_btn.clicked.connect(lambda: print("Invoice template selection dialog (placeholder)"))

        # Inventory controls
        self.low_stock_threshold_input = QLineEdit()
        self.low_stock_threshold_input.setValidator(QIntValidator(0, 10000, self))

        self.default_currency_combo = QComboBox()
        currencies = [
            self.translator.t('usd'),
            self.translator.t('eur'),
            self.translator.t('gbp'),
            self.translator.t('ils')
        ]
        self.default_currency_combo.addItems(currencies)
        self.default_currency_combo.setMinimumWidth(200)

        self.auto_restock_checkbox = QCheckBox()
        self.auto_restock_checkbox.setChecked(True)

    def get_current_settings(self):
        return {
            'theme': self.theme_names[self.theme_combo.currentIndex()],
            'language': self.language_combo.currentData(),
            'low_stock_threshold': self.low_stock_threshold_input.text().strip(),
            'default_currency': self.default_currency_combo.currentText().lower(),
            'auto_restock': self.auto_restock_checkbox.isChecked(),
            'backup_interval': self.db_backup_interval.currentIndex(),
            'measurement_units': self.units_combo.currentIndex()
        }

    def load_initial_settings(self):
        saved_theme = self.gui.settings_db.get_setting('theme', 'classic')
        try:
            theme_index = self.theme_names.index(saved_theme)
        except ValueError:
            theme_index = 0
        self.theme_combo.setCurrentIndex(theme_index)

        low_stock = self.gui.settings_db.get_setting('low_stock_threshold', '10')
        self.low_stock_threshold_input.setText(low_stock)
        is_rtl = self.gui.settings_db.get_setting('rtl', 'false') == 'true'
        self.language_combo.setCurrentIndex(1 if is_rtl else 0)
        self.initial_settings = self.get_current_settings()

    def save_settings(self):
        """Save settings with validation and error handling."""
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            low_stock = self.low_stock_threshold_input.text().strip()
            if not low_stock.isdigit() or int(low_stock) < 0:
                low_stock = "10"
                self.low_stock_threshold_input.setText(low_stock)

            settings = {
                'theme': self.theme_names[self.theme_combo.currentIndex()],
                'language': self.language_combo.currentData(),
                'low_stock_threshold': low_stock,
                'default_currency': self.default_currency_combo.currentText().lower(),
                'auto_restock': str(self.auto_restock_checkbox.isChecked()),
                'backup_interval': str(self.db_backup_interval.currentIndex()),
                'measurement_units': str(self.units_combo.currentIndex())
            }

            for key, value in settings.items():
                self.gui.settings_db.save_setting(key, value)

            self.initial_settings = self.get_current_settings()

            try:
                if settings['language'] != self.translator.language:
                    self.on_save_callback(settings['language'])
            except Exception as lang_error:
                print(f"Error applying language change: {lang_error}")

            try:
                set_theme(settings['theme'])
                if hasattr(self.gui, 'apply_theme_to_all') and callable(self.gui.apply_theme_to_all):
                    self.gui.apply_theme_to_all()
                else:
                    self.apply_theme()
            except Exception as theme_error:
                print(f"Error applying theme change: {theme_error}")

            QMessageBox.information(
                self,
                self.translator.t('success'),
                self.translator.t('settings_saved'),
                buttons=QMessageBox.Ok
            )
        except Exception as e:
            print(f"Settings save error: {e}")
            QMessageBox.critical(
                self,
                self.translator.t('error'),
                f"{self.translator.t('settings_save_error')}\n{e}",
                buttons=QMessageBox.Ok
            )
        finally:
            QApplication.restoreOverrideCursor()

    def cancel_changes(self):
        """Revert settings and navigate back."""
        try:
            if hasattr(self.gui, 'content') and hasattr(self.gui.content, 'stack'):
                self.gui.content.stack.setCurrentIndex(0)
            elif hasattr(self.gui, 'content_stack'):
                self.gui.content_stack.setCurrentWidget(self.gui.home_page)
            self.load_initial_settings()
        except Exception as e:
            print(f"Cancel settings error: {e}")
            self.load_initial_settings()

    def apply_theme(self):
        """Apply theme styling."""
        SettingsStyling.apply_theme(self, self.theme_names, self.theme_combo)

    def _apply_layout_direction(self):
        """Apply correct layout direction based on language."""
        new_direction = Qt.RightToLeft if self.translator.language == 'he' else Qt.LeftToRight
        self.setLayoutDirection(new_direction)
        self.header.setLayoutDirection(new_direction)

        # Remove the old title widget from header layout
        header_layout = self.header.layout()
        while header_layout.count():
            item = header_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Create a new title widget with the updated text and alignment
        self.settings_title = QLabel(self.translator.t('settings_page'))
        self.settings_title.setObjectName("settingsTitle")
        if new_direction == Qt.RightToLeft:
            self.settings_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.settings_title.setContentsMargins(0, 0, 10, 0)
        else:
            self.settings_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.settings_title.setContentsMargins(10, 0, 0, 0)

        # Re-add the title widget with a stretch to position it correctly
        if new_direction == Qt.RightToLeft:
            header_layout.addStretch()
            header_layout.addWidget(self.settings_title)
        else:
            header_layout.addWidget(self.settings_title)
            header_layout.addStretch()

        header_layout.update()
        self.header.update()

    def update_header_title_direction(self):
        """Update header title with correct text direction."""
        # Get the container layout that holds the header
        container_layout = self.container_frame.layout()

        # Remove the existing header widget from the container layout and delete it.
        container_layout.removeWidget(self.header)
        self.header.deleteLater()

        # Create a new header frame and layout.
        self.header = QFrame()
        self.header.setObjectName("settingsHeader")
        self.header.setFixedHeight(60)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        # Determine new direction.
        new_direction = Qt.RightToLeft if self.translator.language == 'he' else Qt.LeftToRight
        self.header.setLayoutDirection(new_direction)

        # Create a new title widget with updated text.
        self.settings_title = QLabel(self.translator.t('settings_page'))
        self.settings_title.setObjectName("settingsTitle")

        # Set alignment and margins based on new direction.
        if new_direction == Qt.RightToLeft:
            self.settings_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.settings_title.setContentsMargins(0, 0, 10, 0)
            header_layout.addStretch()  # Stretch before title pushes it to the right.
            header_layout.addWidget(self.settings_title)
        else:
            self.settings_title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.settings_title.setContentsMargins(10, 0, 0, 0)
            header_layout.addWidget(self.settings_title)
            header_layout.addStretch()  # Stretch after title keeps it left.

        # Re-insert the header into the container layout at the top.
        container_layout.insertWidget(0, self.header)

        # Force a refresh.
        self.header.updateGeometry()
        self.header.update()

    def refresh_scrollbar(self):
        """Refresh the scrollbar appearance."""
        SettingsStyling.refresh_scrollbar(self.scroll_area, self.theme_names, self.theme_combo)

    def add_entrance_animation(self):
        """Add entrance animation to the widget."""
        SettingsStyling.add_entrance_animation(self)

    def update_translations(self):
        """Update all translations in the UI."""
        # Update group titles
        self.language_group.setTitle(self.translator.t('language_settings'))
        self.appearance_group.setTitle(self.translator.t('appearance'))
        self.technical_group.setTitle(self.translator.t('technical_settings'))
        self.inventory_group.setTitle(self.translator.t('inventory_settings'))

        # Update language group
        self.language_group.interface_lang_label.setText(self.translator.t('interface_language'))
        self.language_combo.setItemText(0, self.translator.t('english'))
        self.language_combo.setItemText(1, self.translator.t('hebrew'))

        # Update appearance group
        self.appearance_group.color_theme_label.setText(self.translator.t('color_theme'))

        # Update technical group
        self.technical_group.db_group.setTitle(self.translator.t('auto_backup'))
        self.technical_group.units_group.setTitle(self.translator.t('measurement_units'))
        self.technical_group.db_backup_label.setText(self.translator.t('auto_backup'))
        self.technical_group.units_label.setText(self.translator.t('measurement_units'))
        self.db_backup_interval.setItemText(0, self.translator.t('daily'))
        self.db_backup_interval.setItemText(1, self.translator.t('weekly'))
        self.db_backup_interval.setItemText(2, self.translator.t('monthly'))
        self.units_combo.setItemText(0, self.translator.t('metric_system'))
        self.units_combo.setItemText(1, self.translator.t('imperial_system'))
        self.invoice_template_btn.setText(self.translator.t('select_invoice_template'))

        # Update inventory group
        self.inventory_group.low_stock_threshold_label.setText(self.translator.t('low_stock_threshold'))
        self.inventory_group.default_currency_label.setText(self.translator.t('default_currency'))
        self.inventory_group.auto_restock_label.setText(self.translator.t('enable_auto_restock'))

        # Update buttons
        self.save_btn.setText(self.translator.t('save'))
        self.cancel_btn.setText(self.translator.t('cancel'))

        # Update layout direction
        new_direction = Qt.RightToLeft if self.translator.language == 'he' else Qt.LeftToRight
        self.setLayoutDirection(new_direction)
        for child in self.findChildren(QWidget):
            child.setLayoutDirection(new_direction)

        self.updateGeometry()
        self._apply_layout_direction()
        self.apply_theme()  # Reapply theme

        # Finally, re-create the header so its title picks up the new direction
        self.update_header_title_direction()