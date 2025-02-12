from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta, time
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
import pytz
#from Pillow import ImageTk, Image

class PickNW(models.Model):
    your_primary_key = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length = 100, default='Default Team Name')
    teamnumber = models.IntegerField(default=1)
    pick_number = models.IntegerField(default=1)
    league_number = models.IntegerField(default=1)
    paid = models.BooleanField(default = False)
    username = models.CharField(max_length = 100, default = "username")
    email = models.EmailField(max_length = 100, default = "useremail@gamil.com")
    pick = models.CharField(max_length = 100, default = "N/A")
    pick_team = models.CharField(max_length = 100, default = "N/A")
    pick_position = models.CharField(max_length = 100, default = "N/A")
    pick_color = models.CharField(max_length = 100, default = "N/A")
    pick_player_ID = models.CharField(max_length= 100, default = "N/A")
    def __str__(self):
        return f"{self.team_name}"

class ScorerNW(models.Model):
    name = models.CharField(max_length = 100, default = "name")
    player_ID = models.CharField(max_length= 100, default = "player ID")
    scored = models.BooleanField(default = False)
    not_scored = models.BooleanField(default = False)
    touchdown_count = models.IntegerField(default=0)
    league_number = models.IntegerField(default=1)
    def __str__(self):
        return f"{self.name}" 

class PaidNW(models.Model):
    your_primary_key = models.AutoField(primary_key=True)
    username = models.CharField(max_length = 100, default = "username")
    paid_status = models.BooleanField(default = False)
    numteams = models.IntegerField(default = 0)
    price = models.IntegerField(default = 0)
    league_number = models.IntegerField(default=1)
    def __str__(self):
        return f"{self.username}"

class PromoCodeNW(models.Model):
    name = models.CharField(max_length=100,default = "name of influencer")
    code = models.CharField(max_length=100,default = "Code")
    def __str__(self):
        return f"{self.name}"

class PromoUserNW(models.Model):
    username = models.CharField(max_length = 100, default = "username")
    code = models.CharField(max_length=100,default = "Code")
    active = models.BooleanField(default = False)
    def __str__(self):
        return f"{self.username}"

class WaitlistNW(models.Model):
    username = models.CharField(max_length = 100, default = "username")
    def __str__(self):
        return f"{self.username}"

class MessageNW(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    week = models.IntegerField(null=True, blank=True)
    is_header = models.BooleanField(default=False)
    league_number = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.content}"

class Group(models.Model):
    username = models.CharField(max_length = 100, default = "username")
    group = models.CharField(max_length = 100, default = "username")
    def __str__(self):
        return f"{self.username}"