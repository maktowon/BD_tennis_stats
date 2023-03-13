from django.shortcuts import render
from django.http import HttpResponse
from .models import Player, Match, Tournament, Stats, Favourite

from django.db.models import Sum
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime

from django.contrib.auth import login, authenticate, logout
from .forms import SignupForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordResetForm
from django.db.models.query_utils import Q
from django.contrib.auth.tokens import default_token_generator
from tenis.token import account_activation_token


def index(request):
    return HttpResponse('hello')


def home(request):
    return render(request, 'tenis/main.html')


def remove(request, pk):
    player = Player.objects.get(player_id=pk)
    delete = Favourite.objects.filter(user=request.user).filter(player=player).first()
    delete.delete()
    return redirect('profile')


def player_selected(request, pk):
    player = Player.objects.get(player_id=int(pk))
    won = Match.objects.filter(winners_id=player).order_by('-tourney_id__date')
    lost = Match.objects.filter(losers_id=player).order_by('-tourney_id__date')

    if request.user is not None:
        added = Favourite.objects.filter(user=request.user, player=player).first() is not None
    else:
        added = False

    if request.method == 'POST':
        if request.user is None:
            return redirect('login')

        if Favourite.objects.filter(user=request.user, player=player).first() is None:
            new = Favourite.objects.create(user=request.user, player=player)
            new.save()
        else:
            delete = Favourite.objects.filter(user=request.user).filter(player=player).first()
            delete.delete()

    if len(won) == 0 or len(lost) == 0:
        return render(request, 'tenis/player.html', {'player': player, 'won': won, 'lost': lost, 'ranking': '-1', 'wins': won.count(),
                                                 'loses': lost.count(),
                                                 'wr': 0,
                                                 'lr': 0,
                                                 'all': won.count() + lost.count(), 'added': added})

    ranking = Stats.objects.filter(match_id=won[0])
    ranking = Stats.objects.filter(match_id=lost[0])
    ranking = ranking.get(player_id=player)
    return render(request, 'tenis/player.html', {'player': player, 'won': won, 'lost': lost,
                                                 'ranking': ranking.player_rank, 'wins': won.count(),
                                                 'loses': lost.count(),
                                                 'wr': round(won.count() / (won.count() + lost.count()) * 100, 2),
                                                 'lr': round(lost.count() / (won.count() + lost.count()) * 100, 2),
                                                 'all': won.count() + lost.count(), 'added': added})


def match_selected(request, pk):
    match = Match.objects.get(match_id=str(pk))
    w = Player.objects.get(player_id=match.winners_id_id)
    l = Player.objects.get(player_id=match.losers_id_id)
    stats = Stats.objects.filter(match_id=match)
    winner_stats = stats.filter(player_id=w)
    winner_stats = winner_stats[0]
    loser_stats = stats.filter(player_id=l)
    loser_stats = loser_stats[0]

    return render(request, 'tenis/match_selected.html', {'match': match, 'wstats': winner_stats, 'lstats': loser_stats})


def tournament_selected(request, pk):
    tournament = Tournament.objects.get(tournament_id=str(pk))
    matches = Match.objects.filter(tourney_id=tournament)
    finals = matches.filter(round='F')
    semi = matches.filter(round='SF')
    qf = matches.filter(round='QF')
    b16 = matches.filter(round='R16')
    b32 = matches.filter(round='R32')
    b64 = matches.filter(round='R64')
    b128 = matches.filter(round='R128')

    sorted_matches = finals | semi | qf | b16 | b32 | b64 | b128
    matches = sorted_matches

    if request.GET.get('b32') is not None:
        matches = matches.filter(round='R32')
    if request.GET.get('b16') is not None:
        matches = matches.filter(round='R16')
    if request.GET.get('qf') is not None:
        matches = matches.filter(round='QF')
    if request.GET.get('sf') is not None:
        matches = matches.filter(round='SF')
    if request.GET.get('f') is not None:
        matches = matches.filter(round='F')

    return render(request, 'tenis/tournament.html', {'matches': matches, 'tid': tournament.tournament_id})


def tournament_list(request):
    loc = request.GET.get('loc')
    year = request.GET.get('year')
    tournaments = Tournament.objects.all().order_by('-level', '-date')
    if loc is not None:
        tournaments = tournaments.filter(location__startswith=loc)
    if year is not None and year != '':
        tournaments = tournaments.filter(date__year=year)
    location = request.GET.get('l')
    surface = request.GET.get('s')
    date = request.GET.get('d')
    level = request.GET.get('lv')
    draw = request.GET.get('dr')
    if location is not None:
        tournaments = tournaments.order_by('location', '-date')
    if surface is not None:
        tournaments = tournaments.order_by('surface', '-date')
    if date is not None:
        tournaments = tournaments.order_by('-date')
    if level is not None:
        tournaments = tournaments.order_by('-level', '-date')
    if draw is not None:
        tournaments = tournaments.order_by('draw_size', '-date')
    if request.GET.get('gs') is not None:
        tournaments = tournaments.filter(level='G')
    if request.GET.get('ao') is not None:
        tournaments = tournaments.filter(location='Australian Open')
    if request.GET.get('rg') is not None:
        tournaments = tournaments.filter(location='Roland Garros')
    if request.GET.get('w') is not None:
        tournaments = tournaments.filter(location='Wimbledon')
    if request.GET.get('uso') is not None:
        tournaments = tournaments.filter(location='US Open')
    if request.GET.get('m') is not None:
        tournaments = tournaments.filter(level='M')
    if request.GET.get('grass') is not None:
        tournaments = tournaments.filter(surface='Grass')
    if request.GET.get('clay') is not None:
        tournaments = tournaments.filter(surface='Clay')
    if request.GET.get('hard') is not None:
        tournaments = tournaments.filter(surface='Hard')
    if request.GET.get('carpet') is not None:
        tournaments = tournaments.filter(surface='Carpet')

    return render(request, 'tenis/tournament_list.html', {'tournaments': tournaments})


