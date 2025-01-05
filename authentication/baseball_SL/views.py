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
from .models import PickBL,ScorerBL,PaidBL,PromoCodeBL,PromoUserBL,WaitlistBL,MessageBL,PastPickBL,GrandSlamBL
from authentication.models import OfAge,Game,BaseballPlayer,ChatMessage, Pick
from authentication.NFL_weekly_view.models import PickNW
from authentication.forms import CreateTeam
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
from django.db.models.functions import Lower

@login_required
def message_board(request, league_num):
    username = request.user.username
    player = PaidBL.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("baseballSL:message_board", league_num = player.league_number)
    # Fetch all messages, ordered by week and timestamp
    messages = MessageBL.objects.filter(league_number = league_num).order_by('-week', '-timestamp')

    # Group messages by week
    grouped_messages = {}
    for message in messages:
        if message.week not in grouped_messages:
            grouped_messages[message.week] = []
        grouped_messages[message.week].append(message)

    return render(request, 'baseball_SL/messages.html', {
        'grouped_messages': grouped_messages,
        'pay_status':player.paid_status
        })

def custom_csrf_failure_view(request, reason=""):
    # Set an error message to be displayed on the login page
    messages.error(request, "There was an issue with your request. Please sign in again.")
    # Redirect the user back to the login page
    return redirect('baseballSL:signin')  # 'login' should be the name of your login URL

def home(request):
    total_numteams = PaidBL.objects.filter(paid_status=True).aggregate(Sum('numteams'))['numteams__sum']
    if total_numteams is None:
        total_numteams = 0
    return render(request, "authentication/homepage.html",{'total': 200 - total_numteams})

    
@login_required
def room(request, room_name, league_num):
    username = request.user.username
    player = PaidBL.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("baseballSL:room", room_name = "baseball-SL", league_num = player.league_number)
    username = request.user.username
    try:
        paids = PickBL.objects.get(username=username, teamnumber=1,pick_number=1)
        team = paids.team_name
    except PickBL.DoesNotExist:
        team = "No Team"

    # Fetch all chat messages for the room, including their likes and dislikes count
    messages = ChatMessage.objects.filter(room_name=room_name,league_number= league_num).order_by('timestamp').values(
        'id', 'message', 'team_name', 'timestamp', 'likes_count', 'dislikes_count'
    )

    # Convert the QuerySet to a list of dictionaries
    messages = list(messages)
    
    return render(request, 'baseball_SL/room.html', {
        'room_name': room_name,
        'team': team,
        'messages': messages,
        'league_number': league_num,
        'pay_status':player.paid_status
    })

def rules(request):
    return render(request,'authentication/rules.html')

@login_required
def teamname(request):
    print("hi")
    if not Pick.objects.filter(username=request.user.username).exists() or not PickNW.objects.filter(username=request.user.username).exists():
        if request.method == "POST":
            form = CreateTeam(request.POST)
            if form.is_valid():
                team_name = form.cleaned_data['team_name']
                username = request.user.username
                if PickBL.objects.filter(team_name = team_name).exists() or PickNW.objects.filter(team_name = team_name).exists() or Pick.objects.filter(team_name = team_name).exists():
                    messages.error(request,"Team name already exists.")
                    return redirect('baseballSL:teamname' , league_num = league_num)
                elif len(team_name) > 16:
                    messages.error(request,"Team name needs to be less than 15 characters.")
                    return redirect("baseballSL:teamname" , league_num = league_num)
                else:
                    paid = PaidBL.objects.get(username = request.user.username)
                    if paid.paid_status == False:
                        for j in range(3):
                            new_pick = PickBL(team_name=team_name,username= request.user.username,paid = False,pick_number = j+1, teamnumber = 1)
                            new_pick.save()
                    else:
                        teamcount = paid.numteams
                        for i in range(teamcount):
                            for j in range(3):
                                new_pick = PickBL(team_name=team_name,username= request.user.username,paid = True,pick_number = j+1,teamnumber = i+1)
                                new_pick.save()
                    return redirect('baseballSL:checking', league_num = new_pick.league_number)
            else:
                messages.error(request,"Please submit a valid teamname.")
                return redirect('baseballSL:teamname', league_num = league_num)
    else:
        pick = Pick.objects.get(username = request.user.username, teamnumber = 1)
        paid = PaidBL.objects.get(username = request.user.username)
        if paid.paid_status == False:
            for j in range(3):
                new_pick = PickBL(team_name=pick.team_name,username= request.user.username,paid = False,pick_number = j+1, teamnumber = 1)
                new_pick.save()
        return redirect('baseballSL:checking', league_num = new_pick.league_number)

    return render(request,"baseball_SL/teamname.html")


