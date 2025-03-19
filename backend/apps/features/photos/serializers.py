from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .models import (
    CollectionPhoto, Photo, PhotoCategory, PhotoComment, PhotoLike,
    Category, Collection, PhotoDownload, CollectionLike
)
from PIL import Image as PILImage
from django.utils.translation import gettext_lazy as _
from .utils import process_image, delete_cloudinary_image
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.db.models import F
from apps.core.users.serializers import ProfileSerializer
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class BaseCachedSerializer(serializers.ModelSerializer):
    """Base serializer with caching capabilities."""
    
    def get_cache_key(self, obj, prefix):
        return f"{prefix}:{obj.id}"

    def get_cached_data(self, obj, prefix, callback):
        """Get data from cache or compute and cache it."""
        cache_key = self.get_cache_key(obj, prefix)
        data = cache.get(cache_key)
        if data is None:
            data = callback(obj)
            cache.set(cache_key, data, timeout=3600)  # Cache for 1 hour
        return data

class CategorySerializer(serializers.ModelSerializer):
    """Serializer for photo categories with optimized relationships."""
    photos_count = serializers.IntegerField(read_only=True)
    cover_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'photos_count',
            'cover_photo', 'cover_photo_url', 'is_active', 'order'
        ]
        read_only_fields = ['slug', 'photos_count', 'cover_photo_url']

    def get_cover_photo_url(self, obj):
        """Get the URL of the cover photo."""
        if obj.cover_photo and obj.cover_photo.image:
            return obj.cover_photo.image.url
        return None

    def validate_name(self, value):
        """Validate category name."""
        if len(value.strip()) < 2:
            raise ValidationError(_("Category name must be at least 2 characters long."))
        if len(value.strip()) > 100:
            raise ValidationError(_("Category name cannot exceed 100 characters."))
        return value.strip()

    def validate_description(self, value):
        """Validate category description."""
        if value and len(value.strip()) > 500:
            raise ValidationError(_("Description cannot exceed 500 characters."))
        return value.strip() if value else None

class PhotoCategorySerializer(serializers.ModelSerializer):
    """Serializer for photo-category relationships."""
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PhotoCategory
        fields = ['id', 'category', 'category_id', 'added_at']
        read_only_fields = ['added_at']

    def validate_category_id(self, value):
        """Validate category ID."""
        try:
            category = Category.objects.get(id=value)
            if not category.is_active:
                raise ValidationError(_("This category is not active."))
            return value
        except Category.DoesNotExist:
            raise ValidationError(_("Category not found."))

