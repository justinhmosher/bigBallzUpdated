# Generated by Django 5.1.3 on 2024-12-08 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0005_nbaplayer'),
    ]

    operations = [
        migrations.AddField(
            model_name='pastpick',
            name='TD1_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='pastpick',
            name='TD2_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='scorer',
            name='total_touchdowns',
            field=models.IntegerField(default=0),
        ),
    ]