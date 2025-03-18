from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PhotoViewSet, CategoryViewSet, CollectionViewSet, TagViewSet

app_name = 'photos'

router = DefaultRouter()
router.register(r'photos', PhotoViewSet, basename='photo')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'collections', CollectionViewSet, basename='collection')
router.register(r'tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
]
