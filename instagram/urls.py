from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("posts.urls")),  # مسیر فید اصلی
    path("accounts/", include("accounts.urls")),  # 👈 این خط را اضافه کنید
    path("interactions/", include("interactions.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
