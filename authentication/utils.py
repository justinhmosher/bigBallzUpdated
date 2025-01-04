from django.conf import settings
import requests
from .models import Pick
from authentication.NFL_weekly_view.models import PickNW
from authentication.baseball_SL.models import PickBL
from decouple import config
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from django.template.loader import render_to_string
from django.contrib.staticfiles import finders

def send_email_to_user(scorer,league_num):
    emails1 = Pick.objects.filter(pick1 = scorer, league_number = league_num)
    emails2 = Pick.objects.filter(pick2 = scorer, league_number = league_num)
    email_list = []
    for i in emails1:
        if i.username not in email_list:
            email_list.append(i.username)
    for j in emails2:
        if j.username not in email_list:
            email_list.append(j.username)
    sender_email = config('SENDER_EMAIL')
    sender_name = "The Chosen Fantasy Games"
    sender_password = config('SENDER_PASSWORD')

    smtp_server = config('SMTP_SERVER')
    smtp_port = config('SMTP_PORT')

    for email in email_list:
        receiver_email = email

        message = MIMEMultipart()
        message['From'] = f"{sender_name} <{sender_email}>"
        message['To'] = receiver_email
        message['Subject'] = f"{scorer} has scored!"
        body = render_to_string('authentication/scorer_email.html')

        """
        image_path = finders.find('Simple.png')
        print(f"Image path: {image_path}")
        with open(image_path, 'rb') as img:
            image = MIMEImage(img.read(), _subtype="png")
            image.add_header('Content-ID', '<logo_image>')  # Content-ID must match the CID in your HTML
            message.attach(image)
        """
        message.attach(MIMEText(body, "html"))
        text = message.as_string()
            
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, text)
            print(f'Successfully sent email to {receiver_email}')
        except smtplib.SMTPServerDisconnected:
            print(f"Server disconnected unexpectedly when sending email to {receiver_email}. Reconnecting...")
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, text)
                print(f'Successfully sent email to {receiver_email} after reconnecting')
            except Exception as e:
                print(f"Failed to send email to {receiver_email} after reconnecting: {e}")
            except Exception as e:
                print(f"Failed to send email to {receiver_email}: {e}")
            finally:
                server.quit()

def send_email_to_user_NW(scorer, league_num):
    emails = PickNW.objects.filter(pick = scorer, league_number = league_num)
    email_list = []
    for i in emails:
        if i.username not in email_list:
            email_list.append(i.username)
    sender_email = config('SENDER_EMAIL')
    sender_name = "The Chosen Fantasy Games"
    sender_password = config('SENDER_PASSWORD')

    smtp_server = config('SMTP_SERVER')
    smtp_port = config('SMTP_PORT')

    for email in email_list:
        receiver_email = email

        message = MIMEMultipart()
        message['From'] = f"{sender_name} <{sender_email}>"
        message['To'] = receiver_email
        message['Subject'] = f"{scorer} has scored!"
        body = render_to_string('authentication/scorer_email_NW.html')

        """
        image_path = finders.find('Simple.png')
        print(f"Image path: {image_path}")
        with open(image_path, 'rb') as img:
            image = MIMEImage(img.read(), _subtype="png")
            image.add_header('Content-ID', '<logo_image>')  # Content-ID must match the CID in your HTML
            message.attach(image)
        """
        message.attach(MIMEText(body, "html"))
        text = message.as_string()
            
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, text)
            print(f'Successfully sent email to {receiver_email}')
        except smtplib.SMTPServerDisconnected:
            print(f"Server disconnected unexpectedly when sending email to {receiver_email}. Reconnecting...")
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, text)
                print(f'Successfully sent email to {receiver_email} after reconnecting')
            except Exception as e:
                print(f"Failed to send email to {receiver_email} after reconnecting: {e}")
            except Exception as e:
                print(f"Failed to send email to {receiver_email}: {e}")
            finally:
                server.quit()

def send_email_to_user_BL(scorer, league_num):
    emails = PickBL.objects.filter(pick = scorer, league_number = league_num)
    email_list = []
    for i in emails:
        if i.username not in email_list:
            email_list.append(i.username)
    sender_email = config('SENDER_EMAIL')
    sender_name = "The Chosen Fantasy Games"
    sender_password = config('SENDER_PASSWORD')

    smtp_server = config('SMTP_SERVER')
    smtp_port = config('SMTP_PORT')

    for email in email_list:
        receiver_email = email

        message = MIMEMultipart()
        message['From'] = f"{sender_name} <{sender_email}>"
        message['To'] = receiver_email
        message['Subject'] = f"{scorer} has scored!"
        body = render_to_string('authentication/scorer_email_BL.html')

        """
        image_path = finders.find('Simple.png')
        print(f"Image path: {image_path}")
        with open(image_path, 'rb') as img:
            image = MIMEImage(img.read(), _subtype="png")
            image.add_header('Content-ID', '<logo_image>')  # Content-ID must match the CID in your HTML
            message.attach(image)
        """
        message.attach(MIMEText(body, "html"))
        text = message.as_string()
            
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, text)
            print(f'Successfully sent email to {receiver_email}')
        except smtplib.SMTPServerDisconnected:
            print(f"Server disconnected unexpectedly when sending email to {receiver_email}. Reconnecting...")
            try:
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, text)
                print(f'Successfully sent email to {receiver_email} after reconnecting')
            except Exception as e:
                print(f"Failed to send email to {receiver_email} after reconnecting: {e}")
            except Exception as e:
                print(f"Failed to send email to {receiver_email}: {e}")
            finally:
                server.quit()

def send_paid_email(email, league_num):
    sender_email = config('SENDER_EMAIL')
    sender_name = "The Chosen Fantasy Games"
    sender_password = config('SENDER_PASSWORD')

    smtp_server = config('SMTP_SERVER')
    smtp_port = config('SMTP_PORT')
    receiver_email = email

    message = MIMEMultipart()
    message['From'] = f"{sender_name} <{sender_email}>"
    message['To'] = receiver_email
    message['Subject'] = f"Payment Confirmation"
    body = render_to_string('authentication/paid_email.html')

    """
    image_path = finders.find('Simple.png')
    print(f"Image path: {image_path}")
    with open(image_path, 'rb') as img:
        image = MIMEImage(img.read(), _subtype="png")
        image.add_header('Content-ID', '<logo_image>')  # Content-ID must match the CID in your HTML
        message.attach(image)
    """
    message.attach(MIMEText(body, "html"))
    text = message.as_string()
            
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, text)
        print(f'Successfully sent email to {receiver_email}')
    except smtplib.SMTPServerDisconnected:
        print(f"Server disconnected unexpectedly when sending email to {receiver_email}. Reconnecting...")
        try:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, text)
            print(f'Successfully sent email to {receiver_email} after reconnecting')
        except Exception as e:
            print(f"Failed to send email to {receiver_email} after reconnecting: {e}")
        except Exception as e:
            print(f"Failed to send email to {receiver_email}: {e}")
        finally:
            server.quit()