"""
Preview Screen UI for Image to PDF Converter
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

class PreviewScreen:
    """Preview screen that displays selected images and allows reordering."""
    
    def __init__(self, parent, on_select_files, on_create_pdf, on_view_image, on_delete_images):
        """Initialize the preview screen."""
        self.parent = parent
        self.on_select_files = on_select_files
        self.on_create_pdf = on_create_pdf
        self.on_view_image = on_view_image
        self.on_delete_images = on_delete_images
        self.frame = None
        self.images = []
        self.thumbnails = []
        self.selected_indices = set()
        
        # Drag and drop state
        self.drag_start_index = None
        self.drag_start_y = None
        self.drag_threshold = 10
        self.is_dragging = False
        self.drag_data = None
        
        self.image_frames = []
        self.canvas = None
        self.scrollable_frame = None
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
            style='Accent.TButton'
        )
        pdf_button.pack(side='right')
        
        # Delete button
        delete_button = ttk.Button(
            toolbar,
            text="Delete Selected",
            command=self.delete_selected,
            state='normal'
        )
        delete_button.pack(side='right', padx=(0, 10))
        
        # Main content area
        content_frame = ttk.Frame(self.frame)
        content_frame.pack(expand=True, fill='both', padx=10, pady=(0, 10))
        
        # Instructions
        instructions = ttk.Label(
            content_frame,
            text="Click to select images (Ctrl+click for multiple). Double-click to view full size. Drag to reorder.",
            font=('Arial', 9),
            foreground='gray'
        )
        instructions.pack(pady=(0, 10))
        
        # Scrollable frame for image previews
        self.canvas = tk.Canvas(content_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind mouse wheel to canvas
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.canvas.bind("<MouseWheel>", on_mousewheel)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind keyboard events
        self.parent.bind('<Delete>', lambda e: self.delete_selected())
        self.parent.focus_set()
        
    def update_images(self, images):
        """Update the displayed images."""
        self.images = images
        self.selected_indices = set()
        self.create_thumbnails()
        self.refresh_display()
        
    def create_thumbnails(self):
        """Create thumbnail images for display."""
        self.thumbnails = []
        for img_path in self.images:
            try:
                with Image.open(img_path) as img:
                    # Create thumbnail
                    img.thumbnail((150, 150), Image.Resampling.LANCZOS)
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(img)
                    self.thumbnails.append(photo)
            except Exception as e:
                print(f"Error creating thumbnail for {img_path}: {e}")
                # Create a placeholder
                placeholder_img = Image.new('RGB', (150, 150), color='lightgray')
                photo = ImageTk.PhotoImage(placeholder_img)
                self.thumbnails.append(photo)
                
    def refresh_display(self):
        """Refresh the image display."""
        print(f"Refreshing display. Images: {len(self.images)}, Selected: {self.selected_indices}")
        
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.image_frames = []
            
        # Create image frames
        for i, (img_path, thumbnail) in enumerate(zip(self.images, self.thumbnails)):
            print(f"Creating frame {i} for {os.path.basename(img_path)}")
            frame = self.create_image_frame(i, img_path, thumbnail)
            frame.pack(fill='x', padx=5, pady=2)
            self.image_frames.append(frame)
            
        print(f"Created {len(self.image_frames)} frames")
        
        # Update canvas scroll region
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            
    def create_image_frame(self, index, img_path, thumbnail):
        """Create a frame for displaying an image thumbnail."""
        is_selected = index in self.selected_indices
        
        # Main frame
        if is_selected:
            frame = tk.Frame(self.scrollable_frame, relief='solid', borderwidth=2, 
                           bg='lightblue', highlightbackground='blue', highlightthickness=1)
        else:
            frame = tk.Frame(self.scrollable_frame, relief='solid', borderwidth=1, 
                           bg='white', highlightbackground='gray', highlightthickness=1)
        
        # Store frame data
        frame.image_index = index
        frame.image_path = img_path
        
        # Image and info container
        container = tk.Frame(frame, bg=frame['bg'])
        container.pack(fill='x', padx=5, pady=5)
        
        # Thumbnail label
        img_label = tk.Label(container, image=thumbnail, bg=frame['bg'])
        img_label.pack(side='left', padx=(0, 10))
        
        # Info frame
        info_frame = tk.Frame(container, bg=frame['bg'])
        info_frame.pack(side='left', fill='both', expand=True)
        
        # File name
        filename = os.path.basename(img_path)
        name_label = tk.Label(info_frame, text=filename, font=('Arial', 10, 'bold'), 
                             bg=frame['bg'], anchor='w', justify='left')
        name_label.pack(fill='x', anchor='w')
        
        # File path
        path_label = tk.Label(info_frame, text=img_path, font=('Arial', 8), 
                             fg='gray', bg=frame['bg'], anchor='w', justify='left')
        path_label.pack(fill='x', anchor='w')
        
        # Position indicator
        pos_label = tk.Label(info_frame, text=f"Position: {index + 1}", font=('Arial', 8), 
                           bg=frame['bg'], anchor='w', justify='left')
        pos_label.pack(fill='x', anchor='w', pady=(5, 0))
        
        # Bind events - use a more reliable approach
        self.bind_frame_events(frame, index, img_path)
        
        return frame
    
    def bind_frame_events(self, frame, index, img_path):
        """Bind events to frame and all its children."""
        widgets_to_bind = []
        
        def collect_widgets(widget):
            widgets_to_bind.append(widget)
            for child in widget.winfo_children():
                collect_widgets(child)
        
        collect_widgets(frame)
        
        # Bind events to all widgets
        for widget in widgets_to_bind:
            # Set cursor
            try:
                widget.configure(cursor="hand2")
            except:
                pass
            
            # Mouse events for selection and drag/drop
            widget.bind('<Button-1>', lambda e, idx=index: self.on_mouse_press(e, idx))
            widget.bind('<Double-Button-1>', lambda e, path=img_path: self.on_double_click(e, path))
            widget.bind('<B1-Motion>', lambda e, idx=index: self.on_mouse_drag(e, idx))
            widget.bind('<ButtonRelease-1>', lambda e, idx=index: self.on_mouse_release(e, idx))
            
            # Visual feedback
            widget.bind('<Enter>', lambda e, idx=index: self.on_mouse_enter(e, idx))
            widget.bind('<Leave>', lambda e, idx=index: self.on_mouse_leave(e, idx))
    
    def on_mouse_press(self, event, index):
        """Handle mouse press."""
        print(f"Mouse press on frame {index}")
        
        # Store drag start information
        self.drag_start_index = index
        self.drag_start_y = event.y_root
        self.is_dragging = False
        
        # Start a timer to differentiate between click and drag
        self.parent.after(100, lambda: self.check_for_click(index, event.state))
    
    def check_for_click(self, index, state):
        """Check if this was a click (not a drag)."""
        if not self.is_dragging and self.drag_start_index == index:
            # This was a click, handle selection
            if state & 0x4:  # Ctrl key pressed
                self.toggle_selection(index)
            else:
                self.selected_indices = {index}
            self.update_selection_display()
    
    def on_double_click(self, event, img_path):
        """Handle double-click to view image."""
        if not self.is_dragging:
            self.on_view_image(img_path)
    
    def on_mouse_drag(self, event, index):
        """Handle mouse drag motion."""
        if self.drag_start_index is None:
            return
        
        # Check if we should start dragging
        if not self.is_dragging:
            distance = abs(event.y_root - self.drag_start_y)
            if distance > self.drag_threshold:
                self.start_drag(index)
        
        if self.is_dragging:
            self.update_drag_visual(event)
    
    def start_drag(self, index):
        """Start the drag operation."""
        self.is_dragging = True
        print(f"Started dragging frame {index}")
        
        # Change cursor for all frames
        for frame in self.image_frames:
            try:
                self.set_cursor_recursive(frame, "sb_v_double_arrow")
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
    
    def update_drag_visual(self, event):
        """Update visual feedback during drag."""
        # Find which frame we're over
        target_index = self.find_target_index(event.y_root)
        if target_index is not None and target_index != self.drag_start_index:
            # Could add visual feedback here (highlight target area)
            pass
    
    def on_mouse_release(self, event, index):
        """Handle mouse release."""
        if self.is_dragging and self.drag_start_index is not None:
            # Complete the drag operation
            target_index = self.find_target_index(event.y_root)
            
            if target_index is not None and target_index != self.drag_start_index:
                print(f"Dropping frame {self.drag_start_index} at position {target_index}")
                self.reorder_images(self.drag_start_index, target_index)
            else:
                print("Drag cancelled or dropped at same position")
        
        # Reset drag state
        self.end_drag()
    
    def end_drag(self):
        """End the drag operation."""
        self.drag_start_index = None
        self.drag_start_y = None
        self.is_dragging = False
        
        # Reset cursors
        for frame in self.image_frames:
            try:
                self.set_cursor_recursive(frame, "hand2")
            except:
                pass
    
    def find_target_index(self, y_root):
        """Find the target index for dropping based on Y coordinate."""
        if not self.image_frames:
            return None
        
        # Convert screen coordinate to canvas coordinate
        try:
            canvas_y = y_root - self.canvas.winfo_rooty()
            
            # Account for scroll position
            scroll_top, scroll_bottom = self.canvas.yview()
            canvas_height = self.canvas.winfo_height()
            scroll_region_height = int(self.canvas.cget('scrollregion').split()[3]) or canvas_height
            
            # Calculate actual Y position in the scrollable content
            actual_y = canvas_y + (scroll_top * scroll_region_height)
            
            # Find which frame this Y position corresponds to
            current_y = 0
            for i, frame in enumerate(self.image_frames):
                try:
                    frame_height = frame.winfo_reqheight() + 4  # +4 for pady
                    if actual_y <= current_y + frame_height / 2:
                        return i
                    current_y += frame_height
                except:
                    continue
            
            # If we're past all frames, return the last index + 1
            return len(self.image_frames) - 1
            
        except Exception as e:
            print(f"Error finding target index: {e}")
            return None
    
    def on_mouse_enter(self, event, index):
        """Handle mouse enter for visual feedback."""
        if not self.is_dragging and index not in self.selected_indices:
            frame = self.image_frames[index]
            self.update_frame_bg(frame, '#f0f0f0')
    
    def on_mouse_leave(self, event, index):
        """Handle mouse leave for visual feedback."""
        if not self.is_dragging and index not in self.selected_indices:
            frame = self.image_frames[index]
            self.update_frame_bg(frame, 'white')
    
    def update_frame_bg(self, frame, bg_color):
        """Update frame background color."""
        def update_widget(widget):
            try:
                widget.configure(bg=bg_color)
            except:
                pass
            for child in widget.winfo_children():
                update_widget(child)
        
        update_widget(frame)
            
    def update_selection_display(self):
        """Update the visual display of selections."""
        for i, frame in enumerate(self.image_frames):
            if i in self.selected_indices:
                frame.configure(bg='lightblue', highlightbackground='blue', highlightthickness=2)
                self.update_frame_bg(frame, 'lightblue')
            else:
                frame.configure(bg='white', highlightbackground='gray', highlightthickness=1)
                self.update_frame_bg(frame, 'white')
    
    def toggle_selection(self, index):
        """Toggle selection of an image."""
        print(f"Toggling selection for index {index}")
        if index in self.selected_indices:
            self.selected_indices.remove(index)
        else:
            self.selected_indices.add(index)
        print(f"New selection: {self.selected_indices}")
    
    def reorder_images(self, from_index, to_index):
        """Reorder images by moving from_index to to_index."""
        print(f"Reordering: moving item {from_index} to position {to_index}")
        
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
        
        # Update selection indices
        new_selected = set()
        for idx in self.selected_indices:
            if idx == from_index:
                new_selected.add(to_index)
            elif from_index < to_index:
                if from_index < idx <= to_index:
                    new_selected.add(idx - 1)
                else:
                    new_selected.add(idx)
            else:  # from_index > to_index
                if to_index <= idx < from_index:
                    new_selected.add(idx + 1)
                else:
                    new_selected.add(idx)
        self.selected_indices = new_selected
        
        print(f"Reorder complete. New selection: {self.selected_indices}")
        self.refresh_display()
        
    def delete_selected(self):
        """Delete selected images."""
        if not self.selected_indices:
            tk.messagebox.showinfo("No Selection", "Please select some images to delete first.\n\nClick on images to select them (they will turn blue).")
            return
            
        indices_to_delete = sorted(list(self.selected_indices), reverse=True)
        self.on_delete_images(indices_to_delete)
            
    def select_all(self):
        """Select all images."""
        self.selected_indices = set(range(len(self.images)))
        self.update_selection_display()
        
    def clear_selection(self):
        """Clear all selections."""
        self.selected_indices = set()
        self.update_selection_display()
        
    def show(self):
        """Show the preview screen."""
        self.frame.pack(expand=True, fill='both')
        self.parent.focus_set()
        
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