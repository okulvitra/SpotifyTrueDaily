"""
Utility functions and helpers for the Kivy UI
Following best practices for 2025
"""

from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.clock import Clock

def show_toast(message, duration=2.0):
    """Show a toast message popup"""
    # Create the toast popup
    toast = Popup(
        title='',
        content=Label(text=message),
        size_hint=(None, None),
        size=(dp(300), dp(100)),
        auto_dismiss=True
    )
    
    # Position the toast at the bottom of the screen
    from kivy.core.window import Window
    toast.pos = (Window.width/2 - toast.width/2, dp(50))
    
    # Open the toast
    toast.open()
    
    # Schedule the toast to close after the duration
    Clock.schedule_once(lambda dt: toast.dismiss(), duration)