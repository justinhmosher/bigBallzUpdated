from django.db import models
from django.contrib.auth.models import User

"""
class Player(models.Model):
    team = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.team} ({self.position})"

class SavedPlayer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    player_id = models.IntegerField() # Adjust the max length as needed

    def __str__(self):
        return f"{self.user.username}'s pick: {self.player_name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add any other profile-related fields here
"""

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
    first_name = models.CharField(max_length= 100, default = "player first name")
    last_name = models.CharField(max_length= 100, default = "player last name")
    position = models.CharField(max_length= 100, default = "player position name")
    team_name = models.CharField(max_length= 100, default = "player team name")
    player_ID = models.CharField(max_length= 100, default = "player ID")
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
