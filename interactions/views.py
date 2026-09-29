from django.contrib import messages
from django.db import models
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
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    if not request.user.is_authenticated:
        if is_ajax:
            return JsonResponse(
                {"error": "لطفاً ابتدا وارد حساب کاربری خود شوید."}, status=401
            )
        return redirect("accounts:login")

    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        text_input = request.POST.get("text", "").strip()
        parent_id = request.POST.get("parent_id")

        if not text_input:
            if is_ajax:
                return JsonResponse(
                    {"error": "متن مخابره نمی‌تواند خالی باشد."}, status=400
                )
            messages.error(request, "متن مخابره نمی‌تواند خالی باشد.")
            return redirect("interactions:post_comments_detail", post_id=post.id)

        parent_comment = None
        if parent_id:
            try:
                parent_comment = Comment.objects.get(id=parent_id, post=post)
                # در صورت پاسخ به یک ریپلای، سطح پاسخ به ریشه متصل بماند (مانند اینستاگرام)
                if parent_comment.parent is not None:
                    parent_comment = parent_comment.parent
            except (Comment.DoesNotExist, ValueError):
                parent_comment = None

        new_comment = Comment.objects.create(
            author=request.user,
            post=post,
            text=text_input,
            parent=parent_comment,
        )

        if is_ajax:
            avatar_url = (
                request.user.profile.avatar.url
                if hasattr(request.user, "profile") and request.user.profile.avatar
                else None
            )
            return JsonResponse(
                {
                    "status": "ok",
                    "message": (
                        "سیگنال پاسخ شما در مدار ثبت شد."
                        if parent_comment
                        else "دیدگاه شما در مدار ثبت شد."
                    ),
                    "comment": {
                        "id": new_comment.id,
                        "author": new_comment.author.username,
                        "author_full_name": (
                            getattr(new_comment.author.profile, "full_name", "")
                            if hasattr(new_comment.author, "profile")
                            else ""
                        ),
                        "author_avatar": avatar_url,
                        "text": new_comment.text,
                        "created_at": new_comment.created_at.strftime(
                            "%Y-%m-%d // %H:%M"
                        ),
                        "is_op": new_comment.author == post.author,
                        "is_owner": True,
                        "is_reply": new_comment.parent is not None,
                        "parent_id": new_comment.parent_id,
                        "delete_url": f"/interactions/comment/{new_comment.id}/delete/",
                        "user_profile_url": f"/accounts/user/{new_comment.author.username}/",
                    },
                    "total_comments_count": post.comments.count(),
                }
            )

        if parent_comment:
            messages.success(
                request,
                f"پاسخ شما به @{parent_comment.author.username} در مدار ثبت شد.",
            )
        else:
            messages.success(request, "سیگنال دیدگاه شما در مدار ثبت شد.")

        referer = request.META.get("HTTP_REFERER")
        if referer:
            return redirect(referer)
        return redirect("interactions:post_comments_detail", post_id=post.id)
    return redirect("interactions:post_comments_detail", post_id=post.id)


def delete_comment(request, comment_id):
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"
    if not request.user.is_authenticated:
        if is_ajax:
            return JsonResponse({"error": "لطفاً ابتدا وارد شوید."}, status=401)
        return redirect("accounts:login")

    comment = get_object_or_404(Comment, id=comment_id)
    post = comment.post
    if request.user == comment.author or request.user == post.author:
        was_reply = comment.parent is not None
        parent_id = comment.parent_id
        comment.delete()
        if is_ajax:
            return JsonResponse(
                {
                    "status": "ok",
                    "message": "سیگنال دیدگاه از مدار حذف شد.",
                    "deleted_id": comment_id,
                    "was_reply": was_reply,
                    "parent_id": parent_id,
                    "total_comments_count": post.comments.count(),
                }
            )
        messages.success(request, "سیگنال دیدگاه از مدار حذف شد.")
    else:
        if is_ajax:
            return JsonResponse(
                {"error": "شما اجازه حذف این دیدگاه را ندارید."}, status=403
            )
        messages.error(request, "شما اجازه حذف این دیدگاه را ندارید.")

    referer = request.META.get("HTTP_REFERER")
    if referer:
        return redirect(referer)
    return redirect("interactions:post_comments_detail", post_id=post.id)


def post_comments_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related("author__profile").prefetch_related("likes"),
        id=post_id,
    )
    # واکشی بهینه دیدگاه‌های ریشه همراه با پاسخ‌ها با استفاده از Prefetch جهت جلوگیری از N+1
    root_comments = (
        post.comments.filter(parent__isnull=True)
        .select_related("author__profile")
        .prefetch_related(
            models.Prefetch(
                "replies",
                queryset=Comment.objects.select_related("author__profile").order_by(
                    "created_at"
                ),
            )
        )
        .order_by("created_at")
    )
    is_liked = False
    if request.user.is_authenticated:
        is_liked = post.likes.filter(user=request.user).exists()

    context = {
        "post": post,
        "comments": root_comments,
        "total_comments_count": post.comments.count(),
        "is_liked": is_liked,
    }
    return render(request, "interactions/post_comments.html", context)
