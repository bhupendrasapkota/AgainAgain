from PIL import Image

ALLOWED_IMAGE_TYPES = ["jpeg", "png", "gif", "webp", "tiff", "svg", "jpg"]

def validate_image(file):
    """Validate image file type."""
    try:
        file.seek(0)  # Reset pointer before reading
        with Image.open(file) as img:
            file_type = img.format.lower()
            file.seek(0)  # Reset again before returning
            return file_type in ALLOWED_IMAGE_TYPES
    except Exception:
        return False
