# Generated by Django 5.1.3 on 2024-12-20 02:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0009_emails'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Emails',
            new_name='Email',
        ),
    ]