from django.core.management.base import BaseCommand
from authentication.models import Paid, Email, PastPick
from authentication.NFL_weekly_view.models import PaidNW,PromoUserNW
from authentication.baseball_SL.models import PaidBL,PromoUserBL

class Command(BaseCommand):
    help = 'Transfer all emails from Paid to Email'

    def handle(self, *args, **kwargs):
        paid_list = Paid.objects.all()
        for paid in paid_list:
            new_paid = PaidBL(
                username = paid.username
                )
            new_paid.save()
            new_promo = PromoUserBL(
                username = paid.username
                )
            new_promo.save()

