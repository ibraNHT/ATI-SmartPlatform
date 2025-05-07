from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Departement

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=[('manager', 'Manager'), ('operant', 'Operant')])
    departement = forms.ModelChoiceField(queryset=Departement.objects.all())

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'departement', 'password1', 'password2']
