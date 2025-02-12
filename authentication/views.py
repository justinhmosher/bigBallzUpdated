from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from bigBallz import settings
from django.core.mail import send_mail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.template.loader import render_to_string
import requests
from decouple import config
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .forms import PlayerSearchForm, Pickform, Pick1Form, CreateTeam
from .models import Pick,Wallet,Scorer,Paid,NFLPlayer,Game,PastPick,PromoCode,PromoUser,OfAge,UserVerification,Blog,ChatMessage,Waitlist,MessageReaction,Message,Email,KYC,Group
from authentication.NFL_weekly_view.models import PickNW
from authentication.baseball_SL.models import PickBL,PromoUserBL
from authentication.baseball_WL.models import PickBS,PromoUserBS
from django.db.models import Count,F,ExpressionWrapper,fields,OuterRef,Subquery
from datetime import datetime, time
from itertools import chain
from collections import defaultdict
from django.utils import timezone
import json
import logging
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from email.utils import formataddr
from django.db.models import Sum, IntegerField, F
import pytz
from django.core.paginator import Paginator
from django.db import models
from authentication.NFL_weekly_view.models import PaidNW,PromoUserNW
from django.urls import reverse
from coinbase_commerce.client import Client
from authentication.utils import send_email_to_user_BL, send_paid_email

@login_required
def message_board(request,league_num):
	username = request.user.username
	player = Paid.objects.get(username = username)
	if int(league_num) != player.league_number:
		return redirect("authentication:message_board", league_num = player.league_number)
	# Fetch all messages, ordered by week and timestamp
	messages = Message.objects.filter(league_number = league_num).order_by('-week', '-timestamp')

	# Group messages by week
	grouped_messages = {}
	for message in messages:
		if message.week not in grouped_messages:
			grouped_messages[message.week] = []
		grouped_messages[message.week].append(message)

	wallet_user = Wallet.objects.get(username = request.user.username)
	dollars = wallet_user.amount

	return render(request, 'authentication/messages.html', {
		'grouped_messages': grouped_messages,
		'pay_status':player.paid_status,
		'dollars':dollars
		})

def testing(request):
	return render(request,'authentication/testing.html')

def custom_csrf_failure_view(request, reason=""):
	# Set an error message to be displayed on the login page
	messages.error(request, "There was an issue with your request. Please sign in again.")
	# Redirect the user back to the login page
	return redirect('authentication:signin')  # 'login' should be the name of your login URL

def home(request):
	#return redirect('authentication:tournaments')
	tournaments = [
		{
			'name': 'NFL - Touchdown Mania',
			'description': 'Each week, choose two players to score a touchdown and get one or more offensive yards./If one or both score and have one or more offensive yards, you advance, else you are out./Last man standing wins the pot!',
			'deadline': 'Deadline: September 11, 2025',
		},
		{
			'name': 'MLB - Home Run Derby',
			'description': "Each week, choose three players to hit a home run./If any player hits a home run, you advance, else you are out./You will be unable to reselect your home run hitter the following week only./If a selected player hits a grand slam, you may not choose that player for the remainder of the tournament./Last man standing wins the pot!",
			'deadline': 'Deadline: March 30, 2025',
		},
		{
			'name': 'NBA - Double-Double Contest',
			'description': "Each week, choose two players to record a double-double (double digit numbers in two or more statistical categories)./If one or both players record a double-double, you advance, else you are out./Last man standing wins the pot!",
			'deadline': 'Deadline: October 14, 2025',
		},
	]
	return render(request, "authentication/homepage.html", {'tournaments': tournaments})



def blog_detail(request,slug):
	blog_post = get_object_or_404(Blog, slug=slug)
	tags = blog_post.tags.split(',') if blog_post.tags else []
	return render(request, "authentication/blog_detail.html",{'blog_post': blog_post, 'tags': tags})

def media_page(request):
	blog_posts = Blog.objects.filter(is_published=True).order_by('-date')
	return render(request, "authentication/media.html", {'blog_posts': blog_posts})
	
@login_required
def room(request,room_name,league_num):
	username = request.user.username
	player = Paid.objects.get(username = username)
	if int(league_num) != player.league_number:
		return redirect("authentication:room", room_name = 'general', league_num = player.league_number)

	username = request.user.username
	try:
		paids = Pick.objects.get(username=username, teamnumber=1,pick_number = 1)
		team = paids.team_name
	except Pick.DoesNotExist:
		team = "No Team"

	# Fetch all chat messages for the room, including their likes and dislikes count
	messages = ChatMessage.objects.filter(room_name=room_name, league_number = league_num).order_by('timestamp').values(
		'id', 'message', 'team_name', 'timestamp', 'likes_count', 'dislikes_count'
	)

	# Convert the QuerySet to a list of dictionaries
	messages = list(messages)

	wallet_user = Wallet.objects.get(username = request.user.username)
	dollars = wallet_user.amount
    
	return render(request, 'authentication/room.html', {
		'room_name': room_name,
		'team': team,
		'messages': messages,
		'league_number': league_num,
		'pay_status' : player.paid_status,
		'dollars':dollars
	})

def terms(request):
	return render(request,"authentication/terms.html")

def privacy(request):
	return render(request,"authentication/privacy.html")

def rules(request,game):
	if game == 1:
		return render(request,'authentication/rules.html')
	if game ==2:
		return render(request,"authentication/rules_NW.html")
	if game==3:
		return render(request,"authentication/rules_BL.html")
	if game==4:
		return render(request,"authentication/rules_BS.html")

def confirm_email(request, email):
	user = User.objects.get(username = email)
	if request.method == "POST":
		create_email(request, myuser = user)
	return render(request, "authentication/confirm_email.html",{"email":email})

def signup(request):

	
	if request.method == "POST":

		email = request.POST.get('email')
		password1 = request.POST.get('password1')
		password2 = request.POST.get('password2')
		promocode = request.POST.get('promoCode','').strip()
		username = email

		if password1 != password2:
			messages.error(request,"Passwors didn't match!")
			return redirect('authentication:signup')

		if not promocode:
			promocode = "0000"

		if promocode != "0000" and not PromoCode.objects.filter(code = promocode).exists():
			messages.error(request, "Please enter a valid promocode")
			return redirect('authentication:signup')

		myuser = User.objects.filter(email=email).first()
		if myuser:
			if myuser.is_active:
				messages.error(request, "Email already registered with an active account! Please try another.")
				return redirect('authentication:signup')
			else:
				myuser.username = username
				myuser.email = email
				myuser.set_password(password1)
				myuser.is_active = False
				myuser.save()
		else:
			myuser = User.objects.create_user(username, email, password1)
			myuser.is_active = False
			myuser.save()

		num = create_email(request, myuser)
		if num == 1:
			return redirect('authentication:confirm_email',email = email)
		else:
			messages.error(request, "There was a problem sending your confirmation email.  Please try again.")
			return redirect('authentication:signup')



	return render(request,"authentication/signup.html")

