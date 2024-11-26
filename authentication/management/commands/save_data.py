import requests
from django.core.management.base import BaseCommand
from authentication.models import NFLPlayer
from decouple import config  # Import the decouple library for handling environment variables

class Command(BaseCommand):
    help = 'Fetch NFLPlayers from API and save to the database'

    def handle(self, *args, **options):

        NFLPlayer.objects.all().delete()

        colors = {
        'ARI': '#97233F',
        'ATL' : '#A71930',
        'BAL' : '#241773',
        'BUF' : '#00338D',
        'CAR' : '#00338D',
        'CHI' : '#00338D',
        'CIN':'#FB4F14',
        'CLE':'#311D00',
        'DAL':'#003594',
        'DEN':'#003594',
        'DET':'#0076B6',
        'GB': '#203731',
        'HOU':'#03202F',
        'IND': '#002C5F',
        'JAX':'#006778',
        'KC':'#E31837',
        'LAC': '#0080C6',
        'LAR':'#003594',
        'MIA':'#008E97',
        'MIN': '#4F2683' ,
        'NE':'#002244',
        'NO':'#D3BC8D',
        'NYG':'#0B2265',
        'NYJ':'#125740',
        'LV':'#000000',
        'PHI':'#004C54',
        'PIT':'#FFB612',
        'SF':'#AA0000',
        'SEA':'#002244',
        'TB':'#D50A0A',
        'TEN':'#0C2340',
        'WAS':'#5A1414'
        }

        # Fetch data from the API
        api_key = config('API_SPORTS')  # Replace with your actual API key
        api_endpoint = 'https://api.sportsdata.io/v3/nfl/scores/json/Players'
        headers = {'Ocp-Apim-Subscription-Key': api_key}
        params = {'format': 'json'}  # Specify JSON format

        response = requests.get(api_endpoint, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()

            # Save data to the Book model
            for player_data in data:
                # Adjust the fields based on the actual structure of the API response
                if (player_data['CurrentTeam'] is not None) and ((player_data['Position'] == "RB") or (player_data['Position'] == "WR") or (player_data['Position'] == "TE") or (player_data['Position'] == "QB")):
                    first_name=player_data['FirstName']  # Replace with the actual field in the API response
                    last_name=player_data['LastName']
                    player_name = first_name + " " + last_name 
                    team_name = player_data['CurrentTeam']
                    team_color = colors[team_name]
                    new_player = NFLPlayer(
                        name = player_name,
                        position =player_data['Position'],
                        team_name = player_data['CurrentTeam'],
                        player_ID = player_data['PlayerID'] ,
                        color = team_color
                    )
                    new_player.save()

            self.stdout.write(self.style.SUCCESS('Players fetched and saved successfully.'))
        else:
            self.stdout.write(self.style.ERROR(f'Error fetching data. Status code: {response.status_code}'))