from django.contrib import admin
from .models import (
    Kavezo, Nyitvatartas, Foglalas, Ertekeles, Kedvezmeny, AdminErtekeles, Preferencia, Termek
)


# Nyitvatartások inline megjelenítése
class NyitvatartasInline(admin.TabularInline):
    model = Nyitvatartas
    extra = 1


# Termékek inline megjelenítése
class TermekInline(admin.TabularInline):
    model = Termek
    extra = 1


# Kávézó admin testreszabása
@admin.register(Kavezo)
class KavezoAdmin(admin.ModelAdmin):
    inlines = [NyitvatartasInline, TermekInline]  # Nyitvatartások és Termékek inline megjelenítése
    list_display = ['id', 'nev', 'cim', 'hangulat', 'arkategoriak']
    search_fields = ['nev', 'cim']
    list_filter = ['hangulat', 'arkategoriak']

    class Media:
        js = (
            "https://maps.googleapis.com/maps/api/js?key=AIzaSyAcygYCWGVfayOaUE9ruTUoi6F7XeyFxn0&libraries=places",  # Google Maps API
            "js/google_maps_autocomplete.js",  # Saját statikus JS fájl
        )


# Foglalás admin testreszabása
@admin.register(Foglalas)
class FoglalasAdmin(admin.ModelAdmin):
    list_display = ['felhasznalo', 'kavezo', 'datum', 'szemelyek_szama', 'allapot']
    search_fields = ['felhasznalo__username', 'kavezo__nev']


# Értékelés admin testreszabása
@admin.register(Ertekeles)
class ErtekelesAdmin(admin.ModelAdmin):
    list_display = ['felhasznalo', 'kavezo', 'pontszam', 'datum']
    search_fields = ['felhasznalo__username', 'kavezo__nev']

from django.contrib import admin
from .models import Kedvezmeny

@admin.register(Kedvezmeny)
class KedvezmenyAdmin(admin.ModelAdmin):
    list_display = ('nev', 'ervenyes_tol', 'ervenyes_ig', 'ar_szazalek', 'aktiv')
    list_filter = ('aktiv',)


# Admin Értékelés admin testreszabása
@admin.register(AdminErtekeles)
class AdminErtekelesAdmin(admin.ModelAdmin):
    list_display = ['kavezo', 'ertekeles', 'letrehozas_datum']
    ordering = ['-letrehozas_datum']


# Preferencia admin testreszabása
@admin.register(Preferencia)
class PreferenciaAdmin(admin.ModelAdmin):
    list_display = ['felhasznalo', 'kedvenc_kave', 'hangulat', 'ar']
    search_fields = ['felhasznalo__username', 'kedvenc_kave']


# Termék admin testreszabása (különálló megjelenítés az adminban)
@admin.register(Termek)
class TermekAdmin(admin.ModelAdmin):
    list_display = ('nev', 'kavezo', 'ar', 'kategoria')  # Termék lista megjelenítése
    search_fields = ('nev', 'kategoria')  # Kereshető mezők
    list_filter = ('kategoria', 'kavezo')  # Szűrés lehetőségek
    
from django.contrib import admin
from .models import Profil

class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points')  # IDE kell, nem a modelbe!

admin.site.register(Profil, ProfilAdmin)