def create_email(request, myuser):

	sender_email = config('SENDER_EMAIL')
	sender_name = "The Chosen Fantasy Games"
	sender_password = config('SENDER_PASSWORD')
	receiver_email = myuser.username

	smtp_server = config('SMTP_SERVER')
	smtp_port = config('SMTP_PORT')

	current_site = get_current_site(request)

	message = MIMEMultipart()
	message['From'] = f"{sender_name} <{sender_email}>"
	message['To'] = receiver_email
	message['Subject'] = "Your Confirmation Email"
	body = render_to_string('authentication/email_confirmation.html',{
		'domain' : current_site.domain,
		'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
		'token' : generate_token.make_token(myuser),
			})
	message.attach(MIMEText(body, "html"))
	text = message.as_string()
	try:
		server = smtplib.SMTP(smtp_server, smtp_port)
		server.starttls()  # Secure the connection
		server.login(sender_email, sender_password)
		# Send the email
		server.sendmail(sender_email, receiver_email, text)
		#redirect('confirm_email',email = receiver_email)
	except Exception as e:
		print(f"Failed to send email: {e}")
		messages.error(request, "There was a problem sending your confirmation email.  Please try again.")
		return 2
		#redirect('signup')
	finally:
		server.quit()

	return 1


def get_pick_object(username, teamnumber):
    for model in [Pick, PickBL, PickNW, PickBS]:
        if model.objects.filter(username=username, teamnumber=teamnumber).exists():
            return model.objects.get(username=username, teamnumber=teamnumber, pick_number = 1)
    return None  # Return None if no pick object is found

@login_required
def teamname(request):
    if not Pick.objects.filter(username=request.user.username).exists() and not PickBL.objects.filter(username=request.user.username).exists() and not PickNW.objects.filter(username=request.user.username).exists() and not PickBS.objects.filter(username=request.user.username).exists():
        if request.method == "POST":
            form = CreateTeam(request.POST)
            if form.is_valid():
                team_name = form.cleaned_data['team_name']
                username = request.user.username
                if Pick.objects.filter(team_name = team_name).exists() or PickBL.objects.filter(team_name = team_name).exists() or PickBS.objects.filter(team_name = team_name).exists() or Pick.objects.filter(team_name = team_name).exists():
                    messages.error(request,"Team name already exists.")
                    return redirect('authentication:teamname' , league_num = league_num)
                elif len(team_name) > 16:
                    messages.error(request,"Team name needs to be less than 15 characters.")
                    return redirect("authentication:teamname" , league_num = league_num)
                else:
                    paid = Paid.objects.get(username = request.user.username)
                    if paid.paid_status == False:
                        for j in range(2):
                            new_pick = Pick(team_name=team_name,username= request.user.username,paid = False,pick_number = j+1, teamnumber = 1)
                            new_pick.save()
                    else:
                        teamcount = paid.numteams
                        for i in range(teamcount):
                            for j in range(2):
                                new_pick = Pick(team_name=team_name,username= request.user.username,paid = True,pick_number = j+1,teamnumber = i+1)
                                new_pick.save()
                    return redirect('authentication:checking', league_num = new_pick.league_number)
            else:
                messages.error(request,"Please submit a valid teamname.")
                return redirect('authentication:teamname', league_num = league_num)
    else:
        pick = get_pick_object(request.user.username, teamnumber=1)
        paid = Paid.objects.get(username = request.user.username)
        if paid.paid_status == False:
            for j in range(2):
                new_pick = Pick(team_name=pick.team_name,username= request.user.username,paid = False,pick_number = j+1, teamnumber = 1)
                new_pick.save()
        return redirect('authentication:checking', league_num = new_pick.league_number)

    return render(request,"authentication/teamname.html")


def signin(request):

	if request.method == 'POST':
		username = request.POST.get('username')
		password1 = request.POST.get('password1')

		user = authenticate(username = username, password = password1)

		if user is not None:
			login(request, user)

			request.session.set_expiry(2592000)  # 2 weeks (in seconds)

			next_url = request.POST.get('next')
			if next_url:
				return HttpResponseRedirect(next_url)  # Redirect to the next URL

			return redirect('authentication:tournaments')  # Default redirection
		
		else:
			messages.error(request, "Invalid username or password.")
			return redirect('authentication:signin')	

	return render(request, "authentication/signin.html")

def signout(request):
	logout(request)
	return redirect('authentication:home')

def confirm_forgot_email(request, email):
	user = User.objects.get(username = email)
	if request.method == "POST":
		create_forgot_email(request, myuser = user)
	return render(request, "authentication/confirm_forgot_email.html",{"email":email})

def forgotPassEmail(request):
	if request.method == "POST":
		email = request.POST.get('email')

		if User.objects.filter(email=email).exists():
			myuser = User.objects.get(email = email)
			if myuser.is_active == False:
				messages.error(request,'Please Sign Up again.')
				return redirect('authentication:signup')
			else:
				num = create_forgot_email(request, myuser = myuser)
				if num == 1:
					return redirect('authentication:confirm_forgot_email',email = email)
				else:
					messages.error(request, "There was a problem sending your confirmation email.  Please try again.")
					return redirect('authentication:signup')

		else:
			messages.error(request, "Email does not exist.")
			return redirect('authentication:forgotPassEmail')

	return render(request,'authentication/forgotPassEmail.html')

