from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.auth import get_user_model
import os

# Temporary views for deployment
def migrate(request):
    try:
        # Run migrations
        call_command('makemigrations')
        call_command('migrate')
        # Collect static files
        call_command('collectstatic', '--noinput', '--clear')
        return HttpResponse("Migrations and static files collected successfully")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

def createsu(request):
    try:
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                'admin', 
                'admin@example.com', 
                'adminpass123'
            )
            return HttpResponse("Superuser created")
        return HttpResponse("Superuser already exists")
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)

def check_db(request):
    """Check if database is properly connected"""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return HttpResponse("Database connection successful")
    except Exception as e:
        return HttpResponse(f"Database error: {str(e)}", status=500)
