#!/usr/bin/env python3
"""
Image to PDF Converter - Main Application Entry Point
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app import ImageToPDFApp

def main():
    """Main entry point for the application."""
    app = ImageToPDFApp()
    app.run()

if __name__ == "__main__":
    main()