from django.contrib import admin
from .models import Cours, Module, Contenu

# Register your models here.

admin.site.register(Cours)
admin.site.register(Module)
admin.site.register(Contenu)
