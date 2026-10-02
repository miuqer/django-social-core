from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone


def upload_path(instance, filename):
    # تشخیص نام کلاس (مثلاً 'post' یا 'story')
    class_name = instance.__class__.__name__.lower()
    # بررسی هوشمند فیلد کاربر (چه user باشد چه author)
    user = getattr(instance, "user", None) or getattr(instance, "author", None)
    username = user.username if user else "anonymous"
    return f"{class_name}/{username}/{filename}"


class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="posts", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=upload_path)
    caption = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author.username} - Post #{self.id}"

    def recent_comments(self):
        return self.comments.select_related("author")[:3]


class Story(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="stories", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to=upload_path)
    caption = models.CharField(blank=True, max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def is_active(self):
        return timezone.now() - self.created_at < timedelta(hours=24)

    def __str__(self):
        return f"{self.user.username} - Story #{self.id}"


class StoryView(models.Model):
    story = models.ForeignKey(
        Story,
        verbose_name="استوری",
        on_delete=models.CASCADE,
        related_name="views",
    )
    viewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="بیننده",
        on_delete=models.CASCADE,
        related_name="viewed_stories",
    )
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("story", "viewer")
        ordering = ["-viewed_at"]

    def __str__(self):
        return f"{self.viewer.username} viewed Story #{self.story.id}"
