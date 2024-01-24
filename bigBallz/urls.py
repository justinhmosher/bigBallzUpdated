from django.contrib import admin
from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',include('authentication.urls')),
    path('admin/',admin.site.urls),
    path('count/',views.count, name='count')
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
