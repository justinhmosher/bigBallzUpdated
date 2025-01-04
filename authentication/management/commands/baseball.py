import requests
from django.core.management.base import BaseCommand
from authentication.models import BaseballPlayer
from decouple import config  # Import the decouple library for handling environment variables

class Command(BaseCommand):
    help = 'Fetch MLBPlayers from API and save to the database'

    def handle(self, *args, **options):

        BaseballPlayer.objects.all().delete()

        colors = {
            'ARI': '#A71930',  # Arizona Diamondbacks
            'ATL': '#CE1141',  # Atlanta Braves
            'BAL': '#DF4601',  # Baltimore Orioles
            'BOS': '#BD3039',  # Boston Red Sox
            'CHC': '#0E3386',  # Chicago Cubs
            'CWS': '#27251F',  # Chicago White Sox
            'CIN': '#C6011F',  # Cincinnati Reds
            'CLE': '#00385D',  # Cleveland Guardians
            'COL': '#333366',  # Colorado Rockies
            'DET': '#0C2340',  # Detroit Tigers
            'HOU': '#EB6E1F',  # Houston Astros
            'KC': '#004687',   # Kansas City Royals
            'LAA': '#BA0021',  # Los Angeles Angels
            'LAD': '#005A9C',  # Los Angeles Dodgers
            'MIA': '#00A3E0',  # Miami Marlins
            'MIL': '#FFC52F',  # Milwaukee Brewers
            'MIN': '#002B5C',  # Minnesota Twins
            'NYM': '#FF5910',  # New York Mets
            'NYY': '#003087',  # New York Yankees
            'OAK': '#003831',  # Oakland Athletics
            'PHI': '#E81828',  # Philadelphia Phillies
            'PIT': '#FDB827',  # Pittsburgh Pirates
            'SD': '#2F241D',   # San Diego Padres
            'SF': '#FD5A1E',   # San Francisco Giants
            'SEA': '#005C5C',  # Seattle Mariners
            'STL': '#C41E3A',  # St. Louis Cardinals
            'TB': '#092C5C',   # Tampa Bay Rays
            'TEX': '#003278',  # Texas Rangers
            'TOR': '#134A8E',  # Toronto Blue Jays
            'WSH': '#AB0003'   # Washington Nationals
        }

        # Fetch data from the API
        api_key = config('API_BASE')  # Replace with your actual API key
        api_endpoint = 'https://api.sportsdata.io/v3/mlb/scores/json/PlayersByActive'
        headers = {'Ocp-Apim-Subscription-Key': api_key}
        params = {'format': 'json'}  # Specify JSON format

        response = requests.get(api_endpoint, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()

            # Save data to the Book model
            for player_data in data:
                if (player_data['Team'] is not None):
                    # Adjust the fields based on the actual structure of the API response
                    first_name=player_data['FirstName']  # Replace with the actual field in the API response
                    last_name=player_data['LastName']
                    player_name = first_name + " " + last_name 
                    team_name = player_data['Team']
                    team_color = colors.get(team_name,'#000000')
                    new_player = BaseballPlayer(
                        name = player_name,
                        position =player_data['Position'],
                        team = team_name,
                        player_ID = player_data['PlayerID'] ,
                        color = team_color
                    )
                    new_player.save()

            self.stdout.write(self.style.SUCCESS('Players fetched and saved successfully.'))
        else:
            self.stdout.write(self.style.ERROR(f'Error fetching data. Status code: {response.status_code}'))



