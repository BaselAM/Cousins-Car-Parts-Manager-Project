# widgets/statistics.py
"""
Enhanced Statistics Dashboard for Abu Mukh Car Parts Management System.

This module provides a modern, data-driven dashboard with advanced analytics,
interactive visualizations, and actionable insights for inventory management.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTabWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QGridLayout, QFrame, QGroupBox, QScrollArea, QGraphicsDropShadowEffect,
    QCheckBox, QMessageBox, QToolButton, QSpacerItem, QSplitter, QFileDialog,
    QLineEdit, QDateEdit, QApplication, QProgressBar
)
from PyQt5.QtCore import (
    Qt, pyqtSignal, QTimer, QSize, QRect, QPropertyAnimation,
    QEasingCurve, QDate, QDateTime, QThread, pyqtSlot, QObject, QEvent,
    QPoint, QPointF
)
from PyQt5.QtGui import (
    QPainter, QColor, QBrush, QPen, QFont, QPixmap, QLinearGradient,
    QRadialGradient, QPainterPath, QFontMetrics, QPalette, QCursor, QConicalGradient
)

import threading
import time
from datetime import datetime, timedelta
import math
import csv
import os
import json
from typing import Dict, List, Tuple, Optional, Union, Any

# Try to import QtCharts, fall back to custom implementation if not available
try:
    from PyQt5.QtChart import (
        QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QValueAxis,
        QBarCategoryAxis, QLineSeries, QSplineSeries, QPieSlice,
        QPercentBarSeries
    )

    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False

# Import from your existing systems
from logger import get_logger
from themes import get_color, get_size, get_font_size

# Initialize logger
logger = get_logger(__name__)


class FloatingToolTip(QLabel):
    """Custom tooltip with enhanced styling for data points"""

    class FloatingToolTip(QLabel):
        """Custom tooltip with enhanced styling for data points"""

        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowFlags(Qt.ToolTip)
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setStyleSheet(f"""
                QLabel {{
                    background-color: {get_color('card_bg')};
                    color: {get_color('text')};
                    border: 1px solid {get_color('border')};
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 11px;
                }}
            """)
            self.hide()

        def show_at(self, pos, text):
            """Show tooltip at the specified position with improved boundary checking"""
            self.setText(text)
            self.adjustSize()

            # Get parent widget and screen dimensions
            parent = self.parent()
            if not parent:
                return

            parent_rect = parent.rect()

            # Position near cursor but ensure it's fully visible
            x = pos.x() + 15
            y = pos.y() - self.height() - 10

            # Adjust if it would go off right edge
            if x + self.width() > parent_rect.width():
                x = pos.x() - self.width() - 5

            # Adjust if it would go off top edge
            if y < 0:
                y = pos.y() + 15

            # Ensure it's not off left or bottom edges
            if x < 0:
                x = 0
            if y + self.height() > parent_rect.height():
                y = parent_rect.height() - self.height()

            self.move(parent.mapToGlobal(QPoint(x, y)))
            self.show()

            # Ensure tooltip is on top of all other widgets
            self.raise_()

        def hide_tooltip(self):
            """Hide the tooltip"""
            self.hide()

    def show_at(self, pos, text):
        """Show tooltip at the specified position with text"""
        self.setText(text)
        self.adjustSize()

        # Position near cursor but ensure it's fully visible
        x = pos.x() + 15
        y = pos.y() - self.height() - 10

        # Adjust if it would go off screen
        if x + self.width() > self.parent().width():
            x = pos.x() - self.width() - 5
        if y < 0:
            y = pos.y() + 15

        self.move(self.parent().mapToGlobal(QPoint(x, y)))
        self.show()

    def hide_tooltip(self):
        """Hide the tooltip"""
        self.hide()


class LoadingOverlay(QWidget):
    """Loading overlay with animated spinner"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setVisible(False)

        self.spinner_angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate_spinner)

        # Ensure overlay is on top
        if parent:
            self.setGeometry(parent.rect())

        # Initial raise to ensure proper z-order
        self.raise_()

    def showEvent(self, event):
        """Start animation when shown"""
        if not self.timer.isActive():
            self.timer.start(30)  # Update every 30ms
        self.raise_()  # Ensure on top when shown
        super().showEvent(event)

    def hideEvent(self, event):
        """Stop animation when hidden"""
        if self.timer.isActive():
            self.timer.stop()
        super().hideEvent(event)

    def rotate_spinner(self):
        """Update spinner rotation"""
        self.spinner_angle = (self.spinner_angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        """Paint the spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Semi-transparent background
        bg_color = QColor(get_color('background'))
        bg_color.setAlpha(200)
        painter.fillRect(self.rect(), bg_color)

        # Draw spinner
        center = self.rect().center()
        spinner_size = min(self.width(), self.height()) / 5

        painter.translate(center)
        painter.rotate(self.spinner_angle)

        gradient = QConicalGradient(0, 0, 270)
        gradient.setColorAt(0, QColor(get_color('highlight')))
        gradient.setColorAt(0.5, QColor(get_color('highlight')).lighter(150))
        gradient.setColorAt(1, QColor(get_color('highlight')))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(gradient))

        # Draw spinner arc
        path = QPainterPath()
        path.moveTo(0, 0)
        path.arcTo(-spinner_size / 2, -spinner_size / 2, spinner_size, spinner_size, 0, 280)
        path.closeSubpath()

        painter.drawPath(path)

        # Draw text
        painter.resetTransform()
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        painter.setPen(QColor(get_color('text')))
        text_rect = QRect(0, int(center.y() + spinner_size), self.width(), 30)
        painter.drawText(text_rect, Qt.AlignCenter, "Loading data...")

    def resizeEvent(self, event):
        """Ensure overlay covers the entire parent widget"""
        if self.parentWidget():
            self.setGeometry(self.parentWidget().rect())


class AnimatedStat(QFrame):
    """
    Modern, animated statistic card with data comparison capabilities.
    """

    def __init__(self, title, value="0", icon=None, suffix="", parent=None, trend=0, is_currency=False):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.icon_text = icon
        self.suffix = suffix
        self.trend = trend  # Percentage change: positive = up, negative = down
        self.is_currency = is_currency
        self.currency_symbol = "₪"  # Will be updated from settings

        self.setMinimumSize(180, 120)
        self.setMaximumHeight(160)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("statCard")

        # Add shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(3)
        self.shadow.setYOffset(3)
        self.shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(self.shadow)

        # Set up layout
        self.setup_ui()

        # Set up animation properties
        self.animation_value = 0
        self.animation = QPropertyAnimation(self, b"animation_value")
        self.animation.setDuration(1000)
        self.animation.setEasingCurve(QEasingCurve.OutQuart)

        # Apply theme
        self.apply_theme()

    def setup_ui(self):
        """Set up the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Title and icon row
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)

        if self.icon_text:
            self.icon_label = QLabel(self.icon_text)
            self.icon_label.setFixedSize(20, 20)
            title_layout.addWidget(self.icon_label)

        self.title_label = QLabel(self.title)
        title_font = self.title_label.font()
        title_font.setPointSize(get_font_size("medium"))
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        layout.addLayout(title_layout)

        # Value
        value_layout = QHBoxLayout()
        value_layout.setSpacing(0)

        # Format value based on type
        display_value = self.value
        if self.is_currency and not isinstance(self.value, str):
            display_value = f"{self.currency_symbol}{self.value:,.2f}"

        self.value_label = QLabel(str(display_value))
        value_font = self.value_label.font()
        value_font.setPointSize(get_font_size("xlarge"))
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        value_layout.addWidget(self.value_label)

        # Add suffix if provided
        if self.suffix:
            self.suffix_label = QLabel(self.suffix)
            suffix_font = self.suffix_label.font()
            suffix_font.setPointSize(get_font_size("medium"))
            self.suffix_label.setFont(suffix_font)
            value_layout.addWidget(self.suffix_label)

        value_layout.addStretch()
        layout.addLayout(value_layout)

        # Trend indicator
        if self.trend != 0:
            self.trend_layout = QHBoxLayout()

            trend_text = f"{abs(self.trend):.1f}% " + ("increase" if self.trend > 0 else "decrease")
            self.trend_label = QLabel(trend_text)

            trend_font = self.trend_label.font()
            trend_font.setPointSize(get_font_size("small"))
            self.trend_label.setFont(trend_font)

            # Set color based on trend direction and context
            if self.trend > 0:
                # For most metrics, up is good (green)
                self.trend_label.setStyleSheet(f"color: {get_color('success')};")
                self.trend_icon = QLabel("↑")
                self.trend_icon.setStyleSheet(f"color: {get_color('success')};")
            else:
                # For most metrics, down is bad (red)
                self.trend_label.setStyleSheet(f"color: {get_color('error')};")
                self.trend_icon = QLabel("↓")
                self.trend_icon.setStyleSheet(f"color: {get_color('error')};")

            self.trend_layout.addWidget(self.trend_icon)
            self.trend_layout.addWidget(self.trend_label)
            self.trend_layout.addStretch()

            layout.addLayout(self.trend_layout)

        # Extra space at bottom
        layout.addStretch()

    def animate_value_change(self, old_val, new_val, formatted_new_value):
        """Animate a change in value"""
        try:
            # Store formatted value for end of animation
            self.target_formatted_value = formatted_new_value

            # Set up animation
            self.animation.setStartValue(old_val)
            self.animation.setEndValue(new_val)

            # Connect signals
            self.animation.valueChanged.connect(self._update_animated_value)
            self.animation.finished.connect(self._animation_finished)

            # Start animation
            self.animation.start()

        except Exception as e:
            logger.error(f"Error animating stat: {e}")
            self.value_label.setText(formatted_new_value)

    def _update_animated_value(self, value):
        """Update the displayed value during animation"""
        if self.is_currency:
            self.value_label.setText(f"{self.currency_symbol}{value:,.2f}")
        elif isinstance(value, float):
            self.value_label.setText(f"{value:.1f}")
        else:
            self.value_label.setText(f"{int(value)}")

    def _animation_finished(self):
        """Set final formatted value when animation completes"""
        self.value_label.setText(self.target_formatted_value)

        # Disconnect to prevent memory leaks
        try:
            self.animation.valueChanged.disconnect(self._update_animated_value)
            self.animation.finished.disconnect(self._animation_finished)
        except Exception:
            pass

    def update_value(self, value, trend=None):
        """Update the card value with optional animation"""
        # Store previous value for animation
        old_text = self.value_label.text()
        old_value = 0

        try:
            # Extract numeric value from text
            if self.is_currency:
                old_value = float(old_text.replace(self.currency_symbol, '').replace(',', ''))
            else:
                old_value = float(old_text.replace(',', ''))
        except (ValueError, AttributeError):
            old_value = 0

        # Update value
        self.value = value

        # Update trend if provided
        if trend is not None:
            self.trend = trend
            # Update trend label if it exists
            if hasattr(self, 'trend_label'):
                trend_text = f"{abs(self.trend):.1f}% " + ("increase" if self.trend > 0 else "decrease")

                self.trend_label.setText(trend_text)

                # Update trend color
                if self.trend > 0:
                    self.trend_label.setStyleSheet(f"color: {get_color('success')};")
                    self.trend_icon.setStyleSheet(f"color: {get_color('success')};")
                else:
                    self.trend_label.setStyleSheet(f"color: {get_color('error')};")
                    self.trend_icon.setStyleSheet(f"color: {get_color('error')};")

        # Format final value for display
        if self.is_currency:
            formatted_value = f"{self.currency_symbol}{value:,.2f}"
        elif isinstance(value, float):
            formatted_value = f"{value:.1f}"
        else:
            formatted_value = str(value)

        # Animate the change
        try:
            self.animate_value_change(old_value, float(value), formatted_value)
        except (ValueError, TypeError):
            # If animation fails, just update the text
            self.value_label.setText(formatted_value)

    def apply_theme(self):
        """Apply current theme to the card"""
        # Get colors from theme
        bg_color = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        shadow_color = QColor(0, 0, 0, 60)

        # Create card gradient
        if QColor(bg_color).lightness() < 128:  # Dark theme
            gradient_start = QColor(bg_color).lighter(110)
            gradient_end = QColor(bg_color)
        else:  # Light theme
            gradient_start = QColor(bg_color)
            gradient_end = QColor(bg_color).darker(105)

        # Apply styles
        self.setStyleSheet(f"""
            #statCard {{
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {gradient_start.name()}, 
                    stop: 1 {gradient_end.name()}
                );
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}

            QLabel {{
                background: transparent;
                color: {text_color};
            }}
        """)

        # Update shadow
        self.shadow.setColor(shadow_color)


class ModernProgressBar(QProgressBar):
    """Enhanced progress bar with gradient and animations"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextVisible(False)
        self.setMinimumHeight(8)
        self.setMaximumHeight(8)

        # Apply modern styling
        self.apply_theme()

    def apply_theme(self):
        primary_color = get_color('highlight')
        background_color = get_color('card_bg')
        border_color = get_color('border')

        # Create lighter shade for gradient
        primary_lighter = QColor(primary_color).lighter(120).name()

        self.setStyleSheet(f"""
            QProgressBar {{
                background-color: {background_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                text-align: center;
            }}

            QProgressBar::chunk {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {primary_color}, 
                    stop:1 {primary_lighter}
                );
                border-radius: 4px;
            }}
        """)


class InsightCard(QFrame):
    """
    Card displaying an actionable insight with visualization
    """

    def __init__(self, title, value, context, max_value=100, parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.context = context
        self.max_value = max_value

        self.setMinimumSize(220, 130)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("insightCard")

        # Add shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(shadow)

        # Setup UI
        self.setup_ui()

        # Apply theme
        self.apply_theme()

    def setup_ui(self):
        """Set up the card UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Title
        self.title_label = QLabel(self.title)
        title_font = self.title_label.font()
        title_font.setPointSize(get_font_size("medium"))
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)

        # Value
        value_layout = QHBoxLayout()
        self.value_label = QLabel(str(self.value))
        value_font = self.value_label.font()
        value_font.setPointSize(get_font_size("xlarge"))
        value_font.setBold(True)
        self.value_label.setFont(value_font)
        value_layout.addWidget(self.value_label)
        value_layout.addStretch()
        layout.addLayout(value_layout)

        # Progress bar
        self.progress_bar = ModernProgressBar()
        self.progress_bar.setRange(0, int(self.max_value))
        self.progress_bar.setValue(int(self.value))
        layout.addWidget(self.progress_bar)

        # Context text
        self.context_label = QLabel(self.context)
        context_font = self.context_label.font()
        context_font.setPointSize(get_font_size("small"))
        self.context_label.setFont(context_font)
        self.context_label.setWordWrap(True)
        layout.addWidget(self.context_label)

        layout.addStretch()

    def update_data(self, value, context, max_value=None):
        """Update the card data"""
        self.value = value
        self.context = context

        if max_value is not None:
            self.max_value = max_value
            self.progress_bar.setRange(0, int(self.max_value))

        self.value_label.setText(str(self.value))
        self.context_label.setText(self.context)

        # Animate progress bar
        self.progress_bar.setValue(int(self.value))

    def apply_theme(self):
        """Apply current theme styling"""
        bg_color = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        highlight_color = get_color('highlight')

        # Create card gradient
        if QColor(bg_color).lightness() < 128:  # Dark theme
            gradient_start = QColor(bg_color).lighter(110)
            gradient_end = QColor(bg_color)
        else:  # Light theme
            gradient_start = QColor(bg_color)
            gradient_end = QColor(bg_color).darker(105)

        self.setStyleSheet(f"""
            #insightCard {{
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {gradient_start.name()}, 
                    stop: 1 {gradient_end.name()}
                );
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}

            QLabel {{
                background: transparent;
                color: {text_color};
            }}
        """)


