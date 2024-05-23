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
    path('location',views.location, name = 'location'),
    path('leaderboard',views.leaderboard, name = 'leaderboard'),
    path('playerboard',views.playerboard,name = 'playerboard'),
    path('search',views.search,name='search'),
    path('forgotPassEmail',views.forgotPassEmail,name='forgotPassEmail'),
    path('passreset/<uidb64>/<token>',views.passreset,name='passreset'),
    path('teamcount',views.teamcount,name='teamcount'),
    path('tournaments',views.tournaments,name='tournaments'),
    path('payment',views.payment,name='payment'),
    path('terms',views.terms,name='terms'),
    path('privacy',views.privacy,name='privacy'),
    path('confirm-email/<str:email>/',views.confirm_email,name='confirm_email'),
    path('confirm-forgot-email/<str:email>/',views.confirm_forgot_email,name='confirm_forgot_email'),
    path('webhooks/coinbase/', views.coinbase_webhook, name='coinbase_webhook'),
    path('testing',views.testing,name='testing'),
    path('rules',views.rules,name="rules"),
    path('submitverification',views.submitverification,name = 'submitverification'),
    path('create-email',views.create_email,name = 'create_email'),
    path('create-forgot-email',views.create_forgot_email,name = 'create_forgot_email'),
    path('media-page',views.media_page,name = 'media-page'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
]+static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
