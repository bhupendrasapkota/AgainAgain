from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.core.users.models import User
from .serializers import ProfileSerializer
from cloudinary.uploader import upload
from .security import validate_image

class ProfileView(APIView):
    """Handles retrieving and updating user profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retrieve the logged-in user's profile."""
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        """Update user profile fields."""
        user = request.user
        data = request.data.copy()

        if "profile_picture" in request.FILES:
            profile_file = request.FILES["profile_picture"]

            # Validate file content
            if not validate_image(profile_file):
                return Response({"error": "Invalid image format. Allowed formats: JPG, JPEG, PNG."}, status=status.HTTP_400_BAD_REQUEST)

            upload_result = upload(
                profile_file,
                folder=f"Users/Profile_Picture/{user.username}/",
                public_id=f"{user.username}",
                overwrite=True,
                invalidate=True,
                resource_type="image",
                format="jpg",
                transformation=[
                    {"width": 400, "height": 400, "crop": "fill", "gravity": "face", "quality": "auto"}
                ]
            )

            data["profile_picture"] = upload_result["secure_url"]

        serializer = ProfileSerializer(user, data=data, partial=True)
        if serializer.is_valid():
            User.objects.filter(id=user.id).update(**serializer.validated_data)
            return Response({"message": "Profile updated successfully", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
