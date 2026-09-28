import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import ChatRoom, DirectMessage


class DirectConsumer(WebsocketConsumer):
    def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"direct_{self.room_id}"

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return
        data = json.loads(text_data)
        message_text = data.get("message", "").strip()
        user = self.scope.get("user")

        if message_text and user and user.is_authenticated:
            room = ChatRoom.objects.get(id=self.room_id)
            msg = DirectMessage.objects.create(
                chatroom=room, sender=user, text=message_text
            )
            room.save()

            avatar_url = ""
            if hasattr(user, "profile") and user.profile.avatar:
                avatar_url = user.profile.avatar.url

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message_text,
                    "username": user.username,
                    "user_id": user.id,
                    "avatar_url": avatar_url,
                    "time": msg.created_at.strftime("%H:%M"),
                },
            )

    def chat_message(self, event):
        self.send(
            text_data=json.dumps(
                {
                    "message": event["message"],
                    "username": event["username"],
                    "user_id": event.get("user_id"),
                    "avatar_url": event.get("avatar_url", ""),
                    "time": event.get("time", ""),
                }
            )
        )
