from django.apps import AppConfig
from django.conf import settings


class PhotosConfig(AppConfig):
    """
    Photo management application configuration.
    
    Handles photo uploads, processing, storage, and management including:
    - Image processing and optimization
    - Cloud storage integration
    - Photo collections and categories
    - User interactions (likes, downloads, etc.)
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.features.photos'
    
    def ready(self):
        """Initialize app-specific settings and signals."""
        try:
            import apps.features.photos.signals  # noqa
        except ImportError:
            pass
            
        # Configure Cloudinary if not already configured
        if not hasattr(settings, 'CLOUDINARY_URL'):
            settings.CLOUDINARY_URL = 'cloudinary://default'
