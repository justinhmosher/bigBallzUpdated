# Generated by Django 4.1.5 on 2024-01-15 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0007_pick_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pick',
            name='pick1',
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AlterField(
            model_name='pick',
            name='pick2',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
