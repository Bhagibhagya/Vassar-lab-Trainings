# """
# ASGI config for ConnectedCustomerPlatform project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
# """

import os
import django

django.setup()

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

# Import websocket URL patterns from both apps
from ChatBot.routing import websocket_urlpatterns as chatbot_websocket_urlpatterns
from EmailApp.routing import websocket_urlpatterns as emailapp_websocket_urlpatterns

# Combine the websocket URL patterns from both apps
combined_websocket_urlpatterns = chatbot_websocket_urlpatterns + emailapp_websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    combined_websocket_urlpatterns
                )
            )
        ),
    }
)
