from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Pick, Scorer, Message, Game

# Signal for when a player is marked as out (`isin` = False)

@receiver(pre_save, sender=Pick)
def check_player_out_pre_save(sender, instance, **kwargs):
    # Check if the instance already exists in the database
    game = Game.objects.get(sport = 'Football')
    week = game.week  # Example if there's a ForeignKey to Game
    if instance.pk:
        # Get the previous value of the object from the database
        previous_instance = Pick.objects.get(pk=instance.pk)
        if previous_instance.isin and not instance.isin:
            # Trigger the message creation only if `isin` is changed to False
            content = f"Team {instance.team_name} is out!"
            Message.objects.create(content=content, week= week)

@receiver(pre_save, sender=Scorer)
def check_player_scored_pre_save(sender, instance, **kwargs):
    game = Game.objects.get(sport = 'Football')
    week = game.week  # Example if there's a ForeignKey to Game
    if instance.pk:  # Check if the object exists in the database
        try:
            # Fetch the previous state of the object
            previous_instance = Scorer.objects.get(pk=instance.pk)
            if not previous_instance.not_scored and instance.not_scored:
                # Only create the message if `scored` is changing from False to True
                content = f"{instance.name} did not score."
                Message.objects.create(content=content, week=week)
        except Scorer.DoesNotExist:
            pass  # Handle the rare case where the instance doesn't exist (e.g., deleted)

@receiver(pre_save, sender=Scorer)
def check_player_scored_pre_save(sender, instance, **kwargs):
    game = Game.objects.get(sport = 'Football')
    week = game.week  # Example if there's a ForeignKey to Game
    if instance.pk:  # Check if the object exists in the database
        try:
            # Fetch the previous state of the object
            previous_instance = Scorer.objects.get(pk=instance.pk)
            if not previous_instance.scored and instance.scored:
                # Only create the message if `scored` is changing from False to True
                content = f"{instance.name} has scored!"
                Message.objects.create(content=content, week= week)
        except Scorer.DoesNotExist:
            pass  # Handle the rare case where the instance doesn't exist (e.g., deleted)

# Signal for player buy-back
@receiver(post_save, sender=Pick)
def check_player_buy_back(sender, instance, **kwargs):
    if instance.isin:
        content = f"Team {instance.team_name} bought back {instance.pick1}!"
        Message.objects.create(content=content)