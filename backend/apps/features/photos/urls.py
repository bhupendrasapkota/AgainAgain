from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PhotoViewSet, CategoryViewSet, CollectionViewSet

app_name = 'photos'

router = DefaultRouter()
router.register(r'photos', PhotoViewSet, basename='photo')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'collections', CollectionViewSet, basename='collection')

urlpatterns = [
    path('', include(router.urls)),
    # Photo-specific actions
    path('photos/<int:pk>/like/', PhotoViewSet.as_view({'post': 'like', 'delete': 'unlike'}), name='photo-like'),
    path('photos/<int:pk>/download/', PhotoViewSet.as_view({'post': 'download'}), name='photo-download'),
    path('photos/<int:pk>/stats/', PhotoViewSet.as_view({'get': 'stats'}), name='photo-stats'),
    
    # Collection-specific actions
    path('collections/<int:pk>/like/', CollectionViewSet.as_view({'post': 'like', 'delete': 'unlike'}), name='collection-like'),
    path('collections/<int:pk>/photos/', CollectionViewSet.as_view({'post': 'add_photos', 'delete': 'remove_photos'}), name='collection-photos'),
    path('collections/<int:pk>/stats/', CollectionViewSet.as_view({'get': 'stats'}), name='collection-stats'),
    
    # Category-specific actions
    path('categories/<int:pk>/stats/', CategoryViewSet.as_view({'get': 'stats'}), name='category-stats'),
]