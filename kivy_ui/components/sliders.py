"""
Modern UI sliders for the Kivy application
Following best practices for 2025
"""

from kivy.uix.slider import Slider
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp

from kivy_ui.themes.colors import COLORS

class ModernSlider(Slider):
    """Modern slider with custom styling"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.height = dp(40)
        self.size_hint_y = None
        self.cursor_size = (dp(20), dp(20))
        self.padding = dp(10)
        
        # Create slider track
        with self.canvas.before:
            # Background track
            Color(*COLORS['bg_tertiary'])
            self.bg_track = RoundedRectangle(
                pos=(self.x + self.padding, self.center_y - dp(2)),
                size=(self.width - 2*self.padding, dp(4)),
                radius=[dp(2)]
            )
            
            # Active track
            Color(*COLORS['accent_violet'])
            self.active_track = RoundedRectangle(
                pos=(self.x + self.padding, self.center_y - dp(2)),
                size=(self.width * (self.value - self.min) / (self.max - self.min) - 2*self.padding, dp(4)),
                radius=[dp(2)]
            )
            
        self.bind(pos=self.update_graphics, size=self.update_graphics, value=self.update_graphics)
        
    def update_graphics(self, *args):
        """Update slider graphics"""
        # Update background track
        self.bg_track.pos = (self.x + self.padding, self.center_y - dp(2))
        self.bg_track.size = (self.width - 2*self.padding, dp(4))
        
        # Update active track
        active_width = (self.width - 2*self.padding) * (self.value - self.min) / (self.max - self.min) if (self.max - self.min) != 0 else 0
        self.active_track.pos = (self.x + self.padding, self.center_y - dp(2))
        self.active_track.size = (active_width, dp(4))