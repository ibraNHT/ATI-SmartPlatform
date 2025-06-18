"""
Django settings for the Ati_smart_platform project.

This file is structured to handle both development and production environments.
Environment-specific settings are controlled by the `ENVIRONMENT` variable.
"""

import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# --- 1. Path and Environment Setup ---

# Build paths: BASE_DIR -> repository_root/src/
BASE_DIR = Path(__file__).resolve().parent.parent
# REPO_ROOT -> repository_root/
REPO_ROOT = BASE_DIR.parent

# Load environment variables from .env file in the repository root
load_dotenv(REPO_ROOT / '.env')

# Environment detection (defaults to 'development' if not set)
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development').lower()
IS_PRODUCTION = ENVIRONMENT == 'production'
IS_DEVELOPMENT = not IS_PRODUCTION

# Explicitly disable HTTPS in development
if IS_DEVELOPMENT:
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = None
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False


# --- 2. Core Django Settings ---

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-development-key')

# DEBUG is True in development and False in production
DEBUG = IS_DEVELOPMENT

# Allowed hosts differ for development and production
if IS_DEVELOPMENT:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']
else:
    # In production, trust the value from the environment or use a wildcard
    # for platform-as-a-service providers like Railway.
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

ROOT_URLCONF = 'Ati_smart_platform.urls'
WSGI_APPLICATION = 'Ati_smart_platform.wsgi.application'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SITE_ID = 1


# --- 3. Application Definition (INSTALLED_APPS) ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',

    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',

    # Local apps
    'users.apps.UsersConfig',
]

# Add development-specific apps
if IS_DEVELOPMENT:
    INSTALLED_APPS += ['debug_toolbar']


# --- 4. Middleware (MIDDLEWARE) ---

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Add after other middleware
]

# Add development-specific middleware
if IS_DEVELOPMENT:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1', 'localhost']


# --- 5. Templates (TEMPLATES) ---

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [REPO_ROOT / 'templates'], # Project-level templates
        'DIRS': [BASE_DIR / 'templates'], # Project-level templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# --- 6. Database (DATABASES) ---

if IS_PRODUCTION:
    # In production, use the DATABASE_URL from the environment.
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            ssl_require=True
        )
    }
else:
    # In development, use a local SQLite database.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': REPO_ROOT / 'db.sqlite3',
        }
    }


# --- 7. Password Validation ---

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- 8. Internationalization (I18N) ---

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- 9. Static and Media Files ---

STATIC_URL = '/static/'
STATIC_ROOT = REPO_ROOT / 'staticfiles' # For `collectstatic`
STATICFILES_DIRS = [REPO_ROOT / 'static'] # For local development

MEDIA_URL = '/media/'
MEDIA_ROOT = REPO_ROOT / 'media' # For user-uploaded files

# Use different storage backends for development and production
if IS_PRODUCTION:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
else:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


# --- 10. Security Settings ---

# These settings are only enabled in production to avoid issues in development.
if IS_PRODUCTION:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https') # For reverse proxies
    SECURE_REFERRER_POLICY = 'same-origin'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'


# --- 11. Email Settings ---

EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')


# --- 12. Custom Application Settings ---

# Authentication
AUTH_USER_MODEL = 'users.User'
LOGOUT_REDIRECT_URL = 'users:login' # Use namespaced URL

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Business logic constants
COMPANY_NAME = "ATI Smart"
COMPANY_EMAIL = "ibrahim.ati2024@gmail.com"
VERSION = "0.0.1"

ROLES = (
    ("CEO", "Chief Executive Officer"),
    ("HR_MANAGER", "HR Manager"),
    ("MANAGER", "Department Manager"),
    ("EMPLOYEE", "Employee"),
)

DEPARTMENTS = (
    ("HR", "HR and Accounting"),
    ("Cybersecurity", "Cybersecurity"),
    ("Marketing", "Marketing and Sales"),
    ("Software", "Software Engineering"),
    ("Technical", "Technical Department"),
    ("Operations", "Operations Department"),
    ("Data", "Data Science"),
)

DEPARTMENT_JOBS = {
    "HR and Accounting": ["HR Specialist", "Accountant", "Payroll Manager"],
    "Cybersecurity": ["Security Analyst", "Penetration Tester"],
    "Marketing and Sales": ["Sales Manager", "Marketing Specialist"],
    "Software Engineering": ["Software Engineer", "DevOps Engineer"],
    "Technical Department": ["Technical Support", "Field Engineer"],
    "Operations Department": ["Operations Manager", "Logistics Coordinator"],
    "Data Science": ["Data Scientist", "Data Analyst"],
}