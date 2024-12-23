from django.core.management.base import BaseCommand
from authentication.models import Paid, Email
from authentication.NFL_weekly_view.models import PaidNW,PromoUserNW

class Command(BaseCommand):
    help = 'Transfer all emails from Paid to Email'

    def handle(self, *args, **kwargs):
        Email.objects.all().delete()
        PaidNW.objects.all().delete()
        PromoUserNW.objects.all().delete()
        paid_list = Paid.objects.all()
        for paid in paid_list:
            new_email = Email(
                email = paid.username
                )
            new_email.save()
            new_paid = PaidNW(
                username = paid.username
                )
            new_paid.save()
            new_promo = PromoUserNW(
                username = paid.username
                )
            new_promo.save()

