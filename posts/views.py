from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from .models import Post


def show_post(request):
    # واکشی بهینه پست‌ها همراه با جوین نویسنده و شمارش لایک‌ها در ۱ کوئری
    posts = (
        Post.objects.select_related("author")
        .annotate(total_likes=Count("likes"))
        .prefetch_related("comments__author")
        .all()
    )

    context = {
        "posts": posts,
    }
    return render(request, "posts/index.html", context)
