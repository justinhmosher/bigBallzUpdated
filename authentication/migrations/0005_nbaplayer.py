# Generated by Django 5.1.3 on 2024-11-26 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_rename_team_name_baseballplayer_team'),
    ]

    operations = [
        migrations.CreateModel(
            name='NBAPlayer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='player name', max_length=100)),
                ('position', models.CharField(default='player position name', max_length=100)),
                ('team_name', models.CharField(default='player team name', max_length=100)),
                ('player_ID', models.CharField(default='player ID', max_length=100)),
            ],
        ),
    ]
