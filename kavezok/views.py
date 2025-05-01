from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import Kavezo, Foglalas, Ertekeles, Kedvezmeny, KosarTetel, RendelesTetel, Preferencia, Nyitvatartas, Rendeles, Kosar, Profil, Checkin, Termek
from .forms import KavezoForm, FoglalasForm, ErtekelesForm, PreferenciaForm, SajátRegisztrációsForm
from datetime import timedelta
import requests
from .utils import get_nearby_cafes 
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Avg
from django.urls import reverse
import random
from django.contrib import messages
def index(request):
    return render(request, 'kavezok/index.html', {})
def kavezo_ajanlas(request):
    if request.method == "GET":
        helyszin = request.GET.get("helyszin")
        kavezok = Kavezo.objects.all()
        if helyszin:
            kavezok = kavezok.filter(cim__icontains=helyszin)
        kavezo_list = [
            {
                "nev": k.nev,
                "cim": k.cim,
                "hangulat": k.hangulat,
                "arkategoriak": k.arkategoriak,
                "nyitvatartas": [
                    {
                        "nap": nyitvatartas.get_nap_display(),
                    }
                    for nyitvatartas in k.nyitvatartasok.all()
                ],
            }
            for k in kavezok
        ]
        return JsonResponse({"kavezok": kavezo_list}, safe=False)
    return JsonResponse({"error": "Csak GET metódus támogatott"}, status=400)

def kavezo_lista(request):
    helyszin = request.GET.get('helyszin', '') 
    arkategoria = request.GET.get('arkategoria', '')
    hangulat = request.GET.get('hangulat', '')  
    kavezok = Kavezo.objects.all()
    if helyszin:
        kavezok = kavezok.filter(cim__icontains=helyszin)
    if arkategoria:
        kavezok = kavezok.filter(arkategoriak__icontains=arkategoria)
    if hangulat:
        kavezok = kavezok.filter(hangulat__icontains=hangulat)

    return render(request, 'kavezok/kavezo_lista.html', {'kavezok': kavezok})

@login_required
def kavezo_hozzaadas(request):
    if request.method == 'POST':
        form = KavezoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('kavezok:kavezo_lista')
    else:
        form = KavezoForm()
    return render(request, 'kavezok/kavezo_hozzaadas.html', {'form': form})

def kavezo_reszletek(request, kavezo_id):
    kavezo = get_object_or_404(Kavezo, id=kavezo_id)
    nyitvatartasok = Nyitvatartas.objects.filter(kavezo=kavezo).order_by('nap')
    return render(request, 'kavezok/kavezo_reszletek.html', {
        'kavezo': kavezo,
        'nyitvatartasok': nyitvatartasok,
    })
from django.urls import reverse_lazy

@login_required(login_url=reverse_lazy('kavezok:bejelentkezes'))   # vagy a sima útvonal pl. '/bejelentkezes/'
def foglalas_letrehozas(request):
    if request.method == 'POST':
        form = FoglalasForm(request.POST)
        if form.is_valid():
            foglalas = form.save(commit=False)
            if foglalas.szemelyek_szama <= 0:
                form.add_error('szemelyek_szama', "A férőhelyek száma legyen több, mint nulla.")
                return render(request, 'kavezok/foglalas_letrehozas.html', {'form': form})
            foglalas.felhasznalo = request.user
            foglalas.save()
            return redirect('kavezok:foglalas_siker')
    else:
        form = FoglalasForm()
    return render(request, 'kavezok/foglalas_letrehozas.html', {'form': form})

@login_required
def foglalasok_lista(request):
    foglalasok = Foglalas.objects.filter(felhasznalo=request.user)
    return render(request, 'kavezok/foglalasok_lista.html', {'foglalasok': foglalasok})

def foglalas_siker(request):
    return render(request, 'kavezok/foglalas_siker.html')

@login_required
def ertekeles_letrehozas(request):
    if request.method == 'POST':
        form = ErtekelesForm(request.POST)
        if form.is_valid():
            ertekeles = form.save(commit=False)
            ertekeles.felhasznalo = request.user
            ertekeles.save()
            return redirect('kavezok:ertekelesek_lista')
    else:
        form = ErtekelesForm()
    return render(request, 'kavezok/ertekeles_letrehozas.html', {'form': form})


