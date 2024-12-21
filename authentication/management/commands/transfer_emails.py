from django.core.management.base import BaseCommand
from authentication.models import Paid, Email

class Command(BaseCommand):
    help = 'Transfer all emails from Paid to Email'

    def handle(self, *args, **kwargs):
        Email.objects.all().delete()
        paid_list = Paid.objects.all()
        for paid in paid_list:
            new_email = Email(
                email = paid.username
                )
            new_email.save()
