from django import forms
from django.conf import settings
from .models import Event

Utilisateur = settings.AUTH_USER_MODEL

class EventForm(forms.ModelForm):
    enseignants = forms.ModelMultipleChoiceField(
        queryset=None,  # on mettra le queryset en __init__
        widget=forms.CheckboxSelectMultiple,  # ou SelectMultiple
        required=False,
        label="Enseignants"
    )

    class Meta:
        model = Event
        fields = ['title', 'date', 'enseignants']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Filtrer uniquement les utilisateurs qui sont enseignants
        self.fields['enseignants'].queryset = User.objects.filter(role='ENSEIGNANT')
