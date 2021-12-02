# mysite/asgi.py
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mnky_chat.settings")
agsi_routes = get_asgi_application()

from api.token_auth import TokenAuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import api.routing



application = ProtocolTypeRouter({
#   "http": agsi_routes,
  "websocket": TokenAuthMiddlewareStack(
        URLRouter(
            api.routing.websocket_urlpatterns
        )
    ),
})