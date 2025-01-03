from . import views  # Import the weekly_NFL view
from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

app_name = "baseballSL"  # Namespace for this app

urlpatterns = [
    path('',views.home,name="home"),
    path('signout',views.signout,name="signout"),
    path('teamname',views.teamname,name = "teamname"),
    path('game/<int:league_num>',views.game,name="game"),
    path('checking/<int:league_num>',views.checking, name = 'checking'),
    path('location/<int:league_num>',views.location, name = 'location'),
    path('leaderboard/<int:league_num>',views.leaderboard, name = 'leaderboard'),
    path('playerboard/<int:league_num>',views.playerboard,name = 'playerboard'),
    path('payment/<int:league_num>',views.payment,name='payment'),
    path('rules',views.rules,name="rules"),
    path('submitverification/<int:league_num>',views.submitverification,name = 'submitverification'),
    path('picking/<int:league_num>', views.picking, name='picking'),
    path('leaders/<int:league_num>', views.player_list, name='leaders'),
    path('messages/<int:league_num>', views.message_board, name = 'messages'),
    path('update-pick', views.update_pick, name = 'update_pick'),
    path('search-players', views.search_players, name = 'search_players'),
    path('chat/<str:room_name>/<int:league_num>', views.room, name='room'),
    path('picking', views.picking, name='picking'),
]+static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
