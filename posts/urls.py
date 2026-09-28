from django.urls import path
from .views import show_post

app_name = "posts"

urlpatterns = [
    path("", show_post, name="feed"),
]
