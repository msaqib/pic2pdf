"""
Main Application Class for Image to PDF Converter
"""

import tkinter as tk
from tkinter import ttk
import os
from .gui.main_window import MainWindow
from .utils.config import AppConfig

class ImageToPDFApp:
    """Main application class that manages the GUI and application state."""
    
    def __init__(self):
        """Initialize the application."""
        self.root = tk.Tk()
        self.setup_app()
        
    def setup_app(self):
        """Setup basic application configuration."""
        self.root.title("Image to PDF Converter")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')  # Use a modern theme
        
        # Initialize main window
        self.main_window = MainWindow(self.root)
        
    def run(self):
        """Run the application main loop."""
        self.root.mainloop()