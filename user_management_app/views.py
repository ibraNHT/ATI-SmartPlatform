from django.shortcuts import render

# Create your views here.

# External registering page
from django.shortcuts import render, redirect
from .forms import UserRegistrationForm
from .models import CustomUser, ValidationLog

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Ne peut pas se connecter avant validation
            user.save()
            return redirect('registration_success')
    else:
        form = UserRegistrationForm()
    return render(request, '/user_management_app/registrations/registration.html', {'form': form})

# User registration success view
def registration_success(request):
    return render(request, '/user_management_app/registrations/registration_success.html')


from django.contrib.auth.decorators import login_required
from .models import CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def pending_users(request):
    if request.user.role not in ['superadmin', 'manager']:
        return redirect('unauthorized')
    users = User.objects.filter(is_validated=False)
    return render(request, 'dashboard/pending_users.html', {'users': users})


# User validation view
@login_required
def validate_user(request, user_id):
    if request.user.role not in ['superadmin', 'manager']:
        return redirect('unauthorized')
    
    user = CustomUser.objects.get(id=user_id)
    user.is_validated = True
    user.is_active = True
    user.save()

    # Créer une entrée de validation
    ValidationLog.objects.create(utilisateur=user, valide_par=request.user)
    return redirect('pending_users')