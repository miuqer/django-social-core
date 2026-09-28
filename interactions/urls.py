from django.urls import path
from .views import add_comment, post_comments_detail, toggle_like

app_name = "interactions"

urlpatterns = [
    path("like/<int:post_id>/", toggle_like, name="toggle_like"),
    path("comment/<int:post_id>/add/", add_comment, name="add_comment"),
    path(
        "post/<int:post_id>/comments/",
        post_comments_detail,
        name="post_comments_detail",
    ),
]
