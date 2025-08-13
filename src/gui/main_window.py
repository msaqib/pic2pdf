"""
Main Window Controller for Image to PDF Converter
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from ..models.image_manager import ImageManager
from .home_screen import HomeScreen
from .preview_screen import PreviewScreen
from .image_viewer import ImageViewer
from ..utils.pdf_creator import PDFQualityPresets
from ..utils.progress_dialog import ProgressDialog

class MainWindow:
    """Main window controller that manages different screens and application flow."""
    
    def __init__(self, root):
        """Initialize the main window."""
        self.root = root
        self.image_manager = ImageManager()
        self.current_screen = None
        
        # Initialize screens
        self.home_screen = HomeScreen(self.root, self.on_select_files)
        self.preview_screen = PreviewScreen(
            self.root, 
            self.on_select_files,
            self.on_create_pdf,
            self.on_view_image,
            self.on_delete_images,
            self.on_reorder_images
        )
        self.image_viewer = None
        
        # Show initial screen
        self.show_home_screen()
        
    def show_home_screen(self):
        """Show the home screen."""
        if self.current_screen:
            self.current_screen.hide()
        self.current_screen = self.home_screen
        self.home_screen.show()
        
    def show_preview_screen(self):
        """Show the preview screen with current images."""
        if self.current_screen:
            self.current_screen.hide()
        self.current_screen = self.preview_screen
        self.preview_screen.update_images(self.image_manager.get_images())
        self.preview_screen.show()
        
    def on_select_files(self):
        """Handle file selection."""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.tiff *.webp"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg *.jpeg"),
            ("GIF files", "*.gif"),
            ("All files", "*.*")
        ]
        
        filenames = filedialog.askopenfilenames(
            title="Select Image Files",
            filetypes=filetypes
        )
        
        if filenames:
            # Sort files by creation time to ensure consistent ordering
            sorted_files = sorted(filenames, key=lambda x: os.path.getctime(x))
            self.image_manager.set_images(sorted_files)
            self.show_preview_screen()
            
    def on_view_image(self, image_path):
        """Handle image viewing."""
        if self.image_viewer:
            self.image_viewer.destroy()
        self.image_viewer = ImageViewer(self.root, image_path)
        
    def on_delete_images(self, indices):
        """Handle image deletion from preview."""
        if not indices:
            return
            
        count = len(indices)
        file_word = "file" if count == 1 else "files"
        
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to remove {count} {file_word} from the preview?\n"
            "This will not delete the actual files from your computer."
        )
        
        if result:
            self.image_manager.remove_images(indices)
            if self.image_manager.has_images():
                self.show_preview_screen()
            else:
                self.show_home_screen()
    def on_reorder_images(self, reordered_images):
        """
        Handle image reordering from the preview screen.
        
        Args:
            reordered_images (list): List of image paths in the new order
        """
        print(f"Main window received reorder notification: {len(reordered_images)} images")
        print(f"New order: {[os.path.basename(img) for img in reordered_images]}")
        
        # Update the ImageManager with the new order
        self.image_manager.set_images(reordered_images)
        
        # Verify the order was updated correctly
        current_images = self.image_manager.get_images()
        print(f"ImageManager updated. Current order: {[os.path.basename(img) for img in current_images]}")


    def on_create_pdf(self):
        """Handle PDF creation."""
        if not self.image_manager.has_images():
            messagebox.showwarning("No Images", "Please select some images first.")
            return
            
        # Get the current image order from ImageManager
        images = self.image_manager.get_images()
        print(f"Creating PDF with {len(images)} images in this order:")
        for i, img in enumerate(images, 1):
            print(f"  {i}. {os.path.basename(img)}")

        # Get save location
        filename = filedialog.asksaveasfilename(
            title="Save PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not filename:
            return
            
        # Create progress dialog
        progress_dialog = ProgressDialog(self.root, "Creating PDF...")
        
        def create_pdf_task():
            """Task to create PDF in background."""
            try:
                #images = self.image_manager.get_images()
                pdf_creator = PDFQualityPresets.print_quality()
                pdf_creator.create_pdf(images, filename)
                return True, "PDF created successfully!"
            except Exception as e:
                return False, f"Error creating PDF: {str(e)}"
                
        def on_complete(success, message):
            """Handle completion of PDF creation."""
            progress_dialog.close()
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
                
        progress_dialog.run_task(create_pdf_task, on_complete)