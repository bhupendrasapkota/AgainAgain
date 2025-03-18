from datetime import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import F, Q, Count, Prefetch, Exists, OuterRef
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Photo, PhotoLike, PhotoComment, UserFollow, Category, Collection, PhotoDownload, CollectionLike, Tag
from .serializers import (
    PhotoSerializer,
    PhotoCommentSerializer,
    UserFollowSerializer,
    CategorySerializer,
    CollectionSerializer,
    PhotoDownloadSerializer,
    TagSerializer,
    PhotoCreateSerializer,
    PhotoUpdateSerializer,
    CollectionCreateSerializer,
    CollectionUpdateSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser
from .permissions import IsOwnerOrReadOnly, IsCollectionOwnerOrReadOnly
from django.http import FileResponse
from django.conf import settings
import os

class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class with configurable page size."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

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
    tag = filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')

    class Meta:
        model = Photo
        fields = ['category', 'min_width', 'max_width', 'min_height', 'max_height',
                 'user', 'created_after', 'created_before', 'is_featured',
                 'medium', 'year', 'location', 'tag']

class PhotoViewSet(viewsets.ModelViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = StandardResultsSetPagination
    filterset_class = PhotoFilter
    lookup_field = 'id'
    lookup_url_kwarg = 'photo_id'

    def get_queryset(self):
        queryset = Photo.objects.all()
        category = self.request.query_params.get('category', None)
        tag = self.request.query_params.get('tag', None)
        user = self.request.query_params.get('user', None)
        search = self.request.query_params.get('search', None)

        if category:
            queryset = queryset.filter(categories__slug=category)
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        if user:
            queryset = queryset.filter(user__username=user)
        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset.select_related('user').prefetch_related('categories', 'tags')

    def get_serializer_class(self):
        if self.action == 'create':
            return PhotoCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PhotoUpdateSerializer
        return PhotoSerializer

    @action(detail=False, methods=['post'])
    def upload(self, request):
        serializer = PhotoCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        photo = self.get_object()
        user = request.user
        like, created = PhotoLike.objects.get_or_create(photo=photo, user=user)
        
        if not created:
            like.delete()
            photo.likes_count = F('likes_count') - 1
        else:
            photo.likes_count = F('likes_count') + 1
            
        photo.save()
        photo.refresh_from_db()
        
        serializer = self.get_serializer(photo)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        photo = self.get_object()
        user = request.user
        try:
            like = PhotoLike.objects.get(photo=photo, user=user)
            like.delete()
            photo.likes_count = F('likes_count') - 1
            photo.save()
            photo.refresh_from_db()
            return Response({'message': 'Photo unliked successfully'})
        except PhotoLike.DoesNotExist:
            return Response(
                {'message': 'You have not liked this photo'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        photo = self.get_object()
        size = request.query_params.get('size', 'original')
        download_url = photo.get_download_url(size)
        if not download_url:
            return Response(
                {'message': 'Download URL not available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response({'download_url': download_url})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        category = self.get_object()
        photos = category.photos.all()
        page = self.paginate_queryset(photos)
        if page is not None:
            serializer = PhotoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data)

class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCollectionOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    lookup_field = 'id'
    lookup_url_kwarg = 'collection_id'

    def get_queryset(self):
        queryset = Collection.objects.all()
        user = self.request.query_params.get('user', None)
        search = self.request.query_params.get('search', None)

        if user:
            queryset = queryset.filter(user__username=user)
        if search:
            queryset = queryset.filter(name__icontains=search)

        return queryset.select_related('user', 'curator', 'cover_photo')

    def get_serializer_class(self):
        if self.action == 'create':
            return CollectionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CollectionUpdateSerializer
        return CollectionSerializer

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        collection = self.get_object()
        user = request.user
        if collection.liked_by.filter(id=user.id).exists():
            collection.liked_by.remove(user)
            collection.likes_count = F('likes_count') - 1
        else:
            collection.liked_by.add(user)
            collection.likes_count = F('likes_count') + 1
        
        collection.save()
        collection.refresh_from_db()
        
        serializer = self.get_serializer(collection)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'])
    def unlike(self, request, pk=None):
        collection = self.get_object()
        user = request.user
        if not collection.liked_by.filter(id=user.id).exists():
            return Response(
                {'message': 'You have not liked this collection'},
                status=status.HTTP_400_BAD_REQUEST
            )
        collection.liked_by.remove(user)
        collection.likes_count = F('likes_count') - 1
        collection.save()
        collection.refresh_from_db()
        
        serializer = self.get_serializer(collection)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def increment_views(self, request, pk=None):
        collection = self.get_object()
        collection.views = F('views') + 1
        collection.save()
        collection.refresh_from_db()
        
        serializer = self.get_serializer(collection)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_photo(self, request, collection_id=None):
        collection = self.get_object()
        photo_id = request.data.get('photo_id')
        if not photo_id:
            return Response(
                {'message': 'Photo ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            photo = Photo.objects.get(id=photo_id)
            collection.photos.add(photo)
            collection.update_photos_count()
            collection.update_cover_photo()
            return Response({'message': 'Photo added to collection successfully'})
        except Photo.DoesNotExist:
            return Response(
                {'message': 'Photo not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def remove_photo(self, request, collection_id=None):
        collection = self.get_object()
        photo_id = request.data.get('photo_id')
        if not photo_id:
            return Response(
                {'message': 'Photo ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            photo = Photo.objects.get(id=photo_id)
            collection.photos.remove(photo)
            collection.update_photos_count()
            collection.update_cover_photo()
            return Response({'message': 'Photo removed from collection successfully'})
        except Photo.DoesNotExist:
            return Response(
                {'message': 'Photo not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True)
    def photos(self, request, pk=None):
        tag = self.get_object()
        photos = tag.photos.all().select_related('user').prefetch_related('categories', 'tags')
        serializer = PhotoSerializer(photos, many=True)
        return Response(serializer.data)