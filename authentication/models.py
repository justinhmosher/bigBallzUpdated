from django.db import models
from django.contrib.auth.models import User

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
