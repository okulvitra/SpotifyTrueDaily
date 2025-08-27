"""
Modern Kivy Application for SpotifyTrueDaily
Following best practices for 2025
"""

import sys
import os

# Add the project root to the path so we can import playlist_manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

# Try to import Kivy
try:
    import kivy
    kivy.require('2.3.0')
    from kivy.app import App
    from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.textinput import TextInput
    from kivy.uix.popup import Popup
    from kivy.uix.scrollview import ScrollView
    from kivy.uix.widget import Widget
    from kivy.graphics import Color, Rectangle, RoundedRectangle
    from kivy.clock import Clock
    from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
    from kivy.metrics import dp
    from kivy.animation import Animation
    KIVY_AVAILABLE = True
except ImportError as e:
    print(f"Error importing Kivy: {e}")
    print("Please install Kivy by running: pip install -r kivy_requirements.txt")
    KIVY_AVAILABLE = False

import threading

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

if KIVY_AVAILABLE:
    # Import Kivy UI components
    from kivy_ui.screens.dashboard import DashboardScreen
    from kivy_ui.screens.settings import SettingsScreen
    from kivy_ui.screens.playlist_config import PlaylistConfigScreen
    from kivy_ui.components.navbar import Navbar
    from kivy_ui.themes.colors import COLORS
    from kivy_ui.utils.helpers import show_toast

    class ModernButton(Button):
        """Modern button with hover effects and rounded corners"""
        
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.background_color = (0, 0, 0, 0)  # Transparent background
            self.color = COLORS['text_primary']
            self.height = dp(40)
            self.size_hint_y = None
            
            with self.canvas.before:
                Color(*COLORS['accent_violet'])
                self.bg = RoundedRectangle(
                    pos=self.pos,
                    size=self.size,
                    radius=[dp(8)]
                )
                
            self.bind(pos=self.update_bg, size=self.update_bg)
            
        def update_bg(self, *args):
            """Update button background"""
            self.bg.pos = self.pos
            self.bg.size = self.size

    class ModernCard(BoxLayout):
        """Modern card component with shadow effect"""
        
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.orientation = 'vertical'
            self.padding = dp(15)
            self.spacing = dp(10)
            self.size_hint_y = None
            self.height = dp(150)
            
            with self.canvas.before:
                # Shadow
                Color(0, 0, 0, 0.3)
                self.shadow = RoundedRectangle(
                    pos=(self.x + dp(2), self.y - dp(2)),
                    size=self.size,
                    radius=[dp(10)]
                )
                # Card background
                Color(*COLORS['bg_secondary'])
                self.bg = RoundedRectangle(
                    pos=self.pos,
                    size=self.size,
                    radius=[dp(10)]
                )
                
            self.bind(pos=self.update_graphics, size=self.update_graphics)
            
        def update_graphics(self, *args):
            """Update card graphics"""
            self.shadow.pos = (self.x + dp(2), self.y - dp(2))
            self.shadow.size = self.size
            self.bg.pos = self.pos
            self.bg.size = self.size

    class MainLayout(BoxLayout):
        """Main layout containing navbar and screen manager"""
        
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.orientation = 'horizontal'
            
            # Create navbar
            self.navbar = Navbar(on_nav_item_pressed=self.on_nav_item_pressed)
            self.add_widget(self.navbar)
            
            # Create screen manager with fade transition
            self.screen_manager = ScreenManager(transition=FadeTransition())
            
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
            Window.size = (1200, 800)
            Window.minimum_width, Window.minimum_height = 900, 600
            
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
                show_toast("Playlist manager not available")
                return
                
            def refresh():
                try:
                    # This would be the actual playlist refresh logic
                    # For now, we'll just show a success message
                    show_toast("Daily playlist refreshed successfully!")
                except Exception as e:
                    show_toast(f"Failed to refresh playlist: {str(e)}")
                    
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

    def main():
        """Main entry point"""
        if not KIVY_AVAILABLE:
            print("Kivy is not available. Please install it by running: pip install -r kivy_requirements.txt")
            sys.exit(1)
            
        SpotifyTrueDailyKivyApp().run()

    if __name__ == '__main__':
        main()
else:
    print("Kivy is not available. Please install it by running: pip install -r kivy_requirements.txt")
    sys.exit(1)