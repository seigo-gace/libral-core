"""
Image Processor

Provides comprehensive image processing capabilities for the TxT WORLD Creator's module
and other image-related functionality across Libral Core.
"""

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from typing import Tuple, Optional, Union
import logging
import os


logger = logging.getLogger(__name__)


class ImageProcessor:
    """
    Unified image processing class for all Libral Core modules.
    
    Design Intent:
    - Centralize image processing logic for TxT WORLD Creator's module
    - Provide consistent image operations across all apps
    - Optimize performance through standardized processing workflows
    - Support various output formats for different use cases (Telegram stickers, web display, etc.)
    """
    
    # Standard sizes for different platforms
    TELEGRAM_STICKER_SIZE = (512, 512)
    THUMBNAIL_SIZE = (150, 150)
    PREVIEW_SIZE = (300, 300)
    
    # Supported formats
    SUPPORTED_FORMATS = ['PNG', 'JPEG', 'WEBP', 'GIF']
    
    def __init__(self):
        """Initialize the image processor."""
        self.default_font_size = 48
        self.default_background_color = (255, 255, 255, 0)  # Transparent
        
    def create_sticker(self, text: str, font_path: Optional[str] = None, 
                      bg_path: Optional[str] = None, size: Tuple[int, int] = None) -> bytes:
        """
        Create a sticker image by combining text, font, and background.
        
        This is the core function for TxT WORLD Creator's module, enabling users
        to generate custom stickers with text, fonts, and background images.
        
        Args:
            text: Text to render on the sticker
            font_path: Path to custom font file (TTF/OTF)
            bg_path: Path to background image file
            size: Output size (width, height), defaults to Telegram sticker size
            
        Returns:
            Image data as bytes in PNG format
            
        Example:
            >>> processor = ImageProcessor()
            >>> sticker_data = processor.create_sticker(
            ...     text="Hello World!",
            ...     font_path="/fonts/comic-sans.ttf",
            ...     bg_path="/backgrounds/space.jpg"
            ... )
            >>> with open("sticker.png", "wb") as f:
            ...     f.write(sticker_data)
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Use default size if not specified
        if size is None:
            size = self.TELEGRAM_STICKER_SIZE
        
        # Create base image
        if bg_path and os.path.exists(bg_path):
            # Load and resize background image
            background = Image.open(bg_path)
            background = background.resize(size, Image.Resampling.LANCZOS)
            
            # Convert to RGBA for transparency support
            if background.mode != 'RGBA':
                background = background.convert('RGBA')
                
            image = background
        else:
            # Create transparent background
            image = Image.new('RGBA', size, self.default_background_color)
        
        # Prepare drawing context
        draw = ImageDraw.Draw(image)
        
        # Load font
        try:
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, self.default_font_size)
            else:
                # Try to load default system font
                font = ImageFont.load_default()
        except Exception as e:
            logger.warning(f"Failed to load font: {e}")
            font = ImageFont.load_default()
        
        # Calculate text positioning for center alignment
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (size[0] - text_width) // 2
        y = (size[1] - text_height) // 2
        
        # Add text shadow for better readability
        shadow_offset = 2
        draw.text((x + shadow_offset, y + shadow_offset), text, font=font, fill=(0, 0, 0, 128))
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
        
        # Convert to bytes
        return self._image_to_bytes(image, 'PNG')
    
    def resize_image(self, image_bytes: bytes, max_size: Tuple[int, int], 
                    maintain_aspect: bool = True) -> bytes:
        """
        Resize image to fit within maximum dimensions while maintaining quality.
        
        This function is essential for performance optimization, ensuring images
        are appropriately sized for different contexts (thumbnails, previews, full-size).
        
        Args:
            image_bytes: Original image data
            max_size: Maximum dimensions (width, height)
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            Resized image data as bytes
            
        Example:
            >>> processor = ImageProcessor()
            >>> with open("large_image.jpg", "rb") as f:
            ...     image_data = f.read()
            >>> resized = processor.resize_image(image_data, (300, 300))
        """
        if not image_bytes:
            raise ValueError("Image data cannot be empty")
        
        try:
            # Load image from bytes
            image = Image.open(BytesIO(image_bytes))
            original_format = image.format or 'PNG'
            
            # Calculate new dimensions
            if maintain_aspect:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            else:
                image = image.resize(max_size, Image.Resampling.LANCZOS)
            
            # Convert to bytes with same format
            return self._image_to_bytes(image, original_format)
            
        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            raise ValueError(f"Invalid image data: {e}")
    
    def create_thumbnail(self, image_bytes: bytes, size: Tuple[int, int] = None) -> bytes:
        """
        Create thumbnail for efficient preview display.
        
        Args:
            image_bytes: Original image data
            size: Thumbnail size, defaults to THUMBNAIL_SIZE
            
        Returns:
            Thumbnail image data as bytes
        """
        if size is None:
            size = self.THUMBNAIL_SIZE
            
        return self.resize_image(image_bytes, size, maintain_aspect=True)
    
    def add_watermark(self, image_bytes: bytes, watermark_text: str, 
                     position: str = "bottom-right", opacity: float = 0.5) -> bytes:
        """
        Add watermark to image for copyright protection.
        
        Design Intent: Support content protection in TxT WORLD Creator's
        
        Args:
            image_bytes: Original image data
            watermark_text: Text to use as watermark
            position: Watermark position ("bottom-right", "bottom-left", "center")
            opacity: Watermark opacity (0.0 to 1.0)
            
        Returns:
            Watermarked image data as bytes
        """
        if not image_bytes or not watermark_text:
            return image_bytes
        
        try:
            image = Image.open(BytesIO(image_bytes))
            
            # Create watermark overlay
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Use default font
            font = ImageFont.load_default()
            
            # Calculate watermark position
            text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            margin = 10
            if position == "bottom-right":
                x = image.width - text_width - margin
                y = image.height - text_height - margin
            elif position == "bottom-left":
                x = margin
                y = image.height - text_height - margin
            else:  # center
                x = (image.width - text_width) // 2
                y = (image.height - text_height) // 2
            
            # Draw watermark with specified opacity
            alpha = int(255 * opacity)
            draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, alpha))
            
            # Composite images
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            watermarked = Image.alpha_composite(image, overlay)
            
            return self._image_to_bytes(watermarked, 'PNG')
            
        except Exception as e:
            logger.error(f"Failed to add watermark: {e}")
            return image_bytes
    
    def convert_format(self, image_bytes: bytes, target_format: str) -> bytes:
        """
        Convert image to different format.
        
        Args:
            image_bytes: Original image data
            target_format: Target format ('PNG', 'JPEG', 'WEBP')
            
        Returns:
            Converted image data as bytes
        """
        if target_format.upper() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {target_format}")
        
        try:
            image = Image.open(BytesIO(image_bytes))
            
            # Handle transparency for JPEG conversion
            if target_format.upper() == 'JPEG' and image.mode in ('RGBA', 'LA'):
                # Create white background for JPEG
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])
                else:
                    background.paste(image)
                image = background
            
            return self._image_to_bytes(image, target_format.upper())
            
        except Exception as e:
            logger.error(f"Failed to convert image format: {e}")
            raise ValueError(f"Format conversion failed: {e}")
    
    def get_image_info(self, image_bytes: bytes) -> dict:
        """
        Extract image metadata and information.
        
        Args:
            image_bytes: Image data
            
        Returns:
            Dictionary with image information
        """
        try:
            image = Image.open(BytesIO(image_bytes))
            
            return {
                'format': image.format,
                'mode': image.mode,
                'size': image.size,
                'width': image.width,
                'height': image.height,
                'has_transparency': image.mode in ('RGBA', 'LA') or 'transparency' in image.info
            }
            
        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            return {}
    
    def _image_to_bytes(self, image: Image.Image, format_name: str) -> bytes:
        """
        Convert PIL Image to bytes.
        
        Args:
            image: PIL Image object
            format_name: Output format
            
        Returns:
            Image data as bytes
        """
        buffer = BytesIO()
        
        # Set quality for JPEG
        if format_name.upper() == 'JPEG':
            image.save(buffer, format=format_name, quality=95, optimize=True)
        else:
            image.save(buffer, format=format_name, optimize=True)
        
        return buffer.getvalue()
    
    @staticmethod
    def validate_image(image_bytes: bytes) -> bool:
        """
        Validate if data represents a valid image.
        
        Args:
            image_bytes: Image data to validate
            
        Returns:
            True if valid image, False otherwise
        """
        if not image_bytes:
            return False
        
        try:
            image = Image.open(BytesIO(image_bytes))
            image.verify()  # Verify image integrity
            return True
        except Exception:
            return False