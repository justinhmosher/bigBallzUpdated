from django.db import models

class Player(models.Model):
    team = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.team} ({self.position})"
