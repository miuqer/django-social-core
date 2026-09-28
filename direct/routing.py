from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # الگوی دریافت شناسه عددی اتاق بدون اسلش اولیه
    re_path(
        r'^ws/direct/(?P<room_id>\d+)/$', consumers.DirectConsumer.as_asgi()
    ),
]