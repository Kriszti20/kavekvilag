# kavezok/management/commands/checkin_reminder.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from kavezok.models import Foglalas

class Command(BaseCommand):
    help = 'Emlékeztető email küldése a foglalás előtt 24 órával'

    def handle(self, *args, **options):
        now = timezone.now()
        # 24-25 órán belül esedékes foglalások – egyszerűen: "holnap ilyenkor"
        start = now + timedelta(hours=23)
        end = now + timedelta(hours=25)

        foglalasok = Foglalas.objects.filter(
            emlekezteto_kuldve=False,
            datum__gte=start,
            datum__lt=end
        )
        
        for foglalas in foglalasok:
            user = foglalas.felhasznalo
            if not user or not user.email:
                continue

            # ---- IDŐZÓNA-KORREKCIÓ ITT! ----
            datum = foglalas.datum
            if timezone.is_naive(datum):
                datum = timezone.make_aware(datum, timezone.get_current_timezone())
            datum = datum.astimezone(timezone.get_current_timezone())

            subject = "Foglalás emlékeztető"
            szoveg = (
                f"Kedves {user.username}!\n\n"
                f"Holnap várunk a(z) {foglalas.kavezo.nev} kávézóban!\n"
                f"Cím: {foglalas.kavezo.cim}\n"
                f"Időpont: {datum.strftime('%Y-%m-%d %H:%M')}\n"
                f"Személyek száma: {foglalas.szemelyek_szama}\n"
                f"Megjegyzés: {foglalas.megjegyzes or '-'}\n\n"
                "Kellemes napot kívánunk!"
            )

            send_mail(
                subject,
                szoveg,
                settings.DEFAULT_FROM_EMAIL,
                [user.email]
            )
            foglalas.emlekezteto_kuldve = True
            foglalas.save()
            self.stdout.write(self.style.SUCCESS(f"Emlékeztető elküldve: {user.email} ({foglalas.id})"))