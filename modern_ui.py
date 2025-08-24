"""
Modern UI Components for SpotifyTrueDaily
Clean, focused components for daily playlist refresh
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import threading
import time

class ModernTheme:
    """Modern theme configuration with blue/violet accents"""
    
    COLORS = {
        'bg_primary': '#121212',
        'bg_secondary': '#181818',
        'bg_tertiary': '#282828',
        'accent_blue': '#3B82F6',  # Dark blue
        'accent_violet': '#8B5CF6',  # Violet
        'accent_hover_violet': '#7C3AED',  # Darker violet for hover
        'accent_green': '#1DB954',  # Keep for compatibility
        'text_primary': '#FFFFFF',
        'text_secondary': '#B3B3B3',
        'text_disabled': '#535353',
        'border': '#404040',
        'success': '#3B82F6',  # Changed to blue
        'warning': '#FFB800',
        'error': '#E74C3C'
    }
    
    @classmethod
    def get_accent_color(cls):
        """Get the primary accent color (violet)"""
        return cls.COLORS['accent_violet']
        
    @classmethod
    def get_accent_hover_color(cls):
        """Get the hover accent color"""
        return cls.COLORS['accent_hover_violet']
        
    @classmethod
    def get_accent(cls):
        """Get the primary accent color (violet)"""
        return cls.COLORS['accent_violet']
    
    @staticmethod
    def get_font(font_type="body"):
        """Get font configuration"""
        fonts = {
            "header": ("Segoe UI", 24, "bold"),
            "title": ("Segoe UI", 18, "bold"),
            "body": ("Segoe UI", 13),
            "small": ("Segoe UI", 11),
            "tiny": ("Segoe UI", 9)
        }
        return fonts.get(font_type, fonts["body"])
    
    @staticmethod
    def apply_theme():
        """Apply modern theme to customtkinter"""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

class ModernButton(ctk.CTkButton):
    """Custom rounded button with hover effects"""
    
    def __init__(self, master, text="", command=None, variant="primary", **kwargs):
        self.variant = variant
        self.visible = True
        colors = ModernTheme.COLORS
        
        if variant == "primary":
            fg_color = colors['accent_violet']
            hover_color = colors['accent_hover_violet']
        elif variant == "secondary":
            fg_color = colors['bg_tertiary']
            hover_color = colors['border']
        else:
            fg_color = colors['bg_secondary']
            hover_color = colors['bg_tertiary']
            
        super().__init__(
            master=master,
            text=text,
            command=command,
            fg_color=fg_color,
            hover_color=hover_color,
            text_color=colors['text_primary'],
            corner_radius=20,
            border_width=0,
            font=("Segoe UI", 12, "bold"),
            **kwargs
        )

class Sidebar(ctk.CTkFrame):
    """Modern sidebar navigation"""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=ModernTheme.COLORS['bg_secondary'],
            width=200,
            corner_radius=0,
            **kwargs
        )
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup sidebar UI"""
        # Logo/Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", pady=(20, 30))
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="SpotifyTrueDaily",
            font=("Segoe UI", 18, "bold"),
            text_color=ModernTheme.COLORS['text_primary']
        )
        title_label.pack()
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10)
        
        self.nav_buttons = {}
        
        nav_items = [
            ("Dashboard", "dashboard"),
            ("Playlist Configuration", "playlist_config"),
            ("API Settings", "settings"),
            ("About", "about")
        ]
        
        for text, item_id in nav_items:
            btn = ModernButton(
                nav_frame,
                text=text,
                command=lambda x=item_id: self.on_nav_click(x),
                variant="secondary",
                height=40,
                width=180
            )
            btn.pack(pady=2)
            self.nav_buttons[item_id] = btn
            
    def on_nav_click(self, item_id):
        """Handle navigation clicks with visual feedback"""
        print(f"\n--- SIDEBAR CLICK DEBUG ---")
        print(f"Received click for: {item_id}")
        print(f"Current nav buttons: {list(self.nav_buttons.keys())}")
        print(f"Master class: {self.master.__class__.__name__}")
        print(f"Widget hierarchy: {self.winfo_parent()} -> {self.winfo_children()}")
        
        # Visual feedback animation
        clicked_btn = self.nav_buttons.get(item_id)
        if clicked_btn:
            original_color = clicked_btn.cget('fg_color')
            clicked_btn.configure(fg_color=ModernTheme.COLORS['accent_blue'])
            self.update_idletasks()
            self.after(100, lambda: clicked_btn.configure(fg_color=original_color))

        # Update active state
        print("Updating button states:")
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == item_id:
                print(f"  - Activating {btn_id} ({btn})")
                btn.configure(fg_color=ModernTheme.get_accent_color(),
                             hover_color=ModernTheme.COLORS['accent_hover_violet'])
            else:
                print(f"  - Deactivating {btn_id} ({btn})")
                btn.configure(fg_color=ModernTheme.COLORS['bg_tertiary'],
                             hover_color=ModernTheme.COLORS['border'])
                
        # Trigger navigation event
        event_name = f"<<Nav_{item_id}>>"
        print(f"\nGenerating event: {event_name}")
        print(f"Widget hierarchy: {self.winfo_children()}")
        
        try:
            self.master.event_generate(event_name)
            print("Event generation successful")
            print(f"Posted events: {self.tk.call('event', 'info')}")
        except Exception as e:
            print(f"Error generating event: {str(e)}")
        
        # Force UI update and layout recalculation
        self.update_idletasks()
        print("UI update completed")
        print(f"Current focus: {self.focus_get()}")

