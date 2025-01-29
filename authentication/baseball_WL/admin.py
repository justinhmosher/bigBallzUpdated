from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import PickBS,ScorerBS,PaidBS,PromoCodeBS,PromoUserBS,WaitlistBS,MessageBS # Import your models

class Game2AdminSite(AdminSite):
    site_header = "Game 4 Admin"
    site_title = "Game 4 Admin Portal"
    index_title = "Manage Game 3 Data"
    def has_permission(self, request):
        return request.user.is_active and (request.user.is_staff or request.user.is_superuser)

# Create an instance of this custom admin site
game4_admin = Game2AdminSite(name='game4_admin')

# Register models with the custom admin site
game4_admin.register(PickBS)
game4_admin.register(ScorerBS)
game4_admin.register(PaidBS)
game4_admin.register(PromoUserBS)
game4_admin.register(WaitlistBS)
game4_admin.register(MessageBS)