from django import forms
from .models import Kavezo, Nyitvatartas, Foglalas, Ertekeles, Preferencia


# Kávézó űrlap
class KavezoForm(forms.ModelForm):
    class Meta:
        model = Kavezo
        fields = ['nev', 'cim', 'hangulat', 'arkategoriak']


# Nyitvatartás űrlap
class NyitvatartasForm(forms.ModelForm):
    class Meta:
        model = Nyitvatartas
        fields = ['nap', 'nyitas', 'zaras']
        widgets = {
            'nyitas': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
            'zaras': forms.TimeInput(format='%H:%M', attrs={'type': 'time'}),
        }


class ErtekelesForm(forms.ModelForm):
    class Meta:
        model = Ertekeles
        fields = ['pontszam', 'megjegyzes']
        
# Felhasználói preferenciák űrlap
class PreferenciaForm(forms.ModelForm):
    class Meta:
        model = Preferencia
        fields = ['kedvenc_kave', 'hangulat', 'ar']

class FoglalasForm(forms.ModelForm):
    class Meta:
        model = Foglalas
        fields = ['kavezo', 'datum', 'szemelyek_szama', 'megjegyzes']
        widgets = {
            'datum': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'szemelyek_szama': forms.NumberInput(attrs={'min': 1}),
        }
        labels = {
            'kavezo': 'Kávézó',
            'datum': 'Foglalás időpontja',
            'szemelyek_szama': 'Személyek száma',
            'megjegyzes': 'Megjegyzés'
        }
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SajátUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email cím")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        

class SajátRegisztrációsForm(UserCreationForm):
    email = forms.EmailField(label='Email cím')
    username = forms.CharField(
        label='Felhasználónév',
        help_text='150 karakter vagy kevesebb. Csak betűk, számok, és @/./+/-/_ karakterek.'
    )
    password1 = forms.CharField(
        label='Jelszó',
        help_text=(
            '<ul>'
            '<li>A jelszavad ne legyen túl hasonló más személyes adathoz.</li>'
            '<li>Legalább 8 karakter hosszú legyen.</li>'
            '<li>Ne legyen gyakran használt jelszó.</li>'
            '<li>Ne csak számokat tartalmazzon.</li>'
            '</ul>'
        ),
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label='Jelszó megerősítése',
        help_text='Írd be újra ugyanazt a jelszót.',
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')