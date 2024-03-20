from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home,name="home"),
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
    path('search',views.search,name='search'),
    path('forgotPassEmail',views.forgotPassEmail,name='forgotPassEmail'),
    path('passreset/<uidb64>/<token>',views.passreset,name='passreset'),
    path('teamcount',views.teamcount,name='teamcount'),
    path('tournaments',views.tournaments,name='tournaments'),
    path('payment',views.payment,name='payment'),
    path('webhooks/coinbase/', views.coinbase_webhook, name='coinbase_webhook'),
]+static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
