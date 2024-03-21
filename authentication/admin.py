from django.contrib import admin
from .models import Pick,Paid,NFLPlayer,Game,PastPick,Scorer,BaseballPlayer,PromoCode,PromoUser

# Register your models here.

admin.site.register(Pick)
admin.site.register(Paid)
admin.site.register(NFLPlayer)
admin.site.register(Game)
admin.site.register(PastPick)
admin.site.register(Scorer)
admin.site.register(BaseballPlayer)
admin.site.register(PromoCode)
admin.site.register(PromoUser)