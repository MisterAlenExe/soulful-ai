from django.contrib import admin
from django.urls import path

from core.views import ChatView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("chat/", ChatView.as_view()),
]
