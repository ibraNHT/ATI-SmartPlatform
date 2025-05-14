from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.views import generic
from django.urls import reverse_lazy, reverse
from .forms import UserRegistrationForm, ChangePasswordForm, UserValidationForm  # Import the forms
from django.contrib.auth.models import User, Group
from .models import Profile
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib import messages


class UserRegistrationView(generic.CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:validation_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_role'] = self.request.user.profile.role  # Pass the user's role
        return kwargs

    def form_valid(self, form):
        user = form.save() # save User
        role = form.cleaned_data['role']
        #get other fields
        department = form.cleaned_data['department']
        role_description = form.cleaned_data['role_description']
        address = form.cleaned_data['address']
        telephone = form.cleaned_data['telephone']
        gender = form.cleaned_data['gender']
        date_of_birth = form.cleaned_data['date_of_birth']
        #create profile
        profile = Profile.objects.create(
            user=user,
            role=role,
            is_validated=False,
            department=department,
            role_description=role_description,
            address=address,
            telephone=telephone,
            gender=gender,
            date_of_birth=date_of_birth
        )

        group, created = Group.objects.get_or_create(name=role)
        user.groups.add(group)
        messages.success(self.request, 'User registered successfully. Awaiting validation.')
        return super().form_valid(form)



class HRManagerRegistrationView(generic.CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/hr_register.html'
    success_url = reverse_lazy('users:validation_list')  # Redirect to validation list
    def get_success_url(self):
        return reverse('users:hr_dashboard')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user_role'] = self.request.user.profile.role  # Pass the user's role
        return kwargs

    def form_valid(self, form):
        user = form.save()
        profile = Profile.objects.create(user=user, role='HR Manager', is_validated=True)
        hr_manager_group, created = Group.objects.get_or_create(name='HR Manager')
        user.groups.add(hr_manager_group)
        messages.success(self.request, 'HR Manager registered successfully.')
        return super().form_valid(form)

@login_required
def ceo_dashboard(request):
    try:
        hr_manager = Profile.objects.get(role="HR Manager")
        #If an HR manager exists, go to the CEO dashboard
        return render(request, 'users/ceo_dashboard.html')
    except Profile.DoesNotExist:
        #If an HR manager does not exist, redirect to the HR Manager registration page
        return redirect('users:hr_register')  #  Redirect to the HR Manager registration URL



@login_required
def hr_manager_dashboard(request):
    """
    View for the HR Manager's dashboard.
    """
    # Get the HR Manager's profile
    hr_manager_profile = request.user
    #get all users created by this HR manager
    # users = User.objects.filter(profile__created_by=request.user)
    context = {
        'user': hr_manager_profile,
        # 'users': users,
    }
    return render(request, 'users/hr_manager_dashboard.html', context)


@login_required
def user_dashboard(request):
    """
    View for a regular user's dashboard.
    """
    user_profile = request.user.profile
    context = {
        'user_profile': user_profile,
    }
    return render(request, 'users/user_dashboard.html', context)

# Define a view for the hr manager to view the employees (managers and operators)
@login_required
def hr_list(request):
    """
    View for the employees
    """
    # Get the employees (managers and operators) from the database
    employees = Profile.objects.filter(role__in=['Manager', 'Operator', 'CEO', 'HR Manager'])
    
    context={
        'employees': employees,
    }
    return render(request, 'users/hr_list.html', context)



def user_login(request):
    """
    View for user login.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                auth_login(request, user)
                # Redirect based on user role
                if hasattr(user, 'profile'):
                    if user.profile.role == 'CEO':
                        return redirect('users:ceo_dashboard')
                    elif user.profile.role == 'HR Manager':
                        return redirect('users:hr_manager_dashboard')
                    else:
                        return redirect('users:user_dashboard')
                else:
                    return redirect('users:user_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})



def logout_user(request):
    """
    View for user logout.
    """
    auth_logout(request)
    return redirect('users:login')



class ChangePasswordView(generic.FormView):
    """
    View for changing user password.
    """
    form_class = ChangePasswordForm
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = self.request.user
        old_password = form.cleaned_data.get('old_password')
        new_password = form.cleaned_data.get('new_password1')  # Assuming you want new_password1
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            messages.success(self.request, 'Password changed successfully.')
            return super().form_valid(form)
        else:
            form.add_error('old_password', 'Invalid old password.')
            return self.form_invalid(form)



class UserValidationListView(generic.ListView):
    """
    View for listing users awaiting validation.
    """
    model = Profile
    template_name = 'users/validation_list.html'
    context_object_name = 'profiles'

    def get_queryset(self):
        return Profile.objects.filter(is_validated=False)



class UserValidationView(generic.UpdateView):
    """
    View for validating a user.
    """
    model = User
    form_class = UserValidationForm  # You might not need a separate form for this
    template_name = 'users/validate_user.html'
    success_url = reverse_lazy('users:validation_list')

    def form_valid(self, form):
        user = self.get_object()
        user.profile.is_validated = True  # Update the is_validated field
        user.save()
        #send credentials
        generated_password = get_random_string(length=10)
        user.set_password(generated_password)
        user.save()
        send_mail(
            'Your ATI Smart System Credentials',
            f'Your username is {user.username} and your password is {generated_password}. Please change your password upon first login.',
            'ibrahim.ati2024@gmail.com',  # Replace with your sending email
            [user.email],
            fail_silently=False,
        )
        messages.success(self.request, 'User validated and credentials sent.')
        return super().form_valid(form)

