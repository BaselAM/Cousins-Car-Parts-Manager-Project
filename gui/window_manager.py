# gui/window_manager.py
from PyQt5.QtCore import QSize, QRect, QTimer
from PyQt5.QtWidgets import QDesktopWidget, QApplication
from themes import get_size
from logger import get_logger

logger = get_logger(__name__)


class GUIWindowManager:
    """
    Manages window properties, geometry, and sizing.
    Responsible for window positioning and responsive size adjustments.
    """

    def __init__(self, parent):
        """
        Initialize the window manager.

        Args:
            parent: The main GUI instance
        """
        self.parent = parent
        # Initialize resize tracking flags
        self._in_resize = False
        self._was_manually_resized = False

    def setup_window_properties(self, translator):
        """
        Configure the main window size and position with improved proportions.
        Ensures exact same distance from both sides of the monitor.

        Args:
            translator: Translator object for window title
        """
        self.parent.setWindowTitle(translator.t("window_title"))

        # Initialize resize tracking flags
        self._in_resize = False
        self._was_manually_resized = False

        # Get available screen geometry
        screen = QDesktopWidget().availableGeometry()

        # Use more generous dimensions as starting size
        width_percent = 0.7
        height_percent = 0.8

        width = int(screen.width() * width_percent)
        height = int(screen.height() * height_percent)

        # Ensure width is an even number to guarantee perfect centering
        if width % 2 != 0:
            width += 1

        # Calculate center position precisely
        x = screen.x() + (screen.width() - width) // 2
        y = screen.y() + (screen.height() - height) // 2

        # Log calculated position details for verification
        logger.debug(f"Screen width: {screen.width()}, Window width: {width}")
        logger.debug(f"Left margin: {x - screen.x()}, Right margin: {screen.width() - (x + width)}")

        # Set the geometry
        self.parent.setGeometry(x, y, width, height)

        # Set reasonable minimum size
        min_width = int(screen.width() * 0.45)
        min_height = int(screen.height() * 0.6)  # Increased from 0.55
        self.parent.setMinimumSize(min_width, min_height)

        # No maximum size - allow fullscreen
        self.parent.setMaximumSize(16777215, 16777215)  # QWidget's maximum size

    def center_window(self):
        """
        Center the window on the screen with exact precision.
        Ensures the window has exactly the same distance from both sides of the monitor.
        """
        # Skip centering if the window was manually resized
        if hasattr(self, '_was_manually_resized') and self._was_manually_resized:
            # Only reset this flag after a significant time has passed (5 seconds)
            if not hasattr(self, '_reset_manual_resize_timer'):
                self._reset_manual_resize_timer = QTimer(self.parent)
                self._reset_manual_resize_timer.setSingleShot(True)
                self._reset_manual_resize_timer.timeout.connect(self._reset_manual_resize_flag)

            self._reset_manual_resize_timer.start(5000)  # 5 seconds
            return

        # Only continue if we're not in a resize event
        if hasattr(self, '_in_resize') and self._in_resize:
            return

        # Get current window size
        window_size = self.parent.size()

        # Get screen geometry
        screen = QDesktopWidget().availableGeometry()

        # Calculate margins
        horizontal_margin = (screen.width() - window_size.width()) // 2
        vertical_margin = (screen.height() - window_size.height()) // 2

        # Create a new position with perfect centering
        new_position = QRect(
            screen.x() + horizontal_margin,
            screen.y() + vertical_margin,
            window_size.width(),
            window_size.height()
        )

        # Apply the new geometry - but only if not maximized or fullscreen
        if not self.parent.isMaximized() and not self.parent.isFullScreen():
            self.parent.setGeometry(new_position)

        # Log the margins for verification
        logger.debug(
            f"Left margin: {horizontal_margin}, Right margin: {screen.width() - (horizontal_margin + window_size.width())}")

    def _reset_manual_resize_flag(self):
        """Reset the manual resize flag to allow centering again"""
        self._was_manually_resized = False

    def optimize_window_size(self):
        """Make final adjustments to window size with improved proportions and exact centering"""
        # Skip if window is maximized or full screen
        if self.parent.isMaximized() or self.parent.isFullScreen():
            return

        # Skip if we're in a resize event
        if hasattr(self, '_in_resize') and self._in_resize:
            return

        # Calculate the optimal height based on content requirements
        optimal_height = self.calculate_optimal_height()

        # Calculate an optimal width that maintains a good aspect ratio
        optimal_width = int(optimal_height * 1.4)  # 1.4:1 aspect ratio is visually pleasing

        # Get current geometry
        current_geo = self.parent.geometry()

        # Get screen constraints
        screen = QDesktopWidget().availableGeometry()

        # Limit to screen bounds (but still allow maximizing)
        optimal_width = min(optimal_width, int(screen.width() * 0.9))

        # Ensure width is an even number for perfect centering
        if optimal_width % 2 != 0:
            optimal_width += 1

        # Calculate the exact center position
        x = screen.x() + (screen.width() - optimal_width) // 2
        y = screen.y() + (screen.height() - optimal_height) // 2

        # Set the new geometry with optimal dimensions and perfect centering
        self.parent.setGeometry(
            x,
            y,
            optimal_width,
            optimal_height
        )

        # Verify exact centering
        left_margin = x - screen.x()
        right_margin = screen.width() - (x + optimal_width)
        logger.debug(f"Window positioned with left margin: {left_margin}px, right margin: {right_margin}px")

        # Store initial optimal size for use in proportional calculations
        if not hasattr(self, 'initial_optimal_size'):
            self.initial_optimal_size = QSize(optimal_width, optimal_height)

    def calculate_optimal_height(self):
        """
        Calculate optimal window height based on content.

        Returns:
            int: The calculated optimal height
        """
        # Get screen constraints
        screen = QDesktopWidget().availableGeometry()

        # Estimate required component heights
        header_height = get_size("header_height")
        top_bar_height = 52
        content_min_height = 550  # Increased for better button visibility
        footer_height = get_size("footer_height")
        copyright_height = get_size("copyright_height")

        # Calculate total height with additional padding
        padding = int(screen.height() * 0.02)  # 2% of screen height for padding

        total_height = (
                header_height +
                top_bar_height +
                content_min_height +
                footer_height +
                copyright_height +
                padding * 2
        )

        # Constrain to reasonable minimum height (60% of screen)
        min_height = int(screen.height() * 0.6)

        # Return the greater of calculated height and minimum height
        # But DON'T restrict the maximum height to allow full-screen
        return max(min_height, total_height)

    def simulate_resize(self):
        """Utility method to test responsive design by simulating window resizing"""
        # Save current size
        current_size = self.parent.size()

        # Test at 80% of current size
        self.parent.resize(int(current_size.width() * 0.8), int(current_size.height() * 0.8))
        self.center_window()  # Re-center after resize
        QApplication.processEvents()

        # Test at 120% of current size
        self.parent.resize(int(current_size.width() * 1.2), int(current_size.height() * 1.2))
        self.center_window()  # Re-center after resize
        QApplication.processEvents()

        # Restore original size
        self.parent.resize(current_size)
        self.center_window()  # Re-center after resize
        QApplication.processEvents()