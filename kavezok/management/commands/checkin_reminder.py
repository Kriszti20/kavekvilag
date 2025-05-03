from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.core.signing import TimestampSigner
from kavezok.models import Checkin
from django.conf import settings

class Command(BaseCommand):
    help = 'Napi becsekkolás emlékeztető e-mail küldése ha elmarad'

    def handle(self, *args, **kwargs):
        signer = TimestampSigner()
        today = timezone.localdate()
        User = get_user_model()
        all_users = User.objects.filter(is_active=True, email__isnull=False).exclude(email="")
        checked_in_today = set(Checkin.objects.filter(created=today).values_list('user_id', flat=True))
        no_checkin_users = all_users.exclude(id__in=checked_in_today)
        for user in no_checkin_users:
            token = signer.sign(str(user.id))
            quick_checkin_url = f"{settings.SITE_URL}/quick-checkin/{token}/"
            send_mail(
                "Ne felejts el ma becsekkolni a Kávézós jutalmakért!",
                (
                    f"Szia {user.username}!\n"
                    "Ma még nem csekkoltál be. Lépj be, hogy megszerezd a napi pontokat! :)\n"
                    f"Becsekkoláshoz csak kattints ide: {quick_checkin_url}\n\n"
                    "Ez a link csak 1 napig érvényes."
                ),
                "info@kavekvilaga.hu",
                [user.email],
                fail_silently=False,
            )
            self.stdout.write(f"Emlékeztető elküldve: {user.email}")