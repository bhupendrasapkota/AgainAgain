from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProfileView, UserFollowViewSet

router = DefaultRouter()
router.register(r'follows', UserFollowViewSet, basename='user-follow')

app_name = "users"

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]
