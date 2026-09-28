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


def post_comments_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # واکشی تمام کامنت‌ها همراه با نویسنده در ۱ کوئری
    all_comments = post.comments.select_related("author").all()

    context = {
        "post": post,
        "comments": all_comments,
    }
    return render(request, "interactions/post_comments.html", context)
