from django.contrib import admin
from django.urls import path,include
from django.views.generic import RedirectView
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'authentication'

urlpatterns = [
    path('football/', include(('authentication.NFL_weekly_view.urls', 'football'), namespace='football')),
    path('',views.home,name="home"),
    path('signup',views.signup,name="signup"),
    path('signin',views.signin,name="signin"),
    path('signout',views.signout,name="signout"),
    path('teamname/<int:league_num>',views.teamname,name = "teamname"),
    path('game/<int:league_num>',views.game,name="game"),
    path('checking/<int:league_num>',views.checking, name = 'checking'),
    path('location/<int:league_num>',views.location, name = 'location'),
    path('leaderboard/<int:league_num>',views.leaderboard, name = 'leaderboard'),
    path('playerboard/<int:league_num>',views.playerboard,name = 'playerboard'),
    path('forgotPassEmail',views.forgotPassEmail,name='forgotPassEmail'),
    path('passreset/<uidb64>/<token>',views.passreset,name='passreset'),
    path('tournaments',views.tournaments,name='tournaments'),
    path('payment',views.payment,name='payment'),
    path('terms',views.terms,name='terms'),
    path('privacy',views.privacy,name='privacy'),
    path('confirm-email/<str:email>/',views.confirm_email,name='confirm_email'),
    path('confirm-forgot-email/<str:email>/',views.confirm_forgot_email,name='confirm_forgot_email'),
    path('webhooks/coinbase/', views.coinbase_webhook, name='coinbase_webhook'),
    path('testing',views.testing,name='testing'),
    path('rules/<int:game>',views.rules,name="rules"),
    path('submitverification',views.submitverification,name = 'submitverification'),
    path('create-email',views.create_email,name = 'create_email'),
    path('create-forgot-email',views.create_forgot_email,name = 'create_forgot_email'),
    path('hall-of-fame',views.media_page,name = 'media-page'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('chat/<str:room_name>/<int:league_num>', views.room, name='room'),
    path('picking/<int:league_num>', views.picking, name='picking'),
    path('leaders/<int:league_num>', views.player_list, name='leaders'),
    path('search_players/', views.search_players, name='search_players'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('messages/<int:league_num>', views.message_board, name = 'messages'),
]+static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)
