from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from accounts.models import MyUser
from .models import ChatRoom, DirectMessage


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


@login_required
def send_message_view(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    if request.user not in room.users.all():
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse(
                {"error": "شما اجازه دسترسی به این مدار گفتگو را ندارید."}, status=403
            )
        messages.error(request, "شما اجازه دسترسی به این مدار گفتگو را ندارید.")
        return redirect("direct:inbox")

    if request.method == "POST":
        message_text = request.POST.get("text", "").strip()
        if message_text:
            msg = DirectMessage.objects.create(
                chatroom=room, sender=request.user, text=message_text
            )
            room.save()

            avatar_url = ""
            if hasattr(request.user, "profile") and request.user.profile.avatar:
                avatar_url = request.user.profile.avatar.url

            # ارسال به کانال وب‌سوکت برای مخاطبان آنلاین
            try:
                from asgiref.sync import async_to_sync
                from channels.layers import get_channel_layer

                channel_layer = get_channel_layer()
                if channel_layer:
                    async_to_sync(channel_layer.group_send)(
                        f"direct_{room.id}",
                        {
                            "type": "chat_message",
                            "message": message_text,
                            "username": request.user.username,
                            "user_id": request.user.id,
                            "avatar_url": avatar_url,
                            "time": msg.created_at.strftime("%H:%M"),
                        },
                    )
            except Exception:
                pass

            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {
                        "status": "ok",
                        "message": message_text,
                        "username": request.user.username,
                        "user_id": request.user.id,
                        "avatar_url": avatar_url,
                        "time": msg.created_at.strftime("%H:%M"),
                    }
                )

    return redirect("direct:chat_room", room_id=room.id)
