"""
Dashboard screen for the Kivy UI
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

class DashboardScreen(Screen):
    """Dashboard screen showing daily playlist info"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_ui()
        
    def create_ui(self):
        """Create the dashboard UI"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Welcome section
        welcome_label = Label(
            text="Welcome to SpotifyTrueDaily",
            font_size=24,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(welcome_label)
        
        description_label = Label(
            text="Your daily playlist is automatically updated with your recent tracks, top songs, and podcast episodes.",
            halign='center',
            text_size=(self.width - 40, None)
        )
        layout.add_widget(description_label)
        
        # Refresh button
        refresh_btn = Button(
            text="Refresh Daily Playlist",
            size_hint_y=None,
            height=50
        )
        # In a full implementation, this would call the refresh function
        # refresh_btn.bind(on_press=self.refresh_playlist)
        layout.add_widget(refresh_btn)
        
        # Add layout to screen
        self.add_widget(layout)