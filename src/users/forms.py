from django import forms
from django.core.exceptions import ValidationError
from .models import User, DEPARTMENTS, ROLES
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, Submit
from crispy_forms.bootstrap import (
    PrependedText, PrependedAppendedText, FormActions, StrictButton,
)
from django.utils import timezone

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        required=False
    )
    password_confirm = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        required=False
    )
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput,
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "username", # Added username
            "first_name", "last_name", "personal_email",
            "department", "role", "job_title",
            "professional_email", "birth_date", "start_date",
            "address", "phone_number", "gender",
            "personal_picture", "joined_files", "role_description"
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'personal_picture': forms.ClearableFileInput(),
            'joined_files': forms.FileInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            (role, label) for role, label in ROLES
            if role in ["EMPLOYEE", "MANAGER"]
        ]
        self.fields['personal_picture'].required = False
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Field("username"),
                Field("password"),
                Field("password_confirm"),
                css_class="card mb-3"
            ),
            Div(
                Field("first_name"),
                Field("last_name"),
                Field("personal_email"),
                Field("address"),
                Field("phone_number"),
                Field("gender"),
                Field("birth_date"),
                Field("personal_picture"),
                css_class="card mb-3"
            ),
            Div(
                Field("department"),
                Field("role"),
                Field("job_title"),
                Field("professional_email"),
                Field("start_date"),
                Field("role_description"),
                Field("joined_files"),
                css_class="card"
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.") # Use add_error for specific field
        
        # Check for unique username and personal_email
        username = cleaned_data.get('username')
        personal_email = cleaned_data.get('personal_email')

        # When creating a new user, check for uniqueness
        if not self.instance.pk: # Only for new instances (when instance.pk is None)
            if username and User.objects.filter(username=username).exists():
                self.add_error('username', "This username is already taken.")
            if personal_email and User.objects.filter(personal_email=personal_email).exists():
                self.add_error('personal_email', "This personal email is already registered.")
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password"]
        user.set_password(password)
        user.username +=timezone.now().strftime("%Y%m%d%H%M%S")
        if commit:
            user.save()
        return user


class EmployeeEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "personal_email",
            "address", "phone_number", "gender",
            "birth_date", "personal_picture"
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Field("first_name"),
                Field("last_name"),
                Field("personal_email"),
                Field("address"),
                Field("phone_number"),
                Field("gender"),
                Field("birth_date"),
                Field("personal_picture"),
                css_class="card"
            ),
            FormActions(
                Submit('save', 'Save changes'),
                css_class="mt-3"
            )
        )

class EmployeeDeleteForm(forms.Form):
    confirm = forms.BooleanField(
        label="I confirm I want to delete this account",
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Field("confirm"),
                css_class="card mb-3"
            ),
            FormActions(
                Submit('delete', 'Delete Account', css_class='btn-danger'),
                css_class="mt-3"
            )
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
            "department",
            "job_title",
            "username",
            "password",  # Include password
            "role",
            "role_description",
            "joined_files",
            "is_activated",
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].initial = "HR and Accounting"
        self.fields['role'].initial = "HR_MANAGER"
        self.fields['role'].widget.attrs['readonly'] = True
        self.fields['department'].widget.attrs['readonly'] = True
        self.fields['role'].disabled = True
        self.fields['role_description'].disabled = True
        self.fields['role_description'].initial = "We are creating the HR Manager user account with the ability to create other users"  # Set role description to HR Manager
        self.fields['department'].disabled = True
        self.fields['personal_picture'].required = False  # Make personal picture optional
        # self.fields['personal_picture'].initial = "static/images/logo.png"  # Set initial value for personal picture
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
                css_class="card",
            ),
            Div(  # Professional Information
                Field("email"),
                Field("professional_email"),
                Field("start_date", type="date"),
                Field("department"),
                Field("job_title"),
                Field("role"),
                Field("role_description"),
                Field("joined_files"),
                css_class="card",
            ),
            Div(  # Credentials Information
                Field("username"),
                Field("password", type="password"),
                css_class="card",
            ),
        )
        # Note: 'readonly' attributes set for all fields in original, keeping for now
        # for field_name in self.fields:
        #     self.fields[field_name].widget.attrs['readonly'] = False
        # If specific fields should be readonly, set them individually.

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = ""  # Force empty string if not provided in form for AbstractUser's email
        user.department = "HR and Accounting"  # Set department to HR
        user.role = "HR_MANAGER"  # Set role to HR_MANAGER
        user.is_staff = True
        user.job_title = "HR Manager"  # Set job title to HR Manager
        user.role_description = "We are creating the HR Manager user account with the ability to create other users"  # Set role description to HR Manager
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