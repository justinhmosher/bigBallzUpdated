from django.db import models
from django.contrib.auth.models import User
#from Pillow import ImageTk, Image

class Pick(models.Model):
    your_primary_key = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length = 100, default='Default Team Name')
    username = models.CharField(max_length = 100, default = "username")
    email = models.EmailField(max_length = 100, default = "useremail@gamil.com")
    isin = models.BooleanField(default = True)
    week = models.IntegerField(default = 1)
    pick1 = models.CharField(max_length = 100, default = "N/A")
    pick2 = models.CharField(max_length = 100, default = "N/A")
    def __str__(self):
        return f"{self.team_name}"

class Paid(models.Model):
    your_primary_key = models.AutoField(primary_key=True)
    username = models.CharField(max_length = 100, default = "username")
    paid_status = models.BooleanField(default = False)
    def __str__(self):
        return f"{self.username}"

class NFLPlayer(models.Model):
    name = models.CharField(max_length=100,default = "player name")
    position = models.CharField(max_length= 100, default = "player position name")
    team_name = models.CharField(max_length= 100, default = "player team name")
    player_ID = models.CharField(max_length= 100, default = "player ID")
    image = models.ImageField(null = True, blank = True, upload_to='images/')
    def __str__(self):
        return f"{self.name}"

class Week(models.Model):
    week = models.IntegerField(default = 1)
    def __str__(self):
        return "week"