from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm,PasswordChangeForm
from .models import Utilisateur
from django.contrib.auth.forms import AuthenticationForm


class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Prénom'}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Nom'}))
    role = forms.ChoiceField(
        choices=Utilisateur.ROLES,
        widget=forms.RadioSelect,  # Affiche en format bouton radio
    )
    class Meta:
        model = Utilisateur
        fields = ['username','first_name','last_name','email','password1','password2', 'role']


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))


class ProfileUpdateForm(UserChangeForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'placeholder': 'Nom d’utilisateur'}))

    class Meta:
        model = Utilisateur
        fields = ['username', 'email']

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Ancien mot de passe'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Nouveau mot de passe'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirmer mot de passe'}))