class PhotoSerializer(serializers.ModelSerializer):
    """Serializer for photos with optimized relationships and caching."""
    user = ProfileSerializer(read_only=True)
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    likes_count = serializers.IntegerField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    download_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    aspect_ratio = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    download_urls = serializers.SerializerMethodField()
    exif_data = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = [
            'id', 'user', 'image', 'thumbnail_url', 'title',
            'description', 'width', 'height', 'format', 'file_size',
            'exif_data', 'categories', 'category_ids',
            'likes_count', 'views_count', 'download_count',
            'comment_count', 'is_liked', 'aspect_ratio',
            'download_urls', 'is_public', 'is_archived',
            'is_featured', 'featured_at', 'last_viewed_at',
            'processing_status', 'processing_error',
            'medium', 'year', 'location', 'latitude', 'longitude',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'width', 'height', 'format', 'file_size',
            'thumbnail_url', 'likes_count', 'views_count',
            'download_count', 'comment_count', 'aspect_ratio',
            'download_urls', 'processing_status', 'processing_error',
            'created_at', 'updated_at'
        ]

    def get_is_liked(self, obj):
        """Check if the current user has liked the photo."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_aspect_ratio(self, obj):
        """Get the aspect ratio of the photo."""
        return obj.get_aspect_ratio()

    def get_thumbnail_url(self, obj):
        """Get the thumbnail URL with caching."""
        cache_key = f'photo_thumbnail:{obj.id}'
        thumbnail_url = cache.get(cache_key)
        
        if thumbnail_url is None:
            thumbnail_url = obj.thumbnail.url if obj.thumbnail else obj.image.url
            cache.set(cache_key, thumbnail_url, timeout=3600)  # Cache for 1 hour
        
        return thumbnail_url

    def get_download_urls(self, obj):
        """Get download URLs for different sizes."""
        return {
            'original': obj.get_download_url('original'),
            'large': obj.get_download_url('large'),
            'medium': obj.get_download_url('medium'),
            'small': obj.get_download_url('small')
        }

    def get_exif_data(self, obj):
        """Get filtered EXIF data."""
        if not obj.exif_data:
            return None
            
        # Filter out sensitive or unnecessary EXIF data
        filtered_exif = {}
        allowed_tags = {
            'DateTimeOriginal', 'Make', 'Model', 'ExposureTime',
            'FNumber', 'ISOSpeedRatings', 'FocalLength',
            'LensModel', 'GPSLatitude', 'GPSLongitude'
        }
        
        for tag, value in obj.exif_data.items():
            if tag in allowed_tags:
                filtered_exif[tag] = value
                
        return filtered_exif

    def validate_title(self, value):
        """Validate photo title."""
        if not value.strip():
            raise ValidationError(_("Title cannot be empty."))
        if len(value.strip()) > 255:
            raise ValidationError(_("Title cannot exceed 255 characters."))
        return value.strip()

    def validate_description(self, value):
        """Validate photo description."""
        if value and len(value.strip()) > 1000:
            raise ValidationError(_("Description cannot exceed 1000 characters."))
        return value.strip() if value else None

    def validate_category_ids(self, value):
        """Validate category IDs."""
        if value:
            category_ids = Category.objects.filter(id__in=value, is_active=True)
            if len(category_ids) != len(value):
                raise ValidationError(_("One or more categories not found or inactive."))
        return value

    def validate(self, data):
        """Validate the entire photo data."""
        if not data.get('image'):
            raise ValidationError(_("Image is required."))
        return data

    def create(self, validated_data):
        """Create a new photo with categories."""
        category_ids = validated_data.pop('category_ids', [])
        photo = super().create(validated_data)
        
        if category_ids:
            for category_id in category_ids:
                PhotoCategory.objects.create(photo=photo, category_id=category_id)
        
        return photo

    def update(self, instance, validated_data):
        """Update a photo and its categories."""
        category_ids = validated_data.pop('category_ids', None)
        photo = super().update(instance, validated_data)
        
        if category_ids is not None:
            # Remove old categories
            photo.categories.clear()
            # Add new categories
            for category_id in category_ids:
                PhotoCategory.objects.create(photo=photo, category_id=category_id)
        
        return photo

class PhotoUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        required=False,
        help_text="Upload a photo (JPG, JPEG, PNG, GIF)"
    )
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Photo
        fields = ['title', 'description', 'image', 'category_ids', 'is_public']

    def update(self, instance, validated_data):
        image_file = validated_data.pop('image', None)
        category_ids = validated_data.pop('category_ids', None)
        
        # Handle image update
        if image_file:
            try:
                # Delete old image from Cloudinary
                if instance.image:
                    public_id = instance.image.split('/')[-1].split('.')[0]
                    delete_cloudinary_image(public_id)
                
                # Process and upload new image
                folder_path = f"photos/{instance.user.id}/%Y/%m/%d/"
                upload_result = process_image(image_file, folder_path)
                validated_data['image'] = upload_result['secure_url']
            except Exception as e:
                raise serializers.ValidationError({'image': str(e)})
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if category_ids is not None:
            instance.categories.set(category_ids)
            
        instance.save()
        return instance

class CollectionPhotoSerializer(serializers.ModelSerializer):
    """Serializer for collection-photo relationships."""
    photo = PhotoSerializer(read_only=True)
    photo_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = CollectionPhoto
        fields = ['id', 'photo', 'photo_id', 'order', 'added_at']
        read_only_fields = ['added_at']

    def validate_photo_id(self, value):
        """Validate photo ID."""
        try:
            photo = Photo.objects.get(id=value)
            if not photo.is_public:
                raise ValidationError(_("Cannot add a private photo to a collection."))
            return value
        except Photo.DoesNotExist:
            raise ValidationError(_("Photo not found."))

class CollectionSerializer(serializers.ModelSerializer):
    """Serializer for collections with optimized relationships."""
    user = ProfileSerializer(read_only=True)
    photos = CollectionPhotoSerializer(source='collectionphoto_set', many=True, read_only=True)
    photo_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    likes_count = serializers.IntegerField(read_only=True)
    views_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    cover_photo_url = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            'id', 'user', 'name', 'slug', 'description',
            'is_private', 'cover_photo', 'cover_photo_url',
            'photos', 'photo_ids', 'artwork_count',
            'views_count', 'likes_count', 'is_liked',
            'is_featured', 'featured_at', 'last_viewed_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'slug', 'artwork_count', 'views_count',
            'likes_count', 'cover_photo_url', 'created_at',
            'updated_at'
        ]

    def get_is_liked(self, obj):
        """Check if the current user has liked the collection."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def get_cover_photo_url(self, obj):
        """Get the URL of the cover photo."""
        if obj.cover_photo and obj.cover_photo.image:
            return obj.cover_photo.image.url
        return None

    def validate_name(self, value):
        """Validate collection name."""
        if not value.strip():
            raise ValidationError(_("Name cannot be empty."))
        if len(value.strip()) > 255:
            raise ValidationError(_("Name cannot exceed 255 characters."))
        return value.strip()

    def validate_description(self, value):
        """Validate collection description."""
        if value and len(value.strip()) > 1000:
            raise ValidationError(_("Description cannot exceed 1000 characters."))
        return value.strip() if value else None

    def validate_photo_ids(self, value):
        """Validate photo IDs."""
        if value:
            photos = Photo.objects.filter(id__in=value, is_public=True)
            if len(photos) != len(value):
                raise ValidationError(_("One or more photos not found or private."))
        return value

    def create(self, validated_data):
        """Create a new collection with photos."""
        photo_ids = validated_data.pop('photo_ids', [])
        collection = super().create(validated_data)
        
        if photo_ids:
            for order, photo_id in enumerate(photo_ids):
                CollectionPhoto.objects.create(
                    collection=collection,
                    photo_id=photo_id,
                    order=order
                )
        
        return collection

    def update(self, instance, validated_data):
        """Update a collection and its photos."""
        photo_ids = validated_data.pop('photo_ids', None)
        collection = super().update(instance, validated_data)
        
        if photo_ids is not None:
            # Remove old photos
            collection.photos.clear()
            # Add new photos
            for order, photo_id in enumerate(photo_ids):
                CollectionPhoto.objects.create(
                    collection=collection,
                    photo_id=photo_id,
                    order=order
                )
        
        return collection

