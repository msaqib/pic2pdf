"""
Image Data Management for Image to PDF Converter
"""

class ImageManager:
    """Manages the list of selected images and their ordering."""
    
    def __init__(self):
        """Initialize the image manager."""
        self.images = []
        
    def set_images(self, image_paths):
        """Set the list of images."""
        self.images = list(image_paths)
        
    def get_images(self):
        """Get the current list of images."""
        return self.images.copy()
        
    def add_image(self, image_path):
        """Add a single image to the list."""
        if image_path not in self.images:
            self.images.append(image_path)
            
    def remove_images(self, indices):
        """Remove images at the specified indices."""
        # Sort indices in reverse order to avoid index shifting issues
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.images):
                self.images.pop(index)
                
    def move_image(self, from_index, to_index):
        """Move an image from one position to another."""
        if (0 <= from_index < len(self.images) and 
            0 <= to_index < len(self.images) and 
            from_index != to_index):
            item = self.images.pop(from_index)
            self.images.insert(to_index, item)
            
    def has_images(self):
        """Check if there are any images in the list."""
        return len(self.images) > 0
        
    def clear(self):
        """Clear all images from the list."""
        self.images.clear()
        
    def get_image_count(self):
        """Get the number of images in the list."""
        return len(self.images)