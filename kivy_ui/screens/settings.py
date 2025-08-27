"""
Settings screen for the Kivy UI
Following best practices for 2025
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp

from kivy_ui.components.cards import ConfigCard
from kivy_ui.components.buttons import ModernButton
from kivy_ui.themes.colors import COLORS, FONTS

class SettingsScreen(Screen):
    """Settings screen for API configuration"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_ui()
        
    def create_ui(self):
        """Create the settings UI"""
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        title = Label(
            text="Settings",
            font_size=FONTS['h1'],
            color=COLORS['text_primary'],
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        
        main_layout.add_widget(header)
        
        # Content area with scroll
        self.scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(20), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # API Configuration Card
        api_card = ConfigCard(title="API Configuration")
        
        # Spotify API Section
        spotify_section = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, height=dp(200))
        
        spotify_title = Label(
            text="Spotify API Credentials",
            font_size=FONTS['h3'],
            color=COLORS['text_primary'],
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        spotify_title.bind(size=spotify_title.setter('text_size'))
        spotify_section.add_widget(spotify_title)
        
        # Client ID
        client_id_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        client_id_label = Label(
            text="Client ID:",
            font_size=FONTS['body'],
            color=COLORS['text_secondary'],
            size_hint_x=None,
            width=dp(150),
            halign='left',
            valign='middle'
        )
        client_id_label.bind(size=client_id_label.setter('text_size'))
        self.client_id_input = TextInput(
            multiline=False,
            password=False,
            background_color=COLORS['bg_tertiary'],
            foreground_color=COLORS['text_primary']
        )
        client_id_layout.add_widget(client_id_label)
        client_id_layout.add_widget(self.client_id_input)
        spotify_section.add_widget(client_id_layout)
        
        # Client Secret
        client_secret_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        client_secret_label = Label(
            text="Client Secret:",
            font_size=FONTS['body'],
            color=COLORS['text_secondary'],
            size_hint_x=None,
            width=dp(150),
            halign='left',
            valign='middle'
        )
        client_secret_label.bind(size=client_secret_label.setter('text_size'))
        self.client_secret_input = TextInput(
            multiline=False,
            password=True,
            background_color=COLORS['bg_tertiary'],
            foreground_color=COLORS['text_primary']
        )
        client_secret_layout.add_widget(client_secret_label)
        client_secret_layout.add_widget(self.client_secret_input)
        spotify_section.add_widget(client_secret_layout)
        
        # Redirect URI
        redirect_uri_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        redirect_uri_label = Label(
            text="Redirect URI:",
            font_size=FONTS['body'],
            color=COLORS['text_secondary'],
            size_hint_x=None,
            width=dp(150),
            halign='left',
            valign='middle'
        )
        redirect_uri_label.bind(size=redirect_uri_label.setter('text_size'))
        self.redirect_uri_input = TextInput(
            multiline=False,
            text="http://127.0.0.1:8888/callback",
            background_color=COLORS['bg_tertiary'],
            foreground_color=COLORS['text_primary']
        )
        redirect_uri_layout.add_widget(redirect_uri_label)
        redirect_uri_layout.add_widget(self.redirect_uri_input)
        spotify_section.add_widget(redirect_uri_layout)
        
        api_card.add_widget(spotify_section)
        
        # SoundStat API Section
        soundstat_section = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=None, height=dp(120))
        
        soundstat_title = Label(
            text="SoundStat API Key",
            font_size=FONTS['h3'],
            color=COLORS['text_primary'],
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        soundstat_title.bind(size=soundstat_title.setter('text_size'))
        soundstat_section.add_widget(soundstat_title)
        
        soundstat_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        soundstat_label = Label(
            text="API Key:",
            font_size=FONTS['body'],
            color=COLORS['text_secondary'],
            size_hint_x=None,
            width=dp(150),
            halign='left',
            valign='middle'
        )
        soundstat_label.bind(size=soundstat_label.setter('text_size'))
        self.soundstat_input = TextInput(
            multiline=False,
            password=True,
            background_color=COLORS['bg_tertiary'],
            foreground_color=COLORS['text_primary']
        )
        soundstat_layout.add_widget(soundstat_label)
        soundstat_layout.add_widget(self.soundstat_input)
        soundstat_section.add_widget(soundstat_layout)
        
        api_card.add_widget(soundstat_section)
        
        content.add_widget(api_card)
        
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
        
        self.scroll.add_widget(content)
        main_layout.add_widget(self.scroll)
        
        # Add layout to screen
        self.add_widget(main_layout)
        
        # Force scroll to top after the UI is built
        from kivy.clock import Clock
        Clock.schedule_once(self.scroll_to_top, 0.2)
        
    def scroll_to_top(self, *args):
        """Scroll to the top of the view"""
        if hasattr(self, 'scroll'):
            # Force update of scroll view
            self.scroll.update_from_scroll()
            # Scroll to top
            self.scroll.scroll_y = 1.0