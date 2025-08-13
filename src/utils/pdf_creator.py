"""
PDF Creation Utility for Image to PDF Converter
"""

from PIL import Image
import os

class PDFCreator:
    """Utility class for creating PDF files from images."""
    
    def __init__(self):
        """Initialize the PDF creator."""
        # A4 size in pixels at 72 DPI
        self.page_width = 595
        self.page_height = 842
        
    def create_pdf(self, image_paths, output_path):
        """
        Create a PDF from a list of image paths.
        
        Args:
            image_paths (list): List of paths to image files
            output_path (str): Path where the PDF should be saved
        """
        if not image_paths:
            raise ValueError("No images provided")
            
        # Process images
        processed_images = []
        
        for i, img_path in enumerate(image_paths):
            if not os.path.exists(img_path):
                raise FileNotFoundError(f"Image file not found: {img_path}")
                
            try:
                with Image.open(img_path) as img:
                    # Convert to RGB if necessary (for JPEG compatibility in PDF)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create white background
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    # Resize image to fit A4 page while maintaining aspect ratio
                    img_resized = self.resize_to_fit_page(img)
                    processed_images.append(img_resized)
                    
            except Exception as e:
                raise Exception(f"Error processing image {img_path}: {str(e)}")
        
        # Create PDF
        if processed_images:
            try:
                # Save as PDF
                processed_images[0].save(
                    output_path,
                    format='PDF',
                    save_all=True,
                    append_images=processed_images[1:] if len(processed_images) > 1 else [],
                    resolution=72.0
                )
            except Exception as e:
                raise Exception(f"Error creating PDF: {str(e)}")
        else:
            raise Exception("No valid images to process")
            
    def resize_to_fit_page(self, image):
        """
        Resize image to fit within A4 page dimensions while maintaining aspect ratio.
        
        Args:
            image (PIL.Image): The image to resize
            
        Returns:
            PIL.Image: Resized image
        """
        img_width, img_height = image.size
        
        # Calculate scaling factor to fit within page
        scale_x = self.page_width / img_width
        scale_y = self.page_height / img_height
        scale = min(scale_x, scale_y)
        
        # Only resize if image is larger than page
        if scale < 1:
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
        
    def get_page_dimensions(self):
        """Get the page dimensions used for PDF creation."""
        return self.page_width, self.page_height
        
    def set_page_size(self, width, height):
        """Set custom page dimensions."""
        self.page_width = width
        self.page_height = height