from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from authentication.sitemaps import BlogSitemap, StaticViewSitemap   # Import the sitemap
from authentication.NFL_weekly_view.admin import game2_admin
from authentication.baseball_SL.admin import game3_admin
from authentication.baseball_WL.admin import game4_admin
from django.urls import get_resolver

app_name = 'authentication'
app_name = 'football'
app_name = "baseballSL"
app_name = "baseballWL"

sitemaps = {
    'blogs': BlogSitemap,
    'static': StaticViewSitemap,  # Add this line 
}

urlpatterns = [
    path('', include('authentication.urls', namespace='authentication')),
    path('admin/',admin.site.urls),
    path('admin-game2/', game2_admin.urls),  # Custom admin for Game 2
    path('admin-game3/', game3_admin.urls),  # Custom admin for Game 2
    path('admin-game4/', game4_admin.urls),  # Custom admin for Game 2
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('football/', include('authentication.NFL_weekly_view.urls', namespace='football')),
    path('baseballSL/', include('authentication.baseball_SL.urls', namespace='baseballSL')),
    path('baseballWL/', include('authentication.baseball_WL.urls', namespace='baseballWL')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)