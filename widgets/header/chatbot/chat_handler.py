"""
Chat signal handler for managing chat widget signals.

This module provides a signal proxy that connects chat widget signals
to your application, enabling direct communication between the chat interface
and the main application logic.
"""

from PyQt5.QtCore import QObject, pyqtSignal

class ChatSignalBlocker(QObject):
    """
    Signal proxy for chat widget signals.

    This class bridges the DirectChatWidget signals to your application,
    allowing for central management of chat messages.

    Note: Despite the historical name "Blocker", this class no longer blocks
    any signals and simply passes them through directly.
    """
    # Signal that gets emitted when a chat message is submitted
    chat_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        """Initialize the signal proxy."""
        super().__init__(parent)

    def connect_chat_widget(self, chat_widget):
        """
        Connect to a chat widget's signals.

        Args:
            chat_widget: The DirectChatWidget instance to connect to
        """
        # Direct connection to pass through signals without any blocking
        if hasattr(chat_widget, 'chat_submitted'):
            chat_widget.chat_submitted.connect(self.chat_submitted)

        # Also connect to message_sent for compatibility with older implementations
        if hasattr(chat_widget, 'message_sent'):
            chat_widget.message_sent.connect(self.chat_submitted)

    def handle_chat_message(self, message):
        """
        Forward chat message to application.

        Legacy method that just emits the received message.

        Args:
            message: The chat message text
        """
        # Simply forward the message
        self.chat_submitted.emit(message)