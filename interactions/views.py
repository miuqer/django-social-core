from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from posts.models import Post
from .models import Like, Comment


def toggle_like(request, post_id):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    post = get_object_or_404(Post, id=post_id)
    like_qs = Like.objects.filter(user=request.user, post=post)

    if like_qs.exists():
        like_qs.delete()
    else:
        Like.objects.create(user=request.user, post=post)

    # بازگشت عمومی به همان صفحه در هر دو وضعیت (لایک یا آن‌لایک)
    return redirect(request.META.get("HTTP_REFERER", "posts:feed"))


def add_comment(request, post_id):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        text_input = request.POST.get("text", "").strip()
        if text_input:
            Comment.objects.create(
                author=request.user,
                post=post,
                text=text_input,
            )
            messages.success(request, "سیگنال دیدگاه شما در مدار ثبت شد.")
        else:
            messages.error(request, "متن مخابره نمی‌تواند خالی باشد.")
        return redirect(request.META.get("HTTP_REFERER", "posts:feed"))


def post_comments_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    all_comments = post.comments.select_related("author").all()

    context = {
        "post": post,
        "comments": all_comments,
    }
    return render(request, "interactions/post_comments.html", context)