def compare_stats(request, p1, p2):
    p1 = Player.objects.get(player_id=int(p1))
    p2 = Player.objects.get(player_id=int(p2))

    p1win = Match.objects.filter(winners_id=p1).filter(losers_id=p2).order_by('tourney_id__date')
    r1 = Stats.objects.filter(player_id=p1).filter(match_id=p1win[0])[0]
    r1 = r1.player_rank
    r2 = Stats.objects.filter(player_id=p2).filter(match_id=p1win[0])[0]
    r2 = r2.player_rank
    p2win = Match.objects.filter(winners_id=p2).filter(losers_id=p1)
    matches = p1win | p2win
    p1win = p1win.count()
    p2win = p2win.count()
    s1 = Stats.objects.none()
    s2 = Stats.objects.none()

    for match in matches:
        qs1 = Stats.objects.filter(player_id=p1).filter(match_id=match)
        s1 = s1 | qs1
        qs2 = Stats.objects.filter(player_id=p2).filter(match_id=match)
        s2 = s2 | qs2

    s1 = s1.aggregate(serve_points=Sum('serve_points'), aces=Sum('aces'), double_faults=Sum('double_faults'),
                      first_serve=Sum('first_serve'), first_won=Sum('first_won'), second_won=Sum('second_won'),
                      bp_faced=Sum('bp_faced'), bp_saved=Sum('bp_saved'))

    s2 = s2.aggregate(serve_points=Sum('serve_points'), aces=Sum('aces'), double_faults=Sum('double_faults'),
                      first_serve=Sum('first_serve'), first_won=Sum('first_won'), second_won=Sum('second_won'),
                      bp_faced=Sum('bp_faced'), bp_saved=Sum('bp_saved'))

    matches = matches.count()

    return render(request, 'tenis/compare_stats.html', {'s1': s1, 's2': s2, 'matches': matches, 'p1': p1, 'p2': p2,
                                                        'p1win': p1win, 'p2win': p2win, 'r1': r1, 'r2': r2})


def player_list(request):
    players = Player.objects.all();
    n = request.GET.get('n')
    s = request.GET.get('s')
    c = request.GET.get('c')
    if n is not None:
        players = players.filter(name__startswith=n)
    if s is not None:
        players = players.filter(surname__startswith=s)
    if c is not None:
        players = players.filter(country=c)
    q1 = request.GET.get('su')
    q2 = request.GET.get('sd')
    if q1 is None and q2 is None:
        players = players.order_by('surname')
    elif q1 is not None:
        players = players.order_by('-birth')
    elif q2 is not None:
        players = players.order_by('birth')
    return render(request, 'tenis/player_list.html', {'players': players})


def login_to(request):
    page = 'login'
    if request.method == 'POST':
        user_name = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user_name = User.objects.get(username=user_name)
        except:
            messages.error(request, "Wrong username or password")
        user_authenticate = authenticate(request, username=user_name, password=password)
        if user_authenticate is not None:
            login(request, user_authenticate)
            return redirect('player_list')
        else:
            messages.error(request, "Wrong username or password !!!")
    context = {'page': page}
    return render(request, 'tenis/login_or_register.html', context)


@login_required(login_url='login')
def logout_my(request):
    logout(request)
    return redirect('home')


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            message = render_to_string('tenis/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return redirect('register_complete')
    else:
        form = SignupForm()
    return render(request, 'tenis/signup.html', {'form': form})


def signup_complete(request):
    return render(request, 'tenis/signup_complete.html')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return HttpResponse('Thank you for your email confirmation. Now you can log in to your account.')
    else:
        return HttpResponse('Activation link is invalid!')


@login_required(login_url='login')
def profile_my(request):
    favs = Favourite.objects.filter(user=request.user)
    return render(request, 'tenis/profile.html', context={'favs': favs})


def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data.get('email')


            associated_users = User.objects.filter(email=data)
            for user in associated_users:

                    mail_subject = "Password Reset Requested"
                    current_site = get_current_site(request)
                    message = render_to_string('tenis/acc_reset_password.html', {
                        "email": user.email,
                        'domain': current_site,
                        'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    })
                    to_email = password_reset_form.cleaned_data.get('email')
                    email = EmailMessage(
                        mail_subject, message, to=[to_email]
                    )
                    email.send()
                    return redirect("password_reset/done/")
    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="tenis/password_reset.html",
                  context={"password_reset_form": password_reset_form})