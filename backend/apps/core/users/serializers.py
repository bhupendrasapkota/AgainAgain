from rest_framework import serializers
from django.core.validators import RegexValidator, URLValidator
from django.core.exceptions import ValidationError
from apps.core.users.models import User
from django.contrib.auth import get_user_model
from .models import UserFollow

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.CharField(required=False)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "full_name", "bio", 
            "profile_picture", "about", "phone", "website", 
            "location", "role", "followers_count", "following_count", 
            "is_following", "date_joined"
        ]
        read_only_fields = [
            "id", "date_joined", "followers_count", 
            "following_count", "email", "username"
        ]

    def get_followers_count(self, obj):
        return obj.followers.count()

    def get_following_count(self, obj):
        return obj.following.count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.followers.filter(follower=request.user).exists()
        return False

    def validate_phone(self, value):
        if value and not value.startswith('+'):
            value = '+' + value
        return value

    def validate_bio(self, value):
        if value and len(value) > 500:
            raise ValidationError("Bio cannot exceed 500 characters")
        return value

    def validate_about(self, value):
        if value and len(value) > 1000:
            raise ValidationError("About cannot exceed 1000 characters")
        return value

class UserUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.CharField(required=False)
    
    class Meta:
        model = User
        fields = ["full_name", "bio","profile_picture", "about", "phone", "website", "location"]
        extra_kwargs = {
            'phone': {
                'validators': [
                    RegexValidator(
                        regex=r'^\+?1?\d{9,15}$',
                        message="Phone number must be entered in the format: '+999999999'"
                    )
                ]
            },
            'website': {
                'validators': [URLValidator()]
            },
            'bio': {
                'max_length': 500
            },
            'about': {
                'max_length': 1000
            }
        }

class UserFollowSerializer(serializers.ModelSerializer):
    """Serializer for user following relationships."""
    follower = ProfileSerializer(read_only=True)
    following = ProfileSerializer(read_only=True)
    follower_id = serializers.UUIDField(write_only=True)
    following_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = UserFollow
        fields = [
            'id', 'follower', 'following',
            'follower_id', 'following_id',
            'created_at'
        ]
        read_only_fields = ['created_at']

    def validate(self, data):
        """Validate the follow relationship."""
        follower_id = data.get('follower_id')
        following_id = data.get('following_id')

        if follower_id == following_id:
            raise serializers.ValidationError("A user cannot follow themselves.")

        try:
            follower = User.objects.get(id=follower_id)
            following = User.objects.get(id=following_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("One or both users not found.")

        if UserFollow.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError("Already following this user.")

        return data

    def create(self, validated_data):
        follower_id = validated_data.pop('follower_id')
        following_id = validated_data.pop('following_id')
        
        follower = User.objects.get(id=follower_id)
        following = User.objects.get(id=following_id)
        
        return UserFollow.objects.create(follower=follower, following=following)
