from rest_framework import permissions
from django.core.exceptions import PermissionDenied

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    
    This permission ensures that:
    - Read operations (GET, HEAD, OPTIONS) are allowed for all users
    - Write operations (POST, PUT, PATCH, DELETE) are only allowed for the object owner
    - Unauthorized write attempts raise PermissionDenied
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object.
        if obj.user != request.user:
            raise PermissionDenied("You don't have permission to modify this object.")
        return True

class IsCollectionOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a collection to edit it.
    
    This permission ensures that:
    - Read operations are allowed for all users
    - Write operations are only allowed for the collection owner
    - Private collections are only visible to their owner
    - Unauthorized write attempts raise PermissionDenied
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            # For private collections, only allow access to owner
            if obj.is_private and obj.user != request.user:
                raise PermissionDenied("This collection is private.")
            return True

        # Write permissions are only allowed to the owner of the collection.
        if obj.user != request.user:
            raise PermissionDenied("You don't have permission to modify this collection.")
        return True

class IsPrivateContentOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners to view private content.
    
    This permission ensures that:
    - Private content is only accessible to its owner
    - Public content is accessible to all users
    - Unauthorized access attempts raise PermissionDenied
    """
    def has_object_permission(self, request, view, obj):
        if not obj.is_private:
            return True
            
        if obj.user != request.user:
            raise PermissionDenied("This content is private.")
        return True 