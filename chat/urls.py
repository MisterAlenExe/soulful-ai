from django.urls import path

from .views import ChatPageView, NewChatPageView


urlpatterns = [
    path("", ChatPageView.as_view(), name="chat"),
    path("<uuid:uuid>/", ChatPageView.as_view(), name="chat_by_uuid"),
    path("new/", NewChatPageView.as_view(), name="new_chat"),
]
