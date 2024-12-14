from django.core.management.base import BaseCommand
from authentication.models import Pick, Scorer, NFLPlayer

class Command(BaseCommand):
    help = 'Populates Scorer model with unique players from Pick model where isin is True, sorted by league numbers.'

    def handle(self, *args, **kwargs):
        # Get all league numbers
        league_numbers = Pick.objects.filter(isin=True).values_list('league_number', flat=True).distinct()

        Scorer.objects.all().delete()  # Clear existing Scorer entries

        total_count = 0  # Track the total number of scorers added across leagues

        # Iterate through each league number
        for league_number in league_numbers:
            self.stdout.write(self.style.NOTICE(f"Processing league number: {league_number}"))
        
            # Get picks for the current league
            picks = Pick.objects.filter(isin=True, league_number=league_number)

            # Track unique player IDs
            scorers_list = []
            for pick in picks:
                if pick.pick1_player_ID not in ['player ID', 'N/A']:
                    scorers_list.append(pick.pick1_player_ID)
                if pick.pick2_player_ID not in ['player ID', 'N/A']:
                    scorers_list.append(pick.pick2_player_ID)

            # Remove duplicates
            final_list = list(set(scorers_list))

            league_count = 0  # Track the number of scorers added for the current league
            for ID in final_list:
                try:
                    # Attempt to retrieve the NFLPlayer instance
                    player = NFLPlayer.objects.get(player_ID=ID)

                    # Create a new Scorer entry
                    scorer = Scorer(
                        name=player.name,
                        player_ID=player.player_ID,
                        scored=False,
                        league_number=league_number  # Include league number for tracking
                    )
                    scorer.save()
                    league_count += 1
                except NFLPlayer.DoesNotExist:
                    # Print a message if the player is not found
                    self.stdout.write(
                        self.style.WARNING(f"Warning: NFLPlayer with player_ID '{ID}' does not exist in league {league_number}. Skipping.")
                    )

            # Output the result for the current league
            self.stdout.write(self.style.SUCCESS(f"Successfully added {league_count} new scorers for league {league_number}."))
            total_count += league_count

        # Output the final result
        self.stdout.write(self.style.SUCCESS(f"Successfully added {total_count} new scorers across all leagues."))
