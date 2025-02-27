# Generated by Django 5.1.4 on 2025-01-19 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MessageBS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('content', models.TextField()),
                ('week', models.IntegerField(blank=True, null=True)),
                ('is_header', models.BooleanField(default=False)),
                ('league_number', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='PaidBS',
            fields=[
                ('your_primary_key', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(default='username', max_length=100)),
                ('paid_status', models.BooleanField(default=False)),
                ('numteams', models.IntegerField(default=0)),
                ('price', models.IntegerField(default=0)),
                ('league_number', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='PickBS',
            fields=[
                ('your_primary_key', models.AutoField(primary_key=True, serialize=False)),
                ('team_name', models.CharField(default='Default Team Name', max_length=100)),
                ('teamnumber', models.IntegerField(default=1)),
                ('pick_number', models.IntegerField(default=1)),
                ('league_number', models.IntegerField(default=1)),
                ('paid', models.BooleanField(default=False)),
                ('username', models.CharField(default='username', max_length=100)),
                ('email', models.EmailField(default='useremail@gamil.com', max_length=100)),
                ('pick', models.CharField(default='N/A', max_length=100)),
                ('pick_team', models.CharField(default='N/A', max_length=100)),
                ('pick_position', models.CharField(default='N/A', max_length=100)),
                ('pick_color', models.CharField(default='N/A', max_length=100)),
                ('pick_player_ID', models.CharField(default='N/A', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PromoCodeBS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='name of influencer', max_length=100)),
                ('code', models.CharField(default='Code', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PromoUserBS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='username', max_length=100)),
                ('code', models.CharField(default='Code', max_length=100)),
                ('active', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ScorerBS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='name', max_length=100)),
                ('player_ID', models.CharField(default='player ID', max_length=100)),
                ('scored', models.BooleanField(default=False)),
                ('not_scored', models.BooleanField(default=False)),
                ('touchdown_count', models.IntegerField(default=0)),
                ('league_number', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='WaitlistBS',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='username', max_length=100)),
            ],
        ),
    ]
