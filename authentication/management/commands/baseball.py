import requests
from django.core.management.base import BaseCommand
from authentication.models import BaseballPlayer
from bs4 import BeautifulSoup
import time  # Import the time module

class Command(BaseCommand):
    help = 'Fetch players from A to Z and save to the database'

    def handle(self, *args, **options):
        base_url = 'https://www.baseball-reference.com/players/{}/'
        letters = [chr(i) for i in range(ord('a'), ord('z')+1)]

        for letter in letters:
            time.sleep(1)  # Pause for 1 second before fetching each letter
            url = base_url.format(letter)
            self.stdout.write(f"Fetching players from: {url}")
            
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                bold_players = soup.find_all('b')
                for b_player in bold_players:
                    player = b_player.find('a')  # Assuming the <a> tag is inside <b>
                    if player:
                        name = player.text
                        link = 'https://www.baseball-reference.com' + player['href']
                        new_player = BaseballPlayer(name = name)
                        new_player.save()
                        #print(f'Name: {name}, Link: {link}')
                        # Here, you can add your logic to save the player to the database
                        # Example:
                        # BaseballPlayer.objects.create(name=name, link=link)
                        
                self.stdout.write(self.style.SUCCESS(f'Players fetched successfully from {url}.'))
            else:
                self.stdout.write(self.style.ERROR(f'Error fetching data from {url}. Status code: {response.status_code}'))