def signout(request):
    logout(request)
    return redirect('baseballSL:home')

@login_required
def payment(request, league_num):
    username = request.user.username
    player = PaidBL.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("baseballSL:payment", league_num = player.league_number)
    user = PromoUserBL.objects.get(username = request.user.username)
    code = user.code
    codeuser = False
    if code != "0000":
        codeuser = True

    if request.method == 'POST':
        promocode = request.POST.get('code',"").strip()
        if not promocode:
            promocode = "0000"
        promouser = PromoUserBL.objects.get(username = request.user.username)
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
        info = PaidBL.objects.get(username = request.user.username)
        info.numteams = team_count
        info.price = total_amount
        info.save()
        username = request.user.username
        note = f"Entry-for-{username}-minigame"

        venmo_url = f"https://venmo.com/thechosenfantasy?txn=pay&amount={total_amount}&note={note}"

        return HttpResponseRedirect(venmo_url)
        #messages.success(request,"Please contact (805)377-6155 or email commissioner@thechosenfg.com for payment options")

    else:
        team_count = 1
        total_amount = 100

    context = {
        'team_count': team_count,
        'total_amount': total_amount,
        'promo':codeuser,
        'pay_status':player.paid_status
        } 
    print(context)

    return render(request, 'baseball_SL/payment.html', context)

@login_required
def playerboard(request, league_num):
    username = request.user.username
    player = PaidBL.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("baseballSL:playerboard", league_num = player.league_number)
    # Define the PST timezone
    pst = pytz.timezone('America/Los_Angeles')

    # Get the current time in PST
    current_pst_time = timezone.now().astimezone(pst)
    current_day_pst = current_pst_time.weekday()  # This gives the day of the week (int)
    current_date_pst = current_pst_time.date()

    game = Game.objects.get(sport="Baseball")
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
        return redirect('baseballSL:checking', league_num = league_num)  # Replace 'some_other_page' with the name of an appropriate view
    """
    pick_counts = PickBL.objects.filter(league_number = league_num).exclude(pick='N/A').values('pick','pick_team', 'pick_position').annotate(count=Count('pick')).order_by('-count')

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
    for pick_record in PickBL.objects.exclude(pick='N/A'):
        pick_teams[pick_record.pick].append(pick_record.team_name)

    player_status = {}
    for pick_name in pick_counts:
        player_name = pick_name['pick']
        scorer = ScorerBL.objects.filter(name=player_name).first()
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

    total_in = int(PickBL.objects.filter(paid = True,league_number = league_num).count() / 10)

    # Paginate sorted_player_counts (show 10 players per page)
    paginator = Paginator(sorted_player_counts, 10)  # Show 10 players per page
    page_number = request.GET.get('page')  # Get the page number from the request URL
    page_obj = paginator.get_page(page_number)  # Get the paginated page


    # Pass both sorted_player_counts and player_teams to the template
    return render(request, 'baseball_SL/playerboard.html', {
        'page_obj': page_obj,
        'sorted_player_counts': sorted_player_counts,
        'player_teams': dict(pick_teams),
        'player_status': player_status,
        'total_in': total_in, })

@login_required
def leaderboard(request, league_num):
    username = request.user.username
    player = PaidBL.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("baseballSL:leaderboard", league_num = player.league_number)
    # Define the PST timezone
    pst = pytz.timezone('America/Los_Angeles')

    # Get the current time in PST
    current_pst_time = timezone.now().astimezone(pst)
    current_day_pst = current_pst_time.weekday()  # This gives the day of the week (int)
    current_date_pst = current_pst_time.date()

    game = Game.objects.get(sport="Baseball")
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
        return redirect('baseballSL:checking', league_num = league_num)  # Replace 'some_other_page' with the name of an appropriate view
    """
    pick_counts = PickBL.objects.filter(league_number = league_num).exclude(pick='N/A').values('pick','pick_team', 'pick_position').annotate(count=Count('pick')).order_by('-count')

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
    for pick_record in PickBL.objects.exclude(pick='N/A'):
        pick_teams[pick_record.pick].append(pick_record.team_name)

    player_status = {}
    for pick_name in pick_counts:
        player_name = pick_name['pick']
        scorer = ScorerBL.objects.filter(name=player_name).first()
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

    total_in = int(PickBL.objects.filter(paid = True,league_number = league_num).count() / 10)

    # Paginate sorted_player_counts (show 10 players per page)
    paginator = Paginator(sorted_player_counts, 10)  # Show 10 players per page
    page_number = request.GET.get('page')  # Get the page number from the request URL
    page_obj = paginator.get_page(page_number)  # Get the paginated page

    user_data= PickBL.objects.filter(username = request.user.username)

    # Pass both sorted_player_counts and player_teams to the template
    return render(request, 'baseball_SL/leaderboard.html', {
        'page_obj': page_obj,
        'sorted_player_counts': sorted_player_counts,
        'player_teams': dict(pick_teams),
        'player_status': player_status,
        'total_in': total_in,
        'user_data': user_data,
    })


