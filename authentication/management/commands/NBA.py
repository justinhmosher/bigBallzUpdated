import requests
from django.core.management.base import BaseCommand
from authentication.models import NBAPlayer
from decouple import config  # Import the decouple library for handling environment variables

class Command(BaseCommand):
    help = 'Fetch NBA Players from API and save to the database'

    def handle(self, *args, **options):

        #BaseballPlayer.objects.all().delete()

        # Fetch data from the API
        api_key = config('API_NBA')  # Replace with your actual API key
        api_endpoint = 'https://api.sportsdata.io/v3/nba/scores/json/Players'
        headers = {'Ocp-Apim-Subscription-Key': api_key}
        params = {'format': 'json'}  # Specify JSON format

        response = requests.get(api_endpoint, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()

            # Save data to the Book model
            for player_data in data:
                # Adjust the fields based on the actual structure of the API response
                first_name=player_data['FirstName']  # Replace with the actual field in the API response
                last_name=player_data['LastName']
                player_name = first_name + " " + last_name 
                team_name = player_data['Team']
                new_player = NBAPlayer(
                    name = player_name,
                    position =player_data['Position'],
                    team_name = team_name,
                    player_ID = player_data['PlayerID'] ,
                )
                new_player.save()

            self.stdout.write(self.style.SUCCESS('Players fetched and saved successfully.'))
        else:
            self.stdout.write(self.style.ERROR(f'Error fetching data. Status code: {response.status_code}'))