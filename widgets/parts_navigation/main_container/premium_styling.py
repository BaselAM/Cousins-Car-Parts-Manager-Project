"""
Premium styling utilities for the parts navigation system.
Provides high-end iOS and Android inspired styling with robust Qt compatibility.
"""
from PyQt5.QtGui import QColor, QFont, QFontDatabase

def load_premium_fonts():
    """Load premium fonts for a more elegant interface."""
    # In a real application, you would load custom fonts here
    # For now, we'll use system fonts that are similar to premium designs
    pass

def generate_premium_stylesheet(colors):
    """
    Generate a premium stylesheet for the PartsNavigationContainer with robust Qt compatibility.

    Args:
        colors: A dictionary with theme colors

    Returns:
        str: The generated stylesheet with premium styling
    """
    # Ensure all required colors are available with fallbacks
    bg_color = colors.get('background', '#0F2942')
    card_bg = colors.get('card_bg', '#1E3A5F')
    text_color = colors.get('text', '#E2E8F0')
    highlight = colors.get('highlight', '#4299E1')
    border_color = colors.get('border', '#2C5282')
    button = colors.get('button', '#3182CE')
    button_hover = colors.get('button_hover', '#4299E1')
    button_pressed = colors.get('button_pressed', '#2B6CB0')
    button_disabled = colors.get('button_disabled', '#718096')
    text_disabled = colors.get('text_disabled', '#A0AEC0')
    secondary_text = colors.get('secondary_text', '#A0AEC0')

    # Enhanced colors for premium look - properly computed
    highlight_darker = QColor(highlight).darker(115).name()
    highlight_lighter = QColor(highlight).lighter(115).name()
    button_darker = QColor(button).darker(110).name()
    card_bg_darker = QColor(card_bg).darker(105).name()
    card_bg_lighter = QColor(card_bg).lighter(105).name()

    # Qt-compatible transparency for rgba colors
    soft_shadow_color = "rgba(0, 0, 0, 0.1)"
    medium_shadow_color = "rgba(0, 0, 0, 0.15)"

    # For highlight transparency, create proper rgba format
    h_color = QColor(highlight)
    highlight_trans = f"rgba({h_color.red()}, {h_color.green()}, {h_color.blue()}, 0.5)"

    return f"""
        /* Main container styling with premium look */
        #partsContainer {{
            background-color: {bg_color};
        }}
        
        #partsNavigationTitle {{
            color: {text_color};
            font-weight: bold;
            font-size: 18px;
            letter-spacing: -0.5px;
            margin-bottom: 10px;
            padding: 5px;
            font-family: "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
        }}
        
        #titleSeparator {{
            background-color: {border_color};
            margin-left: 30px;
            margin-right: 30px;
            margin-bottom: 15px;
            height: 1px;
            opacity: 0.5;
        }}
        
        #partsContent {{
            background-color: {card_bg};
            border-radius: 12px;
            border: none;
            padding: 15px;
        }}
        
        /* Premium search styling */
        #searchContainer {{
            padding: 8px;
            background-color: {card_bg_lighter};
            border-radius: 10px;
            margin-bottom: 15px;
        }}
        
        #searchInput {{
            background-color: {card_bg_lighter};
            color: {text_color};
            border: none;
            border-radius: 8px;
            padding: 10px 15px;
            font-size: 14px;
            font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
        }}
        
        #searchInput:focus {{
            background-color: {card_bg};
            border: 1px solid {highlight};
        }}
        
        /* Enhanced search button with premium styling */
        #searchButton {{
            background-color: {highlight};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 18px;
            font-weight: bold;
            font-size: 14px;
            min-width: 100px;
            font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
            letter-spacing: 0.2px;
        }}
        
        #searchButton:hover {{
            background-color: {highlight_lighter};
        }}
        
        #searchButton:pressed {{
            background-color: {highlight_darker};
            padding-top: 11px;
            padding-bottom: 9px;
        }}
        
        #searchButton:disabled {{
            background-color: {button_disabled};
            color: {text_disabled};
        }}
        
        /* Step indicators with premium styling */
        #stepCircleContainer {{
            background-color: transparent;
            border-radius: 20px;
        }}
        
        #stepCircleCompleted {{
            background-color: {highlight};
            color: white;
            border-radius: 20px;
            border: 1px solid {highlight_darker};
        }}
        
        #stepCheckmark {{
            color: white;
            font-size: 16px;
            font-weight: bold;
        }}
        
        #stepTextCompleted {{
            color: {highlight};
            font-weight: 600;
            font-size: 10px;
            margin-top: 5px;
            font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
        }}
        
        #stepCircleCurrent {{
            background-color: {highlight_lighter};
            color: white;
            border-radius: 20px;
            border: 2px solid white;
        }}
        
        #stepNumber {{
            color: white;
            font-size: 14px;
            font-weight: bold;
        }}
        
        #stepTextCurrent {{
            color: {highlight};
            font-weight: 600;
            font-size: 10px;
            margin-top: 5px;
            font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
        }}
        
        #stepCircleFuture {{
            background-color: {card_bg_lighter};
            color: {text_color};
            border-radius: 20px;
            border: 1px solid {border_color};
        }}
        
        #stepTextFuture {{
            color: {text_color};
            font-size: 10px;
            margin-top: 5px;
            opacity: 0.7;
            font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
        }}
        
        /* Premium navigation buttons - simplified for robust Qt compatibility */
        #backButton, #nextButton {{
            border-radius: 25px;
            padding: 12px 24px;
            min-width: 120px;
            font-size: 15px;
            font-weight: 600;
            letter-spacing: 0.2px;
            font-family: "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
        }}
        
        #backButton {{
            background-color: {card_bg_lighter};
            color: {text_color};
            border: 1px solid {border_color};
        }}
        
        #backButton:hover {{
            background-color: {card_bg};
            border: 1px solid {highlight};
        }}
        
        #backButton:pressed {{
            background-color: {card_bg_darker};
            padding-top: 13px;
            padding-bottom: 11px;
            border: 1px solid {highlight};
        }}
        
        #backButton:disabled {{
            background-color: {card_bg};
            color: {text_disabled};
            border: 1px solid {card_bg_darker};
        }}
        
        #nextButton {{
            background-color: {highlight};
            color: white;
            font-weight: bold;
            border: none;
        }}
        
        #nextButton:hover {{
            background-color: {highlight_lighter};
        }}
        
        #nextButton:pressed {{
            background-color: {highlight_darker};
            padding-top: 13px;
            padding-bottom: 11px;
        }}
        
        #nextButton:disabled {{
            background-color: {button_disabled};
            color: {text_disabled};
            opacity: 0.7;
        }}
    """