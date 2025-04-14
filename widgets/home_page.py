from PyQt5.QtCore import Qt, QSize, QEvent, QTimer
from PyQt5.QtWidgets import (
    QWidget, QGridLayout, QVBoxLayout, QLabel,
    QHBoxLayout, QFrame, QSizePolicy, QToolButton
)
from PyQt5.QtGui import QIcon, QFont
from themes import get_color, get_size, get_font_size
from size_policy import SizePolicyMixin, ResponsiveFontMixin
from pathlib import Path


class ResponsiveAppButton(QToolButton, SizePolicyMixin, ResponsiveFontMixin):
    """Modern, responsive app button that adjusts to the window size with controlled growth limits"""

    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(parent)

        # Use Expanding policy to fill available space
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Slightly reduced minimum size for smaller buttons
        self.setMinimumSize(get_size("button_min_width") * 1.8, get_size("button_min_height") * 1.8)

        # Slightly reduced maximum size to maintain elegant proportions
        self.setMaximumSize(get_size("button_min_width") * 3.5, get_size("button_min_height") * 3.5)

        self.setText(text)

        # Set the icon if the path exists
        if icon_path and Path(icon_path).exists():
            self.setIcon(QIcon(str(icon_path)))
            # Larger initial icon size for more elegant appearance
            self.setIconSize(QSize(get_size("xxlarge") * 1.2, get_size("xxlarge") * 1.2))
        else:
            # Fallback if icon not found
            self.setToolButtonStyle(Qt.ToolButtonTextOnly)

        # Install event filter to handle resizing events
        self.installEventFilter(self)

        # Set text below icon
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)

        # Set responsive font with larger size for elegance
        self.set_responsive_font(size_key="large", weight=QFont.Bold, max_point_size=18)

    def eventFilter(self, obj, event):
        """Handle resize events to scale icon size proportionally with constraints"""
        if obj == self and event.type() == QEvent.Resize:
            # Calculate icon size based on button dimensions
            min_dimension = min(self.width(), self.height())

            # Adjusted scaling factor for more elegant icon size
            icon_size = int(min_dimension * 0.50)  # Slightly smaller ratio for better proportions

            # Increased icon size limits
            icon_min = get_size("xlarge") * 1.2  # Larger minimum
            icon_max = get_size("xxlarge") * 2  # Allow for larger maximum

            # Ensure the icon size stays within reasonable bounds
            if icon_size < icon_min:
                icon_size = icon_min
            elif icon_size > icon_max:
                icon_size = icon_max

            # Update icon size with constraints applied
            self.setIconSize(QSize(icon_size, icon_size))

            # Adjust font size with larger range
            self.adjust_font_size_to_width(self.width(),
                                           min_size=12,  # Slightly larger min size
                                           max_size=18,
                                           base_width=get_size("button_min_width") * 2)

        return super().eventFilter(obj, event)


