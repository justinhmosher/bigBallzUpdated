# Generated by Django 4.1.5 on 2024-03-21 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0028_baseballplayer'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromoCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='name of influencer', max_length=100)),
                ('code', models.CharField(default='Code', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PromoUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(default='username', max_length=100)),
                ('code', models.CharField(default='Code', max_length=100)),
                ('active', models.BooleanField(default=False)),
            ],
        ),
    ]
