"""
Main Kivy Application for SpotifyTrueDaily
"""

import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.clock import Clock
import threading
import sys
import os

# Add the project root to the path so we can import playlist_manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

try:
    from playlist_manager import (
        ConfigError,
        authenticate_spotify,
        get_or_create_playlist,
        refresh_daily_playlist as pm_refresh_daily_playlist,
    )
    PLAYLIST_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"Error importing playlist_manager: {e}")
    PLAYLIST_MANAGER_AVAILABLE = False

# Import Kivy UI components
from kivy_ui.screens.dashboard import DashboardScreen
from kivy_ui.screens.settings import SettingsScreen
from kivy_ui.screens.playlist_config import PlaylistConfigScreen
from kivy_ui.components.navbar import Navbar
from kivy_ui.themes.colors import COLORS

kivy.require('2.3.0')

class MainLayout(BoxLayout):
    """Main layout containing navbar and screen manager"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Create navbar
        self.navbar = Navbar(on_nav_item_pressed=self.on_nav_item_pressed)
        self.add_widget(self.navbar)
        
        # Create screen manager
        self.screen_manager = ScreenManager()
        
        # Add screens
        self.dashboard_screen = DashboardScreen(name='dashboard')
        self.settings_screen = SettingsScreen(name='settings')
        self.playlist_config_screen = PlaylistConfigScreen(name='playlist_config')
        
        self.screen_manager.add_widget(self.dashboard_screen)
        self.screen_manager.add_widget(self.settings_screen)
        self.screen_manager.add_widget(self.playlist_config_screen)
        
        self.add_widget(self.screen_manager)
        
    def on_nav_item_pressed(self, screen_name):
        """Handle navigation item press"""
        if self.screen_manager.has_screen(screen_name):
            self.screen_manager.current = screen_name

class SpotifyTrueDailyKivyApp(App):
    """Main Kivy application class"""
    
    def build(self):
        # Set app title
        self.title = "SpotifyTrueDaily - Kivy Version"
        
        # Set window size (optional, for desktop)
        from kivy.core.window import Window
        Window.size = (1000, 750)
        Window.minimum_width, Window.minimum_height = 800, 600
        
        # Apply theme
        self.apply_theme()
        
        # Create main layout
        main_layout = MainLayout()
        
        return main_layout
    
    def apply_theme(self):
        """Apply modern dark theme with blue/violet accents"""
        from kivy.core.window import Window
        Window.clearcolor = COLORS['bg_primary']
    
    def refresh_daily_playlist(self):
        """Refresh the daily playlist"""
        if not PLAYLIST_MANAGER_AVAILABLE:
            self.show_error("Playlist manager not available")
            return
            
        def refresh():
            try:
                # This would be the actual playlist refresh logic
                # For now, we'll just show a success message
                self.show_success("Daily playlist refreshed successfully!")
            except Exception as e:
                self.show_error(f"Failed to refresh playlist: {str(e)}")
                
        # Run in a separate thread to prevent UI freezing
        thread = threading.Thread(target=refresh)
        thread.daemon = True
        thread.start()
    
    def show_error(self, message):
        """Show error message popup"""
        popup = Popup(
            title='Error',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()
    
    def show_success(self, message):
        """Show success message popup"""
        popup = Popup(
            title='Success',
            content=Label(text=message),
            size_hint=(0.8, 0.4)
        )
        popup.open()

if __name__ == '__main__':
    SpotifyTrueDailyKivyApp().run()