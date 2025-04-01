"""
Car Chat - Resilient chat widget with car parts knowledge base

A modular, themeable chat interface that works with or without OpenAI API,
providing car maintenance and part information through a conversational interface.
"""

from .direct_chat import DirectChatWidget
from .chat_handler import ChatSignalBlocker

__version__ = "1.0.0"
__all__ = ['DirectChatWidget', 'ChatSignalBlocker']