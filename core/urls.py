from django.contrib import admin
from django.urls import path, include

from .views import check_authentication


urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("user.urls")),
    path("test-auth/", check_authentication),
]
