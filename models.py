from django.db import models

class Kavezo(models.Model):  # Kávézó modell példa
    nev = models.CharField(max_length=100)  # Kávézó neve
    cim = models.CharField(max_length=255)  # Cím
    nyitvatartas = models.TimeField(blank=True, null=True)  # Nyitvatartás

    def __str__(self):
        return self.nev