class DataTable(QTableWidget):
    """Enhanced table widget with modern styling and features"""

    itemHovered = pyqtSignal(int, int, QTableWidgetItem)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up modern styling
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setShowGrid(False)
        self.verticalHeader().setVisible(False)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setHighlightSections(False)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.setSortingEnabled(True)

        # Track hovering
        self.setMouseTracking(True)
        self.hovered_row = -1
        self.hovered_col = -1

        # Apply theme
        self.apply_theme()

    def mouseMoveEvent(self, event):
        """Track mouse position for hover effects"""
        row = self.rowAt(event.y())
        col = self.columnAt(event.x())

        if row != self.hovered_row or col != self.hovered_col:
            self.hovered_row, self.hovered_col = row, col

            if row >= 0 and col >= 0:
                item = self.item(row, col)
                if item:
                    self.itemHovered.emit(row, col, item)

            self.viewport().update()

        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        """Reset hover state when mouse leaves"""
        self.hovered_row = -1
        self.hovered_col = -1
        self.viewport().update()
        super().leaveEvent(event)

    def set_column_widths(self, widths):
        """Set column widths proportionally"""
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)

        for col, width in enumerate(widths):
            if col < self.columnCount():
                header.setSectionResizeMode(col, QHeaderView.Interactive)
                header.resizeSection(col, width)

    def apply_theme(self):
        """Apply current theme styling"""
        bg_color = get_color('background')
        text_color = get_color('text')
        card_bg = get_color('card_bg')
        border_color = get_color('border')
        highlight_color = get_color('highlight')
        highlight_text = get_color('highlight_text')

        # Compute alternate row color
        if QColor(bg_color).lightness() < 128:  # Dark theme
            alternate_bg = QColor(card_bg).lighter(110).name()
        else:  # Light theme
            alternate_bg = QColor(card_bg).darker(105).name()

        self.setStyleSheet(f"""
            QTableWidget {{
                background-color: {card_bg};
                alternate-background-color: {alternate_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                gridline-color: transparent;
            }}

            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {border_color};
            }}

            QTableWidget::item:selected {{
                background-color: {highlight_color};
                color: {highlight_text};
            }}

            QHeaderView::section {{
                background-color: {card_bg};
                color: {text_color};
                padding: 10px;
                border: none;
                border-bottom: 2px solid {highlight_color};
                font-weight: bold;
                font-size: {get_font_size("medium")}px;
            }}

            QHeaderView::section:hover {{
                background-color: {QColor(card_bg).lighter(110).name()};
            }}

            QScrollBar:vertical {{
                border: none;
                background: {card_bg};
                width: 10px;
                margin: 10px 0 10px 0;
                border-radius: 5px;
            }}

            QScrollBar::handle:vertical {{
                background: {QColor(highlight_color).darker(110).name()};
                min-height: 20px;
                border-radius: 5px;
            }}

            QScrollBar::handle:vertical:hover {{
                background: {highlight_color};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0px;
            }}

            QScrollBar:horizontal {{
                border: none;
                background: {card_bg};
                height: 10px;
                margin: 0 10px 0 10px;
                border-radius: 5px;
            }}

            QScrollBar::handle:horizontal {{
                background: {QColor(highlight_color).darker(110).name()};
                min-width: 20px;
                border-radius: 5px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background: {highlight_color};
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                border: none;
                background: none;
                width: 0px;
            }}
        """)


class FilterPanel(QFrame):
    """
    Advanced filtering panel for statistics
    """

    filtersChanged = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("filterPanel")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Setup UI
        self.setup_ui()

        # Apply theme
        self.apply_theme()

    def setup_ui(self):
        """Set up the filter UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # Header with title and toggle button
        header_layout = QHBoxLayout()

        title_label = QLabel("Advanced Filters")
        title_font = title_label.font()
        title_font.setPointSize(get_font_size("medium"))
        title_font.setBold(True)
        title_label.setFont(title_font)

        self.toggle_button = QToolButton()
        self.toggle_button.setText("▼")
        self.toggle_button.setToolTip("Toggle filters")
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(True)
        self.toggle_button.clicked.connect(self.toggle_content)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.toggle_button)

        main_layout.addLayout(header_layout)

        # Content container
        self.content_widget = QWidget()
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 10, 0, 0)
        self.content_layout.setSpacing(12)

        # Date range
        self.content_layout.addWidget(QLabel("Date Range:"), 0, 0)

        date_layout = QHBoxLayout()

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setDisplayFormat("yyyy-MM-dd")

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("yyyy-MM-dd")

        date_layout.addWidget(self.date_from)
        date_layout.addWidget(QLabel("to"))
        date_layout.addWidget(self.date_to)

        self.content_layout.addLayout(date_layout, 0, 1)

        # Category filter
        self.content_layout.addWidget(QLabel("Categories:"), 1, 0)

        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories")
        self.content_layout.addWidget(self.category_filter, 1, 1)

        # Brand filter
        self.content_layout.addWidget(QLabel("Brands:"), 1, 2)

        self.brand_filter = QComboBox()
        self.brand_filter.addItem("All Brands")
        self.content_layout.addWidget(self.brand_filter, 1, 3)

        # Stock status
        self.content_layout.addWidget(QLabel("Stock Status:"), 2, 0)

        stock_layout = QHBoxLayout()

        self.in_stock_cb = QCheckBox("In Stock")
        self.in_stock_cb.setChecked(True)

        self.low_stock_cb = QCheckBox("Low Stock")
        self.low_stock_cb.setChecked(True)

        self.out_of_stock_cb = QCheckBox("Out of Stock")
        self.out_of_stock_cb.setChecked(True)

        stock_layout.addWidget(self.in_stock_cb)
        stock_layout.addWidget(self.low_stock_cb)
        stock_layout.addWidget(self.out_of_stock_cb)
        stock_layout.addStretch()

        self.content_layout.addLayout(stock_layout, 2, 1, 1, 3)

        # Price range
        self.content_layout.addWidget(QLabel("Price Range:"), 3, 0)

        price_layout = QHBoxLayout()

        self.price_min = QLineEdit()
        self.price_min.setPlaceholderText("Min")

        self.price_max = QLineEdit()
        self.price_max.setPlaceholderText("Max")

        price_layout.addWidget(self.price_min)
        price_layout.addWidget(QLabel("to"))
        price_layout.addWidget(self.price_max)

        self.content_layout.addLayout(price_layout, 3, 1)

        # Action buttons
        button_layout = QHBoxLayout()

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_filters)

        self.apply_button = QPushButton("Apply Filters")
        self.apply_button.clicked.connect(self.apply_filters)
        self.apply_button.setDefault(True)

        button_layout.addStretch()
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.apply_button)

        self.content_layout.addLayout(button_layout, 4, 0, 1, 4)

        main_layout.addWidget(self.content_widget)

        # Connect signals
        self.date_from.dateChanged.connect(self.validate_dates)
        self.date_to.dateChanged.connect(self.validate_dates)

    def toggle_content(self):
        """Toggle visibility of filter content"""
        if self.toggle_button.isChecked():
            self.content_widget.show()
            self.toggle_button.setText("▼")
        else:
            self.content_widget.hide()
            self.toggle_button.setText("▶")

    def validate_dates(self):
        """Ensure from date is before to date"""
        from_date = self.date_from.date()
        to_date = self.date_to.date()

        if from_date > to_date:
            self.date_from.setDate(to_date)

    def populate_categories(self, categories):
        """Populate category dropdown"""
        self.category_filter.clear()
        self.category_filter.addItem("All Categories")
        self.category_filter.addItems(categories)

    def populate_brands(self, brands):
        """Populate brands dropdown"""
        self.brand_filter.clear()
        self.brand_filter.addItem("All Brands")
        self.brand_filter.addItems(brands)

    def reset_filters(self):
        """Reset all filters to default values"""
        # Reset date range to last month
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_to.setDate(QDate.currentDate())

        # Reset dropdowns
        self.category_filter.setCurrentIndex(0)
        self.brand_filter.setCurrentIndex(0)

        # Reset checkboxes
        self.in_stock_cb.setChecked(True)
        self.low_stock_cb.setChecked(True)
        self.out_of_stock_cb.setChecked(True)

        # Reset price range
        self.price_min.clear()
        self.price_max.clear()

        # Apply changes
        self.apply_filters()

    def apply_filters(self):
        """Emit signal with current filter values"""
        filters = {
            'date_from': self.date_from.date().toString("yyyy-MM-dd"),
            'date_to': self.date_to.date().toString("yyyy-MM-dd"),
            'category': self.category_filter.currentText() if self.category_filter.currentIndex() > 0 else None,
            'brand': self.brand_filter.currentText() if self.brand_filter.currentIndex() > 0 else None,
            'stock_status': {
                'in_stock': self.in_stock_cb.isChecked(),
                'low_stock': self.low_stock_cb.isChecked(),
                'out_of_stock': self.out_of_stock_cb.isChecked()
            },
            'price_min': float(self.price_min.text()) if self.price_min.text() else None,
            'price_max': float(self.price_max.text()) if self.price_max.text() else None
        }

        self.filtersChanged.emit(filters)

    def apply_theme(self):
        """Apply current theme styling"""
        bg_color = get_color('card_bg')
        text_color = get_color('text')
        border_color = get_color('border')
        highlight_color = get_color('highlight')

        # Create gradient background
        if QColor(bg_color).lightness() < 128:  # Dark theme
            gradient_start = QColor(bg_color).lighter(110)
            gradient_end = QColor(bg_color)
        else:  # Light theme
            gradient_start = QColor(bg_color)
            gradient_end = QColor(bg_color).darker(105)

        self.setStyleSheet(f"""
            #filterPanel {{
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {gradient_start.name()}, 
                    stop: 1 {gradient_end.name()}
                );
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}

            QLabel {{
                color: {text_color};
                background: transparent;
            }}

            QComboBox, QDateEdit, QLineEdit {{
                background-color: {get_color('input_bg')};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 25px;
            }}

            QComboBox:hover, QDateEdit:hover, QLineEdit:hover {{
                border: 1px solid {highlight_color};
            }}

            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {border_color};
            }}

            QCheckBox {{
                color: {text_color};
                background: transparent;
                spacing: 5px;
            }}

            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 1px solid {border_color};
                border-radius: 3px;
            }}

            QCheckBox::indicator:checked {{
                background-color: {highlight_color};
                border: 1px solid {highlight_color};
            }}

            QPushButton {{
                background-color: {get_color('button')};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 6px 16px;
                font-weight: bold;
            }}

            QPushButton:hover {{
                background-color: {get_color('button_hover')};
                border: 1px solid {highlight_color};
            }}

            QPushButton:pressed {{
                background-color: {get_color('button_pressed')};
            }}
        """)


class TimeRangeSelector(QFrame):
    """
    Modern time range selection component with preset options.
    """

    rangeChanged = pyqtSignal(str, str, str)  # period_type, start_date, end_date

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("timeRangeSelector")
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # Define time range presets with method references
        self.time_ranges = {
            "Today": self._get_today_range,
            "Yesterday": self._get_yesterday_range,
            "This Week": self._get_this_week_range,
            "Last Week": self._get_last_week_range,
            "This Month": self._get_this_month_range,
            "Last Month": self._get_last_month_range,
            "This Quarter": self._get_this_quarter_range,
            "Last Quarter": self._get_last_quarter_range,
            "This Year": self._get_this_year_range,
            "Last Year": self._get_last_year_range,
            "All Time": self._get_all_time_range,
            "Custom": None  # Special case
        }

        # Setup UI
        self.setup_ui()

        # Set default range
        self.set_range("This Month")

        # Apply theme
        self.apply_theme()

    def setup_ui(self):
        """Set up the UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Label
        self.label = QLabel("Time Range:")
        layout.addWidget(self.label)

        # Dropdown for preset ranges
        self.range_combo = QComboBox()
        self.range_combo.addItems(list(self.time_ranges.keys()))
        self.range_combo.setCurrentText("This Month")
        self.range_combo.currentTextChanged.connect(self.on_range_selected)
        layout.addWidget(self.range_combo)

        # Custom date selection (initially hidden)
        self.custom_dates = QFrame()
        custom_layout = QHBoxLayout(self.custom_dates)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        custom_layout.setSpacing(8)

        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        self.date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from.dateChanged.connect(self.validate_dates)

        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to.dateChanged.connect(self.validate_dates)

        self.apply_btn = QPushButton("Apply")
        self.apply_btn.setAutoDefault(False)
        self.apply_btn.clicked.connect(self.apply_custom_range)

        custom_layout.addWidget(self.date_from)
        custom_layout.addWidget(QLabel("to"))
        custom_layout.addWidget(self.date_to)
        custom_layout.addWidget(self.apply_btn)

        layout.addWidget(self.custom_dates)
        self.custom_dates.hide()

        layout.addStretch()

    def on_range_selected(self, range_name):
        """Handle range selection"""
        if range_name == "Custom":
            self.custom_dates.show()
        else:
            self.custom_dates.hide()
            self.set_range(range_name)

    def set_range(self, range_name):
        """Set the time range to a preset"""
        if range_name in self.time_ranges and self.time_ranges[range_name]:
            start_date, end_date = self.time_ranges[range_name]()
            self.emit_range_changed(range_name, start_date, end_date)

    def apply_custom_range(self):
        """Apply the custom date range"""
        start_date = self.date_from.date().toString("yyyy-MM-dd")
        end_date = self.date_to.date().toString("yyyy-MM-dd")
        self.emit_range_changed("Custom", start_date, end_date)

    def emit_range_changed(self, period_type, start_date, end_date):
        """Emit the range changed signal"""
        self.rangeChanged.emit(period_type, start_date, end_date)

    def validate_dates(self):
        """Ensure from date is before to date"""
        from_date = self.date_from.date()
        to_date = self.date_to.date()

        if from_date > to_date:
            self.date_from.setDate(to_date)

    def _get_today_range(self):
        """Get date range for today"""
        today = QDate.currentDate()
        return today.toString("yyyy-MM-dd"), today.toString("yyyy-MM-dd")

    def _get_yesterday_range(self):
        """Get date range for yesterday"""
        yesterday = QDate.currentDate().addDays(-1)
        return yesterday.toString("yyyy-MM-dd"), yesterday.toString("yyyy-MM-dd")

    def _get_this_week_range(self):
        """Get date range for current week (Sunday-Saturday)"""
        today = QDate.currentDate()
        start = today.addDays(-(today.dayOfWeek() % 7))  # Sunday
        end = start.addDays(6)  # Saturday
        return start.toString("yyyy-MM-dd"), end.toString("yyyy-MM-dd")

    def _get_last_week_range(self):
        """Get date range for last week"""
        today = QDate.currentDate()
        start = today.addDays(-(today.dayOfWeek() % 7) - 7)  # Sunday of last week
        end = start.addDays(6)  # Saturday of last week
        return start.toString("yyyy-MM-dd"), end.toString("yyyy-MM-dd")

    def _get_this_month_range(self):
        """Get date range for current month"""
        today = QDate.currentDate()
        start = QDate(today.year(), today.month(), 1)
        end = QDate(today.year(), today.month(), today.daysInMonth())
        return start.toString("yyyy-MM-dd"), end.toString("yyyy-MM-dd")

    def _get_last_month_range(self):
        """Get date range for last month"""
        today = QDate.currentDate()
        month = today.month() - 1
        year = today.year()

        if month == 0:
            month = 12
            year -= 1

        start = QDate(year, month, 1)
        end = QDate(year, month, start.daysInMonth())
        return start.toString("yyyy-MM-dd"), end.toString("yyyy-MM-dd")

    def _get_this_quarter_range(self):
        """Get date range for current quarter"""
        today = QDate.currentDate()
        quarter = (today.month() - 1) // 3
        start_month = quarter * 3 + 1
        end_month = start_month + 2

        start = QDate(today.year(), start_month, 1)
        end = QDate(today.year(), end_month, QDate(today.year(), end_month, 1).daysInMonth())
        return start.toString("yyyy-MM-dd"), end.toString("yyyy-MM-dd")

    def _get_last_quarter_range(self):
        """Get date range for last quarter"""
        today = QDate.currentDate()
        quarter = (today.month() - 1) // 3 - 1
        year = today.year()

        if quarter < 0:
            quarter = 3
            year -= 1

        start_month = quarter * 3 + 1
        end_month = start_month + 2

        start = QDate(year, start_month, 1)
        end = QDate(year, end_month, QDate(year, end_month, 1).daysInMonth())
        return start.toString("yyyy-MM-dd"), end.toString("yyyy-MM-dd")

    def _get_this_year_range(self):
        """Get date range for current year"""
        year = QDate.currentDate().year()
        start = QDate(year, 1, 1)
        end = QDate(year, 12, 31)
        return start.toString("yyyy-MM-dd"), end.toString("yyyy-MM-dd")

    def _get_last_year_range(self):
        """Get date range for last year"""
        year = QDate.currentDate().year() - 1
        start = QDate(year, 1, 1)
        end = QDate(year, 12, 31)
        return start.toString("yyyy-MM-dd"), end.toString("yyyy-MM-dd")

    def _get_all_time_range(self):
        """Get date range for all time (arbitrarily far back to today)"""
        end = QDate.currentDate()
        start = QDate(2000, 1, 1)  # Arbitrary far past date
        return start.toString("yyyy-MM-dd"), end.toString("yyyy-MM-dd")

    def apply_theme(self):
        """Apply current theme styling"""
        # Get theme colors
        text_color = get_color('text')
        bg_color = get_color('background')
        card_bg = get_color('card_bg')
        border_color = get_color('border')
        button_color = get_color('button')
        button_hover = get_color('button_hover')
        button_pressed = get_color('button_pressed')
        highlight_color = get_color('highlight')

        # Style the combo box
        self.range_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {card_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 28px;
            }}

            QComboBox:hover {{
                border: 1px solid {highlight_color};
            }}

            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {border_color};
            }}
        """)

        # Style date edits
        date_style = f"""
            QDateEdit {{
                background-color: {card_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 4px 8px;
                min-height: 28px;
            }}

            QDateEdit:hover {{
                border: 1px solid {highlight_color};
            }}

            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {border_color};
            }}
        """

        self.date_from.setStyleSheet(date_style)
        self.date_to.setStyleSheet(date_style)

        # Style the apply button
        self.apply_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {button_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 4px 16px;
                font-weight: bold;
                min-height: 28px;
            }}

            QPushButton:hover {{
                background-color: {button_hover};
                border: 1px solid {highlight_color};
            }}

            QPushButton:pressed {{
                background-color: {button_pressed};
            }}
        """)

        # Style labels
        self.label.setStyleSheet(f"color: {text_color};")


