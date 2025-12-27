"""
Home Screen UI for Image to PDF Converter
"""

import tkinter as tk
from tkinter import ttk

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
        self.frame = ttk.Frame(self.parent)
        
        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(expand=True, fill='both')
        
        # Center frame
        center_frame = ttk.Frame(main_container)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Title
        title_label = ttk.Label(
            center_frame,
            text="Image to PDF Converter",
            font=('Arial', 18, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(
            center_frame,
            text="Select images to convert them into a PDF document",
            font=('Arial', 10)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Select files button
        select_button = ttk.Button(
            center_frame,
            text="Select input files...",
            command=self.on_select_files,
            style='Accent.TButton'
        )
        select_button.pack(pady=10, padx=20, ipadx=20, ipady=10)
        
        # Instructions
        instructions = ttk.Label(
            center_frame,
            text="Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF, WebP",
            font=('Arial', 8),
            foreground='gray'
        )
        instructions.pack(pady=(20, 0))
        
    def show(self):
        """Show the home screen."""
        self.frame.pack(expand=True, fill='both')
        
    def hide(self):
        """Hide the home screen."""
        self.frame.pack_forget()