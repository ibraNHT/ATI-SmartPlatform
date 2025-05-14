from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(
        max_length=20,
        choices=[
            ('Manager', 'Manager'),
            ('Operator', 'Operator'),
        ],
        default='Manager',
    )
    role = models.CharField(max_length=50)
    is_validated = models.BooleanField(default=False)
    department = models.CharField(
        max_length=100,
        blank=True, null=True,
        choices=[
            ('HR and accountability', 'HR and accountability'),
            ('Marketing-Sales', 'Marketing-Sales'),
            ('Software development', 'Software development'),
            ('Cybersecurity', 'Cybersecurity'),
            ('Data Science', 'Data Science'),
            ('Costumer support', 'Costumer support'),
            ('Operations', 'Operations'),
        ])
    role_description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # No need for a created_by field, as we only have one HR manager and there will be only one creating user profiles but could be usable in the future
    # created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_profiles', null=True, blank=True)
    
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"