from django.contrib import admin
from .models import Pick,Paid,NFLPlayer,Game,PastPick,Scorer,BaseballPlayer,PromoCode,PromoUser,OfAge,UserVerification, Blog

# Register your models here.

class NFLPlayerAdmin(admin.ModelAdmin):
    search_fields = ['name','team_name']

admin.site.register(Pick)
admin.site.register(Paid)
admin.site.register(NFLPlayer, NFLPlayerAdmin)
admin.site.register(Game)
admin.site.register(PastPick)
admin.site.register(Scorer)
admin.site.register(BaseballPlayer)
admin.site.register(PromoCode)
admin.site.register(PromoUser)
admin.site.register(OfAge)
admin.site.register(UserVerification)
admin.site.register(Blog)