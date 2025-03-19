from PIL import Image
import magic
import logging
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os

logger = logging.getLogger(__name__)

# Allowed image types and their MIME types
ALLOWED_IMAGE_TYPES = {
    "jpeg": ["image/jpeg"],
    "jpg": ["image/jpeg"],
    "png": ["image/png"],
    "gif": ["image/gif"],
    "webp": ["image/webp"]
}

# Maximum file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

def validate_image(file):
    """Validate image file type and content."""
    try:
        # Check file size
        if file.size > MAX_FILE_SIZE:
            raise ValidationError(_("File size too large. Maximum size is 5MB."))

        # Get file extension
        file_extension = os.path.splitext(file.name)[1].lower().lstrip('.')
        if file_extension not in ALLOWED_IMAGE_TYPES:
            raise ValidationError(_("Invalid file type. Allowed types: JPG, JPEG, PNG, GIF, WEBP"))

        # Check MIME type
        mime = magic.Magic(mime=True)
        file_mime = mime.from_buffer(file.read(1024))
        file.seek(0)  # Reset file pointer

        if file_mime not in ALLOWED_IMAGE_TYPES.get(file_extension, []):
            raise ValidationError(_("Invalid file content. File type does not match extension."))

        # Validate image content
        with Image.open(file) as img:
            # Check if it's a valid image
            img.verify()
            file.seek(0)  # Reset file pointer

            # Check image dimensions
            if img.size[0] > 4000 or img.size[1] > 4000:
                raise ValidationError(_("Image dimensions too large. Maximum size is 4000x4000 pixels."))

            # Check if image is corrupted
            img.load()
            file.seek(0)  # Reset file pointer

        return True

    except ValidationError as e:
        logger.warning(f"Image validation failed: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Error validating image: {str(e)}")
        raise ValidationError(_("Error validating image. Please try again."))

def sanitize_filename(filename):
    """Sanitize filename to prevent security issues."""
    # Remove any path traversal attempts
    filename = os.path.basename(filename)
    
    # Remove any non-alphanumeric characters except dots and hyphens
    filename = ''.join(c for c in filename if c.isalnum() or c in '.-_')
    
    # Ensure the filename doesn't start with a dot
    if filename.startswith('.'):
        filename = filename[1:]
    
    return filename