@login_required
def location(request, league_num):    
    username = request.user.username
    player = PaidBL.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("baseballSL:location", league_num = player.league_number)
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

        paid = PaidBL.objects.get(username = username)
        compliance = OfAge.objects.get(username = username)
        current_day = timezone.now().date()
        game = Game.objects.get(sport = "Baseball")
        start_date = game.startDate
        end_date = game.endDate
        total_numteams = PaidBL.objects.filter(paid_status=True).aggregate(Sum('numteams'))['numteams__sum']
        if total_numteams is None:
            total_numteams = 0
        if not ((user_state in allowed_states and not is_proxy) or True):
            if is_proxy:
                messages.error(request,"You cannot use a VPN.")
                return redirect('baseballSL:tournaments')
            else:
                messages.error(request,"You are in a disallowed state.")
                return redirect('baseballSL:tournaments')
        else:
            if (start_date <= current_day < end_date):
                return redirect('baseballSL:checking', league_num = league_num)
            else:
                if paid.paid_status == True:
                    return redirect("baseballSL:checking", league_num = league_num)
                else:
                    if total_numteams >= 200:
                        try:
                            Waitlist.objects.get(username = username)
                            messages.error(request,"You are already added to the waitlist.")
                            return redirect('baseballSL:tournaments')
                        except Waitlist.DoesNotExist:
                            waiter = Waitlist(username = username)
                            waiter.save()
                            messages.error(request,"Max number of teams entered, we are adding you to a waitlist.")
                            return redirect('baseballSL:tournaments')
                    else:
                        return redirect('baseballSL:checking', league_num = league_num) #needs to be removed to check age
                        if compliance.old == False and compliance.young == False:
                            age_api_key = config('AGE_API')
                            return render(request,'authentication/agechecking.html',{'api':age_api_key})
                        elif compliance.young == True:
                            messages.error(request,"You are too young to participate.")
                            return redirect("baseballSL:tournaments")
                        else:
                            return redirect('baseballSL:checking', league_num = league_num)

    else:
        messages.error(request,"Failed to register location data.")
        return redirect('baseballSL:tournaments')

@login_required
@csrf_exempt  # Use cautiously, ensure your site is protected against CSRF attacks
def submitverification(request):
    username = request.user.username
    player = PaidBL.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("baseballSL:submitverification", league_num = player.league_number)
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
            return redirect('baseballSL:checking', league_num = league_num)
        else:
            compliance.young = True
            compliance.save()
            return redirect('baseballSL:location', league_num = league_num)

    # If not a POST request, render the form page
    return redirect('baseballSL:checking', league_num = league_num)

