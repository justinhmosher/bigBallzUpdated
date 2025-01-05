# Generated by Django 5.1.4 on 2025-01-04 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseball_SL', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PastPickBL',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='username', max_length=100)),
                ('team_name', models.CharField(default='Default Team Name', max_length=100)),
                ('teamnumber', models.IntegerField(default=1)),
                ('week', models.IntegerField(default=1)),
                ('pick', models.CharField(default='N/A', max_length=100)),
                ('pick_name', models.CharField(default='N/A', max_length=100)),
                ('HR_count', models.IntegerField(default=0)),
                ('league_number', models.IntegerField(default=1)),
            ],
        ),
    ]
