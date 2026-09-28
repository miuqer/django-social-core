from django.db.models import Count
from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from django.contrib import messages


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


def create_post(request):
    if not request.user.is_authenticated:
        messages.error(request, "برای مخابره داده به مدار، ابتدا وارد شوید.")
        return redirect("accounts:login")

    if request.method == "POST":
        image_file = request.FILES.get("image")
        caption_input = request.POST.get("caption", "").strip()

        if not image_file:
            messages.error(request, "انتخاب داده تصویری برای مخابره الزامی است.")
            return render(request, "posts/create_post.html")

        Post.objects.create(
            author=request.user, image=image_file, caption=caption_input
        )
        messages.success(request, "سیگنال و داده مداری با موفقیت مخابره شد! 🛰️")
        return redirect("posts:feed")

    return render(request, "posts/create_post.html")
