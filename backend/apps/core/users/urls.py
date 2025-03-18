from django.urls import path
from .views import ProfileView

app_name = "users"

urlpatterns = [
    path("profile/", ProfileView.as_view(), name="profile"),
]
