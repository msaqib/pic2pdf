"""
PDF Creation Utility for Image to PDF Converter - High Resolution Version
"""

from PIL import Image, ImageOps
import os

class PDFCreator:
    """Utility class for creating high-quality PDF files from images."""
    
    def __init__(self, debug, dpi=300, quality=95):
        """
        Initialize the PDF creator with high-quality settings.
        
        Args:
            dpi (int): DPI for the PDF output (300 is print quality, 150 is good screen quality)
            quality (int): JPEG quality for images in PDF (1-100, 95 is very high quality)
        """
        self.dpi = dpi
        self.quality = quality
        
        # A4 size in pixels at specified DPI
        # A4 is 8.27 × 11.69 inches
        self.page_width_inches = 8.27
        self.page_height_inches = 11.69
        self.page_width = int(self.page_width_inches * dpi)
        self.page_height = int(self.page_height_inches * dpi)
        
        # Margins in pixels (0.5 inch margins)
        self.margin = int(0.5 * dpi)
        self.content_width = self.page_width - (2 * self.margin)
        self.content_height = self.page_height - (2 * self.margin)
        self.debug = debug
        
    def create_pdf(self, image_paths, output_path, fit_mode='fit', preserve_aspect=True):
        """
        Create a high-quality PDF from a list of image paths.
        
        Args:
            image_paths (list): List of paths to image files
            output_path (str): Path where the PDF should be saved
            fit_mode (str): How to fit images ('fit', 'fill', 'original')
                - 'fit': Resize to fit within page while preserving aspect ratio
                - 'fill': Resize to fill entire page (may crop)
                - 'original': Keep original size (may exceed page boundaries)
            preserve_aspect (bool): Whether to preserve aspect ratio when resizing
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
                    # Apply EXIF orientation to display image correctly
                    img = ImageOps.exif_transpose(img)
                    self.debug.info(f"Processing image {i+1}/{len(image_paths)}: {os.path.basename(img_path)}")
                    self.debug.info(f"Original size: {img.size}, Mode: {img.mode}")
                    
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
                    
                    # Process image according to fit mode
                    if fit_mode == 'original':
                        img_processed = img.copy()
                    elif fit_mode == 'fill':
                        img_processed = self.resize_to_fill_page(img, preserve_aspect)
                    else:  # fit mode
                        img_processed = self.resize_to_fit_page(img, preserve_aspect)
                    
                    self.debug.info(f"Processed size: {img_processed.size}")
                    processed_images.append(img_processed)
                    
            except Exception as e:
                raise Exception(f"Error processing image {img_path}: {str(e)}")
        
        # Create PDF with high quality settings
        if processed_images:
            try:
                self.debug.info(f"Creating PDF with {self.dpi} DPI, quality {self.quality}")
                
                # Save as PDF with high quality settings
                processed_images[0].save(
                    output_path,
                    format='PDF',
                    save_all=True,
                    append_images=processed_images[1:] if len(processed_images) > 1 else [],
                    resolution=float(self.dpi),
                    quality=self.quality,
                    optimize=False  # Don't optimize to maintain quality
                )
                
                self.debug.info(f"PDF created successfully: {output_path}")
                
            except Exception as e:
                raise Exception(f"Error creating PDF: {str(e)}")
        else:
            raise Exception("No valid images to process")
    
    def resize_to_fit_page(self, image, preserve_aspect=True):
        """
        Resize image to fit within page content area while maintaining aspect ratio.
        
        Args:
            image (PIL.Image): The image to resize
            preserve_aspect (bool): Whether to preserve aspect ratio
            
        Returns:
            PIL.Image: Resized image
        """
        img_width, img_height = image.size
        
        if preserve_aspect:
            # Calculate scaling factor to fit within content area
            scale_x = self.content_width / img_width
            scale_y = self.content_height / img_height
            scale = min(scale_x, scale_y)
            
            # Calculate new dimensions
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
        else:
            # Stretch to fit exactly
            new_width = self.content_width
            new_height = self.content_height
        
        # Only resize if necessary
        if (new_width, new_height) != (img_width, img_height):
            # Use high-quality resampling
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.debug.info(f"Resized from {img_width}x{img_height} to {new_width}x{new_height}")
        
        return image
    
    def resize_to_fill_page(self, image, preserve_aspect=True):
        """
        Resize image to fill the entire page content area.
        
        Args:
            image (PIL.Image): The image to resize
            preserve_aspect (bool): Whether to preserve aspect ratio (may crop)
            
        Returns:
            PIL.Image: Resized image
        """
        img_width, img_height = image.size
        
        if preserve_aspect:
            # Calculate scaling factor to fill content area
            scale_x = self.content_width / img_width
            scale_y = self.content_height / img_height
            scale = max(scale_x, scale_y)  # Use max to fill, not fit
            
            # Calculate new dimensions
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize image
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Crop to fit content area if necessary
            if new_width > self.content_width or new_height > self.content_height:
                # Calculate crop coordinates (center crop)
                left = max(0, (new_width - self.content_width) // 2)
                top = max(0, (new_height - self.content_height) // 2)
                right = left + self.content_width
                bottom = top + self.content_height
                
                image = image.crop((left, top, right, bottom))
                self.debug.info(f"Cropped to {image.size}")
        else:
            # Stretch to fill exactly
            image = image.resize((self.content_width, self.content_height), Image.Resampling.LANCZOS)
        
        return image
    
    def set_dpi(self, dpi):
        """
        Set the DPI for PDF output and recalculate page dimensions.
        
        Args:
            dpi (int): DPI value (150 for good quality, 300 for print quality)
        """
        self.dpi = dpi
        self.page_width = int(self.page_width_inches * dpi)
        self.page_height = int(self.page_height_inches * dpi)
        self.margin = int(0.5 * dpi)
        self.content_width = self.page_width - (2 * self.margin)
        self.content_height = self.page_height - (2 * self.margin)
        self.debug.info(f"DPI set to {dpi}, page size: {self.page_width}x{self.page_height}")
    
    def set_quality(self, quality):
        """
        Set the JPEG quality for images in the PDF.
        
        Args:
            quality (int): Quality value (1-100, 95+ for high quality)
        """
        self.quality = max(1, min(100, quality))
        self.debug.info(f"Quality set to {self.quality}")
    
    def set_margins(self, margin_inches):
        """
        Set page margins in inches.
        
        Args:
            margin_inches (float): Margin size in inches
        """
        self.margin = int(margin_inches * self.dpi)
        self.content_width = self.page_width - (2 * self.margin)
        self.content_height = self.page_height - (2 * self.margin)
        self.debug.info(f"Margins set to {margin_inches} inches ({self.margin} pixels)")
        
    def get_page_dimensions(self):
        """Get the page dimensions used for PDF creation."""
        return {
            'page_width': self.page_width,
            'page_height': self.page_height,
            'content_width': self.content_width,
            'content_height': self.content_height,
            'margin': self.margin,
            'dpi': self.dpi
        }
        
    def set_page_size(self, width_inches, height_inches):
        """
        Set custom page dimensions in inches.
        
        Args:
            width_inches (float): Page width in inches
            height_inches (float): Page height in inches
        """
        self.page_width_inches = width_inches
        self.page_height_inches = height_inches
        self.page_width = int(width_inches * self.dpi)
        self.page_height = int(height_inches * self.dpi)
        self.content_width = self.page_width - (2 * self.margin)
        self.content_height = self.page_height - (2 * self.margin)
        self.debug.info(f"Page size set to {width_inches}×{height_inches} inches")


# Preset configurations for different quality levels
class PDFQualityPresets:
    """Predefined quality settings for different use cases."""
    
    @staticmethod
    def web_quality():
        """Settings optimized for web viewing (smaller file size)."""
        return PDFCreator(dpi=150, quality=85)
    
    @staticmethod
    def print_quality(debug):
        """Settings optimized for printing (high quality)."""
        return PDFCreator(debug, dpi=300, quality=95)
    
    @staticmethod
    def archive_quality():
        """Settings optimized for archival (maximum quality)."""
        return PDFCreator(dpi=600, quality=98)
    
    @staticmethod
    def balanced_quality():
        """Balanced settings (good quality, reasonable file size)."""
        return PDFCreator(dpi=200, quality=90)