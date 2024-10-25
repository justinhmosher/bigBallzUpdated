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
from .models import Pick,Paid,NFLPlayer,Game,PastPick,PromoCode,PromoUser,OfAge,UserVerification,Blog,ChatMessage,Waitlist
from django.db.models import Count,F,ExpressionWrapper,fields
from datetime import datetime
from itertools import chain
from collections import defaultdict
from django.utils import timezone
import json
import logging
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from email.utils import formataddr
from django.db.models import Sum
import pytz
from django.core.paginator import Paginator


def testing(request):
	return render(request,'authentication/testing.html')

def custom_csrf_failure_view(request, reason=""):
	# Set an error message to be displayed on the login page
	messages.error(request, "There was an issue with your request. Please sign in again.")
	# Redirect the user back to the login page
	return redirect('signin')  # 'login' should be the name of your login URL

def home(request):
	total_numteams = Paid.objects.filter(paid_status=True).aggregate(Sum('numteams'))['numteams__sum']
	if total_numteams is None:
		total_numteams = 0
	return render(request, "authentication/homepage.html",{'total': 200 - total_numteams})

def blog_detail(request,slug):
	blog_post = get_object_or_404(Blog, slug=slug)
	tags = blog_post.tags.split(',') if blog_post.tags else []
	return render(request, "authentication/blog_detail.html",{'blog_post': blog_post, 'tags': tags})

def media_page(request):
	blog_posts = Blog.objects.filter(is_published=True).order_by('-date')
	return render(request, "authentication/media.html", {'blog_posts': blog_posts})
	
@login_required
def discord(request):
	return render(request,"authentication/discord.html")
	
@login_required
def room(request, room_name):
	username = request.user.username
	paids = Pick.objects.get(username=username,teamnumber=1)
	team = paids.team_name
	messages = ChatMessage.objects.filter(room_name=room_name).order_by('timestamp')
	return render(request, 'authentication/room.html', {
		'room_name': room_name,
		'team':team,
		'messages': messages
	})

@require_POST
def like_message(request, message_id):
    message = ChatMessage.objects.get(id=message_id)
    message.likes += 1
    message.save()
    return JsonResponse({'likes': message.likes})

@require_POST
def dislike_message(request, message_id):
    message = ChatMessage.objects.get(id=message_id)
    message.dislikes += 1
    message.save()
    return JsonResponse({'dislikes': message.dislikes})


def terms(request):
	return render(request,"authentication/terms.html")
def privacy(request):
	return render(request,"authentication/privacy.html")
def rules(request):
	return render(request,'authentication/rules.html')

def confirm_email(request, email):
	user = User.objects.get(username = email)
	if request.method == "POST":
		create_email(request, myuser = user)
	return render(request, "authentication/confirm_email.html",{"email":email})

def search(request):
	if request.method == "POST":
		search = request.POST.get('searched')
		players = NFLPlayer.objects.filter(name__contains=search)[:5]
		return render(request, "authentication/search.html",{'players':players})
	else:
		return render(request, "authentication/search.html")

def signup(request):

	
	if request.method == "POST":

		email = request.POST.get('email')
		password1 = request.POST.get('password1')
		password2 = request.POST.get('password2')
		promocode = request.POST.get('promoCode','').strip()
		username = email

		if password1 != password2:
			messages.error(request,"Passwors didn't match!")
			return redirect('signup')

		if not promocode:
			promocode = "0000"

		if promocode != "0000" and not PromoCode.objects.filter(code = promocode).exists():
			messages.error(request, "Please enter a valid promocode")
			return redirect('signup')

		myuser = User.objects.filter(email=email).first()
		if myuser:
			if myuser.is_active:
				messages.error(request, "Email already registered with an active account! Please try another.")
				return redirect('signup')
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
			return redirect('confirm_email',email = email)
		else:
			messages.error(request, "There was a problem sending your confirmation email.  Please try again.")
			return redirect('signup')



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


@login_required
def teamname(request):

	if request.method == "POST":
		form = CreateTeam(request.POST)
		if form.is_valid():
			team_name = form.cleaned_data['team_name']
			username = request.user.username
			if Pick.objects.filter(team_name = team_name).exists():
				messages.error(request,"Team name already exists.")
				return redirect('teamname')
			elif len(team_name) > 15 or len(team_name) < 6:
				messages.error(request,"Team name need to be between 5-14 characters.")
				return redirect("teamname")
			else:
				paid = Paid.objects.get(username = request.user.username)
				teamcount = paid.numteams
				for i in range(teamcount):
					new_pick = Pick(team_name=team_name,username= request.user.username,teamnumber = i+1)
					new_pick.save()
				return redirect('checking')
		else:
			messages.error(request,"Please submit a valid teamname.")
			return redirect('teamname')
	return render(request,"authentication/teamname.html")


