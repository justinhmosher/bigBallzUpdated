from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from authentication.sitemaps import BlogSitemap, StaticViewSitemap   # Import the sitemap

sitemaps = {
    'blogs': BlogSitemap,
    'static': StaticViewSitemap,  # Add this line
}

urlpatterns = [
    path('',include('authentication.urls')),
    path('admin/',admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