def ertekelesek_lista(request):
    ertekelesek = Ertekeles.objects.order_by('-datum')
    return render(request, 'kavezok/ertekelesek_lista.html', {'ertekelesek': ertekelesek})

def kedvezmenyek_lista(request):
    kedvezmenyek = Kedvezmeny.objects.filter(
        ervenyes_tol__lte=now().date(),
        ervenyes_ig__gte=now().date(),
        aktiv=True
    )
    return render(request, 'kavezok/kedvezmenyek_lista.html', {'kedvezmenyek': kedvezmenyek})

def kedvezmeny_reszletek(request, kedvezmeny_id):
    kedvezmeny = get_object_or_404(Kedvezmeny, id=kedvezmeny_id)
    return render(request, 'kavezok/kedvezmeny_reszletek.html', {'kedvezmeny': kedvezmeny})

@login_required
def preferencia_szerkesztes(request):
    preferencia, created = Preferencia.objects.get_or_create(felhasznalo=request.user)
    if request.method == 'POST':
        form = PreferenciaForm(request.POST, instance=preferencia)
        if form.is_valid():
            form.save()
            return redirect('kavezok:preferencia_megtekintes')
    else:
        form = PreferenciaForm(instance=preferencia)
    return render(request, 'kavezok/preferencia_szerkesztes.html', {'form': form})

@login_required
def preferencia_megtekintes(request):
    preferencia = get_object_or_404(Preferencia, felhasznalo=request.user)
    return render(request, 'kavezok/preferencia_megtekintes.html', {'preferencia': preferencia})