def create_forgot_email(request, myuser):

	sender_email = config('SENDER_EMAIL')
	sender_name = "The Chosen Fantasy Games"
	sender_password = config('SENDER_PASSWORD')
	receiver_email = myuser.username

	smtp_server = config('SMTP_SERVER')
	smtp_port = config('SMTP_PORT')

	current_site = get_current_site(request)

	message = MIMEMultipart()
	message['From'] = f"{sender_name} <{sender_email}>"
	message['To'] = receiver_email
	message['Subject'] = "Change Your Password for The Chosen"
	body = render_to_string('authentication/email_change.html',{
		'domain' : current_site.domain,
		'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
		'token' : generate_token.make_token(myuser),
		})
	message.attach(MIMEText(body, "html"))
	text = message.as_string()
	try:
		server = smtplib.SMTP(smtp_server, smtp_port)
		server.starttls()  # Secure the connection
		server.login(sender_email, sender_password)
		server.sendmail(sender_email, receiver_email, text)
	except Exception as e:
		print(f"Failed to send email: {e}")
		messages.error(request, "There was a problem sending your email.  Please try again.")
		return 2
		#redirect('signup')
	finally:
		server.quit()

	return 1


def passreset(request, uidb64, token):
	try:
		uid = force_str(urlsafe_base64_decode(uidb64))
		myuser = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		myuser = None
	if myuser is not None and generate_token.check_token(myuser,token):

		if request.method == "POST":
			pass1 = request.POST.get('password1')
			pass2 = request.POST.get('password2')
			if pass1 == pass2:
				myuser.set_password(pass1)
				myuser.save()
				return redirect('authentication:signin')
			else:
				messages.error(request,"Passwords do not match.")
				return redirect('authentication:passreset',uidb64=uidb64,token=token)
	return render(request,'authentication/passreset.html',{'uidb64':uidb64,'token':token})


def activate(request, uidb64, token):
	try:
		uid = force_str(urlsafe_base64_decode(uidb64))
		myuser = User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		myuser = None

	if myuser is not None and generate_token.check_token(myuser,token):
		myuser.is_active = True
		myuser.save()
		try:
			codeuser = PromoUser(username = myuser.username,code = "0000")
			codeuser.save()
			compliance = OfAge(username = myuser.username)
			compliance.save()
			new_user = Paid(username = myuser.username)
			new_user.save()
			NW_paid = PaidNW(username = myuser.username)
			NW_paid.save()
			NW_promo = PromoUserNW(username = myuser.username)
			NW_promo.save()
			BL_paid = PaidBL(username = myuser.username)
			BL_paid.save()
			BL_promo = PromoUserBL(username = myuser.username)
			BL_promo.save()
			BS_paid = PaidBS(username = myuser.username)
			BS_paid.save()
			BS_promo = PromoUserBS(username = myuser.username)
			BS_promo.save()
			wallet_user = Wallet(username = username)
			wallet_user.save()
			email = Email(email = myuser.username)
			email.save()
		except ObjectDoesNotExist:
			pass
		login(request, myuser)
		return redirect('authentication:signin')
	else:
		return render(request, 'authentication/activation_failed.html')	


logger = logging.getLogger(__name__)


@login_required
def entry(request):
    if request.method == "POST":
        username = request.user.username
        num_entries = int(request.POST.get("num_entries", 1))  # Default to 1 entry
        emails = request.POST.get("emails", "")  # Group email list
        total_cost = num_entries * 50  # $50 per entry

        try:
            wallet = Wallet.objects.get(username=username)

            if wallet.amount < total_cost:
                # Not enough funds, redirect to deposit page
                return JsonResponse({"success": False, "message": "Insufficient funds. <a href='/payment'>Make a deposit here</a>"})

            # Deduct amount from wallet
            wallet.amount -= total_cost
            wallet.save()

            # Store group data
            group_entry = Group(username=username, group=emails)
            group_entry.save()

            paid_user = Paid.objects.get(username=username)
            paid_user.paid_status = True
            paid_user.numteams = num_entries
            paid_user.save()

            pick = Pick.objects.get(username = username, pick_number = 1)
            team = pick.team_name

            for i in Pick.objects.filter(username=username):
                if i.paid == False:
                    i.delete()

            for i in range(num_entries):
                for j in range(2):
                    new_pick = Pick(team_name=team,username= username,paid = True,pick_number = j+1,teamnumber = i+1)
                    new_pick.save()

            send_paid_email(username, 1)

            return JsonResponse({"success": True, "message": "Entry confirmed! Your wallet has been debited."})

        except Wallet.DoesNotExist:
            return JsonResponse({"success": False, "message": "Wallet not found. Please contact support."})

    wallet_user = Wallet.objects.get(username = request.user.username)
    dollars = wallet_user.amount

    return render(request, "authentication/entry.html",{
        'dollars':dollars,
        })

@login_required
def payment(request):

	player = Paid.objects.get(username = request.user.username)

	username = request.user.username
	note = f"Entry-for-{username}-minigame"

	venmo_url = f"https://venmo.com/thechosenfantasy?txn=pay&amount={50}&note={note}"

	wallet_user = Wallet.objects.get(username = request.user.username)
	dollars = wallet_user.amount

	return render(request, 'authentication/payment.html',
        {
        'dollars':dollars,
        'venmo_url':venmo_url,
        'pay_status':player.paid_status,

        })

@login_required
def create_coinbase_payment(request):
    COINBASE_API_KEY = config('COINGBASE_COMMERCE')
    print(COINBASE_API_KEY)
    amount = 50  # Example: $50 deposit amount
    username = request.user.username
    description = f"Deposit for {username}"

    try:
        client = Client(api_key=COINBASE_API_KEY)
        print(client)
        charge = client.charge.create(
            name="Account Deposit",
            description=description,
            local_price={"amount": str(amount), "currency": "USD"},
            pricing_type="fixed_price",
            metadata={"user_id": request.user.id, "username": username},
            redirect_url="https://yourwebsite.com/payment-success/",
            cancel_url="https://yourwebsite.com/payment-failed/"
        )
        return JsonResponse({"checkout_url": charge.hosted_url})
    except Exception as e:
        return JsonResponse({"error": str(e)})