@login_required
def player_list(request, league_num):
    username = request.user.username
    player = PaidBL.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("baseballSL:player_list", league_num = player.league_number)
    # Fetch all PickBL entries
    all_picks = PickBL.objects.filter(league_number = league_num, paid = True)

    # Build a dictionary to store team data
    teams_data = defaultdict(lambda: {'team_name': '', 'total_touchdowns': 0, 'picks': []})

    # Iterate through all picks
    for pick in all_picks:
        team_key = (pick.teamnumber, pick.team_name)  # Unique key for each team by teamnumber and team_name
        teams_data[team_key]['team_name'] = pick.team_name
        # Store player names (PickBL.pick) instead of IDs for hover display
        teams_data[team_key]['picks'].append(pick.pick)

    # Fetch all ScorerBL data for lookup
    scorer_data = {scorer.player_ID: scorer.touchdown_count for scorer in ScorerBL.objects.all()}

    # Calculate total touchdowns for each team
    for team_key, team_info in teams_data.items():
        # Filter picks specific to this team and calculate total touchdowns
        total_touchdowns = sum(
            scorer_data.get(pick.pick_player_ID, 0)
            for pick in all_picks
            if pick.team_name == team_info['team_name'] and pick.teamnumber == team_key[0]
        )
        teams_data[team_key]['total_touchdowns'] = total_touchdowns

    # Convert to a sorted list by total_touchdowns in descending order
    sorted_teams = sorted(
        [{'teamnumber': team_key[0], 'team_name': team_key[1], **team_info} for team_key, team_info in teams_data.items()],
        key=lambda x: x['total_touchdowns'],
        reverse=True
    )

    standings = []
    previous_count = None
    current_rank = 1
    for index, item in enumerate(sorted_teams):
        pick_count = item['total_touchdowns']
        if pick_count == 0:
            pick_count = None
        if previous_count == 0:
            previous_count = None
        # Get the next team's pick count
        next_pick_count = sorted_teams[index + 1]['total_touchdowns'] if index + 1 < len(sorted_teams) else None
        if next_pick_count == 0:
            next_pick_count = None
        is_tied_with_previous = pick_count == previous_count
        is_tied_with_next = pick_count == next_pick_count

        # Handle ties
        if is_tied_with_previous or is_tied_with_next:
            if is_tied_with_previous and is_tied_with_next:
                print("1")
                standings.append({"rank": f"T{current_rank}", "team": item})
            elif is_tied_with_previous and not is_tied_with_next:
                print("2")
                standings.append({"rank": f"T{current_rank}", "team": item})
                current_rank = index + 2
            elif not is_tied_with_previous and is_tied_with_next:
                print("3")
                if index + 1 == len(sorted_teams):
                    standings.append({"rank": f"{current_rank}", "team": item})
                else:
                    standings.append({"rank": f"T{current_rank}", "team": item})
        else:
            print("4")
            standings.append({"rank": current_rank, "team": item})
            current_rank += 1

        previous_count = pick_count

    paginator = Paginator(standings, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Pass the data to the template
    return render(request, 'baseball_SL/leaders.html', {
        'leaderboard': page_obj,
        'pay_status':player.paid_status
    })



@login_required
def game(request, league_num):
    username = request.user.username
    player = PaidBL.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("baseballSL:game", league_num = player.league_number)
    # Define the PST timezone
    paid = PaidBL.objects.get(username = request.user.username)
    pst = pytz.timezone('America/Los_Angeles')

    # Get the current time in PST
    current_pst_time = timezone.now().astimezone(pst)
    current_day_pst = current_pst_time.weekday()  # This gives the day of the week (int)
    current_date_pst = current_pst_time.date()

    game = Game.objects.get(sport="Baseball")
    start_date = game.startDate
    end_date = game.endDate
    paid = PaidBL.objects.get(username = request.user.username)

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
        return redirect('baseballSL:checking', league_num = player.league_number)  # Replace 'some_other_page' with the name of an appropriate view
    """
    user_data = PickBL.objects.filter(username = request.user.username)
    user_pick_data = PickBL.objects.filter(username = request.user.username).order_by('teamnumber','pick_number')
    player_data = []
    pick1_data = None
    pick2_data = None

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        selected_player = request.POST.get('selected_player')
        page_num = request.POST.get('currentPage')
        if selected_player:
            try:
                # Retrieve the selected player
                player_data_selected = BaseballPlayer.objects.get(name=selected_player)
                if paid.paid_status == False:
                    return JsonResponse({'success': False, 'message': "Features activate after payment"})
                else:
                    # Use your existing game_search function
                    result = game_search(request.user.username, player_data_selected,page_num)
                    if result == 11:
                        return JsonResponse({'success': False, 'message': "Selected players cannot be on the same team."})
                    elif result == 13:
                        return JsonResponse({'success': False, 'message': "Player already selected."})
                    elif result == 14:
                        return JsonResponse({'success': False, 'message': "Your team is out."})
                    elif result == 15:
                        return JsonResponse({'success': False, 'message': "Player selected last week."})
                    elif result == 16:
                        return JsonResponse({'success': False, 'message': "Player hit a grand slam for you."})
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

            except BaseballPlayer.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Player not found!'})
            except PickBL.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Pick not found!'})
        else:
            return JsonResponse({'success': False, 'message': 'Invalid data!'})

    game = Game.objects.get(sport = "Baseball")
    start = game.startDate
    current_day = timezone.now().date()
    if current_day <= start:
        has_started = False
    else:
        has_started = True
    team = PickBL.objects.get(username = request.user.username, teamnumber = 1, pick_number =1)
    name = team.team_name

    # Group picks by team
    team_picks_dict = defaultdict(list)
    for pick in user_pick_data:
        team_picks_dict[pick.teamnumber].append(pick)

    # Convert to a list of teams with picks
    team_picks_list = list(team_picks_dict.values())

    out_teams = PickBL.objects.filter(username=username, isin=False).values_list('teamnumber', flat=True).distinct()

    # Paginate the team-level data (1 team per page)
    paginator = Paginator(team_picks_list, 1)  # One team per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    total_in = int(PickBL.objects.filter(paid = True,league_number = league_num).count() / 10)


    return render(request, 'baseball_SL/game.html', 
        {'page_obj': page_obj,
        'user_pick_data' : user_pick_data,
        'has_started' : has_started,
        'start':start,
        'team':name,
        'total':total_in,
        'out_teams':out_teams,
        'pay_status':player.paid_status
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

            user_pick_data = PickBL.objects.filter(username=request.user.username)
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
            players = BaseballPlayer.objects.filter(name__icontains=search_query)[:5]
            player_list = [{'name': player.name} for player in players]
            return JsonResponse({'players': player_list})
    return JsonResponse({'players': []})

def game_search(username,playerdata,pagenum):
    game = Game.objects.get(sport="Baseball")
    week = game.week
    user_pick_data = PickBL.objects.filter(username = username,teamnumber = pagenum).order_by('pick_number')
    past_picks = PastPickBL.objects.filter(username = username,teamnumber = pagenum,week = week -1)
    for pick in user_pick_data:
        if pick.pick == 'N/A':
            try:
                team_list = PickBL.objects.filter(username=username, teamnumber=pick.teamnumber).order_by('pick_number').values_list('pick_team', flat=True)
                all_equal = True
                for i, item in enumerate(team_list):
                    if i != int(pick.pick_number) - 1 and item != playerdata.team:
                        all_equal = False
                        break
                ID_list = PickBL.objects.filter(username=username, teamnumber=pick.teamnumber).values_list('pick_player_ID', flat=True)
                past_pick_ID = PastPickBL.objects.filter(username=username, teamnumber=pick.teamnumber,week = week -1).values_list('pick', flat=True)
                slams = GrandSlamBL.objects.filter(username = username, teamnumber = pick.teamnumber).values_list('player_ID', flat=True)
                if all_equal:
                    return 11
                elif playerdata.player_ID in ID_list:
                    return 13
                elif pick.isin == False:
                    return 14
                elif playerdata.player_ID in past_pick_ID:
                    return 15
                elif playerdata.player_ID in slams:
                    return 16
                else:
                    pick.pick = playerdata.name
                    pick.pick_team = playerdata.team
                    pick.pick_position = playerdata.position 
                    pick.pick_color = playerdata.color
                    pick.pick_player_ID = playerdata.player_ID
                    pick.save()
                    return [pick.teamnumber,pick.pick_number,pick.pick,pick.pick_team,pick.pick_position,pick.pick_color,pick.pick_player_ID]
            except BaseballPlayer.DoesNotExist:
                return [pick.teamnumber,pick.pick_number,pick.pick,pick.pick_team,pick.pick_position,pick.pick_color,pick.pick_player_ID]
    for pick in user_pick_data:
        team_list = PickBL.objects.filter(username=username, teamnumber=pick.teamnumber).order_by('pick_number').values_list('pick_team', flat=True)
        all_equal = True
        for i, item in enumerate(team_list):
            if i != int(pick.pick_number) - 1 and item != playerdata.team:
                all_equal = False
                break
        ID_list = PickBL.objects.filter(username=username, teamnumber=pick.teamnumber).values_list('pick_player_ID', flat=True)
        past_pick_ID = PastPickBL.objects.filter(username=username, teamnumber=pick.teamnumber,week = week -1).values_list('pick', flat=True)
        slams = GrandSlamBL.objects.filter(username = username, teamnumber = pick.teamnumber).values_list('player_ID', flat=True)
        if all_equal:
            return 11
        elif playerdata.player_ID in ID_list:
            return 13
        elif pick.isin == False:
            return 14
        elif playerdata.player_ID in past_pick_ID:
            return 15
        elif playerdata.player_ID in slams:
            return 16
        else:
            pick.pick = playerdata.name
            pick.pick_team = playerdata.team
            pick.pick_position = playerdata.position 
            pick.pick_color = playerdata.color
            pick.pick_player_ID = playerdata.player_ID
            pick.save()
            return [pick.teamnumber,pick.pick_number,pick.pick,pick.pick_team,pick.pick_position,pick.pick_color,pick.pick_player_ID]
    return [pick.teamnumber,pick.pick_number,pick.pick,pick.pick_team,pick.pick_position,pick.pick_color,pick.pick_player_ID]

@login_required
def picking(request, league_num):
    username = request.user.username
    player = PaidBL.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("baseballSL:picking", league_num = player.league_number)
    total_in = int(PickBL.objects.filter(paid = True,league_number = league_num).count() / 10)
    return render(request, 'baseball_SL/picking.html', {'total_in': total_in})

@login_required
def checking(request, league_num):
    username = request.user.username
    player = PaidBL.objects.get(username = username)
    if int(league_num) != player.league_number:
        return redirect("baseballSL:checking", league_num = player.league_number)
    if not PaidBL.objects.filter(username=request.user.username).exists():
        new_user = PaidBL(username=request.user.username)
        new_user.save()
        
    paid = PaidBL.objects.get(username=request.user.username)
    count = PickBL.objects.count()
    
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
    
    game = Game.objects.get(sport="Baseball")
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
        return redirect('baseballSL:picking', league_num = league_num)
    
    elif paid.paid_status == False and (start_datetime <= current_pst_time < end_datetime) and not within_deadline:
        return redirect('baseballSL:playerboard', league_num = league_num)
    
    elif not (start_datetime <= current_pst_time < end_datetime):
        username = request.user.username
        if not PickBL.objects.filter(username=username).exists():
            return redirect('baseballSL:teamname')
        return redirect('baseballSL:game', league_num = league_num)
    
    else:
        username = request.user.username
        if not PickBL.objects.filter(username=username).exists():
            return redirect('baseballSL:teamname')
        else:
            user_data = PickBL.objects.filter(username=username)
            if within_deadline:
                return redirect('baseballSL:game', league_num = league_num)
            else:
                return redirect('baseballSL:leaderboard', league_num = league_num)