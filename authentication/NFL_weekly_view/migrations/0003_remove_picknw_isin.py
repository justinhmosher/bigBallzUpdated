# Generated by Django 5.1.3 on 2024-12-02 23:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('NFL_weekly_view', '0002_rename_message_messagenw_rename_paid_paidnw_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='picknw',
            name='isin',
        ),
    ]
