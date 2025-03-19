import uuid
import requests
from io import BytesIO
from PIL import Image as PILImage
from django.db import models
from cloudinary.models import CloudinaryField
from django.core.cache import cache
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import F, Count, Q, Sum
from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import os
import logging
from datetime import datetime
import cloudinary.uploader
import cloudinary.api

logger = logging.getLogger(__name__)

class BaseTimestampModel(models.Model):
    """Base model with timestamp fields and common functionality."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Override save to handle cache invalidation."""
        super().save(*args, **kwargs)
        self.invalidate_cache()

    def invalidate_cache(self):
        """Invalidate related cache keys."""
        cache_keys = self.get_cache_keys()
        for key in cache_keys:
            cache.delete(key)

    def get_cache_keys(self):
        """Get list of cache keys to invalidate."""
        return []

class Category(BaseTimestampModel):
    """Model for photo categories with optimized relationships."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    photos_count = models.PositiveIntegerField(default=0, db_index=True)
    cover_photo = models.ForeignKey(
        "Photo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='categories_as_cover',
        limit_choices_to={'is_public': True}
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "categories"
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['photos_count']),
            models.Index(fields=['is_active']),
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        self.update_cover_photo()

    def update_photos_count(self):
        """Update the count of photos in this category."""
        self.photos_count = self.photos.filter(is_public=True).count()
        self.save(update_fields=['photos_count'])

    def update_cover_photo(self):
        """Set the first photo as cover if no cover is set."""
        if not self.cover_photo and self.photos.exists():
            self.cover_photo = self.photos.filter(is_public=True).first()
            self.save(update_fields=['cover_photo'])

    def get_cache_keys(self):
        return [
            f'category:{self.id}',
            f'category_photos:{self.id}',
            'category_list'
        ]

class Collection(BaseTimestampModel):
    """Model for photo collections with optimized relationships."""
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name='collections'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_private = models.BooleanField(default=False)
    cover_photo = models.ForeignKey(
        "Photo",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='collections_as_cover',
        limit_choices_to={'is_public': True}
    )
    photos = models.ManyToManyField(
        "Photo",
        through='CollectionPhoto',
        related_name='collections'
    )
    artwork_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(
        "users.User",
        through='CollectionLike',
        related_name='liked_collections'
    )
    is_featured = models.BooleanField(default=False)
    featured_at = models.DateTimeField(null=True, blank=True)
    last_viewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['is_private']),
            models.Index(fields=['artwork_count']),
            models.Index(fields=['views_count']),
            models.Index(fields=['likes_count']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['last_viewed_at']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        self.update_artwork_count()
        self.update_cover_photo()

    def update_artwork_count(self):
        """Update the count of photos in this collection."""
        self.artwork_count = self.photos.filter(is_public=True).count()
        self.save(update_fields=['artwork_count'])

    def update_cover_photo(self):
        """Set the first photo as cover if no cover is set."""
        if not self.cover_photo and self.photos.exists():
            self.cover_photo = self.photos.filter(is_public=True).first()
            self.save(update_fields=['cover_photo'])

    def increment_views(self):
        """Increment the view count and update last viewed timestamp."""
        self.views_count = F('views_count') + 1
        self.last_viewed_at = timezone.now()
        self.save()
        self.refresh_from_db()

    def get_absolute_url(self):
        return reverse('collection-detail', kwargs={'pk': self.pk})

    def get_cache_keys(self):
        return [
            f'collection:{self.id}',
            f'collection_photos:{self.id}',
            f'user_collections:{self.user.id}'
        ]

class CollectionPhoto(BaseTimestampModel):
    """Through model for Collection-Photo relationship with additional metadata."""
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    photo = models.ForeignKey('Photo', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ['collection', 'photo']
        ordering = ['order', '-added_at']
        indexes = [
            models.Index(fields=['collection', 'photo']),
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return f"{self.photo.title} in {self.collection.name}"

class Photo(BaseTimestampModel):
    """Model for photos with optimized Cloudinary integration."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name='photos'
    )
    image = CloudinaryField(
        'image',
        folder='photos/%Y/%m/%d/',
        transformation=[
            {'width': 1200, 'height': 1200, 'crop': 'limit', 'quality': 'auto'},
            {'fetch_format': 'auto'},
            {'radius': 'max'},
            {'dpr': 'auto'},
            {'responsive': True}
        ],
        format='auto'
    )
    thumbnail = CloudinaryField(
        'image',
        folder='photos/thumbnails/%Y/%m/%d/',
        transformation=[
            {'width': 400, 'height': 400, 'crop': 'fill', 'gravity': 'auto', 'quality': 'auto'},
            {'fetch_format': 'auto'},
            {'radius': 'max'},
            {'dpr': 'auto'},
            {'responsive': True}
        ],
        format='auto',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    format = models.CharField(max_length=10, null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    exif_data = models.JSONField(null=True, blank=True)
    categories = models.ManyToManyField(
        Category,
        through='PhotoCategory',
        related_name='photos'
    )
    likes_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(
        "users.User",
        through='PhotoLike',
        related_name='liked_photos'
    )
    is_public = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    featured_at = models.DateTimeField(null=True, blank=True)
    last_viewed_at = models.DateTimeField(null=True, blank=True)
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    processing_error = models.TextField(null=True, blank=True)
    medium = models.CharField(max_length=50, null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['likes_count']),
            models.Index(fields=['views_count']),
            models.Index(fields=['user']),
            models.Index(fields=['is_public']),
            models.Index(fields=['is_archived']),
            models.Index(fields=['download_count']),
            models.Index(fields=['comment_count']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['processing_status']),
            models.Index(fields=['last_viewed_at']),
            models.Index(fields=['medium']),
            models.Index(fields=['year']),
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.image and not self.width:
            try:
                self.processing_status = 'processing'
                super().save(*args, **kwargs)
                
                # Process image dimensions and metadata
                with PILImage.open(self.image) as img:
                    self.width, self.height = img.size
                    self.format = img.format.lower()
                    
                    # Extract EXIF data
                    if hasattr(img, '_getexif') and img._getexif():
                        self.exif_data = self._extract_exif_data(img._getexif())
                    
                    # Generate thumbnail
                    if not self.thumbnail:
                        self.generate_thumbnail()
                    
                    # Update file size
                    if hasattr(self.image, 'size'):
                        self.file_size = self.image.size
                
                self.processing_status = 'completed'
                super().save(update_fields=[
                    'width', 'height', 'format', 'exif_data',
                    'thumbnail', 'file_size', 'processing_status'
                ])
                
            except Exception as e:
                logger.error(f"Error processing image: {str(e)}")
                self.processing_status = 'failed'
                self.processing_error = str(e)
                super().save(update_fields=['processing_status', 'processing_error'])
        else:
            super().save(*args, **kwargs)

    def _extract_exif_data(self, exif):
        """Extract relevant EXIF data from the image."""
        try:
            exif_data = {}
            for tag_id in exif:
                tag = PILImage.ExifTags.TAGS.get(tag_id, tag_id)
                data = exif.get(tag_id)
                if isinstance(data, bytes):
                    data = data.decode(errors='replace')
                exif_data[tag] = data
            return exif_data
        except Exception as e:
            logger.error(f"Error extracting EXIF data: {str(e)}")
            return None

    def generate_thumbnail(self):
        """Generate a thumbnail version of the image."""
        try:
            if self.image:
                thumbnail_url = self.image.build_url(
                    transformation=[
                        {'width': 400, 'height': 400, 'crop': 'fill', 'gravity': 'auto', 'quality': 'auto'},
                        {'fetch_format': 'auto'},
                        {'radius': 'max'},
                        {'dpr': 'auto'},
                        {'responsive': True}
                    ]
                )
                self.thumbnail = thumbnail_url
        except Exception as e:
            logger.error(f"Error generating thumbnail: {str(e)}")
            raise

    def get_aspect_ratio(self):
        """Calculate the aspect ratio of the image."""
        if self.height == 0 or not self.height or not self.width:
            return 1
        return self.width / self.height

    def increment_views(self):
        """Increment the view count and update last viewed timestamp."""
        self.views_count = F('views_count') + 1
        self.last_viewed_at = timezone.now()
        self.save()
        self.refresh_from_db()

    def get_absolute_url(self):
        return reverse('photo-detail', kwargs={'pk': self.pk})

    def get_download_url(self, size='original'):
        """Get the download URL for different image sizes."""
        if not self.image:
            return None
        
        sizes = {
            'small': (800, 600),
            'medium': (1200, 900),
            'large': (1600, 1200)
        }
        
        if size == 'original':
            return self.image.url
            
        if size not in sizes:
            return self.image.url
            
        width, height = sizes[size]
        return self.image.build_url(
            transformation=[
                {'width': width, 'height': height, 'crop': 'limit', 'quality': 'auto'},
                {'fetch_format': 'auto'},
                {'dpr': 'auto'},
                {'responsive': True}
            ]
        )

    def increment_likes(self):
        """Increment the likes count."""
        self.likes_count = F('likes_count') + 1
        self.save()

    def decrement_likes(self):
        """Decrement the likes count."""
        if self.likes_count > 0:
            self.likes_count = F('likes_count') - 1
            self.save()

    def increment_downloads(self):
        """Increment the download count."""
        self.download_count = F('download_count') + 1
        self.save()

    def update_comment_count(self):
        """Update the comment count."""
        self.comment_count = self.comments.filter(is_public=True).count()
        self.save(update_fields=['comment_count'])

    def mark_as_featured(self):
        """Mark the photo as featured."""
        self.is_featured = True
        self.featured_at = timezone.now()
        self.save(update_fields=['is_featured', 'featured_at'])

    def unmark_as_featured(self):
        """Remove featured status from the photo."""
        self.is_featured = False
        self.featured_at = None
        self.save(update_fields=['is_featured', 'featured_at'])

    def archive(self):
        """Archive the photo."""
        self.is_archived = True
        self.save(update_fields=['is_archived'])

    def unarchive(self):
        """Unarchive the photo."""
        self.is_archived = False
        self.save(update_fields=['is_archived'])

    def get_cache_keys(self):
        return [
            f'photo:{self.id}',
            f'user_photos:{self.user.id}',
            f'category_photos:{self.categories.first().id if self.categories.exists() else None}'
        ]

class PhotoCategory(BaseTimestampModel):
    """Through model for Photo-Category relationship."""
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['photo', 'category']
        ordering = ['-added_at']
        indexes = [
            models.Index(fields=['photo', 'category']),
        ]

    def __str__(self):
        return f"{self.photo.title} in {self.category.name}"

class PhotoLike(BaseTimestampModel):
    """Model for photo likes with optimized relationships."""
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        db_table = "photo_likes"
        unique_together = ['user', 'photo']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'photo']),
        ]

    def clean(self):
        """Validate that user hasn't already liked the photo."""
        if PhotoLike.objects.filter(user=self.user, photo=self.photo).exists():
            raise ValidationError(_("You have already liked this photo."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        self.photo.increment_likes()
        cache.delete(f"photo_likes:{self.photo.id}")

    def delete(self, *args, **kwargs):
        self.photo.decrement_likes()
        cache.delete(f"photo_likes:{self.photo.id}")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} likes {self.photo.title or 'Untitled'}"

class PhotoComment(BaseTimestampModel):
    """Model for photo comments with optimized relationships."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='replies'
    )
    is_public = models.BooleanField(default=True)
    likes_count = models.PositiveIntegerField(default=0)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "photo_comments"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'photo']),
            models.Index(fields=['parent']),
            models.Index(fields=['is_public']),
            models.Index(fields=['likes_count']),
        ]

    def clean(self):
        """Validate comment text."""
        if not self.text.strip():
            raise ValidationError(_("Comment cannot be empty."))
        if len(self.text.strip()) > 1000:
            raise ValidationError(_("Comment cannot exceed 1000 characters."))

    def save(self, *args, **kwargs):
        self.clean()
        if not self.pk:  # New comment
            self.photo.comment_count = F('comment_count') + 1
            self.photo.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.photo.comment_count = F('comment_count') - 1
        self.photo.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.photo.title}"

class CollectionLike(BaseTimestampModel):
    """Model for collection likes with optimized relationships."""
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        db_table = "collection_likes"
        unique_together = ['user', 'collection']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'collection']),
        ]

    def clean(self):
        """Validate that user hasn't already liked the collection."""
        if CollectionLike.objects.filter(user=self.user, collection=self.collection).exists():
            raise ValidationError(_("You have already liked this collection."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        self.collection.likes_count = F('likes_count') + 1
        self.collection.save()

    def delete(self, *args, **kwargs):
        self.collection.likes_count = F('likes_count') - 1
        self.collection.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} likes {self.collection.name}"

class PhotoDownload(BaseTimestampModel):
    """Model for tracking photo downloads with optimized relationships."""
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="downloads")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    download_type = models.CharField(
        max_length=10,
        choices=[
            ('original', 'Original'),
            ('medium', 'Medium'),
            ('small', 'Small')
        ],
        default='original'
    )
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)

    class Meta:
        db_table = "photo_downloads"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'photo']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['download_type']),
        ]

    def clean(self):
        """Validate download type."""
        if self.download_type not in dict(self._meta.get_field('download_type').choices):
            raise ValidationError(_("Invalid download type."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        self.photo.increment_downloads()

    def __str__(self):
        return f"Download of {self.photo.title} by {self.user.username if self.user else 'Anonymous'}"

def photo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.title)}_{instance.id}.{ext}"
    return f"photos/{filename}"
