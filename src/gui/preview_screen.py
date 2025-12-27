"""
Preview Screen UI for Image to PDF Converter
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageOps
import os

class PreviewScreen:
    """Preview screen that displays selected images and allows reordering."""
    
    def __init__(self, parent, on_select_files, on_create_pdf, on_view_image, on_delete_images, debug, on_reorder_images=None):
        """Initialize the preview screen."""
        self.parent = parent
        self.on_select_files = on_select_files
        self.on_create_pdf = on_create_pdf
        self.on_view_image = on_view_image
        self.on_delete_images = on_delete_images
        self.on_reorder_images = on_reorder_images
        self.frame = None
        self.images = []
        self.thumbnails = []
        self.grid_thumbnails = []  # Smaller thumbnails for grid
        self.selected_indices = set()
        self.selected_index = None  # Currently selected single file for preview
        self.debug = debug
                
        # Drag and drop state
        self.drag_start_index = None
        self.drag_start_x = None
        self.drag_start_y = None
        self.drag_threshold = 10
        self.is_dragging = False
        
        self.image_frames = []
        self.preview_label = None
        self.preview_canvas = None
        self.preview_image = None
        self.preview_original_images = []  # Store original images for zoom
        self.preview_zoom_factor = 1.0  # Current zoom level
        self.grid_frame = None
        self.grid_canvas = None
        self.grid_scrollable_frame = None
        self.grid_scrollbar = None
        self.status_bar = None
        
        # Grid configuration
        self.grid_cols = 5  # Number of columns in grid
        self.grid_icon_size = 120  # Size of grid icons
        self.grid_padding = 5
        
        # Preview pane configuration
        self.default_preview_height = 400  # Default height for preview pane in pixels
        self.paned_window = None
        
        self.create_widgets()
        
    def create_widgets(self):
        """Create the preview screen widgets."""
        self.frame = ttk.Frame(self.parent)
        
        # Top toolbar
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill='x', padx=10, pady=10)
        
        # Select files button
        select_button = ttk.Button(
            toolbar,
            text="Select input files...",
            command=self.on_select_files
        )
        select_button.pack(side='left', padx=(0, 10))
        
        # Create PDF button
        pdf_button = ttk.Button(
            toolbar,
            text="Create PDF...",
            command=self.on_create_pdf,
            style='Accent.TButton',
        )
        pdf_button.pack(side='right')
        
        # Delete button
        delete_button = ttk.Button(
            toolbar,
            text="Delete Selected",
            command=self.delete_selected,
            state='disabled',            
        )
        delete_button.pack(side='right', padx=(0, 10))
        self.delete_button = delete_button
        
        # Main content area - use PanedWindow for resizable panes
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(expand=True, fill='both', padx=10, pady=(0, 0))
        
        # Create PanedWindow for resizable splitter
        self.paned_window = ttk.PanedWindow(content_frame, orient='vertical')
        self.paned_window.pack(fill='both', expand=True)
        
        # Top pane - Preview area (resizable)
        preview_pane = ttk.LabelFrame(self.paned_window, text="Preview", padding=10)
        self.paned_window.add(preview_pane, weight=0)
        
        # Preview canvas with scrollbars for zoom/pan
        preview_container = tk.Frame(preview_pane, bg='white')
        preview_container.pack(expand=True, fill='both')
        self.preview_container = preview_container  # Store reference
        
        # Canvas for preview with zoom support
        self.preview_canvas = tk.Canvas(preview_container, bg='white', highlightthickness=0)
        preview_v_scrollbar = ttk.Scrollbar(preview_container, orient='vertical', command=self.preview_canvas.yview)
        preview_h_scrollbar = ttk.Scrollbar(preview_container, orient='horizontal', command=self.preview_canvas.xview)
        
        self.preview_canvas.configure(
            yscrollcommand=preview_v_scrollbar.set,
            xscrollcommand=preview_h_scrollbar.set
        )
        
        preview_v_scrollbar.pack(side='right', fill='y')
        preview_h_scrollbar.pack(side='bottom', fill='x')
        self.preview_canvas.pack(side='left', fill='both', expand=True)
        
        # Preview label for placeholder text (when no image selected)
        self.preview_label = tk.Label(
            self.preview_canvas,
            text="Select a file to see preview",
            font=('Arial', 12),
            fg='gray',
            bg='white'
        )
        self.preview_image = None
        self.preview_image_id = None
        
        # Bind mouse wheel for zooming (Ctrl+Wheel for zoom, regular wheel for pan if zoomed)
        def on_preview_wheel(event):
            if event.state & 0x4:  # Ctrl key pressed - zoom
                self.zoom_preview(event.delta, event)
            else:
                # Regular scrolling when zoomed in
                if self.preview_zoom_factor > 1.0:
                    if event.delta < 0:
                        self.preview_canvas.yview_scroll(3, "units")
                    else:
                        self.preview_canvas.yview_scroll(-3, "units")
        
        self.preview_canvas.bind("<MouseWheel>", on_preview_wheel)
        self.preview_container.bind("<MouseWheel>", lambda e: on_preview_wheel(e))
        
        # Pan support (drag to move when zoomed)
        self.preview_pan_start_x = None
        self.preview_pan_start_y = None
        
        def on_preview_press(event):
            if self.preview_zoom_factor > 1.0:
                self.preview_canvas.scan_mark(event.x, event.y)
                self.preview_pan_start_x = event.x
                self.preview_pan_start_y = event.y
        
        def on_preview_drag(event):
            if self.preview_zoom_factor > 1.0 and self.preview_pan_start_x is not None:
                self.preview_canvas.scan_dragto(event.x, event.y, gain=1)
        
        self.preview_canvas.bind('<Button-1>', on_preview_press)
        self.preview_canvas.bind('<B1-Motion>', on_preview_drag)
        
        # Handle canvas resize to update image display
        def on_preview_canvas_configure(event):
            if self.selected_index is not None and self.selected_index < len(self.preview_original_images):
                original_img = self.preview_original_images[self.selected_index]
                if original_img:
                    self.display_preview_image(original_img)
        
        self.preview_canvas.bind('<Configure>', on_preview_canvas_configure)
        
        # Bottom pane - Grid area (resizable, takes remaining space)
        grid_pane = ttk.LabelFrame(self.paned_window, text="Images", padding=5)
        self.paned_window.add(grid_pane, weight=1)
        self.grid_pane = grid_pane  # Store reference for event binding
        
        # Set initial pane sizes and configure minimum sizes
        def set_initial_pane_size():
            try:
                # Get the current height of the paned window
                paned_height = self.paned_window.winfo_height()
                #print(paned_height)
                if paned_height > 1:  # Make sure it's actually rendered
                    # Set preview pane to default height (but not more than 80% of total)
                    #print(int(paned_height * 0.8))
                    #print(self.default_preview_height)
                    preview_height = min(self.default_preview_height, int(paned_height * 0.8))
                    self.paned_window.sashpos(0, preview_height)
            except:
                pass
        
        # Configure paned window minimum sizes
        def configure_paned_sizes(event=None):
            try:
                # Ensure preview pane doesn't get too small (minimum 200px)
                current_pos = self.paned_window.sashpos(0)
                if current_pos < 200:
                    self.paned_window.sashpos(0, 200)
            except:
                pass
        
        # Bind configure event to maintain minimum sizes
        self.paned_window.bind('<ButtonRelease-1>', configure_paned_sizes)
        
        # Scrollable grid frame
        self.grid_canvas = tk.Canvas(grid_pane, highlightthickness=0)
        self.grid_scrollbar = ttk.Scrollbar(grid_pane, orient='vertical', command=self.grid_canvas.yview)
        self.grid_scrollable_frame = tk.Frame(self.grid_canvas, bg='white')
        
        canvas_window = self.grid_canvas.create_window((0, 0), window=self.grid_scrollable_frame, anchor="nw")
        
        # Make canvas window expand to fill canvas width and update scroll region
        def configure_canvas_window(event):
            canvas_width = event.width
            self.grid_canvas.itemconfig(canvas_window, width=canvas_width)
            # Use after_idle to update scrollbar visibility after layout
            self.parent.after_idle(self.update_scrollbar_visibility)
        
        def configure_scrollable_frame(event):
            self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox("all"))
            # Use after_idle to update scrollbar visibility after layout
            self.parent.after_idle(self.update_scrollbar_visibility)
        
        # Custom scrollbar command
        def on_scroll(*args):
            self.grid_scrollbar.set(*args)
        
        # Bind canvas configure to resize the window
        self.grid_canvas.bind('<Configure>', configure_canvas_window)
        # Bind scrollable frame configure to update scroll region
        self.grid_scrollable_frame.bind("<Configure>", configure_scrollable_frame)
        self.grid_canvas.configure(yscrollcommand=on_scroll)
        
        # Bind mouse wheel to grid canvas and parent frame for trackpad support
        def on_mousewheel(event):
            # Only allow scrolling if scrollbar is visible (content exceeds canvas height)
            try:
                bbox = self.grid_canvas.bbox("all")
                if bbox:
                    canvas_height = self.grid_canvas.winfo_height()
                    content_height = bbox[3] - bbox[1]
                    # If content fits in canvas, don't scroll
                    if content_height <= canvas_height:
                        return
            except:
                pass
            
            # Handle both mouse wheel (delta in multiples of 120) and trackpad (smaller deltas)
            # On Windows, delta is typically 120 per "notch", but trackpads can send smaller values
            delta = event.delta
            # Normalize delta (some trackpads send values that aren't multiples of 120)
            if abs(delta) < 120:
                # Trackpad or fine scrolling - scroll by pixels
                units = -delta // 1
            else:
                # Mouse wheel - scroll by units (each unit is typically 3 lines)
                units = int(-delta / 120)
            self.grid_canvas.yview_scroll(units, "units")
        
        # Bind to canvas
        self.grid_canvas.bind("<MouseWheel>", on_mousewheel)
        # Also bind to parent frame and scrollable frame for better trackpad support on Windows
        self.grid_pane.bind("<MouseWheel>", lambda e: on_mousewheel(e))
        self.grid_scrollable_frame.bind("<MouseWheel>", lambda e: on_mousewheel(e))
        
        self.grid_canvas.pack(side="left", fill="both", expand=True)
        # Don't pack scrollbar initially - it will be shown when needed
        
        # Status bar at the bottom
        status_frame = tk.Frame(self.frame, relief='sunken', borderwidth=1)
        status_frame.pack(fill='x', side='bottom', padx=10, pady=(5, 10))
        
        self.status_bar = tk.Label(
            status_frame,
            text="Ready",
            font=('Arial', 9),
            anchor='w',
            bg='#f0f0f0',
            fg='black'
        )
        self.status_bar.pack(fill='x', padx=5, pady=2)
        
        # Bind keyboard events
        self.parent.bind('<Delete>', lambda e: self.delete_selected())
        self.parent.focus_set()
        
    def update_images(self, images):
        """Update the displayed images."""
        self.images = images
        self.selected_indices = set()
        self.selected_index = None
        self.create_thumbnails()
        self.refresh_display()
        self.update_preview()
        
    def create_thumbnails(self):
        """Create thumbnail images for display."""
        self.thumbnails = []
        self.grid_thumbnails = []
        self.preview_original_images = []
        
        # Create preview size thumbnail (larger) - for initial display
        preview_size = (400, 400)
        # Create grid size thumbnails (smaller)
        grid_size = (self.grid_icon_size - 20, self.grid_icon_size - 40)  # Leave space for label
        
        for img_path in self.images:
            try:
                with Image.open(img_path) as img:
                    # Apply EXIF orientation to display image correctly
                    img = ImageOps.exif_transpose(img)
                    
                    # Store original image for zoom
                    self.preview_original_images.append(img.copy())
                    
                    # Create preview thumbnail (initial display size)
                    preview_img = img.copy()
                    preview_img.thumbnail(preview_size, Image.Resampling.LANCZOS)
                    preview_photo = ImageTk.PhotoImage(preview_img)
                    self.thumbnails.append(preview_photo)
                    
                    # Create grid thumbnail
                    grid_img = img.copy()
                    grid_img.thumbnail(grid_size, Image.Resampling.LANCZOS)
                    grid_photo = ImageTk.PhotoImage(grid_img)
                    self.grid_thumbnails.append(grid_photo)
            except Exception as e:
                self.debug.info(f"Error creating thumbnail for {img_path}: {e}")
                # Create placeholders
                placeholder_preview = Image.new('RGB', preview_size, color='lightgray')
                preview_photo = ImageTk.PhotoImage(placeholder_preview)
                self.thumbnails.append(preview_photo)
                self.preview_original_images.append(None)
                
                placeholder_grid = Image.new('RGB', grid_size, color='lightgray')
                grid_photo = ImageTk.PhotoImage(placeholder_grid)
                self.grid_thumbnails.append(grid_photo)
                
    def refresh_display(self):
        """Refresh the grid display."""
        self.debug.info(f"Refreshing display. Images: {len(self.images)}, Selected: {self.selected_indices}")
        
        # Clear existing widgets
        for widget in self.grid_scrollable_frame.winfo_children():
            widget.destroy()
        self.image_frames = []
            
        if not self.images:
            return
        
        # Create grid of image frames
        for i, (img_path, thumbnail) in enumerate(zip(self.images, self.grid_thumbnails)):
            frame = self.create_grid_item(i, img_path, thumbnail)
            self.image_frames.append(frame)
            
        # Layout in grid
        self.layout_grid()
        
        # Update canvas scroll region and scrollbar visibility
        self.grid_scrollable_frame.update_idletasks()
        self.grid_canvas.configure(scrollregion=self.grid_canvas.bbox("all"))
        # Update scrollbar visibility after layout
        self.parent.after_idle(self.update_scrollbar_visibility)
        
    def layout_grid(self):
        """Layout image frames in a grid."""
        row = 0
        col = 0
        
        for i, frame in enumerate(self.image_frames):
            frame.grid(row=row, column=col, padx=self.grid_padding, pady=self.grid_padding, sticky='nsew')
            col += 1
            if col >= self.grid_cols:
                col = 0
                row += 1
        
        # Configure grid weights
        for i in range(self.grid_cols):
            self.grid_scrollable_frame.grid_columnconfigure(i, weight=1)
        
    def create_grid_item(self, index, img_path, thumbnail):
        """Create a grid item frame for displaying an image thumbnail."""
        is_selected = index == self.selected_index
        
        # Main frame
        frame = tk.Frame(
            self.grid_scrollable_frame,
            relief='solid',
            borderwidth=2 if is_selected else 1,
            bg='lightblue' if is_selected else 'white',
            highlightbackground='blue' if is_selected else 'gray',
            highlightthickness=2 if is_selected else 1,
            width=self.grid_icon_size,
            height=self.grid_icon_size + 25
        )
        frame.pack_propagate(False)
        
        # Store frame data
        frame.image_index = index
        frame.image_path = img_path
        
        # Image label
        img_label = tk.Label(frame, image=thumbnail, bg=frame['bg'])
        img_label.pack(pady=(5, 2))
        img_label.image = thumbnail  # Keep a reference
        
        # Filename label (truncated if too long)
        filename = os.path.basename(img_path)
        max_length = 20
        if len(filename) > max_length:
            display_name = filename[:max_length-3] + "..."
        else:
            display_name = filename
            
        name_label = tk.Label(
            frame,
            text=display_name,
            font=('Arial', 8),
            bg=frame['bg'],
            wraplength=self.grid_icon_size - 10
        )
        name_label.pack(padx=2, pady=(0, 5))
        
        # Function to get status bar text
        def get_status_text():
            filename = os.path.basename(img_path)
            dirname = os.path.dirname(img_path)
            try:
                file_size = os.path.getsize(img_path)
                size_str = f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
            except:
                size_str = "Unknown size"
            return f"Filename: {filename}  |  Path: {dirname}  |  Size: {size_str}  |  Position: {index + 1}"
        
        # Bind events
        def on_enter(event):
            # Update status bar with file information
            if self.status_bar:
                self.status_bar.config(text=get_status_text())
            if not self.is_dragging and index != self.selected_index:
                frame.configure(bg='#f0f0f0')
                self.update_frame_bg(frame, '#f0f0f0')
        
        def on_leave(event):
            # Clear status bar
            if self.status_bar:
                self.status_bar.config(text="Ready")
            if not self.is_dragging and index != self.selected_index:
                frame.configure(bg='white')
                self.update_frame_bg(frame, 'white')
        
        def on_press(event):
            self.drag_start_index = index
            self.drag_start_x = event.x_root
            self.drag_start_y = event.y_root
            self.is_dragging = False
        
        def on_drag(event):
            if self.drag_start_index is None:
                return
            
            if not self.is_dragging:
                distance = ((event.x_root - self.drag_start_x)**2 + 
                           (event.y_root - self.drag_start_y)**2)**0.5
                if distance > self.drag_threshold:
                    self.start_drag(index)
        
        def on_release(event):
            if self.is_dragging and self.drag_start_index is not None:
                # Was dragging - complete drag operation
                target_index = self.find_target_index(event.x_root, event.y_root)
                if target_index is not None and target_index != self.drag_start_index:
                    self.reorder_images(self.drag_start_index, target_index)
                self.end_drag()
            elif self.drag_start_index == index:
                # Was a click (not a drag) - select the image
                self.select_image(index)
            self.drag_start_index = None
        
        def on_click(event):
            # Single click - handled in on_release
            pass
        
        def on_double_click(event):
            if not self.is_dragging:
                self.on_view_image(img_path)
        
        # Bind events to frame and all children
        for widget in [frame, img_label, name_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)
            widget.bind('<Button-1>', on_click)
            widget.bind('<Double-Button-1>', on_double_click)
            widget.bind('<ButtonPress-1>', on_press)
            widget.bind('<B1-Motion>', on_drag)
            widget.bind('<ButtonRelease-1>', on_release)
            try:
                widget.configure(cursor="hand2")
            except:
                pass
        
        return frame
    
    def update_frame_bg(self, frame, bg_color):
        """Update frame background color recursively."""
        def update_widget(widget):
            try:
                widget.configure(bg=bg_color)
            except:
                pass
            for child in widget.winfo_children():
                update_widget(child)
        update_widget(frame)
    
    def select_image(self, index):
        """Select an image and update preview."""
        if index < 0 or index >= len(self.images):
            return
            
        self.selected_index = index
        self.selected_indices = {index}
        self.update_preview()
        self.refresh_display()  # Refresh to update selection highlight
        self.update_selection_display()
    
    def update_scrollbar_visibility(self):
        """Show or hide scrollbar based on content height."""
        try:
            bbox = self.grid_canvas.bbox("all")
            if bbox:
                canvas_height = self.grid_canvas.winfo_height()
                content_height = bbox[3] - bbox[1]
                if content_height > canvas_height and canvas_height > 0:
                    # Show scrollbar
                    if not self.grid_scrollbar.winfo_viewable():
                        self.grid_scrollbar.pack(side="right", fill="y")
                else:
                    # Hide scrollbar
                    if self.grid_scrollbar.winfo_viewable():
                        self.grid_scrollbar.pack_forget()
        except:
            pass
    
    def update_preview(self):
        """Update the preview pane with selected image."""
        # Reset zoom when changing images
        self.preview_zoom_factor = 1.0
        
        if self.selected_index is not None and self.selected_index < len(self.preview_original_images):
            # Show selected image on canvas
            original_img = self.preview_original_images[self.selected_index]
            if original_img:
                self.display_preview_image(original_img)
            else:
                self.show_preview_placeholder()
        else:
            # Show placeholder text
            self.show_preview_placeholder()
    
    def show_preview_placeholder(self):
        """Show placeholder text in preview."""
        self.preview_canvas.delete("all")
        self.preview_image_id = None
        self.preview_image = None
        # Center the label
        self.preview_label.place(relx=0.5, rely=0.5, anchor='center')
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
    
    def display_preview_image(self, img):
        """Display image in preview canvas with current zoom."""
        # Hide placeholder label
        self.preview_label.place_forget()
        
        # Calculate display size based on zoom
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not sized yet, use default
            canvas_width = 400
            canvas_height = 400
        
        # Calculate size to fit canvas with zoom
        img_width, img_height = img.size
        scale_x = (canvas_width * 0.95) / img_width
        scale_y = (canvas_height * 0.95) / img_height
        initial_scale = min(scale_x, scale_y, 1.0)  # Don't scale up initially
        
        # Apply zoom factor
        display_scale = initial_scale * self.preview_zoom_factor
        
        # Limit zoom range
        display_scale = max(0.1, min(display_scale, 5.0))
        
        # Resize image
        new_width = int(img_width * display_scale)
        new_height = int(img_height * display_scale)
        
        display_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(display_img)
        
        # Update canvas
        self.preview_canvas.delete("all")
        self.preview_image_id = self.preview_canvas.create_image(
            canvas_width // 2, 
            canvas_height // 2, 
            anchor='center', 
            image=photo
        )
        self.preview_image = photo  # Keep reference
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
    
    def zoom_preview(self, delta, event=None):
        """Zoom the preview image."""
        if self.selected_index is None or self.selected_index >= len(self.preview_original_images):
            return
        
        original_img = self.preview_original_images[self.selected_index]
        if not original_img:
            return
        
        # Calculate zoom step (smaller steps for smoother zooming)
        zoom_step = 0.1 if abs(delta) < 120 else 0.2
        
        # Determine zoom direction
        if delta > 0:
            self.preview_zoom_factor *= (1 + zoom_step)
        else:
            self.preview_zoom_factor *= (1 - zoom_step)
        
        # Limit zoom range
        self.preview_zoom_factor = max(0.1, min(self.preview_zoom_factor, 5.0))
        
        # Update display
        self.display_preview_image(original_img)
    
    def update_selection_display(self):
        """Update the visual display of selections."""
        if self.selected_index is not None:
            self.delete_button['state'] = 'normal'
        else:
            self.delete_button['state'] = 'disabled'
    
    def start_drag(self, index):
        """Start the drag operation."""
        self.is_dragging = True
        self.debug.info(f"Started dragging frame {index}")
        
        # Change cursor for all frames
        for frame in self.image_frames:
            try:
                self.set_cursor_recursive(frame, "hand2")
            except:
                pass
    
    def set_cursor_recursive(self, widget, cursor):
        """Recursively set cursor for widget and children."""
        try:
            widget.configure(cursor=cursor)
        except:
            pass
        for child in widget.winfo_children():
            self.set_cursor_recursive(child, cursor)
    
    def find_target_index(self, x_root, y_root):
        """Find the target index for dropping based on coordinates."""
        if not self.image_frames:
            return None
        
        try:
            # Convert screen coordinates to canvas coordinates
            canvas_x = x_root - self.grid_canvas.winfo_rootx()
            canvas_y = y_root - self.grid_canvas.winfo_rooty()
            
            # Account for scroll position
            scroll_top = self.grid_canvas.yview()[0]
            canvas_height = self.grid_canvas.winfo_height()
            scroll_region = self.grid_canvas.cget('scrollregion')
            if scroll_region:
                scroll_region_height = int(scroll_region.split()[3]) or canvas_height
                actual_y = canvas_y + (scroll_top * scroll_region_height)
            else:
                actual_y = canvas_y
            
            # Find which grid cell this corresponds to by checking frame positions
            # This is more reliable than calculating from dimensions
            best_index = None
            min_distance = float('inf')
            
            for i, frame in enumerate(self.image_frames):
                try:
                    frame_x = frame.winfo_x()
                    frame_y = frame.winfo_y()
                    frame_width = frame.winfo_width()
                    frame_height = frame.winfo_height()
                    
                    # Check if point is within frame bounds
                    frame_center_x = frame_x + frame_width / 2
                    frame_center_y = frame_y + frame_height / 2
                    
                    # Convert to canvas coordinates
                    frame_canvas_y = frame_y + (scroll_top * (scroll_region_height if scroll_region else canvas_height))
                    
                    # Calculate distance from click point
                    dist_x = abs(canvas_x - (frame_x + frame_width / 2))
                    dist_y = abs(actual_y - (frame_canvas_y + frame_height / 2))
                    distance = (dist_x**2 + dist_y**2)**0.5
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_index = i
                except:
                    continue
            
            return best_index if best_index is not None else len(self.image_frames) - 1
            
        except Exception as e:
            self.debug.info(f"Error finding target index: {e}")
            return None
    
    def end_drag(self):
        """End the drag operation."""
        self.drag_start_index = None
        self.drag_start_x = None
        self.drag_start_y = None
        self.is_dragging = False
        
        # Reset cursors
        for frame in self.image_frames:
            try:
                self.set_cursor_recursive(frame, "hand2")
            except:
                pass
    
    def reorder_images(self, from_index, to_index):
        """Reorder images by moving from_index to to_index."""
        self.debug.info(f"Reordering: moving item {from_index} to position {to_index}")
        
        if from_index == to_index or from_index < 0 or to_index < 0:
            return
        if from_index >= len(self.images) or to_index >= len(self.images):
            return
            
        # Move in images list
        item = self.images.pop(from_index)
        self.images.insert(to_index, item)
        
        # Move in thumbnails list
        thumb = self.thumbnails.pop(from_index)
        self.thumbnails.insert(to_index, thumb)
        
        # Move in grid thumbnails list
        grid_thumb = self.grid_thumbnails.pop(from_index)
        self.grid_thumbnails.insert(to_index, grid_thumb)
        
        # Update selection
        if self.selected_index is not None:
            if self.selected_index == from_index:
                self.selected_index = to_index
            elif from_index < to_index:
                if from_index < self.selected_index <= to_index:
                    self.selected_index -= 1
            else:  # from_index > to_index
                if to_index <= self.selected_index < from_index:
                    self.selected_index += 1
        
        self.selected_indices = {self.selected_index} if self.selected_index is not None else set()
        
        self.debug.info(f"Reorder complete. New selected index: {self.selected_index}")
        if self.on_reorder_images:
            self.on_reorder_images(self.images.copy())
        self.refresh_display()
        self.update_preview()
    
    def delete_selected(self):
        """Delete selected images."""
        if self.selected_index is None:
            tk.messagebox.showinfo("No Selection", "Please select an image to delete first.")
            return
            
        indices_to_delete = [self.selected_index]
        self.on_delete_images(indices_to_delete)
    
    def select_all(self):
        """Select all images (selects first one for preview)."""
        if self.images:
            self.selected_index = 0
            self.selected_indices = {0}
            self.update_preview()
        self.update_selection_display()
        self.refresh_display()
    
    def clear_selection(self):
        """Clear all selections."""
        self.selected_indices = set()
        self.selected_index = None
        self.update_preview()
        self.update_selection_display()
        self.refresh_display()
    
    def show(self):
        """Show the preview screen."""
        self.frame.pack(expand=True, fill='both')
        self.parent.focus_set()
        
        # Set initial pane size after screen is displayed
        def set_size_after_layout():
            try:
                # Get the current height of the paned window
                paned_height = self.paned_window.winfo_height()
                if paned_height > 1:  # Make sure it's actually rendered
                    # Set preview pane to default height (but not more than 80% of total)
                    preview_height = min(self.default_preview_height, int(paned_height * 0.8))
                    self.paned_window.sashpos(0, preview_height)
            except:
                pass
        
        # Schedule to set initial size after layout is complete
        self.parent.after(100, set_size_after_layout)
        self.parent.after(300, set_size_after_layout)  # Backup in case first one is too early
        
        # Bind keyboard events
        self.parent.bind('<Delete>', self.on_delete_key)
        self.parent.bind('<Control-a>', self.on_select_all_key)
        
    def hide(self):
        """Hide the preview screen."""
        self.frame.pack_forget()
        try:
            self.parent.unbind('<Delete>')
            self.parent.unbind('<Control-a>')
        except:
            pass
            
    def on_delete_key(self, event):
        """Handle Delete key press."""
        self.delete_selected()
        
    def on_select_all_key(self, event):
        """Handle Ctrl+A key press."""
        self.select_all()
        return 'break'