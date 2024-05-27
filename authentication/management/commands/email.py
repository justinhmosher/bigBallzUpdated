import requests
from django.core.management.base import BaseCommand
from authentication.models import Paid
from decouple import config  # Import the decouple library for handling environment variables
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template.loader import render_to_string
import os
from django.conf import settings
from email.mime.image import MIMEImage

class Command(BaseCommand):
    help = 'Fetch NFLPlayers from API and save to the database'

    def handle(self, *args, **options):

        emails = Paid.objects.values_list('username', flat=True)
        sender_email = config('SENDER_EMAIL')
        sender_name = "The Chosen Fantasy Games"
        sender_password = config('SENDER_PASSWORD')

        smtp_server = config('SMTP_SERVER')
        smtp_port = config('SMTP_PORT')

        for email in emails:
            receiver_email = email
            #urrent_site = get_current_site(request)

            message = MIMEMultipart()
            message['From'] = f"{sender_name} <{sender_email}>"
            message['To'] = receiver_email
            message['Subject'] = "100 Days Out!"
            body = render_to_string('authentication/emarketing.html')
            message.attach(MIMEText(body, "html"))
            text = message.as_string()
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, text)
                self.stdout.write(self.style.SUCCESS(f'Successfully sent email to {receiver_email}'))
            except Exception as e:
                print(f"Failed to send email: {e}")
            finally:
                server.quit()
