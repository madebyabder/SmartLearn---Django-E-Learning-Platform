from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth.decorators import login_required, user_passes_test
from authentication.models import Utilisateur
from admin_app.models import Event, VideoConference
from admin_app.models import ActivityLog
import cours
from cours.models import Cours
# Vérifie que l'utilisateur est un administrateur
from django.http import JsonResponse
from django import forms
from .forms import EventForm


@login_required
def is_admin(user):
    return user.role == 'admin'


# Liste tous les utilisateurs
@login_required
def list_users(request):
    users = Utilisateur .objects.all()
    return render(request, 'admin_app/list_users.html', {'users': users})
# add utilisateur


@login_required
def add_user(request):
    if request.method == 'POST':

        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            role = request.POST.get('role')

            # Vérification doublons
            if Utilisateur.objects.filter(username=username).exists():

                messages.error(request, "Nom d'utilisateur déjà utilisé.")
                return render(request, 'admin_app/add_users.html')

            if Utilisateur.objects.filter(email=email).exists():

                messages.error(request, "Email déjà utilisé.")
                return render(request, 'admin_app/add_users.html')

            # Création de l'utilisateur
            user = Utilisateur.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                role=role
            )

            if role == 'ADMIN':
                user.is_staff = True
                user.is_superuser = True
            user.save()
            ActivityLog.objects.create(
                user=request.user, action=f"a ajouté l'utilisateur {username}")

            messages.success(request, "Utilisateur ajouté avec succès.")
            return redirect('list_users')

        except Exception as e:

            messages.error(request, f"Erreur : {e}")

    return render(request, 'admin_app/add_users.html')

# Supprimer un utilisateur


@login_required
def delete_user(request, user_id):
    user = get_object_or_404(Utilisateur, id=user_id)
    username = user.username  # ✅ Sauvegarder avant suppression
    user.delete()
    ActivityLog.objects.create(
        user=request.user, action=f"a supprimé l'utilisateur {username}")
    return redirect('list_users')


# Modifier un utilisateur
@login_required
def update_user(request, user_id):
    user = get_object_or_404(Utilisateur, id=user_id)

    if request.method == 'POST':
        try:
            user.username = request.POST['username']
            user.first_name = request.POST['first_name']
            user.last_name = request.POST['last_name']
            user.email = request.POST['email']
            user.role = request.POST['role']
            user.is_active = 'is_active' in request.POST  # checkbox
            user.is_staff = user.role == 'ADMIN'
            user.is_superuser = user.role == 'ADMIN'

            # Mot de passe (optionnel)
            password = request.POST['password']
            if password:
                user.password = make_password(password)

            user.save()
            ActivityLog.objects.create(
                user=request.user, action=f"a modifié l'utilisateur {user.username}")

            messages.success(request, "Utilisateur mis à jour avec succès.")

            return redirect('list_users')

        except Exception as e:
            messages.error(request, f"Erreur : {e}")

    return render(request, 'admin_app/update_user.html', {'user': user})
# supervision


@login_required
def supervision_dashboard(request):
    if request.user.role != 'ADMIN':
        return redirect('home')

    logs = ActivityLog.objects.select_related('user').order_by('-timestamp')
    return render(request, 'admin_app/supervision_dashboard.html', {'logs': logs})


# video conference
@login_required
def calendar_events(request):
    events = Event.objects.prefetch_related('videoconference_set').all()

    return render(request, 'admin_app/calendar.html', {'events': events})


@login_required
def add_videoconference(request):
    if request.method == 'POST':
        event_id = request.POST['event_id']
        event = get_object_or_404(Event, id=event_id)

        # Créer la visioconférence associée à l'événement
        VideoConference.objects.create(event=event, is_cancelled=False)

        messages.success(request, "Visioconférence ajoutée avec succès.")
        return redirect('calendar_events')

    # Récupérer les événements disponibles
    events = Event.objects.all()
    return render(request, 'admin_app/add_videoconference.html', {'events': events})


@login_required
def modify_videoconference(request, event_id):
    videoconference = get_object_or_404(VideoConference, event_id=event_id)

    if request.method == 'POST':
        videoconference.is_cancelled = 'is_cancelled' in request.POST
        videoconference.save()

        messages.success(request, "Visioconférence modifiée avec succès.")
        return redirect('calendar_events')

    return render(request, 'admin_app/modify_videoconference.html', {'videoconference': videoconference})


@login_required
def schedule_videoconference(request):
    if request.method == "POST":
        title = request.POST['title']
        date = request.POST['date']
        event = Event.objects.create(title=title, date=date)
        VideoConference.objects.create(event=event)
        return redirect('calendar_events')

    return render(request, 'admin_app/schedule_videoconference.html')


@login_required
def cancel_videoconference(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    videoconference = get_object_or_404(VideoConference, event=event)

    # Annuler la visioconférence
    videoconference.is_cancelled = True
    videoconference.save()

    messages.success(request, "Visioconférence annulée avec succès.")
    return redirect('admin_app:calendar_events')


@login_required
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin_app:calendar_events')
    else:
        form = EventForm()
    return render(request, 'admin_app/add_event.html', {'form': form})


@login_required
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()

    messages.success(request, "Événement supprimé avec succès.")
    return redirect('admin_app:calendar_events')


@login_required
def event_details(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    # Recharger la visioconférence liée pour avoir l’état à jour
    # selon relation OneToOne
    videoconf = getattr(event, 'videoconference', None)
    return render(request, 'admin_app/event_details.html', {'event': event, 'videoconf': videoconf})


@login_required
def toggle_event_status(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    # utilise related_name ou videoconference_set
    videoconf = event.videoconference_set.first()
    if videoconf:
        videoconf.is_cancelled = not videoconf.is_cancelled
        videoconf.save()
        status = "annulé" if videoconf.is_cancelled else "programmé"
        messages.success(
            request, f"L'événement '{event.title}' est maintenant {status}.")
    else:
        messages.error(
            request, "Pas de visioconférence associée à cet événement.")
    return redirect(request.META.get('HTTP_REFERER', 'admin_app:calendar_events'))


@login_required
def ajax_toggle_event_status(request, event_id):
    if request.method == "POST" and request.is_ajax():
        event = get_object_or_404(Event, id=event_id)
        videoconf = event.videoconference_set.first()
        if videoconf:
            videoconf.is_cancelled = not videoconf.is_cancelled
            videoconf.save()
            return JsonResponse({
                'success': True,
                'new_status': videoconf.is_cancelled
            })
        return JsonResponse({'success': False, 'error': 'No videoconference found.'})
    return JsonResponse({'success': False, 'error': 'Invalid request.'})


@login_required
def enseignant_calendar(request):
    user = request.user
    events = user.events.all()  # grâce à related_name='events' dans ManyToMany
    return render(request, 'enseignant/calendar.html', {'events': events})