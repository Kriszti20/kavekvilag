from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import datetime, time
from django.contrib.auth.models import User

#from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from datetime import datetime, time



# Kávézó Modell
class Kavezo(models.Model):
    HANGULATOK = [
        ('nyugodt', 'Nyugodt'),
        ('barátságos', 'Barátságos'),
        ('forgalmas', 'Forgalmas'),
        ('romantikus', 'Romantikus'),
    ]
    ARKATEGORIAK = [
        ('olcsó', 'Olcsó'),
        ('közepes', 'Közepes'),
        ('drága', 'Drága'),
    ]

    nev = models.CharField(max_length=100)
    cim = models.CharField(max_length=255)
    google_place_id = models.CharField(max_length=128, blank=True, null=True, unique=True)
    hangulat = models.CharField(
        max_length=50,
        choices=HANGULATOK,
        default='nyugodt',
        blank=True,
        help_text="Válassza ki a kávézó hangulatát."
    )
    arkategoriak = models.CharField(
        max_length=50,
        choices=ARKATEGORIAK,
        default='közepes',
        blank=True,
        help_text="Pl. alacsony, közepes vagy magas árkategória."
    )

    
    def __str__(self):
        return self.nev


# Nyitvatartás Modell
class Nyitvatartas(models.Model):
    NAPOK = [
        ('hetfo', 'Hétfő'),
        ('kedd', 'Kedd'),
        ('szerda', 'Szerda'),
        ('csutortok', 'Csütörtök'),
        ('pentek', 'Péntek'),
        ('szombat', 'Szombat'),
        ('vasarnap', 'Vasárnap'),
    ]
    kavezo = models.ForeignKey(Kavezo, on_delete=models.CASCADE, related_name="nyitvatartasok")
    nap = models.CharField(max_length=10, choices=NAPOK)
    nyitas = models.TimeField(default=time(8, 0), help_text="Nyitási idő")
    zaras = models.TimeField(default=time(22, 0), help_text="Zárási idő")

    def clean(self):
        if self.nyitas >= self.zaras:
            raise ValidationError("A nyitási idő nem lehet később vagy egyenlő a zárási idővel.")

    def __str__(self):
        return f"{self.kavezo.nev} - {self.get_nap_display()}: {self.nyitas} - {self.zaras}"



# Értékelés Modell
class Ertekeles(models.Model):
    
    felhasznalo = models.ForeignKey(User, on_delete=models.CASCADE)
    kavezo = models.ForeignKey(Kavezo, on_delete=models.CASCADE)
    pontszam = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    megjegyzes = models.TextField(null=True, blank=True)
    datum = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.felhasznalo.username} - {self.kavezo.nev} - {self.pontszam}"

from django.db import models

class Kedvezmeny(models.Model):
    kavezo = models.ForeignKey('Kavezo', on_delete=models.CASCADE, related_name='kedvezmenyek')
    neve = models.CharField(max_length=100)
    leiras = models.TextField()
    ervenyes_tol = models.DateField()
    ervenyes_ig = models.DateField()
    ar_szazalek = models.PositiveIntegerField(null=True, blank=True)  # százalékos kedvezmény
    aktiv = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.neve} ({self.kavezo.nev})"


# Admin Értékelés Modell
class AdminErtekeles(models.Model):
    kavezo = models.ForeignKey(Kavezo, on_delete=models.CASCADE)
    ertekeles = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 11)])
    megjegyzes = models.TextField(blank=True, null=True)
    letrehozas_datum = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.kavezo.nev} - {self.ertekeles}/10"


# Felhasználói Preferenciák Modell
class Preferencia(models.Model):
    felhasznalo = models.OneToOneField(User, on_delete=models.CASCADE)
    kedvenc_kave = models.CharField(
        max_length=255,
        default='Espresso',  # Alapértelmezett érték megadva
        help_text="A felhasználó kedvenc kávéja"
    )
    hangulat = models.CharField(
        max_length=50,
        choices=[
            ('csendes', 'Csendes'),
            ('forgalmas', 'Forgalmas'),
        ],
        default='csendes'
    )
    ar = models.CharField(
        max_length=10,
        choices=[
            ('alacsony', 'Alacsony'),
            ('közepes', 'Közepes'),
            ('magas', 'Magas'),
        ],
        default='közepes'
    )

    def __str__(self):
        return f"{self.felhasznalo.username}"
    
from django.db import models

class Member(models.Model):
    nev = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    csatlakozas_datum = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nev
    
class Foglalas(models.Model):
    felhasznalo = models.ForeignKey(User, on_delete=models.CASCADE)
    kavezo = models.ForeignKey(Kavezo, on_delete=models.CASCADE)
    datum = models.DateTimeField(default=datetime.now)
    szemelyek_szama = models.PositiveIntegerField()
    allapot = models.CharField(
        max_length=20,
        choices=[
            ('függő', 'Függő'),
            ('megerősített', 'Megerősített'),
            ('lemondott', 'Lemondott'),
        ],
        default='függő'
    )
    megjegyzes = models.TextField(blank=True, null=True)  # Új mező

    def __str__(self):
        return f"{self.felhasznalo.username} - {self.kavezo.nev} ({self.datum})"

    
    
    
    from django.db import models

