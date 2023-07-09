"""
ASGI config for Shipping_Django project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""
import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack

# remove 'Shipping_Django.' before launch in ubuntu
import Shipping_Django.Shipping_app.ws_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Shipping_Django.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket':
        URLRouter(
            # remove 'Shipping_Django.' before launch in ubuntu
            Shipping_Django.Shipping_app.ws_routing.websocket_urlpatterns)

})