"""
Navbar component for navigation
Following best practices for 2025
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy_ui.themes.colors import COLORS

class NavItem(BoxLayout):
    """Navigation item with modern styling"""
    
    def __init__(self, text, icon_path=None, on_press=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(50)
        self.spacing = dp(10)
        self.padding = [dp(15), 0]
        self.on_press_callback = on_press
        self.is_active = False
        
        # Create background
        with self.canvas.before:
            self.bg_color = Color(*COLORS['bg_primary'])
            self.bg = Rectangle(pos=self.pos, size=self.size)
            
        self.bind(pos=self.update_bg, size=self.update_bg)
        
        # Add icon if provided
        if icon_path:
            icon = Image(source=icon_path, size_hint_x=None, width=dp(24), height=dp(24))
            # Remove deprecated properties
            # icon.allow_stretch = True
            # icon.keep_ratio = True
            self.add_widget(icon)
        
        # Add text
        self.text_label = Button(
            text=text,
            background_color=(0, 0, 0, 0),
            color=COLORS['text_secondary'],
            font_size='14sp',
            halign='left',
            text_size=(None, None)
        )
        self.text_label.bind(size=self.text_label.setter('text_size'))
        self.text_label.bind(on_press=self.on_item_press)
        self.add_widget(self.text_label)
        
    def update_bg(self, *args):
        """Update background position and size"""
        self.bg.pos = self.pos
        self.bg.size = self.size
        
    def set_active(self, active):
        """Set the active state of the navigation item"""
        self.is_active = active
        if active:
            self.text_label.color = COLORS['accent_violet']
            self.bg_color.rgba = COLORS['bg_tertiary']
        else:
            self.text_label.color = COLORS['text_secondary']
            self.bg_color.rgba = COLORS['bg_primary']
            
    def on_item_press(self, instance):
        """Handle item press"""
        if self.on_press_callback:
            self.on_press_callback(None)

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
        # Using custom PNG icons for better compatibility
        nav_items = [
            {"text": "Dashboard", "screen": "dashboard", "icon_path": "kivy_ui/assets/icons/home.png"},
            {"text": "Playlist Configuration", "screen": "playlist_config", "icon_path": "kivy_ui/assets/icons/music.png"},
            {"text": "Settings", "screen": "settings", "icon_path": "kivy_ui/assets/icons/settings.png"},
        ]
        
        # Create navigation items
        self.nav_buttons = []
        
        for i, item in enumerate(nav_items):
            # Create a wrapper function to capture the screen name correctly
            def make_callback(screen_name=item["screen"]):
                return lambda instance: self.on_item_press(screen_name)
            
            nav_item = NavItem(
                text=item["text"],
                icon_path=item["icon_path"],
                on_press=make_callback()
            )
            self.nav_buttons.append(nav_item)
            self.add_widget(nav_item)
            
        # Set the first button as active by default
        if self.nav_buttons:
            self.set_active_item(0)
            
    def set_active_item(self, index):
        """Set the active navigation item"""
        for i, button in enumerate(self.nav_buttons):
            button.set_active(i == index)
            
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
