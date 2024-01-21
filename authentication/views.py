from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from bigBallz import settings
from django.core.mail import send_mail
import win32com.client as win32
import pythoncom
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.template.loader import render_to_string
import requests
from decouple import config
from django.contrib.auth.decorators import login_required
#from authentication.models import Player
from django.http import JsonResponse
from .forms import PlayerSearchForm, Pickform, Pick1Form, CreateTeam
from .models import Pick,Paid,NFLPlayer
from django.db.models import Count,F,ExpressionWrapper,fields
from datetime import datetime
from itertools import chain
from collections import defaultdict




def home(request):
	return render(request, "authentication/sample.html")

def search(request):
	if request.method == "POST":
		search = request.POST.get('searched')
		players = NFLPlayer.objects.filter(name__contains=search)[:5]
		return render(request, "authentication/search.html",{'players':players})
	else:
		return render(request, "authentication/search.html")

def signup(request):
	
	if request.method == "POST":

		username = request.POST.get('username')
		email = request.POST.get('email')
		password1 = request.POST.get('password1')
		password2 = request.POST.get('password2')

		if User.objects.filter(username = username):
			messages.error(request, "Username already exists!  Please try another.")
			return redirect('signup')

		if User.objects.filter(email = email):
			messages.error(request, "Email already registered!  Please try another.")
			return redirect('signup')

		if len(username) > 15:
			messages.error(request, "Username is too long!  Please try another. (15 max)")
			return redirect('signup')
		
		if len(username) < 6:
			messages.error(request, "Username is too short!  Please try another. (at least 5)")
			return redirect('signup')

		if password1 != password2:
			messages.error(request,"Passwors didn't match!")

		#Finding users location
		user_ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')

		access_key = config('API_KEY')
		ipstack_url = f'http://api.ipstack.com/{user_ip_address}?access_key={access_key}'
		response = requests.get(ipstack_url)

		if response.status_code==200:
			location_data = response.json()
			user_state = location_data.get('region_name')
			print(user_state)

			disallowed_states = ['California']

			if user_state in disallowed_states:
				messages.error(request,"You are in a disallowed state.")
				return redirect('home')

			else:
				myuser = User.objects.create_user(username, email, password1)
				myuser.is_active = False

				myuser.save()

		else:
			messages.error(request,"Failed to register location data")
			return redirect('home')


		messages.success(request, "Your Account has been successfully created!  We have sent you a confirmation email, please confirm your email in order to activate your account.")

		#Welcome Email

		olApp = win32.Dispatch('Outlook.Application',pythoncom.CoInitialize())
		olNS = olApp.GetNameSpace('MAPI')

		mail_item = olApp.createItem(0)

		mail_item.Subject = "Welcome to Big Ballz League"
		mail_item.BodyFormat = 1

		mail_item.Body = "Hello player !! \n" + "Welcome to The Big Ballz League!! \n Thank you for joining our waitlist \n We have also sent you a confirmation email, please confirm your email address in order to activate your account! \n\n Thank You, \n League Commissioner"
		mail_item.Sender = "commissioner@bigballzdfsl.com"
		mail_item.To = myuser.email

		mail_item.Display()
		mail_item.Save()
		mail_item.Send()

		#Email Address Confirmation Email

		mail_item1 = olApp.createItem(0)

		current_site = get_current_site(request)
		mail_item1.Subject = "Confirm your email for The Big Ballz Leage!"
		mail_item1.BodyFormat = 1
		mail_item1.Body = render_to_string('authentication/email_confirmation.html',{
			'domain' : current_site.domain,
			'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
			'token' : generate_token.make_token(myuser),
			})
		mail_item1.Sender = "commissioner@bigballzdfsl.com"
		mail_item1.To = myuser.email
		mail_item1.Save()
		mail_item1.Send()

		return redirect('signin')

	return render(request,"authentication/signsamp.html")

def teamname(request):

	if request.method == "POST":
		form = CreateTeam(request.POST)
		if form.is_valid():
			team_name = form.cleaned_data['team_name']
			username = request.user.username
			if Pick.objects.filter(team_name = team_name).exists():
				messages.error(request,"Team name already exists!")
				return redirect('teamname')
			elif len(team_name) > 15 or len(team_name) < 6:
				messages.error(request,"Team name need to be between 5-14 characters")
				return redirect("teamname")
			else:
				new_pick = Pick(team_name=team_name,username= request.user.username)
				new_pick.save()
				return redirect('checking')
		else:
			messages.error(request,"Please submit a valid teamname")
			return redirect('teamname')
	return render(request,"authentication/teamname.html")


def signin(request):

	if request.method == 'POST':
		username = request.POST.get('username')
		password1 = request.POST.get('password1')

		user = authenticate(username = username, password = password1)

		if user is not None:
			login(request, user)
			return redirect('checking')

		else:
			messages.error(request, "Bad Credentials!")
			return redirect('signin')	

	return render(request, "authentication/signin.html")

def signout(request):
	logout(request)
	messages.success(request, "Logged Out Successfully")
	return redirect('home')

