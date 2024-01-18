from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    #path('signup',RedirectView.as_view(pattern_name='signup', permanent=True)),
    path('signup',views.signup,name="signup"),
    path('signin',views.signin,name="signin"),
    path('signout',views.signout,name="signout"),
    path('teamname',views.teamname,name = "teamname"),
    path('activate/<uidb64>/<token>',views.activate,name='activate'),
    path('signsamp',views.signsamp,name="signsamp"),
    path('game',views.game,name="game"),
    path('checking',views.checking, name = 'checking'),
    path('leaderboard',views.leaderboard, name = 'leaderboard'),
    path('playerboard',views.playerboard,name = 'playerboard'),
    path('search',views.search,name='search')
]