def signin(request):

	if request.method == 'POST':
		username = request.POST.get('username')
		password1 = request.POST.get('password1')
		remember_me = request.POST.get('remember_me')

		user = authenticate(username = username, password = password1)

		if user is not None:
			login(request, user)

			request.session.set_expiry(2592000)  # 2 weeks (in seconds)
			
			return redirect('tournaments')
		else:
			messages.error(request, "Invalid username or password.")
			return redirect('signin')	

	return render(request, "authentication/signin.html")

def signout(request):
	logout(request)
	return redirect('home')

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
				return redirect('signup')
			else:
				num = create_forgot_email(request, myuser = myuser)
				if num == 1:
					return redirect('confirm_forgot_email',email = email)
				else:
					messages.error(request, "There was a problem sending your confirmation email.  Please try again.")
					return redirect('signup')

		else:
			messages.error(request, "Email does not exist.")
			return redirect('forgotPassEmail')

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
				return redirect('signin')
			else:
				messages.error(request,"Passwords do not match.")
				return redirect('passreset',uidb64=uidb64,token=token)
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
		except ObjectDoesNotExist:
			pass
		login(request, myuser)
		return redirect('signin')
	else:
		return render(request, 'authentication/activation_failed.html')	

def signsamp(request):
	return render(request,"authentication/signsamp.html")

@login_required
def teamcount(request):
	team = Paid.objects.get(username = request.user.username)
	if request.method == 'POST':
		num_teams = request.POST.get('num_teams')
		if int(num_teams) > 20:
			messages.error(request,'Maximum of 20 teams allowed.')
			return redirect('teamcount')
		elif int(num_teams) < 1:
			messages.error(request,'Minimum of 1 team.')
			return redirect('teamcount')
		else:
			team.numteams = num_teams
			team.save()
			return redirect('checking')
	return render(request,'authentication/teamcount.html')




logger = logging.getLogger(__name__)

@login_required
def payment(request):
	user = PromoUser.objects.get(username = request.user.username)
	code = user.code
	codeuser = False
	if code != "0000":
		codeuser = True

	if request.method == 'POST':
		promocode = request.POST.get('code',"").strip()
		if not promocode:
			promocode = "0000"
		promouser = PromoUser.objects.get(username = request.user.username)
		promouser.code = promocode
		promouser.save()
		if promocode != "0000":
			codeuser = True
		try:
			team_count = int(request.POST.get('teamCount', 1))
		except ValueError:
			team_count = 1
		if promocode != "0000":
			total_amount = team_count * 50
		else:
			total_amount = team_count * 50  # $50 per team
		info = Paid.objects.get(username = request.user.username)
		info.numteams = team_count
		info.price = total_amount
		info.save()
		username = request.user.username
		note = f"Entry-for-{username}"

		venmo_url = f"https://venmo.com/thechosenfantasy?txn=pay&amount={total_amount}&note={note}"

		return HttpResponseRedirect(venmo_url)
		#messages.success(request,"Please contact (805)377-6155 or email commissioner@thechosenfg.com for payment options")

	else:
		team_count = 1
		total_amount = 100

	context = {
		'team_count': team_count,
		'total_amount': total_amount,
		'promo':codeuser
		} 
	print(context)

	return render(request, 'authentication/payment.html', context)

@csrf_exempt  # Disable CSRF protection for this endpoint
@require_POST
def coinbase_webhook(request):
	payload = json.loads(request.body)
	if payload['event']['type'] == 'charge:confirmed':
		info = Paid.objects.get(username = request.user.username)
		info.paid_status == True
		info.save()
		return redirect('checking')
	else:
		messages.error('Payment was not received.')
		return redirect('payment')

