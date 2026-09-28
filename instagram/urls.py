from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),  # مسیر فید مداری
    path("accounts/", include("accounts.urls")),  # سیستم کاربری
    path("interactions/", include("interactions.urls")),  # لایک و کامنت
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
