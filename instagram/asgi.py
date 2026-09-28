import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "instagram.settings")

# مقداردهی اولیه به جنگو قبل از لود روت‌های سوکت
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        # درخواست‌های معمولی وب
        "http": django_asgi_app,
        # درخواست‌های وب‌سوکت دایرکت
        "websocket": AuthMiddlewareStack(
            URLRouter(
                # روت‌های سوکت را در ایستگاه بعدی اینجا وصل می‌کنیم
                []
            )
        ),
    }
)