class LoadingSpinner(ctk.CTkFrame):
    """Simple loading spinner"""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color="transparent",
            width=60,
            height=60,
            **kwargs
        )
        
        self.dots = []
        self.animation_running = False
        
        # Create dots
        for i in range(3):
            dot = ctk.CTkLabel(
                self,
                text="●",
                font=("Segoe UI", 20),
                text_color=ModernTheme.get_accent_color()
            )
            dot.grid(row=0, column=i, padx=2)
            self.dots.append(dot)
            
    def start(self):
        """Start animation"""
        if not self.animation_running:
            self.animation_running = True
            self.animate()
            
    def stop(self):
        """Stop animation"""
        self.animation_running = False
        
    def animate(self):
        """Animate the dots"""
        if not self.animation_running or not self.winfo_exists():
            return
            
        # Simple fade animation
        for i, dot in enumerate(self.dots):
            opacity = 0.3 + 0.7 * ((time.time() * 3 + i) % 1)
            color = ModernTheme.get_accent_color()
            dot.configure(text_color=color)
            
        if self.animation_running:
            self.after(100, self.animate)

class PlaylistCard(ctk.CTkFrame):
    """Modern playlist card with album artwork and info"""
    
    def __init__(self, master, playlist, on_click=None, **kwargs):
        super().__init__(
            master,
            fg_color=ModernTheme.COLORS['bg_tertiary'],
            corner_radius=8,
            border_width=1,
            border_color=ModernTheme.COLORS['border'],
            **kwargs
        )
        
        self.playlist = playlist
        self.on_click = on_click
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Playlist info
        name_label = ctk.CTkLabel(
            self,
            text=playlist['name'],
            font=ModernTheme.get_font("body"),
            text_color=ModernTheme.COLORS['text_primary'],
            anchor="w"
        )
        name_label.grid(row=0, column=0, columnspan=2, padx=15, pady=(10, 5), sticky="ew")
        
        # Track count
        tracks_text = f"{playlist.get('tracks', {}).get('total', 0)} tracks"
        tracks_label = ctk.CTkLabel(
            self,
            text=tracks_text,
            font=ModernTheme.get_font("small"),
            text_color=ModernTheme.COLORS['text_secondary'],
            anchor="w"
        )
        tracks_label.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")
        
        # Hover effect
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        
        # Click handler
        if self.on_click:
            self.bind("<Button-1>", lambda e: self.on_click(self.playlist))
            for child in self.winfo_children():
                child.bind("<Button-1>", lambda e: self.on_click(self.playlist))
        
    def on_hover(self, event):
        """Handle hover effect"""
        self.configure(border_color=ModernTheme.get_accent_color())
        
    def on_leave(self, event):
        """Handle leave effect"""
        self.configure(border_color=ModernTheme.COLORS['border'])

class ModernScrollableFrame(ctk.CTkScrollableFrame):
    """Modern scrollable frame with custom styling"""
    
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=ModernTheme.COLORS['bg_primary'],
            scrollbar_fg_color=ModernTheme.COLORS['bg_secondary'],
            scrollbar_button_color=ModernTheme.COLORS['bg_tertiary'],
            scrollbar_button_hover_color=ModernTheme.COLORS['border'],
            **kwargs
        )

class SearchBar(ctk.CTkFrame):
    """Modern search bar with instant results"""
    
    def __init__(self, master, on_search=None, **kwargs):
        super().__init__(
            master,
            fg_color=ModernTheme.COLORS['bg_secondary'],
            corner_radius=20,
            **kwargs
        )
        
        self.on_search = on_search
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup search bar UI"""
        # Search icon
        search_icon = ctk.CTkLabel(
            self,
            text="🔍",
            font=("Segoe UI", 14),
            text_color=ModernTheme.COLORS['text_secondary']
        )
        search_icon.pack(side="left", padx=(15, 5))
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_entry = ctk.CTkEntry(
            self,
            textvariable=self.search_var,
            placeholder_text="Search playlists...",
            fg_color="transparent",
            border_width=0,
            font=("Segoe UI", 14),
            text_color=ModernTheme.COLORS['text_primary']
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        # Bind search events
        self.search_var.trace("w", lambda *args: self.on_search_callback())
        
    def on_search_callback(self):
        """Handle search input"""
        if self.on_search:
            query = self.search_var.get()
            self.on_search(query)
