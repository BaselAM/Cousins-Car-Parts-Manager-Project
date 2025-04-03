from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout
from PyQt5.QtGui import (QFont, QFontMetrics, QColor, QPainter, QPainterPath,
                         QLinearGradient, QRadialGradient, QPen, QBrush)

from themes import get_color, get_size, get_font_size
from size_policy import SizePolicyMixin, ResponsiveFontMixin


class ExquisiteTitleLabel(QWidget, ResponsiveFontMixin):
    """
    Ultra-premium title with advanced visual effects and meticulous styling.
    """

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator

        # Keep original dimensions - don't change them
        self.setMinimumHeight(get_size("xxlarge"))
        self.setMinimumWidth(get_size("button_min_width") * 2)

        # Create premium typography
        self.font_primary = QFont("Arial", get_font_size("header"))
        self.font_primary.setWeight(QFont.Black)
        self.font_primary.setLetterSpacing(QFont.AbsoluteSpacing, 3)  # Expansive spacing

        # Visual effect properties
        self.glow_opacity = 15  # Subtle glow effect
        self.shadow_offset = 2  # Slightly deeper shadow for dimension
        self.hover_active = False

        # Track state for visual effects
        self.setMouseTracking(True)

        # Update text initially
        self.update_text()

    def update_text(self):
        """Update the title text based on current language"""
        try:
            if getattr(self.translator, 'language', 'en') == 'he':
                self.text = self.translator.t('app_title_1')
                # Right-to-left layout
                self.setLayoutDirection(Qt.RightToLeft)
            else:
                self.text = self.translator.t('app_title_1').upper()  # All caps for luxury feel
                self.setLayoutDirection(Qt.LeftToRight)
        except:
            self.text = "ABU MUKH CAR PARTS"
            self.setLayoutDirection(Qt.LeftToRight)

    def resizeEvent(self, event):
        """Handle resizing to adjust the font size"""
        # Adjust font size based on widget height
        base_size = get_font_size("header")
        height = self.height()
        new_size = max(base_size * height / get_size("header_height"), get_font_size("large"))

        self.font_primary.setPointSize(int(new_size))
        super().resizeEvent(event)

    def enterEvent(self, event):
        """Subtle hover effect"""
        self.hover_active = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Reset hover effect"""
        self.hover_active = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        """Premium paint implementation with exquisite details"""
        # Create painter with highest quality settings
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.HighQualityAntialiasing, True)

        # Get base colors from theme
        base_color = self.palette().color(self.foregroundRole())
        bg_color = self.palette().color(self.backgroundRole())

        # Create refined font metrics
        painter.setFont(self.font_primary)
        fm = QFontMetrics(self.font_primary)

        # Calculate precise text dimensions
        text_width = fm.horizontalAdvance(self.text) if hasattr(fm,
                                                                'horizontalAdvance') else fm.width(
            self.text)
        text_height = fm.height()

        # IMPORTANT CHANGE: Position the text higher in the available space
        # Instead of centering (50%), we position at 40% of the height
        x = (self.width() - text_width) / 2
        y = (self.height() * 0.4) + (text_height * 0.3)  # Move text upward

        # Create refined text path for advanced effects
        text_path = QPainterPath()
        text_path.addText(x, y, self.font_primary, self.text)

        # Draw subtle background glow if hovered (ultra-subtle effect)
        if self.hover_active:
            glow = QRadialGradient(self.width() / 2, self.height() / 2, self.width() / 2)
            glow_color = QColor(base_color)
            glow_color.setAlpha(5)  # Almost imperceptible
            glow.setColorAt(0, glow_color)
            glow_color.setAlpha(0)
            glow.setColorAt(1, glow_color)
            painter.fillRect(self.rect(), glow)

        # Draw multi-layered shadows for depth (3 layers with decreasing opacity)
        for i in range(3):
            shadow_color = QColor(0, 0, 0, 40 - (i * 10))  # Decreasing opacity
            offset = self.shadow_offset - (i * 0.5)  # Decreasing offset
            shadow_path = QPainterPath(text_path)
            shadow_path.translate(offset, offset)
            painter.fillPath(shadow_path, shadow_color)

        # Draw main text with subtle gradient effect
        text_gradient = QLinearGradient(x, y - text_height, x, y)
        brightness = 100 if self.hover_active else 0  # Subtle brightening on hover

        # Create elegant gradient effect
        main_color = QColor(base_color)
        highlight_color = QColor(base_color).lighter(105 + brightness)

        text_gradient.setColorAt(0, highlight_color)
        text_gradient.setColorAt(1, main_color)

        # Apply gradient to text
        painter.fillPath(text_path, QBrush(text_gradient))

        # Draw ultra-thin outline for definition (0.5px equivalent)
        outline_pen = QPen(QColor(base_color).darker(110))
        outline_pen.setWidthF(0.5)
        painter.strokePath(text_path, outline_pen)

        # Optional: Draw subtle accent lines for luxury branding
        accent_color = QColor(base_color)
        accent_color.setAlpha(40)
        accent_pen = QPen(accent_color)
        accent_pen.setWidthF(1)

        # Draw two thin accent lines - also repositioned higher
        line_width = min(text_width + 100, self.width() - 60)

        # Position the lines relative to the repositioned text
        line_y_top = y - text_height - 5
        line_y_bottom = y + 8  # Closer to text

        # Calculate line positions
        line_x_start = (self.width() - line_width) / 2
        line_x_end = line_x_start + line_width

        # Draw top decorative line
        painter.setPen(accent_pen)
        painter.drawLine(line_x_start, line_y_top, line_x_end, line_y_top)

        # Draw bottom decorative line
        painter.drawLine(line_x_start, line_y_bottom, line_x_end, line_y_bottom)

    def update_translations(self):
        """Handle language changes with refined update"""
        self.update_text()
        self.update()


class HeaderWidget(QWidget, SizePolicyMixin):
    """Refined luxury header for the application"""

    def __init__(self, translator, home_callback=None, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.home_callback = home_callback
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        # Create layout with improved vertical alignment
        layout = QHBoxLayout(self)

        # Adjust margins to position title closer to the top
        # Reduce bottom margin to position title higher in the header
        layout.setContentsMargins(
            get_size("spacing_large"),  # left margin
            get_size("spacing_medium") - 5,  # reduced top margin to move title up
            get_size("spacing_large"),  # right margin
            get_size("spacing_medium") + 10  # increased bottom margin for more space
        )

        # Add title to layout (removed setAlignment call)
        self.title_label = ExquisiteTitleLabel(self.translator, self)
        layout.addWidget(self.title_label)

    def paintEvent(self, event):
        """Enhanced header background with subtle gradient"""
        super().paintEvent(event)
        # Background will be handled by stylesheet and theme

    def apply_theme(self):
        header_bg = get_color('header')
        text_color = get_color('text')
        highlight_color = get_color('highlight')

        # Determine if using dark theme for effect adjustments
        is_dark_theme = QColor(header_bg).lightness() < 128

        # Create subtle border effect for separation
        border_color = QColor(text_color)
        border_color.setAlpha(30)  # Very subtle

        # Apply modern styling to the header with gradient effect
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 {header_bg}, 
                                          stop:1 {QColor(header_bg).darker(110).name()});
                color: {text_color};
                border-bottom: 1px solid rgba({border_color.red()}, {border_color.green()}, {border_color.blue()}, 0.3);
            }}
        """)

    def update_translations(self):
        # Update the title for language change
        self.title_label.update_translations()


class CopyrightWidget(QWidget, SizePolicyMixin):
    """A small copyright notice at the bottom of the application"""

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, get_size("spacing_tiny"), 0, get_size("spacing_tiny"))

        self.copyright_label = QLabel(self.translator.t("copyright"))
        self.copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.copyright_label)

        # Set copyright height using size policy
        self.set_fixed_height_policy("copyright_height")

        # Set object name to make it easy to find
        self.setObjectName("copyrightWidget")

    def apply_theme(self):
        bg_color = get_color('background')
        text_color = get_color('text')

        # Make copyright more elegant with direct style application
        stylesheet = f"""
            background-color: {bg_color};
            color: {text_color};
        """
        self.setStyleSheet(stylesheet)

        # Update label directly with no intermediate stylesheet
        label_color = QColor(text_color).lighter(150).name() if QColor(bg_color).lightness() < 128 else QColor(
            text_color).darker(150).name()
        self.copyright_label.setStyleSheet(f"""
            font-size: {get_font_size("small")}pt;
            color: {label_color};
            font-style: italic;
        """)

        # Force immediate repaint
        self.update()

    def update_translations(self):
        self.copyright_label.setText(self.translator.t("copyright"))