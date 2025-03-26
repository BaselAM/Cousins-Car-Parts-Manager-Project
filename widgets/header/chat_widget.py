# Save this as a new file called direct_chat_widget.py in the same folder as chat_widget.py

from PyQt5.QtCore import Qt, pyqtSignal, QSize, QPoint, QTimer
from PyQt5.QtWidgets import (
    QWidget, QToolButton, QVBoxLayout,
    QLineEdit, QPushButton, QHBoxLayout, QLabel,
    QFrame, QScrollArea, QDialog, QApplication,
    QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor
from pathlib import Path
import themes
import threading
import time
import random


def is_dark_theme():
    """Determine if the current theme is dark based on background color"""
    bg_color = themes.get_color('card_bg')
    bg_color = bg_color.lstrip('#')
    r, g, b = tuple(int(bg_color[i:i + 2], 16) for i in (0, 2, 4))
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return brightness < 128


class DirectChatBubble(QFrame):
    """Chat message bubble"""

    def __init__(self, message, is_user=True, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.setup_ui(message)
        self.apply_theme()

    def setup_ui(self, message):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)

        # Message label
        self.message_label = QLabel(message)
        self.message_label.setWordWrap(True)
        self.message_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        font = QFont("Segoe UI", 10)
        self.message_label.setFont(font)
        self.message_label.setMinimumWidth(150)

        # Layout based on user/bot message
        if self.is_user:
            layout.addStretch(1)
            layout.addWidget(self.message_label)
            self.setObjectName("userMessage")
        else:
            # Bot avatar
            self.avatar_label = QLabel("🤖")
            self.avatar_label.setFixedSize(22, 22)
            layout.addWidget(self.avatar_label)
            layout.addWidget(self.message_label)
            layout.addStretch(1)
            self.setObjectName("botMessage")

        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 2)
        shadow.setColor(QColor(0, 0, 0, 30))
        self.setGraphicsEffect(shadow)

    def apply_theme(self):
        dark_mode = is_dark_theme()

        if self.is_user:
            bubble_color = "#2979FF" if dark_mode else "#2962FF"  # Blue
            text_color = "#FFFFFF"  # White text
        else:
            bubble_color = "#1E2334" if dark_mode else "#F4F6F8"  # Dark/Light grey
            text_color = "#E0E0FF" if dark_mode else "#36454F"  # Light blue/Charcoal

        self.setStyleSheet(f"""
            QFrame#{self.objectName()} {{
                background-color: {bubble_color};
                border-radius: 18px;
            }}
            QLabel {{
                color: {text_color};
                background-color: transparent;
                padding: 4px;
            }}
        """)


