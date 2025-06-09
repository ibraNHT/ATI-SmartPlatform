from django.http import HttpResponse
from django.core.management import call_command
from django.contrib.auth import get_user_model

# Temporary views for deployment
def migrate(request):
    call_command('migrate')
    return HttpResponse("Migrations applied")

def createsu(request):
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            'admin', 
            'admin@example.com', 
            'adminpass123'
        )
        return HttpResponse("Superuser created")
    return HttpResponse("Already exists")
