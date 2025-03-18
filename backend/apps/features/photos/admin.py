from django.contrib import admin
from .models import Photo, Category, Collection, Tag, PhotoLike, CollectionLike

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'photos_count')
    search_fields = ('name', 'slug')
    readonly_fields = ('photos_count',)
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Stats', {
            'fields': ('photos_count',),
            'classes': ('collapse',)
        })
    )

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'photos_count')
    search_fields = ('name', 'slug')
    readonly_fields = ('photos_count',)
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description')
        }),
        ('Stats', {
            'fields': ('photos_count',),
            'classes': ('collapse',)
        })
    )

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'is_featured', 'likes_count', 'views_count')
    list_filter = ('is_featured', 'created_at', 'user')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'likes_count', 'views_count')
    filter_horizontal = ('categories', 'tags')
    raw_id_fields = ('user',)
    fieldsets = (
        (None, {
            'fields': ('title', 'user', 'image', 'description')
        }),
        ('Details', {
            'fields': ('width', 'height', 'format', 'categories', 'tags')
        }),
        ('Metadata', {
            'fields': ('location', 'camera_info', 'medium', 'year', 'artist')
        }),
        ('Stats', {
            'fields': ('is_featured', 'likes_count', 'views_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at', 'is_private', 'artwork_count', 'views_count', 'likes_count')
    list_filter = ('is_private', 'created_at', 'user')
    search_fields = ('name', 'description', 'user__username')
    readonly_fields = ('created_at', 'updated_at', 'artwork_count', 'views_count', 'likes_count')
    filter_horizontal = ('photos',)
    raw_id_fields = ('user', 'curator', 'cover_photo')
    fieldsets = (
        (None, {
            'fields': ('name', 'user', 'description', 'is_private')
        }),
        ('Content', {
            'fields': ('cover_photo', 'photos')
        }),
        ('Details', {
            'fields': ('exhibition_date', 'location', 'curator')
        }),
        ('Stats', {
            'fields': ('artwork_count', 'views_count', 'likes_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(PhotoLike)
class PhotoLikeAdmin(admin.ModelAdmin):
    list_display = ('photo', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('photo__title', 'user__username')
    raw_id_fields = ('user', 'photo')
    readonly_fields = ('created_at',)

@admin.register(CollectionLike)
class CollectionLikeAdmin(admin.ModelAdmin):
    list_display = ('collection', 'user', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('collection__name', 'user__username')
    raw_id_fields = ('user', 'collection')
    readonly_fields = ('created_at',)
