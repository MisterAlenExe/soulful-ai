from django.contrib import admin
from django.urls import path, include

from .views import IndexPageView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", IndexPageView.as_view(), name="index"),
    path("auth/", include("user.urls"), name="auth"),
    path("chat/", include("chat.urls"), name="chat"),
]
