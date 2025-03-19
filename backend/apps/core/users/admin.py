from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserFollow


class UserAdmin(BaseUserAdmin):
    """Manages both user authentication and profile fields in the admin panel."""
    
    list_display = (
        'username', 'email', 'full_name', 'role', 
        'is_active', 'is_staff', 'date_joined'
    )
    list_filter = ('is_active', 'is_staff', 'role')
    list_per_page = 25

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': (
                'email', 'full_name', 'bio', 'about',
                'profile_picture', 'phone', 'website', 'location'
            )
        }),
        (_('Role & Status'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'role'),
        }),
    )

    readonly_fields = (
        'last_login', 'date_joined',
    )

    search_fields = ('username', 'email', 'full_name', 'phone')
    ordering = ('-date_joined',)
    filter_horizontal = ()

    def get_readonly_fields(self, request, obj=None):
        if obj:  # editing an existing object
            return self.readonly_fields + ('username', 'email')
        return self.readonly_fields


class UserFollowAdmin(admin.ModelAdmin):
    """Admin interface for managing user following relationships."""
    
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    raw_id_fields = ('follower', 'following')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('follower', 'following')


# Register User with the structured UserAdmin
admin.site.register(User, UserAdmin)
admin.site.register(UserFollow, UserFollowAdmin)
