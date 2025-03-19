from datetime import timezone
from rest_framework import viewsets, status, permissions, throttling
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import F, Q, Count, Prefetch, Exists, OuterRef, Sum
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import (
    Photo, PhotoLike, PhotoComment, Category, Collection,
    PhotoDownload, CollectionLike, PhotoCategory, CollectionPhoto
)
from .serializers import (
    PhotoSerializer, PhotoCommentSerializer, CategorySerializer,
    CollectionSerializer, PhotoDownloadSerializer, PhotoCreateSerializer,
    PhotoUpdateSerializer, PhotoLikeSerializer, CollectionLikeSerializer,
    PhotoCategorySerializer
)
from rest_framework.parsers import MultiPartParser, FormParser
from .permissions import IsOwnerOrReadOnly, IsCollectionOwnerOrReadOnly
from django.http import FileResponse
from django.conf import settings
import os
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class with configurable page size."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })

class PhotoFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='categories__slug', lookup_expr='iexact')
    min_width = filters.NumberFilter(field_name='width', lookup_expr='gte')
    max_width = filters.NumberFilter(field_name='width', lookup_expr='lte')
    min_height = filters.NumberFilter(field_name='height', lookup_expr='gte')
    max_height = filters.NumberFilter(field_name='height', lookup_expr='lte')
    user = filters.CharFilter(field_name='user__username', lookup_expr='iexact')
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_featured = filters.BooleanFilter(field_name='is_featured')
    medium = filters.CharFilter(field_name='medium', lookup_expr='iexact')
    year = filters.CharFilter(field_name='year', lookup_expr='iexact')
    location = filters.CharFilter(field_name='location', lookup_expr='icontains')
    min_likes = filters.NumberFilter(field_name='likes_count', lookup_expr='gte')
    min_views = filters.NumberFilter(field_name='views_count', lookup_expr='gte')
    is_public = filters.BooleanFilter(field_name='is_public')
    is_archived = filters.BooleanFilter(field_name='is_archived')

    class Meta:
        model = Photo
        fields = [
            'category', 'min_width', 'max_width', 'min_height', 'max_height',
            'user', 'created_after', 'created_before', 'is_featured',
            'medium', 'year', 'location', 'min_likes', 'min_views',
            'is_public', 'is_archived'
        ]

class PhotoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing photos.
    Provides CRUD operations and additional actions for photos.
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = StandardResultsSetPagination
    filterset_class = PhotoFilter
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description', 'location', 'user__username']
    ordering_fields = ['created_at', 'likes_count', 'views_count', 'download_count']
    ordering = ['-created_at']
    lookup_field = 'id'
    lookup_url_kwarg = 'photo_id'
    throttle_classes = [throttling.UserRateThrottle]

    def get_queryset(self):
        queryset = Photo.objects.all()
        category = self.request.query_params.get('category', None)
        user = self.request.query_params.get('user', None)
        search = self.request.query_params.get('search', None)

        if category:
            queryset = queryset.filter(categories__slug=category)
        if user:
            queryset = queryset.filter(user__username=user)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(location__icontains=search)
            )

        return queryset.select_related('user').prefetch_related(
            'categories', 'likes', 'comments'
        ).annotate(
            is_liked=Exists(
                PhotoLike.objects.filter(
                    photo=OuterRef('pk'),
                    user=self.request.user
                )
            ) if self.request.user.is_authenticated else False
        )

    def get_serializer_class(self):
        if self.action == 'create':
            return PhotoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PhotoUpdateSerializer
        return PhotoSerializer

    @swagger_auto_schema(
        operation_description="Upload a new photo",
        request_body=PhotoCreateSerializer,
        responses={201: PhotoSerializer, 400: "Bad Request"}
    )
    @action(detail=False, methods=['post'])
    def upload(self, request):
        serializer = PhotoCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    photo = serializer.save(user=request.user)
                    return Response(
                        PhotoSerializer(photo).data,
                        status=status.HTTP_201_CREATED
                    )
            except ValidationError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="Like a photo",
        responses={200: PhotoSerializer, 400: "Bad Request"}
    )
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        photo = self.get_object()
        if not photo.is_public and photo.user != request.user:
            return Response(
                {'error': 'Cannot like private photos'},
                status=status.HTTP_403_FORBIDDEN
            )

        with transaction.atomic():
            like, created = PhotoLike.objects.get_or_create(
                photo=photo,
                user=request.user
            )
            
            if not created:
                like.delete()
                photo.likes_count = F('likes_count') - 1
            else:
                photo.likes_count = F('likes_count') + 1
                
            photo.save()
            photo.refresh_from_db()
            
            serializer = self.get_serializer(photo)
            return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Unlike a photo",
        responses={200: "Success", 400: "Bad Request"}
    )
    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        photo = self.get_object()
        try:
            with transaction.atomic():
                like = PhotoLike.objects.get(photo=photo, user=request.user)
                like.delete()
                photo.likes_count = F('likes_count') - 1
                photo.save()
                photo.refresh_from_db()
                return Response({'message': 'Photo unliked successfully'})
        except PhotoLike.DoesNotExist:
            return Response(
                {'error': 'You have not liked this photo'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Get download URL for a photo",
        manual_parameters=[
            openapi.Parameter(
                'size',
                openapi.IN_QUERY,
                description="Size of the photo to download (original, large, medium, small)",
                type=openapi.TYPE_STRING
            )
        ],
        responses={200: "Success", 400: "Bad Request"}
    )
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        photo = self.get_object()
        if not photo.is_public and photo.user != request.user:
            return Response(
                {'error': 'Cannot download private photos'},
                status=status.HTTP_403_FORBIDDEN
            )

        size = request.query_params.get('size', 'original')
        download_url = photo.get_download_url(size)
        
        if not download_url:
            return Response(
                {'error': 'Download URL not available'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Record download
        PhotoDownload.objects.create(
            photo=photo,
            user=request.user,
            download_type=size,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            referrer=request.META.get('HTTP_REFERER')
        )

        return Response({'download_url': download_url})

    @swagger_auto_schema(
        operation_description="Get similar photos",
        responses={200: PhotoSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        photo = self.get_object()
        similar_photos = Photo.objects.filter(
            Q(categories__in=photo.categories.all()) |
            Q(medium=photo.medium) |
            Q(year=photo.year)
        ).exclude(id=photo.id).distinct()[:10]
        
        serializer = self.get_serializer(similar_photos, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get photo statistics",
        responses={200: "Success"}
    )
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        photo = self.get_object()
        if not photo.is_public and photo.user != request.user:
            return Response(
                {'error': 'Cannot view private photo stats'},
                status=status.HTTP_403_FORBIDDEN
            )

        stats = {
            'likes_count': photo.likes_count,
            'views_count': photo.views_count,
            'download_count': photo.download_count,
            'comments_count': photo.comments.filter(is_public=True).count(),
            'collections_count': photo.collections.count(),
            'created_at': photo.created_at,
            'last_viewed_at': photo.last_viewed_at,
            'last_downloaded_at': photo.downloads.order_by('-created_at').first().created_at if photo.downloads.exists() else None
        }
        
        return Response(stats)

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing categories.
    Provides CRUD operations and additional actions for categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'photos_count', 'order']
    ordering = ['order', 'name']

    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get photos in a category",
        responses={200: PhotoSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        category = self.get_object()
        photos = category.photos.filter(is_public=True)
        page = self.paginate_queryset(photos)
        if page is not None:
            serializer = PhotoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Get category statistics",
        responses={200: "Success"}
    )
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        category = self.get_object()
        stats = {
            'photos_count': category.photos_count,
            'public_photos_count': category.photos.filter(is_public=True).count(),
            'total_views': category.photos.aggregate(total_views=Sum('views_count'))['total_views'] or 0,
            'total_likes': category.photos.aggregate(total_likes=Sum('likes_count'))['total_likes'] or 0,
            'total_downloads': category.photos.aggregate(total_downloads=Sum('download_count'))['total_downloads'] or 0
        }
        return Response(stats)

class CollectionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing collections.
    Provides CRUD operations and additional actions for collections.
    """
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCollectionOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_private', 'is_featured', 'user']
    search_fields = ['name', 'description', 'user__username']
    ordering_fields = ['created_at', 'artwork_count', 'views_count', 'likes_count']
    ordering = ['-created_at']
    lookup_field = 'id'
    lookup_url_kwarg = 'collection_id'
    throttle_classes = [throttling.UserRateThrottle]

    def get_queryset(self):
        queryset = Collection.objects.all()
        user = self.request.query_params.get('user', None)
        search = self.request.query_params.get('search', None)

        if user:
            queryset = queryset.filter(user__username=user)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )

        return queryset.select_related('user', 'cover_photo').prefetch_related(
            'photos', 'likes'
        ).annotate(
            is_liked=Exists(
                CollectionLike.objects.filter(
                    collection=OuterRef('pk'),
                    user=self.request.user
                )
            ) if self.request.user.is_authenticated else False
        )

    def get_serializer_class(self):
        return CollectionSerializer

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Like a collection",
        responses={200: CollectionSerializer, 400: "Bad Request"}
    )
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        collection = self.get_object()
        if not collection.is_private or collection.user == request.user:
            with transaction.atomic():
                like, created = CollectionLike.objects.get_or_create(
                    collection=collection,
                    user=request.user
                )
                
                if not created:
                    like.delete()
                    collection.likes_count = F('likes_count') - 1
                else:
                    collection.likes_count = F('likes_count') + 1
                    
                collection.save()
                collection.refresh_from_db()
                
                serializer = self.get_serializer(collection)
                return Response(serializer.data)
        return Response(
            {'error': 'Cannot like private collections'},
            status=status.HTTP_403_FORBIDDEN
        )

    @swagger_auto_schema(
        operation_description="Unlike a collection",
        responses={200: "Success", 400: "Bad Request"}
    )
    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        collection = self.get_object()
        try:
            with transaction.atomic():
                like = CollectionLike.objects.get(
                    collection=collection,
                    user=request.user
                )
                like.delete()
                collection.likes_count = F('likes_count') - 1
                collection.save()
                collection.refresh_from_db()
                return Response({'message': 'Collection unliked successfully'})
        except CollectionLike.DoesNotExist:
            return Response(
                {'error': 'You have not liked this collection'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @swagger_auto_schema(
        operation_description="Increment collection views",
        responses={200: CollectionSerializer}
    )
    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        collection = self.get_object()
        if not collection.is_private or collection.user == request.user:
            collection.views_count = F('views_count') + 1
            collection.save()
            collection.refresh_from_db()
            
            serializer = self.get_serializer(collection)
            return Response(serializer.data)
        return Response(
            {'error': 'Cannot view private collections'},
            status=status.HTTP_403_FORBIDDEN
        )

    @swagger_auto_schema(
        operation_description="Add a photo to a collection",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'photo_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'order': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={200: "Success", 400: "Bad Request"}
    )
    @action(detail=True, methods=['post'])
    def add_photo(self, request, collection_id=None):
        collection = self.get_object()
        photo_id = request.data.get('photo_id')
        order = request.data.get('order')

        if not photo_id:
            return Response(
                {'error': 'Photo ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            photo = Photo.objects.get(id=photo_id)
            if not photo.is_public and photo.user != request.user:
                return Response(
                    {'error': 'Cannot add private photos to collections'},
                    status=status.HTTP_403_FORBIDDEN
                )

            with transaction.atomic():
                collection_photo, created = CollectionPhoto.objects.get_or_create(
                    collection=collection,
                    photo=photo,
                    defaults={'order': order or 0}
                )
                
                if not created:
                    collection_photo.order = order or collection_photo.order
                    collection_photo.save()

                collection.artwork_count = F('artwork_count') + 1
                collection.save()
                collection.refresh_from_db()

                return Response({'message': 'Photo added to collection successfully'})
        except Photo.DoesNotExist:
            return Response(
                {'error': 'Photo not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description="Remove a photo from a collection",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'photo_id': openapi.Schema(type=openapi.TYPE_INTEGER)
            }
        ),
        responses={200: "Success", 400: "Bad Request"}
    )
    @action(detail=True, methods=['post'])
    def remove_photo(self, request, collection_id=None):
        collection = self.get_object()
        photo_id = request.data.get('photo_id')

        if not photo_id:
            return Response(
                {'error': 'Photo ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                collection_photo = CollectionPhoto.objects.get(
                    collection=collection,
                    photo_id=photo_id
                )
                collection_photo.delete()
                
                collection.artwork_count = F('artwork_count') - 1
                collection.save()
                collection.refresh_from_db()

                return Response({'message': 'Photo removed from collection successfully'})
        except CollectionPhoto.DoesNotExist:
            return Response(
                {'error': 'Photo not found in collection'},
                status=status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(
        operation_description="Get collection statistics",
        responses={200: "Success"}
    )
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        collection = self.get_object()
        if not collection.is_private or collection.user == request.user:
            stats = {
                'artwork_count': collection.artwork_count,
                'views_count': collection.views_count,
                'likes_count': collection.likes_count,
                'created_at': collection.created_at,
                'last_viewed_at': collection.last_viewed_at,
                'total_photo_views': collection.photos.aggregate(total_views=Sum('views_count'))['total_views'] or 0,
                'total_photo_likes': collection.photos.aggregate(total_likes=Sum('likes_count'))['total_likes'] or 0,
                'total_photo_downloads': collection.photos.aggregate(total_downloads=Sum('download_count'))['total_downloads'] or 0
            }
            return Response(stats)
        return Response(
            {'error': 'Cannot view private collection stats'},
            status=status.HTTP_403_FORBIDDEN
        )