"""Size policy mixins for consistent widget sizing."""
from PyQt5.QtWidgets import QSizePolicy
from PyQt5.QtCore import QSize, QEvent
from PyQt5.QtGui import QFontMetrics, QFont
from themes import get_size, get_font_size, get_base_unit


class SizePolicyMixin:
    """Mixin to provide consistent size policies for widgets."""

    def set_expanding_policy(self):
        """Set widget to expand in both directions."""
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_fixed_height_policy(self, height_key=None):
        """Set widget to have a fixed height but expand horizontally.

        Args:
            height_key (str, optional): Size key from themes.SIZE. If None, height is not set.
        """
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        if height_key:
            self.setFixedHeight(get_size(height_key))

    def set_fixed_width_policy(self, width_key=None):
        """Set widget to have a fixed width but expand vertically.

        Args:
            width_key (str, optional): Size key from themes.SIZE. If None, width is not set.
        """
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        if width_key:
            self.setFixedWidth(get_size(width_key))

    def set_preferred_policy(self):
        """Set widget to prefer its sizeHint but can still be resized."""
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def set_minimum_expanding_policy(self):
        """Set widget to have no maximum size, but respect minimum size."""
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

    def set_button_size_policy(self):
        """Set size policy specifically for buttons."""
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    def set_responsive_size_constraints(self, min_width_key=None, min_height_key=None,
                                        max_width_key=None, max_height_key=None):
        """Set minimum and maximum size constraints.

        Args:
            min_width_key (str, optional): Size key for minimum width
            min_height_key (str, optional): Size key for minimum height
            max_width_key (str, optional): Size key for maximum width
            max_height_key (str, optional): Size key for maximum height
        """
        if min_width_key:
            self.setMinimumWidth(get_size(min_width_key))
        if min_height_key:
            self.setMinimumHeight(get_size(min_height_key))
        if max_width_key:
            self.setMaximumWidth(get_size(max_width_key))
        if max_height_key:
            self.setMaximumHeight(get_size(max_height_key))

    def calculate_responsive_font_size(self, base_size_key="regular", min_size=8, max_size=48):
        """Calculate a font size based on widget height.

        Args:
            base_size_key (str): Key for base font size
            min_size (int): Minimum font size
            max_size (int): Maximum font size

        Returns:
            int: Calculated font size
        """
        base_size = get_font_size(base_size_key)
        height = self.height()

        # Calculate a responsive font size based on widget height
        # Using a simple scale factor: height / 10 as a heuristic
        calculated_size = int(height / 10)

        # Ensure it stays within min and max bounds
        return max(min_size, min(calculated_size, max_size, base_size * 2))


# The ResponsiveFontMixin class should be updated in the size_policy.py file
# Based on the imports in your files, this is where the class is defined

# Here's how the file structure should look:

# size_policy.py
#  |- SizePolicyMixin class
#  |- ResponsiveFontMixin class (update this with the provided code)

# Complete replacement for ResponsiveFontMixin in size_policy.py:

class ResponsiveFontMixin:
    """
    Enhanced mixin that provides responsive font sizing with improved constraints
    to ensure elegance at all window sizes.
    """

    def set_responsive_font(self, size_key="regular", weight=QFont.Normal, max_point_size=None):
        """
        Set up a responsive font with maximum size constraints to prevent
        excessive growth on large screens.

        Args:
            size_key: Theme size key or direct point size
            weight: Font weight (e.g., QFont.Bold)
            max_point_size: Maximum point size to prevent excessive scaling
        """
        try:
            # Get initial size from theme if it's a string key
            if isinstance(size_key, str):
                initial_size = get_font_size(size_key)
            else:
                initial_size = size_key

            # Store the base size for proportional calculations
            self._base_font_size = initial_size
            self._max_font_size = max_point_size or initial_size * 1.5

            # Create font with initial settings
            font = QFont()
            font.setPointSize(initial_size)
            font.setWeight(weight)

            # Apply the font
            self.setFont(font)

            # Install filter if not already done
            if not hasattr(self, "_font_event_filter_installed"):
                self.installEventFilter(self)
                self._font_event_filter_installed = True

        except Exception as e:
            print(f"Error setting responsive font: {str(e)}")

    def adjust_font_size_to_width(self, width, min_size=8, max_size=None, base_width=200):
        """
        Adjust font size based on width with improved constraints.
        Uses a logarithmic growth curve to slow down font size increases.

        Args:
            width: Current width
            min_size: Minimum font size
            max_size: Maximum font size
            base_width: Reference width for scaling
        """
        try:
            # If no max size specified, use the stored maximum
            if max_size is None:
                max_size = getattr(self, "_max_font_size", 16)

            # Calculate size using progressive scaling (logarithmic growth)
            # This provides more gradual size increases as width grows
            if width <= base_width:
                # Linear scaling for small sizes
                ratio = width / base_width
                new_size = self._base_font_size * ratio
            else:
                # Logarithmic scaling for larger sizes to slow growth
                excess_width = width - base_width
                import math  # Import math for logarithm
                log_factor = 1 + (math.log(1 + excess_width / base_width) * 0.5)
                new_size = self._base_font_size * log_factor

            # Apply constraints
            new_size = max(min_size, min(new_size, max_size))

            # Update font if size changed significantly (avoid constant updates)
            current_size = self.font().pointSize()
            if abs(current_size - new_size) >= 0.5:  # Only update if change is notable
                font = self.font()
                font.setPointSize(int(new_size))
                self.setFont(font)

        except Exception as e:
            print(f"Error adjusting font size: {str(e)}")

    def eventFilter(self, obj, event):
        """Handle resize events to adjust font size proportionally."""
        # Only process if this is for the current object and it's a resize event
        if obj == self and event.type() == QEvent.Resize:
            # Different handling based on widget type
            if hasattr(self, 'width'):
                # For regular widgets like buttons
                self.adjust_font_size_to_width(self.width())
            elif hasattr(self, 'viewport') and hasattr(self.viewport(), 'width'):
                # For scroll areas and similar
                self.adjust_font_size_to_width(self.viewport().width())

        # Pass event to base implementation
        return False  # Don't consume the event