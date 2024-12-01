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
from django.template.loader import render_to_string
import requests
from decouple import config
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Pick,Scorer,Paid,PromoCode,PromoUser,OfAge,UserVerification,Waitlist,Message
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
from django.db.models import Sum
import pytz
from django.core.paginator import Paginator
from django.db import models
from ..views import tournaments

def message_board(request):
    # Fetch all messages, ordered by week and timestamp
    messages = Message.objects.order_by('week', '-timestamp')

    # Group messages by week
    grouped_messages = {}
    for message in messages:
        if message.week not in grouped_messages:
            grouped_messages[message.week] = []
        grouped_messages[message.week].append(message)

    return render(request, 'authentication/messages.html', {'grouped_messages': grouped_messages})

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

    
@login_required
def room(request, room_name):
    username = request.user.username
    try:
        paids = Pick.objects.get(username=username, teamnumber=1)
        team = paids.team_name
    except Pick.DoesNotExist:
        team = "No Team"

    # Fetch all chat messages for the room, including their likes and dislikes count
    messages = ChatMessage.objects.filter(room_name=room_name).order_by('timestamp').values(
        'id', 'message', 'team_name', 'timestamp', 'likes_count', 'dislikes_count'
    )

    # Convert the QuerySet to a list of dictionaries
    messages = list(messages)
    
    return render(request, 'authentication/room.html', {
        'room_name': room_name,
        'team': team,
        'messages': messages
    })

def rules(request):
    return render(request,'authentication/rules.html')

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


def signout(request):
    logout(request)
    return redirect('home')

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

def playerboard(request):
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


    if current_day_pst == 3 and current_pst_time <= thursday_deadline:  # Thursday before 5:00 PM PST
        within_deadline = True
    elif current_day_pst in [1, 2]:  # Tuesday or Wednesday
        within_deadline = True
    else:
        within_deadline = False
    
    if (within_deadline) or not (start_datetime <= current_pst_time < end_datetime):
        return redirect('checking')  # Replace 'some_other_page' with the name of an appropriate view

    player_counts1 = Pick.objects.filter(isin=True).exclude(pick1='N/A').values('pick1').annotate(count=Count('pick1')).order_by('-count')
    player_counts2 = Pick.objects.filter(isin=True).exclude(pick2='N/A').values('pick2').annotate(count=Count('pick2')).order_by('-count')

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
        # Get player statuses
    player_status = {}
    for player in player_counts.keys():
        scorer = Scorer.objects.filter(name=player).first()
        if scorer:
            player_status[player] = {
                'scored': scorer.scored,
                'not_scored': scorer.not_scored,
            }
        else:
            player_status[player] = {
                'scored': False,
                'not_scored': False,
            }

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
        'player_status': player_status,
        'total_in': total_in,
    })


    return render(request,'authentication/playerboard.html',{'player_counts':sorted_player_counts,'count':count,'total_in':total_in})

@login_required
def leaderboard(request):
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

    if current_day_pst == 3 and current_pst_time <= thursday_deadline:  # Thursday before 5:00 PM PST
        within_deadline = True
    elif current_day_pst in [1, 2]:  # Tuesday or Wednesday
        within_deadline = True
    else:
        within_deadline = False

    if (within_deadline) or not (start_datetime <= current_pst_time < end_datetime):
        return redirect('checking')  # Replace 'some_other_page' with the name of an appropriate view
    
    player_counts1 = Pick.objects.filter(isin=True).exclude(pick1='N/A').values('pick1').annotate(count=Count('pick1')).order_by('-count')
    player_counts2 = Pick.objects.filter(isin=True).exclude(pick2='N/A').values('pick2').annotate(count=Count('pick2')).order_by('-count')


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

    # Get player statuses
    player_status = {}
    for player in player_counts.keys():
        scorer = Scorer.objects.filter(name=player).first()
        if scorer:
            player_status[player] = {
                'scored': scorer.scored,
                'not_scored': scorer.not_scored,
            }
        else:
            player_status[player] = {
                'scored': False,
                'not_scored': False,
            }



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
        'player_status': player_status,
        'total_in': total_in,
        'user_data': user_data,
    })


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
                        return redirect('checking') #needs to be removed to check age
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

