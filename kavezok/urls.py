from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from .views import porgeto_view
app_name = 'kavezok'

urlpatterns = [
    # Kezdőoldal
    path('', views.index, name='index'),  # Főoldal
    #path('profil/', views.profil, name='profil'),

    # Kávézók
    path('kavezok/', views.kavezo_lista, name='kavezo_lista'),  # Kávézók listázása
    path('kavezo/hozzaadas/', views.kavezo_hozzaadas, name='kavezo_hozzaadas'),  # Új kávézó hozzáadása
    path('kavezo/<int:kavezo_id>/', views.kavezo_reszletek, name='kavezo_reszletek'),  # Kávézó részletei

    # Keresés és ajánlások
    path('kereso/', views.kereso, name='kereso'),  # Keresés nézet
    path('kavezo-ajanlas/', views.kavezo_ajanlas, name='kavezo_ajanlas'),  # Ajánlások

    # Foglalások
    # Értékelések
    path('ertekelesek/', views.ertekelesek_lista, name='ertekelesek_lista'),  # Értékelések listázása
    path('ertekelesek/uj/', views.ertekeles_letrehozas, name='ertekeles_letrehozas'),  # Új értékelés hozzáadása

    # Kedvezmények
    path('kedvezmenyek/', views.kedvezmenyek_lista, name='kedvezmenyek_lista'),  # Kedvezmények listázása
    path('kedvezmenyek/<int:kedvezmeny_id>/', views.kedvezmeny_reszletek, name='kedvezmeny_reszletek'),  # Kedvezmény részletei

    # Preferenciák
    path('preferenciak/', views.preferencia_megtekintes, name='preferencia_megtekintes'),  # Preferenciák megtekintése
    path('preferenciak/szerkesztes/', views.preferencia_szerkesztes, name='preferencia_szerkesztes'),  # Preferenciák szerkesztése



    path('bejelentkezes/', views.egyedi_bejelentkezes, name='bejelentkezes'),
    # Kijelentkezés

    # Regisztráció
    path('regisztracio/', views.regisztracio, name='regisztracio'),

    # Profil oldal
    #path('profil/', views.profil, name='profil'),
    path('profil/szerkesztes/', views.profil_szerkesztes, name='profil_szerkesztes'),  # Profil szerkesztés
    
    
    path('foglalasok/', views.foglalasok_lista, name='foglalasok_lista'),
    path('foglalasok/uj/', views.foglalas_letrehozas, name='foglalas_letrehozas'),
    path('foglalasok/siker/', views.foglalas_siker, name='foglalas_siker'),
    
    path('', views.index, name='index'),
    #path('profil/', views.profil, name='profil'),
    path('foglalas_torles/<int:foglalas_id>/', views.foglalas_torles, name='foglalas_torles'),

    path('kavezo/<int:kavezo_id>/termekek/', views.kavezo_termekek, name='kavezo_termekek'),
    path('kavezo/<int:kavezo_id>/rendeles/', views.rendeles_letrehozas, name='rendeles_letrehozas'),
    path('kijelentkezes/', LogoutView.as_view(next_page='kavezok:index'), name='logout'),
    path('<int:kavezo_id>/', views.kavezo_reszletek, name='kavezo_reszletek'),
    path('<int:kavezo_id>/rendeles/', views.rendeles_letrehozas, name='rendeles_letrehozas'),
    path('termek/rendeles/<int:termek_id>/', views.rendeles_hozzaadas, name='rendeles_hozzaadas'),
    path('rendeles/hozzaadas/<int:termek_id>/', views.rendeles_hozzaadas, name='rendeles_hozzaadas'),
    path('kavezo/<int:kavezo_id>/rendeles/', views.rendeles_letrehozas, name='rendeles_letrehozas'),
    path('kavezo/<int:kavezo_id>/', views.kavezo_reszletek, name='kavezo_reszletek'),
    #path('profil/', views.profil, name='profil'),  
    path('ajanlott-kavezok/', views.ajanlott_kavezok, name='ajanlott_kavezok'),
    #path('kosar/', views.kosar, name='kosar_megjelenitese'),
    path('kosar/', views.kosar_megjelenitese, name='kosar_megjelenitese'),
    path('kosar/hozzaad/<int:termek_id>/', views.kosar_hozzaad, name='kosar_hozzaad'),
    path('kosar/mennyiseg-modositas/<int:tetel_id>/', views.kosar_mennyiseg_modositas, name='kosar_mennyiseg_modositas'),

    path('kosar/torles/<int:tetel_id>/', views.kosar_torles, name='kosar_torles'),
    path('kosar/veglegesites/', views.kosar_veglegesites, name='kosar_veglegesites'),
    path('rendeles_sikeres/', views.rendeles_sikeres, name='rendeles_sikeres'),
    path('api/ajanlott_kavezok/', views.ajanlott_kavezok, name='ajanlott_kavezok'),
    path('api/kavezok_kereso_api', views.kavezok_kereso_api, name='kavezok_kereso_api'),
    path('kavezo/import-google/', views.import_google_kavezo_es_megjelenit, name='import_google_kavezo'),
    path('kavezo/<int:kavezo_id>/', views.kavezo_reszletek, name='kavezo_reszletek'),
    path('kavezo/<int:kavezo_id>/', views.kavezo_reszletek, name='kavezo_reszletek'),

    path('api/google_place_details/', views.google_place_details_api, name='google_place_details_api'),
    

    path('elfelejtett-jelszo/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('elfelejtett-jelszo/email-kuldve/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('checkin/', views.checkin, name='checkin'),
    # urls.py
    path('profil/', views.profil_view, name='profil'),
    path("porgeto/", porgeto_view, name="porgeto"),
]

