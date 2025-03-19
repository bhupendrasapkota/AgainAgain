from rest_framework import serializers
from django.core.validators import RegexValidator, URLValidator
from django.core.exceptions import ValidationError
from apps.core.users.models import User

class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.CharField(required=False)
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    email = serializers.EmailField(read_only=True)
    username = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            "id", "username", "email", "full_name", "bio", 
            "profile_picture", "about", "phone", "website", 
            "location", "followers_count", "following_count", 
            "date_joined", "role"
        ]
        read_only_fields = [
            "id", "date_joined", "followers_count", 
            "following_count", "email", "username"
        ]

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
    class Meta:
        model = User
        fields = ["full_name", "bio", "about", "phone", "website", "location"]
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
