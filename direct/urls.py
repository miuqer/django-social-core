from django.urls import path
from . import views

app_name = "direct"

urlpatterns = [
    path("", views.direct_inbox_view, name="inbox"),
    path("room/<int:room_id>/", views.chat_room_view, name="chat_room"),
    path("room/<int:room_id>/send/", views.send_message_view, name="send_message"),
    path("start/<int:user_id>/", views.start_or_get_chat_view, name="start_chat"),
]
