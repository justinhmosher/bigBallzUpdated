from django.core.management.base import BaseCommand
from authentication.baseball_SL.models import PickBL, ScorerBL
from authentication.models import BaseballPlayer

class Command(BaseCommand):
    help = 'Populates ScorerBL model with unique players from PickBL model, handling multiple leagues.'

    def handle(self, *args, **kwargs):
        # Get all unique league numbers
        league_numbers = PickBL.objects.values_list('league_number', flat=True).distinct()

        # Clear all existing ScorerBL entries
        ScorerBL.objects.all().delete()

        total_count = 0  # Track the total number of scorers added across all leagues

        # Process each league separately
        for league_number in league_numbers:
            self.stdout.write(self.style.NOTICE(f"Processing league number: {league_number}"))

            # Filter picks for the current league
            picks = PickBL.objects.filter(league_number=league_number)

            # Track unique player IDs for the current league
            scorers_list = []
            for pick in picks:
                if pick.pick_player_ID not in ['player ID', 'N/A']:
                    scorers_list.append(pick.pick_player_ID)

            # Remove duplicates
            final_list = list(set(scorers_list))

            league_count = 0  # Track the number of scorers added for the current league
            for ID in final_list:
                try:
                    # Attempt to retrieve the BaseballPlayer instance
                    player = BaseballPlayer.objects.get(player_ID=ID)

                    # Create a new ScorerBL entry
                    scorer = ScorerBL(
                        name=player.name,
                        player_ID=player.player_ID,
                        scored=False,
                        league_number=league_number  # Associate with the current league
                    )
                    scorer.save()
                    league_count += 1
                except BaseballPlayer.DoesNotExist:
                    # Print a warning message if the player is not found
                    self.stdout.write(
                        self.style.WARNING(f"Warning: BaseballPlayer with player_ID '{ID}' does not exist in league {league_number}. Skipping.")
                    )

            # Output the result for the current league
            self.stdout.write(self.style.SUCCESS(f"Successfully added {league_count} new scorers for league {league_number}."))
            total_count += league_count

        # Output the total result
        self.stdout.write(self.style.SUCCESS(f"Successfully added {total_count} new scorers across all leagues."))