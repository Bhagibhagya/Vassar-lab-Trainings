# myapp/routing.py

from django.urls import path
from .consumers import TextConsumer

websocket_urlpatterns = [
    path(r"ws/text/", TextConsumer.as_asgi()),
]
