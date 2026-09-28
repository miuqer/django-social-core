from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import MyUser
from .models import ChatRoom


@login_required
def direct_inbox_view(request):
    user_rooms = request.user.conversations.prefetch_related(
        "users__profile", "messages"
    ).order_by("-updated_at")
    first_room = user_rooms.first()
    if first_room:
        return redirect("direct:chat_room", room_id=first_room.id)

    return render(
        request,
        "direct/chat_room.html",
        {
            "room": None,
            "messages": [],
            "user_rooms": user_rooms,
            "other_user": None,
        },
    )


@login_required
def chat_room_view(request, room_id):
    # ۱. واکشی اتاق یا بازگرداندن ۴۰۴
    room = get_object_or_404(ChatRoom, id=room_id)

    # ۲. بررسی دسترسی امنیتی
    if request.user not in room.users.all():
        messages.error(request, "شما اجازه دسترسی به این مدار گفتگو را ندارید.")
        return render(request, "direct/oh_no.html", status=403)

    # ۳. دریافت پیام‌ها با نام متغیر تفکیک‌شده و علامت‌گذاری پیام‌های خوانده شده
    chat_messages = room.messages.select_related("sender__profile").all()
    room.messages.exclude(sender=request.user).filter(has_seen=False).update(
        has_seen=True
    )

    # ۴. لیست سایر مکالمات کاربر جهت نمایش در سایدبار چت
    user_rooms = request.user.conversations.prefetch_related(
        "users__profile", "messages"
    ).order_by("-updated_at")
    other_user = room.users.exclude(id=request.user.id).first()

    # ۵. ارسال به قالب
    return render(
        request,
        "direct/chat_room.html",
        {
            "room": room,
            "messages": chat_messages,
            "user_rooms": user_rooms,
            "other_user": other_user,
        },
    )


@login_required
def start_or_get_chat_view(request, user_id):
    target_user = get_object_or_404(MyUser, id=user_id)
    if target_user == request.user:
        messages.error(request, "امکان برقراری ارتباط مداری با خودتان وجود ندارد.")
        return redirect("posts:feed")

    # واکشی اتاق مشترک یا ساخت اتاق جدید
    existing_room = (
        ChatRoom.objects.filter(users=request.user).filter(users=target_user).first()
    )
    if not existing_room:
        existing_room = ChatRoom.objects.create()
        existing_room.users.add(request.user, target_user)

    return redirect("direct:chat_room", room_id=existing_room.id)