class HomePageWidget(QWidget, SizePolicyMixin):
    def __init__(self, translator, navigation_functions, parent=None, user_data=None):
        super().__init__(parent)
        self.translator = translator
        self.navigation_functions = navigation_functions

        # Initialize with user data from database instead of hardcoded value
        self.username = user_data if user_data else ""

        # Title proportion configuration
        self.title_proportion = 0.07  # Increased proportion for better visibility

        self.setup_ui()
        self.apply_theme()

        # Set up resize timer to avoid excessive font recalculations
        self.resize_timer = QTimer()
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.update_title_size)

        # Install event filter to catch resize events
        self.installEventFilter(self)

    def is_dark_theme(self, bg_color):
        """Determine if current theme is dark based on background color"""
        # If bg_color is a string like "#1e2124"
        if isinstance(bg_color, str) and bg_color.startswith('#'):
            # Convert hex to RGB and calculate brightness
            if len(bg_color) >= 7:  # Make sure we have enough characters
                try:
                    r = int(bg_color[1:3], 16)
                    g = int(bg_color[3:5], 16)
                    b = int(bg_color[5:7], 16)
                    brightness = (r * 299 + g * 587 + b * 114) / 1000
                    return brightness < 128
                except (ValueError, IndexError):
                    # In case of invalid hex string
                    return True
        return True  # Default to dark theme if can't determine

    def get_adaptive_title_color(self, is_dark_theme):
        """Return appropriate title color based on theme"""
        if is_dark_theme:
            # Bright white for dark themes to ensure visibility
            return "#FFFFFF"
        else:
            # Deep navy for light themes
            return "#1a365d"

    def get_adaptive_shadow(self, is_dark_theme, intensity=1.0):
        """Return appropriate text shadow based on theme"""
        if is_dark_theme:
            # Golden glow for dark themes
            alpha = 0.3 * intensity
            return f"0px 1px 2px rgba(212, 175, 55, {alpha})"
        else:
            # Subtle shadow for light themes
            alpha = 0.4 * intensity
            return f"0px 1px 1px rgba(0, 0, 25, {alpha})"

    def eventFilter(self, obj, event):
        """Handle resize events to adjust title proportions"""
        if obj == self and event.type() == QEvent.Resize:
            # Use timer to avoid excessive updates during resizing
            self.resize_timer.start(100)  # 100ms delay
        return super().eventFilter(obj, event)

    def update_title_size(self):
        """Update title size to maintain proportion of window height"""
        if hasattr(self, 'title_container') and hasattr(self, 'title'):
            # Calculate target height based on window size and desired proportion
            window_height = self.height()
            window_width = self.width()
            title_height = int(window_height * self.title_proportion)

            # Enforce more generous min/max limits
            min_height = max(get_size("large") * 2, 50)  # Increased minimum height
            max_height = get_size("xxlarge") * 2.5  # Increased maximum height
            title_height = max(min_height, min(max_height, title_height))

            # Set container height with extra padding
            self.title_container.setFixedHeight(title_height + 15)  # Added padding

            # Adjust font size based on container height AND width
            base_font_size = int(title_height * 0.40)  # Base on height

            # Scale down if window is narrow
            width_factor = min(1.0, window_width / 800.0)  # Start scaling down if width < 800px

            # Calculate font size considering both height and width
            font_size = int(base_font_size * width_factor)

            # Enforce reasonable font size limits with lower minimum
            min_font = min(get_font_size("medium"), 12)  # Lower minimum font size
            max_font = get_font_size("xxlarge") * 1.5
            font_size = max(min_font, min(max_font, font_size))

            # Update font
            font = self.title.font()
            font.setPointSize(font_size)
            self.title.setFont(font)

            # Also update decorative elements font size
            if hasattr(self, 'left_decor') and hasattr(self, 'right_decor'):
                decor_font = QFont()
                decor_font.setPointSize(int(font_size * 0.6))
                self.left_decor.setFont(decor_font)
                self.right_decor.setFont(decor_font)

    def setup_ui(self):
        """Create a modern app-like layout with responsive buttons"""
        # Main layout with adjusted margins and increased spacing
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(
            get_size("spacing_large"),
            get_size("spacing_medium"),  # Increased top margin
            get_size("spacing_large"),
            get_size("spacing_medium")
        )
        self.main_layout.setSpacing(get_size("spacing_large"))  # Increased spacing between elements

        # ===== TITLE SECTION =====
        # Create a dedicated container for the title with controlled sizing
        self.title_container = QFrame()
        self.title_container.setObjectName("titleContainer")

        # Use HBoxLayout to enable proper centering and spacing
        title_layout = QHBoxLayout(self.title_container)
        title_layout.setContentsMargins(15, 12, 15, 12)  # Increased vertical padding

        # Remove background for a cleaner look
        self.title_container.setStyleSheet("")

        # Title with modern styling - increased height to prevent cutting off
        self.title = QLabel()
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setWordWrap(True)
        self.title.setMinimumHeight(45)  # Increased minimum height
        title_font = QFont("Segoe UI", get_font_size("large"))
        title_font.setWeight(QFont.DemiBold)  # More modern weight
        self.title.setFont(title_font)
        self.title.setObjectName("pageTitle")

        # Modern, clean layout with just the title
        title_layout.addWidget(self.title, 10)

        # Add separator line below title
        self.title_separator = QFrame()
        self.title_separator.setFrameShape(QFrame.HLine)
        self.title_separator.setObjectName("titleSeparator")

        # Add explicit spacing after the title section
        self.main_layout.addWidget(self.title_container)
        self.main_layout.addWidget(self.title_separator)
        self.main_layout.addSpacing(get_size("spacing_medium"))  # Add extra space here

        # ===== MAIN CONTENT AREA =====
        # Create a container for buttons and welcome message
        content_container = QFrame()
        content_container.setObjectName("appGridContainer")
        content_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create layout for content container
        content_layout = QVBoxLayout(content_container)
        # Add padding around the content - more compact but still elegant
        padding_size = get_size("spacing_large")  # Slightly reduced padding
        content_layout.setContentsMargins(padding_size, padding_size, padding_size, padding_size)
        content_layout.setSpacing(get_size("spacing_medium"))  # Reduced spacing for compression

        # Create a simple 3x2 grid for the buttons with more elegant spacing
        button_grid = QGridLayout()
        # Slightly reduced spacing between buttons for a more compact look
        button_grid.setSpacing(get_size("spacing_medium"))  # Reduced for a more compact layout

        # Define buttons configuration
        # Define buttons configuration
        buttons = [
            {"id": "products_button", "icon": "resources/product_icon.png", "row": 0, "col": 0},
            {"id": "smart_search_button", "icon": "resources/parts_icon.png", "row": 0, "col": 1},
            {"id": "register_button", "icon": "resources/search_web_icon.png", "row": 0, "col": 2},
            {"id": "statistics_button", "icon": "resources/stats_icon.png", "row": 1, "col": 0},
            {"id": "settings_button", "icon": "resources/settings_icon.png", "row": 1, "col": 1},
            {"id": "help_button", "icon": "resources/help_icon.png", "row": 1, "col": 2}
        ]

        # Create buttons and add to grid
        self.nav_buttons = {}
        for btn in buttons:
            button = ResponsiveAppButton(
                self.translator.t(btn["id"]),
                btn["icon"]
            )
            if btn["id"] in self.navigation_functions:
                button.clicked.connect(self.navigation_functions[btn["id"]])

            self.nav_buttons[btn["id"]] = button
            button_grid.addWidget(button, btn["row"], btn["col"])

        # Set equal column and row stretch
        for i in range(3):  # 3 columns
            button_grid.setColumnStretch(i, 1)
        for i in range(2):  # 2 rows
            button_grid.setRowStretch(i, 1)

        # Add button grid to content layout
        content_layout.addLayout(button_grid, 10)  # Button grid takes most space

        # ===== WELCOME MESSAGE =====
        # Create vertical layout for welcome and username (stacked)
        welcome_layout = QVBoxLayout()
        welcome_layout.setSpacing(get_size("spacing_small"))
        welcome_layout.setAlignment(Qt.AlignCenter)  # Center vertically and horizontally

        # Create welcome label
        self.welcome_label = QLabel()
        self.welcome_label.setAlignment(Qt.AlignCenter)  # Center text
        welcome_font = QFont("Segoe UI", get_font_size("medium"))
        welcome_font.setBold(True)
        self.welcome_label.setFont(welcome_font)
        self.welcome_label.setObjectName("welcomeText")

        # Create username label
        self.user_info = QLabel(self.username)
        self.user_info.setAlignment(Qt.AlignCenter)  # Center text
        user_font = QFont("Segoe UI", get_font_size("large"))
        user_font.setBold(True)
        self.user_info.setFont(user_font)
        self.user_info.setObjectName("usernameText")

        # Add labels to welcome layout - welcome on top, username below
        welcome_layout.addWidget(self.welcome_label)
        welcome_layout.addWidget(self.user_info)

        # Create a frame to contain the welcome section with elegant styling
        welcome_frame = QFrame()
        welcome_frame.setObjectName("welcomeFrame")
        welcome_frame_layout = QVBoxLayout(welcome_frame)
        welcome_frame_layout.addLayout(welcome_layout)
        welcome_frame_layout.setContentsMargins(
            get_size("spacing_medium"),
            get_size("spacing_small"),  # Reduced top padding
            get_size("spacing_medium"),
            get_size("spacing_small")  # Reduced bottom padding
        )

        # Add welcome frame to content - reduced vertical size
        content_layout.addWidget(welcome_frame, 1)  # Reduced proportion for welcome section

        # Add content container to main layout
        self.main_layout.addWidget(content_container, 10)

        # ===== EXIT BUTTON =====
        # Create container for exit button
        exit_container = QFrame()
        exit_layout = QHBoxLayout(exit_container)
        exit_layout.setContentsMargins(0, get_size("spacing_small"), 0, 0)

        # Create exit button
        self.exit_button = QToolButton()
        self.exit_button.setText(self.translator.t("exit_button"))
        self.exit_button.setMinimumSize(
            get_size("button_min_width") / 2,
            get_size("button_min_height")
        )
        self.exit_button.setMaximumSize(
            get_size("button_min_width") * 1.5,
            get_size("button_min_height") * 1.2
        )

        if "exit_button" in self.navigation_functions:
            self.exit_button.clicked.connect(self.navigation_functions["exit_button"])

        # Add exit button to layout
        exit_layout.addStretch(1)
        exit_layout.addWidget(self.exit_button)
        exit_layout.addStretch(1)

        # Add exit container to main layout
        self.main_layout.addWidget(exit_container, 1)

        # Initialize translations
        self.update_translations()

        # Set responsive size policy for the whole widget
        self.set_expanding_policy()

    def apply_theme(self):
        """Apply elegant theme styling with modern app aesthetics"""
        bg_color = get_color('background')
        card_bg = get_color('card_bg')
        text_color = get_color('text')
        button_bg = get_color('button')
        button_hover = get_color('button_hover')
        highlight_color = get_color('highlight')

        # Determine if we're using a light or dark theme to adapt the title styling
        is_dark_theme = self.is_dark_theme(bg_color)

        # Modern, minimal title styling with better margins
        title_container_style = f"""
            #titleContainer {{
                background: transparent;
                margin: {get_size("spacing_medium")}px {get_size("spacing_medium")}px 0px;
                padding: 0px;
                min-height: 45px;
            }}

            #titleSeparator {{
                height: 1px;
                background-color: {highlight_color}40;
                margin: 8px {get_size("spacing_xlarge")}px {get_size("spacing_large")}px;  /* Added bottom margin */
            }}

            #pageTitle {{
                color: {self.get_adaptive_title_color(is_dark_theme)};
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-weight: 500;
                letter-spacing: 0.5px;
                padding: 8px 0px;  /* Increased padding */
                margin: 0px;
                text-transform: uppercase;
                min-height: 35px;  /* Increased height */
                line-height: 140%;  /* Added line height for better text display */
            }}
        """

        # Content container styling
        container_style = f"""
            #appGridContainer {{
                background-color: {card_bg};
                border-radius: {get_size("border_radius_large")}px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            }}

            #welcomeFrame {{
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: {get_size("border_radius_medium")}px;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                margin-top: {get_size("spacing_medium")}px;
            }}

            #welcomeText {{
                color: {text_color};
                font-size: {get_font_size("medium")}px;
                padding-bottom: 2px;
            }}

            #usernameText {{
                color: {highlight_color};
                font-size: {get_font_size("large")}px;
                font-weight: bold;
                padding-top: 2px;
            }}
        """

        # Button styling - more elegant with better shadows and transitions
        # Increased padding for more space around the edges
        button_style = f"""
            QToolButton {{
                background-color: {button_bg};
                color: {text_color};
                border: none;
                border-radius: {get_size("border_radius_large")}px;
                padding: {get_size("spacing_large") * 1.2}px;  /* Increased padding */
                font-size: {get_font_size("regular")}px;
                font-weight: bold;
                box-shadow: 0 3px 5px rgba(0, 0, 0, 0.1);
                transition: all 0.2s ease;
            }}

            QToolButton:hover {{
                background-color: {button_hover};
                border: 2px solid {get_color('highlight')};
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
                transform: translateY(-2px);
            }}

            QToolButton:pressed {{
                background-color: {get_color('button_pressed')};
                border: 2px solid {get_color('highlight')};
                padding-top: {get_size("spacing_large") * 1.2 + 2}px;
                padding-bottom: {get_size("spacing_large") * 1.2 - 2}px;
                box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1);
                transform: translateY(1px);
            }}
        """

        # Exit button styling
        exit_button_style = f"""
            QToolButton {{
                background-color: {get_color('error')};
                color: white;
                border: none;
                border-radius: {get_size("border_radius_large")}px;
                padding: {get_size("spacing_medium")}px {get_size("spacing_large")}px;
                font-size: {get_font_size("regular")}px;
                font-weight: bold;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}

            QToolButton:hover {{
                background-color: #FF5252;
                border: 2px solid #FF8A80;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
            }}

            QToolButton:pressed {{
                background-color: #D32F2F;
                padding-top: {get_size("spacing_medium") + 2}px;
                padding-bottom: {get_size("spacing_medium") - 2}px;
                box-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
            }}
        """

        # Apply styles to elements
        for button in self.nav_buttons.values():
            button.setStyleSheet(button_style)

        self.exit_button.setStyleSheet(exit_button_style)

        # Apply main styling
        self.setStyleSheet(f"""
            HomePageWidget {{
                background-color: {bg_color};
            }}

            QLabel {{
                color: {text_color};
            }}

            {title_container_style}
            {container_style}
        """)

        # No direct styling - keeping it clean and theme-compatible

    def update_user(self, user_data):
        """Update the displayed username"""
        # Store the user data
        self.username = user_data

        if hasattr(self, 'user_info'):
            # Handle the username display based on the type
            if isinstance(user_data, dict):
                # If it's a dictionary, extract username or display name
                display_name = user_data.get('username', '')
                if not display_name and 'name' in user_data:
                    display_name = user_data['name']
                if not display_name and 'display_name' in user_data:
                    display_name = user_data['display_name']
                if not display_name:
                    # If no specific name field found, use the first value in the dict
                    for key, value in user_data.items():
                        if isinstance(value, str):
                            display_name = value
                            break

                # Set the user info text
                self.user_info.setText(str(display_name))
            else:
                # If it's not a dictionary (assume string), use it directly
                self.user_info.setText(str(user_data))

    def update_translations(self):
        """Update all text when language changes"""
        # Clean, modern title without letter spacing
        title_text = self.translator.t("home_page_title")
        # Simple capitalization for modern look
        self.title.setText(title_text.upper())

        # Update welcome message
        self.welcome_label.setText(self.translator.t("welcome_message"))

        # Update button texts
        for btn_id, button in self.nav_buttons.items():
            if btn_id == "smart_search_button":
                button.setText("Smart Search")  # Direct text instead of translation
            else:
                button.setText(self.translator.t(btn_id))

        # Ensure user info is up to date
        if hasattr(self, 'user_info') and self.username:
            self.update_user(self.username)

        # Update exit button
        self.exit_button.setText(self.translator.t('exit_button'))