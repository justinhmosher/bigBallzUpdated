# Generated by Django 5.1.4 on 2025-01-15 00:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('baseball_SL', '0004_grandslambl_delete_grandslam'),
    ]

    operations = [
        migrations.AddField(
            model_name='grandslambl',
            name='team_name',
            field=models.CharField(default='Default Team Name', max_length=100),
        ),
    ]
