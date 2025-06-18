from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from .models import Utilisateur
from .forms import RegistrationForm
from django.contrib.auth.views import LoginView
from django.contrib.auth import login,  authenticate
from admin_app.models import ActivityLog


class RegisterView(CreateView):
    model = Utilisateur
    form_class = RegistrationForm
    template_name = 'authentication/register.html'
    success_url = '/authentication/login/'

    def form_valid(self, form):
        utilisateur = form.save(commit=False)
        print("Utilisateur en création :", utilisateur.username, utilisateur.role)
        messages.success(self.request, f"Bienvenue {utilisateur.username} ! Inscription réussie ")
        utilisateur.password = make_password(utilisateur.password)  # Hash automatique
        utilisateur.save()
        ActivityLog.objects.create(
            user=utilisateur,
            action=f"s'est inscrit avec le rôle {utilisateur.role}"
        )
        return super().form_valid(form)


class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'

    def dispatch(self, request, *args, **kwargs):
        request.session.pop('_messages', None)
        return super().dispatch(request, *args, **kwargs)
    def form_valid(self, form):
        email = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, email=email, password=password)

        if user is not None:
            ActivityLog.objects.create(
                user=user,
                action="s'est connecté"
            )
            login(self.request, user)
            role = user.role.strip().lower()

            print(f"User authenticated: {user.email}, Detected role: '{user.role}'")
            if role == 'admin':
                return redirect('/dashboard/admin/')
            elif role == 'enseignant':
                return redirect('/dashboard/enseignant/')
            elif role == 'apprenant':
                return redirect('/dashboard/apprenant/')
            else:
                return redirect('/home/')
        else:
            return self.form_invalid(form)
        