"""
def KYC_check(username):
	if KYC.objects.filter(username = username).exists():
		kyc_entry = KYC.objects.filter(username=username).first()
		if kyc_entry.kyc_status == "rejected":
			return 0
		elif kyc_entry.kyc_status == "pending":
			return 1
		elif kyc_entry.kyc_status == "approved":
			return 2
	else:
		return redirect("authentication:start_KYC_verification")

@login_required
def start_KYC_verification(request):
	SUMSUB_API_URL = "https://api.sumsub.com"
	SUMSUB_APP_TOKEN = config('SUBSUM_SECRET')

	#Starts the Sumsub KYC verification process for a user without an existing applicant ID.

	username = request.user.username
	user = request.user
	kyc_entry, created = KYC.objects.get_or_create(username=username, user = user)

	# 🔹 Only create a Sumsub applicant if it doesn’t exist
	if not kyc_entry.applicant_id:
		url = f"{SUMSUB_API_URL}/resources/applicants?levelName=basic-kyc-level"
		headers = {
			"X-App-Token": SUMSUB_APP_TOKEN,
			"Content-Type": "application/json"
		}
		data = {"externalUserId": "SMITH ANDREW", "fixedInfo": {"country": "US"}}

		response = requests.post(url, headers=headers, json=data)

		if response.status_code in [200, 201]:
			applicant_data = response.json()
			kyc_entry.applicant_id = applicant_data["id"]
			kyc_entry.kyc_status = "pending"
			kyc_entry.save()
		else:
			return render(request, "authentication/kyc_failed.html", {"error": "Failed to start verification"})

	# 🔹 Fetch Sumsub access token for Web SDK
	url = f"{SUMSUB_API_URL}/resources/accessTokens?userId={kyc_entry.applicant_id}&levelName=basic-kyc-level"
	headers = {"X-App-Token": SUMSUB_APP_TOKEN}
	response = requests.post(url, headers=headers)

	if response.status_code == 200:
		access_token = response.json()["token"]
		return render(request, "authentication/kyc_verification.html", {"access_token": access_token})
	else:
		return render(request, "authentication/kyc_failed.html", {"error": "Failed to fetch verification token"})


def subsum_webhook(request):

    #Webhook to update KYC status when Sumsub completes verification.

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        raw_body = request.body
        sumsub_signature = request.headers.get("X-App-Access-Sig", "")

        computed_signature = hmac.new(
            settings.SUBSUM_SECRET_KEY.encode(), raw_body, hashlib.sha256
        ).hexdigest()

        if computed_signature != sumsub_signature:
            return JsonResponse({"error": "Invalid signature"}, status=403)

        data = json.loads(raw_body)
        applicant_id = data.get("applicantId")
        review_status = data.get("reviewStatus")

        kyc_entry = KYC.objects.filter(applicant_id=applicant_id).first()
        if not kyc_entry:
            return JsonResponse({"error": "User not found"}, status=404)

        # ✅ Update KYC status based on Sumsub result
        if review_status == "completed":
            review_result = data.get("reviewResult", {})
            if review_result.get("reviewAnswer") == "GREEN":
                kyc_entry.kyc_status = "approved"
                kyc_entry.kyc_verified_at = timezone.now()
            else:
                kyc_entry.kyc_status = "rejected"
            kyc_entry.save()

        return JsonResponse({"message": "Webhook received", "status": kyc_entry.kyc_status})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
"""

@csrf_exempt  # Disable CSRF protection for this endpoint
@require_POST
def coinbase_webhook(request):
	payload = json.loads(request.body)
	if payload['event']['type'] == 'charge:confirmed':
		info = Paid.objects.get(username = request.user.username)
		info.paid_status == True
		info.save()
		return redirect('authentication:checking')
	else:
		messages.error('Payment was not received.')
		return redirect('authentication:payment')

@login_required
def playerboard(request, league_num):
    username = request.user.username
    player = Paid.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("authentication:playerboard", league_num = player.league_number)
    # Define the PST timezone
    pst = pytz.timezone('America/Los_Angeles')

    # Get the current time in PST
    current_pst_time = timezone.now().astimezone(pst)
    current_day_pst = current_pst_time.weekday()  # This gives the day of the week (int)
    current_date_pst = current_pst_time.date()

    game = Game.objects.get(sport="Football")
    start_date = game.startDate
    end_date = game.endDate

    end_datetime = datetime.combine(end_date, time(23, 59, 59))
    end_datetime = pst.localize(end_datetime)

    start_datetime = datetime.combine(start_date, time(17, 0))  # Combine date with 5:00 PM
    start_datetime = pst.localize(start_datetime)  # Make it timezone-aware

    current_pst_time = datetime.now(pst)

    """
    if current_day_pst == 3 and current_pst_time <= thursday_deadline:  # Thursday before 5:00 PM PST
        within_deadline = True
    elif current_day_pst in [1, 2]:  # Tuesday or Wednesday
        within_deadline = True
    else:
        within_deadline = False
    
    if (within_deadline) or not (start_datetime <= current_pst_time < end_datetime):
        return redirect('authentication:checking', league_num = league_num)  # Replace 'some_other_page' with the name of an appropriate view
    """
    pick_counts = Pick.objects.filter(league_number = league_num).exclude(pick='N/A').values('pick','pick_team', 'pick_position').annotate(count=Count('pick')).order_by('-count')

    player_counts = defaultdict(lambda: {'count': 0, 'teams': None, 'positions': None})

    for players in pick_counts:
        player_name = players.get('pick')
        team = players.get('pick_team')
        position = players.get('pick_position')
        player_counts[player_name]['count'] += players['count']
        player_counts[player_name]['teams'] = team
        player_counts[player_name]['positions'] = position

    # Collect teams or users associated with each pick
    pick_teams = defaultdict(list)
    for pick_record in Pick.objects.exclude(pick='N/A'):
        pick_teams[pick_record.pick].append(pick_record.team_name)

    player_status = {}
    for pick_name in pick_counts:
        player_name = pick_name['pick']
        scorer = Scorer.objects.filter(name=player_name).first()
        player_status[player_name] = {
            'scored':scorer.scored if scorer else False,
            'not_scored':scorer.not_scored if scorer else False,
        }


    # Sort players by the number of picks
    sorted_player_counts = sorted(
        [{'player': player, **data} for player, data in player_counts.items()],
        key=lambda x: x['count'],
        reverse=True
    )

    total_in = int(Pick.objects.filter(paid = True,league_number = league_num).count() / 2)

    # Paginate sorted_player_counts (show 10 players per page)
    paginator = Paginator(sorted_player_counts, 10)  # Show 10 players per page
    page_number = request.GET.get('page')  # Get the page number from the request URL
    page_obj = paginator.get_page(page_number)  # Get the paginated page


    # Pass both sorted_player_counts and player_teams to the template

    wallet_user = Wallet.objects.get(username = request.user.username)
    dollars = wallet_user.amount

    return render(request, 'authentication/playerboard.html', {
        'page_obj': page_obj,
        'sorted_player_counts': sorted_player_counts,
        'player_teams': dict(pick_teams),
        'player_status': player_status,
        'total_in': total_in, 
        'dollars':dollars
        })


