"""
Playlist configuration screen for the Kivy UI
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider

class PlaylistConfigScreen(Screen):
    """Playlist configuration screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_ui()
        
    def create_ui(self):
        """Create the playlist configuration UI"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title_label = Label(
            text="Playlist Configuration",
            font_size=24,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title_label)
        
        # Description
        description_label = Label(
            text="Configure how many tracks to include from each category in your daily playlist",
            halign='center',
            text_size=(self.width - 40, None)
        )
        layout.add_widget(description_label)
        
        # Configuration items
        config_items = [
            ("Recent Tracks", "Number of recently played tracks to include"),
            ("Top Tracks", "Number of your most popular tracks to include"),
            ("Podcast Episodes", "Number of recent podcast episodes to include"),
            ("Library Recommendations", "Number of random tracks from your library"),
            ("SoundStat Recommendations", "Number of tracks recommended by SoundStat"),
            ("SoundStat Seed Tracks", "Number of tracks to use as seeds for SoundStat recommendations")
        ]
        
        for title, description in config_items:
            item_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
            
            # Title and description
            title_label = Label(text=title, font_size=16, size_hint_y=None, height=25)
            desc_label = Label(text=description, font_size=12, size_hint_y=None, height=20)
            item_layout.add_widget(title_label)
            item_layout.add_widget(desc_label)
            
            # Slider
            slider = Slider(min=0, max=20, value=5)
            item_layout.add_widget(slider)
            
            layout.add_widget(item_layout)
        
        # Add layout to screen
        self.add_widget(layout)