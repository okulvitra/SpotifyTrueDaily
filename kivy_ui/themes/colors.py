"""
Color definitions for the Kivy UI
Following best practices for 2025
"""

# Define colors as RGBA tuples (0-1 range)
COLORS = {
    # Background colors
    'bg_primary': (0.039, 0.039, 0.039, 1),      # #0A0A0A - Deeper dark background
    'bg_secondary': (0.071, 0.071, 0.071, 1),    # #121212 - Slightly lighter dark background
    'bg_tertiary': (0.118, 0.118, 0.118, 1),     # #1E1E1E - Medium dark background
    'bg_card': (0.098, 0.098, 0.098, 1),         # #191919 - Card background
    
    # Accent colors
    'accent_blue': (0.231, 0.510, 0.965, 1),     # #3B82F6 - Dark blue
    'accent_violet': (0.545, 0.361, 0.965, 1),   # #8B5CF6 - Violet
    'accent_hover_violet': (0.486, 0.227, 0.929, 1),  # #7C3AED - Darker violet for hover
    'accent_green': (0.114, 0.725, 0.329, 1),    # #1DB954 - Spotify green for compatibility
    
    # Text colors
    'text_primary': (1, 1, 1, 1),                # #FFFFFF - White
    'text_secondary': (0.702, 0.702, 0.702, 1),  # #B3B3B3 - Light gray
    'text_disabled': (0.325, 0.325, 0.325, 1),   # #535353 - Dark gray
    'text_on_accent': (1, 1, 1, 1),              # #FFFFFF - White for text on accent colors
    
    # Border colors
    'border': (0.165, 0.165, 0.165, 1),          # #2A2A2A - Softer border color
    'border_light': (0.227, 0.227, 0.227, 1),    # #3A3A3A - Lighter border for highlights
    
    # Status colors
    'success': (0.114, 0.725, 0.329, 1),         # #1DB954 - Green for success
    'warning': (1, 0.722, 0, 1),                 # #FFB800 - Orange for warning
    'error': (0.906, 0.298, 0.235, 1),           # #E74C3C - Red for error
    
    # Shadow
    'shadow': (0, 0, 0, 0.5),                    # Black with transparency for shadows
}

# Font sizes (in dp)
FONTS = {
    'h1': '24sp',
    'h2': '20sp',
    'h3': '18sp',
    'body_large': '16sp',
    'body': '14sp',
    'caption': '12sp',
    'button': '14sp'
}