"""
Django settings for ati_smart_system project.
"""

import os
from pathlib import Path
import environ  # Import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# ===============================
# Environment Variables
# ===============================
env = environ.Env()  # Initialize environ
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))  # Read .env file

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
#  Use a strong, random key in production.  You can generate one with:
#  python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
SECRET_KEY = env('SECRET_KEY')  # Get SECRET_KEY from .env

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG')  # Get DEBUG from .env

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')  # Get ALLOWED_HOSTS from .env


# Application definition
#  Add your apps here.  'users' is our user management app.
INSTALLED_APPS = [
    'django.contrib.admin',      # Django's built-in admin site (optional)
    'django.contrib.auth',       # Django's authentication system
    'django.contrib.contenttypes',  # For generic relations
    'django.contrib.sessions',     # For session management
    'django.contrib.messages',     # For message framework
    'django.contrib.staticfiles',   # For serving static files (CSS, JS, images)
    'users',                   # Our 'users' app
    'rest_framework',          # Django REST Framework (for the API)
    'bootstrap5',       # Django Bootstrap 5
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  #  CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Authentication
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ati_smart_system.urls'  #  Project's main URL configuration

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  #  Where your project-level templates are stored
        'APP_DIRS': True,  #  Django will also look for templates in app directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  #  Required for user authentication
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'ati_smart_system.wsgi.application'  #  WSGI entry point


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
#  Use PostgreSQL in production.  For development, SQLite is fine.
DATABASES = {
    'default': env.db('DATABASE_URL')  # Get DATABASE_URL from .env
}

#  If you want to use PostgreSQL in development, configure it here:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'your_database_name',
#         'USER': 'your_username',
#         'PASSWORD': 'your_password',
#         'HOST': 'localhost',
#         'PORT': '5432',
#     }
# }


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
#  These settings control password strength requirements.
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
#  Set your project's language and timezone.
LANGUAGE_CODE = 'en-us'  #  English (US)
TIME_ZONE = 'UTC'      #  Coordinated Universal Time
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
#  Where Django will look for your static files.
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles' # For production

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#  Email settings (for sending credentials)
#  Configure these with your email provider's settings.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'  # Or use 'django.core.mail.backends.console.EmailBackend' for testing
EMAIL_HOST = 'gmail.google.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ibrahim.ati2024@gmail.com'
EMAIL_HOST_PASSWORD = 'AcheteIci2024#'
DEFAULT_FROM_EMAIL = 'ibrahim.ati2024@gmail.com'
SERVER_EMAIL = 'ibrahim.ati2024@gmail.com'

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication', #  For JWT Authentication
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', #  Require authentication by default
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

#  JWT settings (if you choose to use JWT)
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,  # Use the same SECRET_KEY
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
}

# Bootstrap 5
BOOTSTRAP5 = {
    "css_url": {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css",
        "integrity": "sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN",
        "crossorigin": "anonymous",
    },
    "js_url": {
        "url": "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js",
        "integrity": "sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq4vNWg",
        "crossorigin": "anonymous",
    },
}