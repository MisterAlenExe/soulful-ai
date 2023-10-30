from django.contrib import admin
from django.urls import path, include

from .views import IndexPageView, ProfilePageView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexPageView.as_view(), name="index"),
    path("profile/", ProfilePageView.as_view(), name="profile"),
    path("auth/", include("user.urls"), name="auth"),
]
