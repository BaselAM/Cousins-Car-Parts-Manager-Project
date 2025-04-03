"""
Premium step connector for elegant navigation.
Features sophisticated animations and visual treatments.
Enhanced for better visibility and theme integration.
"""
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect, QSizePolicy)
from PyQt5.QtCore import (Qt, QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
                          QSequentialAnimationGroup, pyqtProperty, QSize)
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QLinearGradient

from themes import get_color

class PremiumStepConnector(QFrame):
    """A premium connector between step indicators with elegant animations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("premiumStepConnector")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(6)  # Slightly taller for more elegant appearance

        # Progress tracking (0.0 to 1.0)
        self._progress = 0.0
        self._is_completed = False
        self._animation = None

        # Create a container for better layout control
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """Set up the UI components for a premium look with better visibility."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Base track (shown always)
        self.track = QFrame()
        self.track.setObjectName("connectorTrack")
        self.track.setFixedHeight(2)  # Thinner track for elegant appearance

        # Progress overlay (grows as step is completed)
        self.progress_overlay = QFrame()
        self.progress_overlay.setObjectName("connectorProgress")
        self.progress_overlay.setFixedHeight(2)  # Same as track
        self.progress_overlay.setMaximumWidth(0)  # Initially hidden

        # Add both to layout
        layout.addWidget(self.track, 1)  # Takes all space

        # We'll handle the overlay with absolute positioning for animation
        self.progress_overlay.setParent(self)
        self.progress_overlay.move(0, 2)  # Center vertically

    def apply_theme(self):
        """Apply theme styling with proper color integration."""
        # Get theme colors with fallbacks
        highlight = get_color('highlight', '#4299E1')
        border_color = get_color('border', '#2C5282')

        # Calculate variation colors
        highlight_lighter = QColor(highlight).lighter(115).name()

        # Apply styling with theme colors
        self.setStyleSheet(f"""
            #connectorTrack {{
                background-color: {border_color};
                border-radius: 1px;
            }}
            
            #connectorProgress {{
                background-color: {highlight};
                border-radius: 1px;
            }}
        """)

    def set_completed(self, completed, animate=True):
        """Set the completed state with an elegant animation."""
        # Store previous state
        was_completed = self._is_completed
        self._is_completed = completed

        # If state changed and animation requested
        if was_completed != completed and animate:
            self.animate_progress(1.0 if completed else 0.0)
        else:
            # Instant update
            self._progress = 1.0 if completed else 0.0
            self.update_progress()

    def animate_progress(self, target_progress, duration=500):
        """Animate the progress with a sophisticated animation."""
        # Cancel any running animation
        if self._animation and self._animation.state() == QPropertyAnimation.Running:
            self._animation.stop()

        # Create animation
        self._animation = QPropertyAnimation(self, b"progress")
        self._animation.setDuration(duration)
        self._animation.setStartValue(self._progress)
        self._animation.setEndValue(target_progress)

        # Use a subtle ease curve for premium feel
        self._animation.setEasingCurve(QEasingCurve.OutQuart)

        # Start animation
        self._animation.start()

    def update_progress(self):
        """Update the visual progress indicator with improved visibility."""
        # Calculate width based on progress
        progress_width = int(self.width() * self._progress)

        # Update overlay width
        self.progress_overlay.setFixedWidth(progress_width)

        # Update overlay position (always centered vertically)
        self.progress_overlay.move(0, 2)

    def _get_progress(self):
        return self._progress

    def _set_progress(self, progress):
        if self._progress != progress:
            self._progress = progress
            self.update_progress()

    # Property for animation
    progress = pyqtProperty(float, _get_progress, _set_progress)

    def resizeEvent(self, event):
        """Handle resize events to keep progress accurate."""
        super().resizeEvent(event)
        self.update_progress()

    def sizeHint(self):
        """Return the preferred size with appropriate dimensions."""
        return QSize(30, 6)  # Minimum width, fixed height

    def paintEvent(self, event):
        """Custom paint for premium appearance with improved visual quality."""
        # Let the base class handle the basic painting
        super().paintEvent(event)

        # Get theme colors for custom painting
        highlight = get_color('highlight', '#4299E1')
        border_color = get_color('border', '#2C5282')

        # Create a painter for custom effects
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        # Add subtle highlight at the top edge for 3D effect
        highlight_pen = QPen(QColor(255, 255, 255, 20))  # Very subtle highlight
        highlight_pen.setWidth(1)
        painter.setPen(highlight_pen)
        painter.drawLine(0, 0, self.width(), 0)

        # Optional: Add subtle shadow at bottom for depth
        shadow_pen = QPen(QColor(0, 0, 0, 15))  # Very subtle shadow
        shadow_pen.setWidth(1)
        painter.setPen(shadow_pen)
        painter.drawLine(0, 5, self.width(), 5)