class Termek(models.Model):
    kavezo = models.ForeignKey(Kavezo, on_delete=models.CASCADE, related_name='termekek')
    nev = models.CharField(max_length=255)
    leiras = models.TextField(blank=True, null=True)
    ar = models.DecimalField(max_digits=10, decimal_places=2)
    kategoria = models.CharField(max_length=255, blank=True, null=True)  # Pl. "Kávé", "Sütemény"
    
    def __str__(self):
        return f"{self.nev} )"
    

    
from django.shortcuts import render, get_object_or_404
from .models import Kavezo, Termek

def kavezo_termekek(request, kavezo_id):
    kavezo = get_object_or_404(Kavezo, id=kavezo_id)
    termekek = Termek.objects.filter(kavezo=kavezo)
    return render(request, 'kavezok/kavezo_termekek.html', {
        'kavezo': kavezo,
        'termekek': termekek,
    })
    
class Rendeles(models.Model):
    felhasznalo = models.ForeignKey(User, on_delete=models.CASCADE)
    kavezo = models.ForeignKey(Kavezo, on_delete=models.CASCADE)
    datum = models.DateTimeField(auto_now_add=True)
    termekek = models.ManyToManyField(Termek)

    def __str__(self):
        return f"Rendelés {self.felhasznalo.username} részére ({self.datum})"


from django.db import models

class RendelesTetel(models.Model):
    rendeles = models.ForeignKey(Rendeles, on_delete=models.CASCADE, related_name="tetel_lista")
    termek = models.ForeignKey('Termek', on_delete=models.CASCADE)
    mennyiseg = models.PositiveIntegerField(default=1)
    # Opcionális: ár mentése a rendelés pillanatában
    ar = models.PositiveIntegerField(default=0)

    @property
    def osszeg(self):
        return self.mennyiseg * self.ar



from django.db import models
from django.contrib import admin


class ArKategoria(models.Model):
    nev = models.CharField(max_length=100)  # Pl. 'olcsó', 'közepes', 'drága'

    def __str__(self):
        return self.nev
    
from django.db import models

from django.contrib.auth.models import User

class Kosar(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='kosar')
    # egy felhasználónak csak egy kosara van

#class KosarTetel(models.Model):
 #   kosar = models.ForeignKey(Kosar, on_delete=models.CASCADE, related_name='tetel_lista')
  #  termek = models.ForeignKey(Termek, on_delete=models.CASCADE)
   # mennyiseg = models.PositiveIntegerField(default=1)

# models.py
class KosarTetel(models.Model):
    kosar = models.ForeignKey(Kosar, on_delete=models.CASCADE, related_name='tetel_lista', null=True, blank=True)
    felhasznalo = models.ForeignKey(User, on_delete=models.CASCADE, related_name="kosar_tetelek")
    termek = models.ForeignKey(Termek, on_delete=models.CASCADE)
    mennyiseg = models.PositiveIntegerField(default=1)

    @property
    def osszeg(self):
        return self.termek.ar * self.mennyiseg


from django.db import models

class Kedvezmeny(models.Model):
    kavezo = models.ForeignKey(Kavezo, on_delete=models.CASCADE, related_name="kedvezmenyek", null=True, blank=True)
    nev = models.CharField(max_length=50)
    kod = models.CharField(max_length=32, unique=True)  # EZ a kuponkód, erre keres a rendszer!
    ar_szazalek = models.PositiveIntegerField()         # kedvezmény %-osan
    minimum_osszeg = models.PositiveIntegerField(default=0)  # min. kosárérték
    ervenyes_tol = models.DateField()
    ervenyes_ig = models.DateField()
    aktiv = models.BooleanField(default=True)
    leiras = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nev} ({self.kod})"

class Kupon(models.Model):
    kod = models.CharField(max_length=50, unique=True)
    szazalek = models.PositiveIntegerField(default=0)  # pl. 10 jelent 10%-ot
    aktiv = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.kod} ({self.szazalek}%)"
    
# model.py
from django.db import models
from django.contrib.auth.models import User

from django.db import models
from django.contrib.auth.models import User

class Profil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_points = models.IntegerField(default=0)
    last_spin = models.DateField(null=True, blank=True) 
    utolso_belepes = models.DateField(null=True, blank=True)
    checkin_start = models.DateField(null=True, blank=True)  

    @property
    def pontok(self):
        return self.total_points

    @pontok.setter
    def pontok(self, value):
        self.total_points = value

    def __str__(self):
        return self.user.username

from django.db import models
from django.contrib.auth.models import User

class Pontgyujtes(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_checkin = models.DateField(null=True, blank=True)
    streak = models.PositiveIntegerField(default=0)  # hány nap folyamatosan
    total_points = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.total_points} pont"
    
class Checkin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created = models.DateField()  # <--- csak így!
