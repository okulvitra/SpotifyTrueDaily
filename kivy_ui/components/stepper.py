"""
Modern UI stepper component for the Kivy application
Following best practices for 2025
"""

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.event import EventDispatcher

from kivy_ui.themes.colors import COLORS, FONTS
from kivy_ui.components.buttons import ModernButton

class Stepper(BoxLayout):
    """A stepper component with +/- buttons and a label to display the value"""
    
    def __init__(self, min_value=0, max_value=10, default_value=0, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.height = dp(40)
        self.spacing = dp(10)
        
        self.min_value = min_value
        self.max_value = max_value
        self._value = default_value  # Internal value storage
        
        # Register the on_value event
        self.register_event_type('on_value')
        
        # Create decrease button
        self.decrease_btn = ModernButton(
            text="-",
            size_hint_x=None,
            width=dp(40)
        )
        self.decrease_btn.bind(on_press=self.decrease)
        self.add_widget(self.decrease_btn)
        
        # Create value label
        self.value_label = Label(
            text=str(self._value),
            font_size=FONTS['body_large'],
            color=COLORS['text_primary'],
            halign='center',
            size_hint_x=None,
            width=dp(40)
        )
        self.value_label.bind(size=self.value_label.setter('text_size'))
        self.add_widget(self.value_label)
        
        # Create increase button
        self.increase_btn = ModernButton(
            text="+",
            size_hint_x=None,
            width=dp(40)
        )
        self.increase_btn.bind(on_press=self.increase)
        self.add_widget(self.increase_btn)
        
        # Update button states
        self.update_button_states()
        
    @property
    def value(self):
        """Get the current value"""
        return self._value
        
    @value.setter
    def value(self, val):
        """Set the value and update the UI"""
        self._value = max(self.min_value, min(self.max_value, val))
        if self.value_label:
            self.value_label.text = str(self._value)
        self.update_button_states()
        
    def decrease(self, *args):
        """Decrease the value"""
        if self._value > self.min_value:
            self._value -= 1
            self.update_value()
            
    def increase(self, *args):
        """Increase the value"""
        if self._value < self.max_value:
            self._value += 1
            self.update_value()
            
    def update_value(self):
        """Update the value label and button states"""
        self.value_label.text = str(self._value)
        self.update_button_states()
        
        # Dispatch value change event
        self.dispatch('on_value')
        
    def update_button_states(self):
        """Update the enabled state of the buttons"""
        if self.decrease_btn and self.increase_btn:
            self.decrease_btn.disabled = self._value <= self.min_value
            self.increase_btn.disabled = self._value >= self.max_value
            
    def on_value(self):
        """Event handler for value changes"""
        pass