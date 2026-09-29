from django.urls import path
from .views import (
    login_view,
    logout_view,
    password_reset_confirm_view,
    password_reset_request_view,
    profile_view,
    register_view,
    toggle_follow,
    user_profile_view,
)

app_name = "accounts"

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
    path("follow/<int:user_id>/", toggle_follow, name="toggle_follow"),
    path(
        "password-reset/",
        password_reset_request_view,
        name="password_reset_request",
    ),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        password_reset_confirm_view,
        name="password_reset_confirm",
    ),
    path("user/<str:username>/", user_profile_view, name="user_profile"),
    path("<str:username>/", user_profile_view, name="user_profile_short"),
]
