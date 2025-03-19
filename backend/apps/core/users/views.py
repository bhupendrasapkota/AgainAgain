from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.cache import cache
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db import transaction
import logging
from apps.core.users.models import User
from .serializers import ProfileSerializer, UserUpdateSerializer, UserFollowSerializer
from cloudinary.uploader import upload
from .security import validate_image
from rest_framework import viewsets
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from .models import UserFollow

logger = logging.getLogger(__name__)

User = get_user_model()

class ProfileView(APIView):
    """Handles retrieving and updating user profile."""
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get(self, request):
        """Retrieve the logged-in user's profile."""
        try:
            # Try to get from cache first
            cache_key = f"user_profile_{request.user.id}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return Response(cached_data, status=status.HTTP_200_OK)
            
            # If not in cache, get from database
            serializer = ProfileSerializer(request.user)
            data = serializer.data
            
            # Cache the response
            cache.set(cache_key, data, timeout=3600)
            
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error retrieving profile: {str(e)}")
            return Response(
                {"error": _("Error retrieving profile. Please try again.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @transaction.atomic
    def patch(self, request):
        """Update user profile fields."""
        try:
            user = request.user
            data = request.data.copy()

            if "profile_picture" in request.FILES:
                profile_file = request.FILES["profile_picture"]

                # Validate file content
                if not validate_image(profile_file):
                    return Response(
                        {"error": _("Invalid image format. Allowed formats: JPG, JPEG, PNG.")},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # Validate file size
                if profile_file.size > settings.MAX_UPLOAD_SIZE:
                    return Response(
                        {"error": _("File size too large. Maximum size is 5MB.")},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                try:
                    upload_result = upload(
                        profile_file,
                        folder=f"Users/Profile_Picture/{user.username}/",
                        public_id=f"{user.username}",
                        overwrite=True,
                        invalidate=True,
                        resource_type="image",
                        format="jpg",
                        transformation=[
                            {"width": 400, "height": 400, "crop": "fill", "gravity": "face", "quality": "auto"},
                            {"radius": "max"}
                        ]
                    )
                    data["profile_picture"] = upload_result["secure_url"]
                except Exception as e:
                    logger.error(f"Error uploading profile picture: {str(e)}")
                    return Response(
                        {"error": _("Error uploading profile picture. Please try again.")},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

            # Use UserUpdateSerializer for better validation
            serializer = UserUpdateSerializer(user, data=data, partial=True)
            if serializer.is_valid():
                # Update user fields
                for field, value in serializer.validated_data.items():
                    setattr(user, field, value)
                user.save()

                # Clear cache
                cache.delete(f"user_profile_{user.id}")
                
                # Get updated data
                updated_data = ProfileSerializer(user).data
                
                return Response({
                    "message": _("Profile updated successfully"),
                    "data": updated_data
                }, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return Response(
                {"error": _("Error updating profile. Please try again.")},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserFollowViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user following relationships."""
    serializer_class = UserFollowSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get the queryset based on the action."""
        if self.action == 'list':
            return UserFollow.objects.filter(follower=self.request.user)
        return UserFollow.objects.all()

    def perform_create(self, serializer):
        """Create a new follow relationship."""
        serializer.save(follower=self.request.user)

    @action(detail=False, methods=['get'])
    def followers(self, request):
        """Get the user's followers."""
        followers = UserFollow.objects.filter(following=request.user)
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def following(self, request):
        """Get the users that the current user is following."""
        following = UserFollow.objects.filter(follower=request.user)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)