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
    pick1 = models.CharField(max_length = 100, default = "N/A")
    pick1_team = models.CharField(max_length = 100, default = "N/A")
    pick1_position = models.CharField(max_length = 100, default = "N/A")
    pick1_color = models.CharField(max_length = 100, default = "N/A")
    pick1_player_ID = models.CharField(max_length= 100, default = "N/A")
    pick1_image = models.ImageField(null = True, blank = True, upload_to='images/')
    pick2 = models.CharField(max_length = 100, default = "N/A")
    pick2_team = models.CharField(max_length = 100, default = "N/A")
    pick2_position = models.CharField(max_length = 100, default = "N/A")
    pick2_color = models.CharField(max_length = 100, default = "N/A")
    pick2_player_ID = models.CharField(max_length= 100, default = "N/A")
    pick2_image = models.ImageField(null = True, blank = True, upload_to='images/')
    def __str__(self):
        return f"{self.team_name}"

class Scorer(models.Model):
    name = models.CharField(max_length = 100, default = "name")
    player_ID = models.CharField(max_length= 100, default = "player ID")
    scored = models.BooleanField(default = False)
    not_scored = models.BooleanField(default = False)
    total_touchdowns = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.name}" 

class PastPick(models.Model):
    username = models.CharField(max_length = 100, default = "username")
    team_name = models.CharField(max_length = 100, default='Default Team Name')
    teamnumber = models.IntegerField(default=1)
    week = models.IntegerField(default = 1)
    pick1 = models.CharField(max_length = 100, default = "N/A")
    pick1_name = models.CharField(max_length = 100, default = "N/A")
    TD1_count = models.IntegerField(default=0)
    pick2 = models.CharField(max_length = 100, default = "N/A")
    pick2_name = models.CharField(max_length = 100, default = "N/A")
    TD2_count = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.team_name}"

class Paid(models.Model):
    your_primary_key = models.AutoField(primary_key=True)
    username = models.CharField(max_length = 100, default = "username")
    paid_status = models.BooleanField(default = False)
    numteams = models.IntegerField(default = 0)
    price = models.IntegerField(default = 0)
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

class NBAPlayer(models.Model):
    name = models.CharField(max_length=100,default = "player name")
    position = models.CharField(max_length= 100, default = "player position name")
    team_name = models.CharField(max_length= 100, default = "player team name")
    player_ID = models.CharField(max_length= 100, default = "player ID")
    def __str__(self):
        return f"{self.name}"

class BaseballPlayer(models.Model):
    name = models.CharField(max_length=100,default = "player name")
    position = models.CharField(max_length= 100, default = "player position name")
    team = models.CharField(max_length= 100, default = "player team name")
    player_ID = models.CharField(max_length= 100, default = "player ID")
    def __str__(self):
        return f"{self.name}"

class Game(models.Model):
    sport = models.CharField(max_length=100,default = "type a sport")
    startDate = models.DateField(default=date.today)
    endDate = models.DateField(default=date.today)
    pot = models.CharField(max_length=100, default="1000")
    week = models.IntegerField(default = 1)
    def __str__(self):
        return f"{self.sport}"

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

class Blog(models.Model):
    title = models.CharField(max_length=100, default="Title")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    body = CKEditor5Field(default="Body")
    author = models.CharField(max_length=100, default="Author")
    date = models.DateField(default=date.today)
    updated_at = models.DateTimeField(auto_now=True) 
    summary = models.CharField(max_length=255, default="Summary", blank=True)
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    tags = models.CharField(max_length=100, blank=True)
    is_published = models.BooleanField(default=False)
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Blog, self).save(*args, **kwargs)
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})

class Waitlist(models.Model):
    username = models.CharField(max_length = 100, default = "username")
    def __str__(self):
        return f"{self.username}"

class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    team_name = models.CharField(max_length=100, default="Team")
    likes_count = models.IntegerField(default=0)
    dislikes_count = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.room_name} - {self.message[:50]}"

class MessageReaction(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    REACTION_CHOICES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'message')

class Message(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    week = models.IntegerField(null=True, blank=True)
    is_header = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.content}"


