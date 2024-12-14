import requests
from django.core.management.base import BaseCommand
from authentication.models import Scorer,PastPick,Pick,Game
from decouple import config  # Import the decouple library for handling environment variables

class Command(BaseCommand):
    help = 'Fetch NFLPlayers from API and save to the database, handling multiple leagues.'

    def handle(self, *args, **options):
        # Iterate through each league separately
        league_numbers = Pick.objects.values_list('league_number', flat=True).distinct()

        for league_number in league_numbers:
            self.stdout.write(self.style.NOTICE(f"Processing league number: {league_number}"))

            # Fetch the current game for this league
            try:
                game = Game.objects.get(sport="Football")
                week = game.week
            except Game.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Game not found. Skipping."))
                continue

            # Get scorers who have scored for this league
            scorers = Scorer.objects.filter(scored=True, league_number=league_number).values_list('player_ID', flat=True)

            # Iterate through all picks in this league
            for pick in Pick.objects.filter(isin=True, league_number=league_number):
                if pick.pick1_player_ID not in scorers and pick.pick2_player_ID not in scorers:
                    # Eliminate the team if neither player scored
                    pick.isin = False
                    pick.save()
                else:
                    # Handle pick1 if the player scored
                    if pick.pick1_player_ID in scorers:
                        try:
                            scorer = Scorer.objects.get(player_ID=pick.pick1_player_ID, league_number=league_number)
                            past_pick = PastPick(
                                username=pick.username,
                                team_name=pick.team_name,
                                week=week,
                                teamnumber=pick.teamnumber,
                                pick1=pick.pick1_player_ID,
                                pick1_name=pick.pick1,
                                TD1_count=scorer.total_touchdowns,
                                league_number=league_number,  # Track league number
                            )
                            past_pick.save()
                        except Scorer.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"Scorer for pick1 {pick.pick1_player_ID} in league {league_number} not found. Skipping."))

                        # Reset pick1 fields
                        pick.pick1 = "N/A"
                        pick.pick1_team = "N/A"
                        pick.pick1_position = "N/A"
                        pick.pick1_color = "N/A"
                        pick.pick1_player_ID = "N/A"
                        pick.save()

                    # Handle pick2 if the player scored
                    if pick.pick2_player_ID in scorers:
                        try:
                            scorer = Scorer.objects.get(player_ID=pick.pick2_player_ID, league_number=league_number)
                            past_pick = PastPick(
                                username=pick.username,
                                team_name=pick.team_name,
                                week=week,
                                teamnumber=pick.teamnumber,
                                pick2=pick.pick2_player_ID,
                                pick2_name=pick.pick2,
                                TD2_count=scorer.total_touchdowns,
                                league_number=league_number,  # Track league number
                            )
                            past_pick.save()
                        except Scorer.DoesNotExist:
                            self.stdout.write(self.style.WARNING(f"Scorer for pick2 {pick.pick2_player_ID} in league {league_number} not found. Skipping."))

                        # Reset pick2 fields
                        pick.pick2 = "N/A"
                        pick.pick2_team = "N/A"
                        pick.pick2_position = "N/A"
                        pick.pick2_color = "N/A"
                        pick.pick2_player_ID = "N/A"
                        pick.save()

            self.stdout.write(self.style.SUCCESS(f"Finished processing league {league_number}."))

        self.stdout.write(self.style.SUCCESS("Successfully processed all leagues."))



