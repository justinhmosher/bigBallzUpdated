# Generated by Django 4.1.5 on 2024-05-03 00:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0032_pick_pick1_image_pick_pick2_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfAge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='username', max_length=100)),
                ('status', models.BooleanField(default=False)),
            ],
        ),
    ]