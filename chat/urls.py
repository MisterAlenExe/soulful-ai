from django.urls import path

from .views import ChatPageView


urlpatterns = [
    path("", ChatPageView.as_view(), name="chat"),
]
