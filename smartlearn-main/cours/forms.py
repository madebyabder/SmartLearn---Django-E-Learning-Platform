from django import forms
from .models import Cours,Module, Contenu


class EnrollForm(forms.Form):
    cours_id = forms.IntegerField(widget=forms.HiddenInput())

class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['title', 'description','category', 'difficulty_level','image','is_published']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': "Ex: Introduction à l'IA", 'required': True}),
            'description': forms.Textarea(attrs={'placeholder': "Ajoutez une description du cours"}),
        }

class ModuleForm(forms.ModelForm):
    class Meta:
        model = Module
        fields = ['title','order_position']

class ContenuForm(forms.ModelForm):
    class Meta:
        model = Contenu
        fields = ['title', 'description', 'video']
