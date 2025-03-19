from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator, URLValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        min_length=8,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    fullName = serializers.CharField(
        source='full_name',
        required=True,
        max_length=100,
        trim_whitespace=True
    )
    role = serializers.ChoiceField(
        choices=User._meta.get_field('role').choices,
        default='user',
        required=False
    )

    class Meta:
        model = User
        fields = ["id", "email", "password", "password2", "fullName", "role"]
        extra_kwargs = {
            'email': {
                'required': True,
                'allow_blank': False,
                'trim_whitespace': True
            }
        }

    def validate_email(self, value):
        """Validate email format and uniqueness."""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise ValidationError(_('Enter a valid email address.'))
        if User.objects.filter(email=value).exists():
            raise ValidationError(_('A user with this email already exists.'))
        return value.lower()

    def validate_password(self, value):
        """Validate password strength."""
        if len(value) < 8:
            raise ValidationError(_('Password must be at least 8 characters long.'))
        if not re.search(r'[A-Z]', value):
            raise ValidationError(_('Password must contain at least one uppercase letter.'))
        if not re.search(r'[a-z]', value):
            raise ValidationError(_('Password must contain at least one lowercase letter.'))
        if not re.search(r'\d', value):
            raise ValidationError(_('Password must contain at least one number.'))
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError(_('Password must contain at least one special character.'))
        return value

    def validate(self, attrs):
        """Validate all fields together."""
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({"password": _("Password fields didn't match.")})
        
        # Check if username from email is already taken
        email = attrs.get('email')
        username = email.split('@')[0]
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {"email": _("A user with this email already exists.")}
            )
        
        return attrs

    def create(self, validated_data):
        """Create a new user."""
        email = validated_data.get('email')
        username = email.split('@')[0]
        full_name = validated_data.pop('full_name')
        password = validated_data.pop('password')
        
        user = User.objects.create(
            username=username,
            email=email,
            full_name=full_name,
            **validated_data
        )
        user.set_password(password)
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        trim_whitespace=True
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate_email(self, value):
        """Validate email format."""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise ValidationError(_('Enter a valid email address.'))
        return value.lower()