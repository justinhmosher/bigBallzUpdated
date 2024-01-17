from django.contrib import admin
from .models import Pick,Paid,NFLPlayer

# Register your models here.

admin.site.register(Pick)
admin.site.register(Paid)
admin.site.register(NFLPlayer)