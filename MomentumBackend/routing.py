from django.urls import re_path

from .consumers import SetConsumer

websocket_urlpatterns = [
    re_path("ws/socket", SetConsumer.as_asgi()),
]
