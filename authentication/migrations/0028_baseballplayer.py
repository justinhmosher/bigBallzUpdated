# Generated by Django 4.1.5 on 2024-03-15 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0027_game_delete_date_delete_week'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseballPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='player name', max_length=100)),
            ],
        ),
    ]