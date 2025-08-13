"""
Application Configuration for Image to PDF Converter
"""

import os

class AppConfig:
    """Application configuration settings."""
    
    # Application metadata
    APP_NAME = "Image(s) to PDF Converter"
    VERSION = "1.0.0"
    AUTHOR = "Muhammad Saqib Ilyas"
    
    # Supported image formats
    SUPPORTED_FORMATS = {
        '.png': 'PNG files',
        '.jpg': 'JPEG files', 
        '.jpeg': 'JPEG files',
        '.gif': 'GIF files',
        '.bmp': 'Bitmap files',
        '.tiff': 'TIFF files',
        '.tif': 'TIFF files',
        '.webp': 'WebP files'
    }
    
    # File dialog filters
    FILE_TYPES = [
        ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.tif *.webp"),
        ("PNG files", "*.png"),
        ("JPEG files", "*.jpg *.jpeg"),
        ("GIF files", "*.gif"),
        ("Bitmap files", "*.bmp"),
        ("TIFF files", "*.tiff *.tif"),
        ("WebP files", "*.webp"),
        ("All files", "*.*")
    ]
    
    # PDF settings
    PDF_PAGE_WIDTH = 595  # A4 width in points
    PDF_PAGE_HEIGHT = 842  # A4 height in points
    PDF_DPI = 72
    
    # UI settings
    THUMBNAIL_SIZE = (150, 150)
    MIN_WINDOW_WIDTH = 600
    MIN_WINDOW_HEIGHT = 400
    DEFAULT_WINDOW_WIDTH = 800
    DEFAULT_WINDOW_HEIGHT = 600
    
    # Theme settings
    THEME = 'clam'  # tkinter theme

    DEBUG = False
    
    @classmethod
    def get_supported_extensions(cls):
        """Get list of supported file extensions."""
        return list(cls.SUPPORTED_FORMATS.keys())
        
    @classmethod
    def is_supported_format(cls, filename):
        """Check if a file format is supported."""
        _, ext = os.path.splitext(filename.lower())
        return ext in cls.SUPPORTED_FORMATS
        
    @classmethod
    def get_format_description(cls, filename):
        """Get description for a file format."""
        _, ext = os.path.splitext(filename.lower())
        return cls.SUPPORTED_FORMATS.get(ext, "Unknown format")