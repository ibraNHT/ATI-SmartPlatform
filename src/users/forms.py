# src/users/forms.py
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div
from crispy_forms.bootstrap import (
    PrependedText, PrependedAppendedText, FormActions, StrictButton,
)


class UserCreationForm(UserCreationForm):
    """Form for creating new users (employees) by the HR Manager."""   
    # Make password fields optional
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        required=False
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        required=False
    )  
        
    email = forms.EmailField(initial="", required= False)  # Set initial value for email

    class Meta:
        model = User
        fields = (
            "email",  # Email field
            "professional_email",
            "personal_email",
            "department",
            "job_title",
            "birth_date",
            "start_date",
            "role_description",
            "address",
            "phone_number",
            "gender",
            "personal_picture",
            "role",
            "joined_files",
            "first_name",
            "last_name",
        )  #  fields
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),  # Use date input for start date
            'start_date': forms.DateInput(attrs={'type': 'date'}),  # Use date input for birth date
        }
        # Add the fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            (role, label) for role, label in settings.HR_ROLES 
            if role in ["EMPLOYEE", "MANAGER"]  # Use "MANAGER" not "Manager"
        ]   # Role filtering
        self.fields['personal_picture'].required = False  # Make personal picture optional
        self.fields['personal_picture'].initial = "static/images/logo.png"  # Set initial value for personal picture
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(  # Personal Information
                Field("first_name"),
                Field("last_name"),
                Field("personal_email"),
                Field("address"),
                Field("phone_number"),
                Field("gender"),
                Field("birth_date", type="date"),
                Field("personal_picture"),
                css_class="card",
            ),
            Div(  # Professional Information
                Field("email"),
                Field("professional_email"),
                Field("department"),
                Field("role"),
                Field("job_title"),
                Field("start_date", type="date"),
                Field("role_description"),
                Field("joined_files"),
                css_class="card",
            ),
        )
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = ""  # Force empty string if not provided
        user.is_staff = True
        user.password1 = ''  # Set to empty
        user.password2 = ''  # Set to empty
        user.professional_email = self.cleaned_data["professional_email"]  # Set the professional email
        if commit:
            user.save()
        return user


class UserChangeForm(forms.Form):
    """Form for updating user authentication data (for CEO)."""
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field("username"),
            Field("password", type="password"),
        )



class HRManagerCreationForm(forms.ModelForm):
    """Form for creating the HR Manager user by the CEO."""
    password = forms.CharField(widget=forms.PasswordInput)  # Add password field
    email = forms.EmailField(initial="", required=False)  # Set initial value for email

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "personal_email",
            "address",
            "phone_number",
            "gender",
            "birth_date",
            "personal_picture",
            "email",  # Include email
            "professional_email",
            "start_date",
            # "employee_id",
            "department",
            "job_title",
            "username",
            "password",  # Include password
            "role",
            "role_description",
            "joined_files",
            "is_activated",
        ]
        # Add the fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].initial = "HR"
        self.fields['role'].initial = "HR_MANAGER"
        self.fields['role'].widget.attrs['readonly'] = True
        self.fields['department'].widget.attrs['readonly'] = True
        self.fields['personal_picture'].required = False  # Make personal picture optional
        self.fields['personal_picture'].initial = "static/images/logo.png"  # Set initial value for personal picture
        self.helper = FormHelper()  # Initialize Crispy Form Helper
        self.helper.layout = Layout(  # Define the layout of the form
            Div(  # Personal Information
                Field("first_name"),
                Field("last_name"),
                Field("personal_email"),
                Field("address"),
                Field("phone_number"),
                Field("gender"),
                Field("birth_date", type="date"),
                Field("personal_picture"),
                Field("joined_files"),
                css_class="card",
            ),
            Div(  # Professional Information
                Field("email"),
                Field("professional_email"),
                Field("start_date", type="date"),
                # Field("employee_id"),
                Field("department"),
                Field("job_title"),
                Field("role"),
                Field("role_description"),
                css_class="card",
            ),
            Div(  # Credentials Information
                Field("username"),
                Field("password", type="password"),
                css_class="card",
            ),
        )
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['readonly'] = False
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = ""  # Force empty string if not provided
        user.department = "HR and accounting"  # Set department to HR
        user.role = "HR_MANAGER"  # Set role to HR_MANAGER
        user.is_staff = True
        user.job_title = "HR Manager"  # Set job title to HR Manager
        user.role_description = "HR Manager with the ability to create other users"  # Set role description to HR Manager
        user.is_activated = True  # Set is_activated to True
        user.set_password(self.cleaned_data["password"])  # Set the password
        user.username = self.cleaned_data["username"]  # Set the username
        user.professional_email = self.cleaned_data["professional_email"]  # Set the professional email
        if commit:
            user.save()
        return user
    def clean_personal_email(self):
        email = self.cleaned_data.get('personal_email')
        if User.objects.filter(personal_email=email).exists():
            raise forms.ValidationError("This personal email is already registered.")
        return email
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username



class EmployeeValidationForm(forms.Form):
    """Form for validating employees by the CEO."""
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div( # Credentials
                Field("username"),
                Field("password", type="password"),
                css_class="card"
            ),
        )
        