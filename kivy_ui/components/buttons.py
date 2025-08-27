"""
Modern UI buttons for the Kivy application
Following best practices for 2025
"""

from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle
from kivy.metrics import dp
from kivy.animation import Animation

from kivy_ui.themes.colors import COLORS

class ModernButton(Button):
    """Modern button with hover effects and rounded corners"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  # Transparent background
        self.color = COLORS['text_on_accent']
        self.height = dp(40)
        self.size_hint_y = None
        self.border = (0, 0, 0, 0)  # Remove default border
        
        # Create button background
        with self.canvas.before:
            Color(*COLORS['accent_violet'])
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
            
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Bind to touch events for hover effect
        self.bind(on_press=self.on_press_effect)
        
    def update_bg(self, *args):
        """Update button background"""
        self.bg.pos = self.pos
        self.bg.size = self.size
        
    def on_press_effect(self, *args):
        """Visual effect when button is pressed"""
        # Animate color change by updating the canvas
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLORS['accent_hover_violet'])
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )
        
        # Reset color after a short delay
        from kivy.clock import Clock
        Clock.schedule_once(self.reset_color, 0.1)
        
    def reset_color(self, *args):
        """Reset button color"""
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*COLORS['accent_violet'])
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(8)]
            )