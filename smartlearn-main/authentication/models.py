from django.db import models
from django.contrib.auth.models import AbstractUser


class Utilisateur(AbstractUser):
    ROLES = (
        ('ENSEIGNANT','Enseignant'),
        ('APPRENANT','Apprenant')
    )
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLES, default='APPRENANT')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    def is_admin(self):
        return self.is_superuser
    def is_enseignant(self):
        return self.role == 'ENSEIGNANT'
    def is_apprenant(self):
        return self.role == 'APPRENANT'
    
    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = 'ADMIN'  # Assigne automatiquement le rôle Admin
        super().save(*args, **kwargs)
    