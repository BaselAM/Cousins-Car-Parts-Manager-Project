from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt5.QtWidgets import (QWidget, QLineEdit, QHBoxLayout, QPushButton,
                             QCompleter, QListView, QFrame, QShortcut,
                             QAbstractItemView, QStyledItemDelegate, QApplication)
from PyQt5.QtGui import QFont, QColor, QKeySequence, QPen, QBrush, QPainterPath
from typing import List

from themes import get_color


class SuggestionDelegate(QStyledItemDelegate):
    """Custom delegate for styling suggestion items in the completer popup"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hover_index = -1

    def paint(self, painter, option, index):
        """Override paint method to provide custom styling for each suggestion item"""
        # Get colors from parent theme if available
        try:
            bg_color = get_color('background')
            text_color = get_color('text')
            accent_color = get_color('highlight')

            # Determine if we need dark or light theme colors
            is_dark = QColor(bg_color).lightness() < 128
            hover_bg = QColor(accent_color).lighter(130) if is_dark else QColor(
                accent_color).lighter(150)
            hover_bg.setAlpha(70)  # Semi-transparent hover effect
        except:
            # Fallback colors
            bg_color = "#ffffff" if option.state & QAbstractItemView.State_Selected else "#f5f5f5"
            text_color = "#333333"
            accent_color = "#4a90e2"
            hover_bg = QColor(accent_color)
            hover_bg.setAlpha(70)
            is_dark = False

        # Selected item styling
        if option.state & QAbstractItemView.State_Selected:
            painter.save()
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(accent_color))

            # Draw rounded rectangle for selection
            path = QPainterPath()
            path.addRoundedRect(option.rect.adjusted(4, 2, -4, -2), 6, 6)
            painter.drawPath(path)

            # Draw text in white or contrasting color
            text_brush = QBrush(QColor("white" if is_dark else "#ffffff"))
            painter.setPen(QPen(text_brush, 1))
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
            painter.drawText(option.rect.adjusted(15, 0, -10, 0), Qt.AlignVCenter,
                             index.data())
            painter.restore()

        # Hover styling (not selected)
        elif self.hover_index == index.row():
            painter.save()
            painter.setPen(Qt.NoPen)
            painter.setBrush(hover_bg)

            # Draw rounded rectangle for hover
            path = QPainterPath()
            path.addRoundedRect(option.rect.adjusted(4, 2, -4, -2), 6, 6)
            painter.drawPath(path)

            # Draw text
            painter.setPen(QPen(QColor(text_color), 1))
            painter.drawText(option.rect.adjusted(15, 0, -10, 0), Qt.AlignVCenter,
                             index.data())
            painter.restore()

        # Normal item styling
        else:
            painter.save()
            painter.setPen(QPen(QColor(text_color), 1))
            painter.drawText(option.rect.adjusted(15, 0, -10, 0), Qt.AlignVCenter,
                             index.data())
            painter.restore()

    def sizeHint(self, option, index):
        """Adjust the size of suggestion items for better spacing"""
        size = super().sizeHint(option, index)
        return QPoint(size.width(), size.height() + 10)  # Add vertical padding


class ModernCompleterPopup(QListView):
    """Enhanced list view for search suggestions with elegant visuals"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("suggestionsPopup")
        self.setFont(QFont("Arial", 10))
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setMouseTracking(True)  # Enable mouse tracking for hover effects

        # Use custom delegate for item rendering
        self.delegate = SuggestionDelegate(self)
        self.setItemDelegate(self.delegate)

    def mouseMoveEvent(self, event):
        """Track mouse position for hover effects"""
        index = self.indexAt(event.pos())
        if index.isValid():
            self.delegate.hover_index = index.row()
        else:
            self.delegate.hover_index = -1
        self.viewport().update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        """Clear hover state when mouse leaves the widget"""
        self.delegate.hover_index = -1
        self.viewport().update()
        super().leaveEvent(event)


