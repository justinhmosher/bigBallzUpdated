import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bigBallz.settings')
django.setup()
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
import authentication.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                authentication.routing.websocket_urlpatterns
            )
        )
    ),
})
