from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QGroupBox, QFormLayout, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QCheckBox, QPushButton
)

from .settings_helpers import fix_form_layout_labels


class SettingsGroupCreator:
    """Factory class for creating setting group widgets"""

    def __init__(self, translator, parent=None):
        self.translator = translator
        self.parent = parent

        # Theme mappings - will be accessed by the main widget
        self.theme_names = ["classic", "dark", "light"]
        self.theme_display_names = ["Classic", "Dark", "Light"]

    def create_language_group(self, language_combo):
        """Create language settings group"""
        group = QGroupBox(self.translator.t('language_settings'), self.parent)
        layout = QFormLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        interface_lang_label = QLabel(self.translator.t('interface_language'))
        layout.addRow(interface_lang_label, language_combo)
        fix_form_layout_labels(layout)
        group.setLayout(layout)

        # Store references to widgets that need translation updates
        group.interface_lang_label = interface_lang_label

        return group

    def create_appearance_group(self, theme_combo):
        """Create appearance settings group"""
        group = QGroupBox(self.translator.t('appearance'), self.parent)
        layout = QFormLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        color_theme_label = QLabel(self.translator.t('color_theme'))
        layout.addRow(color_theme_label, theme_combo)
        fix_form_layout_labels(layout)
        group.setLayout(layout)

        # Store references
        group.color_theme_label = color_theme_label

        return group

    def create_technical_group(self, db_backup_interval, units_combo, invoice_template_btn):
        """Create technical settings group"""
        group = QGroupBox(self.translator.t('technical_settings'), self.parent)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        # Auto-backup sub-group
        db_group = QGroupBox(self.translator.t('auto_backup'))
        db_layout = QFormLayout()
        db_layout.setContentsMargins(8, 8, 8, 8)
        db_layout.setSpacing(10)
        db_backup_label = QLabel(self.translator.t('auto_backup'))
        db_layout.addRow(db_backup_label, db_backup_interval)
        fix_form_layout_labels(db_layout)
        db_group.setLayout(db_layout)

        # Measurement units sub-group
        units_group = QGroupBox(self.translator.t('measurement_units'))
        units_layout = QFormLayout()
        units_layout.setContentsMargins(8, 8, 8, 8)
        units_layout.setSpacing(10)
        units_label = QLabel(self.translator.t('measurement_units'))
        units_layout.addRow(units_label, units_combo)
        fix_form_layout_labels(units_layout)
        units_group.setLayout(units_layout)

        # Invoice template button in its own layout for proper alignment
        invoice_layout = QHBoxLayout()
        invoice_layout.setContentsMargins(8, 8, 8, 8)
        invoice_layout.setSpacing(10)
        invoice_layout.addWidget(invoice_template_btn)
        invoice_layout.addStretch()

        main_layout.addWidget(db_group)
        main_layout.addWidget(units_group)
        main_layout.addLayout(invoice_layout)
        main_layout.addStretch()
        group.setLayout(main_layout)

        # Store references
        group.db_group = db_group
        group.units_group = units_group
        group.db_backup_label = db_backup_label
        group.units_label = units_label

        return group

    def create_inventory_group(self, low_stock_input, default_currency_combo, auto_restock_checkbox):
        """Create inventory settings group"""
        group = QGroupBox(self.translator.t('inventory_settings'), self.parent)
        layout = QFormLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.setFormAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Low stock threshold row
        low_stock_threshold_label = QLabel(self.translator.t('low_stock_threshold'))
        layout.addRow(low_stock_threshold_label, low_stock_input)

        # Default currency row
        default_currency_label = QLabel(self.translator.t('default_currency'))
        layout.addRow(default_currency_label, default_currency_combo)

        # Auto-restock row
        auto_restock_label = QLabel(self.translator.t('enable_auto_restock'))
        layout.addRow(auto_restock_label, auto_restock_checkbox)

        fix_form_layout_labels(layout)
        group.setLayout(layout)

        # Store references
        group.low_stock_threshold_label = low_stock_threshold_label
        group.default_currency_label = default_currency_label
        group.auto_restock_label = auto_restock_label

        return group