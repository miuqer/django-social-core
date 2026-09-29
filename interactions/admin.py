from django.contrib import admin
from .models import Like, Comment

# Register your models here.


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "post", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "post__id")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "parent", "short_text", "created_at")
    list_filter = ("created_at", "post", "parent")
    search_fields = ("author__username", "text")

    @admin.display(description="خلاصه دیدگاه")
    def short_text(self, obj):
        return obj.text[:20]
