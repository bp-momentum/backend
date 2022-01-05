from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path('ws/socket', consumers.ChatConsumer.as_asgi()),
]
