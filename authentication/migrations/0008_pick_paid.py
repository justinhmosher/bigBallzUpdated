# Generated by Django 5.1.3 on 2024-12-19 00:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_chatmessage_league_number_message_league_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pick',
            name='paid',
            field=models.BooleanField(default=True),
        ),
    ]