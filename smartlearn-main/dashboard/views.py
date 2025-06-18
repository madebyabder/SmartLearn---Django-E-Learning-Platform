from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from authentication.forms import ProfileUpdateForm, CustomPasswordChangeForm
from cours.models import Cours
from cours.models import Inscription
from admin_app.models import ActivityLog
from django.contrib.auth import get_user_model
from django.db.models import Count
from datetime import datetime, timedelta


@login_required
def apprenant_dashboard(request):
    cours_inscrits_ids = Inscription.objects.filter(apprenant=request.user).values_list('cours_id', flat=True)
    liste_cours = Cours.objects.filter(is_published=True)

    return render(request, 'dashboard/apprenant_dashboard.html', {
        'cours_inscrits_ids': cours_inscrits_ids,
        'liste_cours': liste_cours,
    })

@login_required
def admin_dashboard(request):
    User = get_user_model()
    
    # Get total counts
    total_users = User.objects.count()
    total_courses = Cours.objects.count()
    total_teachers = User.objects.filter(role='enseignant').count()
    total_students = User.objects.filter(role='apprenant').count()

    # Get recent activities
    recent_activities = []
    
    # Get recent user registrations
    recent_users = User.objects.order_by('-date_joined')[:5]
    for user in recent_users:
        recent_activities.append({
            'type': 'user',
            'title': f'Nouvel utilisateur: {user.username}',
            'time': user.date_joined.strftime('%d/%m/%Y %H:%M')
        })
    
    # Get recent course creations
    recent_courses = Cours.objects.order_by('-created_at')[:5]
    for course in recent_courses:
        recent_activities.append({
            'type': 'course',
            'title': f'Nouveau cours: {course.title}',
            'time': course.created_at.strftime('%d/%m/%Y %H:%M')
        })
    
    # Get recent teacher activities
    recent_teachers = User.objects.filter(role='enseignant').order_by('-date_joined')[:5]
    for teacher in recent_teachers:
        recent_activities.append({
            'type': 'teacher',
            'title': f'Nouvel enseignant: {teacher.username}',
            'time': teacher.date_joined.strftime('%d/%m/%Y %H:%M')
        })
    
    # Get recent student activities
    recent_students = User.objects.filter(role='apprenant').order_by('-date_joined')[:5]
    for student in recent_students:
        recent_activities.append({
            'type': 'student',
            'title': f'Nouvel apprenant: {student.username}',
            'time': student.date_joined.strftime('%d/%m/%Y %H:%M')
        })
    
    # Sort activities by time
    recent_activities.sort(key=lambda x: datetime.strptime(x['time'], '%d/%m/%Y %H:%M'), reverse=True)
    recent_activities = recent_activities[:10]  # Get only the 10 most recent activities

    context = {
        'user': request.user,
        'total_users': total_users,
        'total_courses': total_courses,
        'total_teachers': total_teachers,
        'total_students': total_students,
        'recent_activities': recent_activities
    }
    
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def enseignant_dashboard(request):
    liste_cours = Cours.objects.filter(teacher=request.user, is_published=True)
    activity_logs = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')[:10]  # Get last 10 activities
    return render(request, 'dashboard/enseignant_dashboard.html', 
                  {'user': request.user, 'liste_cours': liste_cours, 'activity_logs': activity_logs})

@login_required
def dashboard_redirect(request):
    role = request.user.role.strip().lower()
    if role == 'admin':
        return redirect('dashboard:admin_dashboard')
    elif role == 'enseignant':
        return redirect('dashboard:enseignant_dashboard')
    elif role == 'apprenant':
        return redirect('dashboard:apprenant_dashboard')
    else:
        return redirect('home')
    

@login_required
def profile_view(request):
    return render(request, 'dashboard/profile.html')

@login_required
def profile(request):
    profile_form = ProfileUpdateForm(instance=request.user)
    password_form = CustomPasswordChangeForm(request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ProfileUpdateForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Profil mis à jour avec succès!")
                return redirect('profile')  # ✅ Absolute path

        elif 'update_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)
                messages.success(request, "Mot de passe mis à jour!")
                return redirect('profile')  # ✅ Absolute path

    return render(request, 'dashboard/profile.html', {
        'profile_form': profile_form, 
        'password_form': password_form
    })




@login_required
def dashboard_view(request):
    cours = Cours.objects.filter(teacher=request.user)
    return render(request, 'dashboard.html', {'cours': cours})