@login_required
def leaderboard(request, league_num):
    username = request.user.username
    player = Paid.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("authentication:leaderboard", league_num = player.league_number)
    # Define the PST timezone
    pst = pytz.timezone('America/Los_Angeles')

    # Get the current time in PST
    current_pst_time = timezone.now().astimezone(pst)
    current_day_pst = current_pst_time.weekday()  # This gives the day of the week (int)
    current_date_pst = current_pst_time.date()

    game = Game.objects.get(sport="Football")
    start_date = game.startDate
    end_date = game.endDate

    end_datetime = datetime.combine(end_date, time(23, 59, 59))
    end_datetime = pst.localize(end_datetime)

    start_datetime = datetime.combine(start_date, time(17, 0))  # Combine date with 5:00 PM
    start_datetime = pst.localize(start_datetime)  # Make it timezone-aware

    current_pst_time = datetime.now(pst)

    """
    if current_day_pst == 3 and current_pst_time <= thursday_deadline:  # Thursday before 5:00 PM PST
        within_deadline = True
    elif current_day_pst in [1, 2]:  # Tuesday or Wednesday
        within_deadline = True
    else:
        within_deadline = False
    
    if (within_deadline) or not (start_datetime <= current_pst_time < end_datetime):
        return redirect('authentication:checking', league_num = league_num)  # Replace 'some_other_page' with the name of an appropriate view
    """
    pick_counts = Pick.objects.filter(league_number = league_num).exclude(pick='N/A').values('pick','pick_team', 'pick_position').annotate(count=Count('pick')).order_by('-count')

    player_counts = defaultdict(lambda: {'count': 0, 'teams': None, 'positions': None})

    for players in pick_counts:
        player_name = players.get('pick')
        team = players.get('pick_team')
        position = players.get('pick_position')
        player_counts[player_name]['count'] += players['count']
        player_counts[player_name]['teams'] = team
        player_counts[player_name]['positions'] = position

    # Collect teams or users associated with each pick
    pick_teams = defaultdict(list)
    for pick_record in Pick.objects.exclude(pick='N/A'):
        pick_teams[pick_record.pick].append(pick_record.team_name)

    player_status = {}
    for pick_name in pick_counts:
        player_name = pick_name['pick']
        scorer = Scorer.objects.filter(name=player_name).first()
        player_status[player_name] = {
            'scored':scorer.scored if scorer else False,
            'not_scored':scorer.not_scored if scorer else False,
        }


    # Sort players by the number of picks
    sorted_player_counts = sorted(
        [{'player': player, **data} for player, data in player_counts.items()],
        key=lambda x: x['count'],
        reverse=True
    )

    total_in = int(Pick.objects.filter(paid = True,league_number = league_num).count() / 2)

    # Paginate sorted_player_counts (show 10 players per page)
    paginator = Paginator(sorted_player_counts, 10)  # Show 10 players per page
    page_number = request.GET.get('page')  # Get the page number from the request URL
    page_obj = paginator.get_page(page_number)  # Get the paginated page

    user_data= Pick.objects.filter(username = request.user.username)

    wallet_user = Wallet.objects.get(username = request.user.username)
    dollars = wallet_user.amount

    # Pass both sorted_player_counts and player_teams to the template
    return render(request, 'authentication/leaderboard.html', {
        'page_obj': page_obj,
        'sorted_player_counts': sorted_player_counts,
        'player_teams': dict(pick_teams),
        'player_status': player_status,
        'total_in': total_in,
        'user_data': user_data,
        'dollars':dollars
    })

def tournaments(request):
	"""
	try:
		user = username.objects.filter(username = username)
	except user.DoesNotExist:
		user = False
	"""

	games = {
		"Football": [
			{"name": "SEASON LONG GAME", 
			"summary": "Each week, choose two players to score a touchdown and get one or more offensive yards./If one or both score and have one or more offensive yards, you advance, else you're out./Last man standing wins the pot!", 
			"money": "",
			"rules": 1, 
			"playable": True,
			"app": "authentication",
			"path": reverse("authentication:location", args=[1])
		},
		{	
			"name": "WEEKLY GAME", 
			"summary": "Select 10 NFL players to score touchdowns and accumulate one or more offensive yards./The user with the most comultive touchdowns wins the pot!", 
			"money": "",
			"rules": 2, 
			"playable": True,
			"app" : "football",
			"path": reverse("football:location", args=[1]) }
		],
		"Baseball": [
			{"name": "SEASON LONG GAME", 
			"summary": "Each week, choose three players to hit a home run./If any player hits a home run, you advance, else you are out./You will be unable to reselect your home run hitter the following week only./If a selected player hits a grand slam, you may not choose that player for the remainder of the tournament./Last man standing wins the pot!", 
			"money": "Buy In: $50",
			"rules": 3, 
			"playable": True,
			"app" : "football",
			"path":reverse("baseballSL:location", args=[1])
		},
		{
			"name": "WEEKLY GAME", 
			"summary": "Select 10 players to hit a home run./The user with the most comultive home runs wins the pot!", 
			"money": "",
			"rules": 4, 
			"playable": True,
			"app" : "football",
			"path":reverse("baseballWL:location", args=[1])},
		],
		"Basketball": [
			{"name": "SEASON LONG GAME", 
			"summary": "Each week, choose two players to record a double-double (double digit numbers in two or more statistical categories)./If one or both players record a double-double, you advance, else you're out./Last man standing wins the pot!", 
			"money": "",
			"rules": 5, 
			"playable": False,
			"app" : "football",
			"path":reverse("authentication:location", args=[1])
		},
		{
			"name": "WEEKLY GAME", 
			"summary": "Select 10 players to record a double-double (double digit numbers in two or more statistical categories)./The user with the most comultive double-doubles wins the pot!", 
			"money": "",
			"rules": 6, 
			"playable": False,
			"app" : "football",
			"path":reverse("authentication:location", args=[1])},
		],
	}
	for sport, sport_games in games.items():
		for game in sport_games:
			game["summary"] = game["summary"].split('/')

	for sport, sport_games in games.items():
		for game in sport_games:
			game["money"] = game["money"].split('/')
	"""
	game = Game.objects.get(sport = "Football")
	start_date = game.startDate
	today = timezone.now().date()
	days_until_start = (start_date - today).days
	pot = game.pot
	"""
	current_sport = request.GET.get("sport", "Football")
	current_games = games.get(current_sport, [])
	context = {
		"current_sport": current_sport,
		"games": current_games,
	}
	return render(request, 'authentication/tournaments.html', context)


