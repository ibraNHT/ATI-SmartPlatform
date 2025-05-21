# src/users/models.py
from django.conf import settings  # Import settings to access custom settings
from django.contrib.auth.models import AbstractUser, BaseUserManager  # Import necessary modules
from django.db import models  # Import the models module for defining database models
from django.utils.translation import gettext_lazy as _  # Import gettext_lazy for internationalization


class CustomUserManager(BaseUserManager):
    """
    Define a model manager for our User model.
    This manager is responsible for creating and saving User objects.
    """

    def _create_user(self, email, username, password=None, **extra_fields):
        """
        Create and save a User with the given username, email and password.
        This is a helper method used by create_user and create_superuser.
        It encapsulates the common logic of user creation.
        """
        if not email:
            raise ValueError('The given email must be set')  # Raise an error if no email is provided
        email = self.normalize_email(email)  # Normalize the email address (e.g., convert to lowercase)
        if not username:
            raise ValueError('The given username must be set')
        user = self.model(email=email, username=username, **extra_fields)  # Create a User object
        user.set_password(password)  # Set the user's password (hashing it)
        user.save(using=self._db)  # Save the User object to the database
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)  # Set default value for is_staff
        extra_fields.setdefault('is_superuser', False)  # Set default value for is_superuser
        return self._create_user(email, username, password, **extra_fields)  # Call the _create_user method

    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given username, email and password.
        A SuperUser has all permissions.
        """
        extra_fields.setdefault('is_staff', True)  # Set is_staff to True
        extra_fields.setdefault('is_superuser', True)  # Set is_superuser to True

        if extra_fields.get('is_staff') is not True:  # Check if is_staff is True
            raise ValueError('Superuser must have is_staff=True.')  # Raise error if not True
        if extra_fields.get('is_superuser') is not True:  # Check if is_superuser is True
            raise ValueError('Superuser must have is_superuser=True.')  # Raise error if not True

        return self._create_user(email, username, password, **extra_fields)  # Call the _create_user method


class User(AbstractUser):
    """
    Custom User model to extend the default Django User.
    By extending AbstractUser, we get all the default User fields and functionality,
    and we can add our own custom fields.
    """
    department = models.CharField(max_length=255, choices=settings.DEPARTMENTS, null=True, blank=True)
    role = models.CharField(max_length=20, choices=settings.HR_ROLES, null=True, blank=True)  # Dynamic choices handled in forms/views
    job_title = models.CharField(max_length=255, null=True, blank=True)  # Dynamic choices handled in forms/views
    email = models.EmailField(_('email address'), blank=True, default="")  # Make optional
    username = models.CharField(max_length=150, unique=True, blank=False)  # Retain username
    # Use username as the primary key
    USERNAME_FIELD = 'username'  # Specify that 'username' is the field used for login
    REQUIRED_FIELDS = ['email']  #  email is already required
    # ID_FIELD = 'employee_id'  # Specify the field used as the primary key

    # Add the fields here
    # employee_id = models.CharField(max_length=255, unique=True)  # Employee ID, primary key, max 255 chars, must be unique
    professional_email = models.EmailField(unique=True, null=True, blank=True)  # Professional email, must be unique, can be null or blank
    start_date = models.DateField(null=True, blank=True)  # Start date, can be null or blank
    first_name = models.CharField(max_length=150, blank=False)  # Required
    personal_email = models.EmailField(blank=False)             # Required
    role_description = models.TextField(null=True, blank=True)  # Role description, a text field, can be null or blank
    address = models.CharField(max_length=255, null=True, blank=True)  # Address, max 255 chars, can be null or blank
    phone_number = models.CharField(max_length=20, null=True, blank=True)  # Phone number, max 20 chars, can be null or blank
    gender = models.CharField(  # Gender, a choice field
        max_length=10, choices=[("female", "Female"), ("male", "Male")], null=True, blank=True
    )
    birth_date = models.DateField(null=True, blank=True)  # Birth date, can be null or blank
    personal_picture = models.FileField(upload_to="profile_pics/", null=True, blank=True)  # Personal picture, uploaded to 'profile_pics/' directory, can be null or blank
    is_activated = models.BooleanField(default=False)  # Flag to indicate if the profile is activated, default is False
    joined_files = models.FileField(upload_to="joined_files/", null=True, blank=True)  # Joined files, uploaded to 'joined_files/' directory, can be null or blank

    objects = CustomUserManager()  # Use our custom user manager

    def __str__(self):
        return self.username  # Return the username as the string representation of the User object.

    class Meta:
        verbose_name = _('user')  # Set the verbose name for the model
        verbose_name_plural = _('users')  # Set the plural verbose name for the model
        abstract = False
        
    # Add these at the bottom of your model class
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',  # Changed from default 'user_set'
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # Changed from default 'user_set'
        related_query_name='user',
    )
    
    # ... rest of your model ...
