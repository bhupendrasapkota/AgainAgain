from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Photo
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Photo)
def update_photo_stats(sender, instance, created, **kwargs):
    """Update photo statistics when a photo is saved."""
    if created:
        try:
            instance.update_stats()
        except Exception as e:
            logger.error(f"Error updating stats for photo {instance.id}: {str(e)}")

@receiver(post_delete, sender=Photo)
def cleanup_photo(sender, instance, **kwargs):
    """Cleanup photo resources when deleted."""
    try:
        instance.cleanup()
    except Exception as e:
        logger.error(f"Error cleaning up photo {instance.id}: {str(e)}") 