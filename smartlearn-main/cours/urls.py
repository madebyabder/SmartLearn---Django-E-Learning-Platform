from django.urls import path
from .views import liste_cours, details_cours,course_catalogue,mes_cours_apprenant,catalogue
from .views import modify_cours, delete_cours, modify_module,modify_contenu,certificat
from .views import add_cours,add_module,add_contenu,delete_module,delete_contenu, take_quiz
from . import views


app_name = "cours"

urlpatterns = [
    path('', liste_cours, name='liste_cours'),
    path('liste/', liste_cours, name='liste_cours'),
    path('details/<int:cours_id>/', details_cours, name='details_cours'),

    path("cours/add/", add_cours, name="add_cours"),
    path('cours/<int:cours_id>/add_module/',add_module, name='add_module'),
    path('module/<int:module_id>/add_contenu/', add_contenu, name='add_contenu'),

    path('modify/<int:cours_id>/', modify_cours, name='modify_cours'),
    path('module/<int:module_id>/modifier/', modify_module, name='modify_module'),
    path('contenu/<int:contenu_id>/modifier/', modify_contenu, name='modify_contenu'),

    path('delete/<int:cours_id>/', delete_cours, name='delete_cours'),
    path('module/<int:module_id>/delete/', delete_module, name='delete_module'),
    path('contenu/delete/<int:contenu_id>/', delete_contenu, name='delete_contenu'),

    path('inscrire/<int:cours_id>/', views.inscrire_cours, name='inscrire_cours'),
    path('cours/<int:cours_id>/', views.cours_detail_public, name='cours_detail_public'),
    path('cours/<int:cours_id>/content/', views.cours_content, name='cours_content'),

    path('module/<int:module_id>/quiz/', views.take_quiz, name='take_quiz'),
    path('catalogue/', views.course_catalogue, name='course_catalogue'),
    path('mes-cours/', views.mes_cours_apprenant, name='mes_cours_apprenant'),
    path('certificat/<int:cours_id>/', views.certificat, name='certificat'),
    path('catalogue/', views.catalogue, name='catalogue'),
    path('cours/<int:id>/', views.cours_detail_public, name='cours_detail_public'),

]

