from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    User management application configuration.
    
    Handles user-related functionality including profiles, authentication,
    and user-specific features.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core.users'
