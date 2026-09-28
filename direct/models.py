from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL, verbose_name=("کاربران"), related_name="conversations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"اتاق مداری #{self.id}"


class DirectMessage(models.Model):
    chatroom = models.ForeignKey(
        "ChatRoom",
        verbose_name=("اتاق مکالمه"),
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=("فرستنده"),
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    text = models.TextField()
    has_seen = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.text[:20]}"

    class Meta:
        ordering = ["created_at"]
