from django.urls import path
from .views import create_post, show_post

app_name = "posts"

urlpatterns = [
    path("", show_post, name="feed"),
    path("create/", create_post, name="create_post"),
]
