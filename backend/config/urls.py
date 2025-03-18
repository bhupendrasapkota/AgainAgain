from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf.urls import handler404

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/users/", include("apps.core.users.urls", namespace="users")),  
    path("api/auth/", include("apps.core.authentication.urls", namespace="authentication")),  
    path("api/", include("apps.features.photos.urls", namespace="photos")),
]

def custom_404(request, exception=None):
    return JsonResponse({"detail": "The requested endpoint was not found."}, status=404)

handler404 = custom_404