from django.contrib.auth import authenticate
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.conf import settings
import logging
from apps.core.users.models import User
from .serializers import RegisterSerializer, LoginSerializer

logger = logging.getLogger(__name__)

class AuthViewSet(ViewSet):
    """Handles authentication: Register, Login, Logout"""
    permission_classes = [AllowAny]

    def _get_user_response(self, user):
        """Generate standardized user response"""
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "full_name": user.full_name,
            "profile_picture": user.profile_picture.url if user.profile_picture else None
        }

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        """User Registration"""
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                refresh = RefreshToken.for_user(user)
                
                # Cache user data for better performance
                cache_key = f"user_{user.id}"
                cache.set(cache_key, self._get_user_response(user), timeout=3600)
                
                return Response({
                    "token": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": self._get_user_response(user)
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return Response(
                {"error": "Registration failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        """User Login"""
        try:
            serializer = LoginSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data["email"]
                password = serializer.validated_data["password"]

                # Check for too many login attempts
                cache_key = f"login_attempts_{email}"
                attempts = cache.get(cache_key, 0)
                if attempts >= settings.MAX_LOGIN_ATTEMPTS:
                    return Response(
                        {"error": "Too many login attempts. Please try again later."},
                        status=status.HTTP_429_TOO_MANY_REQUESTS
                    )

                user = get_object_or_404(User, email=email)
                if not user.is_active:
                    return Response(
                        {"error": "Account is inactive. Please activate your account."},
                        status=status.HTTP_403_FORBIDDEN
                    )

                if not user.check_password(password):
                    # Increment failed login attempts
                    cache.set(cache_key, attempts + 1, timeout=3600)
                    return Response(
                        {"error": "Invalid credentials"},
                        status=status.HTTP_401_UNAUTHORIZED
                    )

                # Reset login attempts on successful login
                cache.delete(cache_key)
                
                refresh = RefreshToken.for_user(user)
                
                # Cache user data
                cache_key = f"user_{user.id}"
                cache.set(cache_key, self._get_user_response(user), timeout=3600)
                
                return Response({
                    "token": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": self._get_user_response(user)
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {"error": "Login failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=["post"], url_path="logout")
    def logout(self, request):
        """User Logout - Blacklist Refresh Token"""
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            # Clear user cache
            user_id = token.payload.get('user_id')
            if user_id:
                cache.delete(f"user_{user_id}")
            
            return Response(
                {"message": "Logout successful"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST
            )