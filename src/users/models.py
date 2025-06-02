from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

# Local department definitions (removed from settings)
DEPARTMENTS = (
    ("HR", "HR and Accounting"),
    ("Cybersecurity", "Cybersecurity"),
    ("Marketing", "Marketing and Sales"),
    ("Software", "Software Engineering"),
    ("Technical", "Technical Department"),
    ("Operations", "Operations Department"),
    ("Data", "Data Science"),
)

ROLES = (
    ("CEO", "Chief Executive Officer"),
    ("HR_MANAGER", "HR Manager"),
    ("MANAGER", "Department Manager"),
    ("EMPLOYEE", "Employee"),
)

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, username, password=None, **extra_fields):
        email = self.normalize_email(email) if email else ""
        username = username if username else ""
        
        if not username and not email:
            raise ValueError("Either username or email must be set")
            
        user = self.model(email=email, username=username, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, username, password, **extra_fields)

class User(AbstractUser):
    department = models.CharField(max_length=255, choices=DEPARTMENTS, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLES, null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(_('email address'), blank=True, default="")
    
    # Professional fields
    professional_email = models.EmailField(unique=True, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    role_description = models.TextField(null=True, blank=True)
    
    # Personal fields
    personal_email = models.EmailField(blank=False)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(
        max_length=20, 
        null=True, 
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    gender = models.CharField(
        max_length=10, 
        choices=[("female", "Female"), ("male", "Male")], 
        null=True, 
        blank=True
    )
    personal_picture = models.ImageField(
        upload_to="profile_pics/",
        null=True,
        blank=True,
        default=None
    )
    joined_files = models.FileField(
        upload_to="joined_files/",
        null=True,
        blank=True
    )
    is_activated = models.BooleanField(default=False)

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['last_name', 'first_name']

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        related_name='custom_user_set',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        related_name='custom_user_set',
        related_query_name='user',
    )