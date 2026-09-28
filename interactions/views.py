from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from posts.models import Post
from .models import Like, Comment


def toggle_like(request, post_id):
    if not request.user.is_authenticated:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"error": "لطفاً ابتدا وارد شوید."}, status=401)
        return redirect("accounts:login")

    post = get_object_or_404(Post, id=post_id)
    like_qs = Like.objects.filter(user=request.user, post=post)

    if like_qs.exists():
        like_qs.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, post=post)
        liked = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse(
            {
                "status": "ok",
                "liked": liked,
                "total_likes": post.likes.count(),
            }
        )

    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    return redirect("interactions:post_comments_detail", post_id=post.id)


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
        referer = request.META.get("HTTP_REFERER")
        if referer:
            return redirect(referer)
        return redirect("interactions:post_comments_detail", post_id=post.id)
    return redirect("interactions:post_comments_detail", post_id=post.id)


def delete_comment(request, comment_id):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    if request.user == comment.author or request.user == comment.post.author:
        comment.delete()
        messages.success(request, "سیگنال دیدگاه از مدار حذف شد.")
    else:
        messages.error(request, "شما اجازه حذف این دیدگاه را ندارید.")
    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    return redirect("interactions:post_comments_detail", post_id=post_id)


def post_comments_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("author__profile").prefetch_related("likes"),
        id=post_id,
    )
    all_comments = post.comments.select_related("author__profile").order_by(
        "created_at"
    )
    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(user=request.user).exists()

    context = {
        "post": post,
        "comments": all_comments,
        "is_liked": is_liked,
    }
    return render(request, "interactions/post_comments.html", context)
