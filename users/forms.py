from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=[])  # Start with empty choices
    department = forms.ChoiceField(
        choices=[
            ('HR and accountability', 'HR and accountability'),
            ('Marketing-Sales', 'Marketing-Sales'),
            ('Software development', 'Software development'),
            ('Cybersecurity', 'Cybersecurity'),
            ('Data Science', 'Data Science'),
            ('Costumer support', 'Costumer support'),
            ('Operations', 'Operations'),
        ],
        required=True,
    )
    role_description = forms.CharField(widget=forms.Textarea, required=False)
    address = forms.CharField(max_length=255, required=False)
    telephone = forms.CharField(max_length=20, required=False)
    gender = forms.CharField(max_length=10, required=False)
    date_of_birth = forms.DateField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        user_role = kwargs.pop('user_role', None)  # Get user role from kwargs
        super().__init__(*args, **kwargs)
        if user_role == 'CEO':
            self.fields['role'].choices = [('HR Manager', 'HR Manager')]
        elif user_role == 'HR Manager':
            self.fields['role'].choices = [('Manager', 'Manager'), ('Operator', 'Operator')]
        else:
            self.fields['role'].choices = []  # no roles

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password1 = forms.CharField(widget=forms.PasswordInput)
    new_password2 = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("New passwords do not match")
        return cleaned_data
    
class UserValidationForm(forms.Form):
    is_validated = forms.BooleanField(label="Validate User", required=False)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_validated'].label = "Validate User"
    
