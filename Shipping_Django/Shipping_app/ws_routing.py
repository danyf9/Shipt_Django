from django.urls import path
from . import ws_consumers

""" here we define a routing between the asgi requests to consumers """

websocket_urlpatterns = [
    path("ws", ws_consumers.MyConsumer.as_asgi()),
]