import uuid

from django.db import models

from user.models import User


class ChatRoom(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=100, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    uuid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_ai = models.BooleanField(default=False)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.email} - {self.content}"
