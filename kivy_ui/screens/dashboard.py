"""
Dashboard screen for the Kivy UI
Following best practices for 2025
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.clock import Clock

from kivy_ui.components.cards import PlaylistCard, StatCard
from kivy_ui.components.buttons import ModernButton
from kivy_ui.themes.colors import COLORS, FONTS

class DashboardScreen(Screen):
    """Dashboard screen showing daily playlist info"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_ui()
        
    def create_ui(self):
        """Create the dashboard UI"""
        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        
        # Header
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        
        title = Label(
            text="Dashboard",
            font_size=FONTS['h1'],
            color=COLORS['text_primary'],
            halign='left',
            valign='middle'
        )
        title.bind(size=title.setter('text_size'))
        header.add_widget(title)
        
        # Refresh button
        refresh_btn = ModernButton(
            text="Refresh Playlist",
            size_hint_x=None,
            width=dp(150)
        )
        # In a full implementation, this would call the refresh function
        # refresh_btn.bind(on_press=self.refresh_playlist)
        header.add_widget(refresh_btn)
        
        main_layout.add_widget(header)
        
        # Content area with scroll
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', spacing=dp(20), size_hint_y=None)
        content.bind(minimum_height=content.setter('height'))
        
        # Welcome card
        welcome_card = BoxLayout(
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10),
            size_hint_y=None,
            height=dp(150)
        )
        
        welcome_title = Label(
            text="Welcome to SpotifyTrueDaily",
            font_size=FONTS['h2'],
            color=COLORS['text_primary'],
            halign='center'
        )
        welcome_title.bind(size=welcome_title.setter('text_size'))
        welcome_card.add_widget(welcome_title)
        
        welcome_desc = Label(
            text="Your daily playlist is automatically updated with your recent tracks, top songs, and podcast episodes.",
            font_size=FONTS['body'],
            color=COLORS['text_secondary'],
            halign='center'
        )
        welcome_desc.bind(size=welcome_desc.setter('text_size'))
        welcome_card.add_widget(welcome_desc)
        
        content.add_widget(welcome_card)
        
        # Stats cards
        stats_layout = GridLayout(cols=3, spacing=dp(15), size_hint_y=None, height=dp(120))
        
        # In a real app, these would be populated with actual data
        stats = [
            {"title": "Total Tracks", "value": "0", "description": "All tracks in playlist"},
            {"title": "Songs", "value": "0", "description": "Music tracks"},
            {"title": "Podcasts", "value": "0", "description": "Podcast episodes"}
        ]
        
        for stat in stats:
            stat_card = StatCard(
                title=stat["title"],
                value=stat["value"],
                description=stat["description"]
            )
            stats_layout.add_widget(stat_card)
            
        content.add_widget(stats_layout)
        
        # Recent activity section
        activity_header = BoxLayout(size_hint_y=None, height=dp(40))
        activity_title = Label(
            text="Recent Activity",
            font_size=FONTS['h3'],
            color=COLORS['text_primary'],
            halign='left'
        )
        activity_title.bind(size=activity_title.setter('text_size'))
        activity_header.add_widget(activity_title)
        content.add_widget(activity_header)
        
        # Playlist cards
        playlists_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(300))
        
        # In a real app, these would be populated with actual playlists
        for i in range(3):
            playlist_card = PlaylistCard(
                title=f"Playlist {i+1}",
                track_count=f"{i*10 + 5} tracks",
                image_source=None  # Would be an actual image path
            )
            playlists_layout.add_widget(playlist_card)
            
        content.add_widget(playlists_layout)
        
        scroll.add_widget(content)
        main_layout.add_widget(scroll)
        
        # Add layout to screen
        self.add_widget(main_layout)