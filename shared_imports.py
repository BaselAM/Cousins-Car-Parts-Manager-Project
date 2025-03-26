"""
Centralized imports for the application.
This module provides common imports used throughout the application.
"""
from pathlib import Path
import time
from datetime import datetime

# --- Path Definitions ---
SCRIPT_DIR = Path(__file__).resolve().parent

# --- Database Imports ---
from database.car_parts_db import CarPartsDB
from database.settings_db import SettingsDB

# --- Translator ---
from translations import EnhancedTranslator

# --- Qt Core Imports ---
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSlot,
    QMetaObject, Q_ARG, QThread, pyqtSignal, QStringListModel,
    QSize, QRect
)

# --- Qt GUI Imports ---
from PyQt5.QtGui import (
    QPixmap, QPainter, QIcon, QColor, QIntValidator,
    QDoubleValidator, QPalette, QFont
)

# --- Qt Widget Imports ---
from PyQt5.QtWidgets import (
    QApplication, QWidget, QDesktopWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QStackedLayout, QGraphicsOpacityEffect, QTableWidget, QHeaderView, QTableWidgetItem,
    QLineEdit, QPushButton, QScrollArea, QFormLayout, QComboBox, QColorDialog,
    QGroupBox, QAction, QGridLayout, QListWidget, QStyledItemDelegate,
    QMessageBox, QDialog, QDialogButtonBox, QCompleter, QAbstractItemView,
    QCheckBox, QSizePolicy, QFrame, QSpinBox, QDoubleSpinBox, QTextEdit, QBoxLayout
)

# Fix for IDE warnings about connect() method
pyqtSignal.__class_getitem__ = lambda cls, args: cls