# mysite/asgi.py
import os

from api.token_auth import TokenAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import api.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mnky_chat.settings")

application = ProtocolTypeRouter({
  "http": get_asgi_application(),
  "websocket": TokenAuthMiddlewareStack(
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    ),
})