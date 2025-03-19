from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MinLengthValidator, RegexValidator, URLValidator
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import uuid
from cloudinary.models import CloudinaryField
from PIL import Image, ImageDraw
import io
import logging
from datetime import datetime
import cloudinary
import os

logger = logging.getLogger(__name__)

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(
        max_length=50, 
        unique=True,
        validators=[MinLengthValidator(3)]
    )
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True, max_length=500)
    profile_picture = CloudinaryField('image', folder="profile_pictures/", blank=True, null=True)
    about = models.TextField(blank=True, null=True, max_length=1000)
    phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999'"
            )
        ]
    )
    website = models.URLField(
        max_length=200, 
        blank=True, 
        null=True,
        validators=[URLValidator()]
    )
    location = models.CharField(max_length=100, blank=True, null=True)
    role = models.CharField(
        max_length=20, 
        default='user', 
        choices=[
            ('user', 'User'),
            ('artist', 'Artist'),
            ('curator', 'Curator'),
            ('collector', 'Collector')
        ]
    )

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['role']),
        ]
        ordering = ['-date_joined']

    def save(self, *args, **kwargs):
        if self.password and not self.password.startswith("pbkdf2_sha256"):
            self.set_password(self.password)
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    def clean(self):
        if self.phone and not self.phone.startswith('+'):
            self.phone = '+' + self.phone
        if self.bio and len(self.bio) > 500:
            raise ValidationError("Bio cannot exceed 500 characters")
        if self.about and len(self.about) > 1000:
            raise ValidationError("About cannot exceed 1000 characters")

def process_profile_picture(image):
    """Process and optimize the profile picture."""
    try:
        # Open the image
        img = Image.open(image)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Calculate new dimensions while maintaining aspect ratio
        max_size = (400, 400)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Create a circular mask
        mask = Image.new('L', img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)

        # Apply the mask
        output = Image.new('RGB', img.size, (255, 255, 255))
        output.paste(img, mask=mask)

        # Save the processed image
        output_buffer = io.BytesIO()
        output.save(output_buffer, format='JPEG', quality=85, optimize=True)
        output_buffer.seek(0)

        return output_buffer
    except Exception as e:
        logger.error(f"Error processing profile picture: {str(e)}")
        raise ValidationError(f"Error processing profile picture: {str(e)}")

@receiver(post_save, sender=User)
def handle_profile_picture(sender, instance, **kwargs):
    """Handle profile picture processing after user save."""
    if instance.profile_picture:
        try:
            # Get the current profile picture
            current_picture = instance.profile_picture
            
            # Process the image
            processed_image = process_profile_picture(current_picture)
            
            # Generate a unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"profile_{instance.id}_{timestamp}"
            
            # Upload the processed image
            upload_result = cloudinary.uploader.upload(
                processed_image,
                folder="profile_pictures/",
                public_id=filename,
                resource_type="image",
                overwrite=True
            )
            
            # Update the user's profile picture with the processed version
            instance.profile_picture = upload_result['secure_url']
            instance.save(update_fields=['profile_picture'])
            
        except Exception as e:
            logger.error(f"Error handling profile picture for user {instance.id}: {str(e)}")
            # Don't raise the exception to prevent user creation failure
            # but log it for debugging

class UserFollow(models.Model):
    """Model for user following relationships."""
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        help_text="The user who is following"
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        help_text="The user being followed"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'following']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']

    def clean(self):
        if self.follower == self.following:
            raise ValidationError("A user cannot follow themselves.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"