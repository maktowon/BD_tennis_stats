from django.db import models
from django.contrib.auth.models import User

class Surface(models.TextChoices):
    GRASS = 'g'
    HARD = 'h'
    CLAY = 'c'


class Draw_Size(models.IntegerChoices):
    D128 = 128
    D64 = 64
    D32 = 32
    D8 = 8
    D4 = 4


class Country(models.Model):
    name = models.CharField(max_length=10, primary_key=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    player_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=10, null=True)
    surname = models.CharField(max_length=10, null=True)
    hand = models.CharField(max_length=1, null=True)
    height = models.IntegerField(null=True)
    birth = models.DateField(null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name + ' ' + self.surname


class Tournament(models.Model):
    tournament_id = models.TextField(primary_key=True)
    location = models.CharField(max_length=30, null=True)
    surface = models.TextField(choices=Surface.choices, null=True)
    draw_size = models.IntegerField(choices=Draw_Size.choices, null=True)
    date = models.DateField(null=True)
    level = models.CharField(max_length=1, null=True)

    def __str__(self):
        return self.location


class Match(models.Model):
    match_id = models.TextField(primary_key=True)
    time = models.IntegerField(null=True)
    tourney_id = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    losers_id = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='loser')
    winners_id = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='winner')
    round = models.TextField(null=True)
    score = models.TextField(null=True)

    def __str__(self):
        return str(self.id)


class Stats(models.Model):
    player_id = models.ForeignKey(Player, on_delete=models.CASCADE)
    match_id = models.ForeignKey(Match, on_delete=models.CASCADE)
    player_points = models.IntegerField(null=True)
    player_rank = models.IntegerField(null=True)
    aces = models.IntegerField(null=True)
    double_faults = models.IntegerField(null=True)
    serve_points = models.IntegerField(null=True)
    first_serve = models.IntegerField(null=True)
    first_won = models.IntegerField(null=True)
    second_won = models.IntegerField(null=True)
    serves_game = models.IntegerField(null=True)
    bp_saved = models.IntegerField(null=True)
    bp_faced = models.IntegerField(null=True)

    def __str__(self):
        return str(self.player_id) + str(self.match_id)


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user.username) + str(self.player.player_id)
