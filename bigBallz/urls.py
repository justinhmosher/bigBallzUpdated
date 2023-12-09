from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',include('authentication.urls')),
    path('admin/',admin.site.urls),
    path('count/',views.count, name='count')
]
