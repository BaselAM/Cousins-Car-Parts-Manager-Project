"""
Utility functions for the register widget.
"""
from PyQt5.QtWidgets import QSizePolicy


class SizePolicyMixin:
    """A mixin class to set size policies for widgets."""

    def set_fixed_policy(self):
        """Set fixed size policy in both directions."""
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def set_expanding_policy(self):
        """Set expanding size policy in both directions."""
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def set_preferred_policy(self):
        """Set preferred size policy in both directions."""
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)

    def set_vertical_expanding_policy(self):
        """Set expanding size policy in vertical direction."""
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

    def set_horizontal_expanding_policy(self):
        """Set expanding size policy in horizontal direction."""
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


class ResponsiveFontMixin:
    """A mixin class to handle responsive font sizes."""

    def set_responsive_font_size(self, base_size, min_size=8, max_size=24):
        """Set a font size that can scale based on widget size.

        Args:
            base_size (int): The base font size
            min_size (int): Minimum font size
            max_size (int): Maximum font size
        """
        font = self.font()

        # Start with the base size
        adjusted_size = base_size

        # Apply constraints
        adjusted_size = max(min_size, min(adjusted_size, max_size))

        # Set the font size
        font.setPointSize(adjusted_size)
        self.setFont(font)