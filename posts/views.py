from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Post, Story, StoryView


def show_post(request):
    # واکشی بهینه پست‌ها همراه با جوین نویسنده و شمارش لایک‌ها در ۱ کوئری
    posts = (
        Post.objects.select_related("author__profile")
        .annotate(total_likes=Count("likes"))
        .prefetch_related("comments__author__profile")
        .order_by("-created_at")
        .all()
    )

    # دریافت استوری‌های فعال ۲۴ ساعت گذشته
    cutoff = timezone.now() - timedelta(hours=24)
    active_stories = (
        Story.objects.filter(created_at__gte=cutoff)
        .select_related("user__profile")
        .prefetch_related("views")
        .order_by("-created_at")
    )

    # گروه‌بندی استوری‌ها بر پایه کاربر برای نوار استوری‌های فید
    user_stories_map = {}
    for s in active_stories:
        u = s.user
        if u.id not in user_stories_map:
            user_stories_map[u.id] = {
                "user": u,
                "latest_story": s,
                "first_story_id": s.id,
                "stories_count": 0,
                "has_unseen": False,
            }
        user_stories_map[u.id]["stories_count"] += 1
        is_seen = (
            any(v.viewer_id == request.user.id for v in s.views.all())
            if request.user.is_authenticated
            else False
        )
        if not is_seen:
            user_stories_map[u.id]["has_unseen"] = True

    story_items = list(user_stories_map.values())
    user_has_story = False
    user_first_story_id = None
    if request.user.is_authenticated:
        if request.user.id in user_stories_map:
            user_has_story = True
            user_first_story_id = user_stories_map[request.user.id]["first_story_id"]
        # استوری‌های دیده‌نشده در ابتدای لیست قرار گیرند
        story_items.sort(
            key=lambda x: (
                x["user"].id == request.user.id,
                x["has_unseen"],
            ),
            reverse=True,
        )

    context = {
        "posts": posts,
        "story_items": story_items,
        "user_has_story": user_has_story,
        "user_first_story_id": user_first_story_id,
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


@login_required
def create_story(request):
    if request.method == "POST":
        image_file = request.FILES.get("image")
        caption_input = request.POST.get("caption", "").strip()

        if not image_file:
            messages.error(request, "انتخاب داده تصویری برای استوری الزامی است.")
            return render(request, "posts/create_story.html")

        story = Story.objects.create(
            user=request.user, image=image_file, caption=caption_input
        )
        messages.success(request, "استوری با موفقیت به مدار ارسال شد! 🌟")
        return redirect("posts:show_story", story_id=story.id)

    return render(request, "posts/create_story.html")


def show_story(request, story_id):
    story = get_object_or_404(
        Story.objects.select_related("user__profile").prefetch_related(
            "views__viewer__profile"
        ),
        id=story_id,
    )

    if not story.is_active:
        messages.error(request, "این استوری منقضی شده است و دیگر قابل مشاهده نیست.")
        return redirect("posts:feed")

    if request.user.is_authenticated and request.user != story.user:
        # ثبت بازدید استوری فقط اگر کاربر وارد شده باشد و خودش صاحب استوری نباشد
        StoryView.objects.get_or_create(story=story, viewer=request.user)

    cutoff = timezone.now() - timedelta(hours=24)
    user_stories = list(
        Story.objects.filter(user=story.user, created_at__gte=cutoff).order_by(
            "created_at"
        )
    )
    current_index = 0
    for idx, s in enumerate(user_stories):
        if s.id == story.id:
            current_index = idx
            break

    prev_story = user_stories[current_index - 1] if current_index > 0 else None
    next_story = (
        user_stories[current_index + 1]
        if current_index < len(user_stories) - 1
        else None
    )

    story_views = (
        story.views.select_related("viewer__profile").all()
        if request.user == story.user
        else []
    )

    context = {
        "story": story,
        "user_stories": user_stories,
        "current_index": current_index,
        "total_user_stories": len(user_stories),
        "prev_story": prev_story,
        "next_story": next_story,
        "story_views": story_views,
    }
    return render(request, "posts/show_story.html", context)
