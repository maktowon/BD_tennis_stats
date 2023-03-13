from django.contrib import admin
from .models import Player, Match, Tournament, Country, Stats, Favourite

admin.site.register(Country)
admin.site.register(Player)
admin.site.register(Tournament)
admin.site.register(Match)
admin.site.register(Stats)
admin.site.register(Favourite)