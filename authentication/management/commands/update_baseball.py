import requests
from django.core.management.base import BaseCommand
from authentication.baseball_SL.models import ScorerBL,PastPickBL,PickBL,GrandSlamBL
from authentication.models import Game
from decouple import config  # Import the decouple library for handling environment variables
from collections import defaultdict

class Command(BaseCommand):
    help = 'Fetch NFLPlayers from API and save to the database, handling multiple leagues.'

    def handle(self, *args, **options):
        # Iterate through each league separately
        league_numbers = PickBL.objects.values_list('league_number', flat=True).distinct()

        for league_number in league_numbers:
            self.stdout.write(self.style.NOTICE(f"Processing league number: {league_number}"))

            # Fetch the current game for this league
            try:
                game = Game.objects.get(sport="Baseball")
                week = game.week
            except Game.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Game not found. Skipping."))
                continue

            # Get scorers who have scored for this league
            scorers = ScorerBL.objects.filter(scored=True, league_number=league_number).values_list('player_ID', flat=True)
            picks = PickBL.objects.filter(isin = True).order_by('teamnumber', 'username', 'pick_number')
            # Use a dictionary to group picks by teamnumber and username
            grouped_picks = defaultdict(lambda: defaultdict(list))
            for pick in picks:
                # Group by teamnumber and username
                grouped_picks[pick.teamnumber][pick.username].append(pick.pick_player_ID)
            # Check each group and update isin field
            for teamnumber, user_data in grouped_picks.items():
                for username, pick_player_IDs in user_data.items():
                    # Check if any pick_player_ID matches a scorer
                    if not any(pick_player_ID in scorers for pick_player_ID in pick_player_IDs):
                        # Update all picks for this teamnumber and username to set isin=False
                        PickBL.objects.filter(teamnumber=teamnumber, username=username).update(isin=False)
                    else:
                        # Handle matching player IDs
                        for pick_player_ID in [pid for pid in pick_player_IDs if pid in scorers]:
                            matching_scorer = ScorerBL.objects.get(player_ID=pick_player_ID)
                            if matching_scorer.player_ID == pick_player_ID:
                                # Create a PastPickBL instance
                                PastPickBL.objects.create(
                                    username=username,
                                    team_name=PickBL.objects.filter(username=username, teamnumber=teamnumber).first().team_name,
                                    teamnumber=teamnumber,
                                    week=week,  # Assuming week is passed as pagenum or needs to be set dynamically
                                    pick=pick_player_ID,
                                    pick_name=matching_scorer.name,
                                    HR_count=matching_scorer.homerun_count,
                                    league_number=league_number
                                )
                                PickBL.objects.filter(
                                    username=username,
                                    teamnumber=teamnumber,
                                    pick_player_ID=pick_player_ID
                                ).update(
                                    pick="N/A",
                                    pick_team="N/A",
                                    pick_position="N/A",
                                    pick_color="N/A",
                                    pick_player_ID="N/A"
                                )
                                if matching_scorer.grand_slam == True:
                                    GrandSlamBL.objects.create(
                                        player_name = matching_scorer.name,
                                        player_ID = pick_player_ID,
                                        username = username,
                                        league_number = league_number,
                                        teamnumber = teamnumber)
                                    
        game = Game.objects.get(sport="Baseball")
        week = game.week
        Game.objects.get(name = "Baseball").update(week = week + 1)

            self.stdout.write(self.style.SUCCESS(f"Finished processing league {league_number}."))

        self.stdout.write(self.style.SUCCESS("Successfully processed all leagues."))