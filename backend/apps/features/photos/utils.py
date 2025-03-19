import logging
from PIL import Image, ExifTags
from io import BytesIO
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import cloudinary
import cloudinary.uploader
from django.conf import settings
import magic
import os
from datetime import datetime
from typing import Dict, Any, Optional, Union
from functools import cache, lru_cache
import hashlib
import concurrent.futures
from pathlib import Path

logger = logging.getLogger(__name__)

# Constants
ALLOWED_IMAGE_TYPES = {
    'jpeg': ['image/jpeg'],
    'jpg': ['image/jpeg'],
    'png': ['image/png'],
    'gif': ['image/gif'],
    'webp': ['image/webp']
}

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_DIMENSION = 4000
MIN_IMAGE_DIMENSION = 100
MAX_THUMBNAIL_SIZE = (400, 400)
MAX_PREVIEW_SIZE = (800, 600)
MAX_FULL_SIZE = (1600, 1200)

# Cache settings
CACHE_TIMEOUT = 3600  # 1 hour
MAX_CACHE_SIZE = 1000

class ImageProcessingError(Exception):
    """Custom exception for image processing errors."""
    pass

@lru_cache(maxsize=MAX_CACHE_SIZE)
def get_file_hash(file_path: str) -> str:
    """Generate a hash for a file to detect duplicates."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def process_image(
    image_file: Any,
    folder_path: str,
    public_id: Optional[str] = None,
    optimize: bool = True
) -> Dict[str, Any]:
    """
    Process and upload an image to Cloudinary with advanced optimizations.
    
    Args:
        image_file: The image file to process
        folder_path: The folder path in Cloudinary
        public_id: Optional public ID for the image
        optimize: Whether to optimize the image before upload
    
    Returns:
        dict: Cloudinary upload result with additional metadata
    """
    try:
        # Validate image
        validate_image_file(image_file)
        
        # Process image before upload if optimization is enabled
        if optimize:
            processed_image = optimize_image(image_file)
        else:
            processed_image = image_file
        
        # Generate a unique filename if public_id is not provided
        if not public_id:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_hash = get_file_hash(image_file.name) if hasattr(image_file, 'name') else ''
            public_id = f"photo_{timestamp}_{file_hash[:8]}"
        
        # Prepare transformations
        transformations = [
            {'width': 1200, 'height': 1200, 'crop': 'limit', 'quality': 'auto'},
            {'fetch_format': 'auto'},
            {'dpr': 'auto'},
            {'responsive': True}
        ]
        
        # Prepare eager transformations for different sizes
        eager_transformations = [
            {'width': MAX_THUMBNAIL_SIZE[0], 'height': MAX_THUMBNAIL_SIZE[1], 
             'crop': 'fill', 'gravity': 'auto', 'quality': 'auto'},
            {'width': MAX_PREVIEW_SIZE[0], 'height': MAX_PREVIEW_SIZE[1], 
             'crop': 'limit', 'quality': 'auto'},
            {'width': MAX_FULL_SIZE[0], 'height': MAX_FULL_SIZE[1], 
             'crop': 'limit', 'quality': 'auto'}
        ]
        
        # Upload to Cloudinary with error handling
        try:
            upload_result = cloudinary.uploader.upload(
                processed_image,
                folder=folder_path,
                public_id=public_id,
                resource_type="image",
                format="auto",
                transformation=transformations,
                eager=eager_transformations,
                eager_async=True
            )
            
            # Add additional metadata
            upload_result['metadata'] = get_image_metadata(image_file)
            upload_result['processing_status'] = 'completed'
            
            return upload_result
            
        except cloudinary.Error as e:
            logger.error(f"Cloudinary upload error: {str(e)}")
            raise ImageProcessingError(_("Error uploading image to cloud storage."))
            
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise ImageProcessingError(_("Error processing image. Please try again."))

def validate_image_file(image_file: Any) -> None:
    """
    Comprehensive validation of image file type, size, and content.
    
    Args:
        image_file: The image file to validate
        
    Raises:
        ValidationError: If validation fails
    """
    try:
        # Check file size
        if image_file.size > MAX_FILE_SIZE:
            raise ValidationError(_("File size too large. Maximum size is 10MB."))

        # Check file extension
        file_extension = os.path.splitext(image_file.name)[1].lower().lstrip('.')
        if file_extension not in ALLOWED_IMAGE_TYPES:
            raise ValidationError(_("Invalid file type. Allowed types: JPG, JPEG, PNG, GIF, WEBP"))

        # Check MIME type
        mime = magic.Magic(mime=True)
        file_mime = mime.from_buffer(image_file.read(1024))
        image_file.seek(0)  # Reset file pointer

        if file_mime not in ALLOWED_IMAGE_TYPES.get(file_extension, []):
            raise ValidationError(_("Invalid file content. File type does not match extension."))

        # Validate image content
        with Image.open(image_file) as img:
            # Check if it's a valid image
            img.verify()
            image_file.seek(0)  # Reset file pointer

            # Check image dimensions
            width, height = img.size
            if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
                raise ValidationError(_("Image dimensions too large. Maximum size is 4000x4000 pixels."))
            if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
                raise ValidationError(_("Image dimensions too small. Minimum size is 100x100 pixels."))

            # Check if image is corrupted
            img.load()
            image_file.seek(0)  # Reset file pointer

    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Image validation error: {str(e)}")
        raise ValidationError(_("Invalid image file. Please try again."))

def optimize_image(image_file: Any) -> BytesIO:
    """
    Advanced image optimization with quality and size improvements.
    
    Args:
        image_file: The image file to optimize
        
    Returns:
        BytesIO: Optimized image buffer
        
    Raises:
        ImageProcessingError: If optimization fails
    """
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Calculate new dimensions while maintaining aspect ratio
        max_size = (1200, 1200)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save the optimized image with advanced settings
        output_buffer = BytesIO()
        img.save(
            output_buffer,
            format='JPEG',
            quality=85,
            optimize=True,
            progressive=True,
            exif=img.getexif(),
            subsampling=0  # Best quality for chroma subsampling
        )
        output_buffer.seek(0)

        return output_buffer

    except Exception as e:
        logger.error(f"Error optimizing image: {str(e)}")
        raise ImageProcessingError(_("Error optimizing image. Please try again."))

def delete_cloudinary_image(public_id: str) -> None:
    """
    Delete an image from Cloudinary with error handling.
    
    Args:
        public_id: The public ID of the image to delete
        
    Raises:
        ImageProcessingError: If deletion fails
    """
    try:
        # Delete all transformations
        cloudinary.uploader.destroy(public_id, invalidate=True)
        
        # Clear any cached versions
        cache_key = f"cloudinary_image:{public_id}"
        cache.delete(cache_key)
        
    except cloudinary.Error as e:
        logger.error(f"Error deleting image from Cloudinary: {str(e)}")
        raise ImageProcessingError(_("Error deleting image. Please try again."))

def get_image_metadata(image_file: Any) -> Optional[Dict[str, Any]]:
    """
    Extract comprehensive metadata from image file.
    
    Args:
        image_file: The image file to extract metadata from
        
    Returns:
        Optional[Dict[str, Any]]: Dictionary containing image metadata
    """
    try:
        with Image.open(image_file) as img:
            metadata = {
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'info': img.info,
                'exif': None,
                'dpi': img.info.get('dpi', None),
                'compression': img.info.get('compression', None),
                'progressive': img.info.get('progressive', False)
            }
            
            if hasattr(img, '_getexif') and img._getexif():
                exif_data = {}
                for tag_id in img._getexif():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    data = img._getexif().get(tag_id)
                    if isinstance(data, bytes):
                        try:
                            data = data.decode(errors='replace')
                        except UnicodeDecodeError:
                            data = str(data)
                    exif_data[tag] = data
                metadata['exif'] = exif_data
            
            return metadata
            
    except Exception as e:
        logger.error(f"Error extracting image metadata: {str(e)}")
        return None

def process_image_batch(
    image_files: list,
    folder_path: str,
    max_workers: int = 4
) -> list:
    """
    Process multiple images in parallel.
    
    Args:
        image_files: List of image files to process
        folder_path: The folder path in Cloudinary
        max_workers: Maximum number of parallel workers
        
    Returns:
        list: List of processing results
    """
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {
            executor.submit(process_image, file, folder_path): file 
            for file in image_files
        }
        
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {file}: {str(e)}")
                results.append({
                    'file': file,
                    'error': str(e),
                    'status': 'failed'
                })
    
    return results 