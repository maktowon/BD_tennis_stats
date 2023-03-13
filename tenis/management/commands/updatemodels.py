from django.core.management.base import BaseCommand
import numpy as np
import pandas as pd
from tenis.models import Country, Player, Match, Tournament, Stats, Surface, Draw_Size
from datetime import datetime

class Command(BaseCommand):
    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        country_table = pd.read_csv("~/Documents/rp/pythonProject1/country.csv")
        for country in country_table.ioc:
            c = Country(name=country)
            c.save()

        player_table = pd.read_csv("~/Documents/rp/pythonProject1/player.csv")
        player_table = player_table.reset_index()
        for index, row in player_table.iterrows():
            c = Country.objects.get(name=row.ioc)
            date_tmp = str(int(row.dob))
            date = datetime.strptime(date_tmp, '%Y%m%d')
            p = Player(name=row.name_first, surname=row.name_last, player_id=row.player_id, hand=row.hand, birth=date, country=c, height=row.height)
            p.save()

        tournament_table = pd.read_csv("~/Documents/rp/pythonProject1/tournament.csv")
        tournament_table = tournament_table.reset_index()
        for index, row in tournament_table.iterrows():
            date_tmp = str(int(row.tourney_date))
            date = datetime.strptime(date_tmp, '%Y%m%d')
            t = Tournament(tournament_id=row.tourney_id, location=row.tourney_name, surface=row.surface, draw_size=row.draw_size, date=date, level=row.tourney_level)
            t.save()

        match_table = pd.read_csv("~/Documents/rp/pythonProject1/match.csv")
        match_table = match_table.reset_index()
        for index, row in match_table.iterrows():
            loser_id = Player.objects.get(player_id=row.loser_id)
            winner_id = Player.objects.get(player_id=row.winner_id)
            tourney_id = Tournament.objects.get(tournament_id=row.tourney_id)
            m = Match(match_id=row.match_num, time=row.minutes, tourney_id=tourney_id, losers_id=loser_id, winners_id=winner_id, round=row.round_num, score=row.score)
            m.save()

        stats_table = pd.read_csv("~/Documents/rp/pythonProject1/stat.csv")
        stats_table = stats_table.fillna(0)
        for index, row in stats_table.iterrows():
            player_id = Player.objects.get(player_id=row.id)
            match_id = Match.objects.get(match_id=row.match_num)
            pts = int(float(row.rank_points))
            ranking = int(float(row['rank']))
            ace = int(float(row.ace))
            df = int(float(row.df))
            svpt = int(float(row.svpt))
            fin = int(float(row.firstIn))
            fwon = int(float(row.firstWon))
            swon = int(float(row.secondWon))
            svgms = int(float(row.SvGms))
            bpS = int(float(row.bpSaved))
            bpF = int(float(row.bpFaced))

            s = Stats(player_id=player_id, match_id=match_id, player_points=pts, player_rank=ranking, aces=ace, double_faults=df, serve_points=svpt, first_serve=fin, first_won=fwon, second_won=swon, serves_game=svgms, bp_faced=bpF, bp_saved=bpS)
            s.save()
