from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import PickNW,ScorerNW,PaidNW,PromoCodeNW,PromoUserNW,WaitlistNW,MessageNW  # Import your models

class Game2AdminSite(AdminSite):
    site_header = "Game 2 Admin"
    site_title = "Game 2 Admin Portal"
    index_title = "Manage Game 2 Data"
    def has_permission(self, request):
        return request.user.is_active and (request.user.is_staff or request.user.is_superuser)

# Create an instance of this custom admin site
game2_admin = Game2AdminSite(name='game2_admin')

# Register models with the custom admin site
game2_admin.register(PickNW)
game2_admin.register(ScorerNW)
game2_admin.register(PaidNW)
game2_admin.register(PromoUserNW)
game2_admin.register(WaitlistNW)
game2_admin.register(MessageNW)


