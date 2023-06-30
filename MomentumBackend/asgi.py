import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import re_path

from MomentumBackend.consumers import SetConsumer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MomentumBackend.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(URLRouter([
            re_path("ws(/socket)?", SetConsumer.as_asgi()),
        ])),
    }
)
