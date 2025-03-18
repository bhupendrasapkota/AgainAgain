import uuid
import requests
from io import BytesIO
from PIL import Image as PILImage
from django.db import models
from cloudinary.models import CloudinaryField
from django.core.cache import cache
from django.utils import timezone
from django.utils.text import slugify
from django.db.models import F
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.urls import reverse
import os

class BaseTimestampModel(models.Model):
    """Base model with timestamp fields."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(BaseTimestampModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    photos_count = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        db_table = "categories"
        verbose_name_plural = "categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['photos_count']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def update_photos_count(self):
        self.photos_count = self.photos.count()
        self.save(update_fields=['photos_count'])

    def __str__(self):
        return self.name

class Tag(BaseTimestampModel):
    """Model for photo tags."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    photos_count = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        db_table = "tags"
        ordering = ['name']
        indexes = [
            models.Index(fields=['photos_count']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def update_photos_count(self):
        self.photos_count = self.photo_set.count()
        self.save(update_fields=['photos_count'])

    def __str__(self):
        return self.name

class Collection(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_private = models.BooleanField(default=False)
    cover_photo = models.ForeignKey("Photo", on_delete=models.SET_NULL, null=True, blank=True, related_name='collections_as_cover')
    photos = models.ManyToManyField("Photo", related_name='collections')
    artwork_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    exhibition_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    curator = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True, related_name='curated_collections')
    liked_by = models.ManyToManyField("users.User", through='CollectionLike', related_name='liked_collections')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['is_private']),
            models.Index(fields=['artwork_count']),
            models.Index(fields=['views_count']),
            models.Index(fields=['likes_count']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.curator:
            self.curator = self.user
        super().save(*args, **kwargs)
        self.update_artwork_count()
        self.update_cover_photo()

    def update_artwork_count(self):
        self.artwork_count = self.photos.count()
        self.save(update_fields=['artwork_count'])

    def update_cover_photo(self):
        if not self.cover_photo and self.photos.exists():
            self.cover_photo = self.photos.first()
            self.save(update_fields=['cover_photo'])

    def increment_views(self):
        self.views_count = F('views_count') + 1
        self.save()
        self.refresh_from_db()

    def get_absolute_url(self):
        return reverse('collection-detail', kwargs={'pk': self.pk})

class Photo(models.Model):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(
        upload_to='photos/%Y/%m/%d/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])],
        help_text="Upload a photo (JPG, JPEG, PNG, GIF)"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    format = models.CharField(max_length=10, null=True, blank=True)
    categories = models.ManyToManyField(Category, related_name='photos')
    tags = models.ManyToManyField(Tag, related_name='photos')
    likes_count = models.PositiveIntegerField(default=0)
    views_count = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    location = models.CharField(max_length=255, blank=True, null=True)
    camera_info = models.JSONField(null=True, blank=True)
    medium = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=4, blank=True, null=True)
    artist = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    liked_by = models.ManyToManyField("users.User", through='PhotoLike', related_name='liked_photos')
    is_public = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['likes_count']),
            models.Index(fields=['views_count']),
            models.Index(fields=['user']),
            models.Index(fields=['is_public']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.artist and self.user:
            self.artist = self.user.get_full_name() or self.user.username
        super().save(*args, **kwargs)

    def get_aspect_ratio(self):
        if self.height == 0 or not self.height or not self.width:
            return 1
        return self.width / self.height

    def increment_views(self):
        self.views_count = F('views_count') + 1
        self.save()
        self.refresh_from_db()

    def get_absolute_url(self):
        return reverse('photo-detail', kwargs={'pk': self.pk})

    def get_download_url(self, size='original'):
        if not self.image:
            return None
        
        if size == 'original':
            return self.image.url
        
        # Handle different sizes (small, medium, large)
        sizes = {
            'small': (800, 600),
            'medium': (1200, 900),
            'large': (1600, 1200)
        }
        
        if size not in sizes:
            return self.image.url
            
        width, height = sizes[size]
        return f"{self.image.url}?width={width}&height={height}"

    def increment_likes(self):
        self.likes_count = F('likes_count') + 1
        self.save()

    def decrement_likes(self):
        if self.likes_count > 0:
            self.likes_count = F('likes_count') - 1
            self.save()

class PhotoLike(BaseTimestampModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        db_table = "photo_likes"
        unique_together = ['user', 'photo']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'photo']),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update photo likes count
        self.photo.likes_count = self.photo.likes_count + 1
        self.photo.save(update_fields=['likes_count'])
        # Clear cache
        cache.delete(f"photo:{self.photo.id}")

    def delete(self, *args, **kwargs):
        # Update photo likes count before deletion
        self.photo.likes_count = max(0, self.photo.likes_count - 1)
        self.photo.save(update_fields=['likes_count'])
        # Clear cache
        cache.delete(f"photo:{self.photo.id}")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} likes {self.photo.title or 'Untitled'}"

class PhotoComment(BaseTimestampModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    likes_count = models.PositiveIntegerField(default=0, db_index=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    class Meta:
        db_table = "photo_comments"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['photo', '-created_at']),
            models.Index(fields=['parent', '-created_at']),
        ]

class UserFollow(BaseTimestampModel):
    follower = models.ForeignKey("users.User", related_name="following", on_delete=models.CASCADE)
    following = models.ForeignKey("users.User", related_name="followers", on_delete=models.CASCADE)

    class Meta:
        db_table = "user_follows"
        unique_together = ['follower', 'following']
        indexes = [
            models.Index(fields=['follower', 'following']),
        ]

class PhotoDownload(BaseTimestampModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True, blank=True)
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name="downloads")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    download_type = models.CharField(
        max_length=20, 
        default='original',
        choices=[
            ('original', 'Original'),
            ('large', 'Large (1920x1080)'),
            ('medium', 'Medium (1280x720)'),
            ('small', 'Small (640x360)')
        ]
    )

    class Meta:
        db_table = "photo_downloads"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['photo', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

class CollectionLike(BaseTimestampModel):
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        db_table = "collection_likes"
        unique_together = ['user', 'collection']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'collection']),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.collection.likes_count = F('likes_count') + 1
        self.collection.save(update_fields=['likes_count'])

    def delete(self, *args, **kwargs):
        self.collection.likes_count = F('likes_count') - 1
        self.collection.save(update_fields=['likes_count'])
        super().delete(*args, **kwargs)

def photo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.title)}_{instance.id}.{ext}"
    return f"photos/{filename}"