@login_required
def location(request,league_num):
	username = request.user.username
	player = Paid.objects.get(username = request.user.username)
	if int(league_num) != player.league_number:
		return redirect("authentication:location", league_num = player.league_number)
	user_ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
	return redirect("authentication:checking", league_num = player.league_number)

	access_key = config('API_KEY')
	ipstack_url = f'https://api.ipstack.com/{user_ip_address}?access_key={access_key}'
	response = requests.get(ipstack_url)
		
	if response.status_code==200:
		location_data = response.json()
		user_state = location_data.get('region_name')
		security_data = location_data.get('security', {})
		is_proxy = security_data.get('is_proxy', False)

		disallowed_states = ['Washington','Idaho','Nevada','Montana','Wyoming','Colorado','Iowa','Missouri','Tenessee','Mississippi','Louisiana','Alabama','Florida','Michigan','Ohio','West Virginia','Pensylvania','Maryland','Deleware','New Jersey','Conneticut','Ney York','Maine','New Hampshire','Massachusetts']

		allowed_states = [None,'None','California','Oregon','Alaska','Arizona','Utah','New Mexico','Texas','Oklahoma','Arkansas','Kansas','Nebraska','South Dakota','North Dekota','Minnesota','Wisconsin','Illinois','Indiana','Kentucky','Virginia','North Carolina','South Carolina','Georgia','Vermont','Rhode Island']

		paid = Paid.objects.get(username = username)
		compliance = OfAge.objects.get(username = username)
		current_day = timezone.now().date()
		game = Game.objects.get(sport = "Football")
		start_date = game.startDate
		end_date = game.endDate
		total_numteams = Paid.objects.filter(paid_status=True).aggregate(Sum('numteams'))['numteams__sum']
		if total_numteams is None:
			total_numteams = 0
		if not ((user_state in allowed_states and not is_proxy) or True):
			if is_proxy:
				messages.error(request,"You cannot use a VPN.")
				return redirect('authentication:tournaments')
			else:
				messages.error(request,"You are in a disallowed state.")
				return redirect('authentication:tournaments')
		else:
			if (start_date <= current_day < end_date):
				return redirect('authentication:checking', league_num = player.league_number)
			else:
				if paid.paid_status == True:
					return redirect('authentication:checking', league_num = player.league_number)
				else:
					if total_numteams >= 200:
						try:
							Waitlist.objects.get(username = username)
							messages.error(request,"You are already added to the waitlist.")
							return redirect('authentication:tournaments')
						except Waitlist.DoesNotExist:
							waiter = Waitlist(username = username)
							waiter.save()
							messages.error(request,"Max number of teams entered, we are adding you to a waitlist.")
							return redirect('authentication:tournaments')
					else:
						return redirect('authentication:checking', league_num = player.league_number) #needs to be removed to check age
						if compliance.old == False and compliance.young == False:
							age_api_key = config('AGE_API')
							return render(request,'authentication/agechecking.html',{'api':age_api_key})
						elif compliance.young == True:
							messages.error(request,"You are too young to participate.")
							return redirect("authentication:tournaments")
						else:
							return redirect('authentication:checking', league_num = player.league_number)

	else:
		messages.error(request,"Failed to register location data.")
		return redirect('authentication:tournaments')

@login_required
@csrf_exempt  # Use cautiously, ensure your site is protected against CSRF attacks
def submitverification(request, league_num):
	username = request.user.username
	player = Paid.objects.get(username = username)
	if int(league_num) != player.league_number:
		return redirect("authentication:submitverification", league_num = player.league_number)
	compliance = OfAge.objects.get(username=username)
	# Prepare data for the AgeChecker API
	headers = {
		 "X-AgeChecker-Secret": config('AGE_API_SECRET'),
		 "X-AgeChecker-Key": config('AGE_API'),
		 }
	# Call the AgeChecker API
	response = requests.get('https://api.agechecker.net/v1/latest', headers=headers)

	# Check if the API call was successful
	if response.status_code == 200:
		response_data = response.json()
		verification_status = response_data['status']
		uuid = response_data['uuid']
		# Save verification details in the database

		if verification_status in ['accepted', 'verified']:
			compliance.old = True
			compliance.save()
			return redirect('authentication:checking', league_num = player.league_number)
		else:
			compliance.young = True
			compliance.save()
			return redirect('authentication:location', league_num = player.league_number)

	# If not a POST request, render the form page
	return redirect('authentication:checking', league_num = player.league_number)

