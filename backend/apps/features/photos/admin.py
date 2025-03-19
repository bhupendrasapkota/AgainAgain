from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    Photo, Category, Collection, PhotoLike, CollectionLike,
    PhotoComment, PhotoDownload, PhotoCategory, CollectionPhoto
)
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'photos_count', 'is_active', 'order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    readonly_fields = ('photos_count',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'is_active', 'order')
        }),
        ('Cover Photo', {
            'fields': ('cover_photo',),
            'classes': ('collapse',)
        }),
        ('Stats', {
            'fields': ('photos_count',),
            'classes': ('collapse',)
        })
    )

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = obj.name.lower().replace(' ', '-')
        super().save_model(request, obj, form, change)

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        'thumbnail', 'title', 'user', 'created_at', 'is_featured',
        'is_public', 'is_archived', 'likes_count', 'views_count',
        'download_count'
    )
    list_display_links = ('thumbnail', 'title')
    list_filter = (
        'is_featured', 'is_public', 'is_archived',
        'created_at', 'user', 'medium', 'year',
        'processing_status'
    )
    search_fields = ('title', 'description', 'user__username', 'location')
    readonly_fields = (
        'created_at', 'updated_at', 'likes_count', 'views_count',
        'download_count', 'width', 'height', 'format', 'file_size',
        'processing_status', 'processing_error', 'thumbnail_preview'
    )
    raw_id_fields = ('user',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_per_page = 25
    actions = ['make_featured', 'make_public', 'archive_photos']
    fieldsets = (
        (None, {
            'fields': ('title', 'user', 'image', 'thumbnail_preview', 'description', 'is_public', 'is_archived')
        }),
        ('Details', {
            'fields': (
                'width', 'height', 'format', 'file_size',
                'medium', 'year', 'location', 'latitude', 'longitude'
            )
        }),
        ('Processing', {
            'fields': ('processing_status', 'processing_error'),
            'classes': ('collapse',)
        }),
        ('Stats', {
            'fields': ('is_featured', 'likes_count', 'views_count', 'download_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'featured_at', 'last_viewed_at'),
            'classes': ('collapse',)
        })
    )

    def thumbnail(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "-"
    thumbnail.short_description = _("Thumbnail")

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="200" height="200" style="object-fit: contain;" />', obj.image.url)
        return "-"
    thumbnail_preview.short_description = _("Preview")

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)
    make_featured.short_description = _("Mark selected photos as featured")

    def make_public(self, request, queryset):
        queryset.update(is_public=True)
    make_public.short_description = _("Mark selected photos as public")

    def archive_photos(self, request, queryset):
        queryset.update(is_archived=True)
    archive_photos.short_description = _("Archive selected photos")

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'user', 'created_at', 'is_private', 'is_featured',
        'artwork_count', 'views_count', 'likes_count'
    )
    list_filter = (
        'is_private', 'is_featured', 'created_at', 'user'
    )
    search_fields = ('name', 'description', 'user__username', 'location')
    readonly_fields = (
        'created_at', 'updated_at', 'artwork_count',
        'views_count', 'likes_count', 'slug'
    )
    raw_id_fields = ('user', 'cover_photo')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('name', 'user', 'description', 'is_private', 'is_featured')
        }),
        ('Content', {
            'fields': ('cover_photo',)
        }),
        ('Stats', {
            'fields': ('artwork_count', 'views_count', 'likes_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'featured_at', 'last_viewed_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(PhotoComment)
class PhotoCommentAdmin(admin.ModelAdmin):
    list_display = ('photo', 'user', 'text', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at', 'user')
    search_fields = ('photo__title', 'user__username', 'text')
    raw_id_fields = ('user', 'photo', 'parent')
    readonly_fields = ('created_at', 'edited_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(PhotoDownload)
class PhotoDownloadAdmin(admin.ModelAdmin):
    list_display = ('photo', 'user', 'download_type', 'created_at')
    list_filter = ('download_type', 'created_at', 'user')
    search_fields = ('photo__title', 'user__username')
    raw_id_fields = ('user', 'photo')
    readonly_fields = ('created_at', 'ip_address', 'user_agent', 'referrer')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(PhotoLike)
class PhotoLikeAdmin(admin.ModelAdmin):
    list_display = ('photo', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('photo__title', 'user__username')
    raw_id_fields = ('user', 'photo')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(CollectionLike)
class CollectionLikeAdmin(admin.ModelAdmin):
    list_display = ('collection', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('collection__name', 'user__username')
    raw_id_fields = ('user', 'collection')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

@admin.register(PhotoCategory)
class PhotoCategoryAdmin(admin.ModelAdmin):
    list_display = ('photo', 'category', 'added_at')
    list_filter = ('added_at', 'category')
    search_fields = ('photo__title', 'category__name')
    raw_id_fields = ('photo', 'category')
    readonly_fields = ('added_at',)
    date_hierarchy = 'added_at'
    ordering = ('-added_at',)

@admin.register(CollectionPhoto)
class CollectionPhotoAdmin(admin.ModelAdmin):
    list_display = ('collection', 'photo', 'order', 'added_at')
    list_filter = ('added_at', 'collection')
    search_fields = ('collection__name', 'photo__title')
    raw_id_fields = ('collection', 'photo')
    readonly_fields = ('added_at',)
    date_hierarchy = 'added_at'
    ordering = ('collection', 'order')
