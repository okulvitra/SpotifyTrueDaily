"""
Modern SpotifyTrueDaily Application
Clean interface for refreshing daily playlists
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import sys
import os
import traceback
from datetime import datetime

# Import modern UI components
from modern_ui import (
    ModernTheme, ModernButton, Sidebar, 
    SearchBar, LoadingSpinner, PlaylistCard, ModernScrollableFrame
)

# Import existing modules
try:
    from playlist_manager import ConfigError as PM_ConfigError
    import playlist_manager as pm
    playlist_manager_module = pm
except ImportError as e:
    print(f"Error importing playlist_manager: {e}")
    playlist_manager_module = None

# Import Spotify API client
try:
    import spotipy
    from spotipy.oauth2 import SpotifyOAuth
    SPOTIPY_AVAILABLE = True
except ImportError:
    SPOTIPY_AVAILABLE = False
    print("Warning: spotipy not available. Some features may not work.")

# Configuration functions
def save_config_values_to_file(config_data, app_instance=None):
    """Save configuration values to config.py file"""
    import os
    
    CONFIG_FILENAME = "config.py"
    
    content = f"""# config.py - VOS INFORMATIONS CONFIDENTIELLES ET PRÉFÉRENCES
# Ce fichier est généré par l'application SpotifyTrueDaily.
# Configuration Spotify
SPOTIPY_CLIENT_ID = '{config_data.get("SPOTIPY_CLIENT_ID", "")}'
SPOTIPY_CLIENT_SECRET = '{config_data.get("SPOTIPY_CLIENT_SECRET", "")}'
SPOTIPY_REDIRECT_URI = '{config_data.get("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")}'
# Configuration SoundStat
SOUNDSTAT_API_KEY = '{config_data.get("SOUNDSTAT_API_KEY", "")}'
# Paramètres de contenu de la Playlist Journalière
MAX_RECENT_TRACKS = {int(config_data.get("MAX_RECENT_TRACKS", 5))}
MAX_TOP_TRACKS = {int(config_data.get("MAX_TOP_TRACKS", 5))}
MAX_PODCAST_EPISODES = {int(config_data.get("MAX_PODCAST_EPISODES", 3))}
MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY = {int(config_data.get("MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY", 2))}
MAX_SOUNDSTAT_RECOMMENDATIONS = {int(config_data.get("MAX_SOUNDSTAT_RECOMMENDATIONS", 3))}
SOUNDSTAT_SEED_TRACK_COUNT = {int(config_data.get("SOUNDSTAT_SEED_TRACK_COUNT", 2))}
"""
    
    try:
        with open(CONFIG_FILENAME, 'w', encoding='utf-8') as f:
            f.write(content)
            
        if app_instance:
            app_instance.show_info("Settings", f"Configuration sauvegardée dans {CONFIG_FILENAME} !\n\n"
                                          "Les nouveaux paramètres seront utilisés au prochain lancement de la mise à jour.")
    except Exception as e:
        if app_instance:
            app_instance.show_error("Erreur de sauvegarde", f"Impossible de sauvegarder la configuration : {e}")

class ModernSpotifyApp(ctk.CTk):
    """Main application focused on daily playlist refresh"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize navigation history
        self.navigation_history = []
        
        # Apply modern theme
        ModernTheme.apply_theme()
        
        # Configure window
        self.title("SpotifyTrueDaily - Daily Playlist Refresh")
        self.geometry("900x700")
        self.minsize(700, 500)
        
        # Configure grid
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)  # Sidebar fixed width
        self.grid_columnconfigure(1, weight=1)  # Main content expands
        
        # Initialize state
        self.playlists = []
        self.is_loading = False
        self.daily_playlist = None
        self.daily_playlist_tracks = []
        
        # Setup UI
        self.setup_ui()
        
        # Load initial data
        self.load_initial_data()
        
    def setup_ui(self):
        """Setup the clean, focused UI"""
        # Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Bind navigation events with detailed tracing
        print("Binding navigation events")
        
        def make_handler(name, func):
            def handler(e):
                print(f"\n--- {name} EVENT HANDLER ---")
                print(f"Event type: {e.type}")
                print(f"Widget: {e.widget}")
                print(f"Time: {e.time}")
                self.clear_content()
                func()
                self.content_frame.update_idletasks()
                self.update()
            return handler
        
        self.bind("<<Nav_dashboard>>", make_handler("DASHBOARD", self.show_dashboard))
        self.bind("<<Nav_playlist_config>>", make_handler("PLAYLIST_CONFIG", self.show_playlist_configuration))
        self.bind("<<Nav_settings>>", make_handler("SETTINGS", self.show_settings))
        self.bind("<<Nav_about>>", make_handler("ABOUT", self.show_about))
        
        # Force initial dashboard view
        self.after(100, self.show_dashboard)
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self, fg_color=ModernTheme.COLORS['bg_primary'])
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        self.setup_header()
        
        # Content frame
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color=ModernTheme.COLORS['bg_primary'])
        self.content_frame.grid(row=2, column=0, sticky="nsew", pady=(20, 0))
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.update_idletasks()
        
        # Loading spinner
        self.loading_spinner = LoadingSpinner(self.main_frame)
        
    def setup_header(self):
        """Setup the header with title and last update info"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(0, weight=0)  # Back button
        header_frame.grid_columnconfigure(1, weight=1)  # Title
        header_frame.grid_columnconfigure(2, weight=0)  # Refresh button
        
        # Back button
        self.back_button = ModernButton(
            header_frame,
            text="← Back",
            command=self.go_back,
            width=60,
            height=32
        )
        self.back_button.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0,10))
        self.back_button.grid_remove()  # Initially hidden
        
        # Title
        title = ctk.CTkLabel(
            header_frame,
            text="Daily Playlist Refresh",
            font=("Segoe UI", 18, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        title.grid(row=0, column=1, sticky="w")
        
        # Last update info
        self.last_update_label = ctk.CTkLabel(
            header_frame,
            text="Last updated: Never",
            font=("Segoe UI", 12),
            text_color=ModernTheme.COLORS['text_secondary']
        )
        self.last_update_label.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Refresh button
        refresh_btn = ModernButton(
            header_frame,
            text="Refresh Now",
            command=self.refresh_daily_playlist,
            width=120,
            height=32
        )
        refresh_btn.grid(row=0, column=1, rowspan=2, sticky="e")
        
    def show_dashboard(self):
        """Show dashboard view with daily playlist info"""
        print("Showing dashboard")
        self.clear_content()
        print("Creating dashboard widgets")
        self.update()
        
        # Dashboard frame
        dashboard_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        dashboard_frame.pack(fill="both", expand=True)
        
        # Welcome section
        welcome_frame = ctk.CTkFrame(dashboard_frame, fg_color=ModernTheme.COLORS['bg_secondary'], corner_radius=8)
        welcome_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        welcome_title = ctk.CTkLabel(
            welcome_frame,
            text="Welcome to SpotifyTrueDaily",
            font=("Segoe UI", 16, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        welcome_title.pack(pady=10)
        
        welcome_text = ctk.CTkLabel(
            welcome_frame,
            text="Your daily playlist is automatically updated with your recent tracks, top songs, and podcast episodes.",
            font=("Segoe UI", 12),
            text_color=ModernTheme.COLORS['text_secondary']
        )
        welcome_text.pack(pady=(0, 10))
        
        # Daily playlist status
        if self.daily_playlist:
            self.create_playlist_status_card(dashboard_frame)
        else:
            self.create_no_playlist_card(dashboard_frame)
            
        # Quick actions
        actions_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
        actions_frame.pack(fill="x", padx=20, pady=10)
        
        actions_title = ctk.CTkLabel(
            actions_frame,
            text="Quick Actions",
            font=("Segoe UI", 14, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        actions_title.pack(anchor="w", pady=(0, 10))
        
        actions_grid = ctk.CTkFrame(actions_frame, fg_color="transparent")
        actions_grid.pack(fill="x")
        
        # Create playlist button
        create_btn = ModernButton(
            actions_grid,
            text="Create Daily Playlist",
            command=self.create_daily_playlist,
            width=150,
            height=35
        )
        create_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # View playlists button
        view_btn = ModernButton(
            actions_grid,
            text="View All Playlists",
            command=lambda: self.show_playlists(),
            width=150,
            height=35
        )
        view_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            actions_grid,
            text="Settings",
            command=lambda: self.show_settings(),
            width=150,
            height=35,
            corner_radius=6,
            border_width=0,
            font=("Segoe UI", 12),
            fg_color="transparent",
            hover_color=ModernTheme.COLORS['bg_tertiary'],
            text_color=ModernTheme.COLORS['text_secondary']
        )
        settings_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        # Configuration button
        config_btn = ModernButton(
            actions_grid,
            text="Playlist Configuration",
            command=lambda: self.show_playlist_configuration(),
            width=150,
            height=35
        )
        config_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
        
    def create_playlist_status_card(self, parent):
        """Create card showing daily playlist status"""
        status_card = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['bg_secondary'], corner_radius=8)
        status_card.pack(fill="x", padx=20, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(status_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=15)
        
        playlist_title = ctk.CTkLabel(
            header_frame,
            text=f"🎵 {self.daily_playlist['name']}",
            font=("Segoe UI", 16, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        playlist_title.pack(anchor="w")
        
        # Stats
        stats_frame = ctk.CTkFrame(status_card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Track counts
        total_tracks = len(self.daily_playlist_tracks)
        songs_count = sum(1 for track in self.daily_playlist_tracks if 'track' in track and track['track'])
        podcasts_count = total_tracks - songs_count
        
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(fill="x")
        
        # Total tracks
        total_label = ctk.CTkLabel(
            stats_grid,
            text="Total Tracks:",
            font=("Segoe UI", 11, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        total_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
        
        total_value = ctk.CTkLabel(
            stats_grid,
            text=str(total_tracks),
            font=("Segoe UI", 11),
            text_color=ModernTheme.COLORS['accent_violet']
        )
        total_value.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # Songs
        songs_label = ctk.CTkLabel(
            stats_grid,
            text="Songs:",
            font=("Segoe UI", 11, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        songs_label.grid(row=0, column=2, sticky="w", padx=5, pady=2)
        
        songs_value = ctk.CTkLabel(
            stats_grid,
            text=str(songs_count),
            font=("Segoe UI", 11),
            text_color=ModernTheme.COLORS['accent_violet']
        )
        songs_value.grid(row=0, column=3, sticky="w", padx=5, pady=2)
        
        # Podcasts
        podcasts_label = ctk.CTkLabel(
            stats_grid,
            text="Podcasts:",
            font=("Segoe UI", 11, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        podcasts_label.grid(row=0, column=4, sticky="w", padx=5, pady=2)
        
        podcasts_value = ctk.CTkLabel(
            stats_grid,
            text=str(podcasts_count),
            font=("Segoe UI", 11),
            text_color=ModernTheme.COLORS['accent_violet']
        )
        podcasts_value.grid(row=0, column=5, sticky="w", padx=5, pady=2)
        
        # Refresh button
        refresh_btn = ModernButton(
            status_card,
            text="Refresh Playlist",
            command=self.refresh_daily_playlist,
            width=150,
            height=35
        )
        refresh_btn.pack(pady=(0, 15))
        
    def create_no_playlist_card(self, parent):
        """Create card when no daily playlist exists"""
        no_playlist_card = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['bg_secondary'], corner_radius=8)
        no_playlist_card.pack(fill="x", padx=20, pady=10)
        
        # Header
        header_frame = ctk.CTkFrame(no_playlist_card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=15)
        
        title = ctk.CTkLabel(
            header_frame,
            text="No Daily Playlist Found",
            font=("Segoe UI", 16, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        title.pack(anchor="w")
        
        # Description
        desc_frame = ctk.CTkFrame(no_playlist_card, fg_color="transparent")
        desc_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        desc_text = ctk.CTkLabel(
            desc_frame,
            text="Create a daily playlist to automatically update it with your recent tracks, top songs, and podcast episodes.",
            font=("Segoe UI", 12),
            text_color=ModernTheme.COLORS['text_secondary'],
            wraplength=600
        )
        desc_text.pack(anchor="w")
        
        # Create button
        create_btn = ModernButton(
            no_playlist_card,
            text="Create Daily Playlist",
            command=self.create_daily_playlist,
            width=150,
            height=35
        )
        create_btn.pack(pady=(0, 15))
        
    def show_playlists(self):
        """Show all playlists view"""
        self.clear_content()
        
        # Header
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Your Playlists",
            font=("Segoe UI", 18, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        title.pack(anchor="w")
        
        # Search bar
        search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        search_bar = SearchBar(
            search_frame,
            on_search=self.search_playlists,
            width=300,
            height=35
        )
        search_bar.pack()
        
        # Playlists container
        self.playlists_container = ModernScrollableFrame(self.content_frame)
        self.playlists_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Load playlists
        self.load_playlists()
        
    def show_settings(self):
        """Show settings view with API configuration fields"""
        print("Showing settings")
        self.clear_content()
        print("Creating settings widgets")
        self.content_frame.update_idletasks()
        self.update()
        self.update()
        
        settings_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True)
        
        # Settings title
        title = ctk.CTkLabel(
            settings_frame,
            text="API Configuration",
            font=("Segoe UI", 18, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        title.pack(pady=(20, 10))

        # Configuration form
        form_frame = ctk.CTkFrame(settings_frame, fg_color=ModernTheme.COLORS['bg_secondary'], corner_radius=8)
        form_frame.pack(fill="x", padx=20, pady=10)

        # Spotify API Section
        spotify_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        spotify_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            spotify_frame,
            text="Spotify API Credentials",
            font=("Segoe UI", 14, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(anchor="w")

        # Client ID
        ctk.CTkLabel(
            spotify_frame,
            text="Client ID:",
            font=("Segoe UI", 12),
            text_color=ModernTheme.COLORS['text_secondary']
        ).pack(anchor="w", pady=(10, 0))
        self.client_id_entry = ctk.CTkEntry(
            spotify_frame,
            placeholder_text="Enter Spotify Client ID",
            width=300,
            fg_color=ModernTheme.COLORS['bg_primary']
        )
        self.client_id_entry.pack(anchor="w")

        # Client Secret
        ctk.CTkLabel(
            spotify_frame,
            text="Client Secret:",
            font=("Segoe UI", 12),
            text_color=ModernTheme.COLORS['text_secondary']
        ).pack(anchor="w", pady=(10, 0))
        self.client_secret_entry = ctk.CTkEntry(
            spotify_frame,
            placeholder_text="Enter Spotify Client Secret",
            width=300,
            fg_color=ModernTheme.COLORS['bg_primary'],
            show="•"
        )
        self.client_secret_entry.pack(anchor="w")

        # Redirect URI
        ctk.CTkLabel(
            spotify_frame,
            text="Redirect URI:",
            font=("Segoe UI", 12),
            text_color=ModernTheme.COLORS['text_secondary']
        ).pack(anchor="w", pady=(10, 0))
        self.redirect_uri_entry = ctk.CTkEntry(
            spotify_frame,
            placeholder_text="http://127.0.0.1:8888/callback",
            width=300,
            fg_color=ModernTheme.COLORS['bg_primary']
        )
        self.redirect_uri_entry.pack(anchor="w")

        # SoundStat API Section
        soundstat_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        soundstat_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(
            soundstat_frame,
            text="SoundStat API Key",
            font=("Segoe UI", 14, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        ).pack(anchor="w")

        self.soundstat_key_entry = ctk.CTkEntry(
            soundstat_frame,
            placeholder_text="Enter SoundStat API Key",
            width=300,
            fg_color=ModernTheme.COLORS['bg_primary'],
            show="•"
        )
        self.soundstat_key_entry.pack(anchor="w", pady=(10, 0))

        # Save button
        save_btn = ModernButton(
            form_frame,
            text="Save API Configuration",
            command=self.save_api_configuration,
            width=200,
            height=35
        )
        save_btn.pack(pady=20)

    def save_api_configuration(self):
        """Save API configuration to config.py"""
        config_data = {
            "SPOTIPY_CLIENT_ID": self.client_id_entry.get().strip(),
            "SPOTIPY_CLIENT_SECRET": self.client_secret_entry.get().strip(),
            "SPOTIPY_REDIRECT_URI": self.redirect_uri_entry.get().strip(),
            "SOUNDSTAT_API_KEY": self.soundstat_key_entry.get().strip()
        }
        
        print(f"Validating credentials: Client ID {'exists' if config_data['SPOTIPY_CLIENT_ID'] else 'missing'}, "
              f"Secret {'exists' if config_data['SPOTIPY_CLIENT_SECRET'] else 'missing'}")
        
        # Validate required fields
        if not config_data["SPOTIPY_CLIENT_ID"] or not config_data["SPOTIPY_CLIENT_SECRET"]:
            self.show_error("Spotify Client ID and Secret are required")
            return
            
        try:
            save_config_values_to_file(config_data, self)
            print("Config file updated successfully")
            
            # Force full configuration reload
            global playlist_manager_module
            if playlist_manager_module:
                print("Reloading playlist manager module...")
                import importlib
                importlib.reload(playlist_manager_module)
                # Clear any cached credentials
                if hasattr(playlist_manager_module, 'SPOTIPY_CLIENT_ID'):
                    print(f"New Client ID: {playlist_manager_module.SPOTIPY_CLIENT_ID[:3]}...")
                # Reinitialize Spotify client
                playlist_manager_module.authenticate_spotify = importlib.reload(playlist_manager_module).authenticate_spotify
                
            self.show_success("API configuration saved and reloaded!")
            # Refresh UI state
            self.after(1000, self.load_initial_data)
        except Exception as e:
            self.show_error(f"Failed to save configuration: {str(e)}")
        
    def show_about(self):
        """Show about view"""
        self.clear_content()
        
        about_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        about_frame.pack(fill="both", expand=True)
        
        # About title
        title = ctk.CTkLabel(
            about_frame,
            text="About SpotifyTrueDaily",
            font=("Segoe UI", 18, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        title.pack(pady=(20, 10))
        
        # App info
        info_frame = ctk.CTkFrame(about_frame, fg_color=ModernTheme.COLORS['bg_secondary'], corner_radius=8)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        app_name = ctk.CTkLabel(
            info_frame,
            text="SpotifyTrueDaily",
            font=("Segoe UI", 16, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        app_name.pack(pady=10)
        
        version = ctk.CTkLabel(
            info_frame,
            text="Version 1.0",
            font=("Segoe UI", 12),
            text_color=ModernTheme.COLORS['text_secondary']
        )
        version.pack()
        
        description = ctk.CTkLabel(
            info_frame,
            text="A modern application for creating and refreshing daily playlists on Spotify.\n\nFeatures:\n• Automatic daily playlist updates\n• Configurable track categories\n• Modern, Spotify-inspired UI\n• Integration with SoundStat recommendations",
            font=("Segoe UI", 12),
            text_color=ModernTheme.COLORS['text_secondary'],
            justify="left"
        )
        description.pack(padx=15, pady=10)
        
        # Credits
        credits_frame = ctk.CTkFrame(about_frame, fg_color=ModernTheme.COLORS['bg_secondary'], corner_radius=8)
        credits_frame.pack(fill="x", padx=20, pady=10)
        
        credits_title = ctk.CTkLabel(
            credits_frame,
            text="Credits",
            font=("Segoe UI", 14, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        credits_title.pack(pady=10)
        
        credits_text = ctk.CTkLabel(
            credits_frame,
            text="Created by okulvitra\n\nBuilt with:\n• CustomTkinter\n• Spotify Web API\n• SoundStat API",
            font=("Segoe UI", 12),
            text_color=ModernTheme.COLORS['text_secondary'],
            justify="left"
        )
        credits_text.pack(padx=15, pady=(0, 15))
        
    def show_playlist_configuration(self):
        """Show playlist configuration view"""
        print("Showing playlist config")
        self.clear_content()
        print("Creating config widgets")
        self.update()
        
        # Header
        header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Playlist Configuration",
            font=("Segoe UI", 18, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        title.pack(anchor="w")
        
        # Description
        desc_text = ctk.CTkLabel(
            header_frame,
            text="Configure how many tracks to include from each category in your daily playlist",
            font=("Segoe UI", 12),
            text_color=ModernTheme.COLORS['text_secondary']
        )
        desc_text.pack(anchor="w", pady=(5, 0))
        
        # Configuration cards container
        config_container = ModernScrollableFrame(self.content_frame)
        config_container.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
        # Create configuration cards
        self.create_config_cards(config_container)
        
    def create_config_cards(self, parent):
        """Create configuration cards for each content type"""
        # Recent tracks card
        recent_card = self.create_config_card(
            parent,
            title="Recent Tracks",
            description="Number of recently played tracks to include",
            icon="🎵",
            config_key="MAX_RECENT_TRACKS",
            default_value=5,
            min_value=0,
            max_value=20
        )
        recent_card.pack(fill="x", pady=5)
        
        # Top tracks card
        top_card = self.create_config_card(
            parent,
            title="Top Tracks",
            description="Number of your most popular tracks to include",
            icon="🏆",
            config_key="MAX_TOP_TRACKS",
            default_value=5,
            min_value=0,
            max_value=20
        )
        top_card.pack(fill="x", pady=5)
        
        # Podcast episodes card
        podcast_card = self.create_config_card(
            parent,
            title="Podcast Episodes",
            description="Number of recent podcast episodes to include",
            icon="🎙️",
            config_key="MAX_PODCAST_EPISODES",
            default_value=3,
            min_value=0,
            max_value=10
        )
        podcast_card.pack(fill="x", pady=5)
        
        # Library recommendations card
        library_card = self.create_config_card(
            parent,
            title="Library Recommendations",
            description="Number of random tracks from your library",
            icon="📚",
            config_key="MAX_RANDOM_RECOMMENDATIONS_FROM_LIBRARY",
            default_value=2,
            min_value=0,
            max_value=10
        )
        library_card.pack(fill="x", pady=5)
        
        # SoundStat recommendations card
        soundstat_card = self.create_config_card(
            parent,
            title="SoundStat Recommendations",
            description="Number of tracks recommended by SoundStat",
            icon="🎯",
            config_key="MAX_SOUNDSTAT_RECOMMENDATIONS",
            default_value=3,
            min_value=0,
            max_value=10
        )
        soundstat_card.pack(fill="x", pady=5)
        
        # SoundStat seed count card
        seed_card = self.create_config_card(
            parent,
            title="SoundStat Seed Tracks",
            description="Number of tracks to use as seeds for SoundStat recommendations",
            icon="🌱",
            config_key="SOUNDSTAT_SEED_TRACK_COUNT",
            default_value=2,
            min_value=1,
            max_value=5
        )
        seed_card.pack(fill="x", pady=5)
        
        # Save button
        save_frame = ctk.CTkFrame(parent, fg_color="transparent")
        save_frame.pack(fill="x", pady=(20, 0))
        
        save_btn = ModernButton(
            save_frame,
            text="Save Configuration",
            command=self.save_configuration,
            width=150,
            height=35
        )
        save_btn.pack()
        
    def create_config_card(self, parent, title, description, icon, config_key, default_value, min_value, max_value):
        """Create a configuration card for a specific setting"""
        card = ctk.CTkFrame(parent, fg_color=ModernTheme.COLORS['bg_secondary'], corner_radius=8)
        
        # Header
        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=15)
        
        # Title with icon
        title_label = ctk.CTkLabel(
            header_frame,
            text=f"{icon} {title}",
            font=("Segoe UI", 14, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        title_label.pack(anchor="w")
        
        # Description
        desc_label = ctk.CTkLabel(
            header_frame,
            text=description,
            font=("Segoe UI", 11),
            text_color=ModernTheme.COLORS['text_secondary']
        )
        desc_label.pack(anchor="w", pady=(2, 0))
        
        # Value control
        control_frame = ctk.CTkFrame(card, fg_color="transparent")
        control_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Decrease button
        decrease_btn = ctk.CTkButton(
            control_frame,
            text="-",
            width=30,
            height=30,
            corner_radius=15,
            border_width=0,
            font=("Segoe UI", 14, "bold"),
            fg_color=ModernTheme.COLORS['bg_tertiary'],
            hover_color=ModernTheme.COLORS['border'],
            command=lambda: self.adjust_value(config_key, -1)
        )
        decrease_btn.pack(side="left", padx=(0, 10))
        
        # Value label
        value_var = tk.StringVar(value=str(default_value))
        value_label = ctk.CTkLabel(
            control_frame,
            textvariable=value_var,
            font=("Segoe UI", 14, "bold"),
            text_color=ModernTheme.COLORS['accent_violet'],
            width=30
        )
        value_label.pack(side="left")
        
        # Increase button
        increase_btn = ctk.CTkButton(
            control_frame,
            text="+",
            width=30,
            height=30,
            corner_radius=15,
            border_width=0,
            font=("Segoe UI", 14, "bold"),
            fg_color=ModernTheme.COLORS['bg_tertiary'],
            hover_color=ModernTheme.COLORS['border'],
            command=lambda: self.adjust_value(config_key, 1)
        )
        increase_btn.pack(side="left", padx=(10, 0))
        
        # Store reference to value variable
        if not hasattr(self, 'config_values'):
            self.config_values = {}
        self.config_values[config_key] = {
            'var': value_var,
            'min': min_value,
            'max': max_value,
            'default': default_value
        }
        
        return card
        
    def adjust_value(self, config_key, delta):
        """Adjust configuration value"""
        if config_key in self.config_values:
            config = self.config_values[config_key]
            current_value = int(config['var'].get())
            new_value = max(config['min'], min(config['max'], current_value + delta))
            config['var'].set(str(new_value))
            
    def save_configuration(self):
        """Save configuration values"""
        if not playlist_manager_module:
            self.show_error("Playlist manager not available")
            return
            
        try:
            # Build configuration dictionary
            config_data = {}
            for key, config in self.config_values.items():
                config_data[key] = int(config['var'].get())
                
            # Save to config file
            save_config_values_to_file(config_data, self)
            
            # Update playlist manager module
            for key, value in config_data.items():
                if hasattr(playlist_manager_module, key):
                    setattr(playlist_manager_module, key, value)
                    
            self.show_success("Configuration saved successfully!")
            
        except Exception as e:
            self.show_error(f"Failed to save configuration: {str(e)}")
        
    def clear_content(self):
        """Clear content frame"""
        print(f"Clearing content frame ({len(self.content_frame.winfo_children())} widgets)")
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        print(f"Content cleared ({len(self.content_frame.winfo_children())} remaining)")
        self.update_idletasks()
            
    def load_initial_data(self):
        """Load initial playlist data"""
        if not playlist_manager_module:
            self.show_error("Playlist manager not available")
            return
            
        self.show_loading()
        
        def load_data():
            try:
                sp = playlist_manager_module.authenticate_spotify()
                playlists_data = playlist_manager_module.get_user_playlists(sp)
                self.playlists = playlists_data['items']
                
                # Find the daily playlist
                for playlist in self.playlists:
                    if playlist['name'] == 'Journalière':
                        self.daily_playlist = playlist
                        self.load_daily_playlist_tracks(sp, playlist['id'])
                        break
                
                print("Initial data load completed successfully")
                self.after(0, self.hide_loading)
                self.after(0, self.show_dashboard)
                self.after(0, lambda: print("UI refresh triggered"))
                
            except Exception as e:
                self.after(0, lambda: self.show_error(f"Failed to load data: {str(e)}"))
                self.after(0, self.hide_loading)
                
        thread = threading.Thread(target=load_data, daemon=True)
        thread.start()
        
    def load_daily_playlist_tracks(self, sp, playlist_id):
        """Load tracks from the daily playlist"""
        try:
            results = sp.playlist_tracks(playlist_id)
            self.daily_playlist_tracks = results['items']
        except Exception as e:
            print(f"Error loading playlist tracks: {e}")
            self.daily_playlist_tracks = []
            
    def load_playlists(self):
        """Load and display all playlists"""
        # Clear existing playlists
        for widget in self.playlists_container.winfo_children():
            widget.destroy()
            
        if not self.playlists:
            # Show empty state
            empty_label = ctk.CTkLabel(
                self.playlists_container,
                text="No playlists found",
                font=("Segoe UI", 14),
                text_color=ModernTheme.COLORS['text_secondary']
            )
            empty_label.pack(expand=True)
            return
            
        # Display playlists
        for playlist in self.playlists:
            card = PlaylistCard(
                self.playlists_container,
                playlist=playlist,
                width=300,
                height=80,
                on_click=lambda p=playlist: self.open_playlist(p)
            )
            card.pack(pady=5)
            
    def search_playlists(self, query):
        """Search playlists by name"""
        if not query:
            self.load_playlists()
            return
            
        filtered = [p for p in self.playlists if query.lower() in p['name'].lower()]
        
        # Clear existing playlists
        for widget in self.playlists_container.winfo_children():
            widget.destroy()
            
        if not filtered:
            # Show no results
            empty_label = ctk.CTkLabel(
                self.playlists_container,
                text="No playlists found",
                font=("Segoe UI", 14),
                text_color=ModernTheme.COLORS['text_secondary']
            )
            empty_label.pack(expand=True)
            return
            
        # Display filtered playlists
        for playlist in filtered:
            card = PlaylistCard(
                self.playlists_container,
                playlist=playlist,
                width=300,
                height=80,
                on_click=lambda p=playlist: self.open_playlist(p)
            )
            card.pack(pady=5)
            
    def open_playlist(self, playlist):
        """Open a playlist in Spotify"""
        if playlist and playlist['external_urls'] and 'spotify' in playlist['external_urls']:
            import webbrowser
            webbrowser.open(playlist['external_urls']['spotify'])
            
    def create_daily_playlist(self):
        """Create the daily playlist"""
        if not playlist_manager_module:
            self.show_error("Playlist manager not available")
            return
            
        self.show_loading()
        
        def create():
            try:
                sp = playlist_manager_module.authenticate_spotify()
                user_data = sp.current_user()
                user_id = user_data['id']
                
                playlist_id = playlist_manager_module.get_or_create_playlist(sp, user_id, 'Journalière')
                
                # Update the daily playlist reference
                for playlist in self.playlists:
                    if playlist['id'] == playlist_id:
                        self.daily_playlist = playlist
                        self.load_daily_playlist_tracks(sp, playlist_id)
                        break
                
                self.after(0, lambda: self.show_success("Daily playlist created successfully!"))
                self.after(0, lambda: self.show_dashboard())
                self.after(0, self.hide_loading)
                
            except Exception as e:
                self.after(0, lambda: self.show_error(f"Failed to create playlist: {str(e)}"))
                self.after(0, self.hide_loading)
                
        thread = threading.Thread(target=create, daemon=True)
        thread.start()
        
    def refresh_daily_playlist(self):
        """Refresh the daily playlist with new content"""
        if not playlist_manager_module:
            self.show_error("Playlist manager not available")
            return
            
        if self.is_loading:
            return
            
        self.show_loading()
        
        def refresh():
            try:
                sp = playlist_manager_module.authenticate_spotify()
                
                if not self.daily_playlist:
                    # Create playlist first
                    user_data = sp.current_user()
                    user_id = user_data['id']
                    playlist_id = playlist_manager_module.get_or_create_playlist(sp, user_id, 'Journalière')
                    
                    # Update reference
                    for playlist in self.playlists:
                        if playlist['id'] == playlist_id:
                            self.daily_playlist = playlist
                            break
                else:
                    playlist_id = self.daily_playlist['id']
                
                # Refresh the playlist
                playlist_manager_module.refresh_daily_playlist()
                
                # Reload playlist tracks
                self.load_daily_playlist_tracks(sp, playlist_id)
                
                self.after(0, lambda: self.update_last_refresh_time())
                self.after(0, lambda: self.show_success("Daily playlist refreshed successfully!"))
                self.after(0, lambda: self.show_dashboard())
                self.after(0, self.hide_loading)
                
            except Exception as e:
                self.after(0, lambda: self.show_error(f"Failed to refresh playlist: {str(e)}"))
                self.after(0, self.hide_loading)
                
        thread = threading.Thread(target=refresh, daemon=True)
        thread.start()
        
    def refresh_config(self):
        """Refresh configuration"""
        self.show_info("Configuration", "Configuration refreshed. Please restart the application for changes to take effect.")
        
    def show_loading(self):
        """Show loading spinner"""
        if hasattr(self, 'loading_spinner'):
            self.is_loading = True
            self.loading_spinner.place(relx=0.5, rely=0.5, anchor="center")
            self.loading_spinner.start()
        
    def hide_loading(self):
        """Hide loading spinner"""
        if hasattr(self, 'loading_spinner') and self.loading_spinner.winfo_exists():
            self.loading_spinner.stop()
            self.loading_spinner.place_forget()
        self.is_loading = False
        
    def go_back(self):
        """Navigate back to previous view"""
        if len(self.navigation_history) > 1:
            # Remove current view from history
            self.navigation_history.pop()
            # Get previous view
            previous_view = self.navigation_history[-1]
            # Show previous view and clear current content
            getattr(self, f"show_{previous_view}")()
            
    def update_back_button(self):
        """Update back button visibility based on navigation history"""
        self.back_button.configure(visible=len(self.navigation_history) > 1)
            
    def update_last_refresh_time(self):
        """Update the last refresh time display"""
        self.last_update_label.configure(text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
        
    def show_success(self, message):
        """Show success message"""
        messagebox.showinfo("Success", message)
        
    def show_info(self, title, message):
        """Show info message"""
        messagebox.showinfo(title, message)
        
    def run(self):
        """Start the application"""
        self.show_dashboard()
        self.mainloop()

def main():
    """Main entry point"""
    try:
        app = ModernSpotifyApp()
        app.run()
    except Exception as e:
        print(f"Error running application: {e}")
        traceback.print_exc()
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
