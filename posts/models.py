from django.db import models
from django.conf import settings


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="posts", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="posts/")
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username} - Post #{self.id}"

    def recent_comments(self):
        return self.comments.select_related("author")[:3]