def playerboard(request):
	# Collect player counts from both pick1 and pick2
	player_counts1 = Pick.objects.filter(isin=True).values('pick1').annotate(count=Count('pick1')).order_by('-count')
	player_counts2 = Pick.objects.filter(isin=True).values('pick2').annotate(count=Count('pick2')).order_by('-count')

	# Combine player counts
	player_counts = defaultdict(int)
	player_teams = defaultdict(list)  # Collect teams per player

	for player_count in chain(player_counts1, player_counts2):
		player_name = player_count.get('pick1') or player_count.get('pick2')
		player_counts[player_name] += player_count['count']

	for player_name in player_counts.keys():
		for pick in Pick.objects.filter(isin = True):
			if pick.pick1 == player_name:
				player_teams[player_name].append(pick.team_name)
			if pick.pick2 == player_name:
				player_teams[player_name].append(pick.team_name)

	# Sort players by the number of picks
	sorted_player_counts = sorted(player_counts.items(), key=lambda x: x[1], reverse=True)

	total_in = Pick.objects.filter(isin=True).count()

	# Paginate sorted_player_counts (show 10 players per page)
	paginator = Paginator(sorted_player_counts, 10)  # Show 10 players per page
	page_number = request.GET.get('page')  # Get the page number from the request URL
	page_obj = paginator.get_page(page_number)  # Get the paginated page


	# Pass both sorted_player_counts and player_teams to the template
	return render(request, 'authentication/playerboard.html', {
		'page_obj': page_obj,
		'sorted_player_counts': sorted_player_counts,
		'player_teams': dict(player_teams),
		'total_in': total_in,
	})


	return render(request,'authentication/playerboard.html',{'player_counts':sorted_player_counts,'count':count,'total_in':total_in})

@login_required
def leaderboard(request):
	# Collect player counts from both pick1 and pick2
	player_counts1 = Pick.objects.filter(isin=True).values('pick1').annotate(count=Count('pick1')).order_by('-count')
	player_counts2 = Pick.objects.filter(isin=True).values('pick2').annotate(count=Count('pick2')).order_by('-count')

	# Combine player counts
	player_counts = defaultdict(int)
	player_teams = defaultdict(list)  # Collect teams per player

	for player_count in chain(player_counts1, player_counts2):
		player_name = player_count.get('pick1') or player_count.get('pick2')
		player_counts[player_name] += player_count['count']

	for player_name in player_counts.keys():
		for pick in Pick.objects.filter(isin = True):
			if pick.pick1 == player_name:
				player_teams[player_name].append(pick.team_name)
			if pick.pick2 == player_name:
				player_teams[player_name].append(pick.team_name)


	# Sort players by the number of picks
	sorted_player_counts = sorted(player_counts.items(), key=lambda x: x[1], reverse=True)

	total_in = Pick.objects.filter(isin=True).count()


	user_data = Pick.objects.filter(username=request.user.username, isin=True)

	# Paginate sorted_player_counts (show 10 players per page)
	paginator = Paginator(sorted_player_counts, 10)  # Show 10 players per page
	page_number = request.GET.get('page')  # Get the page number from the request URL
	page_obj = paginator.get_page(page_number)  # Get the paginated page


	# Pass both sorted_player_counts and player_teams to the template
	return render(request, 'authentication/leaderboard.html', {
		'page_obj': page_obj,
		'sorted_player_counts': sorted_player_counts,
		'player_teams': dict(player_teams),
		'total_in': total_in,
		'user_data': user_data,
	})

@login_required
def tournaments(request):
	user = Paid.objects.get(username = request.user.username)
	play = user.paid_status
	game = Game.objects.get(sport = "Football")
	start_date = game.startDate
	today = timezone.now().date()
	days_until_start = (start_date - today).days
	pot = game.pot

	return render(request,'authentication/tournaments.html',{'days':days_until_start,"pot":pot,"play":play})

@login_required
def location(request):
	username = request.user.username
	user_ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')

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
				return redirect('tournaments')
			else:
				messages.error(request,"You are in a disallowed state.")
				return redirect('tournaments')
		else:
			if (start_date <= current_day < end_date):
				return redirect('checking')
			else:
				if paid.paid_status == True:
					return redirect('checking')
				else:
					if total_numteams >= 200:
						try:
							Waitlist.objects.get(username = username)
							messages.error(request,"You are already added to the waitlist.")
							return redirect('tournaments')
						except Waitlist.DoesNotExist:
							waiter = Waitlist(username = username)
							waiter.save()
							messages.error(request,"Max number of teams entered, we are adding you to a waitlist.")
							return redirect('tournaments')
					else:
						if compliance.old == False and compliance.young == False:
							age_api_key = config('AGE_API')
							return render(request,'authentication/agechecking.html',{'api':age_api_key})
						elif compliance.young == True:
							messages.error(request,"You are too young to participate.")
							return redirect("tournaments")
						else:
							return redirect('checking')

	else:
		messages.error(request,"Failed to register location data.")
		return redirect('tournaments')

