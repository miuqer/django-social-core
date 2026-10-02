from django.urls import path
from .views import create_post, create_story, show_post, show_story

app_name = "posts"

urlpatterns = [
    path("", show_post, name="feed"),
    path("create/", create_post, name="create_post"),
    path("story/create/", create_story, name="create_story"),
    path("story/<int:story_id>/", show_story, name="show_story"),
]
