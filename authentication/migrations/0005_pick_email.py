# Generated by Django 4.1.5 on 2023-12-12 02:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_rename_pcik1_pick_pick1_rename_pcik2_pick_pick2_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='pick',
            name='email',
            field=models.EmailField(default='useremail@gamil.com', max_length=100),
        ),
    ]