@login_required
def player_list(request,league_num):
	username = request.user.username
	player = Paid.objects.get(username = username)
	if int(league_num) != player.league_number:
		return redirect("authentication:player_list", league_num = player.league_number)
	# Create a Subquery to count matching PastPick entries
	past_pick_count = PastPick.objects.filter(
		username=OuterRef('username'), 
    	teamnumber=OuterRef('teamnumber'),
    	league_number= league_num
	).values('username', 'teamnumber').annotate(
		total_touchdowns=Sum(F('TD1_count') + F('TD2_count'))
	).values('total_touchdowns')[:1]  # Use [:1] to limit to one value per group (Subquery requirement)


	# Annotate the Picks queryset with the count of past picks
	data = Pick.objects.filter(paid = True).annotate(
		pick_count=Subquery(past_pick_count, output_field=IntegerField())
	).order_by(
		'-isin',  # Order by `isin` (True first)
		F('pick_count').desc(nulls_last=True),  # Then by pick_count (nulls go to the end)
		'team_name',  # Optional: Break ties by team_name
	)

	data = list(data)
	standings = []
	previous_count = None
	current_rank = 1
	tie_rank = 0
	for index, item in enumerate(data):
		pick_count = item.pick_count
		if pick_count == 0:
			pick_count = None
		if previous_count == 0:
			previous_count = None
		next_pick_count = data[index + 1].pick_count if index + 1 < len(data) else None
		if next_pick_count == 0:
			next_pick_count = None
		is_tied_with_previous = pick_count == previous_count
		is_tied_with_next = pick_count == next_pick_count

		# Handle ties
		if is_tied_with_previous or is_tied_with_next:
			if is_tied_with_previous and is_tied_with_next:
				standings.append({"rank": f"T{current_rank}", "team": item})
			if is_tied_with_previous and not is_tied_with_next:
				standings.append({"rank": f"T{current_rank}", "team": item})
				current_rank = index + 2
			if not is_tied_with_previous and is_tied_with_next:
				if index + 1 == len(data):
					standings.append({"rank": f"{current_rank}", "team": item})
				else:
					standings.append({"rank": f"T{current_rank}", "team": item})
		else:
			standings.append({"rank": current_rank, "team": item})
			current_rank += 1

		previous_count = pick_count

	# Fetch all past picks and group them by (username, teamnumber)
	past_picks_map = {}
	for pick in data:
		# Fetch the related past picks for each team
		past_picks = PastPick.objects.filter(username=pick.username, teamnumber=pick.teamnumber)
		past_picks_map[(pick.username, pick.teamnumber)] = past_picks

	paginator = Paginator(standings, 20)
	page_number = request.GET.get('page', 1)
	page_obj = paginator.get_page(page_number)

	wallet_user = Wallet.objects.get(username = request.user.username)
	dollars = wallet_user.amount

	# Pass the data to the template
	return render(request, 'authentication/leaders.html', {
		'leaderboard': page_obj,
		'past_picks_map': past_picks_map,
		'pay_status':player.paid_status,
		'dollars':dollars,
	})


@login_required
def game(request, league_num):
    username = request.user.username
    player = Paid.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("authentication:game", league_num = player.league_number)
    # Define the PST timezone
    paid = Paid.objects.get(username = request.user.username)
    pst = pytz.timezone('America/Los_Angeles')

    # Get the current time in PST
    current_pst_time = timezone.now().astimezone(pst)
    current_day_pst = current_pst_time.weekday()  # This gives the day of the week (int)
    current_date_pst = current_pst_time.date()

    game = Game.objects.get(sport="Football")
    start_date = game.startDate
    end_date = game.endDate
    paid = Paid.objects.get(username = request.user.username)

    end_datetime = datetime.combine(end_date, time(23, 59, 59))
    end_datetime = pst.localize(end_datetime)

    start_datetime = datetime.combine(start_date, time(17, 0))  # Combine date with 5:00 PM
    start_datetime = pst.localize(start_datetime)  # Make it timezone-aware
    current_pst_time = datetime.now(pst)

    thursday_deadline = current_pst_time.replace(hour=17, minute=0, second=0, microsecond=0)
    """
    if current_day_pst == 3 and current_pst_time <= thursday_deadline:  # Thursday before 5:00 PM PST
        within_deadline = True
    elif current_day_pst in [1, 2]:  # Tuesday or Wednesday
        within_deadline = True
    else:
        within_deadline = False
    if (not within_deadline and (start_datetime <= current_pst_time < end_datetime)):
        return redirect('football:checking', league_num = player.league_number)  # Replace 'some_other_page' with the name of an appropriate view
    """
    user_data = Pick.objects.filter(username = request.user.username)
    user_pick_data = Pick.objects.filter(username = request.user.username).order_by('teamnumber','pick_number')
    player_data = []
    pick1_data = None
    pick2_data = None

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        selected_player = request.POST.get('selected_player')
        page_num = request.POST.get('currentPage')
        if selected_player:
            try:
                # Retrieve the selected player
                player_data_selected = NFLPlayer.objects.get(name=selected_player)
                if paid.paid_status == False:
                    return JsonResponse({"success": False, "message": "Features activate after entry. <a href='/entry'>Enter here.</a>"})
                else:
                    # Use your existing game_search function
                    result = game_search(request.user.username, player_data_selected,page_num)
                    if result == 11:
                        return JsonResponse({'success': False, 'message': "Selected players cannot be on the same team."})
                    elif result == 13:
                        return JsonResponse({'success': False, 'message': "Player already selected."})
                    else:
                        return JsonResponse({
                            'success': True,
                            'message': 'Player selected successfully!',
                            'pick': {
                                'pick_number': result[1],
                                'team_number': result[0],
                                'pick_name': result[2],
                                'pick_team': result[3],
                                'pick_position': result[4],
                                'pick_color': result[5],
                            }
                        })

            except NFLPlayer.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Player not found!'})
            except Pick.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Pick not found!'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid data!'})

    game = Game.objects.get(sport = "Football")
    start = game.startDate
    current_day = timezone.now().date()
    if current_day <= start:
        has_started = False
    else:
        has_started = True
    team = Pick.objects.get(username = request.user.username, teamnumber = 1, pick_number =1)
    name = team.team_name

    # Group picks by team
    team_picks_dict = defaultdict(list)
    for pick in user_pick_data:
        team_picks_dict[pick.teamnumber].append(pick)

    # Convert to a list of teams with picks
    team_picks_list = list(team_picks_dict.values())

    # Paginate the team-level data (1 team per page)
    paginator = Paginator(team_picks_list, 1)  # One team per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_in = int(Pick.objects.filter(paid = True,isin = True,league_number = league_num).count()/2)

    wallet_user = Wallet.objects.get(username = request.user.username)
    dollars = wallet_user.amount


    return render(request, 'authentication/game.html', 
        {'page_obj': page_obj,
        'user_pick_data' : user_pick_data,
        'has_started' : has_started,
        'start':start,
        'team':name,
        'total':total_in,
        'pay_status':player.paid_status,
        'dollars':dollars
        })

@csrf_exempt
@login_required
def update_pick(request):
    if request.method == 'POST':
        change_pick = request.POST.get('change_pick', '{}')
        try:
            data = json.loads(change_pick)
            pick = data.get('pick_number')
            team = data.get('teamnumber')

            if not (pick and team):
                raise ValueError("Invalid pick or team data.")

            user_pick_data = Pick.objects.filter(username=request.user.username)
            for user_pick in user_pick_data.filter(teamnumber=team):
                if int(pick) == user_pick.pick_number:
                    user_pick.pick = "N/A"
                    user_pick.pick_team = "N/A"
                    user_pick.pick_position = "N/A" 
                    user_pick.pick_color = "N/A"
                    user_pick.pick_player_ID = "N/A"
                    user_pick.save()

            return JsonResponse({'success': True})

        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request.'})

