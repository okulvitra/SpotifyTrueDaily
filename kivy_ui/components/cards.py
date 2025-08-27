"""
Modern UI components for the Kivy application
Following best practices for 2025
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty

from kivy_ui.themes.colors import COLORS, FONTS

class ModernCard(BoxLayout):
    """Base class for modern cards with rounded corners and shadow"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(15)
        self.spacing = dp(10)
        self.size_hint_y = None
        
        # Set up canvas for drawing
        with self.canvas.before:
            # Shadow
            Color(*COLORS['shadow'])
            self.shadow = RoundedRectangle(
                pos=(self.x + dp(2), self.y - dp(2)),
                size=self.size,
                radius=[dp(10)]
            )
            # Card background
            Color(*COLORS['bg_card'])
            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )
            
        self.bind(pos=self.update_graphics, size=self.update_graphics)
        
    def update_graphics(self, *args):
        """Update card graphics when position or size changes"""
        self.shadow.pos = (self.x + dp(2), self.y - dp(2))
        self.shadow.size = self.size
        self.bg.pos = self.pos
        self.bg.size = self.size

class PlaylistCard(ModernCard):
    """Card for displaying playlist information"""
    
    title = StringProperty("Playlist Title")
    track_count = StringProperty("0 tracks")
    
    def __init__(self, title="", track_count="", image_source=None, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.track_count = track_count
        self.height = dp(80)
        
        # Create content layout
        content = BoxLayout(orientation='horizontal', spacing=dp(10))
        
        # Placeholder for album art
        if image_source:
            from kivy.uix.image import Image
            image = Image(source=image_source, size_hint_x=None, width=dp(60))
            content.add_widget(image)
        else:
            # Placeholder rectangle
            placeholder = BoxLayout(size_hint_x=None, width=dp(60))
            with placeholder.canvas.before:
                Color(*COLORS['bg_tertiary'])
                Rectangle(pos=placeholder.pos, size=placeholder.size)
            placeholder.bind(pos=lambda instance, value: self.update_placeholder(instance), 
                            size=lambda instance, value: self.update_placeholder(instance))
            content.add_widget(placeholder)
        
        # Text information
        text_layout = BoxLayout(orientation='vertical', spacing=dp(5))
        
        title_label = Label(
            text=self.title,
            font_size=FONTS['body_large'],
            color=COLORS['text_primary'],
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        text_layout.add_widget(title_label)
        
        track_label = Label(
            text=self.track_count,
            font_size=FONTS['caption'],
            color=COLORS['text_secondary'],
            halign='left'
        )
        track_label.bind(size=track_label.setter('text_size'))
        text_layout.add_widget(track_label)
        
        content.add_widget(text_layout)
        self.add_widget(content)
        
    def update_placeholder(self, instance):
        """Update placeholder graphics"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            Color(*COLORS['bg_tertiary'])
            Rectangle(pos=instance.pos, size=instance.size)

class StatCard(ModernCard):
    """Card for displaying statistics"""
    
    title = StringProperty("Title")
    value = StringProperty("0")
    description = StringProperty("Description")
    
    def __init__(self, title="", value="", description="", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.value = value
        self.description = description
        self.height = dp(120)
        
        # Title
        title_label = Label(
            text=self.title,
            font_size=FONTS['caption'],
            color=COLORS['text_secondary'],
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.add_widget(title_label)
        
        # Value
        value_label = Label(
            text=self.value,
            font_size=FONTS['h1'],
            color=COLORS['accent_violet'],
            halign='left'
        )
        value_label.bind(size=value_label.setter('text_size'))
        self.add_widget(value_label)
        
        # Description
        desc_label = Label(
            text=self.description,
            font_size=FONTS['caption'],
            color=COLORS['text_disabled'],
            halign='left'
        )
        desc_label.bind(size=desc_label.setter('text_size'))
        self.add_widget(desc_label)

class ConfigCard(ModernCard):
    """Card for configuration sections"""
    
    title = StringProperty("Configuration")
    description = StringProperty("")
    
    def __init__(self, title="", description="", **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.description = description
        self.orientation = 'vertical'
        # Initial height - will be updated when content is added
        self.height = dp(60)  # Height of header only initially
        
        # Header
        self.header = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(60))
        
        title_label = Label(
            text=self.title,
            font_size=FONTS['h2'],
            color=COLORS['text_primary'],
            halign='left'
        )
        title_label.bind(size=title_label.setter('text_size'))
        self.header.add_widget(title_label)
        
        if self.description:
            desc_label = Label(
                text=self.description,
                font_size=FONTS['body'],
                color=COLORS['text_secondary'],
                halign='left'
            )
            desc_label.bind(size=desc_label.setter('text_size'))
            self.header.add_widget(desc_label)
            
        self.add_widget(self.header)
        
        # Bind to update height when children are added
        self.bind(children=self.update_height)
        
    def update_height(self, *args):
        """Update the height of the card based on its content"""
        # Start with header height
        total_height = self.header.height + self.padding[1] * 2  # padding top and bottom
        
        # Add height of all content widgets (excluding header)
        for child in self.children:
            if child != self.header:
                if hasattr(child, 'height') and hasattr(child, 'size_hint_y'):
                    if child.size_hint_y is None:
                        total_height += child.height + self.spacing
                    elif hasattr(child, 'minimum_height'):
                        total_height += child.minimum_height + self.spacing
                        
        self.height = total_height