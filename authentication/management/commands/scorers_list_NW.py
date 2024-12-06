from django.core.management.base import BaseCommand
from authentication.NFL_weekly_view.models import PickNW, ScorerNW
from authentication.models import NFLPlayer

class Command(BaseCommand):
    help = 'Populates Scorer model with unique players from Pick model where isin is True'

    def handle(self, *args, **kwargs):
        # Get all picks where isin is True
        picks = PickNW.objects.all()

        ScorerNW.objects.all().delete()

        # Track the number of scorers added
        scorers_list = []
        for pick in picks:
            if pick.pick_player_ID != 'player ID' and pick.pick_player_ID != 'N/A':
                scorers_list.append(pick.pick_player_ID)

        final_list = [] 

        for scorer in scorers_list:
            if scorer not in final_list:
                final_list.append(scorer)

        print(final_list)

        count = 0

        for ID in final_list:
            try:
                # Attempt to retrieve the NFLPlayer instance
                player = NFLPlayer.objects.get(player_ID=ID)
                print(player)  # Optional: Print the player for debugging

                # Create a new Scorer entry
                scorer = ScorerNW(name=player.name, player_ID=player.player_ID, scored=False)
                scorer.save()
                count += 1
            except NFLPlayer.DoesNotExist:
                # Print a message if the player is not found
                print(f"Warning: NFLPlayer with player_ID '{ID}' does not exist. Skipping.")


        # Output the result to the console
        self.stdout.write(self.style.SUCCESS(f'Successfully added {count} new scorers.'))