# Generated by Django 5.1.3 on 2024-12-20 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0008_pick_paid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Emails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.CharField(default='email', max_length=100)),
                ('blocked', models.BooleanField(default=False)),
            ],
        ),
    ]