@login_required
@csrf_exempt  # Use cautiously, ensure your site is protected against CSRF attacks
def submitverification(request):
	username = request.user.username
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
			return redirect('checking')
		else:
			compliance.young = True
			compliance.save()
			return redirect('location')

	# If not a POST request, render the form page
	return redirect('checking')


@login_required
def game(request):
	user_data = Pick.objects.filter(username = request.user.username)
	user_pick_data = Pick.objects.filter(username = request.user.username,isin = True).order_by('teamnumber')
	player_data = []
	pick1_data = None
	pick2_data = None

	if request.method == 'POST':
		search = request.POST.get('searched')

		if search is not None:
			player_data = NFLPlayer.objects.filter(name__icontains=search)[:5]
		
		selected_player = request.POST.get('selected_player')
		try:
			player_data_selected = NFLPlayer.objects.get(name=selected_player)
		except NFLPlayer.DoesNotExist:
			player_data_selected = None
			#messages.error(request, "Selected player does not exist.")
		if player_data_selected is not None:
			num = game_search(request.user.username,player_data_selected)
			if num == 1:
				messages.error(request,"Selected players cannot be on the same team.")
			elif num ==3:
				messages.error(request,"Your selected player has already scored a TD.")

		change_pick = request.POST.get('change_pick','{}')
		try:
			data = json.loads(change_pick)
			pick = data.get('pick')
			team = data.get('team')
			for user_pick in user_pick_data.filter(teamnumber=team):
				if pick == 'pick1':
					user_pick.pick1 = "N/A"
					user_pick.pick1_team = "N/A"
					user_pick.pick1_position = "N/A" 
					user_pick.pick1_color = "N/A"
					user_pick.pick1_player_ID = "N/A"
					user_pick.pick1_image = "N/A"
				elif pick == "pick2":
					user_pick.pick2 = "N/A"
					user_pick.pick2 = "N/A"
					user_pick.pick2_team = "N/A"
					user_pick.pick2_position = "N/A" 
					user_pick.pick2_color = "N/A"
					user_pick.pick2_player_ID = "N/A"
					user_pick.pick2_image = "N/A"
				user_pick.save()
		except json.JSONDecodeError:
			messages.error(request, "Invalid change pick data.")

	game = Game.objects.get(sport = "Football")
	start = game.startDate
	current_day = timezone.now().date()
	if current_day <= start:
		has_started = False
	else:
		has_started = True
	team = Pick.objects.get(username = request.user.username, teamnumber = 1)
	name = team.team_name

	total_in = Pick.objects.filter(isin = True).count()

	active_teams = Pick.objects.filter(username=request.user.username, isin=True).values_list('teamnumber', flat=True)

	past_picks = PastPick.objects.filter(username=request.user.username, teamnumber__in=active_teams).order_by('teamnumber', 'pick1', 'pick2')

	organized_picks = defaultdict(list)

	for pick in past_picks:
		if pick.pick1 != "N/A":  # Only add if pick1 is not "N/A"
			player1 = NFLPlayer.objects.get(player_ID=pick.pick1)
			organized_picks[pick.teamnumber].append(player1.name)
		if pick.pick2 != "N/A":  # Only add if pick2 is not "N/A"
			player2 = NFLPlayer.objects.get(player_ID=pick.pick2)
			organized_picks[pick.teamnumber].append(player2.name)

	organized_picks = dict(organized_picks)

	print(organized_picks)


	return render(request, 'authentication/game.html', 
		{'player_data': player_data, 
		'user_pick_data' : user_pick_data,
		'has_started' : has_started,
		'start':start,
		'team':name,
		'total':total_in,
		'organized_picks': organized_picks
		})

