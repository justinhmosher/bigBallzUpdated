from . import weekly_NFL  # Import the weekly_NFL view
from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

app_name = "football"  # Namespace for this app

urlpatterns = [
    path('',weekly_NFL.home,name="home"),
    path('signout',weekly_NFL.signout,name="signout"),
    path('teamname',weekly_NFL.teamname,name = "teamname"),
    path('game/<int:league_num>',weekly_NFL.game,name="game"),
    path('checking/<int:league_num>',weekly_NFL.checking, name = 'checking'),
    path('location/<int:league_num>',weekly_NFL.location, name = 'location'),
    path('leaderboard/<int:league_num>',weekly_NFL.leaderboard, name = 'leaderboard'),
    path('playerboard/<int:league_num>',weekly_NFL.playerboard,name = 'playerboard'),
    path('payment/<int:league_num>',weekly_NFL.payment,name='payment'),
    path('rules',weekly_NFL.rules,name="rules"),
    path('submitverification/<int:league_num>',weekly_NFL.submitverification,name = 'submitverification'),
    path('picking/<int:league_num>', weekly_NFL.picking, name='picking'),
    path('leaders/<int:league_num>', weekly_NFL.player_list, name='leaders'),
    path('messages/<int:league_num>', weekly_NFL.message_board, name = 'messages'),
    path('update-pick', weekly_NFL.update_pick, name = 'update_pick'),
    path('search-players', weekly_NFL.search_players, name = 'search_players'),
    path('chat/<str:room_name>/<int:league_num>', weekly_NFL.room, name='room'),
    path('picking', weekly_NFL.picking, name='picking'),
]+static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)

