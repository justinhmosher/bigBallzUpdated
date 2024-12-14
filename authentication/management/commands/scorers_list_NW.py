from django.core.management.base import BaseCommand
from authentication.NFL_weekly_view.models import PickNW, ScorerNW
from authentication.models import NFLPlayer

class Command(BaseCommand):
    help = 'Populates ScorerNW model with unique players from PickNW model, handling multiple leagues.'

    def handle(self, *args, **kwargs):
        # Get all unique league numbers
        league_numbers = PickNW.objects.values_list('league_number', flat=True).distinct()

        # Clear all existing ScorerNW entries
        ScorerNW.objects.all().delete()

        total_count = 0  # Track the total number of scorers added across all leagues

        # Process each league separately
        for league_number in league_numbers:
            self.stdout.write(self.style.NOTICE(f"Processing league number: {league_number}"))

            # Filter picks for the current league
            picks = PickNW.objects.filter(league_number=league_number)

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
                    # Attempt to retrieve the NFLPlayer instance
                    player = NFLPlayer.objects.get(player_ID=ID)

                    # Create a new ScorerNW entry
                    scorer = ScorerNW(
                        name=player.name,
                        player_ID=player.player_ID,
                        scored=False,
                        league_number=league_number  # Associate with the current league
                    )
                    scorer.save()
                    league_count += 1
                except NFLPlayer.DoesNotExist:
                    # Print a warning message if the player is not found
                    self.stdout.write(
                        self.style.WARNING(f"Warning: NFLPlayer with player_ID '{ID}' does not exist in league {league_number}. Skipping.")
                    )

            # Output the result for the current league
            self.stdout.write(self.style.SUCCESS(f"Successfully added {league_count} new scorers for league {league_number}."))
            total_count += league_count

        # Output the total result
        self.stdout.write(self.style.SUCCESS(f"Successfully added {total_count} new scorers across all leagues."))
