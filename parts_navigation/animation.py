"""
Animation utilities for the parts navigation system.

This module provides reusable animation functions for creating
smooth, premium transitions throughout the application.
"""
from PyQt5.QtCore import (QPropertyAnimation, QEasingCurve, QParallelAnimationGroup,
                          QSequentialAnimationGroup, QTimer)
from PyQt5.QtWidgets import QGraphicsOpacityEffect


class AnimationManager:
    """
    Manages animations throughout the navigation system.

    Provides consistent, premium animation effects that can be
    reused across the application for a cohesive look and feel.
    """

    @staticmethod
    def fade_transition(from_widget, to_widget, stack_widget, to_index,
                        duration=400, delay=150):  # Increased duration and delay
        """
        Animate a fade transition between two widgets with enhanced smoothness.

        Args:
            from_widget: The source widget
            to_widget: The destination widget
            stack_widget: The QStackedWidget containing the widgets
            to_index: The index to change to
            duration: Animation duration in milliseconds
            delay: Delay between fade out and fade in

        Returns:
            QParallelAnimationGroup: The animation group
        """
        # Create animation group
        animation_group = QParallelAnimationGroup()

        # Store widget references directly on the animation group to prevent GC
        animation_group._from_widget = from_widget
        animation_group._to_widget = to_widget
        animation_group._stack_widget = stack_widget

        # Apply opacity effect to source widget
        from_effect = QGraphicsOpacityEffect(from_widget)
        from_effect.setOpacity(1.0)
        from_widget.setGraphicsEffect(from_effect)

        # Store effect reference to prevent premature GC
        animation_group._from_effect = from_effect

        # Apply opacity effect to destination widget
        to_effect = QGraphicsOpacityEffect(to_widget)
        to_effect.setOpacity(0.0)
        to_widget.setGraphicsEffect(to_effect)

        # Store effect reference to prevent premature GC
        animation_group._to_effect = to_effect

        # Create fade out animation with easing
        fade_out = QPropertyAnimation(from_effect, b"opacity")
        fade_out.setDuration(duration)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.InOutQuad)

        # Store for GC protection
        animation_group._fade_out = fade_out

        # Create safer index change function - no lambda
        def change_index():
            stack_widget.setCurrentIndex(to_index)

        # Connect index change function
        fade_out.finished.connect(change_index)

        # Create fade in animation with easing
        fade_in = QPropertyAnimation(to_effect, b"opacity")
        fade_in.setDuration(duration)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.InOutQuad)

        # Store for GC protection
        animation_group._fade_in = fade_in

        # Add fade out to group
        animation_group.addAnimation(fade_out)

        # Create safer fade-in adder - no lambda
        def add_fade_in():
            animation_group.addAnimation(fade_in)

        # Add fade in after delay
        QTimer.singleShot(delay, add_fade_in)

        # Start animation
        animation_group.start()

        return animation_group

    @staticmethod
    def slide_transition(from_widget, to_widget, stack_widget, to_index,
                         direction='left', duration=300):
        """
        Animate a slide transition between two widgets.

        Args:
            from_widget: The source widget
            to_widget: The destination widget
            stack_widget: The QStackedWidget containing the widgets
            to_index: The index to change to
            direction: Slide direction ('left', 'right', 'up', 'down')
            duration: Animation duration in milliseconds

        Returns:
            QParallelAnimationGroup: The animation group
        """
        # Will be implemented for the full animation class
        pass

    @staticmethod
    def fade_widget(widget, start_value, end_value, duration=250,
                    easing=QEasingCurve.InOutQuad):
        """
        Fade a widget in or out.

        Args:
            widget: The widget to animate
            start_value: Starting opacity (0.0 to 1.0)
            end_value: Ending opacity (0.0 to 1.0)
            duration: Animation duration in milliseconds
            easing: Easing curve to use

        Returns:
            QPropertyAnimation: The animation object
        """
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)
        effect.setOpacity(start_value)

        animation = QPropertyAnimation(effect, b"opacity")
        animation.setStartValue(start_value)
        animation.setEndValue(end_value)
        animation.setDuration(duration)
        animation.setEasingCurve(easing)

        # Store references to prevent GC
        animation._widget = widget
        animation._effect = effect

        # Define functions instead of lambdas
        def on_fade_out_finished():
            if hasattr(widget, 'hide'):
                widget.hide()

        def on_fade_in_started():
            if hasattr(widget, 'show'):
                widget.show()

        # Hide widget when fade out completes
        if end_value == 0.0:
            animation.finished.connect(on_fade_out_finished)
        elif start_value == 0.0:
            on_fade_in_started()

        animation.start()

        return animation

    @staticmethod
    def pulse_widget(widget, scale_factor=1.1, duration=300):
        """
        Create a pulse animation effect on a widget.

        Args:
            widget: The widget to animate
            scale_factor: Maximum scale factor
            duration: Animation duration in milliseconds

        Returns:
            QSequentialAnimationGroup: The animation group
        """
        # Get original size
        original_size = widget.size()

        # Create animation group
        animation_group = QSequentialAnimationGroup()

        # Store widget reference to prevent GC
        animation_group._widget = widget

        # Scale up animation
        scale_up = QPropertyAnimation(widget, b"size")
        scale_up.setDuration(duration // 2)
        scale_up.setStartValue(original_size)
        scale_up.setEndValue(original_size * scale_factor)
        scale_up.setEasingCurve(QEasingCurve.OutQuad)

        # Scale down animation
        scale_down = QPropertyAnimation(widget, b"size")
        scale_down.setDuration(duration // 2)
        scale_down.setStartValue(original_size * scale_factor)
        scale_down.setEndValue(original_size)
        scale_down.setEasingCurve(QEasingCurve.InOutQuad)

        # Store animations to prevent GC
        animation_group._scale_up = scale_up
        animation_group._scale_down = scale_down

        # Add animations to group
        animation_group.addAnimation(scale_up)
        animation_group.addAnimation(scale_down)

        # Start animation
        animation_group.start()

        return animation_group