class ChartBase(QWidget):
    """Base class for chart widgets with common functionality"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.data = []
        self.setMinimumSize(300, 250)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Tooltip for hover data
        self.tooltip = FloatingToolTip(self)

        # Animation timer with safety
        self.animation_timer = None

        # Animation state
        self.is_animating = False

        # Apply theme
        self.apply_theme()

    def setup_animation(self, interval=50):
        """Setup animation timer with proper handling"""
        if self.animation_timer is None:
            self.animation_timer = QTimer(self)
            self.animation_timer.timeout.connect(self.update)
            self.animation_timer.start(interval)

    def stop_animation(self):
        """Safely stop animation"""
        if self.animation_timer is not None and self.animation_timer.isActive():
            self.animation_timer.stop()

    def start_animation(self):
        """Safely start animation"""
        if self.animation_timer is not None and not self.animation_timer.isActive():
            self.animation_timer.start()
            self.is_animating = True

    def update_data(self, data, title=None):
        """Update chart data and optionally title"""
        self.data = data
        if title:
            self.title = title

        # Restart animation for new data
        self.is_animating = True
        self.start_animation()
        self.update()

    def apply_theme(self):
        """Apply current theme styling to be implemented by subclasses"""
        pass

    def show_tooltip(self, pos, text):
        """Show tooltip at the specified position"""
        self.tooltip.show_at(pos, text)

    def hide_tooltip(self):
        """Hide tooltip"""
        self.tooltip.hide_tooltip()

    def cleanup(self):
        """Clean up resources"""
        self.stop_animation()
        if hasattr(self, 'tooltip'):
            self.tooltip.hide_tooltip()

class ModernPieChart(ChartBase):
    """Enhanced pie chart with smooth gradients and animations"""

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setMouseTracking(True)

        # Animation properties
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update)
        self.animation_timer.start(50)  # 50ms refresh rate for smooth animation
        self.animation_progress = 0

        # Interactive properties
        self.hovered_slice = -1
        self.mouse_x = -1
        self.mouse_y = -1

        # Modern color palette with gradients
        self.colors = [
            QColor("#4361ee"), QColor("#3a0ca3"), QColor("#7209b7"),
            QColor("#f72585"), QColor("#4cc9f0"), QColor("#4895ef"),
            QColor("#560bad"), QColor("#480ca8"), QColor("#b5179e"),
            QColor("#3f37c9"), QColor("#0077b6"), QColor("#023e8a")
        ]

    def mouseMoveEvent(self, event):
        """Track mouse position for hover effects"""
        self.mouse_x = event.x()
        self.mouse_y = event.y()
        self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        """Reset hover state when mouse leaves"""
        self.mouse_x = -1
        self.mouse_y = -1
        self.hovered_slice = -1
        self.hide_tooltip()
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        """Paint the chart with enhanced visual effects"""
        if not self.data:
            return

        # Update animation progress
        self.animation_progress = (self.animation_progress + 1) % 100
        animation_factor = 1.0 + 0.03 * math.sin(self.animation_progress / 50.0 * math.pi)

        # Setup painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw title with subtle shadow
        title_font = painter.font()
        title_font.setPointSize(get_font_size("large"))
        title_font.setBold(True)
        painter.setFont(title_font)

        # Shadow effect for title
        painter.setPen(QColor(0, 0, 0, 50))
        painter.drawText(22, 32, self.title)

        # Actual title
        painter.setPen(QColor(get_color('text')))
        painter.drawText(20, 30, self.title)

        # Calculate total for percentages
        total = sum(value for _, value in self.data)
        if total <= 0:
            return

        # Define pie chart dimensions
        width = self.width() - 60
        height = self.height() - 80
        chart_size = min(width, height)
        chart_rect = QRect(
            (self.width() - chart_size) // 2,
            60,
            chart_size,
            chart_size
        )

        # Calculate center and radii
        center_x = chart_rect.center().x()
        center_y = chart_rect.center().y()
        outer_radius = chart_size // 2
        inner_radius = outer_radius * 0.55  # 55% of radius for donut hole

        # Check if mouse is over the chart for hover detection
        mouse_dist = math.sqrt((self.mouse_x - center_x) ** 2 + (self.mouse_y - center_y) ** 2)
        mouse_in_donut = inner_radius < mouse_dist < outer_radius

        # Draw subtle shadow behind chart
        shadow_rect = QRect(chart_rect)
        shadow_rect.translate(4, 4)
        shadow_gradient = QRadialGradient(
            chart_rect.center(),
            outer_radius * 1.1
        )
        shadow_gradient.setColorAt(0, QColor(0, 0, 0, 30))
        shadow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(shadow_gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(shadow_rect)

        # Draw slices with enhanced styling
        start_angle = 0
        self.hovered_slice = -1

        for i, (label, value) in enumerate(self.data):
            # Calculate angle
            angle = int(360 * value / total)
            if angle == 0:
                continue

            # Calculate middle angle for potential hover
            mid_angle_rad = math.radians(start_angle + angle / 2)

            # Check if slice is hovered
            if mouse_in_donut:
                # Calculate angle of mouse position
                mouse_angle = math.degrees(math.atan2(self.mouse_y - center_y, self.mouse_x - center_x))
                # Convert to same coordinate system as start_angle
                mouse_angle = (90 - mouse_angle) % 360

                # Check if mouse angle is within slice
                slice_end = start_angle + angle
                if start_angle <= mouse_angle <= slice_end or \
                        (start_angle <= mouse_angle + 360 <= slice_end + 360):
                    self.hovered_slice = i

                    # Show tooltip with slice data
                    percentage = 100 * value / total
                    tooltip_text = f"{label}: {value} ({percentage:.1f}%)"
                    self.show_tooltip(QPoint(self.mouse_x, self.mouse_y), tooltip_text)

            # Determine if slice should be highlighted
            is_hovered = (self.hovered_slice == i)

            # Calculate offset for hovered slice
            offset_x, offset_y = 0, 0
            if is_hovered:
                offset_dist = 10
                offset_x = math.cos(mid_angle_rad) * offset_dist
                offset_y = -math.sin(mid_angle_rad) * offset_dist  # Negative because Y is inverted

            # Create enhanced gradient for slice
            base_color = self.colors[i % len(self.colors)]

            # Make hovered slices more vibrant
            if is_hovered:
                base_color = base_color.lighter(115)

            # Create radial gradient for slice
            gradient = QRadialGradient(
                chart_rect.center(),
                outer_radius
            )

            # Enhanced gradient with highlight effect
            gradient.setColorAt(0.5, base_color.lighter(120))
            gradient.setColorAt(0.8, base_color)
            gradient.setColorAt(1.0, base_color.darker(110))

            # Setup painter for slice
            painter.setBrush(QBrush(gradient))

            # Enhanced slice border
            if is_hovered:
                glow_pen = QPen(QColor(255, 255, 255, 120), 2)
                painter.setPen(glow_pen)
            else:
                painter.setPen(QPen(QColor(get_color('card_bg')), 1))

            # Draw slice with offset if hovered
            slice_rect = QRect(chart_rect)
            if is_hovered:
                # Apply offset for pop-out effect
                slice_rect.translate(int(offset_x), int(offset_y))

                # Apply slightly stronger animation for hovered slice
                pulse_factor = 1.0 + 0.06 * math.sin(self.animation_progress / 50.0 * math.pi * 2)
                slice_rect = QRect(
                    int(center_x - outer_radius * pulse_factor + offset_x),
                    int(center_y - outer_radius * pulse_factor + offset_y),
                    int(outer_radius * 2 * pulse_factor),
                    int(outer_radius * 2 * pulse_factor)
                )

            # Draw the pie slice
            painter.drawPie(slice_rect, start_angle * 16, angle * 16)

            # Draw percentage label for larger slices or hovered slice
            if angle > 15 or is_hovered:
                # Calculate position for label
                label_radius = outer_radius * (0.75 if not is_hovered else 0.8)
                label_x = center_x + math.cos(mid_angle_rad) * label_radius + offset_x
                label_y = center_y - math.sin(mid_angle_rad) * label_radius + offset_y

                # Format percentage
                percentage = 100 * value / total
                percentage_text = f"{percentage:.1f}%"

                # Setup text font
                text_font = painter.font()
                text_font.setPointSize(get_font_size("medium") - 1 if is_hovered else get_font_size("small"))
                text_font.setBold(is_hovered)
                painter.setFont(text_font)

                # Calculate text dimensions for centering
                fm = QFontMetrics(text_font)
                text_width = fm.horizontalAdvance(percentage_text)
                text_height = fm.height()

                # Draw text with enhanced visibility
                if is_hovered:
                    # Glow effect for hovered slice text
                    glow_color = QColor(255, 255, 255, 160)
                    for offset in range(3, 0, -1):
                        painter.setPen(QColor(glow_color))
                        glow_color.setAlpha(glow_color.alpha() - 40)
                        painter.drawText(
                            int(label_x - text_width / 2) + offset,
                            int(label_y + text_height / 4),
                            percentage_text
                        )
                        painter.drawText(
                            int(label_x - text_width / 2) - offset,
                            int(label_y + text_height / 4),
                            percentage_text
                        )
                        painter.drawText(
                            int(label_x - text_width / 2),
                            int(label_y + text_height / 4) + offset,
                            percentage_text
                        )
                        painter.drawText(
                            int(label_x - text_width / 2),
                            int(label_y + text_height / 4) - offset,
                            percentage_text
                        )

                # Draw main text in contrasting color
                if QColor(base_color).lightness() > 150:
                    text_color = QColor(0, 0, 0)
                else:
                    text_color = QColor(255, 255, 255)

                painter.setPen(text_color)
                painter.drawText(
                    int(label_x - text_width / 2),
                    int(label_y + text_height / 4),
                    percentage_text
                )

            # Update start angle for next slice
            start_angle += angle

        # Draw inner circle (donut hole) with subtle gradient
        bg_color = QColor(get_color('background'))
        inner_gradient = QRadialGradient(
            chart_rect.center(),
            inner_radius
        )
        inner_gradient.setColorAt(0, bg_color.lighter(115))
        inner_gradient.setColorAt(1, bg_color)

        painter.setBrush(QBrush(inner_gradient))
        painter.setPen(Qt.NoPen)

        inner_rect = QRect(
            center_x - inner_radius,
            center_y - inner_radius,
            inner_radius * 2,
            inner_radius * 2
        )
        painter.drawEllipse(inner_rect)

        # Draw legend with enhanced styling
        self.draw_legend(painter, total)

    def draw_legend(self, painter, total):
        """Draw the chart legend with modern styling"""
        # Set up legend position and styling
        legend_x = 20
        legend_y = self.height() - 20 - (len(self.data) * 22)

        # Limit to reasonable height
        if legend_y < 100:
            legend_y = 100

        # Setup legend font
        legend_font = painter.font()
        legend_font.setPointSize(get_font_size("small"))
        legend_font.setBold(False)
        painter.setFont(legend_font)

        # Draw legend items
        for i, (label, value) in enumerate(self.data):
            # Skip items with zero value
            if value == 0:
                continue

            # Determine if this legend item is highlighted
            is_highlighted = (self.hovered_slice == i)

            # Draw color indicator with enhanced styling
            color = self.colors[i % len(self.colors)]
            color_rect = QRect(legend_x, legend_y + (i * 22), 12, 12)

            if is_highlighted:
                # Draw glow for highlighted item
                glow_rect = color_rect.adjusted(-2, -2, 2, 2)
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(color).lighter(120))
                painter.drawRoundedRect(glow_rect, 3, 3)

                # Make highlighted color brighter
                color = color.lighter(115)

            # Draw rounded color box with gradient
            color_gradient = QLinearGradient(
                color_rect.topLeft(),
                color_rect.bottomRight()
            )
            color_gradient.setColorAt(0, color.lighter(110))
            color_gradient.setColorAt(1, color)

            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(color_gradient))
            painter.drawRoundedRect(color_rect, 3, 3)

            # Add thin border around color box
            painter.setPen(QPen(QColor(255, 255, 255, 100), 1))
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(color_rect, 3, 3)

            # Draw label text with formatting
            if is_highlighted:
                # Bold and slightly larger text for highlighted items
                highlight_font = painter.font()
                highlight_font.setBold(True)
                highlight_font.setPointSize(get_font_size("medium") - 1)
                painter.setFont(highlight_font)
                painter.setPen(QColor(get_color('highlight')))
            else:
                painter.setPen(QColor(get_color('text')))

            # Format the text with value and percentage
            percentage = 100 * value / total
            text = f"{label}: {value} ({percentage:.1f}%)"

            # Truncate long labels with ellipsis
            fm = QFontMetrics(painter.font())
            max_width = self.width() - legend_x - 20 - 20  # Account for margins
            if fm.horizontalAdvance(text) > max_width:
                text = fm.elidedText(text, Qt.ElideRight, max_width)

            painter.drawText(legend_x + 20, legend_y + (i * 22) + 11, text)

            # Reset font if it was changed
            if is_highlighted:
                painter.setFont(legend_font)

    def apply_theme(self):
        """Apply current theme styling"""
        # Nothing specific to do here - theme colors are used directly in paint event
        pass


class ModernBarChart(ChartBase):
    """Enhanced bar chart with modern styling and animations"""

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setMouseTracking(True)

        # Animation properties
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update)
        self.animation_timer.start(50)  # 50ms refresh
        self.animation_progress = 0
        self.bar_heights = []  # Tracks animated height of each bar

        # Interactive properties
        self.hovered_bar = -1
        self.mouse_x = -1
        self.mouse_y = -1

        # Modern gradient colors
        self.gradient_start = QColor("#4cc9f0")
        self.gradient_end = QColor("#3a0ca3")

    def mouseMoveEvent(self, event):
        """Track mouse position for hover effects"""
        self.mouse_x = event.x()
        self.mouse_y = event.y()
        self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        """Reset hover state when mouse leaves"""
        self.mouse_x = -1
        self.mouse_y = -1
        self.hovered_bar = -1
        self.hide_tooltip()
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        """Paint the chart with enhanced visual effects"""
        if not self.data:
            return

        # Update animation progress
        self.animation_progress = (self.animation_progress + 1) % 100
        animation_factor = 1.0 + 0.02 * math.sin(self.animation_progress / 50.0 * math.pi)

        # Initialize bar heights array if needed
        if len(self.bar_heights) != len(self.data):
            self.bar_heights = [0] * len(self.data)

        # Setup painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw title with subtle shadow
        title_font = painter.font()
        title_font.setPointSize(get_font_size("large"))
        title_font.setBold(True)
        painter.setFont(title_font)

        # Title shadow
        painter.setPen(QColor(0, 0, 0, 50))
        painter.drawText(22, 32, self.title)

        # Actual title
        painter.setPen(QColor(get_color('text')))
        painter.drawText(20, 30, self.title)

        # Define chart area
        chart_x = 80  # Space for Y-axis labels
        chart_y = 50  # Space for title
        chart_width = self.width() - chart_x - 30  # Right margin
        chart_height = self.height() - chart_y - 80  # Space for X-axis labels and legend

        # Draw subtle chart background
        chart_bg = QRect(chart_x, chart_y, chart_width, chart_height)
        bg_color = QColor(get_color('background'))

        # Background gradient
        bg_gradient = QLinearGradient(
            chart_bg.topLeft(),
            chart_bg.bottomRight()
        )

        if bg_color.lightness() < 128:  # Dark theme
            bg_gradient.setColorAt(0, bg_color.lighter(110))
            bg_gradient.setColorAt(1, bg_color)
        else:  # Light theme
            bg_gradient.setColorAt(0, bg_color)
            bg_gradient.setColorAt(1, bg_color.darker(105))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_gradient))
        painter.drawRoundedRect(chart_bg, 4, 4)

        # Draw axes
        axis_pen = QPen(QColor(get_color('border')))
        axis_pen.setWidth(2)
        painter.setPen(axis_pen)

        # Y-axis
        painter.drawLine(chart_x, chart_y, chart_x, chart_y + chart_height)

        # X-axis
        painter.drawLine(chart_x, chart_y + chart_height, chart_x + chart_width, chart_y + chart_height)

        # Draw grid lines
        grid_pen = QPen(QColor(get_color('border')))
        grid_pen.setStyle(Qt.DashLine)
        grid_pen.setWidth(1)
        painter.setPen(grid_pen)

        # Calculate scale with headroom
        max_value = max(value for _, value in self.data) if self.data else 0
        if max_value <= 0:
            return

        scale_factor = chart_height / (max_value * 1.15)  # 15% margin at top

        # Draw Y-axis grid and labels
        tick_count = 5
        tick_step = max_value / tick_count

        # Round tick step to a nice number
        magnitude = 10 ** math.floor(math.log10(tick_step))
        mantissa = tick_step / magnitude

        if mantissa < 1.5:
            nice_mantissa = 1
        elif mantissa < 3:
            nice_mantissa = 2
        elif mantissa < 7:
            nice_mantissa = 5
        else:
            nice_mantissa = 10

        nice_tick_step = nice_mantissa * magnitude

        # Draw grid lines and labels
        label_font = painter.font()
        label_font.setPointSize(get_font_size("small"))
        label_font.setBold(False)
        painter.setFont(label_font)

        for i in range(tick_count + 1):
            tick_value = i * nice_tick_step
            if tick_value > max_value * 1.15:
                break

            tick_y = chart_y + chart_height - tick_value * scale_factor

            # Grid line
            grid_color = QColor(get_color('border'))
            grid_color.setAlpha(30 + (i * 15))  # Increase opacity for higher values
            grid_pen.setColor(grid_color)
            painter.setPen(grid_pen)
            painter.drawLine(chart_x + 1, tick_y, chart_x + chart_width, tick_y)

            # Format tick label
            if tick_value >= 1000000:
                tick_label = f"{tick_value / 1000000:.1f}M"
            elif tick_value >= 1000:
                tick_label = f"{tick_value / 1000:.1f}K"
            else:
                tick_label = str(int(tick_value)) if tick_value == int(tick_value) else f"{tick_value:.1f}"

            # Draw Y-axis label
            painter.setPen(QColor(get_color('text')))
            text_width = painter.fontMetrics().horizontalAdvance(tick_label)
            painter.drawText(chart_x - text_width - 10, tick_y + 5, tick_label)

        # Calculate bar dimensions
        bar_count = len(self.data)
        available_width = chart_width - 30  # Margin
        max_bar_width = 65  # Maximum width for aesthetics
        min_bar_width = 20  # Minimum width

        if bar_count > 0:
            # Dynamic width based on space
            calculated_width = available_width / bar_count * 0.75
            bar_width = max(min_bar_width, min(max_bar_width, calculated_width))
            bar_spacing = available_width / bar_count - bar_width
        else:
            return

        # Reset hovered bar
        self.hovered_bar = -1

        # Create gradient for bars
        bar_gradient = QLinearGradient(0, chart_y, 0, chart_y + chart_height)
        bar_gradient.setColorAt(0, self.gradient_start)
        bar_gradient.setColorAt(1, self.gradient_end)

        # Draw bars with enhanced styling
        for i, (label, value) in enumerate(self.data):
            # Bar position
            bar_x = chart_x + 15 + i * (bar_width + bar_spacing)

            # Animate bar height
            target_height = value * scale_factor

            # Gradually approach target height for smooth animation
            if self.bar_heights[i] < target_height:
                self.bar_heights[i] = min(self.bar_heights[i] + (target_height / 15), target_height)
            elif self.bar_heights[i] > target_height:
                self.bar_heights[i] = max(self.bar_heights[i] - (target_height / 15), target_height)

            bar_height = self.bar_heights[i]
            bar_y = chart_y + chart_height - bar_height

            # Check if bar is hovered
            is_hovered = (
                    bar_x <= self.mouse_x <= bar_x + bar_width and
                    bar_y <= self.mouse_y <= bar_y + bar_height
            )

            if is_hovered:
                self.hovered_bar = i

                # Show tooltip with bar data
                tooltip_text = f"{label}: {value}"
                self.show_tooltip(QPoint(self.mouse_x, self.mouse_y), tooltip_text)

            # Bar dimensions with hover/animation effects
            actual_bar_y = bar_y
            actual_bar_height = bar_height
            actual_bar_width = bar_width

            # Apply hover and animation effects
            if is_hovered:
                # Make hovered bars stand out
                hover_scale = 1.05 + (0.02 * animation_factor)
                actual_bar_width = bar_width * hover_scale
                actual_bar_y -= 3  # Lift slightly
                actual_bar_height = bar_height * hover_scale
                bar_x -= (actual_bar_width - bar_width) / 2  # Center the wider bar
            else:
                # Subtle breathing animation for non-hovered bars
                breath_scale = 1.0 + (0.01 * animation_factor)
                actual_bar_height = bar_height * breath_scale
                actual_bar_y = chart_y + chart_height - actual_bar_height

            # Create path for bar with rounded top corners
            path = QPainterPath()
            corner_radius = min(6, actual_bar_width / 4)  # Limit corner radius

            # Start at bottom-left corner
            path.moveTo(bar_x, chart_y + chart_height)

            # Bottom edge
            path.lineTo(bar_x + actual_bar_width, chart_y + chart_height)

            # Right edge to top-right corner
            path.lineTo(bar_x + actual_bar_width, actual_bar_y + corner_radius)

            # Top-right rounded corner
            path.arcTo(
                bar_x + actual_bar_width - corner_radius * 2,
                actual_bar_y,
                corner_radius * 2,
                corner_radius * 2,
                0,
                90
            )

            # Top edge
            path.lineTo(bar_x + corner_radius, actual_bar_y)

            # Top-left rounded corner
            path.arcTo(
                bar_x,
                actual_bar_y,
                corner_radius * 2,
                corner_radius * 2,
                90,
                90
            )

            # Left edge back to start
            path.lineTo(bar_x, chart_y + chart_height)

            # Draw shadow for bar
            if is_hovered:
                # Enhanced shadow for hovered bars
                shadow_path = QPainterPath(path)
                shadow_offset = 5
                shadow_color = QColor(0, 0, 0, 50)

                painter.save()
                painter.setPen(Qt.NoPen)
                painter.setBrush(shadow_color)
                painter.translate(shadow_offset, shadow_offset)
                painter.drawPath(shadow_path)
                painter.restore()
            else:
                # Subtle shadow for non-hovered bars
                shadow_path = QPainterPath(path)
                shadow_offset = 3
                shadow_color = QColor(0, 0, 0, 30)

                painter.save()
                painter.setPen(Qt.NoPen)
                painter.setBrush(shadow_color)
                painter.translate(shadow_offset, shadow_offset)
                painter.drawPath(shadow_path)
                painter.restore()

            # Create custom gradient for this bar
            bar_gradient = QLinearGradient(
                bar_x,
                actual_bar_y,
                bar_x,
                chart_y + chart_height
            )

            if is_hovered:
                # Brighter gradient for hovered bars
                bar_gradient.setColorAt(0, self.gradient_start.lighter(120))
                bar_gradient.setColorAt(1, self.gradient_end.lighter(110))

                # Add shine effect at top
                bar_gradient.setColorAt(0.05, QColor(255, 255, 255, 100))
            else:
                # Normal gradient with slight variation based on position
                hue_shift = (i % 3) * 10  # Slight color variation
                start_color = self.gradient_start.lighter(100 + hue_shift)
                end_color = self.gradient_end.darker(100 - hue_shift)

                bar_gradient.setColorAt(0, start_color)
                bar_gradient.setColorAt(1, end_color)

            # Draw the bar
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(bar_gradient))
            painter.drawPath(path)

            # Add highlight edge
            edge_pen = QPen()
            if is_hovered:
                edge_pen.setColor(QColor(255, 255, 255, 120))
                edge_pen.setWidth(2)
            else:
                edge_pen.setColor(QColor(255, 255, 255, 60))
                edge_pen.setWidth(1)

            painter.setPen(edge_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)

            # Draw value on top of bar
            value_text = f"{value:.1f}" if isinstance(value, float) and value != int(value) else str(int(value))

            # Style based on hover
            if is_hovered:
                value_font = painter.font()
                value_font.setPointSize(get_font_size("medium"))
                value_font.setBold(True)
                painter.setFont(value_font)
            else:
                value_font = painter.font()
                value_font.setPointSize(get_font_size("small"))
                value_font.setBold(True)
                painter.setFont(value_font)

            text_width = painter.fontMetrics().horizontalAdvance(value_text)
            text_height = painter.fontMetrics().height()

            # Position text above bar
            text_x = bar_x + (actual_bar_width - text_width) / 2
            text_y = actual_bar_y - 8

            # Draw with shadow for better visibility
            if is_hovered:
                # Glow effect for hovered bar
                glow_color = QColor(0, 0, 0, 40)
                painter.setPen(glow_color)
                painter.drawText(text_x + 1, text_y + 1, value_text)
                painter.drawText(text_x - 1, text_y - 1, value_text)
                painter.drawText(text_x + 1, text_y - 1, value_text)
                painter.drawText(text_x - 1, text_y + 1, value_text)

            # Main text
            painter.setPen(QColor(get_color('text')))
            painter.drawText(text_x, text_y, value_text)

            # Reset font for labels
            label_font = painter.font()
            label_font.setPointSize(get_font_size("small"))
            label_font.setBold(False)
            painter.setFont(label_font)

            # Draw X-axis label
            label_text = label
            text_width = painter.fontMetrics().horizontalAdvance(label_text)

            # Rotate text if needed
            if bar_count > 6 or text_width > bar_width * 1.5:
                painter.save()
                label_x = bar_x + actual_bar_width / 2
                label_y = chart_y + chart_height + 12

                painter.translate(label_x, label_y)
                painter.rotate(45)

                # Draw the rotated label
                if is_hovered:
                    painter.setPen(QColor(get_color('highlight')))
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                else:
                    painter.setPen(QColor(get_color('text')))

                painter.drawText(5, 0, label_text)
                painter.restore()
            else:
                # Regular horizontal label
                label_x = bar_x + (actual_bar_width - text_width) / 2
                label_y = chart_y + chart_height + 20

                if is_hovered:
                    painter.setPen(QColor(get_color('highlight')))
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                else:
                    painter.setPen(QColor(get_color('text')))

                painter.drawText(label_x, label_y, label_text)

    def apply_theme(self):
        """Apply current theme styling"""
        # Theme colors are applied directly in paint event
        pass


class ModernLineChart(ChartBase):
    """Enhanced line chart with smooth curves and area fill"""

    def __init__(self, title="", parent=None, include_area=True):
        super().__init__(title, parent)
        self.setMouseTracking(True)
        self.include_area = include_area

        # Animation properties
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update)
        self.animation_timer.start(50)  # 50ms refresh rate
        self.animation_progress = 0
        self.animation_completed = False

        # Interactive properties
        self.hovered_point_index = -1
        self.mouse_x = -1
        self.mouse_y = -1

        # Line style properties
        self.line_width = 3
        self.point_radius = 4
        self.line_color = QColor(get_color('highlight'))

    def set_data(self, data, is_time_series=False):
        """Set chart data with time series option"""
        self.data = data
        self.is_time_series = is_time_series
        self.animation_completed = False
        self.update()

    def mouseMoveEvent(self, event):
        """Track mouse position for hover effects"""
        self.mouse_x = event.x()
        self.mouse_y = event.y()
        self.update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        """Reset hover state when mouse leaves"""
        self.mouse_x = -1
        self.mouse_y = -1
        self.hovered_point_index = -1
        self.hide_tooltip()
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        """Paint the chart with enhanced visual effects"""
        if not self.data or len(self.data) < 2:
            return

        # Update animation progress
        if not self.animation_completed:
            self.animation_progress = min(self.animation_progress + 2, 100)
            if self.animation_progress >= 100:
                self.animation_completed = True

        # Setup painter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw title with subtle shadow
        title_font = painter.font()
        title_font.setPointSize(get_font_size("large"))
        title_font.setBold(True)
        painter.setFont(title_font)

        # Title shadow
        painter.setPen(QColor(0, 0, 0, 50))
        painter.drawText(22, 32, self.title)

        # Actual title
        painter.setPen(QColor(get_color('text')))
        painter.drawText(20, 30, self.title)

        # Define chart area
        chart_x = 80  # Space for Y-axis labels
        chart_y = 50  # Space for title
        chart_width = self.width() - chart_x - 30  # Right margin
        chart_height = self.height() - chart_y - 50  # Space for X-axis labels

        # Draw chart background
        chart_bg = QRect(chart_x, chart_y, chart_width, chart_height)
        bg_color = QColor(get_color('background'))

        # Background gradient
        bg_gradient = QLinearGradient(
            chart_bg.topLeft(),
            chart_bg.bottomRight()
        )

        if bg_color.lightness() < 128:  # Dark theme
            bg_gradient.setColorAt(0, bg_color.lighter(110))
            bg_gradient.setColorAt(1, bg_color)
        else:  # Light theme
            bg_gradient.setColorAt(0, bg_color)
            bg_gradient.setColorAt(1, bg_color.darker(105))

        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(bg_gradient))
        painter.drawRoundedRect(chart_bg, 4, 4)

        # Find data range
        y_values = [point[1] for point in self.data]
        min_y = min(y_values)
        max_y = max(y_values)

        # Ensure there's a range to display
        if max_y == min_y:
            max_y = min_y + 1

        # Add padding to Y range (10%)
        y_padding = (max_y - min_y) * 0.1
        min_y = max(0, min_y - y_padding)  # Don't go below zero for most data
        max_y = max_y + y_padding

        # Calculate scales
        x_scale = chart_width / (len(self.data) - 1)
        y_scale = chart_height / (max_y - min_y)

        # Draw grid and axes
        self._draw_grid(painter, chart_x, chart_y, chart_width, chart_height, min_y, max_y)

        # Convert data points to screen coordinates
        points = []
        for i, (label, value) in enumerate(self.data):
            # Apply animation by limiting the number of points
            if self.animation_completed or i <= (len(self.data) - 1) * self.animation_progress / 100:
                x = chart_x + i * x_scale
                y = chart_y + chart_height - (value - min_y) * y_scale
                points.append((x, y, label, value))

        # Don't draw anything else if we don't have enough points yet
        if len(points) < 2:
            return

        # Draw area fill beneath line
        if self.include_area:
            # Create gradient for area
            area_gradient = QLinearGradient(0, chart_y, 0, chart_y + chart_height)

            area_color = QColor(self.line_color)
            area_gradient.setColorAt(0, QColor(area_color.red(),
                                               area_color.green(),
                                               area_color.blue(),
                                               100))  # Semi-transparent at top
            area_gradient.setColorAt(1, QColor(area_color.red(),
                                               area_color.green(),
                                               area_color.blue(),
                                               10))  # Almost transparent at bottom

            # Create path for area
            area_path = QPainterPath()
            area_path.moveTo(points[0][0], chart_y + chart_height)  # Start at bottom left
            area_path.lineTo(points[0][0], points[0][1])  # Up to first point

            # Add all points to path
            for x, y, _, _ in points:
                area_path.lineTo(x, y)

            # Close the path
            area_path.lineTo(points[-1][0], chart_y + chart_height)  # Down to bottom right
            area_path.closeSubpath()

            # Draw area
            painter.setPen(Qt.NoPen)
            painter.setBrush(area_gradient)
            painter.drawPath(area_path)

        # Draw the line with enhanced styling
        pen = QPen(self.line_color)
        pen.setWidth(self.line_width)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        # Create path for smooth line
        line_path = QPainterPath()
        line_path.moveTo(points[0][0], points[0][1])

        # Draw smooth curve through points
        if len(points) > 2:
            # Use Bezier curves for smooth line
            for i in range(1, len(points)):
                # Calculate control points for curve
                if i < len(points) - 1:
                    # Middle control points for smoother curve
                    c1x = (points[i - 1][0] + points[i][0]) / 2
                    c1y = points[i][1]
                    c2x = (points[i][0] + points[i + 1][0]) / 2
                    c2y = points[i][1]
                    line_path.cubicTo(c1x, c1y, c2x, c2y, points[i][0], points[i][1])
                else:
                    # Last point
                    line_path.lineTo(points[i][0], points[i][1])
        else:
            # Simple line for just 2 points
            line_path.lineTo(points[1][0], points[1][1])

        # Draw the line
        painter.drawPath(line_path)

        # Reset hover point
        self.hovered_point_index = -1

        # Find closest point to mouse for hover effect
        if self.mouse_x >= chart_x and self.mouse_x <= chart_x + chart_width:
            closest_dist = float('inf')
            closest_index = -1

            for i, (x, y, label, value) in enumerate(points):
                # Distance to point
                dist = math.sqrt((x - self.mouse_x) ** 2 + (y - self.mouse_y) ** 2)

                # Update closest if needed
                if dist < closest_dist and dist < 30:  # 30px hover radius
                    closest_dist = dist
                    closest_index = i

            # If we found a close point, mark it as hovered
            if closest_index >= 0:
                self.hovered_point_index = closest_index

                # Show tooltip with point data
                x, y, label, value = points[closest_index]
                tooltip_text = f"{label}: {value}"
                self.show_tooltip(QPoint(int(x), int(y - 20)), tooltip_text)

        # Draw points with highlight for hovered point
        for i, (x, y, label, value) in enumerate(points):
            if i == self.hovered_point_index:
                # Hovered point gets larger, brighter appearance
                # Draw glow
                glow_radius = self.point_radius * 2.5
                glow_gradient = QRadialGradient(x, y, glow_radius)
                glow_color = QColor(self.line_color)
                glow_color.setAlpha(100)
                glow_gradient.setColorAt(0, glow_color)
                glow_gradient.setColorAt(1, QColor(0, 0, 0, 0))

                painter.setPen(Qt.NoPen)
                painter.setBrush(glow_gradient)
                painter.drawEllipse(QPointF(x, y), glow_radius, glow_radius)

                # Draw larger point
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor("white"))
                painter.drawEllipse(QPointF(x, y), self.point_radius * 1.8, self.point_radius * 1.8)

                # Draw colored center
                painter.setBrush(self.line_color.lighter(120))
                painter.drawEllipse(QPointF(x, y), self.point_radius * 1.2, self.point_radius * 1.2)
            else:
                # Regular points
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor("white"))
                painter.drawEllipse(QPointF(x, y), self.point_radius, self.point_radius)

                painter.setBrush(self.line_color)
                painter.drawEllipse(QPointF(x, y), self.point_radius * 0.6, self.point_radius * 0.6)

        # Draw X-axis labels (simplified for space)
        if len(self.data) > 1:
            label_count = min(len(self.data), 5)  # Limit to avoid crowding
            step = max(1, len(self.data) // label_count)

            for i in range(0, len(self.data), step):
                if i < len(points):  # Make sure we have this point already
                    x, _, label, _ = points[i]

                    # Format label
                    if len(label) > 10:
                        label = label[:7] + "..."

                    # Draw label
                    painter.setPen(QColor(get_color('text')))
                    text_width = painter.fontMetrics().horizontalAdvance(label)
                    painter.drawText(x - text_width / 2, chart_y + chart_height + 20, label)

    def _draw_grid(self, painter, x, y, width, height, min_y, max_y):
        """Draw grid, axes and labels"""
        # Draw axes
        axis_pen = QPen(QColor(get_color('border')))
        axis_pen.setWidth(2)
        painter.setPen(axis_pen)

        # Y-axis
        painter.drawLine(x, y, x, y + height)

        # X-axis
        painter.drawLine(x, y + height, x + width, y + height)

        # Draw Y-axis grid and labels
        grid_pen = QPen(QColor(get_color('border')))
        grid_pen.setStyle(Qt.DashLine)
        grid_pen.setWidth(1)

        # Y-axis ticks
        tick_count = 5
        y_range = max_y - min_y
        tick_step = y_range / tick_count

        # Format Y labels
        label_font = painter.font()
        label_font.setPointSize(get_font_size("small"))
        label_font.setBold(False)
        painter.setFont(label_font)

        for i in range(tick_count + 1):
            tick_value = min_y + i * tick_step
            tick_y = y + height - i * height / tick_count

            # Grid line
            grid_color = QColor(get_color('border'))
            grid_color.setAlpha(30 + (i * 15))
            grid_pen.setColor(grid_color)
            painter.setPen(grid_pen)
            painter.drawLine(x + 1, tick_y, x + width, tick_y)

            # Format label
            if tick_value >= 1000000:
                tick_label = f"{tick_value / 1000000:.1f}M"
            elif tick_value >= 1000:
                tick_label = f"{tick_value / 1000:.1f}K"
            else:
                tick_label = f"{tick_value:.1f}"

            # Y label
            painter.setPen(QColor(get_color('text')))
            text_width = painter.fontMetrics().horizontalAdvance(tick_label)
            painter.drawText(x - text_width - 10, tick_y + 5, tick_label)

    def apply_theme(self):
        """Apply current theme styling"""
        self.line_color = QColor(get_color('highlight'))


class DataLoader(QObject):
    """Worker object for loading data asynchronously"""

    data_loaded = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, db, settings_db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.settings_db = settings_db
        self.filters = {}
        self._loading_lock = threading.RLock()  # Lock for thread safety
        self._is_loading = False  # Flag to prevent concurrent loading

    def load_data(self, filters=None):
        """Load statistics data with optional filters and thread safety"""
        # Thread safety - prevent concurrent loading
        with self._loading_lock:
            if self._is_loading:
                logger.info("Data loading already in progress, request ignored")
                return

            self._is_loading = True

        if filters:
            self.filters = filters

        try:
            # Get all parts with error handling
            try:
                all_parts = self.db.get_all_parts()
            except Exception as e:
                logger.error(f"Database error when loading all parts: {e}")
                self.error_occurred.emit(f"Database error: {str(e)}")
                self._is_loading = False
                return

            # Apply filters if any
            parts = self._apply_filters(all_parts)

            # Calculate statistics
            stats = self._calculate_stats(parts)

            # Emit signal with data
            self.data_loaded.emit(stats)

        except Exception as e:
            logger.error(f"Error loading statistics data: {str(e)}")
            self.error_occurred.emit(f"Failed to load data: {str(e)}")
        finally:
            # Always reset loading flag
            self._is_loading = False

    def _apply_filters(self, parts):
        """Apply filters to the parts list with improved error handling"""
        if not self.filters:
            return parts

        filtered_parts = []

        try:
            for part in parts:
                include_part = True

                # Stock status filtering
                if 'stock_status' in self.filters:
                    quantity = part.get('quantity', 0)

                    if quantity == 0 and not self.filters['stock_status'].get('out_of_stock', True):
                        include_part = False
                    elif 0 < quantity < 5 and not self.filters['stock_status'].get('low_stock', True):
                        include_part = False
                    elif quantity >= 5 and not self.filters['stock_status'].get('in_stock', True):
                        include_part = False

                # Category filtering
                if include_part and self.filters.get('category'):
                    if part.get('category') != self.filters['category']:
                        include_part = False

                # Brand filtering
                if include_part and self.filters.get('brand'):
                    compatible_brands = part.get('compatible_brands', '')
                    brand_list = [b.strip() for b in compatible_brands.split(',')]
                    if self.filters['brand'] not in brand_list:
                        include_part = False

                # Price range filtering
                if include_part:
                    price = part.get('price', 0)
                    if self.filters.get('price_min') is not None and price < self.filters['price_min']:
                        include_part = False
                    if self.filters.get('price_max') is not None and price > self.filters['price_max']:
                        include_part = False

                # Date filtering would be handled here if dates were available

                # Add part if it passes all filters
                if include_part:
                    filtered_parts.append(part)

        except Exception as e:
            logger.error(f"Error applying filters: {e}")
            # If error in filtering, return unfiltered parts
            return parts

        return filtered_parts


    def _calculate_stats(self, parts):
        """Calculate all statistics from parts data"""
        # Basic metrics
        total_parts = len(parts)
        total_value = sum(part.get('price', 0) * part.get('quantity', 0) for part in parts)

        try:
            avg_price = sum(part.get('price', 0) for part in parts) / total_parts if total_parts > 0 else 0
        except Exception:
            avg_price = 0

        # Stock status metrics
        in_stock = sum(1 for part in parts if part.get('quantity', 0) >= 5)
        low_stock = sum(1 for part in parts if 0 < part.get('quantity', 0) < 5)
        out_of_stock = sum(1 for part in parts if part.get('quantity', 0) == 0)

        # Extract unique categories and brands
        categories = set()
        brands = set()

        for part in parts:
            # Categories
            category = part.get('category', '').strip()
            if category:
                categories.add(category)

            # Brands
            brands_str = part.get('compatible_brands', '').strip()
            if brands_str:
                for brand in brands_str.split(','):
                    brand = brand.strip()
                    if brand:
                        brands.add(brand)

        # Calculate category data
        category_data = {}
        for part in parts:
            category = part.get('category', 'Unknown').strip()
            if not category:
                category = 'Unknown'

            if category not in category_data:
                category_data[category] = {
                    'count': 0,
                    'value': 0,
                    'parts': []
                }

            quantity = part.get('quantity', 0)
            price = part.get('price', 0)
            value = quantity * price

            category_data[category]['count'] += 1
            category_data[category]['value'] += value
            category_data[category]['parts'].append(part)

        # Calculate brand data
        brand_data = {}
        for part in parts:
            brands_str = part.get('compatible_brands', '').strip()
            if not brands_str:
                continue

            for brand in brands_str.split(','):
                brand = brand.strip()
                if not brand:
                    continue

                if brand not in brand_data:
                    brand_data[brand] = {
                        'count': 0,
                        'value': 0,
                        'categories': set(),
                        'parts': []
                    }

                quantity = part.get('quantity', 0)
                price = part.get('price', 0)
                value = quantity * price
                category = part.get('category', 'Unknown').strip()

                brand_data[brand]['count'] += 1
                brand_data[brand]['value'] += value
                brand_data[brand]['parts'].append(part)

                if category:
                    brand_data[brand]['categories'].add(category)

        # Find top selling parts (hypothetical based on quantity)
        top_selling = sorted(
            parts,
            key=lambda p: p.get('quantity', 0),
            reverse=True
        )[:10]

        # Most valuable items
        valuable_items = sorted(
            parts,
            key=lambda p: p.get('price', 0) * p.get('quantity', 0),
            reverse=True
        )[:10]

        # Low stock items
        low_stock_items = [
            part for part in parts
            if 0 < part.get('quantity', 0) < 5
        ]

        # Calculate price range for filtering
        prices = [part.get('price', 0) for part in parts]
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0

        # Combine all statistics
        stats = {
            'total_parts': total_parts,
            'total_value': total_value,
            'avg_price': avg_price,
            'stock_status': {
                'in_stock': in_stock,
                'low_stock': low_stock,
                'out_of_stock': out_of_stock
            },
            'categories': sorted(list(categories)),
            'brands': sorted(list(brands)),
            'category_data': category_data,
            'brand_data': brand_data,
            'top_selling': top_selling,
            'valuable_items': valuable_items,
            'low_stock_items': low_stock_items,
            'price_range': {
                'min': min_price,
                'max': max_price
            }
        }

        return stats


class StatisticsWidget(QWidget):
    """
        Enhanced dashboard for car parts inventory analytics.

        Features:
        - Modern, interactive visualizations
        - Real-time data filtering and insights
        - Performance optimizations for large datasets
        - Responsive layout that adapts to screen size
        - Export capabilities for reports
        """

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.db = None
        self.settings_db = None
        self.stats_data = {}
        self.currency_symbol = "₪"  # Default

        # Thread-safe data handling
        self.data_lock = threading.RLock()

        # Signal connections tracking
        self._connected_signals = []

        # Setup UI
        self.setup_ui()

        # Apply initial translations
        self.update_translations()

        # Initialize loading overlay
        self.loading_overlay = LoadingOverlay(self)
        self.loading_overlay.raise_()  # Ensure overlay is on top

        # Data not loaded yet
        self.data_loaded = False

        # Setup refresh timer (every 5 minutes)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(300000)  # 5 minutes

        # Apply theme
        self.apply_theme()

    """
    Modified methods from statistics.py to improve layout and scrolling
    """

    def setup_ui(self):
        """Set up the main UI components with improved layout and scrolling"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Create scroll area for the main content
        self.main_scroll_area = QScrollArea()
        self.main_scroll_area.setWidgetResizable(True)
        self.main_scroll_area.setFrameShape(QFrame.NoFrame)
        self.main_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create a container widget for the scrollable content
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(15)

        # Dashboard header with controls
        header_layout = QHBoxLayout()

        # Title
        self.title_label = QLabel("Analytics Dashboard")
        title_font = self.title_label.font()
        title_font.setPointSize(get_font_size("xlarge") - 2)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Time range selector
        self.time_range_selector = TimeRangeSelector()
        self._connected_signals.append((self.time_range_selector.rangeChanged, self.on_time_range_changed))
        self.time_range_selector.rangeChanged.connect(self.on_time_range_changed)
        header_layout.addWidget(self.time_range_selector)

        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setIcon(QApplication.style().standardIcon(QApplication.style().SP_BrowserReload))
        self._connected_signals.append((self.refresh_button.clicked, self.refresh_data))
        self.refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_button)

        # Export button
        self.export_button = QPushButton("Export")
        self._connected_signals.append((self.export_button.clicked, self.export_report))
        self.export_button.clicked.connect(self.export_report)
        header_layout.addWidget(self.export_button)

        # Add header to main layout (outside scroll area)
        main_layout.addLayout(header_layout)

        # Optional filter panel
        self.filter_panel = FilterPanel()
        self._connected_signals.append((self.filter_panel.filtersChanged, self.apply_filters))
        self.filter_panel.filtersChanged.connect(self.apply_filters)
        main_layout.addWidget(self.filter_panel)

        # Summary cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(15)

        # Total parts card
        self.total_parts_card = AnimatedStat(
            "Total Parts", "0", icon="📦"
        )
        cards_layout.addWidget(self.total_parts_card)

        # Total value card
        self.total_value_card = AnimatedStat(
            "Total Value", "0", icon="💰", is_currency=True
        )
        cards_layout.addWidget(self.total_value_card)

        # Average price card
        self.avg_price_card = AnimatedStat(
            "Average Price", "0", icon="⚖️", is_currency=True
        )
        cards_layout.addWidget(self.avg_price_card)

        # Out of stock card
        self.out_of_stock_card = AnimatedStat(
            "Out of Stock", "0", icon="⚠️"
        )
        cards_layout.addWidget(self.out_of_stock_card)

        self.scroll_layout.addLayout(cards_layout)

        # Main charts section
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)

        # Category distribution chart
        category_chart_frame = QFrame()
        category_chart_frame.setFrameShape(QFrame.StyledPanel)
        category_chart_frame.setObjectName("chartFrame")
        category_chart_frame.setMinimumHeight(300)  # Ensure enough vertical space
        category_chart_layout = QVBoxLayout(category_chart_frame)

        self.category_chart = ModernPieChart("Parts by Category")
        self.category_chart.setMinimumSize(300, 250)  # Set minimum chart size
        category_chart_layout.addWidget(self.category_chart)

        charts_layout.addWidget(category_chart_frame)

        # Value by brand chart
        brand_chart_frame = QFrame()
        brand_chart_frame.setFrameShape(QFrame.StyledPanel)
        brand_chart_frame.setObjectName("chartFrame")
        brand_chart_frame.setMinimumHeight(300)  # Ensure enough vertical space
        brand_chart_layout = QVBoxLayout(brand_chart_frame)

        self.brand_chart = ModernBarChart("Inventory Value by Brand")
        self.brand_chart.setMinimumSize(300, 250)  # Set minimum chart size
        brand_chart_layout.addWidget(self.brand_chart)

        charts_layout.addWidget(brand_chart_frame)

        self.scroll_layout.addLayout(charts_layout)

        # Tab widget for different data views
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setMinimumHeight(400)  # Ensure tabs have enough space

        # Inventory insights tab
        self.insights_tab = QWidget()
        self.setup_insights_tab()
        self.tabs.addTab(self.insights_tab, "Inventory Insights")

        # Categories tab
        self.categories_tab = QWidget()
        self.setup_categories_tab()
        self.tabs.addTab(self.categories_tab, "Categories")

        # Brands tab
        self.brands_tab = QWidget()
        self.setup_brands_tab()
        self.tabs.addTab(self.brands_tab, "Brands")

        # Inventory tab
        self.inventory_tab = QWidget()
        self.setup_inventory_tab()
        self.tabs.addTab(self.inventory_tab, "Low Stock")

        self.scroll_layout.addWidget(self.tabs)

        # Set the content widget to the scroll area
        self.main_scroll_area.setWidget(scroll_content)

        # Add the scroll area to the main layout
        main_layout.addWidget(self.main_scroll_area, 1)  # Give it a stretch factor of 1

        # Status bar
        status_layout = QHBoxLayout()

        self.status_label = QLabel("Ready")
        status_font = self.status_label.font()
        status_font.setItalic(True)
        self.status_label.setFont(status_font)

        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        self.last_updated_label = QLabel("")
        status_layout.addWidget(self.last_updated_label)

        main_layout.addLayout(status_layout)

    def setup_insights_tab(self):
        """Set up the inventory insights tab with scrolling support"""
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create the content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)

        # Top row - insights cards
        insights_layout = QHBoxLayout()
        insights_layout.setSpacing(15)

        # Low stock insight
        self.low_stock_insight = InsightCard(
            "Low Stock Items",
            "0",
            "Items that need reordering soon"
        )
        insights_layout.addWidget(self.low_stock_insight)

        # Categories insight
        self.categories_insight = InsightCard(
            "Categories",
            "0",
            "Total categories in inventory"
        )
        insights_layout.addWidget(self.categories_insight)

        # Brands insight
        self.brands_insight = InsightCard(
            "Brands",
            "0",
            "Car brands with compatible parts"
        )
        insights_layout.addWidget(self.brands_insight)

        layout.addLayout(insights_layout)

        # Inventory over time chart
        inventory_chart_frame = QFrame()
        inventory_chart_frame.setFrameShape(QFrame.StyledPanel)
        inventory_chart_frame.setObjectName("chartFrame")
        inventory_chart_frame.setMinimumHeight(300)  # Ensure enough vertical space
        inventory_chart_layout = QVBoxLayout(inventory_chart_frame)

        self.inventory_chart = ModernLineChart("Inventory Value Trend")
        self.inventory_chart.setMinimumSize(300, 250)  # Set minimum chart size
        inventory_chart_layout.addWidget(self.inventory_chart)

        # Generate some sample data for now
        sample_data = [
            ("Jan", 150000),
            ("Feb", 180000),
            ("Mar", 210000),
            ("Apr", 190000),
            ("May", 220000),
            ("Jun", 250000),
        ]
        self.inventory_chart.update_data(sample_data)

        layout.addWidget(inventory_chart_frame)

        # Most valuable items table
        table_layout = QVBoxLayout()

        table_label = QLabel("Most Valuable Inventory Items")
        table_font = table_label.font()
        table_font.setBold(True)
        table_font.setPointSize(get_font_size("large"))
        table_label.setFont(table_font)
        table_layout.addWidget(table_label)

        self.valuable_table = DataTable()
        self.valuable_table.setMinimumHeight(200)  # Ensure table is visible
        self.valuable_table.setColumnCount(5)
        self.valuable_table.setHorizontalHeaderLabels([
            "Part Name", "Category", "Price", "Quantity", "Total Value"
        ])
        self.valuable_table.set_column_widths([180, 150, 100, 100, 120])
        table_layout.addWidget(self.valuable_table)

        layout.addLayout(table_layout)

        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)

        # Create a main layout for the tab
        tab_layout = QVBoxLayout(self.insights_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

    def setup_categories_tab(self):
        """Set up the categories tab with scrolling support"""
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create the content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)

        # Category selector
        selector_layout = QHBoxLayout()

        selector_layout.addWidget(QLabel("Select Category:"))

        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(200)
        self.category_combo.currentIndexChanged.connect(self.update_category_data)
        selector_layout.addWidget(self.category_combo)

        selector_layout.addStretch()

        layout.addLayout(selector_layout)

        # Category charts in a split view
        charts_layout = QHBoxLayout()

        # Items by category pie chart
        pie_frame = QFrame()
        pie_frame.setFrameShape(QFrame.StyledPanel)
        pie_frame.setObjectName("chartFrame")
        pie_frame.setMinimumHeight(300)  # Ensure enough vertical space
        pie_layout = QVBoxLayout(pie_frame)

        self.category_pie_chart = ModernPieChart("Part Distribution")
        self.category_pie_chart.setMinimumSize(300, 250)  # Set minimum chart size
        pie_layout.addWidget(self.category_pie_chart)

        charts_layout.addWidget(pie_frame)

        # Value distribution bar chart
        bar_frame = QFrame()
        bar_frame.setFrameShape(QFrame.StyledPanel)
        bar_frame.setObjectName("chartFrame")
        bar_frame.setMinimumHeight(300)  # Ensure enough vertical space
        bar_layout = QVBoxLayout(bar_frame)

        self.category_bar_chart = ModernBarChart("Price Distribution")
        self.category_bar_chart.setMinimumSize(300, 250)  # Set minimum chart size
        bar_layout.addWidget(self.category_bar_chart)

        charts_layout.addWidget(bar_frame)

        layout.addLayout(charts_layout)

        # Category parts table
        table_layout = QVBoxLayout()

        table_label = QLabel("Parts in Category")
        table_font = table_label.font()
        table_font.setBold(True)
        table_font.setPointSize(get_font_size("large"))
        table_label.setFont(table_font)
        table_layout.addWidget(table_label)

        self.category_table = DataTable()
        self.category_table.setMinimumHeight(200)  # Ensure table is visible
        self.category_table.setColumnCount(5)
        self.category_table.setHorizontalHeaderLabels([
            "Part Name", "Compatible Brands", "Price", "Quantity", "Value"
        ])
        self.category_table.set_column_widths([150, 200, 100, 100, 100])
        table_layout.addWidget(self.category_table)

        layout.addLayout(table_layout)

        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)

        # Create a main layout for the tab
        tab_layout = QVBoxLayout(self.categories_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

    def setup_brands_tab(self):
        """Set up the brands tab with scrolling support"""
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create the content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)

        # Brand selector
        selector_layout = QHBoxLayout()

        selector_layout.addWidget(QLabel("Select Brand:"))

        self.brand_combo = QComboBox()
        self.brand_combo.setMinimumWidth(200)
        self.brand_combo.currentIndexChanged.connect(self.update_brand_data)
        selector_layout.addWidget(self.brand_combo)

        selector_layout.addStretch()

        layout.addLayout(selector_layout)

        # Brand charts in a split view
        charts_layout = QHBoxLayout()

        # Categories for this brand pie chart
        pie_frame = QFrame()
        pie_frame.setFrameShape(QFrame.StyledPanel)
        pie_frame.setObjectName("chartFrame")
        pie_frame.setMinimumHeight(300)  # Ensure enough vertical space
        pie_layout = QVBoxLayout(pie_frame)

        self.brand_category_chart = ModernPieChart("Categories for Brand")
        self.brand_category_chart.setMinimumSize(300, 250)  # Set minimum chart size
        pie_layout.addWidget(self.brand_category_chart)

        charts_layout.addWidget(pie_frame)

        # Price distribution for this brand
        bar_frame = QFrame()
        bar_frame.setFrameShape(QFrame.StyledPanel)
        bar_frame.setObjectName("chartFrame")
        bar_frame.setMinimumHeight(300)  # Ensure enough vertical space
        bar_layout = QVBoxLayout(bar_frame)

        self.brand_price_chart = ModernBarChart("Price Distribution")
        self.brand_price_chart.setMinimumSize(300, 250)  # Set minimum chart size
        bar_layout.addWidget(self.brand_price_chart)

        charts_layout.addWidget(bar_frame)

        layout.addLayout(charts_layout)

        # Brand parts table
        table_layout = QVBoxLayout()

        table_label = QLabel("Parts for Brand")
        table_font = table_label.font()
        table_font.setBold(True)
        table_font.setPointSize(get_font_size("large"))
        table_label.setFont(table_font)
        table_layout.addWidget(table_label)

        self.brand_table = DataTable()
        self.brand_table.setMinimumHeight(200)  # Ensure table is visible
        self.brand_table.setColumnCount(5)
        self.brand_table.setHorizontalHeaderLabels([
            "Part Name", "Category", "Price", "Quantity", "Value"
        ])
        self.brand_table.set_column_widths([180, 150, 100, 100, 120])
        table_layout.addWidget(self.brand_table)

        layout.addLayout(table_layout)

        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)

        # Create a main layout for the tab
        tab_layout = QVBoxLayout(self.brands_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

    def setup_inventory_tab(self):
        """Set up the inventory tab with scrolling support"""
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create the content widget
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(15)

        # Top row - distribution charts
        charts_layout = QHBoxLayout()

        # Stock status chart
        status_frame = QFrame()
        status_frame.setFrameShape(QFrame.StyledPanel)
        status_frame.setObjectName("chartFrame")
        status_frame.setMinimumHeight(300)  # Ensure enough vertical space
        status_layout = QVBoxLayout(status_frame)

        self.stock_status_chart = ModernPieChart("Stock Status")
        self.stock_status_chart.setMinimumSize(300, 250)  # Set minimum chart size
        status_layout.addWidget(self.stock_status_chart)

        charts_layout.addWidget(status_frame)

        # Category vs Stock level chart
        category_frame = QFrame()
        category_frame.setFrameShape(QFrame.StyledPanel)
        category_frame.setObjectName("chartFrame")
        category_frame.setMinimumHeight(300)  # Ensure enough vertical space
        category_layout = QVBoxLayout(category_frame)

        self.category_stock_chart = ModernBarChart("Low Stock by Category")
        self.category_stock_chart.setMinimumSize(300, 250)  # Set minimum chart size
        category_layout.addWidget(self.category_stock_chart)

        charts_layout.addWidget(category_frame)

        layout.addLayout(charts_layout)

        # Low stock table
        table_layout = QVBoxLayout()

        table_label = QLabel("Low Stock Items (Quantity < 5)")
        table_font = table_label.font()
        table_font.setBold(True)
        table_font.setPointSize(get_font_size("large"))
        table_label.setFont(table_font)
        table_layout.addWidget(table_label)

        self.low_stock_table = DataTable()
        self.low_stock_table.setMinimumHeight(200)  # Ensure table is visible
        self.low_stock_table.setColumnCount(5)
        self.low_stock_table.setHorizontalHeaderLabels([
            "Part Name", "Category", "Compatible Brands", "Price", "Quantity"
        ])
        self.low_stock_table.set_column_widths([150, 120, 200, 100, 80])
        table_layout.addWidget(self.low_stock_table)

        layout.addLayout(table_layout)

        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)

        # Create a main layout for the tab
        tab_layout = QVBoxLayout(self.inventory_tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll_area)

    def resizeEvent(self, event):
        """Handle resize events with improved overlay handling"""
        super().resizeEvent(event)

        # Make sure loading overlay covers everything
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setGeometry(self.rect())
            # Ensure overlay stays on top
            if self.loading_overlay.isVisible():
                self.loading_overlay.raise_()

        # Update scroll area to match new size
        if hasattr(self, 'main_scroll_area'):
            scrollbar_width = self.main_scroll_area.verticalScrollBar().width() if self.main_scroll_area.verticalScrollBar().isVisible() else 0
            content_width = self.width() - 30 - scrollbar_width  # 30 for margins

            # Update minimum sizes of chart frames if needed
            for chart in self.findChildren(ChartBase):
                parent_frame = chart.parent()
                if isinstance(parent_frame, QFrame) and "chartFrame" in parent_frame.objectName():
                    # Calculate appropriate width based on layout
                    if parent_frame.parent() and parent_frame.parent().layout():
                        if isinstance(parent_frame.parent().layout(), QHBoxLayout):
                            # For horizontal layouts, divide available width
                            item_count = parent_frame.parent().layout().count()
                            if item_count > 0:
                                chart_width = max(300, (content_width - (item_count - 1) * 15) // item_count)
                                chart.setMinimumWidth(chart_width - 30)  # 30 for frame padding

    def apply_theme(self):
        """Apply current theme to the widget with scrollbar styling"""
        try:
            # Get theme colors
            bg_color = get_color('background')
            text_color = get_color('text')
            card_bg = get_color('card_bg')
            border_color = get_color('border')
            highlight_color = get_color('highlight')

            # Apply styles with enhanced scrollbar styling
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {bg_color};
                    color: {text_color};
                }}

                QTabWidget::pane {{
                    border: 1px solid {border_color};
                    border-radius: 4px;
                }}

                QTabBar::tab {{
                    background-color: {card_bg};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 8px 12px;
                    margin-right: 2px;
                }}

                QTabBar::tab:selected {{
                    background-color: {highlight_color};
                    color: {get_color('highlight_text')};
                }}

                QTabBar::tab:hover:!selected {{
                    background-color: {get_color('button_hover')};
                }}

                #chartFrame {{
                    background-color: {card_bg};
                    border: 1px solid {border_color};
                    border-radius: 8px;
                }}

                /* Scrollbar styling */
                QScrollBar:vertical {{
                    border: none;
                    background: {QColor(card_bg).darker(110).name()};
                    width: 12px;
                    margin: 0px;
                    border-radius: 6px;
                }}

                QScrollBar::handle:vertical {{
                    background-color: {highlight_color};
                    border-radius: 6px;
                    min-height: 30px;
                }}

                QScrollBar::handle:vertical:hover {{
                    background-color: {QColor(highlight_color).lighter(110).name()};
                }}

                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0px;
                }}

                QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                    background: none;
                }}

                QScrollArea {{
                    border: none;
                    background-color: transparent;
                }}
            """)

            # Update all child widgets that have theme support
            for widget in self.findChildren(QWidget):
                if hasattr(widget, 'apply_theme'):
                    widget.apply_theme()

        except Exception as e:
            logger.error(f"Error applying theme: {e}")


    def setup_database(self, db, settings_db=None):
        """Setup database connections"""
        self.db = db
        self.settings_db = settings_db

        # Load currency symbol from settings
        self._load_currency_settings()

        # Create data loader worker
        self.data_loader = DataLoader(db, settings_db)
        self._connected_signals.append((self.data_loader.data_loaded, self.on_data_loaded))
        self._connected_signals.append((self.data_loader.error_occurred, self.show_error))
        self.data_loader.data_loaded.connect(self.on_data_loaded)
        self.data_loader.error_occurred.connect(self.show_error)

        # Load initial data
        self.refresh_data()

    def refresh_data(self):
        """Refresh data from database with safeguards"""
        if not self.db:
            self.show_error("Database not configured")
            return

        # Prevent multiple simultaneous refreshes
        if hasattr(self, 'refresh_button') and self.refresh_button:
            if not self.refresh_button.isEnabled():
                return

        # Show loading state
        self.status_label.setText("Loading data...")
        self.loading_overlay.setVisible(True)
        self.loading_overlay.raise_()  # Ensure overlay is on top

        if hasattr(self, 'refresh_button') and self.refresh_button:
            self.refresh_button.setEnabled(False)

        # Start data loading in background with a small delay to ensure UI updates
        QTimer.singleShot(100, lambda: self.data_loader.load_data())

    def on_data_loaded(self, data):
        """Handle loaded data with thread safety"""
        try:
            with self.data_lock:
                # Store data
                self.stats_data = data
                self.data_loaded = True

            # Update UI (this calls methods that use the data_lock internally)
            self.update_ui_with_data()

            # Update status
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_updated_label.setText(f"Last updated: {timestamp}")
            self.status_label.setText("Ready")

            # Enable refresh button
            if hasattr(self, 'refresh_button') and self.refresh_button:
                self.refresh_button.setEnabled(True)

            # Hide loading overlay
            self.loading_overlay.setVisible(False)

            # Populate filter dropdowns
            with self.data_lock:
                self.filter_panel.populate_categories(self.stats_data['categories'])
                self.filter_panel.populate_brands(self.stats_data['brands'])

        except Exception as e:
            logger.error(f"Error processing loaded data: {e}")
            self.show_error(f"Failed to process data: {str(e)}")

            # Ensure refresh button is enabled even on error
            if hasattr(self, 'refresh_button') and self.refresh_button:
                self.refresh_button.setEnabled(True)

            # Hide loading overlay
            self.loading_overlay.setVisible(False)

    def update_ui_with_data(self):
        """Update all UI elements with current data in an organized manner"""
        try:
            with self.data_lock:
                # Cache necessary data to minimize lock time
                total_parts = self.stats_data['total_parts']
                total_value = self.stats_data['total_value']
                avg_price = self.stats_data['avg_price']
                out_of_stock = self.stats_data['stock_status']['out_of_stock']
                low_stock = self.stats_data['stock_status']['low_stock']
                categories_count = len(self.stats_data['categories'])
                brands_count = len(self.stats_data['brands'])
                categories = self.stats_data['categories'].copy()
                brands = self.stats_data['brands'].copy()

            # Update summary stats with animations
            self.total_parts_card.update_value(total_parts)
            self.total_value_card.update_value(total_value)
            self.avg_price_card.update_value(avg_price)
            self.out_of_stock_card.update_value(out_of_stock)

            # Update insights cards
            self.low_stock_insight.update_data(
                low_stock,
                "Items that need reordering soon",
                total_parts
            )

            self.categories_insight.update_data(
                categories_count,
                "Total categories in inventory",
                50  # Arbitrary max for progress bar
            )

            self.brands_insight.update_data(
                brands_count,
                "Car brands with compatible parts",
                50  # Arbitrary max for progress bar
            )

            # Update selectors
            self._update_selectors(categories, brands)

            # Update charts
            self._update_main_charts()

            # Update stock charts
            self._update_stock_charts()

            # Update tables
            self._update_tables()

        except Exception as e:
            logger.error(f"Error updating UI with data: {e}")
            self.show_error(f"Error updating display: {str(e)}")

    def _update_selectors(self, categories, brands):
        """Update dropdown selectors with thread safety"""
        try:
            # Remember current selections
            current_category = self.category_combo.currentText() if self.category_combo.count() > 0 else ""
            current_brand = self.brand_combo.currentText() if self.brand_combo.count() > 0 else ""

            # Update category selector
            self.category_combo.blockSignals(True)  # Prevent triggering updates during population
            self.category_combo.clear()
            self.category_combo.addItems(categories)

            # Restore previous selection if possible
            if current_category in categories:
                self.category_combo.setCurrentText(current_category)
            self.category_combo.blockSignals(False)

            # Update brand selector
            self.brand_combo.blockSignals(True)
            self.brand_combo.clear()
            self.brand_combo.addItems(brands)

            # Restore previous selection if possible
            if current_brand in brands:
                self.brand_combo.setCurrentText(current_brand)
            self.brand_combo.blockSignals(False)

            # Trigger data updates for current selections
            if self.category_combo.currentText():
                self.update_category_data()

            if self.brand_combo.currentText():
                self.update_brand_data()

        except Exception as e:
            logger.error(f"Error updating selectors: {e}")

    def _update_main_charts(self):
        """Update main charts with thread safety"""
        try:
            # Update category chart
            self.update_category_chart()

            # Update brand chart
            self.update_brand_chart()

        except Exception as e:
            logger.error(f"Error updating main charts: {e}")

    def _update_stock_charts(self):
        """Update stock-related charts with thread safety"""
        try:
            # Update stock status chart
            self.update_stock_status_chart()

            # Update category stock chart
            self.update_category_stock_chart()

        except Exception as e:
            logger.error(f"Error updating stock charts: {e}")

    def _update_tables(self):
        """Update all data tables with thread safety"""
        try:
            # Update valuable items table
            self.update_valuable_table()

            # Update low stock table
            self.update_low_stock_table()

        except Exception as e:
            logger.error(f"Error updating tables: {e}")

    def show_error(self, message):
        """Display error message and update status"""
        self.status_label.setText(f"Error: {message}")
        self.status_label.setStyleSheet("color: red;")

        # Ensure loading overlay is hidden
        if hasattr(self, 'loading_overlay'):
            self.loading_overlay.setVisible(False)

        # Re-enable refresh button
        if hasattr(self, 'refresh_button') and self.refresh_button:
            self.refresh_button.setEnabled(True)

        # Log the error
        logger.error(message)

        # Reset status styling after a delay
        QTimer.singleShot(5000, lambda: self.status_label.setStyleSheet(""))



    def closeEvent(self, event):
        """Clean up resources when widget is closed"""
        # Stop timers
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()

        # Clean up chart animations
        for widget in self.findChildren(ChartBase):
            if hasattr(widget, 'cleanup'):
                widget.cleanup()

        # Disconnect signals to prevent memory leaks
        self._disconnect_signals()

        super().closeEvent(event)

    def _disconnect_signals(self):
        """Disconnect all signals"""
        try:
            for signal, slot in self._connected_signals:
                try:
                    signal.disconnect(slot)
                except (TypeError, RuntimeError):
                    # It's normal to get an exception if already disconnected
                    pass

            self._connected_signals = []
        except Exception as e:
            logger.error(f"Error disconnecting signals: {e}")




    def _load_currency_settings(self):
        """Load currency settings from database"""
        try:
            if self.settings_db:
                currency_code = self.settings_db.get_setting('default_currency', 'ILS')
                currency_symbols = {
                    'ILS': '₪',
                    'USD': '$',
                           'EUR': '€',
                'GBP': '£'
                }
                self.currency_symbol = currency_symbols.get(currency_code, '₪')

                # Update currency symbol in stat cards
                self.total_value_card.currency_symbol = self.currency_symbol
                self.avg_price_card.currency_symbol = self.currency_symbol

                logger.info(f"Using currency symbol: {self.currency_symbol}")
        except Exception as e:
            logger.error(f"Error loading currency settings: {e}")


    def update_category_chart(self):
        """Update the main category distribution chart"""
        try:
            # Prepare data for chart
            category_counts = []
            for category, data in self.stats_data['category_data'].items():
                category_counts.append((category, data['count']))

            # Sort by count descending
            category_counts.sort(key=lambda x: x[1], reverse=True)

            # Limit to top 8 categories for readability
            if len(category_counts) > 8:
                other_count = sum(count for _, count in category_counts[8:])
                top_categories = category_counts[:8]
                top_categories.append(("Other", other_count))
                category_counts = top_categories

            # Update chart
            self.category_chart.update_data(category_counts)

        except Exception as e:
            logger.error(f"Error updating category chart: {e}")

    def update_brand_chart(self):
        """Update the main brand value chart"""
        try:
            # Prepare data for chart
            brand_values = []
            for brand, data in self.stats_data['brand_data'].items():
                brand_values.append((brand, data['value']))

            # Sort by value descending
            brand_values.sort(key=lambda x: x[1], reverse=True)

            # Limit to top 8 brands for readability
            brand_values = brand_values[:8]

            # Update chart
            self.brand_chart.update_data(brand_values)

        except Exception as e:
            logger.error(f"Error updating brand chart: {e}")

    def update_stock_status_chart(self):
        """Update the stock status distribution chart"""
        try:
            # Prepare data
            stock_status = [
                ("In Stock", self.stats_data['stock_status']['in_stock']),
                ("Low Stock", self.stats_data['stock_status']['low_stock']),
                ("Out of Stock", self.stats_data['stock_status']['out_of_stock'])
            ]

            # Update chart
            self.stock_status_chart.update_data(stock_status)

        except Exception as e:
            logger.error(f"Error updating stock status chart: {e}")

    def update_category_stock_chart(self):
        """Update the category vs stock level chart"""
        try:
            # Get categories with low stock
            low_stock_by_category = {}

            for part in self.stats_data['low_stock_items']:
                category = part.get('category', 'Unknown')
                if not category:
                    category = 'Unknown'

                if category not in low_stock_by_category:
                    low_stock_by_category[category] = 0

                low_stock_by_category[category] += 1

            # Convert to list and sort
            category_stock = [(cat, count) for cat, count in low_stock_by_category.items()]
            category_stock.sort(key=lambda x: x[1], reverse=True)

            # Limit to top 8
            category_stock = category_stock[:8]

            # Update chart
            self.category_stock_chart.update_data(category_stock)

        except Exception as e:
            logger.error(f"Error updating category stock chart: {e}")

    def update_valuable_table(self):
        """Update the most valuable items table"""
        try:
            # Clear table
            self.valuable_table.setRowCount(0)

            # Get valuable items
            valuable_items = self.stats_data['valuable_items']

            # Set row count
            self.valuable_table.setRowCount(len(valuable_items))

            # Add data
            for row, part in enumerate(valuable_items):
                # Part name
                name_item = QTableWidgetItem(part.get('product_name', 'Unknown'))
                self.valuable_table.setItem(row, 0, name_item)

                # Category
                category_item = QTableWidgetItem(part.get('category', 'Unknown'))
                self.valuable_table.setItem(row, 1, category_item)

                # Price
                price = part.get('price', 0)
                price_item = QTableWidgetItem(f"{self.currency_symbol}{price:.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.valuable_table.setItem(row, 2, price_item)

                # Quantity
                quantity = part.get('quantity', 0)
                quantity_item = QTableWidgetItem(str(quantity))
                quantity_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.valuable_table.setItem(row, 3, quantity_item)

                # Total value
                value = price * quantity
                value_item = QTableWidgetItem(f"{self.currency_symbol}{value:.2f}")
                value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.valuable_table.setItem(row, 4, value_item)

        except Exception as e:
            logger.error(f"Error updating valuable items table: {e}")

    def update_low_stock_table(self):
        """Update the low stock items table"""
        try:
            # Clear table
            self.low_stock_table.setRowCount(0)

            # Get low stock items
            low_stock_items = self.stats_data['low_stock_items']

            # Set row count
            self.low_stock_table.setRowCount(len(low_stock_items))

            # Add data
            for row, part in enumerate(low_stock_items):
                # Part name
                name_item = QTableWidgetItem(part.get('product_name', 'Unknown'))
                self.low_stock_table.setItem(row, 0, name_item)

                # Category
                category_item = QTableWidgetItem(part.get('category', 'Unknown'))
                self.low_stock_table.setItem(row, 1, category_item)

                # Compatible brands
                brands_item = QTableWidgetItem(part.get('compatible_brands', 'N/A'))
                self.low_stock_table.setItem(row, 2, brands_item)

                # Price
                price = part.get('price', 0)
                price_item = QTableWidgetItem(f"{self.currency_symbol}{price:.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.low_stock_table.setItem(row, 3, price_item)

                # Quantity
                quantity = part.get('quantity', 0)
                quantity_item = QTableWidgetItem(str(quantity))
                quantity_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.low_stock_table.setItem(row, 4, quantity_item)

        except Exception as e:
            logger.error(f"Error updating low stock table: {e}")

    def update_category_data(self):
        """Update the category tab with data for the selected category"""
        try:
            category = self.category_combo.currentText()
            if not category or category not in self.stats_data['category_data']:
                return

            category_data = self.stats_data['category_data'][category]

            # Update charts
            self._update_category_pie_chart(category)
            self._update_category_price_chart(category)

            # Update table
            self.category_table.setRowCount(0)
            self.category_table.setRowCount(len(category_data['parts']))

            for row, part in enumerate(category_data['parts']):
                # Part name
                name_item = QTableWidgetItem(part.get('product_name', 'Unknown'))
                self.category_table.setItem(row, 0, name_item)

                # Compatible brands
                brands_item = QTableWidgetItem(part.get('compatible_brands', 'N/A'))
                self.category_table.setItem(row, 1, brands_item)

                # Price
                price = part.get('price', 0)
                price_item = QTableWidgetItem(f"{self.currency_symbol}{price:.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.category_table.setItem(row, 2, price_item)

                # Quantity
                quantity = part.get('quantity', 0)
                quantity_item = QTableWidgetItem(str(quantity))
                quantity_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.category_table.setItem(row, 3, quantity_item)

                # Value
                value = price * quantity
                value_item = QTableWidgetItem(f"{self.currency_symbol}{value:.2f}")
                value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.category_table.setItem(row, 4, value_item)

        except Exception as e:
            logger.error(f"Error updating category data: {e}")

    def _update_category_pie_chart(self, category):
        """Update the category parts distribution pie chart"""
        try:
            if category not in self.stats_data['category_data']:
                return

            category_data = self.stats_data['category_data'][category]

            # Count parts by compatible brand
            brand_counts = {}
            for part in category_data['parts']:
                brands_str = part.get('compatible_brands', '')
                if not brands_str:
                    continue

                for brand in brands_str.split(','):
                    brand = brand.strip()
                    if not brand:
                        continue

                    if brand not in brand_counts:
                        brand_counts[brand] = 0

                    brand_counts[brand] += 1

            # Convert to list and sort
            brand_data = [(brand, count) for brand, count in brand_counts.items()]
            brand_data.sort(key=lambda x: x[1], reverse=True)

            # Limit to top 8
            if len(brand_data) > 8:
                other_count = sum(count for _, count in brand_data[8:])
                top_brands = brand_data[:8]
                top_brands.append(("Other", other_count))
                brand_data = top_brands

            # Update chart
            self.category_pie_chart.update_data(brand_data, f"Brands for {category}")

        except Exception as e:
            logger.error(f"Error updating category pie chart: {e}")

    def _update_category_price_chart(self, category):
        """Update the category price distribution chart"""
        try:
            if category not in self.stats_data['category_data']:
                return

            category_data = self.stats_data['category_data'][category]

            # Define price ranges
            price_ranges = [
                (0, 50),
                (50, 100),
                (100, 200),
                (200, 500),
                (500, 1000),
                (1000, float('inf'))
            ]

            range_labels = [
                f"0-50 {self.currency_symbol}",
                f"50-100 {self.currency_symbol}",
                f"100-200 {self.currency_symbol}",
                f"200-500 {self.currency_symbol}",
                f"500-1000 {self.currency_symbol}",
                f"1000+ {self.currency_symbol}"
            ]

            # Count parts in each range
            range_counts = [0] * len(price_ranges)

            for part in category_data['parts']:
                price = part.get('price', 0)

                for i, (min_price, max_price) in enumerate(price_ranges):
                    if min_price <= price < max_price or (i == len(price_ranges) - 1 and price >= min_price):
                        range_counts[i] += 1
                        break

            # Create data for chart
            chart_data = [(label, count) for label, count in zip(range_labels, range_counts) if count > 0]

            # Update chart
            self.category_bar_chart.update_data(chart_data, f"Price Ranges for {category}")

        except Exception as e:
            logger.error(f"Error updating category price chart: {e}")

    def update_brand_data(self):
        """Update the brand tab with data for the selected brand"""
        try:
            brand = self.brand_combo.currentText()
            if not brand or brand not in self.stats_data['brand_data']:
                return

            brand_data = self.stats_data['brand_data'][brand]

            # Update charts
            self._update_brand_category_chart(brand)
            self._update_brand_price_chart(brand)

            # Update table
            self.brand_table.setRowCount(0)
            self.brand_table.setRowCount(len(brand_data['parts']))

            for row, part in enumerate(brand_data['parts']):
                # Part name
                name_item = QTableWidgetItem(part.get('product_name', 'Unknown'))
                self.brand_table.setItem(row, 0, name_item)

                # Category
                category_item = QTableWidgetItem(part.get('category', 'Unknown'))
                self.brand_table.setItem(row, 1, category_item)

                # Price
                price = part.get('price', 0)
                price_item = QTableWidgetItem(f"{self.currency_symbol}{price:.2f}")
                price_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.brand_table.setItem(row, 2, price_item)

                # Quantity
                quantity = part.get('quantity', 0)
                quantity_item = QTableWidgetItem(str(quantity))
                quantity_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.brand_table.setItem(row, 3, quantity_item)

                # Value
                value = price * quantity
                value_item = QTableWidgetItem(f"{self.currency_symbol}{value:.2f}")
                value_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.brand_table.setItem(row, 4, value_item)

        except Exception as e:
            logger.error(f"Error updating brand data: {e}")

    def _update_brand_category_chart(self, brand):
        """Update the brand categories distribution chart"""
        try:
            if brand not in self.stats_data['brand_data']:
                return

            brand_data = self.stats_data['brand_data'][brand]

            # Count parts by category
            category_counts = {}
            for part in brand_data['parts']:
                category = part.get('category', 'Unknown')
                if not category:
                    category = 'Unknown'

                if category not in category_counts:
                    category_counts[category] = 0

                category_counts[category] += 1

            # Convert to list and sort
            category_data = [(category, count) for category, count in category_counts.items()]
            category_data.sort(key=lambda x: x[1], reverse=True)

            # Update chart
            self.brand_category_chart.update_data(category_data, f"Categories for {brand}")

        except Exception as e:
            logger.error(f"Error updating brand category chart: {e}")

    def _update_brand_price_chart(self, brand):
        """Update the brand price distribution chart"""
        try:
            if brand not in self.stats_data['brand_data']:
                return

            brand_data = self.stats_data['brand_data'][brand]

            # Define price ranges
            price_ranges = [
                (0, 50),
                (50, 100),
                (100, 200),
                (200, 500),
                (500, 1000),
                (1000, float('inf'))
            ]

            range_labels = [
                f"0-50 {self.currency_symbol}",
                f"50-100 {self.currency_symbol}",
                f"100-200 {self.currency_symbol}",
                f"200-500 {self.currency_symbol}",
                f"500-1000 {self.currency_symbol}",
                f"1000+ {self.currency_symbol}"
            ]

            # Count parts in each range
            range_counts = [0] * len(price_ranges)

            for part in brand_data['parts']:
                price = part.get('price', 0)

                for i, (min_price, max_price) in enumerate(price_ranges):
                    if min_price <= price < max_price or (i == len(price_ranges) - 1 and price >= min_price):
                        range_counts[i] += 1
                        break

            # Create data for chart
            chart_data = [(label, count) for label, count in zip(range_labels, range_counts) if count > 0]

            # Update chart
            self.brand_price_chart.update_data(chart_data, f"Price Ranges for {brand}")

        except Exception as e:
            logger.error(f"Error updating brand price chart: {e}")

    def on_time_range_changed(self, period_type, start_date, end_date):
        """Handle time range selection changes"""
        logger.info(f"Time range changed: {period_type} ({start_date} to {end_date})")

        # Update filters and refresh
        filters = self.data_loader.filters.copy() if hasattr(self.data_loader, 'filters') else {}
        filters['date_from'] = start_date
        filters['date_to'] = end_date

        # Apply new filters (would trigger data reload in a real system)
        # For now, just display a status message
        self.status_label.setText(f"Selected time range: {period_type} ({start_date} to {end_date})")

    def apply_filters(self, filters):
        """Apply filters and reload data"""
        logger.info(f"Applying filters: {filters}")

        # Show loading state
        self.status_label.setText("Filtering data...")
        self.loading_overlay.setVisible(True)
        self.refresh_button.setEnabled(False)

        # Apply filters in background
        QTimer.singleShot(100, lambda: self.data_loader.load_data(filters))

    def export_report(self):
        """Export statistics report"""
        try:
            # Create file dialog
            options = QFileDialog.Options()
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Statistics Report",
                "",
                "CSV Files (*.csv)",
                options=options
            )

            if not file_path:
                return

            if not file_path.endswith('.csv'):
                # Add extension if needed
                file_path += '.csv'

            self._export_csv(file_path)

            self.status_label.setText(f"Report exported to {file_path}")

        except Exception as e:
            logger.error(f"Error exporting report: {e}")
            self.show_error(f"Failed to export report: {str(e)}")

    def _export_csv(self, file_path):
        """Export data to CSV format"""
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow([
                    "Statistics Report",
                    f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                ])
                writer.writerow([])

                # Summary section
                writer.writerow(["SUMMARY"])
                writer.writerow(["Total Parts", self.stats_data['total_parts']])
                writer.writerow(["Total Value", f"{self.currency_symbol}{self.stats_data['total_value']:.2f}"])
                writer.writerow(["Average Price", f"{self.currency_symbol}{self.stats_data['avg_price']:.2f}"])
                writer.writerow(["Categories", len(self.stats_data['categories'])])
                writer.writerow(["Brands", len(self.stats_data['brands'])])
                writer.writerow([])

                # Stock status
                writer.writerow(["STOCK STATUS"])
                writer.writerow(["In Stock", self.stats_data['stock_status']['in_stock']])
                writer.writerow(["Low Stock", self.stats_data['stock_status']['low_stock']])
                writer.writerow(["Out of Stock", self.stats_data['stock_status']['out_of_stock']])
                writer.writerow([])

                # Category breakdown
                writer.writerow(["CATEGORY BREAKDOWN"])
                writer.writerow(["Category", "Parts Count", "Total Value"])

                for category, data in sorted(
                        self.stats_data['category_data'].items(),
                        key=lambda x: x[1]['count'],
                        reverse=True
                ):
                    writer.writerow([
                        category,
                        data['count'],
                        f"{self.currency_symbol}{data['value']:.2f}"
                    ])
                writer.writerow([])

                # Brand breakdown
                writer.writerow(["BRAND BREAKDOWN"])
                writer.writerow(["Brand", "Parts Count", "Total Value"])

                for brand, data in sorted(
                        self.stats_data['brand_data'].items(),
                        key=lambda x: x[1]['count'],
                        reverse=True
                ):
                    writer.writerow([
                        brand,
                        data['count'],
                        f"{self.currency_symbol}{data['value']:.2f}"
                    ])
                writer.writerow([])

                # Most valuable items
                writer.writerow(["MOST VALUABLE ITEMS"])
                writer.writerow(["Part Name", "Category", "Price", "Quantity", "Total Value"])

                for part in self.stats_data['valuable_items']:
                    writer.writerow([
                        part.get('product_name', 'Unknown'),
                        part.get('category', 'Unknown'),
                        f"{self.currency_symbol}{part.get('price', 0):.2f}",
                        part.get('quantity', 0),
                        f"{self.currency_symbol}{part.get('price', 0) * part.get('quantity', 0):.2f}"
                    ])
                writer.writerow([])

                # Low stock items
                writer.writerow(["LOW STOCK ITEMS"])
                writer.writerow(["Part Name", "Category", "Price", "Quantity"])

                for part in self.stats_data['low_stock_items']:
                    writer.writerow([
                        part.get('product_name', 'Unknown'),
                        part.get('category', 'Unknown'),
                        f"{self.currency_symbol}{part.get('price', 0):.2f}",
                        part.get('quantity', 0)
                    ])

        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            raise

    def update_translations(self):
        """Update all translatable text in the statistics widget"""
        try:
            # Update main UI elements
            self.title_label.setText(self.translator.t("statistics:analytics_dashboard"))
            self.refresh_button.setText(self.translator.t("statistics:refresh_statistics"))
            self.export_button.setText(self.translator.t("statistics:export"))

            # Update tab names
            self.tabs.setTabText(0, self.translator.t("statistics:inventory_insights"))
            self.tabs.setTabText(1, self.translator.t("statistics:categories"))
            self.tabs.setTabText(2, self.translator.t("statistics:brands"))
            self.tabs.setTabText(3, self.translator.t("statistics:low_stock"))

            # Update stat cards
            self.total_parts_card.title = self.translator.t("statistics:total_parts")
            self.total_value_card.title = self.translator.t("statistics:total_value")
            self.avg_price_card.title = self.translator.t("statistics:average_price")
            self.out_of_stock_card.title = self.translator.t("statistics:out_of_stock")

            # Update insight cards
            self.low_stock_insight.title = self.translator.t("statistics:low_stock_items")
            self.low_stock_insight.context = self.translator.t("statistics:items_need_reordering")

            self.categories_insight.title = self.translator.t("statistics:categories")
            self.categories_insight.context = self.translator.t("statistics:total_categories")

            self.brands_insight.title = self.translator.t("statistics:brands")
            self.brands_insight.context = self.translator.t("statistics:car_brands_compatible")

            # Update chart titles
            self.inventory_chart.title = self.translator.t("statistics:inventory_value_trend")
            self.category_chart.title = self.translator.t("statistics:parts_by_category")
            self.brand_chart.title = self.translator.t("statistics:inventory_value_by_brand")
            self.category_pie_chart.title = self.translator.t("statistics:part_distribution")
            self.category_bar_chart.title = self.translator.t("statistics:price_distribution")
            self.brand_category_chart.title = self.translator.t("statistics:categories_for_brand")
            self.brand_price_chart.title = self.translator.t("statistics:price_distribution")
            self.stock_status_chart.title = self.translator.t("statistics:stock_status")
            self.category_stock_chart.title = self.translator.t("statistics:low_stock_by_category")

            # Update selectors and labels
            for widget in self.findChildren(QLabel):
                if widget.text() == "Select Category:":
                    widget.setText(self.translator.t("statistics:select_category"))
                elif widget.text() == "Select Brand:":
                    widget.setText(self.translator.t("statistics:select_brand"))
                elif widget.text() == "Most Valuable Inventory Items":
                    widget.setText(self.translator.t("statistics:most_valuable_items"))
                elif widget.text() == "Parts in Category":
                    widget.setText(self.translator.t("statistics:parts_in_category"))
                elif widget.text() == "Parts for Brand":
                    widget.setText(self.translator.t("statistics:parts_for_brand"))
                elif widget.text() == "Low Stock Items (Quantity < 5)":
                    widget.setText(self.translator.t("statistics:low_stock_items_quantity"))

            # Update filter panel
            if hasattr(self, 'filter_panel'):
                for child in self.filter_panel.findChildren(QLabel):
                    if child.text() == "Advanced Filters":
                        child.setText(self.translator.t("statistics:advanced_filters"))
                    elif child.text() == "Date Range:":
                        child.setText(self.translator.t("statistics:date_range"))
                    elif child.text() == "Categories:":
                        child.setText(self.translator.t("statistics:categories"))
                    elif child.text() == "Brands:":
                        child.setText(self.translator.t("statistics:brands"))
                    elif child.text() == "Stock Status:":
                        child.setText(self.translator.t("statistics:stock_status_filter"))
                    elif child.text() == "Price Range:":
                        child.setText(self.translator.t("statistics:price_range"))

                # Update filter checkboxes
                for child in self.filter_panel.findChildren(QCheckBox):
                    if child.text() == "In Stock":
                        child.setText(self.translator.t("statistics:in_stock"))
                    elif child.text() == "Low Stock":
                        child.setText(self.translator.t("statistics:low_stock"))
                    elif child.text() == "Out of Stock":
                        child.setText(self.translator.t("statistics:out_of_stock"))

                # Update filter buttons
                for child in self.filter_panel.findChildren(QPushButton):
                    if child.text() == "Reset":
                        child.setText(self.translator.t("statistics:reset"))
                    elif child.text() == "Apply Filters":
                        child.setText(self.translator.t("statistics:apply_filters"))

            # Update time range selector
            if hasattr(self, 'time_range_selector'):
                for child in self.time_range_selector.findChildren(QLabel):
                    if child.text() == "Time Range:":
                        child.setText(self.translator.t("statistics:time_range"))
                    elif child.text() == "to":
                        child.setText(self.translator.t("statistics:to"))

                # Update apply button
                for child in self.time_range_selector.findChildren(QPushButton):
                    if child.text() == "Apply":
                        child.setText(self.translator.t("statistics:apply"))

            # Update table headers
            self._update_table_headers(self.valuable_table)
            self._update_table_headers(self.category_table)
            self._update_table_headers(self.brand_table)
            self._update_table_headers(self.low_stock_table)

            # Update status labels
            if self.status_label.text() == "Ready":
                self.status_label.setText(self.translator.t("statistics:ready"))

            # Update "Last updated" label if it contains text
            if self.last_updated_label.text() and self.last_updated_label.text().startswith("Last updated:"):
                timestamp = self.last_updated_label.text().split(": ")[1]
                self.last_updated_label.setText(f"{self.translator.t('statistics:last_updated')} {timestamp}")

        except Exception as e:
            logger.error(f"Error updating translations: {e}")

    def _update_table_headers(self, table):
        """Update table headers with translations"""
        if not table:
            return

        column_count = table.columnCount()
        for i in range(column_count):
            header_text = table.horizontalHeaderItem(i).text()

            # Map header text to translation keys
            translation_key = None
            if header_text == "Part Name":
                translation_key = "statistics:part_name"
            elif header_text == "Category":
                translation_key = "statistics:category"
            elif header_text == "Price":
                translation_key = "statistics:price"
            elif header_text == "Quantity":
                translation_key = "statistics:quantity"
            elif header_text == "Total Value":
                translation_key = "statistics:total_value_column"
            elif header_text == "Value":
                translation_key = "statistics:value_column"
            elif header_text == "Compatible Brands":
                translation_key = "statistics:compatible_brands"

            if translation_key:
                table.setHorizontalHeaderItem(i, QTableWidgetItem(self.translator.t(translation_key)))