def search_players(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
        search_query = request.GET.get('search', '')
        if search_query:
            players = NFLPlayer.objects.filter(name__icontains=search_query)[:5]
            player_list = [{'name': player.name} for player in players]
            return JsonResponse({'players': player_list})
    return JsonResponse({'players': []})

def game_search(username,playerdata,pagenum):
    user_pick_data = Pick.objects.filter(username = username,teamnumber = pagenum).order_by('pick_number')
    for pick in user_pick_data:
        if pick.pick == 'N/A':
            try:
                team_list = Pick.objects.filter(username=username, teamnumber=pick.teamnumber).order_by('pick_number').values_list('pick_team', flat=True)
                all_equal = True
                for i, item in enumerate(team_list):
                    if i != int(pick.pick_number) - 1 and item != playerdata.team_name:
                        all_equal = False
                        break
                ID_list = Pick.objects.filter(username=username, teamnumber=pick.teamnumber).values_list('pick_player_ID', flat=True)
                if all_equal:
                    return 11
                elif playerdata.player_ID in ID_list:
                    return 13
                else:
                    pick.pick = playerdata.name
                    pick.pick_team = playerdata.team_name
                    pick.pick_position = playerdata.position 
                    pick.pick_color = playerdata.color
                    pick.pick_player_ID = playerdata.player_ID
                    pick.save()
                    return [pick.teamnumber,pick.pick_number,pick.pick,pick.pick_team,pick.pick_position,pick.pick_color,pick.pick_player_ID]
            except NFLPlayer.DoesNotExist:
                return [pick.teamnumber,pick.pick_number,pick.pick,pick.pick_team,pick.pick_position,pick.pick_color,pick.pick_player_ID]
    for pick in user_pick_data:
        team_list = Pick.objects.filter(username=username, teamnumber=pick.teamnumber).order_by('pick_number').values_list('pick_team', flat=True)
        all_equal = True
        for i, item in enumerate(team_list):
            if i != int(pick.pick_number) - 1 and item != playerdata.team_name:
                all_equal = False
                break
        ID_list = Pick.objects.filter(username=username, teamnumber=pick.teamnumber).values_list('pick_player_ID', flat=True)
        if all_equal:
            return 11
        elif playerdata.player_ID in ID_list:
            return 13
        else:
            pick.pick = playerdata.name
            pick.pick_team = playerdata.team_name
            pick.pick_position = playerdata.position 
            pick.pick_color = playerdata.color
            pick.pick_player_ID = playerdata.player_ID
            pick.save()
            return [pick.teamnumber,pick.pick_number,pick.pick,pick.pick_team,pick.pick_position,pick.pick_color,pick.pick_player_ID]
    return [pick.teamnumber,pick.pick_number,pick.pick,pick.pick_team,pick.pick_position,pick.pick_color,pick.pick_player_ID]

@login_required
def picking(request,league_num):
	total_in = int(Pick.objects.filter(isin = True,paid = True, league_number = league_num).count() /2)

	wallet_user = Wallet.objects.get(username = request.user.username)
	dollars = wallet_user.amount

	return render(request, 'authentication/picking.html', {
		'total_in': total_in,
		'dollars':dollars
		})

@login_required
def checking(request,league_num):
    username = request.user.username
    player = Paid.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("authentication:checking", league_num = player.league_number)
    if not Paid.objects.filter(username=request.user.username).exists():
        new_user = Paid(username=request.user.username)
        new_user.save()
        
    paid = Paid.objects.get(username=request.user.username)
    count = Pick.objects.filter(isin=True).count()
    
    # Define the PST timezone
    pst = pytz.timezone('America/Los_Angeles')

    # Get the current time in PST
    current_pst_time = timezone.now().astimezone(pst)
    current_day_pst = current_pst_time.weekday()  # This gives the day of the week (int)
    thursday_deadline = current_pst_time.replace(hour=17, minute=0, second=0, microsecond=0)
    if current_day_pst == 3 and current_pst_time <= thursday_deadline:  # Thursday before 5:00 PM PST
    	within_deadline = True
    elif current_day_pst in [1, 2]:  # Tuesday or Wednesday
    	within_deadline = True
    else:
    	within_deadline = False

    # Get the current date in PST for comparison with start and end dates
    current_date_pst = current_pst_time.date()
    
    game = Game.objects.get(sport="Football")
    start_date = game.startDate
    end_date = game.endDate
    week = game.week

    end_datetime = datetime.combine(end_date, time(23, 59, 59))
    end_datetime = pst.localize(end_datetime)

    start_datetime = datetime.combine(start_date, time(17, 0))  # Combine date with 5:00 PM
    start_datetime = pst.localize(start_datetime)  # Make it timezone-aware
    current_pst_time = datetime.now(pst)

    
    # Check if the current date is within the game's start and end dates
    if paid.paid_status == False and (start_datetime <= current_pst_time < end_datetime) and within_deadline:
        return redirect('authentication:picking', league_num = player.league_number)
    
    elif paid.paid_status == False and (start_datetime <= current_pst_time < end_datetime) and not within_deadline:
        return redirect('authentication:playerboard', league_num = player.league_number)
    
    elif  not (start_datetime <= current_pst_time < end_datetime):
        username = request.user.username
        if not Pick.objects.filter(username=username).exists():
            return redirect('authentication:teamname')
        return redirect('authentication:game', league_num = player.league_number)
    else:
        username = request.user.username
        if not Pick.objects.filter(username=username).exists():
            return redirect('authentication:teamname')
        else:
            user_data = Pick.objects.filter(username=username)
            count_ins = 0
            for i in user_data:
                if i.isin:
                    count_ins += 1
            if count_ins >= 1:
                if within_deadline and count > 1 and week != 18:
                    return redirect('authentication:game', league_num = player.league_number)
                elif count == 1 or week == 18:
                    winners_list = Pick.objects.filter(isin=True)
                    winners = []
                    for win in winners_list:
                        if win.team_name not in winners:
                            winners.append(win.team_name)
                    return render(request, 'authentication/win.html', {'winners': winners})
                else:
                    return redirect('authentication:leaderboard', league_num = player.league_number)
            else:
                if within_deadline:
                    return redirect('authentication:game', league_num = player.league_number)
                else:
                    return redirect('authentication:playerboard', league_num = player.league_number)
