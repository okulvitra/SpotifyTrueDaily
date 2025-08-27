"""
Playlist configuration screen for the Kivy UI
Following best practices for 2025
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp

from kivy_ui.components.cards import ConfigCard
from kivy_ui.components.sliders import ModernSlider
from kivy_ui.components.buttons import ModernButton
from kivy_ui.themes.colors import COLORS, FONTS

class PlaylistConfigScreen(Screen):
    """Playlist configuration screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_ui()
        
    def create_ui(self):
        """Create the playlist configuration UI"""
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        title = Label(
            text="Playlist Configuration",
            font_size=FONTS['h1'],
            color=COLORS['text_primary'],
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        
        main_layout.add_widget(header)
        
        # Content area with scroll
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(20), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Configuration Card
        config_card = ConfigCard(
            title="Content Configuration",
            description="Configure how many tracks to include from each category in your daily playlist"
        )
        
        # Configuration items
        config_items = [
            {
                "title": "Recent Tracks", 
                "description": "Number of recently played tracks to include",
                "min": 0,
                "max": 20,
                "default": 5
            },
            {
                "title": "Top Tracks", 
                "description": "Number of your most popular tracks to include",
                "min": 0,
                "max": 20,
                "default": 5
            },
            {
                "title": "Podcast Episodes", 
                "description": "Number of recent podcast episodes to include",
                "min": 0,
                "max": 10,
                "default": 3
            },
            {
                "title": "Library Recommendations", 
                "description": "Number of random tracks from your library",
                "min": 0,
                "max": 10,
                "default": 2
            },
            {
                "title": "SoundStat Recommendations", 
                "description": "Number of tracks recommended by SoundStat",
                "min": 0,
                "max": 10,
                "default": 3
            },
            {
                "title": "SoundStat Seed Tracks", 
                "description": "Number of tracks to use as seeds for SoundStat recommendations",
                "min": 1,
                "max": 5,
                "default": 2
            }
        ]
        
        for item in config_items:
            # Item layout
            item_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
            
            # Title and description
            title_label = Label(
                text=item["title"],
                font_size=FONTS['h3'],
                color=COLORS['text_primary'],
                halign='left',
                size_hint_y=None,
                height=dp(25)
            )
            title_label.bind(size=title_label.setter('text_size'))
            item_layout.add_widget(title_label)
            
            desc_label = Label(
                text=item["description"],
                font_size=FONTS['body'],
                color=COLORS['text_secondary'],
                halign='left',
                size_hint_y=None,
                height=dp(20)
            )
            desc_label.bind(size=desc_label.setter('text_size'))
            item_layout.add_widget(desc_label)
            
            # Slider
            slider = ModernSlider(
                min=item["min"],
                max=item["max"],
                value=item["default"]
            )
            item_layout.add_widget(slider)
            
            config_card.add_widget(item_layout)
            
        content.add_widget(config_card)
        
        # Save button
        save_btn = ModernButton(
            text="Save Configuration",
            size_hint_x=None,
            width=dp(200),
            height=dp(50)
        )
        # In a full implementation, this would save the configuration
        # save_btn.bind(on_press=self.save_config)
        
        button_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        button_container.add_widget(Widget())  # Spacer
        button_container.add_widget(save_btn)
        button_container.add_widget(Widget())  # Spacer
        
        content.add_widget(button_container)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        # Add layout to screen
        self.add_widget(main_layout)