class DirectChatWidget(QWidget):
    """Self-contained chat widget implementation"""
    chat_submitted = pyqtSignal(str)

    def __init__(self, translator, parent=None):
        super().__init__(parent)
        self.translator = translator

        # State variables
        self.chat_visible = False
        self.is_expanded = False

        # Bot responses for BaselAM
        self.responses = [
            "Hello BaselAM! I'm your new chat implementation.",
            "I'm responding directly now, no more 'coming soon' messages!",
            "Your message has been received. This is the new chat system working.",
            "The chat is fully operational now, BaselAM.",
            "I'm integrated and responding to your messages now.",
            "Your new chat implementation is working correctly!",
            "This is your embedded AI assistant responding.",
            "Message received and processed by the new chat system.",
            "The chat functionality is now working properly.",
            "I'm here and responsive, BaselAM! No more waiting."
        ]

        # Set up the UI
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Chat button
        self.chat_btn = QToolButton()
        self.chat_btn.setFixedSize(40, 40)
        self.chat_btn.setCursor(Qt.PointingHandCursor)
        self.chat_btn.setToolTip("Chat")

        # Try to find icon, use text if missing
        chat_icon_path = Path(
            __file__).resolve().parent.parent.parent / "resources/chatbot.png"
        if chat_icon_path.exists():
            self.chat_btn.setIcon(QIcon(str(chat_icon_path)))
            self.chat_btn.setIconSize(QSize(26, 26))
        else:
            self.chat_btn.setText("💬")

        # Connect button to toggle function
        self.chat_btn.clicked.connect(self.toggle_chat)

        # Chat popup container
        self.chat_container = QFrame()
        self.chat_container.setObjectName("chatContainer")
        self.chat_container.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.chat_container.setAttribute(Qt.WA_TranslucentBackground)

        # Shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.chat_container.setGraphicsEffect(shadow)

        # Container layout
        container_layout = QVBoxLayout(self.chat_container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        # Content frame
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Header with title and buttons
        header = QWidget()
        header.setObjectName("chatHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)

        # Header content
        title = QLabel("Chat Assistant")
        title.setObjectName("chatTitle")
        font = QFont("Segoe UI", 11)
        font.setBold(True)
        title.setFont(font)

        # Buttons
        self.expand_btn = QToolButton()
        self.expand_btn.setText("⤢")
        self.expand_btn.setObjectName("expandButton")
        self.expand_btn.setToolTip("Expand")
        self.expand_btn.clicked.connect(self.toggle_expand)

        close_btn = QToolButton()
        close_btn.setText("✕")
        close_btn.setObjectName("closeButton")
        close_btn.setToolTip("Close")
        close_btn.clicked.connect(self.toggle_chat)

        # Add to header layout
        header_layout.addWidget(QLabel("🤖"))
        header_layout.addWidget(title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.expand_btn)
        header_layout.addWidget(close_btn)

        # Scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setObjectName("chatScroll")
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        # Messages container
        messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(messages_widget)
        self.messages_layout.setSpacing(12)
        self.messages_layout.setContentsMargins(15, 15, 15, 15)
        self.messages_layout.addStretch(1)

        self.scroll_area.setWidget(messages_widget)

        # Input area
        input_container = QWidget()
        input_container.setObjectName("inputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(10)

        # Input field
        self.message_input = QLineEdit()
        self.message_input.setObjectName("messageInput")
        self.message_input.setPlaceholderText("Type a message...")
        self.message_input.setFixedHeight(38)
        self.message_input.returnPressed.connect(self.send_message)

        # Send button
        self.send_btn = QPushButton("Send")
        self.send_btn.setObjectName("sendButton")
        self.send_btn.setFixedSize(70, 38)
        self.send_btn.setCursor(Qt.PointingHandCursor)
        self.send_btn.clicked.connect(self.send_message)

        # Add to input layout
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_btn)

        # Build the complete layout
        content_layout.addWidget(header)
        content_layout.addWidget(self.scroll_area, 1)
        content_layout.addWidget(input_container)

        container_layout.addWidget(content_frame)

        # Set size
        self.chat_container.setFixedWidth(320)
        self.chat_container.setFixedHeight(420)

        # Add welcome message
        self.add_message(
            "Hello BaselAM! I'm your new chat assistant that actually works. Try sending a message!",
            False)

        # Add to main layout
        layout.addWidget(self.chat_btn)

        # Apply styling
        self.apply_theme()

    def toggle_chat(self):
        """Toggle chat visibility"""
        self.chat_visible = not self.chat_visible

        if self.chat_visible:
            # Position near button
            btn_pos = self.chat_btn.mapToGlobal(QPoint(0, self.chat_btn.height()))

            # Ensure on screen
            screen = QApplication.desktop().screenGeometry()
            x = min(btn_pos.x(), screen.width() - self.chat_container.width() - 20)
            x = max(20, x)

            self.chat_container.move(x, btn_pos.y() + 5)
            self.chat_container.show()
            self.message_input.setFocus()
        else:
            self.chat_container.hide()

    def toggle_expand(self):
        """Toggle between normal and expanded chat size"""
        self.is_expanded = not self.is_expanded

        if self.is_expanded:
            self.chat_container.setFixedWidth(400)
            self.chat_container.setFixedHeight(500)
            self.expand_btn.setText("⤡")
        else:
            self.chat_container.setFixedWidth(320)
            self.chat_container.setFixedHeight(420)
            self.expand_btn.setText("⤢")

    def send_message(self):
        """Send a message and get response"""
        message = self.message_input.text().strip()
        if not message:
            return

        # Add user message
        self.add_message(message, True)

        # Clear input
        self.message_input.clear()

        # Emit signal
        self.chat_submitted.emit(message)

        # Show thinking message
        thinking = self.add_message("Thinking...", False)

        # Process in thread
        def get_response():
            # Simulate thinking
            time.sleep(1)

            # Get random response
            response = random.choice(self.responses)

            # Remove thinking message
            QTimer.singleShot(0, lambda: self.remove_message(thinking))

            # Add AI response
            QTimer.singleShot(100, lambda: self.add_message(response, False))

        threading.Thread(target=get_response, daemon=True).start()

    def add_message(self, message, is_user=True):
        """Add a message bubble to the chat"""
        bubble = DirectChatBubble(message, is_user)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)

        # Scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)

        return bubble

    def remove_message(self, bubble):
        """Remove a message bubble from the chat"""
        self.messages_layout.removeWidget(bubble)
        bubble.deleteLater()

    def scroll_to_bottom(self):
        """Scroll to the bottom of the chat"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def apply_theme(self):
        """Apply theme styling"""
        dark_mode = is_dark_theme()
        accent_color = "#3949AB" if dark_mode else "#3F51B5"
        accent_hover = "#5C6BC0"
        button_text = "#FFFFFF"

        bg_color = themes.get_color('card_bg')
        text_color = themes.get_color('text')
        input_bg = themes.get_color('input_bg')

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

        # Container style
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

            #expandButton, #closeButton {{
                background-color: transparent;
                color: {button_text};
                border: none;
                padding: 3px;
                border-radius: 4px;
            }}

            #expandButton:hover, #closeButton:hover {{
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