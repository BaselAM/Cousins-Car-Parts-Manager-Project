"""
Main chat widget with resilient design that works with or without API access.
"""

import os
import threading
import time
from pathlib import Path

from PyQt5.QtCore import pyqtSignal, QSize, QPoint, QTimer, Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QToolButton, QFrame,
    QScrollArea, QLabel, QLineEdit, QPushButton, QApplication,
    QMessageBox, QGraphicsDropShadowEffect, QDialog
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor

# Import the logger system
from logger import get_logger
from .utils import is_dark_theme, SignalBridge
from .api_key_manager import ApiKeyManager
from .car_knowledge_base import CarPartsKnowledgeBase
from .openai_client import OpenAIChat
from .settings_dialog import ChatSettingsDialog

# Get a logger instance for this module
logger = get_logger(__name__)


class DirectChatWidget(QWidget):
    """Chat widget with resilient design for car parts information"""

    # Signal for notifying when a chat message is submitted
    chat_submitted = pyqtSignal(str)

    def __init__(self, translator=None, parent=None):
        """Initialize the chat widget with optional translator"""
        super().__init__(parent)
        self.translator = translator

        # Debugging info
        logger.debug("Initializing DirectChatWidget with car knowledge and resilient design")

        # State variables
        self.chat_visible = False
        self.is_expanded = False

        # Create signal bridge for cross-thread communication
        self.signal_bridge = SignalBridge()
        self.signal_bridge.update_signal.connect(self._add_message_safe)
        self.signal_bridge.remove_thinking_signal.connect(self._remove_thinking_safe)
        self.signal_bridge.api_error_signal.connect(self._show_api_error)

        # Get username from environment or use default
        self.username = os.environ.get('USERNAME', os.environ.get('USER', 'User'))
        logger.debug(f"Username: {self.username}")

        # Initialize API key manager
        self.key_manager = ApiKeyManager()

        # Load API key if available
        api_key = self.key_manager.load_api_key()

        # Initialize OpenAI Chat client with fallback capability
        self.openai_chat = OpenAIChat(api_key)

        # Setup UI
        self.setup_ui()

        # Reference to thinking bubble for removal
        self.thinking_label = None

    def setup_ui(self):
        """Create the chat UI components"""
        logger.debug("Setting up UI components")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create chat button with modern styling
        self.chat_btn = QToolButton()
        self.chat_btn.setCursor(Qt.PointingHandCursor)
        self.chat_btn.setToolTip("Chat")
        self.chat_btn.clicked.connect(self.toggle_chat)

        # Try different locations for the chat icon
        # Try different locations for the chat icon
        icon_locations = [
            # Look for chat_icon.png first (your new icon)
            Path(__file__).resolve().parent / "resources" / "chat_icon.png",
            Path(__file__).resolve().parent.parent / "resources" / "chat_icon.png",
            Path(__file__).resolve().parent.parent.parent / "resources" / "chat_icon.png",
            # Then fall back to original paths if needed
            Path(__file__).resolve().parent / "resources" / "chatbot.png",
            Path(__file__).resolve().parent.parent / "resources" / "chatbot.png",
            Path(__file__).resolve().parent.parent.parent / "resources" / "chatbot.png",
        ]

        icon_found = False
        chat_icon_path = None  # Initialize the variable outside the loop
        for icon_path in icon_locations:
            if icon_path.exists():
                logger.debug(f"Using chat icon from: {icon_path}")
                self.chat_btn.setIcon(QIcon(str(icon_path)))
                self.chat_btn.setIconSize(QSize(26, 26))
                icon_found = True
                chat_icon_path = icon_path  # Store the path for later use
                break

        if not icon_found:
            logger.warning("Chat icon not found, using text emoji")
            self.chat_btn.setText("💬")
            self.chat_btn.setToolButtonStyle(Qt.ToolButtonTextOnly)

        # Make button appropriately sized
        self.chat_btn.setMinimumSize(40, 40)

        # Create chat container with popup behavior
        self.chat_container = QFrame()
        self.chat_container.setObjectName("chatContainer")
        self.chat_container.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.chat_container.setAttribute(Qt.WA_TranslucentBackground)

        # Add shadow to the container
        container_shadow = QGraphicsDropShadowEffect()
        container_shadow.setBlurRadius(20)
        container_shadow.setOffset(0, 4)
        container_shadow.setColor(QColor(0, 0, 0, 40))
        self.chat_container.setGraphicsEffect(container_shadow)

        # Container layout
        container_layout = QVBoxLayout(self.chat_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        # Inner content frame
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")

        # Content layout
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Chat header with title and buttons
        header_container = QWidget()
        header_container.setObjectName("chatHeader")
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(15, 10, 15, 10)

        # Add avatar in header
        header_avatar = QLabel()
        if icon_found and chat_icon_path:
            avatar_pixmap = QPixmap(str(chat_icon_path)).scaled(22, 22,
                                                                Qt.KeepAspectRatio,
                                                                Qt.SmoothTransformation)
            header_avatar.setPixmap(avatar_pixmap)

        chat_title = QLabel("Car Assistant")
        font = QFont("Segoe UI", 11)
        font.setBold(True)
        chat_title.setFont(font)
        chat_title.setObjectName("chatTitle")

        # Settings button
        self.settings_btn = QToolButton()
        self.settings_btn.setText("⚙")  # Gear icon
        self.settings_btn.setObjectName("configButton")
        self.settings_btn.setToolTip("Chat Settings")
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.clicked.connect(self.show_settings)

        # Expand button
        self.expand_btn = QToolButton()
        self.expand_btn.setText("⤢")  # Unicode expand symbol
        self.expand_btn.setObjectName("expandButton")
        self.expand_btn.setToolTip("Expand chat")
        self.expand_btn.setCursor(Qt.PointingHandCursor)
        self.expand_btn.clicked.connect(self.toggle_expand)

        # Close button
        close_btn = QToolButton()
        close_btn.setText("✕")
        close_btn.setObjectName("closeButton")
        close_btn.setToolTip("Close")
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.toggle_chat)

        # Add header elements
        header_layout.addWidget(header_avatar)
        header_layout.addWidget(chat_title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.settings_btn)
        header_layout.addWidget(self.expand_btn)
        header_layout.addWidget(close_btn)

        # Chat messages area with scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName("chatScroll")
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        # Container for chat messages
        self.messages_container = QWidget()
        self.messages_container.setObjectName("messagesContainer")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setSpacing(12)
        self.messages_layout.setContentsMargins(15, 15, 15, 15)
        self.messages_layout.setAlignment(Qt.AlignTop)

        # Set the container as the widget for the scroll area
        self.scroll_area.setWidget(self.messages_container)

        # Message input area
        input_container = QWidget()
        input_container.setObjectName("inputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)

        self.message_input = QLineEdit()
        self.message_input.setObjectName("messageInput")
        self.message_input.setPlaceholderText("Ask me about car parts...")
        self.message_input.returnPressed.connect(self.send_message)
        self.message_input.setFixedHeight(38)

        send_btn = QPushButton("Send")
        send_btn.setObjectName("sendButton")
        send_btn.setFixedSize(70, 38)
        send_btn.setCursor(Qt.PointingHandCursor)
        send_btn.clicked.connect(self.send_message)

        # Add input elements
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(send_btn)

        # Add everything to content layout
        content_layout.addWidget(header_container)
        content_layout.addWidget(self.scroll_area, 1)
        content_layout.addWidget(input_container)

        # Add content frame to container
        container_layout.addWidget(content_frame)

        # Set fixed size for the popup
        self.chat_container.setFixedWidth(320)
        self.chat_container.setFixedHeight(420)

        # Add button to main layout
        layout.addWidget(self.chat_btn)

        # Apply theme
        self.apply_theme()

        # Add welcome message
        welcome_message = f"Hello {self.username}! I'm your car assistant. Ask me about vehicle parts, maintenance, and common issues. I can help in English or Hebrew!"
        self._add_message_safe(welcome_message, False)

        logger.debug("UI setup complete")

    def show_settings(self, api_issue=False):
        """Show chat settings dialog"""
        logger.debug("Showing chat settings dialog")

        # Use the top-level window as parent to ensure proper centering
        current_key = self.openai_chat.api_key
        # Find the main window/parent
        parent_window = None
        parent = self.parent()
        while parent:
            parent_window = parent
            parent = parent.parent()

        dialog = ChatSettingsDialog(parent_window, current_key, api_issue)

        if dialog.exec_() == QDialog.Accepted:
            new_key = dialog.api_key
            use_fallback = dialog.use_fallback_mode

            if use_fallback:
                # User chose local mode
                self.key_manager.delete_api_key()
                self.openai_chat.use_fallback_mode = True
                logger.info("Using local car knowledge base (no API)")
                self._add_message_safe(
                    "Using built-in car knowledge base for assistance!", False)
            else:
                # User chose API mode
                if new_key:
                    self.key_manager.save_api_key(new_key)
                    self.openai_chat.setup_client(new_key)
                    logger.info("Using OpenAI API mode")
                    self._add_message_safe("OpenAI API mode activated.", False)
                else:
                    # No key provided but API mode selected
                    self._add_message_safe("Please provide an API key to use API mode.",
                                           False)
                    self.openai_chat.use_fallback_mode = True

    def send_message(self):
        """Send a message and process response"""
        logger.debug("send_message called")

        # Get message text
        message = self.message_input.text().strip()
        if not message:
            return

        logger.debug(f"Message to process: {message}")

        # Emit signal for external listeners
        self.chat_submitted.emit(message)

        # Add user message to UI
        self._add_message_safe(message, True)

        # Clear input field
        self.message_input.clear()

        # Show thinking indicator
        self._add_thinking_indicator()

        # Process in separate thread
        def process_message():
            try:
                # Get response using car knowledge base or OpenAI
                logger.debug("Getting response")
                response = self.openai_chat.get_response(message)
                logger.debug(f"Received response: {response}")

                # Remove thinking indicator and add response
                self.signal_bridge.remove_thinking_signal.emit()
                time.sleep(0.1)  # Small delay for UI update
                self.signal_bridge.update_signal.emit(response, False)

            except Exception as e:
                logger.error(f"Error generating response: {e}")
                error_message = str(e)

                # Remove thinking indicator
                self.signal_bridge.remove_thinking_signal.emit()
                time.sleep(0.1)

                # Check for API-related errors
                if any(term in error_message.lower() for term in ['quota', 'rate limit', 'capacity', 'exceeded']):
                    error_type = 'api_issue'
                    # Switch to fallback mode
                    self.openai_chat.use_fallback_mode = True

                    # Get fallback response
                    fallback = self.openai_chat.fallback.get_response(message)

                    # Show dialog about API issue (only once)
                    self.signal_bridge.api_error_signal.emit(error_message, error_type)

                    # Add explanatory message first, then the response
                    self.signal_bridge.update_signal.emit(
                        "I've switched to using the built-in car knowledge base due to API issues:", False
                    )
                    time.sleep(0.1)
                    self.signal_bridge.update_signal.emit(fallback, False)

                else:
                    # General error
                    self.signal_bridge.api_error_signal.emit(error_message, "general_error")

                    # Add fallback response to chat
                    fallback = self.openai_chat.fallback.get_response(message)
                    self.signal_bridge.update_signal.emit(fallback, False)

        # Start processing thread
        threading.Thread(target=process_message, daemon=True).start()
        logger.debug("Started processing thread")

    def _show_api_error(self, error_message, error_type):
        """Show API error message and handle based on type"""
        logger.error(f"API error: {error_message} (type: {error_type})")

        # For API quota/rate limit issues
        if error_type == 'api_issue':
            # Only show the settings dialog once per session for API issues
            if not self.openai_chat.use_fallback_mode:
                self.show_settings(api_issue=True)
        else:
            # For other errors, just show a simple message box
            QMessageBox.warning(
                self,
                "Chat Error",
                f"Error: {error_message}\n\nUsing built-in responses instead."
            )

    def _add_thinking_indicator(self):
        """Add a thinking indicator to the chat"""
        logger.debug("Adding thinking indicator")
        self.signal_bridge.update_signal.emit("Thinking...", False)

    def _add_message_safe(self, message, is_user):
        """Add a message to the chat from the main UI thread"""
        logger.debug(f"Adding {'user' if is_user else 'bot'} message safely: {message}")

        # Create message container
        message_frame = QFrame(self.messages_container)
        message_frame.setObjectName("userBubble" if is_user else "botBubble")

        # Layout for the message
        message_layout = QHBoxLayout(message_frame)
        message_layout.setContentsMargins(8, 6, 8, 6)
        message_layout.setSpacing(10)

        # Create label for the message text
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)

        # Set font
        font = QFont("Segoe UI", 10)
        message_label.setFont(font)
        message_label.setMinimumWidth(150)

        # If this is a thinking bubble, store a reference
        if not is_user and message == "Thinking...":
            self.thinking_label = message_frame

        # Layout arrangement based on user/bot
        if is_user:
            message_layout.addStretch(1)
            message_layout.addWidget(message_label)
        else:
            # Avatar for bot
            avatar_label = QLabel()
            # Try the same icon locations
            icon_locations = [
                Path(__file__).resolve().parent / "resources" / "chatbot.png",
                Path(__file__).resolve().parent.parent / "resources" / "chatbot.png",
                Path(__file__).resolve().parent.parent.parent / "resources" / "chatbot.png",
            ]

            icon_found = False
            avatar_path = None  # Initialize variable before loop
            for path in icon_locations:
                if path.exists():
                    avatar_pixmap = QPixmap(str(path)).scaled(22, 22,
                                                             Qt.KeepAspectRatio,
                                                             Qt.SmoothTransformation)
                    avatar_label.setPixmap(avatar_pixmap)
                    icon_found = True
                    avatar_path = path  # Store path if found
                    break

            if not icon_found:
                avatar_label.setText("🤖")

            avatar_label.setFixedSize(22, 22)

            message_layout.addWidget(avatar_label)
            message_layout.addWidget(message_label)
            message_layout.addStretch(1)

        # Apply theme colors
        dark_mode = is_dark_theme()
        if is_user:
            bubble_color = "#2979FF" if dark_mode else "#2962FF"  # Blue
            text_color = "#FFFFFF"  # White
        else:
            bubble_color = "#1E2334" if dark_mode else "#F4F6F8"  # Dark/Light gray
            text_color = "#E0E0FF" if dark_mode else "#36454F"  # Blue-white/Charcoal

        # Apply styles
        message_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bubble_color};
                border-radius: 18px;
            }}
            QLabel {{
                color: {text_color};
                background-color: transparent;
                padding: 4px;
            }}
        """)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 30))
        message_frame.setGraphicsEffect(shadow)

        # Add to layout
        self.messages_layout.addWidget(message_frame)

        # Make the message visible immediately
        message_frame.show()

        # Force update
        self.messages_container.updateGeometry()
        self.messages_container.update()
        QApplication.processEvents()

        # Scroll to bottom
        self.scroll_to_bottom()

        logger.debug(f"Added {'user' if is_user else 'bot'} message to UI")

    def _remove_thinking_safe(self):
        """Remove the thinking indicator from the main UI thread"""
        logger.debug("Removing thinking indicator safely")
        if self.thinking_label:
            self.thinking_label.hide()
            self.thinking_label.deleteLater()
            self.thinking_label = None
            QApplication.processEvents()
            logger.debug("Thinking indicator removed")

    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat"""
        try:
            scrollbar = self.scroll_area.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            logger.debug("Scrolled to bottom")
        except Exception as e:
            logger.error(f"Error scrolling: {e}")

    def toggle_chat(self):
        """Toggle chat visibility"""
        logger.debug("toggle_chat called")

        self.chat_visible = not self.chat_visible

        if self.chat_visible:
            logger.debug("Showing chat window")

            # Position the popup near the button
            btn_global_pos = self.chat_btn.mapToGlobal(QPoint(0, self.chat_btn.height()))

            # Calculate position to make sure it's visible
            screen = QApplication.desktop().screenGeometry()
            x = min(btn_global_pos.x(), screen.width() - self.chat_container.width() - 20)
            x = max(20, x)

            self.chat_container.move(x, btn_global_pos.y() + 5)
            self.chat_container.show()
            self.message_input.setFocus()

            # Ensure we scroll to bottom
            QTimer.singleShot(100, self.scroll_to_bottom)
        else:
            logger.debug("Hiding chat window")
            self.chat_container.hide()

    def toggle_expand(self):
        """Toggle between normal and expanded chat size"""
        self.is_expanded = not self.is_expanded

        if self.is_expanded:
            self.chat_container.setFixedWidth(400)
            self.chat_container.setFixedHeight(500)
            self.expand_btn.setText("⤡")  # Unicode collapse symbol
            self.expand_btn.setToolTip("Collapse chat")
        else:
            self.chat_container.setFixedWidth(320)
            self.chat_container.setFixedHeight(420)
            self.expand_btn.setText("⤢")  # Unicode expand symbol
            self.expand_btn.setToolTip("Expand chat")

        # Ensure we scroll to bottom after resize
        QTimer.singleShot(100, self.scroll_to_bottom)

    def apply_theme(self):
        """Apply modern theme styling"""
        # Determine if we're in dark mode
        dark_mode = is_dark_theme()

        # Define colors
        if dark_mode:
            accent_color = "#2A4B8D"  # Slightly lighter blue for dark theme
            accent_hover = "#5C6BC0"  # Lighter indigo for hover
            button_text = "#FFFFFF"
        else:
            accent_color = "#2A4B8D"  # Slightly lighter blue for light theme
            accent_hover = "#5C6BC0"  # Lighter indigo for hover
            button_text = "#FFFFFF"

        # Get theme colors
        try:
            import themes
            bg_color = themes.get_color('card_bg')
            text_color = themes.get_color('text')
            input_bg = themes.get_color('input_bg')
        except Exception as e:
            logger.error(f"Error getting theme colors: {e}")
            # Fallback colors
            bg_color = "#1E1E1E" if dark_mode else "#FFFFFF"
            text_color = "#FFFFFF" if dark_mode else "#000000"
            input_bg = "#2D2D2D" if dark_mode else "#F0F0F0"

        # Button style
        self.chat_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: transparent;
                border: none;
                padding: 6px;
            }}
            QToolButton:hover {{
                background-color: {accent_color}40;
                border-radius: 20px;
            }}
            QToolButton:pressed {{
                background-color: {accent_color}70;
                border-radius: 20px;
            }}
        """)

        # Container style with additional config button styling
        self.chat_container.setStyleSheet(f"""
            QFrame#chatContainer {{
                background-color: transparent;
                border: none;
            }}

            QFrame#contentFrame {{
                background-color: {bg_color};
                border-radius: 10px;
                border: none;
            }}

            #chatHeader {{
                background-color: {accent_color};
                color: {button_text};
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }}

            #chatTitle {{
                color: {button_text};
                font-weight: bold;
            }}

            #expandButton, #closeButton, #configButton {{
                background-color: transparent;
                color: {button_text};
                border: none;
                padding: 3px;
                border-radius: 4px;
            }}

            #expandButton:hover, #closeButton:hover, #configButton:hover {{
                background-color: {accent_hover};
            }}

            #chatScroll {{
                border: none;
                background-color: transparent;
            }}

            QScrollBar:vertical {{
                background-color: transparent;
                width: 8px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background-color: {accent_color}50;
                min-height: 20px;
                border-radius: 4px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {accent_color}80;
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            #messagesContainer {{
                background-color: transparent;
            }}

            #inputContainer {{
                background-color: {bg_color};
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }}

            #messageInput {{
                background-color: {input_bg};
                color: {text_color};
                border: none;
                border-radius: 19px;
                padding: 8px 15px;
                font-size: 10pt;
            }}

            #messageInput:focus {{
                border: 1px solid {accent_color};
            }}

            #sendButton {{
                background-color: {accent_color};
                color: white;
                border: none;
                border-radius: 19px;
                padding: 5px 10px;
                font-size: 10pt;
                font-weight: bold;
            }}

            #sendButton:hover {{
                background-color: {accent_hover};
            }}
        """)

    def update_translations(self):
        """Update UI translations if translator is available"""
        if self.translator:
            # Update placeholder text and buttons
            self.message_input.setPlaceholderText(
                self.translator.tr("Ask me about car parts...")
            )
            # Update other UI elements as needed

    # Method to support pop-out chat functionality
    def pop_out_chat(self):
        """Future method for pop-out chat functionality"""
        logger.debug("Pop-out chat not implemented")
        pass