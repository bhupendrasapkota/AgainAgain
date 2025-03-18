from rest_framework import serializers
from apps.core.users.models import User
from django.contrib.auth.hashers import make_password


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    fullName = serializers.CharField(source='full_name')  # Map to full_name field
    role = serializers.CharField(required=False, default='user')

    class Meta:
        model = User
        fields = ["id", "email", "password", "fullName", "role"]
    
    def create(self, validated_data):
        # Generate username from email (before @ symbol)
        email = validated_data.get('email')
        username = email.split('@')[0]
        
        # Get full_name from validated_data
        full_name = validated_data.pop('full_name')  # This contains the fullName value
        
        # Hash the password
        password = make_password(validated_data.pop('password'))
        
        # Create the user with all fields
        user = User.objects.create(
            username=username,
            full_name=full_name,
            password=password,
            **validated_data
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'full_name')
