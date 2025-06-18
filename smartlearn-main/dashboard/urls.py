from django.urls import path
from .views import admin_dashboard, enseignant_dashboard, apprenant_dashboard, dashboard_redirect
from .views import profile
from .views import dashboard_view
app_name = 'dashboard'

urlpatterns = [
    path('admin/', admin_dashboard, name='admin_dashboard'),
    path('enseignant/', enseignant_dashboard, name='enseignant_dashboard'),
    path('apprenant/', apprenant_dashboard, name='apprenant_dashboard'),
    path('', dashboard_redirect, name='dashboard_redirect'),
    path('profile/', profile, name='profile'),

]