def egyedi_bejelentkezes(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('kavezok:profil')
        else:
            return render(request, 'kavezok/bejelentkezes.html', {
                'error_message': 'Hibás felhasználónév vagy jelszó.'
            })
    return render(request, 'kavezok/bejelentkezes.html')

def regisztracio(request):
    if request.method == 'POST':
        form = SajátRegisztrációsForm(request.POST)
        if form.is_valid():
            form.save()
            # bejelentkeztetheted is automatikusan itt, ha akarod, majd redirect
            return redirect('kavezok:bejelentkezes')
    else:
        form = SajátRegisztrációsForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profil_szerkesztes(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()
        messages.success(request, "Profilod frissítve!")
        return redirect('kavezok:profil')
    return render(request, 'kavezok/profil_szerkesztes.html', {'user': request.user})

def kereso(request):
    return render(request, 'kavezok/kereso.html')

@login_required
def profil(request):
    foglalasok = Foglalas.objects.filter(felhasznalo=request.user).select_related('kavezo').order_by('-datum')
    rendelesek = Rendeles.objects.filter(felhasznalo=request.user).prefetch_related('termekek__kavezo').order_by('-datum') 
    return render(request, 'kavezok/profil.html', {
        'user': request.user,
        'foglalasok': foglalasok,
        'rendelesek': rendelesek,
    })
    
@login_required
def foglalas_torles(request, foglalas_id):
    foglalas = get_object_or_404(Foglalas, id=foglalas_id, felhasznalo=request.user)
    foglalas.delete()
    return HttpResponseRedirect(reverse('kavezok:profil'))

@login_required
def rendeles_letrehozas(request, kavezo_id):
    kavezo = get_object_or_404(Kavezo, id=kavezo_id)
    if request.method == 'POST':
        termek_ids = request.POST.getlist('termekek')
        if termek_ids:
            rendeles = Rendeles.objects.create(felhasznalo=request.user, kavezo=kavezo)
            for termek_id in termek_ids:
                rendeles.termekek.add(termek_id)
            rendeles.save()
            return HttpResponseRedirect(reverse('kavezok:profil'))
    return HttpResponseRedirect(reverse('kavezok:kavezo_termekek', kwargs={'kavezo_id': kavezo_id}))

@login_required
def profil(request):
    foglalasok = Foglalas.objects.filter(felhasznalo=request.user)\
                                 .select_related('kavezo')\
                                 .order_by('-datum')
    rendelesek = Rendeles.objects.filter(felhasznalo=request.user)\
                                 .prefetch_related('termekek')\
                                 .order_by('-datum')
    ertekelesek = Ertekeles.objects.filter(felhasznalo=request.user)\
                                   .select_related('kavezo')\
                                   .order_by('-datum')
    return render(request, 'kavezok/profil.html', {
        'user': request.user,
        'foglalasok': foglalasok,
        'rendelesek': rendelesek,
        'ertekelesek': ertekelesek,
    })

def kavezo_termekek(request, kavezo_id):
    kavezo = get_object_or_404(Kavezo, id=kavezo_id)
    termekek = Termek.objects.filter(kavezo=kavezo)
    return render(request, 'kavezok/kavezo_termekek.html', {
        'kavezo': kavezo,
        'termekek': termekek,
    })

def kavezo_ajanlas(request):
    helyszin = request.GET.get('helyszin')
    arkategoria = request.GET.get('arkategoria')
    hangulat = request.GET.get('hangulat')
    kavezok = Kavezo.objects.all()
    if helyszin:
        kavezok = kavezok.filter(cim__icontains=helyszin)
    if arkategoria:
        kavezok = kavezok.filter(arkategoriak__icontains=arkategoria)
    if hangulat:
        kavezok = kavezok.filter(hangulat__icontains=hangulat)
    return render(request, 'kavezok/ajanlas.html', {'kavezok': kavezok})

@login_required
def rendeles_hozzaadas(request, termek_id):
    termek = get_object_or_404(Termek, id=termek_id)
    rendeles, created = Rendeles.objects.get_or_create(
        felhasznalo=request.user,
        defaults={'kavezo': termek.kavezo}
    )
    rendeles.termekek.add(termek)
    rendeles.save()
    return redirect('kavezok:kavezo_reszletek', termek.kavezo.id)

@login_required
def rendeles_letrehozas(request, kavezo_id):
    kavezo = get_object_or_404(Kavezo, id=kavezo_id)
    termekek = Termek.objects.filter(kavezo=kavezo)
    if request.method == 'POST':
        termekek_ids = request.POST.getlist('termekek')
        if termekek_ids:
            rendeles = Rendeles.objects.create(
                felhasznalo=request.user, 
                kavezo=kavezo
            )
            rendeles.termekek.add(*termekek_ids)
            rendeles.save()
            return redirect('kavezok:profil')
        else:
            return render(request, 'kavezok/rendeles_hiba.html', {'kavezo': kavezo, 'termekek': termekek})
    return render(request, 'kavezok/rendeles_letrehozas.html', {
        'kavezo': kavezo,
        'termekek': termekek
    })

def ajanlott_kavezok(request):
    try:
        kavezok = Kavezo.objects.all()
        ajanlott_kavezok = random.sample(list(kavezok), min(4, len(kavezok))) if kavezok else []
    except Exception as e:
        print("Hiba az ajánlott kávézók lekérdezésekor:", e)
        ajanlott_kavezok = []
    return render(request, 'kavezok/ajanlott_kavezok.html', {
        'ajanlott_kavezok': ajanlott_kavezok,
    })

def kavezo_reszletek(request, kavezo_id):
    kavezo = get_object_or_404(Kavezo, id=kavezo_id)
    termekek = Termek.objects.filter(kavezo=kavezo)
    ertekelesek = Ertekeles.objects.filter(kavezo=kavezo)
    atlagpontszam = ertekelesek.aggregate(atlag=Avg("pontszam"))["atlag"]
    ma = timezone.now().date()
    kedvezmenyek = kavezo.kedvezmenyek.filter(
        aktiv=True, ervenyes_tol__lte=ma, ervenyes_ig__gte=ma
    )
    error_message = None
    if request.method == "POST":
        form = ErtekelesForm(request.POST)
        print("DEBUG ERTEKELESFORM FIELDS (POST):", form.fields)
        if form.is_valid():
            ertekeles = form.save(commit=False)
            ertekeles.kavezo = kavezo
            if request.user.is_authenticated:
                ertekeles.felhasznalo = request.user
            ertekeles.save()
            return redirect("kavezok:kavezo_reszletek", kavezo_id=kavezo.id)
        else:
            error_message = "Minden mezőt ki kell tölteni!"
    else:
        form = ErtekelesForm()
        print("DEBUG ERTEKELESFORM FIELDS (GET):", form.fields)
    return render(request, "kavezok/kavezo_reszletek.html", {
        "kavezo": kavezo,
        "termekek": termekek,
        "ertekelesek": ertekelesek,
        "atlagpontszam": atlagpontszam,
        "kedvezmenyek": kedvezmenyek,
        "error_message": error_message,
        "form": form,
    })

def kosar_hozzaad(request, termek_id):
    kosar, created = Kosar.objects.get_or_create(user=request.user)
    termek = get_object_or_404(Termek, id=termek_id)
    tetel, created = KosarTetel.objects.get_or_create(
        kosar=kosar,
        termek=termek,
        felhasznalo=request.user,
    )
    if not created:
        tetel.mennyiseg += 1
        tetel.save()
    return redirect('kavezok:kosar_megjelenitese')

@login_required
def kosar_veglegesites(request):
    tetelek = KosarTetel.objects.filter(felhasznalo=request.user)
    if not tetelek.exists():
        return render(request, 'kavezok/kosar.html', {
            "hiba": "A kosár üres!",
            "tetelek": tetelek,
        })
    kavezok = set(tetel.termek.kavezo for tetel in tetelek)
    if len(set(tetel.termek.kavezo_id for tetel in tetelek)) > 1:
        nev_lista = ", ".join(set(tetel.termek.kavezo.nev for tetel in tetelek))
        hiba = f"Több kávézóból ({nev_lista}) származó tétel van a kosárban, egyszerre csak egyből rendelhetsz!"
    if len(kavezok) > 1:
        return render(request, 'kavezok/kosar.html', {
                "hiba": "Több kávézóból nem lehet egyszerre rendelni!",
                "tetelek": tetelek,
            })
    if not request.user.email:
        messages.error(request, "A rendeléshez meg kell adnod egy e-mail címet a profilodban!")
        profil_url = reverse('kavezok:profil_szerkesztes')
        return redirect(f'{profil_url}?next={request.path}')
    kavezo = tetelek[0].termek.kavezo
    kedvezmeny_adatok = request.session.get('kedvezmeny')
    kedvezmeny_osszeg = 0
    kedvezmeny_nev = ""
    if kedvezmeny_adatok:
        kedvezmeny_osszeg = kedvezmeny_adatok.get('kedvezmeny_osszeg', 0)
        kedvezmeny_nev = kedvezmeny_adatok.get('nev', '')
    profil = request.user.profil
    pontlevonas = request.session.get("pontlevonas", 0)
    pontlevonas = int(pontlevonas) if pontlevonas else 0
    with transaction.atomic():
        rendeles = Rendeles.objects.create(felhasznalo=request.user, kavezo=kavezo)
        osszeg = 0
        for tetel in tetelek:
            rendeles_tetel = RendelesTetel.objects.create(
                rendeles=rendeles,
                termek=tetel.termek,
                mennyiseg=tetel.mennyiseg,
                ar=tetel.termek.ar
            )
            osszeg += rendeles_tetel.osszeg
        fizetendo = max(osszeg - kedvezmeny_osszeg, 0)
        if pontlevonas and pontlevonas > 0:
            if profil.pontok >= pontlevonas:
                profil.pontok -= pontlevonas
                profil.save()
                fizetendo = max(fizetendo - pontlevonas, 0)
            if "pontlevonas" in request.session:
                del request.session["pontlevonas"]
        rendeles.osszesen = fizetendo
        rendeles.save()
        tetelek.delete()
        request.session.pop('kedvezmeny', None)
        if 'kedvezmeny_tipus' in request.session:
            request.session.pop('kedvezmeny_tipus')
        if 'kedvezmeny_nev' in request.session:
            request.session.pop('kedvezmeny_nev')
    szoveg = f"Szia {request.user.username}! Köszönjük a rendelésed.\n\n"
    for tetel in rendeles.tetel_lista.all():
        szoveg += (
            f"- {tetel.termek.nev} x {tetel.mennyiseg} db, ár: {tetel.ar} Ft/db, összesen: {tetel.osszeg} Ft\n"
        )
    szoveg += f"\nEredeti összeg: {osszeg:.2f} Ft"
    if kedvezmeny_osszeg:
        if kedvezmeny_nev:
            szoveg += f"\nKedvezmény típusa: {kedvezmeny_nev}"
        szoveg += f"\nKedvezmény összege: -{kedvezmeny_osszeg} Ft"
    if pontlevonas:
        szoveg += f"\nElhasznált pontjaid: -{pontlevonas} Ft"
    szoveg += f"\nÖsszesen fizetendő: {fizetendo:.2f} Ft\n\nÜdvözlettel: Kávézó csapata"
    send_mail(
        'Rendelés visszaigazolása',
        szoveg,
        settings.DEFAULT_FROM_EMAIL,
        [request.user.email],
    )
    return redirect('kavezok:rendeles_sikeres')

def kosar_mennyiseg_modositas(request, tetel_id):
    tetel = get_object_or_404(KosarTetel, id=tetel_id, felhasznalo=request.user)
    if request.method == "POST":
        uj_mennyiseg = int(request.POST.get('mennyiseg', 1))
        if uj_mennyiseg > 0:
            tetel.mennyiseg = uj_mennyiseg
            tetel.save()
        else:
            tetel.delete()
        akt_kedvezmeny = request.session.get('kedvezmeny', None)
        if akt_kedvezmeny:
            tetelek = KosarTetel.objects.filter(felhasznalo=request.user)
            ossz_ar = sum(t.termek.ar * t.mennyiseg for t in tetelek)
            kod = akt_kedvezmeny['kod']
            uj_ar, kedvezmeny_osszeg, uzenet, kedvezmeny_nev = apply_discount(ossz_ar, kod)
            request.session['kedvezmeny'] = {
                'kod': kod,
                'kedvezmeny_osszeg': kedvezmeny_osszeg,
                'uzenet': uzenet,
                'nev': kedvezmeny_nev or "",
            }
        return redirect('kavezok:kosar_megjelenitese')

def kosar_torles(request, tetel_id):
    tetel = get_object_or_404(KosarTetel, id=tetel_id)
    if request.method == "POST":
        tetel.delete()
    return redirect('kavezok:kosar_megjelenitese')

def rendeles_sikeres(request):
    return render(request, "kavezok/rendeles_sikeres.html")

def apply_discount(ossz_ar, kod):
    today = timezone.now().date()
    kedvezmeny = Kedvezmeny.objects.filter(
        kod__iexact=kod,
        aktiv=True,
        ervenyes_tol__lte=today,
        ervenyes_ig__gte=today
    ).first()
    if not kedvezmeny:
        return ossz_ar, 0, "Nincs ilyen, vagy érvénytelen kedvezménykód.", "" 
    if ossz_ar < kedvezmeny.minimum_osszeg:
        return ossz_ar, 0, "A kosár értéke nem éri el a kedvezmény minimumát.", kedvezmeny.nev if kedvezmeny else ""
    kedvezmeny_osszeg = int(ossz_ar * kedvezmeny.ar_szazalek / 100)
    uj_ar = ossz_ar - kedvezmeny_osszeg
    return uj_ar, kedvezmeny_osszeg, f"Kedvezmény aktiválva! (-{kedvezmeny_osszeg} Ft)", kedvezmeny.nev

def kosar_megjelenitese(request):
    if not request.user.is_authenticated:
        return render(request, "kavezok/kosar.html", {"login_required": True})
    kosar, _ = Kosar.objects.get_or_create(user=request.user)
    tetelek = kosar.tetel_lista.all()
    ossz_ar = sum(tetel.osszeg for tetel in tetelek) if tetelek else 0
    kavezok = set(tetel.termek.kavezo.id for tetel in tetelek)
    hiba = None
    if len(kavezok) > 1:
        hiba = "Figyelem! Több kávézóból is van termék a kosárban. Ezeket csak külön-külön tudod majd megrendelni!"
    if request.method == "POST" and "kedvezmeny_kod" in request.POST:
        kod = request.POST.get("kedvezmeny_kod", "").strip()
        if kod:
            uj_ar, kedvezmeny_osszeg, uzenet, kedvezmeny_nev = apply_discount(ossz_ar, kod)
            request.session["kedvezmeny"] = {
                "kod": kod,
                "kedvezmeny_osszeg": kedvezmeny_osszeg,
                "uzenet": uzenet,
                "nev": kedvezmeny_nev or "",
            }
        else:
            request.session.pop("kedvezmeny", None)
        return redirect("kavezok:kosar_megjelenitese")
    akt_kedvezmeny = request.session.get("kedvezmeny", None)
    kedvezmeny_osszeg = akt_kedvezmeny["kedvezmeny_osszeg"] if akt_kedvezmeny else 0
    kedvezmeny_uzenet = akt_kedvezmeny["uzenet"] if akt_kedvezmeny else ""
    kedvezmeny_nev = akt_kedvezmeny["nev"] if akt_kedvezmeny else ""
    fizetendo_ar = ossz_ar - kedvezmeny_osszeg
    profil = request.user.profil
    pontjaid = profil.pontok
    levont_pont = request.session.get("pontlevonas", 0)
    max_levonhato_pont = min(pontjaid + levont_pont, int(fizetendo_ar // 2))
    if request.method == "POST":
        if "pontlevonas" in request.POST:
            try:
                igenyelt_pont = int(request.POST.get("pont_osszeg", "0"))
            except (TypeError, ValueError):
                igenyelt_pont = 0
            igenyelt_pont = max(1, min(igenyelt_pont, max_levonhato_pont))
            if levont_pont == 0 and igenyelt_pont > 0:
                request.session["pontlevonas"] = igenyelt_pont
            return redirect("kavezok:kosar_megjelenitese")
        if "pontlevonas_torles" in request.POST:
            if levont_pont > 0:
                request.session.pop("pontlevonas", None)
            return redirect("kavezok:kosar_megjelenitese")
    levont_pont = request.session.get("pontlevonas", 0)
    ponttal_csokkentett_ar = max(fizetendo_ar - levont_pont, 0)
    pontlevonas_uzenet = ""
    if levont_pont:
        pontlevonas_uzenet = f"Rendeléskor {levont_pont} pontot fogunk levonni, az új végösszeg: {ponttal_csokkentett_ar} Ft."
    return render(request, "kavezok/kosar.html", {
        "tetelek": tetelek,
        "ossz_ar": ossz_ar,
        "kedvezmeny_osszeg": kedvezmeny_osszeg,
        "kedvezmeny_nev": kedvezmeny_nev,
        "kedvezmeny_uzenet": kedvezmeny_uzenet,
        "fizetendo_ar": fizetendo_ar,
        "hiba": hiba,
        "pontjaid": profil.pontok,
        "max_levonhato_pont": max_levonhato_pont,
        "levont_pont": levont_pont,
        "ponttal_csokkentett_ar": ponttal_csokkentett_ar,
        "pontlevonas_uzenet": pontlevonas_uzenet,
        "login_required": False,
    })
    
def ajanlott_kavezok(request):
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    print("Lekért pozíció:", lat, lng)
    if not lat or not lng:
        return JsonResponse({'error': 'Hiányzó GPS koordináta!'}, status=400)
    cafes = get_nearby_cafes(lat, lng)
    print("Talált kávézók:", cafes)
    cafes = sorted(cafes, key=lambda c: c.get("rating", 0), reverse=True)
    return JsonResponse({'kavezok': cafes})

def kavezok_kereso_api(request):
    nev = request.GET.get('nev', '').strip()
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    arszint = request.GET.get('arszint', '').strip()
    min_rating = request.GET.get('min_rating', '').strip()
    api_key = 'AIzaSyAcygYCWGVfayOaUE9ruTUoi6F7XeyFxn0'
    if not (nev or lat or lng or arszint or min_rating):
        return JsonResponse({'error': 'Hiányzó paraméter!'}, status=400)
    if lat and lng:
        url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={lat},{lng}&radius=6000&type=cafe&language=hu&key={api_key}"
        )
        if nev:
            url += f"&keyword={requests.utils.quote(nev)}"
        resp = requests.get(url)
    elif nev:
        url = (
            f"https://maps.googleapis.com/maps/api/place/textsearch/json"
            f"?query={requests.utils.quote(nev)}&type=cafe&language=hu&key={api_key}"
        )
        resp = requests.get(url)
    else:
        default_lat, default_lng = "47.4979", "19.0402"
        url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={default_lat},{default_lng}&radius=6000&type=cafe&language=hu&key={api_key}"
        )
        resp = requests.get(url)
    data = resp.json()
    eredmenyek = data.get('results', [])
    if arszint:
        arszint_map = {
            'olcso': 1,
            'kozepes': 2,
            'draga': 3
        }
        price_val = arszint_map.get(arszint)
        if price_val is not None:
            eredmenyek = [k for k in eredmenyek if k.get('price_level') == price_val]
    if min_rating:
        try:
            rating_val = float(min_rating)
            eredmenyek = [k for k in eredmenyek if k.get('rating', 0) >= rating_val]
        except ValueError:
            pass

    data['results'] = eredmenyek
    return JsonResponse(data)

def import_google_kavezo_es_megjelenit(request):
    place_id = request.GET.get('place_id')
    nev = request.GET.get('nev')
    cim = request.GET.get('cim')
    if not place_id:
        return redirect('kavezok:kavezo_ajanlas')
    kavezo, created = Kavezo.objects.get_or_create(
        google_place_id=place_id,
        defaults={
            'nev': nev or 'Ismeretlen név',
            'cim': cim or 'Ismeretlen cím'
        }
    )
    if not created and cim and kavezo.cim != cim:
        kavezo.cim = cim
        kavezo.save()

    return redirect('kavezok:kavezo_reszletek', kavezo_id=kavezo.id)

def google_place_details_api(request):
    place_id = request.GET.get('place_id')
    if not place_id:
        return JsonResponse({'error': 'place_id missing'}, status=400)
    # ADJ MEG IGAZI kulcsot!
    api_key = 'AIzaSyAcygYCWGVfayOaUE9ruTUoi6F7XeyFxn0'
    url = (
        'https://maps.googleapis.com/maps/api/place/details/json'
        f'?place_id={place_id}&language=hu&key={api_key}'
    )
    resp = requests.get(url)
    return JsonResponse(resp.json())

PONTOK_HETRE = [1, 3, 5, 5, 14, 10, 20]

def hetinapok():
    """Adott hét hétfőtől vasárnapig napjai (date lista)"""
    today = timezone.localdate()
    start_of_week = today - timedelta(days=today.weekday())
    return [start_of_week + timedelta(days=i) for i in range(7)]

def get_current_week_days():
    today = timezone.localdate()
    week_start = today - timedelta(days=today.weekday())
    week_days = [week_start + timedelta(days=i) for i in range(7)]
    return week_days, week_start

def get_user_7_days(user):
    last_checkin = Checkin.objects.filter(user=user).order_by('-created').first()
    if last_checkin:
        first_day = last_checkin.created
    else:
        first_day = timezone.localdate()
    return [first_day + timedelta(days=i) for i in range(7)], first_day

def get_current_streak_days(user):
    today = timezone.localdate()
    checkins = Checkin.objects.filter(user=user).order_by('-created')
    checked_days = set([c.created for c in checkins])
    streak_start = today
    for i in range(7):
        day = today - timedelta(days=i)
        if day in checked_days:
            streak_start = day
        else:
            if i == 0:
                streak_start = today
            break
    week_days = [streak_start + timedelta(days=i) for i in range(7)]
    return week_days, checked_days, streak_start

def get_user_streak_window(user):
    today = timezone.localdate()
    checkins = (
        Checkin.objects.filter(user=user)
        .order_by('created')
        .values_list('created', flat=True)
    )
    checkins = list(checkins)
    if not checkins:
        base_day = today
        streak = 0
    else:
        streak = 0
        base_day = today
        checkset = set(checkins)
        for days_ago in range(0, 7):
            day = today - timedelta(days=days_ago)
            if day in checkset:
                streak += 1
                base_day = day
            else:
                if days_ago == 0:
                    base_day = today
                else:
                    base_day = today - timedelta(days=days_ago - 1)
                break
    week_days = [base_day + timedelta(days=i) for i in range(7)]
    return week_days, set(checkins), streak, today

def get_user_current_streak_window(user):
    today = timezone.localdate()
    checkin_dates = list(
        Checkin.objects.filter(user=user)
        .order_by('created')
        .values_list('created', flat=True)
    )
    if not checkin_dates:
        streak_start = today
        streak = 0
    else:
        streak = 0
        streak_start = today
        checkset = set(checkin_dates)
        for offset in range(0, 7):
            day = today - timedelta(days=offset)
            if day in checkset:
                streak += 1
                streak_start = day
            else:
                if offset == 0:
                    streak_start = today
                    streak = 0
                break
    week_days = [streak_start + timedelta(days=i) for i in range(7)]
    return week_days, set(checkin_dates), streak, today

def get_personal_streak_window(user):
    today = timezone.localdate()
    checkins = set(
        Checkin.objects.filter(user=user)
        .values_list('created', flat=True)
    )
    streak = 0
    for i in range(0, 7):
        day = today - timedelta(days=i)
        if day in checkins:
            streak += 1
        else:
            break
    if streak == 0:
        window_start = today
    else:
        window_start = today - timedelta(days=streak-1)
    week_days = [window_start + timedelta(days=i) for i in range(7)]
    return week_days, checkins, streak, today

def profil_view(request):
    # A felhasználó összes korábbi foglalása
    foglalasok = Foglalas.objects.filter(felhasznalo=request.user)\
        .select_related('kavezo')\
        .order_by('kavezo__nev', '-datum')

    # Kávézók kigyűjtése, ahova már foglalt (duplázás nélkül, név szerint rendezve)
    kavezok = Kavezo.objects.filter(foglalas__felhasznalo=request.user).distinct().order_by('nev')

    # GET paraméter alapján szűrés, ha kiválasztott kávézó van
    kavezo_id = request.GET.get('kavezo_id')
    if kavezo_id:
        foglalasok = foglalasok.filter(kavezo_id=kavezo_id)

    # Rendelések és értékelések ugyanúgy maradnak
    rendelesek = Rendeles.objects.filter(felhasznalo=request.user) \
                                 .prefetch_related('termekek') \
                                 .order_by('-datum')
    ertekelesek = Ertekeles.objects.filter(felhasznalo=request.user) \
                                   .select_related('kavezo') \
                                   .order_by('-datum')

    user = request.user
    week_days, checked_days, streak, today = get_personal_streak_window(user)
    pontok_hetre = [1, 3, 5, 5, 14, 10, 20]
    idx_today = (today - week_days[0]).days
    pont_ma = pontok_hetre[idx_today] if 0 <= idx_today < 7 else pontok_hetre[0]

    return render(request, "kavezok/profil.html", {
        'user': user,
        'foglalasok': foglalasok,
        'kavezok': kavezok,
        'kavezo_id': kavezo_id,
        'rendelesek': rendelesek,
        'ertekelesek': ertekelesek,
        "week_days": week_days,
        "checked_days": checked_days,
        "pont_ma": pont_ma,
        "pontok_hetre": pontok_hetre,
        "streak": streak,
        "today": today,
    })
    
def checkin(request):
    user = request.user
    today = timezone.localdate()
    week_days, _, _, _ = get_user_current_streak_window(user)  # Mostantól ezt használd!
    today_idx = (today - week_days[0]).days
    pont_ma = [1, 3, 5, 5, 14, 10, 20][today_idx] if 0 <= today_idx < 7 else 1

    if not Checkin.objects.filter(user=user, created=today).exists() and 0 <= today_idx < 7:
        profil = Profil.objects.get(user=user)
        profil.total_points += pont_ma
        profil.save()
        Checkin.objects.create(user=user, created=today)
    return redirect('kavezok:profil')

SPIN_POINTS = [0, 5, 10, 20, 50, 100]

@login_required
def porgeto_view(request):
    user = request.user
    profil = user.profil
    spun_points = None
    can_spin = profil.last_spin != now().date()
    if request.method == "POST" and can_spin:
        spun_points = random.choice(SPIN_POINTS)
        profil.total_points += spun_points
        profil.last_spin = now().date()
        profil.save()
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "result": spun_points,
                "points_index": SPIN_POINTS.index(spun_points),
                "current_points": profil.total_points,
            })
    return render(request, "kavezok/porgeto.html", {
        'spun_points': spun_points,
        'current_points': profil.total_points,
        'can_spin': can_spin,
        'points_list': SPIN_POINTS,
    })