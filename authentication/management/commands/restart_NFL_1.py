from django.core.management.base import BaseCommand
from authentication.models import Paid

class Command(BaseCommand):
    help = 'Set all Paid.paid_status to False'

    def handle(self, *args, **kwargs):
        updated_count = Paid.objects.all().update(paid_status=False)
        self.stdout.write(f"Successfully updated {updated_count} records to set paid_status=False.")