class IOSSearchWidget(QWidget):
    """
    Elegant iOS-style search widget with translucent appearance.

    Provides a visually appealing search interface that matches iOS design language
    while maintaining all functionality of the original search widget.
    """
    search_submitted = pyqtSignal(str)

    def __init__(self, translator, database, parent=None):
        """
        Initialize the search widget with translator and database.

        Args:
            translator: Translation service object
            database: Database connection for suggestions
            parent: Optional parent widget
        """
        super().__init__(parent)
        self.translator = translator
        self.database = database
        self.default_width = 350

        # Track if search is empty for styling
        self.is_empty = True
        self.is_focused = False

        # Get RTL setting from the app layout direction
        self.is_rtl = self._detect_rtl_setting(parent)

        # Setup components
        self._setup_ui()
        self._setup_shortcuts()
        self.setMinimumWidth(self.default_width)
        self.apply_theme()

    def _detect_rtl_setting(self, parent):
        """Detect RTL setting from parent widgets or application settings."""
        # Method 1: Check application layout direction
        if QApplication.layoutDirection() == Qt.RightToLeft:
            return True

        # Method 2: Check parent widget layout direction
        if parent and parent.layoutDirection() == Qt.RightToLeft:
            return True

        # Method 3: Try to access GUI's rtl_enabled property by traversing up
        widget = parent
        while widget:
            if hasattr(widget, 'rtl_enabled'):
                return widget.rtl_enabled
            widget = widget.parent()

        # Method 4: Try to access settings database through parent
        widget = parent
        while widget:
            if hasattr(widget, 'settings_db'):
                return widget.settings_db.get_rtl_setting()
            widget = widget.parent()

        # Default to LTR if we can't detect
        return False

    def _setup_ui(self) -> None:
        """Create iOS-style UI components with proper text direction."""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Container for styling and visual grouping
        self.container = QFrame()
        self.container.setObjectName("searchContainer")
        self.container.setFixedHeight(36)

        # Set the container's layout direction
        self.container.setLayoutDirection(Qt.RightToLeft if self.is_rtl else Qt.LeftToRight)

        # Container layout
        container_layout = QHBoxLayout(self.container)
        container_layout.setContentsMargins(10, 2, 10, 2)
        container_layout.setSpacing(4)

        # Search icon (positioned based on text direction)
        self.search_icon = QPushButton("🔍")
        self.search_icon.setObjectName("searchIcon")
        self.search_icon.setFixedSize(18, 18)
        self.search_icon.setEnabled(False)  # Just a visual element
        self.search_icon.setCursor(Qt.ArrowCursor)

        # Search input field
        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("searchInput")
        self.search_edit.setFont(QFont("SF Pro Text", 10))  # iOS-like font

        # Set appropriate text alignment based on language direction
        self.search_edit.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter if self.is_rtl else Qt.AlignLeft | Qt.AlignVCenter)

        # Set text direction for proper cursor positioning
        if self.is_rtl:
            self.search_edit.setLayoutDirection(Qt.RightToLeft)
            # Force Qt to handle RTL input methods correctly
            self.search_edit.setInputMethodHints(Qt.ImhPreferNumbers | Qt.ImhLatinOnly)
        else:
            self.search_edit.setLayoutDirection(Qt.LeftToRight)

        self.search_edit.returnPressed.connect(self.submit_search)
        self.search_edit.setPlaceholderText(self._translate("search_placeholder"))
        self.search_edit.textChanged.connect(self._on_text_changed)
        self.search_edit.focusInEvent = self._focus_in_event
        self.search_edit.focusOutEvent = self._focus_out_event

        # Clear button (hidden initially, iOS-style)
        self.clear_button = QPushButton("✕")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.setFixedSize(18, 18)
        self.clear_button.clicked.connect(self.clear_search)
        self.clear_button.hide()  # Hidden when empty

        # Add components to container based on text direction
        if self.is_rtl:
            # RTL order: clear button, input, search icon
            container_layout.addWidget(self.clear_button)
            container_layout.addWidget(self.search_edit)
            container_layout.addWidget(self.search_icon)
        else:
            # LTR order: search icon, input, clear button
            container_layout.addWidget(self.search_icon)
            container_layout.addWidget(self.search_edit)
            container_layout.addWidget(self.clear_button)

        # Add container to main layout
        layout.addWidget(self.container)

        # Setup search suggestions
        self._setup_suggestions()

    def _focus_in_event(self, event):
        """Custom focus in event."""
        QLineEdit.focusInEvent(self.search_edit, event)
        self.is_focused = True
        self._update_search_appearance()

    def _focus_out_event(self, event):
        """Custom focus out event."""
        QLineEdit.focusOutEvent(self.search_edit, event)
        self.is_focused = False
        self._update_search_appearance()

    def _on_text_changed(self, text: str) -> None:
        """
        Handle text changes in the search input with iOS-style animation.

        Args:
            text: Current text in the search field
        """
        self.is_empty = not bool(text.strip())
        self._update_search_appearance()

    def _update_search_appearance(self):
        """Update the search field appearance based on state."""
        if self.is_empty:
            # Empty state - hide clear button
            self.clear_button.hide()
        else:
            # Non-empty state - show clear button
            self.clear_button.show()

        # Text alignment is maintained based on language direction
        # No need to change alignment here

    def apply_theme(self) -> None:
        """Apply iOS-style theme styling to all components."""
        try:
            # Get colors from theme system
            bg_color = get_color('header')
            text_color = get_color('text')

            # Determine if we need dark or light theme iOS styling
            bg = QColor(bg_color)
            is_dark = bg.lightness() < 128

            # iOS-style search bar colors
            if is_dark:
                # Dark mode iOS
                container_bg = "rgba(55, 55, 60, 0.8)"  # Translucent dark gray
                placeholder_color = "rgba(235, 235, 245, 0.6)"  # Light gray
                icon_color = "rgba(235, 235, 245, 0.6)"  # Light gray
                clear_button_bg = "rgba(90, 90, 90, 0.7)"  # Gray circle
                clear_text_color = "rgba(235, 235, 245, 0.8)"  # Light gray
            else:
                # Light mode iOS
                container_bg = "rgba(118, 118, 128, 0.12)"  # Very light gray
                placeholder_color = "rgba(60, 60, 67, 0.6)"  # Medium gray
                icon_color = "rgba(60, 60, 67, 0.6)"  # Medium gray
                clear_button_bg = "rgba(200, 200, 200, 0.7)"  # Light gray circle
                clear_text_color = "rgba(60, 60, 67, 0.8)"  # Dark gray

            # Apply iOS-style unified styling
            self.setStyleSheet(f"""
                #searchContainer {{
                    background-color: {container_bg};
                    border-radius: 10px;  /* iOS-style rounded corners */
                    border: none;
                }}

                #searchInput {{
                    background-color: transparent;
                    color: {text_color};
                    border: none;
                    padding: 0 4px;
                    font-size: 10pt;
                }}

                #searchInput::placeholder {{
                    color: {placeholder_color};
                }}

                #searchContainer:focus-within {{
                    background-color: {container_bg};
                }}

                #searchIcon {{
                    background-color: transparent;
                    color: {icon_color};
                    border: none;
                    font-size: 12px;
                }}

                #clearButton {{
                    background-color: {clear_button_bg};
                    color: {clear_text_color};
                    border: none;
                    border-radius: 9px;  /* Make it a circle */
                    font-size: 10px;
                    font-weight: bold;
                    padding: 0px;
                }}

                #clearButton:hover {{
                    background-color: {clear_button_bg.replace('0.7', '0.9')};
                }}
            """)

            # Style the completer popup if it exists
            if hasattr(self, 'completer') and self.completer:
                popup = self.completer.popup()
                if popup:
                    popup_bg = "rgba(30, 30, 30, 0.9)" if is_dark else "rgba(255, 255, 255, 0.95)"
                    border_color = "rgba(80, 80, 80, 0.5)" if is_dark else "rgba(200, 200, 200, 0.8)"

                    popup.setStyleSheet(f"""
                        QListView {{
                            background-color: {popup_bg};
                            border: 1px solid {border_color};
                            border-radius: 12px;
                            padding: 6px;
                        }}

                        QScrollBar:vertical {{
                            background: transparent;
                            width: 6px;
                            margin: 4px 2px;
                            border-radius: 3px;
                        }}

                        QScrollBar::handle:vertical {{
                            background: rgba(150, 150, 150, 0.6);
                            border-radius: 3px;
                            min-height: 20px;
                        }}
                    """)

        except Exception as e:
            print(f"Error applying iOS theme: {str(e)}")
            # Fallback styling
            self.setStyleSheet("""
                #searchContainer {
                    background-color: rgba(200, 200, 200, 0.3);
                    border-radius: 10px;
                }

                #searchInput {
                    background-color: transparent;
                    color: black;
                    border: none;
                }
            """)

    # Other methods remain the same, just modify what we need for iOS appearance
    def _setup_shortcuts(self):
        # Same as original
        self.escape_shortcut = QShortcut(QKeySequence(Qt.Key_Escape), self)
        self.escape_shortcut.activated.connect(self.clear_search)

        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self.window())
        self.search_shortcut.activated.connect(self._focus_search)

    def _setup_suggestions(self):
        # Same as original but with iOS styling adjustments
        suggestions = self._get_search_suggestions()
        if not suggestions:
            return

        self.completer = QCompleter(suggestions)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)

        popup = ModernCompleterPopup()
        popup.setMinimumWidth(300)

        self.completer.setPopup(popup)
        self.search_edit.setCompleter(self.completer)
        self.completer.activated.connect(self.submit_search)

    def _get_search_suggestions(self):
        # Same as original
        try:
            if hasattr(self.database, 'get_search_suggestions'):
                db_suggestions = self.database.get_search_suggestions()
                if db_suggestions and len(db_suggestions) > 0:
                    return db_suggestions

            return [
                self._translate("suggestion_parts"),
                self._translate("suggestion_service"),
                self._translate("suggestion_repair"),
                self._translate("suggestion_brands"),
                self._translate("suggestion_inventory")
            ]
        except Exception as e:
            print(f"Error loading search suggestions: {str(e)}")
            return ["Parts", "Service", "Repair", "Brands", "Inventory"]

    def _translate(self, key, default=""):
        # Same as original
        try:
            if hasattr(self.translator, 't'):
                return self.translator.t(key)
            return default or key
        except Exception:
            return default or key

    def submit_search(self):
        # Same as original
        search_text = self.search_edit.text().strip()
        if search_text:
            self.search_submitted.emit(search_text)
            self.search_edit.clear()

    def _focus_search(self):
        # Same as original
        self.search_edit.setFocus()
        self.search_edit.selectAll()

    def clear_search(self):
        # Modified to update appearance
        self.search_edit.clear()
        self.is_empty = True
        self._update_search_appearance()

    def update_translations(self):
        """Update translations and text direction based on current language."""
        # Update placeholder text
        self.search_edit.setPlaceholderText(
            self._translate("search_placeholder", "Search..."))

        # Update RTL setting
        self.is_rtl = self._detect_rtl_setting(self.parent())

        # Set proper text alignment and direction
        self.search_edit.setAlignment(
            Qt.AlignRight | Qt.AlignVCenter if self.is_rtl else Qt.AlignLeft | Qt.AlignVCenter)
        self.search_edit.setLayoutDirection(Qt.RightToLeft if self.is_rtl else Qt.LeftToRight)
        self.container.setLayoutDirection(Qt.RightToLeft if self.is_rtl else Qt.LeftToRight)

        # Reorder components based on new direction
        container_layout = self.container.layout()

        # Clear the layout
        while container_layout.count():
            item = container_layout.takeAt(0)

        # Add components back in correct order
        if self.is_rtl:
            # RTL order: clear button, input, search icon
            container_layout.addWidget(self.clear_button)
            container_layout.addWidget(self.search_edit)
            container_layout.addWidget(self.search_icon)
        else:
            # LTR order: search icon, input, clear button
            container_layout.addWidget(self.search_icon)
            container_layout.addWidget(self.search_edit)
            container_layout.addWidget(self.clear_button)

        # Update input method hints
        if self.is_rtl:
            self.search_edit.setInputMethodHints(Qt.ImhPreferNumbers | Qt.ImhLatinOnly)
        else:
            self.search_edit.setInputMethodHints(Qt.ImhNone)

        # Update suggestions
        if hasattr(self, 'completer'):
            self.completer.setModel(None)
            self.completer = QCompleter(self._get_search_suggestions())
            self.completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.completer.setFilterMode(Qt.MatchContains)

            popup = ModernCompleterPopup()
            popup.setMinimumWidth(300)
            self.completer.setPopup(popup)

            self.search_edit.setCompleter(self.completer)