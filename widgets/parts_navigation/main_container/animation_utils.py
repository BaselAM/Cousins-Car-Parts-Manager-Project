"""
Animation utilities for the parts navigation system.
"""
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QTimer


def animate_fade_transition(from_widget, to_widget, stack_widget, to_index):
    """
    Animate a fade transition between two widgets.

    Args:
        from_widget: The source widget
        to_widget: The destination widget
        stack_widget: The QStackedWidget containing the widgets
        to_index: The index to change to

    Returns:
        bool: True if animation started, False otherwise
    """
    if not from_widget or not to_widget:
        return False

    # Set up fade out animation for current widget
    fade_out = QPropertyAnimation(from_widget, b"windowOpacity")
    fade_out.setDuration(150)  # Short duration for a subtle effect
    fade_out.setStartValue(1.0)
    fade_out.setEndValue(0.0)
    fade_out.setEasingCurve(QEasingCurve.OutQuad)

    # Set up fade in animation for next widget
    fade_in = QPropertyAnimation(to_widget, b"windowOpacity")
    fade_in.setDuration(150)
    fade_in.setStartValue(0.0)
    fade_in.setEndValue(1.0)
    fade_in.setEasingCurve(QEasingCurve.InQuad)

    # Connect signals to handle the actual widget change
    fade_out.finished.connect(lambda: stack_widget.setCurrentIndex(to_index))

    # Start with fade out
    to_widget.setWindowOpacity(0.0)
    fade_out.start()

    # Start fade in after a short delay
    QTimer.singleShot(75, lambda: fade_in.start())

    return True