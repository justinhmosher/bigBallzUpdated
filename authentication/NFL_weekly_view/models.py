from django.db import models
from django.contrib.auth.models import User
from datetime import date, datetime, timedelta, time
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field
import pytz
#from Pillow import ImageTk, Image

class Pick(models.Model):
    your_primary_key = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length = 100, default='Default Team Name')
    teamnumber = models.IntegerField(default=1)
    username = models.CharField(max_length = 100, default = "username")
    email = models.EmailField(max_length = 100, default = "useremail@gamil.com")
    isin = models.BooleanField(default = True)
    pick = models.CharField(max_length = 100, default = "N/A")
    pick_team = models.CharField(max_length = 100, default = "N/A")
    pick_position = models.CharField(max_length = 100, default = "N/A")
    pick_color = models.CharField(max_length = 100, default = "N/A")
    pick_player_ID = models.CharField(max_length= 100, default = "N/A")
    def __str__(self):
        return f"{self.team_name}"

class Scorer(models.Model):
    name = models.CharField(max_length = 100, default = "name")
    player_ID = models.CharField(max_length= 100, default = "player ID")
    scored = models.BooleanField(default = False)
    not_scored = models.BooleanField(default = False)
    touchdown_count = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.name}" 

class Paid(models.Model):
    your_primary_key = models.AutoField(primary_key=True)
    username = models.CharField(max_length = 100, default = "username")
    paid_status = models.BooleanField(default = False)
    numteams = models.IntegerField(default = 0)
    price = models.IntegerField(default = 0)
    def __str__(self):
        return f"{self.username}"

class PromoCode(models.Model):
    name = models.CharField(max_length=100,default = "name of influencer")
    code = models.CharField(max_length=100,default = "Code")
    def __str__(self):
        return f"{self.name}"

class PromoUser(models.Model):
    username = models.CharField(max_length = 100, default = "username")
    code = models.CharField(max_length=100,default = "Code")
    active = models.BooleanField(default = False)
    def __str__(self):
        return f"{self.username}"

class OfAge(models.Model):
    username = models.CharField(max_length = 100, default = "username")
    old = models.BooleanField(default = False)
    young = models.BooleanField(default = False)
    def __str__(self):
        return f"{self.username}"

class UserVerification(models.Model):
    username = models.CharField(max_length = 100, default = "username")
    first_name = models.CharField(max_length=100,default = "first name")
    last_name = models.CharField(max_length=100, default = 'last name')
    dob = models.DateTimeField(default=timezone.now)
    verification_status = models.CharField(max_length=20, blank=True)
    uuid = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return f"{self.username}"

class Waitlist(models.Model):
    username = models.CharField(max_length = 100, default = "username")
    def __str__(self):
        return f"{self.username}"

class Message(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    week = models.IntegerField(null=True, blank=True)
    is_header = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.content}"