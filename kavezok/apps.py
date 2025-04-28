from django.apps import AppConfig


class KavezokConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kavezok'

from django.apps import AppConfig

class KavezokConfig(AppConfig):
    name = 'kavezok'

    def ready(self):
        import kavezok.signals
        
        