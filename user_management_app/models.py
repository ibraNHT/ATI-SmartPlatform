from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

# Choix de rôles utilisateur
ROLE_CHOICES = (
    ('superadmin', 'Super Administrateur'),
    ('manager', 'Manager'),
    ('operant', 'Operant'),
)

# Département
class Departement(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

# Utilisateur personnalisé
class CustomUser(AbstractUser):
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    departement = models.ForeignKey(Departement, on_delete=models.SET_NULL, null=True, blank=True)
    is_validated = models.BooleanField(default=False)  # Validation par le superadmin ou manager

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# Historique des validations
class ValidationLog(models.Model):
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    valide_par = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="validateur")
    date_validation = models.DateTimeField(auto_now_add=True)
