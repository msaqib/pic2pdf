#!/usr/bin/env python3
"""
Image to PDF Converter - Main Application Entry Point
"""

import sys
import os
import logging
from src.utils.config import AppConfig #.src.utils.config import AppConfig

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import ImageToPDFApp

def main():
    """Main entry point for the application."""
    if AppConfig.DEBUG:
        logging.basicConfig(
    level=logging.DEBUG,  # Change to logging.INFO to hide debug messages
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
        
    else:
        logging.basicConfig(
    level=logging.ERROR,  # Change to logging.INFO to hide debug messages
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)       
    app = ImageToPDFApp(logging)
    app.run()

if __name__ == "__main__":
    main()