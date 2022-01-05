0"""
ASGI config for BPBackendDjango project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path

from BPBackendDjango.BPBackendDjango.WebSocket.Consumer import MyConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BPBackendDjango.settings')

application = ProtocolTypeRouter({


    "websocket": AuthMiddlewareStack(
        URLRouter([
            # URLRouter just takes standard Django path() or url() entries.
            path("api/socket", MyConsumer),
        ]),
    ),

})