def game_search(username,playerdata):
	user_pick_data = Pick.objects.filter(username = username,isin = True).order_by('teamnumber')
	for pick in user_pick_data:
		past_picks = PastPick.objects.filter(username = username,teamnumber = pick.teamnumber)
		scorers = []
		for past in past_picks:
			if past.pick1 != "N/A":
				scorers.append(past.pick1)
			elif past.pick2 != "N/A":
				scorers.append(past.pick2)
		if pick.pick1 == 'N/A':
			try:
				player_data_pick2 = NFLPlayer.objects.get(name=pick.pick2)
				if player_data_pick2.team_name == playerdata.team_name:
					return 1
				elif playerdata.player_ID in scorers:
					return 3
				else:
					pick.pick1 = playerdata.name
					pick.pick1_team = playerdata.team_name
					pick.pick1_position = playerdata.position 
					pick.pick1_color = playerdata.color
					pick.pick1_player_ID = playerdata.player_ID
					pick.pick1_image = playerdata.image
					pick.save()
					return 2
			except NFLPlayer.DoesNotExist:
				if playerdata.player_ID in scorers:
					return 3
				else:
					pick.pick1 = playerdata.name
					pick.pick1_team = playerdata.team_name
					pick.pick1_position = playerdata.position 
					pick.pick1_color = playerdata.color
					pick.pick1_player_ID = playerdata.player_ID
					pick.pick1_image = playerdata.image
					pick.save()
					return 2
		elif pick.pick2 == 'N/A':
			try:
				player_data_pick1 = NFLPlayer.objects.get(name=pick.pick1)
				if player_data_pick1.team_name == playerdata.team_name:
					return 1
				elif playerdata.player_ID in scorers:
					return 3
				else:
					pick.pick2 = playerdata.name
					pick.pick2_team = playerdata.team_name
					pick.pick2_position = playerdata.position
					pick.pick2_color = playerdata.color
					pick.pick2_player_ID = playerdata.player_ID
					pick.pick2_image = playerdata.image
					pick.save()
					return 2
			except NFLPlayer.DoesNotExist:
				pick.pick2 = playerdata.name
				pick.pick2_team = playerdata.team_name
				pick.pick2_position = playerdata.position
				pick.pick2_color = playerdata.color
				pick.pick2_player_ID = playerdata.player_ID
				pick.pick2_image = playerdata.image
				pick.save()
				return 2

	for pick in user_pick_data:
		past_picks = PastPick.objects.filter(username = username,teamnumber = pick.teamnumber)
		scorers = []
		for past in past_picks:
			if past.pick1 != "N/A":
				scorers.append(past.pick1)
			elif past.pick2 != "N/A":
				scorers.append(past.pick2)
		try:
			print(scorers)
			print(playerdata.player_ID)
			player_data_pick2 = NFLPlayer.objects.get(name=pick.pick2)
			if player_data_pick2.team_name == playerdata.team_name:
				return 1
			elif playerdata.player_ID in scorers:
				print('hi')
				return 3
			else:
				print('hello')
				pick.pick1 = playerdata.name
				pick.pick1_team = playerdata.team_name
				pick.pick1_position = playerdata.position 
				pick.pick1_color = playerdata.color
				pick.pick1_player_ID = playerdata.player_ID
				pick.pick1_image = playerdata.image
				pick.save()
				return 2
		except NFLPlayer.DoesNotExist:
				pick.pick1 = playerdata.name
				pick.pick1_team = playerdata.team_name
				pick.pick1_position = playerdata.position
				pick.pick1_color = playerdata.color
				pick.pick1_player_ID = playerdata.player_ID
				pick.pick1_image = playerdata.image
				pick.save()
				return 2
	return 2



@login_required
def checking(request):
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

    # Get the current date in PST for comparison with start and end dates
    current_date_pst = current_pst_time.date()
    
    game = Game.objects.get(sport="Football")
    start_date = game.startDate
    end_date = game.endDate
    week = game.week
    
    # Check if the current date is within the game's start and end dates
    if paid.paid_status == False and (start_date <= current_date_pst < end_date) and current_day_pst in [1, 2]:
        return render(request, 'authentication/picking.html')
    
    elif paid.paid_status == False and (start_date <= current_date_pst < end_date) and current_day_pst not in [1, 2]:
        return redirect('playerboard')
    
    elif paid.paid_status == False:
        return redirect('payment')
    
    elif (paid.paid_status == True) and not (start_date <= current_date_pst < end_date):
        username = request.user.username
        if not Pick.objects.filter(username=username).exists():
            return redirect('teamname')
        return redirect('game')
    
    else:
        username = request.user.username
        if not Pick.objects.filter(username=username).exists():
            return redirect('teamname')
        else:
            user_data = Pick.objects.filter(username=username)
            count_ins = 0
            for i in user_data:
                if i.isin:
                    count_ins += 1
            if count_ins >= 1:
                if current_day_pst in [1, 2] and count > 1 and week != 18:
                    return redirect('game')
                elif count == 1 or week == 18:
                    winners_list = Pick.objects.filter(isin=True)
                    winners = []
                    for win in winners_list:
                        if win.team_name not in winners:
                            winners.append(win.team_name)
                    return render(request, 'authentication/win.html', {'winners': winners})
                else:
                    return redirect('leaderboard')
            else:
                if current_day_pst in [1, 2]:
                    return render(request, 'authentication/picking.html')
                else:
                    return redirect('playerboard')
