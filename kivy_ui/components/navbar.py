"""
Navbar component for navigation
Following best practices for 2025
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy_ui.themes.colors import COLORS

class NavItem(ToggleButton):
    """Navigation item with modern styling"""
    
    def __init__(self, text, icon=None, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.group = 'nav'
        self.size_hint_y = None
        self.height = dp(50)
        self.background_color = (0, 0, 0, 0)  # Transparent
        self.color = COLORS['text_secondary']
        
        # Create background
        with self.canvas.before:
            self.bg_color = Color(*COLORS['bg_primary'])
            self.bg = Rectangle(pos=self.pos, size=self.size)
            
        self.bind(pos=self.update_bg, size=self.update_bg)
        
    def update_bg(self, *args):
        """Update background position and size"""
        self.bg.pos = self.pos
        self.bg.size = self.size
        
    def on_state(self, instance, value):
        """Change color based on state"""
        if value == 'down':
            self.color = COLORS['accent_violet']
            self.bg_color.rgba = COLORS['bg_tertiary']
        else:
            self.color = COLORS['text_secondary']
            self.bg_color.rgba = COLORS['bg_primary']

class Navbar(BoxLayout):
    """Modern sidebar navigation"""
    
    def __init__(self, on_nav_item_pressed=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_x = None
        self.width = dp(250)
        self.spacing = dp(5)
        
        # Callback for navigation item press
        self.on_nav_item_pressed = on_nav_item_pressed
        
        # Create header
        self.create_header()
        
        # Create navigation items
        self.create_nav_items()
        
        # Create footer
        self.create_footer()
        
    def create_header(self):
        """Create navbar header"""
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            padding=[dp(15), dp(10)]
        )
        
        # App title
        title = Button(
            text='SpotifyTrueDaily',
            background_color=(0, 0, 0, 0),
            color=COLORS['text_primary'],
            font_size='18sp',
            halign='left',
            text_size=(None, None)
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        
        self.add_widget(header)
        
    def create_nav_items(self):
        """Create navigation items"""
        nav_items = [
            {"text": "Dashboard", "screen": "dashboard", "icon": "🏠"},
            {"text": "Playlist Configuration", "screen": "playlist_config", "icon": "🎵"},
            {"text": "Settings", "screen": "settings", "icon": "⚙️"},
        ]
        
        # Create a group for the toggle buttons
        self.nav_buttons = []
        
        for item in nav_items:
            nav_item = NavItem(
                text=f"{item['icon']}  {item['text']}",
                on_press=lambda x, screen=item["screen"]: self.on_item_press(screen)
            )
            self.nav_buttons.append(nav_item)
            self.add_widget(nav_item)
            
        # Set the first button as active by default
        if self.nav_buttons:
            self.nav_buttons[0].state = 'down'
            
    def create_footer(self):
        """Create navbar footer"""
        # Add a spacer to push footer to bottom
        spacer = Widget()
        self.add_widget(spacer)
        
        # Footer with version info
        footer = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(60),
            padding=[dp(15), dp(10)]
        )
        
        version = Button(
            text='Version 1.0',
            background_color=(0, 0, 0, 0),
            color=COLORS['text_disabled'],
            font_size='12sp',
            halign='left'
        )
        footer.add_widget(version)
        
        self.add_widget(footer)
        
    def on_item_press(self, screen_name):
        """Handle item press"""
        if self.on_nav_item_pressed:
            self.on_nav_item_pressed(screen_name)