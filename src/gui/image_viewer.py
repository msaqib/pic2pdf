"""
Full Size Image Viewer for Image to PDF Converter
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps

# Import color scheme
try:
    from .preview_screen import Colors, Fonts
except ImportError:
    # Fallback if import fails
    class Colors:
        BG_PRIMARY = '#FAFBFC'
        BG_SECONDARY = '#F8F9FA'
        BG_PREVIEW = '#F9FAFB'
        TEXT_PRIMARY = '#111827'
        TEXT_SECONDARY = '#6B7280'
    class Fonts:
        BODY = ('Segoe UI', 'Helvetica Neue', 'Arial', 10, 'normal')
        SMALL = ('Segoe UI', 'Helvetica Neue', 'Arial', 9, 'normal')

class ImageViewer:
    """Full size image viewer with zoom and pan capabilities."""
    
    def __init__(self, parent, image_path):
        """Initialize the image viewer."""
        self.parent = parent
        self.image_path = image_path
        self.zoom_factor = 1.0
        self.pan_start_x = 0
        self.pan_start_y = 0
        
        # Create window
        self.window = tk.Toplevel(parent)
        self.window.title(f"Image Viewer - {image_path}")
        self.window.geometry("800x600")
        self.window.transient(parent)
        self.window.grab_set()
        
        # Load image and apply EXIF orientation
        img = Image.open(image_path)
        self.original_image = ImageOps.exif_transpose(img)
        self.current_image = self.original_image.copy()
        
        self.create_widgets()
        self.update_image()
        
        # Center the window
        self.center_window()
        
    def create_widgets(self):
        """Create the viewer widgets."""
        # Toolbar with modern styling
        toolbar = tk.Frame(self.window, bg=Colors.BG_SECONDARY, relief='flat', height=50)
        toolbar.pack(fill='x', padx=0, pady=0)
        toolbar.pack_propagate(False)
        
        toolbar_inner = ttk.Frame(toolbar)
        toolbar_inner.pack(fill='both', expand=True, padx=12, pady=10)
        
        # Close button
        close_button = ttk.Button(
            toolbar_inner,
            text="✕ Close",
            command=self.close
        )
        close_button.pack(side='left', padx=(0, 12))
        
        # Zoom controls
        zoom_label = tk.Label(
            toolbar_inner,
            text="Zoom:",
            font=Fonts.SMALL,
            bg=Colors.BG_SECONDARY,
            fg=Colors.TEXT_SECONDARY
        )
        zoom_label.pack(side='left', padx=(12, 5))
        
        zoom_out_btn = ttk.Button(
            toolbar_inner,
            text="−",
            command=self.zoom_out,
            width=3
        )
        zoom_out_btn.pack(side='left')
        
        self.zoom_label = tk.Label(
            toolbar_inner,
            text="100%",
            font=Fonts.SMALL,
            bg=Colors.BG_SECONDARY,
            fg=Colors.TEXT_PRIMARY,
            width=5
        )
        self.zoom_label.pack(side='left', padx=5)
        
        zoom_in_btn = ttk.Button(
            toolbar_inner,
            text="+",
            command=self.zoom_in,
            width=3
        )
        zoom_in_btn.pack(side='left')
        
        reset_zoom_btn = ttk.Button(
            toolbar_inner,
            text="Reset",
            command=self.reset_zoom
        )
        reset_zoom_btn.pack(side='left', padx=(5, 0))
        
        # Fit to window button
        fit_button = ttk.Button(
            toolbar_inner,
            text="Fit to Window",
            command=self.fit_to_window
        )
        fit_button.pack(side='left', padx=(12, 0))
        
        # Main canvas with scrollbars
        main_frame = ttk.Frame(self.window)
        main_frame.pack(expand=True, fill='both', padx=8, pady=(0, 8))
        
        # Canvas
        self.canvas = tk.Canvas(main_frame, bg=Colors.BG_PREVIEW, highlightthickness=0)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_frame, orient='vertical', command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient='horizontal', command=self.canvas.xview)
        
        self.canvas.configure(
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Bind events
        self.bind_events()
        
    def bind_events(self):
        """Bind keyboard and mouse events."""
        # Keyboard shortcuts
        self.window.bind('<Escape>', lambda e: self.close())
        self.window.bind('<Control-plus>', lambda e: self.zoom_in())
        self.window.bind('<Control-minus>', lambda e: self.zoom_out())
        self.window.bind('<Control-0>', lambda e: self.reset_zoom())
        
        # Mouse wheel for zooming
        def on_mouse_wheel(event):
            if event.state & 0x4:  # Ctrl key pressed
                if event.delta > 0:
                    self.zoom_in()
                else:
                    self.zoom_out()
            else:
                # Regular scrolling
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        self.canvas.bind('<MouseWheel>', on_mouse_wheel)
        
        # Pan with middle mouse button
        def start_pan(event):
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            
        def pan_image(event):
            dx = event.x - self.pan_start_x
            dy = event.y - self.pan_start_y
            self.canvas.scan_dragto(dx, dy, gain=1)
            
        self.canvas.bind('<Button-2>', start_pan)  # Middle click
        self.canvas.bind('<B2-Motion>', pan_image)
        
        # Pan with left click drag
        def start_drag(event):
            self.canvas.scan_mark(event.x, event.y)
            
        def drag_image(event):
            self.canvas.scan_dragto(event.x, event.y, gain=1)
            
        self.canvas.bind('<Button-1>', start_drag)
        self.canvas.bind('<B1-Motion>', drag_image)
        
        # Focus for keyboard events
        self.window.focus_set()
        
    def update_image(self):
        """Update the displayed image."""
        # Calculate new size
        width = int(self.original_image.width * self.zoom_factor)
        height = int(self.original_image.height * self.zoom_factor)
        
        # Resize image
        if self.zoom_factor == 1.0:
            self.current_image = self.original_image.copy()
        else:
            self.current_image = self.original_image.resize(
                (width, height),
                Image.Resampling.LANCZOS
            )
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(self.current_image)
        
        # Update canvas
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Update zoom label
        if hasattr(self, 'zoom_label'):
            self.zoom_label.config(text=f"{int(self.zoom_factor * 100)}%")
        
    def zoom_in(self):
        """Zoom in on the image."""
        self.zoom_factor = min(self.zoom_factor * 1.2, 5.0)
        self.update_image()
        
    def zoom_out(self):
        """Zoom out of the image."""
        self.zoom_factor = max(self.zoom_factor / 1.2, 0.1)
        self.update_image()
        
    def reset_zoom(self):
        """Reset zoom to 100%."""
        self.zoom_factor = 1.0
        self.update_image()
        
    def fit_to_window(self):
        """Fit image to window size."""
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not properly initialized yet
            self.window.after(100, self.fit_to_window)
            return
            
        img_width = self.original_image.width
        img_height = self.original_image.height
        
        # Calculate zoom factor to fit
        zoom_x = canvas_width / img_width
        zoom_y = canvas_height / img_height
        self.zoom_factor = min(zoom_x, zoom_y, 1.0)  # Don't zoom in beyond 100%
        
        self.update_image()
        
    def center_window(self):
        """Center the window on the parent."""
        self.window.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() // 2) - (self.window.winfo_width() // 2)
        y = self.parent.winfo_y() + (self.parent.winfo_height() // 2) - (self.window.winfo_height() // 2)
        self.window.geometry(f"+{x}+{y}")
        
    def close(self):
        """Close the image viewer."""
        self.window.destroy()
        
    def destroy(self):
        """Destroy the image viewer."""
        if self.window.winfo_exists():
            self.window.destroy()