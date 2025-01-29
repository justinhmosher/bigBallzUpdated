from django.core.management.base import BaseCommand
from authentication.models import Paid, Email, PastPick
from authentication.NFL_weekly_view.models import PaidNW,PromoUserNW
from authentication.baseball_WL.models import PaidBS,PromoUserBS

class Command(BaseCommand):
    help = 'Transfer all emails from Paid to Email'

    def handle(self, *args, **kwargs):
        paid_list = Paid.objects.all()
        for paid in paid_list:
            new_paid = PaidBS(
                username = paid.username
                )
            new_paid.save()
            new_promo = PromoUserBS(
                username = paid.username
                )
            new_promo.save()

