"""
Navbar component for navigation
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle

class Navbar(BoxLayout):
    """Modern sidebar navigation with collapse/expand functionality"""
    
    def __init__(self, on_nav_item_pressed=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_x = None
        self.width = 200
        
        # Callback for navigation item press
        self.on_nav_item_pressed = on_nav_item_pressed
        
        # Create navigation items
        self.create_nav_items()
        
    def create_nav_items(self):
        """Create navigation items"""
        nav_items = [
            {"text": "Dashboard", "screen": "dashboard"},
            {"text": "Playlist Configuration", "screen": "playlist_config"},
            {"text": "Settings", "screen": "settings"},
        ]
        
        for item in nav_items:
            btn = Button(
                text=item["text"],
                size_hint_y=None,
                height=50,
                background_color=(0.118, 0.118, 0.118, 1),  # bg_tertiary
                color=(1, 1, 1, 1),  # text_primary
                on_press=lambda x, screen=item["screen"]: self.on_item_press(screen)
            )
            self.add_widget(btn)
            
    def on_item_press(self, screen_name):
        """Handle item press"""
        if self.on_nav_item_pressed:
            self.on_nav_item_pressed(screen_name)