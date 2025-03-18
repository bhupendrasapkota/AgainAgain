from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.cache import cache
from .models import (
    Photo, PhotoComment, PhotoLike, UserFollow,
    Category, Collection, PhotoDownload, Tag, CollectionLike
)
from PIL import Image as PILImage

User = get_user_model()

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

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at']
        read_only_fields = ['slug', 'created_at']

class UserSerializer(BaseCachedSerializer):
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    photos_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'profile_picture',
            'full_name', 'bio', 'about',
            'followers_count', 'following_count', 'photos_count',
            'is_following', 'created_at'
        ]
        read_only_fields = ['followers_count', 'following_count', 'photos_count']

    def get_followers_count(self, obj):
        return self.get_cached_data(obj, 'user_followers_count',
            lambda x: x.followers.count())

    def get_following_count(self, obj):
        return self.get_cached_data(obj, 'user_following_count',
            lambda x: x.following.count())

    def get_photos_count(self, obj):
        return self.get_cached_data(obj, 'user_photos_count',
            lambda x: x.photos.count())

    def get_is_following(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        
        cache_key = f"user_following:{request.user.id}:{obj.id}"
        is_following = cache.get(cache_key)
        
        if is_following is None:
            is_following = UserFollow.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
            cache.set(cache_key, is_following, timeout=3600)
        
        return is_following

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'created_at']
        read_only_fields = ['slug', 'created_at']

class PhotoSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    categories = CategorySerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Photo
        fields = [
            'id', 'title', 'description', 'image_url', 'user',
            'categories', 'tags', 'created_at', 'updated_at',
            'likes', 'views', 'featured', 'is_public', 'is_liked'
        ]
        read_only_fields = ['created_at', 'updated_at', 'likes', 'views']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_likes(self, obj):
        return obj.likes_count

    def get_views(self, obj):
        return obj.views_count

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(id=request.user.id).exists()
        return False

class PhotoCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        required=True,
        help_text="Upload a photo (JPG, JPEG, PNG, GIF)"
    )
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Photo
        fields = ['title', 'description', 'image', 'categories', 'tags', 'is_public']

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        tags = validated_data.pop('tags', [])
        photo = Photo.objects.create(**validated_data)
        
        if categories:
            photo.categories.set(categories)
        if tags:
            photo.tags.set(tags)
            
        return photo

class PhotoUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        required=False,
        help_text="Upload a photo (JPG, JPEG, PNG, GIF)"
    )
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Photo
        fields = ['title', 'description', 'image', 'categories', 'tags', 'is_public']

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories', None)
        tags = validated_data.pop('tags', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if categories is not None:
            instance.categories.set(categories)
        if tags is not None:
            instance.tags.set(tags)
            
        instance.save()
        return instance

class CollectionSerializer(serializers.ModelSerializer):
    artwork_count = serializers.IntegerField(read_only=True)
    likes = serializers.SerializerMethodField()
    views = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    cover_image = serializers.SerializerMethodField()
    curator = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = Collection
        fields = [
            'id', 'name', 'description', 'user', 'curator',
            'cover_image', 'created_at', 'updated_at',
            'artwork_count', 'likes', 'views', 'is_public', 'is_liked'
        ]
        read_only_fields = ['created_at', 'updated_at', 'artwork_count', 'likes', 'views']

    def get_likes(self, obj):
        return obj.likes_count

    def get_views(self, obj):
        return obj.views_count

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(id=request.user.id).exists()
        return False

    def get_cover_image(self, obj):
        request = self.context.get('request')
        if obj.cover_photo and obj.cover_photo.image:
            return request.build_absolute_uri(obj.cover_photo.image.url)
        return None

class CollectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'is_public']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['curator'] = self.context['request'].user
        return super().create(validated_data)

class CollectionUpdateSerializer(serializers.ModelSerializer):
    cover_photo = serializers.PrimaryKeyRelatedField(
        queryset=Photo.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Collection
        fields = ['name', 'description', 'cover_photo', 'is_public']

class PhotoCommentSerializer(BaseCachedSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    replies_count = serializers.SerializerMethodField()

    class Meta:
        model = PhotoComment
        fields = [
            'id', 'user', 'photo', 'text',
            'created_at', 'updated_at', 'likes_count',
            'parent', 'replies', 'replies_count'
        ]
        read_only_fields = [
            'user', 'photo', 'likes_count',
            'created_at', 'updated_at'
        ]

    def get_replies(self, obj):
        if obj.parent:
            return []
            
        cache_key = f"comment_replies:{obj.id}"
        replies = cache.get(cache_key)
        
        if replies is None:
            replies = PhotoCommentSerializer(
                obj.replies.select_related('user').all(),
                many=True,
                context=self.context
            ).data
            cache.set(cache_key, replies, timeout=3600)
        
        return replies

    def get_replies_count(self, obj):
        if obj.parent:
            return 0
            
        return self.get_cached_data(obj, 'comment_replies_count',
            lambda x: x.replies.count())

    def validate_text(self, value):
        """Validate comment text."""
        if len(value.strip()) < 1:
            raise serializers.ValidationError("Comment text cannot be empty.")
        if len(value) > 1000:
            raise serializers.ValidationError("Comment text too long. Maximum length is 1000 characters.")
        return value.strip()

class UserFollowSerializer(BaseCachedSerializer):
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)

    class Meta:
        model = UserFollow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['follower', 'following', 'created_at']

class PhotoDownloadSerializer(BaseCachedSerializer):
    user = UserSerializer(read_only=True)
    photo = PhotoSerializer(read_only=True)

    class Meta:
        model = PhotoDownload
        fields = [
            'id', 'user', 'photo', 'created_at',
            'download_type', 'ip_address'
        ]
        read_only_fields = [
            'user', 'photo', 'created_at',
            'ip_address'
        ]

    def validate_download_type(self, value):
        """Validate download type."""
        valid_types = ['original', 'large', 'medium', 'small']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Invalid download type. Must be one of: {', '.join(valid_types)}"
            )
        return value
