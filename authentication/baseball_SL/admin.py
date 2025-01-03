from django.contrib.admin import AdminSite
from django.contrib import admin
from .models import PickBL,ScorerBL,PaidBL,PromoCodeBL,PromoUserBL,WaitlistBL,MessageBL  # Import your models

class Game2AdminSite(AdminSite):
    site_header = "Game 3 Admin"
    site_title = "Game 3 Admin Portal"
    index_title = "Manage Game 3 Data"
    def has_permission(self, request):
        return request.user.is_active and (request.user.is_staff or request.user.is_superuser)

# Create an instance of this custom admin site
game3_admin = Game2AdminSite(name='game3_admin')

# Register models with the custom admin site
game3_admin.register(PickBL)
game3_admin.register(ScorerBL)
game3_admin.register(PaidBL)
game3_admin.register(PromoUserBL)
game3_admin.register(WaitlistBL)
game3_admin.register(MessageBL)
