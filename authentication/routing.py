from django.urls import re_path
from authentication.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>[-\w]+)/(?P<league_number>[-\w]+)/?$", ChatConsumer.as_asgi()),
]
