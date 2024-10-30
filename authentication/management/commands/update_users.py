import requests
from django.core.management.base import BaseCommand
from authentication.models import Scorer,PastPick,Pick,Game
from decouple import config  # Import the decouple library for handling environment variables

class Command(BaseCommand):
    help = 'Fetch NFLPlayers from API and save to the database'

    def handle(self, *args, **options):
        scorers = Scorer.objects.filter(scored=True).values_list('player_ID', flat=True)
        game = Game.objects.get(sport = "Football")
        week = game.week
        for pick in Pick.objects.filter(isin = True):
            if pick.pick1_player_ID not in scorers and pick.pick2_player_ID not in scorers:
                pick.isin = False
                pick.save()
            else:
                if pick.pick1_player_ID in scorers:
                    past_pick = PastPick(username = pick.username,
                        team_name = pick.team_name,
                        week = week,
                        teamnumber = pick.teamnumber,
                        pick1 = pick.pick1_player_ID)
                    past_pick.save()
                    pick.pick1 = "N/A"
                    pick.pick1_team = "N/A"
                    pick.pick1_position = "N/A" 
                    pick.pick1_color = "N/A"
                    pick.pick1_player_ID = "N/A"
                    pick.save()
                if pick.pick2_player_ID in scorers:
                    past_pick = PastPick(username = pick.username,
                        team_name = pick.team_name,
                        week = week,
                        teamnumber = pick.teamnumber,
                        pick2 = pick.pick2_player_ID)
                    past_pick.save()
                    pick.pick2 = "N/A"
                    pick.pick2_team = "N/A"
                    pick.pick2_position = "N/A" 
                    pick.pick2_color = "N/A"
                    pick.pick2_player_ID = "N/A"
                    pick.save()



