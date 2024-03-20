from django.db import models
from django.contrib.auth.models import User
from datetime import date
#from Pillow import ImageTk, Image

class Pick(models.Model):
    your_primary_key = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length = 100, default='Default Team Name')
    teamnumber = models.IntegerField(default=1)
    username = models.CharField(max_length = 100, default = "username")
    email = models.EmailField(max_length = 100, default = "useremail@gamil.com")
    isin = models.BooleanField(default = True)
    pick1 = models.CharField(max_length = 100, default = "N/A")
    pick1_team = models.CharField(max_length = 100, default = "N/A")
    pick1_position = models.CharField(max_length = 100, default = "N/A")
    pick1_color = models.CharField(max_length = 100, default = "N/A")
    pick1_player_ID = models.CharField(max_length= 100, default = "player ID")
    pick2 = models.CharField(max_length = 100, default = "N/A")
    pick2_team = models.CharField(max_length = 100, default = "N/A")
    pick2_position = models.CharField(max_length = 100, default = "N/A")
    pick2_color = models.CharField(max_length = 100, default = "N/A")
    pick2_player_ID = models.CharField(max_length= 100, default = "player ID")
    def __str__(self):
        return f"{self.team_name}"

class Scorer(models.Model):
    player_ID = models.CharField(max_length= 100, default = "player ID")
    def __str__(self):
        return f"{self.player_ID}" 

class PastPick(models.Model):
    username = models.CharField(max_length = 100, default = "username")
    team_name = models.CharField(max_length = 100, default='Default Team Name')
    teamnumber = models.IntegerField(default=1)
    week = models.IntegerField(default = 1)
    pick1 = models.CharField(max_length = 100, default = "N/A")
    pick2 = models.CharField(max_length = 100, default = "N/A")
    def __str__(self):
        return f"{self.team_name}"

class Paid(models.Model):
    your_primary_key = models.AutoField(primary_key=True)
    username = models.CharField(max_length = 100, default = "username")
    paid_status = models.BooleanField(default = False)
    numteams = models.IntegerField(default = 0)
    def __str__(self):
        return f"{self.username}"

class NFLPlayer(models.Model):
    name = models.CharField(max_length=100,default = "player name")
    position = models.CharField(max_length= 100, default = "player position name")
    team_name = models.CharField(max_length= 100, default = "player team name")
    player_ID = models.CharField(max_length= 100, default = "player ID")
    image = models.ImageField(null = True, blank = True, upload_to='images/')
    color = models.CharField(max_length=100,default = "#000000")
    def __str__(self):
        return f"{self.name}"

class BaseballPlayer(models.Model):
    name = models.CharField(max_length=100,default = "player name")
    def __str__(self):
        return f"{self.name}"

class Game(models.Model):
    sport = models.CharField(max_length=100,default = "type a sport")
    startDate = models.DateField(default=date.today)
    endDate = models.DateField(default=date.today)
    pot = models.IntegerField(default=1000)
    week = models.IntegerField(default = 1)
    def __str__(self):
        return f"{self.sport}"

class BitcoinPayment(models.Model):
    address = models.CharField(max_length=35)
    amount = models.DecimalField(max_digits=10, decimal_places=8)
    status = models.CharField(max_length=10, default='pending')  # e.g., pending, confirmed
    created_at = models.DateTimeField(auto_now_add=True)


