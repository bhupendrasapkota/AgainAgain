from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    """Manages both user authentication and profile fields in the admin panel."""
    
    list_display = ('username', 'email', 'full_name', 'followers_count','following_count', 'is_admin', 'is_staff', 'is_active')
    list_filter = ('is_admin', 'is_staff', 'is_active')

    fieldsets = (
        ('Authentication', {'fields': ('email', 'username', 'password')}),
        ('Profile Info', {'fields': ('full_name', 'bio', 'profile_picture', 'about', 'contact', 'followers_count', 'following_count')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_staff', 'is_superuser')}),
        ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2')},
        ),
    )

    readonly_fields = ('last_login', 'created_at', 'updated_at', 'followers_count', 'following_count')

    search_fields = ('email', 'username', 'full_name')
    ordering = ('email',)
    filter_horizontal = ()

# Register User with the structured UserAdmin
admin.site.register(User, UserAdmin)
