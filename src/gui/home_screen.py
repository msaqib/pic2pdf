"""
Home Screen UI for Image to PDF Converter
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont

# Import color scheme and icon creation function
try:
    from .preview_screen import Colors, Fonts, create_icon_image
except ImportError:
    # Fallback if import fails
    class Colors:
        BG_PRIMARY = '#FAFBFC'
        BG_SECONDARY = '#F8F9FA'
        BG_CARD = '#FFFFFF'
        TEXT_PRIMARY = '#111827'
        TEXT_SECONDARY = '#6B7280'
        TEXT_TERTIARY = '#9CA3AF'
    class Fonts:
        TITLE = ('Segoe UI', 'Helvetica Neue', 'Arial', 18, 'bold')
        SUBTITLE = ('Segoe UI', 'Helvetica Neue', 'Arial', 10, 'normal')
        SMALL = ('Segoe UI', 'Helvetica Neue', 'Arial', 8, 'normal')

class HomeScreen:
    """Home screen that displays the initial interface with file selection button."""
    
    def __init__(self, parent, on_select_files):
        """Initialize the home screen."""
        self.parent = parent
        self.on_select_files = on_select_files
        self.frame = None
        self.create_widgets()
        
    def create_widgets(self):
        """Create the home screen widgets."""
        self.frame = tk.Frame(self.parent, bg=Colors.BG_PRIMARY)
        
        # Main container with card-like appearance
        main_container = tk.Frame(self.frame, bg=Colors.BG_PRIMARY)
        main_container.pack(expand=True, fill='both')
        
        # Center frame (card style)
        center_frame = tk.Frame(
            main_container,
            bg=Colors.BG_CARD,
            relief='flat',
            borderwidth=0
        )
        center_frame.place(relx=0.5, rely=0.5, anchor='center', width=500, height=350)
        
        # Inner padding frame
        inner_frame = tk.Frame(center_frame, bg=Colors.BG_CARD)
        inner_frame.pack(expand=True, fill='both', padx=40, pady=40)
        
        # Title
        title_label = tk.Label(
            inner_frame,
            text="Image to PDF Converter",
            font=Fonts.TITLE,
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_PRIMARY
        )
        title_label.pack(pady=(0, 16))
        
        # Subtitle
        subtitle_label = tk.Label(
            inner_frame,
            text="Select images to convert them into a PDF document",
            font=Fonts.SUBTITLE,
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_SECONDARY
        )
        subtitle_label.pack(pady=(0, 32))
        
        # Create folder icon (larger than text) with green color
        folder_icon = create_icon_image('📁', size=20, color='#10B981')  # Green
        
        # Select files button
        select_button = ttk.Button(
            inner_frame,
            text="Select input files...",
            image=folder_icon,
            compound='left',
            command=self.on_select_files
        )
        select_button.pack(pady=8, ipadx=24, ipady=12)
        # Keep reference to prevent garbage collection
        select_button.image = folder_icon
        
        # Instructions
        instructions = tk.Label(
            inner_frame,
            text="Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF, WebP",
            font=Fonts.SMALL,
            bg=Colors.BG_CARD,
            fg=Colors.TEXT_TERTIARY
        )
        instructions.pack(pady=(24, 0))
        
    def show(self):
        """Show the home screen."""
        self.frame.pack(expand=True, fill='both')
        
    def hide(self):
        """Hide the home screen."""
        self.frame.pack_forget()