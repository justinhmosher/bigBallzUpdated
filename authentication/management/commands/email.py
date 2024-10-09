import requests
from django.core.management.base import BaseCommand
from authentication.models import Paid
from decouple import config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.template.loader import render_to_string

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

            message = MIMEMultipart()
            message['From'] = f"{sender_name} <{sender_email}>"
            message['To'] = receiver_email
            message['Subject'] = "Week 6 Picks Reminder"
            body = render_to_string('authentication/emarketing.html')
            message.attach(MIMEText(body, "html"))
            text = message.as_string()
            
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, text)
                self.stdout.write(self.style.SUCCESS(f'Successfully sent email to {receiver_email}'))
            except smtplib.SMTPServerDisconnected:
                self.stdout.write(self.style.ERROR(f"Server disconnected unexpectedly when sending email to {receiver_email}. Reconnecting..."))
                try:
                    server = smtplib.SMTP(smtp_server, smtp_port)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, text)
                    self.stdout.write(self.style.SUCCESS(f'Successfully sent email to {receiver_email} after reconnecting'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to send email to {receiver_email} after reconnecting: {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to send email to {receiver_email}: {e}"))
            finally:
                server.quit()