def forgotPassEmail(request):
	if request.method == "POST":
		email = request.POST.get('email')

		if User.objects.filter(email=email).exists():

			myuser = User.objects.get(email = email)

			olApp = win32.Dispatch('Outlook.Application',pythoncom.CoInitialize())
			olNS = olApp.GetNameSpace('MAPI')

			mail_item1 = olApp.createItem(0)

			current_site = get_current_site(request)

			mail_item1.Subject = "Confirm your email for The Big Ballz Leage!"
			mail_item1.BodyFormat = 1
			mail_item1.Body = render_to_string('authentication/email_change.html',{
				'domain' : current_site.domain,
				'uid' : urlsafe_base64_encode(force_bytes(myuser.pk)),
				'token' : generate_token.make_token(myuser),
				})

			mail_item1.Sender = "commissioner@bigballzdfsl.com"
			mail_item1.To = email

			mail_item1.Display()
			mail_item1.Save()
			mail_item1.Send()

			messages.success(request,"We sent password change instructions over email")
			return redirect('forgotPassEmail')
		else:
			messages.error(request,"Please provide a valid email")

	return render(request,'authentication/forgotPassEmail.html')

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
				print("hi")

				return redirect('signin')
			else:
				messages.error("Passwors do not match")
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
		login(request, myuser)
		return redirect('signin')
	else:
		return render(request, 'authentication/activation_failed.html')	

def signsamp(request):
	return render(request,"authentication/signsamp.html")

def playerboard(request):
	player_counts1 = Pick.objects.filter(isin=True).values('pick1').annotate(count=Count('pick1')).order_by('-count')
	player_counts2 = Pick.objects.filter(isin=True).values('pick2').annotate(count=Count('pick2')).order_by('-count')
	
	player_counts = defaultdict(int)

	for player_count in chain(player_counts1, player_counts2):
		player_name = player_count.get('pick1') or player_count.get('pick2')
		player_counts[player_name] += player_count['count']

	sorted_player_counts = sorted(player_counts.items(), key=lambda x: x[1], reverse=True)
	
	total_in = Pick.objects.filter(isin = True).count()

	return render(request,'authentication/playerboard.html',{'player_counts':sorted_player_counts,'total_in':total_in})

@login_required
def leaderboard(request):
	player_counts1 = Pick.objects.filter(isin=True).values('pick1').annotate(count=Count('pick1')).order_by('-count')
	player_counts2 = Pick.objects.filter(isin=True).values('pick2').annotate(count=Count('pick2')).order_by('-count')
	
	player_counts = defaultdict(int)

	for player_count in chain(player_counts1, player_counts2):
		player_name = player_count.get('pick1') or player_count.get('pick2')
		player_counts[player_name] += player_count['count']

	sorted_player_counts = sorted(player_counts.items(), key=lambda x: x[1], reverse=True)
	
	total_in = Pick.objects.filter(isin = True).count()

	user_data = Pick.objects.get(username = request.user.username)

	return render(request,'authentication/leaderboard.html',{'player_counts':sorted_player_counts,'total_in':total_in, 'user_data':user_data})

@login_required
def game(request):
	user_data = Pick.objects.filter(username = request.user.username)
	user_pick = Pick.objects.get(username = request.user.username)
	player_data = []
	error_message = None

	if request.method == 'POST':
		search = request.POST.get('searched')

		if search is not None:
			player_data = NFLPlayer.objects.filter(name__contains=search)[:5]
		
		selected_player = request.POST.get('selected_player')
		try:
			player_data_selected = NFLPlayer.objects.get(name=selected_player)
		except NFLPlayer.DoesNotExist:
			player_data_selected = None 
		try:
			player_data_pick1 = NFLPlayer.objects.get(name=user_pick.pick1)
		except NFLPlayer.DoesNotExist:
			player_data_pick1 = None 
		try:
			player_data_pick2 = NFLPlayer.objects.get(name=user_pick.pick2)
		except NFLPlayer.DoesNotExist:
			player_data_pick2 = None 
		if selected_player is not None:
			if user_pick.pick1 == "N/A" and user_pick.pick2 == "N/A":
				user_pick.pick1 = selected_player
			elif user_pick.pick1 == "N/A":
				if player_data_selected.team_name == player_data_pick2.team_name:
					messages.error(request,"Selected players cannot be on the same team")
				else:
					user_pick.pick1 = selected_player
			else:
				if player_data_selected.team_name == player_data_pick1.team_name:
					messages.error(request,"Selected players cannot be on the same team")
				else:
					user_pick.pick2 = selected_player
			user_pick.save()

		change_pick = request.POST.get('change_pick')
		if change_pick == 'pick1':
			user_pick.pick1 = "N/A"
			user_pick.save()
		elif change_pick == "pick2":
			user_pick.pick2 = "N/A"
			user_pick.save()

	return render(request, 'authentication/game.html', 
		{'player_data': player_data, 
		'error_message': error_message,
		'user_data' : user_data
		})

@login_required
def checking(request):
	if not Paid.objects.filter(username = request.user.username).exists():
		new_user = Paid(username = request.user.username)
		new_user.save()
	paid = Paid.objects.get(username = request.user.username)
	if paid.paid_status == False:
		return render(request,'authentication/pay.html')
	else:
		username = request.user.username
		current_day = datetime.now().weekday()
		if not Pick.objects.filter(username = username).exists():
			return redirect('teamname')
		else:
			user_data = Pick.objects.get(username = username)
			if user_data.isin == True:
				if current_day not in [1,2]:
					return redirect('game')
				else:
					return redirect('leaderboard')
			else:
				return redirect('playerboard')
