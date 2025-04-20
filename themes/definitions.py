"""Theme color definitions and size constants for the application."""

# Base unit for consistent sizing across the application
# Base unit for consistent sizing across the application
BASE_UNIT = 8  # 8px as base unit

# Size constants defined as multiples of BASE_UNIT
SIZE = {
    # Basic sizes
    "tiny": BASE_UNIT,  # 8px
    "small": BASE_UNIT * 2,  # 16px
    "medium": BASE_UNIT * 3,  # 24px
    "large": BASE_UNIT * 4,  # 32px
    "xlarge": BASE_UNIT * 5,  # 40px
    "xxlarge": BASE_UNIT * 6,  # 48px

    # Specific element sizes
    "button_min_width": BASE_UNIT * 20,  # 160px
    "button_min_height": BASE_UNIT * 7,  # 56px
    "button_max_width": BASE_UNIT * 37,  # 296px
    "button_max_height": BASE_UNIT * 20,  # 160px

    # Header and footer heights
    "header_height": BASE_UNIT * 9,  # 72px
    "footer_height": BASE_UNIT * 4,  # 32px
    "copyright_height": BASE_UNIT * 4,  # 32px

    # Spacing and margins
    "spacing_tiny": BASE_UNIT / 2,  # 4px
    "spacing_small": BASE_UNIT,  # 8px
    "spacing_medium": BASE_UNIT * 2,  # 16px
    "spacing_large": BASE_UNIT * 3,  # 24px
    "spacing_xlarge": BASE_UNIT * 4,  # 32px
    "spacing_xxlarge": BASE_UNIT * 5,  # 40px

    # Borders and radiuses
    "border_radius_small": BASE_UNIT / 2,  # 4px
    "border_radius_medium": BASE_UNIT,  # 8px
    "border_radius_large": BASE_UNIT * 2,  # 16px

    # Additional aliases used by widgets (these prevent the warnings)
    "border_radius": BASE_UNIT,  # Maps to border_radius_medium
    "padding": BASE_UNIT,  # Maps to spacing_small
    "margin": BASE_UNIT,  # Maps to spacing_small
}
# Font sizes
FONT_SIZE = {
    "tiny": 8,
    "small": 10,
    "medium": 12,
    "regular": 14,
    "large": 16,
    "xlarge": 20,
    "xxlarge": 24,
    "header": 32,
    "title": 40
}

# Theme color palettes - enhanced for consistency and expanded for more UI elements
THEMES = {
    "classic": {
        "primary": "#1A365D",
        "secondary": "#2A4365",
        "background": "#0F2942",
        "text": "#E2E8F0",
        "button": "#3182CE",
        "button_hover": "#4299E1",
        "button_pressed": "#2B6CB0",
        "button_disabled": "#718096",  # Added
        "text_disabled": "#A0AEC0",    # Added
        "border": "#2C5282",
        "input_bg": "#1E3A5F",
        "header": "#0F2942",
        "footer": "#0F2942",
        "sidebar_bg": "#0F2942",
        "sidebar_button": "#1E3A5F",
        "stats_card": "#2A4D6A",
        "warning": "#ECC94B",
        "success": "#38B2AC",
        "error": "#E53E3E",
        "card_bg": "#1E3A5F",
        "shadow": "#00000066",
        "highlight": "#4299E1",
        "highlight_text": "#FFFFFF",   # Added
        "divider": "#2C5282",
        "accent": "#805AD5",
        "overlay": "#0F2942DD",
        "title": "#E2E8F0",
        "secondary_text": "#A0AEC0"    # Added
    },
    "dark": {
        "primary": "#121212",
        "secondary": "#1E1E1E",
        "background": "#000000",
        "text": "#F7FAFC",
        "button": "#2D3748",
        "button_hover": "#4A5568",
        "button_pressed": "#1A202C",
        "button_disabled": "#4A5568",  # Added
        "text_disabled": "#718096",    # Added
        "border": "#2D3748",
        "input_bg": "#1E1E1E",
        "header": "#000000",
        "footer": "#000000",
        "sidebar_bg": "#121212",
        "sidebar_button": "#1E1E1E",
        "stats_card": "#1A202C",
        "success": "#38A169",
        "warning": "#DD6B20",
        "error": "#E53E3E",
        "card_bg": "#1E1E1E",
        "shadow": "#00000080",
        "highlight": "#5A67D8",
        "divider": "#2D3748",
        "accent": "#9F7AEA",
        "overlay": "#000000E6",
        "title": "#F7FAFC",
        "highlight_text": "#FFFFFF",
        "secondary_text": "#A0AEC0"
    },
    "light": {
        "primary": "#FFFFFF",
        "secondary": "#F7FAFC",
        "background": "#EDF2F7",
        "text": "#1A202C",
        "button": "#4299E1",
        "button_hover": "#63B3ED",
        "button_pressed": "#3182CE",
        "button_disabled": "#CBD5E0",  # Added
        "text_disabled": "#718096",    # Added
        "border": "#CBD5E0",
        "input_bg": "#FFFFFF",
        "header": "#FFFFFF",
        "footer": "#FFFFFF",
        "sidebar_bg": "#FFFFFF",
        "sidebar_button": "#F7FAFC",
        "stats_card": "#F7FAFC",
        "success": "#38A169",
        "warning": "#DD6B20",
        "error": "#E53E3E",
        "card_bg": "#FFFFFF",
        "shadow": "#00000015",
        "highlight": "#90CDF4",
        "divider": "#E2E8F0",
        "accent": "#9F7AEA",
        "overlay": "#EDF2F7E6",
        "title": "#1A202C",
        "highlight_text": "#1A202C",   # Added
        "secondary_text": "#4A5568"    # Added
    }
}