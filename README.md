# Image to PDF Converter

A user-friendly GUI application built with Python and Tkinter that converts multiple images into a single PDF document. The application supports drag-and-drop reordering, image preview, and full-size image viewing.

## Features

- **Multi-format Support**: PNG, JPG, JPEG, GIF, BMP, TIFF, WebP
- **Image Preview**: Thumbnail previews with file information
- **Drag & Drop Reordering**: Rearrange images by clicking and dragging
- **Full-size Viewer**: View images at full resolution with zoom and pan
- **Batch Selection**: Select multiple images at once
- **PDF Generation**: Creates A4-sized PDF with one image per page
- **Progress Indication**: Animated progress dialog during PDF creation
- **Intuitive Interface**: Clean, modern GUI with keyboard shortcuts

## Requirements

- Python 3.7 or higher
- Tkinter (usually included with Python)
- Pillow (PIL) for image processing

## Installation & Setup

### 1. Clone or Download

Download the project files to your local machine.

### 2. Create Virtual Environment

```bash
# Windows
python -m venv image-to-pdf-env
image-to-pdf-env\Scripts\activate

# macOS/Linux
python3 -m venv image-to-pdf-env
source image-to-pdf-env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

## Project Structure

```
image-to-pdf-converter/
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── src/                        # Source code directory
    ├── __init__.py
    ├── app.py                  # Main application class
    ├── gui/                    # GUI components
    │   ├── __init__.py
    │   ├── main_window.py      # Main window controller
    │   ├── home_screen.py      # Initial home screen
    │   ├── preview_screen.py   # Image preview interface
    │   └── image_viewer.py     # Full-size image viewer
    ├── models/                 # Data models
    │   ├── __init__.py
    │   └── image_manager.py    # Image list management
    └── utils/                  # Utility modules
        ├── __init__.py
        ├── config.py           # Configuration settings
        ├── pdf_creator.py      # PDF generation logic
        └── progress_dialog.py  # Progress dialog with animation
```

## Usage Guide

### 1. Starting the Application

Run `python main.py` to launch the application. You'll see the home screen with a "Select input files..." button.

### 2. Selecting Images

- Click "Select input files..." to open a file browser
- Select one or multiple image files
- Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF, WebP
- Files will be ordered by their creation time on the filesystem

### 3. Preview Screen

After selecting images, you'll see the preview screen with:
- Thumbnails of all selected images
- File names and paths
- Position indicators
- Control buttons at the top

### 4. Reordering Images

- Click and drag any image to reorder it
- The position numbers will update automatically
- The final PDF will use this order

### 5. Viewing Images

- Double-click any thumbnail to view the full-size image
- In the full-size viewer:
  - Use zoom controls (+, -, Reset, Fit to Window)
  - Drag to pan around the image
  - Use Ctrl+Mouse Wheel to zoom
  - Press Escape or click "✕ Close" to return

### 6. Removing Images

- Single-click to select images (multiple selection supported)
- Click "Delete Selected" or press the Delete key
- Confirm the removal (files are not deleted from your computer)

### 7. Creating PDF

- Click "Create PDF..." when you're satisfied with your selection
- Choose a save location and filename
- Wait for the progress dialog to complete
- The PDF will be created with A4 page size, one image per page

### 8. Keyboard Shortcuts

**In Image Viewer:**
- `Escape`: Close viewer
- `Ctrl +`: Zoom in
- `Ctrl -`: Zoom out
- `Ctrl 0`: Reset zoom to 100%

**In Preview Screen:**
- `Delete`: Remove selected images

## Technical Details

### PDF Generation

- Uses Pillow (PIL) for image processing
- Automatically converts images to RGB format for PDF compatibility
- Maintains aspect ratios when fitting images to A4 pages
- Creates multi-page PDFs with one image per page

### Image Processing

- Supports all major image formats
- Creates thumbnails for preview (150x150 pixels)
- Handles transparency by compositing onto white background
- Efficient memory usage with image streaming

### GUI Architecture

- Modular design with separate screens and controllers
- Uses tkinter's ttk widgets for modern appearance
- Responsive layout that adapts to window resizing
- Proper event handling and keyboard shortcuts

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Make sure you've activated the virtual environment and installed dependencies

2. **Images not displaying**: Ensure image files are not corrupted and are in supported formats

3. **PDF creation fails**: Check that you have write permissions to the selected output directory

4. **Large images cause slowness**: The application automatically creates thumbnails, but very large images may take time to load

### Performance Tips

- For best performance, keep images under 50MB each
- The application handles large batches (100+ images) but may be slower
- Close the full-size image viewer when not needed to free memory

## Development

### Adding New Features

The modular structure makes it easy to extend:

- **New image formats**: Update `config.py` with format definitions
- **Different PDF sizes**: Modify `pdf_creator.py` page dimensions
- **UI improvements**: Add new screens in the `gui/` directory
- **Export formats**: Create new export utilities in `utils/`

### Testing

Test the application with various image formats and sizes to ensure compatibility.

## License

This project is provided as-is for educational and personal use.

## Support

For issues or feature requests, please check the code comments and documentation within the source files.