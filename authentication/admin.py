from django.contrib import admin
from .models import Pick,Paid,NFLPlayer,Week,Date,PastPick,Scorer

# Register your models here.

admin.site.register(Pick)
admin.site.register(Paid)
admin.site.register(NFLPlayer)
admin.site.register(Week)
admin.site.register(Date)
admin.site.register(PastPick)
admin.site.register(Scorer)