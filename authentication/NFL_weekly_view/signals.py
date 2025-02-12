from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import PickNW, ScorerNW, MessageNW, PaidNW
from authentication.models import Game
from authentication.utils import send_email_to_user_NW, send_paid_email

@receiver(pre_save, sender=ScorerNW)
def check_player_scored_pre_save(sender, instance, **kwargs):
    if instance.pk:  # Check if the object exists in the database
        try:
            # Fetch the previous state of the object
            previous_instance = ScorerNW.objects.get(pk=instance.pk)
            if not previous_instance.scored and instance.scored:
                # Only create the message if `scored` is changing from False to True
                send_email_to_user_NW(instance.name, instance.league_number)
        except ScorerNW.DoesNotExist:
            pass  # Handle the rare case where the instance doesn't exist (e.g., deleted)



