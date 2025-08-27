"""
Settings screen for the Kivy UI
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class SettingsScreen(Screen):
    """Settings screen for API configuration"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_ui()
        
    def create_ui(self):
        """Create the settings UI"""
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title_label = Label(
            text="API Configuration",
            font_size=24,
            size_hint_y=None,
            height=50
        )
        layout.add_widget(title_label)
        
        # Spotify API Section
        spotify_title = Label(
            text="Spotify API Credentials",
            font_size=18,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(spotify_title)
        
        # Client ID
        client_id_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        client_id_label = Label(text="Client ID:", size_hint_x=0.3)
        self.client_id_input = TextInput(size_hint_x=0.7)
        client_id_layout.add_widget(client_id_label)
        client_id_layout.add_widget(self.client_id_input)
        layout.add_widget(client_id_layout)
        
        # Client Secret
        client_secret_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        client_secret_label = Label(text="Client Secret:", size_hint_x=0.3)
        self.client_secret_input = TextInput(size_hint_x=0.7, password=True)
        client_secret_layout.add_widget(client_secret_label)
        client_secret_layout.add_widget(self.client_secret_input)
        layout.add_widget(client_secret_layout)
        
        # Redirect URI
        redirect_uri_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        redirect_uri_label = Label(text="Redirect URI:", size_hint_x=0.3)
        self.redirect_uri_input = TextInput(size_hint_x=0.7, text="http://127.0.0.1:8888/callback")
        redirect_uri_layout.add_widget(redirect_uri_label)
        redirect_uri_layout.add_widget(self.redirect_uri_input)
        layout.add_widget(redirect_uri_layout)
        
        # SoundStat API Section
        soundstat_title = Label(
            text="SoundStat API Key",
            font_size=18,
            size_hint_y=None,
            height=40
        )
        layout.add_widget(soundstat_title)
        
        soundstat_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40)
        soundstat_label = Label(text="API Key:", size_hint_x=0.3)
        self.soundstat_input = TextInput(size_hint_x=0.7, password=True)
        soundstat_layout.add_widget(soundstat_label)
        soundstat_layout.add_widget(self.soundstat_input)
        layout.add_widget(soundstat_layout)
        
        # Save button
        save_btn = Button(
            text="Save Configuration",
            size_hint_y=None,
            height=50
        )
        # In a full implementation, this would save the configuration
        # save_btn.bind(on_press=self.save_config)
        layout.add_widget(save_btn)
        
        # Add layout to screen
        self.add_widget(layout)