#@login_required
def player_list(request):
    # Create a Subquery to count matching PastPick entries
    past_pick_count = PastPick.objects.filter(
        username=OuterRef('username'),
        teamnumber=OuterRef('teamnumber')
    ).values('username').annotate(count=Count('id')).values('count')

    # Annotate the Picks queryset with the count of past picks
    data = Pick.objects.annotate(
        pick_count=Subquery(past_pick_count, output_field=models.IntegerField())
    ).order_by('-isin', '-pick_count')

    # Fetch all past picks and group them by (username, teamnumber)
    past_picks_map = {}
    for pick in data:
        # Fetch the related past picks for each team
        past_picks = PastPick.objects.filter(username=pick.username, teamnumber=pick.teamnumber)
        past_picks_map[(pick.username, pick.teamnumber)] = past_picks

    # Pass the data to the template
    return render(request, 'authentication/leaders.html', {
        'leaderboard': data,
        'past_picks_map': past_picks_map
    })


@login_required
def game(request):
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

    thursday_deadline = current_pst_time.replace(hour=17, minute=0, second=0, microsecond=0)
    if current_day_pst == 3 and current_pst_time <= thursday_deadline:  # Thursday before 5:00 PM PST
        within_deadline = True
    elif current_day_pst in [1, 2]:  # Tuesday or Wednesday
        within_deadline = True
    else:
        within_deadline = False
    if (not within_deadline and (start_datetime <= current_pst_time < end_datetime)):
        return redirect('checking')  # Replace 'some_other_page' with the name of an appropriate view
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

    user_picks_out = Pick.objects.filter(username=request.user.username, isin=False).order_by('teamnumber')
    user_picks_in = Pick.objects.filter(username=request.user.username, isin=True).order_by('teamnumber')

    all_teams_in = user_picks_out.count() == 0
    all_teams_out = user_picks_in.count() == 0

    if all_teams_in:
        isin = True
    elif all_teams_out:
        isin = False
    else:
        isin = request.GET.get('isin', 'True') == 'True'  # Use the query parameter if mixed

    page_number = request.GET.get('page', 1)  # Default to page 1
    in_paginator = Paginator(user_pick_data,20)
    out_paginator = Paginator(user_picks_out,20)

    user_pick_data = in_paginator.get_page(page_number) if isin else out_paginator.get_page(page_number)


    return render(request, 'authentication/game.html', 
        {'player_data': player_data, 
        'user_pick_data' : user_pick_data,
        'has_started' : has_started,
        'isin': isin,
        'start':start,
        'all_teams_in': all_teams_in,
        'all_teams_out': all_teams_out,
        'page_obj': user_pick_data,
        'team':name,
        'total':total_in,
        'organized_picks': organized_picks
        })

def search_players(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.method == 'GET':
        search_query = request.GET.get('search', '')
        if search_query:
            players = NFLPlayer.objects.filter(name__icontains=search_query)[:5]
            player_list = [{'name': player.name} for player in players]
            return JsonResponse({'players': player_list})
    return JsonResponse({'players': []})

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
                pick.pick1 = playerdata.name
                pick.pick1_team = playerdata.team_name
                pick.pick1_position = playerdata.position
                pick.pick1_color = playerdata.color
                pick.pick1_player_ID = playerdata.player_ID
                pick.pick1_image = playerdata.image
                pick.save()
                return 2
    return 2

def picking(request):
    total_in = Pick.objects.filter(isin = True).count()
    return render(request, 'authentication/picking.html', {'total_in': total_in})

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
        return redirect('picking')
    
    elif paid.paid_status == False and (start_datetime <= current_pst_time < end_datetime) and not within_deadline:
        return redirect('playerboard')
    
    elif paid.paid_status == False:
        return redirect('payment')
    
    elif (paid.paid_status == True) and not (start_datetime <= current_pst_time < end_datetime):
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
                if within_deadline and count > 1 and week != 18:
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
                if within_deadline:
                    return redirect('game')
                else:
                    return redirect('playerboard')

