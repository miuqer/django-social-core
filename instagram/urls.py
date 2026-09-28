from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),  # مسیر فید
    path("accounts/", include("accounts.urls")),  # فقط اپ اکانتس
    path("interactions/", include("interactions.urls")),  # فقط اپ تعاملات
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