class CollectionLikeSerializer(serializers.ModelSerializer):
    """Serializer for collection likes."""
    user = ProfileSerializer(read_only=True)
    collection_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CollectionLike
        fields = ['id', 'user', 'collection_id', 'created_at']
        read_only_fields = ['created_at']

    def validate_collection_id(self, value):
        """Validate collection ID."""
        try:
            collection = Collection.objects.get(id=value)
            if collection.is_private:
                raise ValidationError(_("Cannot like a private collection."))
            return value
        except Collection.DoesNotExist:
            raise ValidationError(_("Collection not found."))

class PhotoCommentSerializer(serializers.ModelSerializer):
    """Serializer for photo comments with nested replies."""
    user = ProfileSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    likes_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = PhotoComment
        fields = [
            'id', 'user', 'text', 'parent', 'replies',
            'is_public', 'likes_count', 'is_liked',
            'is_edited', 'edited_at', 'created_at'
        ]
        read_only_fields = ['is_edited', 'edited_at', 'created_at']

    def get_replies(self, obj):
        """Get nested replies for the comment."""
        if obj.parent is None:  # Only get replies for top-level comments
            replies = obj.replies.filter(is_public=True).order_by('created_at')
            return PhotoCommentSerializer(replies, many=True).data
        return []

    def get_is_liked(self, obj):
        """Check if the current user has liked the comment."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False

    def validate_text(self, value):
        """Validate comment text."""
        if not value.strip():
            raise ValidationError(_("Comment cannot be empty."))
        if len(value.strip()) > 1000:
            raise ValidationError(_("Comment cannot exceed 1000 characters."))
        return value.strip()

    def validate_parent(self, value):
        """Validate parent comment."""
        if value and value.parent:
            raise ValidationError(_("Replies cannot have their own replies."))
        return value

class PhotoDownloadSerializer(serializers.ModelSerializer):
    """Serializer for photo downloads."""
    user = ProfileSerializer(read_only=True)
    photo_id = serializers.UUIDField(write_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = PhotoDownload
        fields = [
            'id', 'user', 'photo_id', 'download_type',
            'download_url', 'ip_address', 'user_agent',
            'referrer', 'created_at'
        ]
        read_only_fields = ['ip_address', 'user_agent', 'referrer', 'created_at']

    def get_download_url(self, obj):
        """Get the download URL for the photo."""
        return obj.photo.get_download_url(obj.download_type)

    def validate_photo_id(self, value):
        """Validate photo ID."""
        try:
            photo = Photo.objects.get(id=value)
            if not photo.is_public:
                raise ValidationError(_("Cannot download a private photo."))
            return value
        except Photo.DoesNotExist:
            raise ValidationError(_("Photo not found."))

class PhotoLikeSerializer(serializers.ModelSerializer):
    """Serializer for photo likes with validation."""
    user = ProfileSerializer(read_only=True)
    photo_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = PhotoLike
        fields = ['id', 'user', 'photo_id', 'created_at']
        read_only_fields = ['created_at']

    def validate_photo_id(self, value):
        """Validate photo ID."""
        try:
            photo = Photo.objects.get(id=value)
            if not photo.is_public:
                raise ValidationError(_("Cannot like a private photo."))
            return value
        except Photo.DoesNotExist:
            raise ValidationError(_("Photo not found."))

    def validate(self, data):
        """Validate the like data."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise ValidationError(_("You must be logged in to like a photo."))
        
        # Check if user already liked the photo
        if PhotoLike.objects.filter(user=request.user, photo_id=data['photo_id']).exists():
            raise ValidationError(_("You have already liked this photo."))
        
        return data


class PhotoCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new photos with optimized image processing."""
    image = serializers.ImageField(
        required=True,
        help_text="Upload a photo (JPG, JPEG, PNG, GIF)"
    )
    category_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )

    class Meta:
        model = Photo
        fields = ['title', 'description', 'image', 'category_ids', 'is_public']

    def validate_image(self, value):
        """Validate image file."""
        if value.size > 10 * 1024 * 1024:  # 10MB limit
            raise ValidationError(_("Image file too large ( > 10MB )"))
        return value

    def create(self, validated_data):
        """Create a new photo with optimized image processing."""
        category_ids = validated_data.pop('category_ids', [])
        image_file = validated_data.pop('image')
        
        try:
            # Process and upload image
            folder_path = f"photos/{self.context['request'].user.id}/%Y/%m/%d/"
            upload_result = process_image(image_file, folder_path)
            validated_data['image'] = upload_result['secure_url']
            
            # Create photo instance
            photo = Photo.objects.create(**validated_data)
            
            # Set categories
            if category_ids:
                for category_id in category_ids:
                    PhotoCategory.objects.create(photo=photo, category_id=category_id)
            
            return photo
            
        except Exception as e:
            logger.error(f"Error creating photo: {str(e)}")
            raise ValidationError({'image': str(e)})