# # src/users/views.py
# from datetime import timezone
# from django.utils import timezone
# from django.urls import reverse, reverse_lazy
# from django.views.generic.edit import CreateView, UpdateView
# from django.contrib.auth.views import LoginView, LogoutView
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth import login, logout, get_user_model
# from django.contrib import messages
# from django.core.mail import send_mail
# from django.conf import settings
# from django.views import View
# from django.views.generic import ListView
# from django.contrib.auth import get_user_model
# from .models import User
# from .forms import UserCreationForm, UserChangeForm, HRManagerCreationForm, EmployeeValidationForm
# from django.contrib.auth.decorators import login_required, user_passes_test
# from django.utils.decorators import method_decorator
# import secrets
# import string
# # import the settings from your settings.py
# from django.conf import settings

# User = get_user_model()

# # --- Utility Functions ---
# def generate_random_password(length=10):
#     """Generate a secure random password"""
#     chars = string.ascii_letters + string.digits + "!@#$%"
#     return ''.join(secrets.choice(chars) for _ in range(length))

# def send_credentials_email(user, username, password):
#     """Send login credentials to user's email"""
#     subject = 'Your ATI Smart Platform Credentials'
#     message = f'''
#     Hello {user.first_name},
    
#     Your account has been created successfully.
    
#     Username: {username}
#     Password: {password}
    
#     Please log in at: {settings.BASE_URL}/login
    
#     © {settings.COMPANY_NAME}
#     '''
#     send_mail(
#         subject,
#         message,
#         settings.DEFAULT_FROM_EMAIL,
#         [user.personal_email],
#         fail_silently=False
#     )

# # --- Decorators ---
# def ceo_required(view_func):
#     """Decorator to ensure only CEO can access a view"""
#     return user_passes_test(lambda u: u.is_superuser)(view_func)

# def hr_required(view_func):
#     """Decorator to ensure only HR can access a view"""
#     return user_passes_test(lambda u: u.role == 'HR_MANAGER')(view_func)

# # --- Authentication Views ---
# class CustomLoginView(LoginView):
#     """
#     Custom login view with remember me functionality and role-based redirect
#     """
#     template_name = 'users/auth/login.html'
#     extra_context = {'company_name': settings.COMPANY_NAME}
    
#     def form_valid(self, form):
#         response = super().form_valid(form)
#         if self.request.POST.get('remember_me'):
#             self.request.session.set_expiry(1209600)  # 2 weeks
            
#         # Role-based redirect
#         user = self.request.user
#         if user.is_superuser:
#             return redirect('users:ceo_dashboard')
#         elif user.role == 'HR_MANAGER':
#             return redirect('users:hr_dashboard')
#         elif user.role == 'MANAGER':
#             return redirect('users:manager_dashboard')
#         return redirect('users:employee_dashboard')

# class CustomLogoutView(LogoutView):
#     """
#     Enhanced logout view with confirmation message
#     """
#     template_name = 'users/auth/logout.html'
#     next_page = reverse_lazy('users:login')

#     def dispatch(self, request, *args, **kwargs):
#         response = super().dispatch(request, *args, **kwargs)
#         messages.info(request, "You have been successfully logged out.")
#         return response

# # --- CEO Views ---
# class CEODashboardView(View):
#     """CEO dashboard showing pending validations and quick actions"""
#     template_name = 'users/ceo/dashboard.html'
    
#     @method_decorator(login_required)
#     @method_decorator(ceo_required)
#     def get(self, request):
#         context = {
#             'total_employees': User.objects.exclude(is_superuser=True).count(),
#             'total_managers': User.objects.filter(role__in=['MANAGER', 'HR_MANAGER']).count(),
#             'total_hr_managers': User.objects.filter(role='HR_MANAGER').count(),
#             'pending_validations': User.objects.filter(is_activated=False, role__in=['EMPLOYEE', 'MANAGER']).count(),
#             'total_departments': len(settings.DEPARTMENTS),
#             'pending_users': User.objects.filter(is_activated=False, role__in=['EMPLOYEE', 'MANAGER']),
#             'company_name': settings.COMPANY_NAME
#         }
#         return render(request, 'users/ceo/dashboard.html', context)

# class HRManagerCreateView(CreateView):
#     """
#     View for CEO to create HR Manager accounts
#     """
#     form_class = HRManagerCreationForm
#     template_name = 'users/ceo/create_hr.html'
#     success_url = reverse_lazy('users:hr_creation_success')
    
#     @method_decorator(login_required)
#     @method_decorator(ceo_required)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['company_name'] = settings.COMPANY_NAME
#         return context
    
#     def form_valid(self, form):
#         user = form.save()
#         user.is_activated = True
#         user.is_staff = True
#         user.role = 'HR_MANAGER'
#         user.username = form.cleaned_data['username']
#         user.password = form.cleaned_data['password']
#         user.set_password(user.password)
#         user.department = 'HR and Accounting'
#         user.role_description = 'HR Manager as the main user of the platform'
#         user.joined_files = form.cleaned_data['joined_files']
#         user.job_title = 'HR Manager'
#         user.save()
        
#         password = form.cleaned_data['password']
#         try:
#             send_credentials_email(user, user.username, password)
#         except Exception as e:
#             print(f"Email failed: {e}")  # Check console for errors
        
#         messages.success(self.request, 'HR Manager created successfully!')
#         return super().form_valid(form)
    
# class EmployeeValidationView(View):
#     template_name = 'users/employee/validate.html'
#     success_url = reverse_lazy('users:validation_success')

#     def get(self, request, id):
#         employee = get_object_or_404(User, id=id, is_activated=False)
#         # Extract year from start_date
#         year = employee.start_date.year if employee.start_date else ''
        
#         # Format department (convert to lowercase and remove spaces)
#         department = employee.department.lower().replace(' ', '') if employee.department else ''
        
#         form = EmployeeValidationForm(initial={
#             'username': f"{employee.last_name.lower()}.ati{year}@{department}"
#         })
#         return render(request, self.template_name, {
#             'employee': employee,
#             'form': form,
#             'company_name': settings.COMPANY_NAME
#         })
        
#     def post(self, request, id):
#         employee = get_object_or_404(User, id=id, is_activated=False)
#         form = EmployeeValidationForm(request.POST)
        
#         if form.is_valid():
#             employee.username = form.cleaned_data['username']
#             employee.is_activated = True
#             employee.set_password(form.cleaned_data['password'])
#             employee.save()
            
#             # Send email with credentials
#             # send_credentials_email(employee, employee.username, form.cleaned_data['password'])
            
#             messages.success(request, f'Employee {employee.first_name} has been validated successfully.')
#             return redirect(self.success_url, id=employee.id)
        
#         return render(request, self.template_name, {
#             'employee': employee,
#             'form': form,
#             'company_name': settings.COMPANY_NAME
#         })
        
        
# # A class view for the ceo to look at the list of employees awaiting validation
# # class EmployeeValidationListView(ListView):
# #     model = User
# #     template_name = 'users/ceo/validation_list.html'
# #     context_object_name = 'pending_employees'
# #     paginate_by = 10
# #     ordering = ['-date_joined']
    
# #     def get_queryset(self):
# #         return User.objects.filter(is_activated=False).order_by('-date_joined')
    
# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         context['company_name'] = settings.COMPANY_NAME
# #         return context
    

# # --- HR Manager Views ---
# class HRDashboardView(View):
#     """HR dashboard showing pending registrations"""
#     template_name = 'users/hr_manager/dashboard.html'
    
#     @method_decorator(login_required)
#     @method_decorator(hr_required)
#     def get(self, request):
#         context = {
#             'total_employees': User.objects.exclude(is_superuser = True).count(),
#             'pending_validations': User.objects.filter(is_activated=False, role__in=["MANAGER", "EMPLOYEE"]).count(),
#             'new_this_month': User.objects.filter(
#                 date_joined__month=timezone.now().month, role__in=["MANAGER", "EMPLOYEE"]
#             ).count(),
#             'total_departments': len(settings.DEPARTMENTS),
#             'recent_employees': User.objects.filter(role__in=['MANAGER', 'EMPLOYEE']).order_by('-date_joined')[:5],
#             'company_name': settings.COMPANY_NAME
#         }
#         return render(request, self.template_name, context)

# # --- Success Views ---
# class SuccessView(View):
#     """Base success view with animations"""
#     template_name = "users/success/generic.html"
#     message = "Action completed successfully"
#     animation_class = "animate__fadeInUp"
    
#     def get(self, request):
#         return render(request, self.template_name, {
#             'message': self.message,
#             'animation_class': self.animation_class,
#             'company_name': settings.COMPANY_NAME
#         })

# # The employee list view returning the employees and the user connected
# class EmployeeListView(ListView):
#     model = User
#     template_name = 'users/employee/list.html'
#     context_object_name = 'employees'
#     paginate_by = 10  # Number of employees per page
    
#     @method_decorator(login_required)
#     def get(self, request, *args, **kwargs):
#         # Firstly a list of all the employees excluding the superuser
#         # Check if the user is authenticated
#         if not request.user.is_authenticated:
#             messages.error(request, "You must be logged in to access this page.")
#             return redirect('users:login')
#         employees = User.objects.exclude(is_superuser=True).order_by('-date_joined')
#         # Filter employees based on the connected user's role
#         if request.user.is_superuser:
#             employees = User.objects.exclude(is_superuser=True).order_by('-date_joined')
#         elif request.user.role == 'HR_MANAGER':
#             employees = User.objects.exclude(is_superuser = True).order_by('-date_joined')
#         elif request.user.role == 'MANAGER':
#             employees = User.objects.filter(department=request.user.department).order_by('-date_joined')
#         else:
#             employees = User.objects.filter(role='').order_by('-date_joined')
            
#         print(f"Connected user: {request.user.is_superuser}, Role: {request.user.role}")
        
#         return render(request, self.template_name, {
#             'employees': employees,
#             'company_name': settings.COMPANY_NAME,
#             'connected_user': request.user
#         })

# class EmployeeCreateSuccessView(View):
#     template_name = 'users/success/employee_created.html'
    
#     def get(self, request):
#         employee = get_object_or_404(User, is_activated=False, role__in=['EMPLOYEE', 'MANAGER'])
#         # Ensure the employee is not activated yet
#         if employee.is_activated:
#             messages.error(request, "This employee is already activated.")
#             return redirect('users:employee_list')
#         return render(request, self.template_name, {
#             'employee': employee,
#             'company_name': settings.COMPANY_NAME
#         })

# class HRCreateSuccessView(View):
#     template_name = 'users/success/hr_created.html'
    
#     def get(self, request):
#         hr_manager = get_object_or_404(User.objects.filter(role='HR_MANAGER', is_activated=True))
#         return render(request, self.template_name, {
#             'hr_manager': hr_manager,
#             'company_name': settings.COMPANY_NAME
#         })

# class ValidationSuccessView(View):
#     template_name = 'users/employee/validated.html'
    
#     def get(self, request):
#         # employee = get_object_or_404(User.objects.filter(username=request.username))
#         # Ensure the employee is activated and has a role
#         # if not employee.is_activated or employee.role not in ['EMPLOYEE', 'MANAGER', 'HR_MANAGER']:
#         #     messages.error(request, "This employee is not activated or does not have a valid role.")
#         #     return redirect('users:ceo_employee_list')
#         return render(request, self.template_name, {
#             # 'employee': employee,
#             'company_name': settings.COMPANY_NAME
#         })

# # --- Manager Views ---
# class ManagerDashboardView(View):
#     template_name = 'users/manager/dashboard.html'
    
#     @method_decorator(login_required)
#     def get(self, request):
#         # For managers, show team count - for regular employees, show department count and the department name
#         department_name = request.user.department if request.user.department else "No Department"
#         employees = User.objects.filter(department=request.user.department).exclude(id=request.user.id)
#         # Check if the user is authenticated
#         if not request.user.is_authenticated:
#             messages.error(request, "You must be logged in to access this page.")
#             return redirect('users:login')
        
#         if request.user.role == 'MANAGER':
#             team_members = User.objects.filter(
#             department=request.user.department
#             ).exclude(id=request.user.id).count()
#         else:
#             team_members = User.objects.filter(
#             department=request.user.department
#             ).count()
            
#         return render(request, self.template_name, {
#             'team_members': team_members,
#             'company_name': settings.COMPANY_NAME,
#             'department_name': department_name,
#             'employees': employees
#         })

# # --- Employee Views ---
# from django.views.generic import TemplateView
# from django.utils import timezone
# # from tasks.models import Task
# # from communication.models import Message
# # from events.models import Event
# from datetime import timedelta

# # class ManagerDashboardView(View):
# #     template_name = 'users/manager/dashboard.html'
    
# #     @method_decorator(login_required)
# #     def get(self, request):
# #         # For managers, show team count - for regular employees, show department count and the department name
# #         department_name = request.user.department if request.user.department else "No Department"
# #         # Check if the user is authenticated
# #         if not request.user.is_authenticated:
# #             messages.error(request, "You must be logged in to access this page.")
# #             return redirect('users:login')
        
# #         if request.user.role == 'MANAGER':
# #             team_members = User.objects.filter(
# #             department=request.user.department
# #             ).exclude(id=request.user.id).count()
# #         else:
# #             team_members = User.objects.filter(
# #             department=request.user.department
# #             ).count()
            
# #         return render(request, self.template_name, {
# #             'team_members': team_members,
# #             'company_name': settings.COMPANY_NAME,
# #             'department_name': department_name
# #         })

# class EmployeeDashboardView(TemplateView):
#     template_name = 'users/employee/dashboard.html'

#     @method_decorator(login_required)
#     def get(self, request):
#         employee_manager = User.objects.filter(department=request.user.department, role='MANAGER')[0]
        
#         if not request.user.is_authenticated:
#             messages.error(request, "You must be logged in to access this page")
#             return redirect('users:login')
        

#         return render(request, self.template_name, {
#             'employee_manager': employee_manager,
#             'company_name': settings.COMPANY_NAME,
#             'department_name': request.user.department
#         })
        
# class EmployeeCreateView(CreateView):
#     """View for HR to register new employees"""
#     form_class = UserCreationForm
#     template_name = 'users/hr_manager/create_employee.html'
#     # Add the success_url variable with the user id
#     success_url = reverse_lazy('users:employee_creation_success')
#     # Add the company name as an extrat context
#     extra_context = {'company_name': settings.COMPANY_NAME}
    
#     @method_decorator(login_required)
#     @method_decorator(hr_required)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
    
#     def form_valid(self, form):
#         employee = form.save(commit=False)
#         employee.is_activated = False  # Requires CEO validation
#         employee.email= ''  # Set to empty string
#         employee.username = employee.personal_email.split('@')[0] + employee.start_date.strftime('%Y%m%d')
#         employee.save()
#         messages.success(self.request, 'Employee registered! Waiting for CEO validation.')
#         return super().form_valid(form)
    
#     def get_success_url(self):
#         # return reverse('users:employee_creation_success', args=[self.object.id])
#         return reverse('users:employee_creation_success')
    
# # A class view called AboutMeView for every users to look at their account details with just simple informations
# class AboutMeView(View):
#     template_name = 'users/auth/about_me.html'
    
# #    @method_decorator(login_required)
#     def get(self, request):
#         return render(request, self.template_name, {
#             'user': request.user,
#             'company_name': settings.COMPANY_NAME
#         })

# # --- A view to view a unique employee for the CEO, the HR Manager and the other managers ---
# class EmployeeDetailView(View):
#     template_name = 'users/employee/detail.html'
    
#     @method_decorator(login_required)
#     def get(self, request, id):
#         employee = get_object_or_404(User, id=id)
#         connected_user = request.user
#         return render(request, self.template_name, {
#             'employee': employee,
#             'connected_user': connected_user,
#             # 'is_ceo': connected_user.is_superuser,
#             # 'is_hr_manager': connected_user.role == 'HR_MANAGER',
#             # 'is_manager': connected_user.role == 'MANAGER',
#             # 'is_employee': connected_user.role == 'EMPLOYEE',
#             'company_name': settings.COMPANY_NAME
#         })

# # --- A view to delete an employee for the CEO ---
# class EmployeeDeleteView(View):
#     template_name = 'users/ceo/delete_employee.html'
    
#     @method_decorator(login_required)
#     @method_decorator(ceo_required)
#     def get(self, request, id):
#         employee = get_object_or_404(User, id=id)
#         return render(request, self.template_name, {
#             'employee': employee,
#             'company_name': settings.COMPANY_NAME
#         })
    
#     def post(self, request, id):
#         employee = get_object_or_404(User, id=id)
#         employee.delete()
#         messages.success(request, f'Employee {employee.first_name} has been deleted successfully.')
#         return redirect('users:ceo_employee_list')  # Redirect to the employee list after deletion
    
# # class EmployeeEditView(UpdateView):
# #     model = User
# #     form_class = UserChangeForm
# #     template_name = 'users/hr_manager/edit_employee.html'
# #     success_url = reverse_lazy('users:employee_list')
    
# #     @method_decorator(login_required)
# #     @method_decorator(hr_required)
# #     def dispatch(self, *args, **kwargs):
# #         return super().dispatch(*args, **kwargs)
    
# #     def get_context_data(self, **kwargs):
# #         context = super().get_context_data(**kwargs)
# #         context['company_name'] = settings.COMPANY_NAME
# #         return context
    
# #     def form_valid(self, form):
# #         messages.success(self.request, 'Employee details updated successfully!')
# #         return super().form_valid(form)

# # --- A view to edit an employee for the HR Manager ---
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.utils.translation import gettext as _

# class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
#     model = User
#     form_class = UserChangeForm
#     template_name = 'users/hr_manager/edit_employee.html'  # match your template path
#     context_object_name = 'employee'
#     success_url = reverse_lazy('users:employee_list')  # adjust to your success URL

#     @method_decorator(login_required)
#     @method_decorator(hr_required)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
#     # Ensure the user is logged in and has HR permissions
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['company_name'] = settings.COMPANY_NAME  # or get from settings
#         return context

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         messages.success(
#             self.request,
#             _(f"{self.object.get_full_name()}'s profile was updated successfully!")
#         )
#         return response

#     def form_invalid(self, form):
#         messages.error(
#             self.request,
#             _("Please correct the errors below.")
#         )
#         return super().form_invalid(form)

#     # Optional: Add permission mixin if needed
#     # from django.contrib.auth.mixins import PermissionRequiredMixin
#     # permission_required = 'users.change_employee'
#     # raise_exception = True

from datetime import datetime, timedelta
# src/users/views.py
import os
import sys
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views import View
from django.views.generic import ListView, TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _
import secrets
import string

# Ensure the 'src' directory is in the Python path for module imports
# This helps manage.py find 'Ati_smart_platform' and other modules
project_root = os.path.dirname(os.path.abspath(__file__))
# Navigate up from views.py -> users/ -> src/ -> ATI-SmartPlatform/
repo_root = os.path.abspath(os.path.join(project_root, '..', '..', '..'))
src_path = os.path.join(repo_root, 'src')

if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Import models and forms after path adjustment
from Ati_smart_platform.settings import DEPARTMENTS # Import DEPARTMENTS from settings.py
from .models import User # Assuming User model is defined in .models
from .forms import (
    UserCreationForm, EmployeeEditForm, EmployeeDeleteForm,
    HRManagerCreationForm, EmployeeValidationForm
)

# Get the custom User model
User = get_user_model()

# --- Utility Functions ---
def generate_random_password(length=10):
    """Generate a secure random password for initial account setup."""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(chars) for _ in range(length))

def send_credentials_email(user_instance, username, password):
    """
    Send login credentials to user's personal email.
    Assumes settings.BASE_URL and settings.COMPANY_NAME are defined.
    """
    subject = 'Your ATI Smart Platform Credentials'
    message = f'''
Hello {user_instance.first_name},
    
Your account has been created/validated successfully.
    
Username: {username}
Password: {password}
    
Please log in at: {getattr(settings, 'BASE_URL', 'http://localhost:8000')}/users/login/
    
© {getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')}
'''
    try:
        send_mail(
            subject,
            message,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@atisys.com'),
            [user_instance.personal_email],
            fail_silently=False
        )
        # messages.success(None, f"Credentials sent to {user_instance.personal_email}.") # Messages need request
    except Exception as e:
        # messages.error(None, f"Failed to send email to {user_instance.personal_email}: {e}") # Messages need request
        print(f"Error sending email to {user_instance.personal_email}: {e}") # For debugging


# --- Predicate Functions for Decorators ---
# These functions define the test for user roles. They return True or False.
def is_ceo_user(user):
    return user.is_superuser

def is_hr_manager_user(user):
    return user.is_authenticated and user.role == 'HR_MANAGER'

def is_manager_user(user):
    return user.is_authenticated and user.role == 'MANAGER'

def is_employee_user(user):
    return user.is_authenticated and user.role == 'EMPLOYEE'


# --- Authentication Views ---
class CustomLoginView(LoginView):
    """
    Custom login view with remember me functionality and role-based redirect.
    """
    template_name = 'users/auth/login.html'
    extra_context = {'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')}
    
    def form_valid(self, form):
        """
        If the form is valid, log the user in and redirect based on their role.
        """
        remember_me = self.request.POST.get('remember_me')
        login(self.request, form.get_user(), backend='django.contrib.auth.backends.ModelBackend')

        if remember_me:
            self.request.session.set_expiry(1209600)  # 2 weeks
        else:
            self.request.session.set_expiry(0) # Session expires when browser is closed

        user = self.request.user
        if user.is_superuser:
            messages.success(self.request, f"Welcome CEO {user.first_name}!")
            return redirect(reverse_lazy('users:ceo_dashboard'))
        elif user.role == 'HR_MANAGER':
            messages.success(self.request, f"Welcome HR Manager {user.first_name}!")
            return redirect(reverse_lazy('users:hr_dashboard'))
        elif user.role == 'MANAGER':
            messages.success(self.request, f"Welcome Manager {user.first_name}!")
            return redirect(reverse_lazy('users:manager_dashboard'))
        elif user.role == 'EMPLOYEE':
            messages.success(self.request, f"Welcome Employee {user.first_name}!")
            return redirect(reverse_lazy('users:employee_dashboard'))
        else:
            messages.warning(self.request, "Your role is not defined. Redirecting to generic dashboard.")
            return redirect(reverse_lazy('users:about_me')) # Fallback for undefined roles

    def form_invalid(self, form):
        """
        If the form is invalid, display an error message.
        """
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

class CustomLogoutView(LogoutView):
    """
    Enhanced logout view with confirmation message.
    """
    template_name = 'users/auth/logout.html' # Consider a simple redirect or modal logout
    next_page = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            messages.info(request, "You have been successfully logged out.")
        return super().dispatch(request, *args, **kwargs)


# --- CEO Views ---
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_ceo_user, login_url=reverse_lazy('users:login')), name='dispatch')
class CEODashboardView(TemplateView):
    """CEO dashboard showing key metrics and pending validations."""
    template_name = 'users/ceo/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if HR Manager exists for initial setup redirection
        hr_manager_exists = User.objects.filter(role='HR_MANAGER', is_activated=True).exists()

        context.update({
            'hr_manager_exists': hr_manager_exists,
            'total_employees': User.objects.filter(is_superuser=False).count(),
            'total_managers': User.objects.filter(role__in=['MANAGER', 'HR_MANAGER']).count(),
            'total_hr_managers': User.objects.filter(role='HR_MANAGER').count(),
            'pending_validations': User.objects.filter(is_activated=False, role__in=['EMPLOYEE', 'MANAGER']).count(),
            'total_departments': len(DEPARTMENTS),
            'pending_users': User.objects.filter(is_activated=False, role__in=['EMPLOYEE', 'MANAGER']).order_by('-date_joined'),
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        })
        return context

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_ceo_user, login_url=reverse_lazy('users:login')), name='dispatch')
class HRManagerCreateView(CreateView):
    """
    View for CEO to create HR Manager accounts.
    """
    form_class = HRManagerCreationForm
    template_name = 'users/ceo/create_hr.html'
    success_url = reverse_lazy('users:hr_creation_success')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        return context
    
    def form_valid(self, form):
        """
        If the form is valid, save the HR Manager and send credentials.
        The form's save method handles role, department, activation, and password hashing.
        """
        try:
            user = form.save() # The form's save method sets password, role, is_activated, etc.
            
            # Send credentials only after successful save and activation
            send_credentials_email(user, user.username, form.cleaned_data['password'])
            
            messages.success(self.request, f"HR Manager '{user.get_full_name()}' created successfully! Credentials sent to their personal email.")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred: {e}. Please try again.")
            print(f"Error in HRManagerCreateView form_valid: {e}")
            return self.form_invalid(form) # Re-render form with errors

    def form_invalid(self, form):
        """
        If the form is invalid, display an error message and re-render the form.
        """
        messages.error(self.request, "Error creating HR Manager. Please correct the highlighted errors.")
        return render(self.request, self.template_name, {'form': form, 'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_ceo_user, login_url=reverse_lazy('users:login')), name='dispatch')
class EmployeeValidationView(View):
    """
    View for CEO to validate employees.
    Allows CEO to set username and password for a non-activated employee.
    """
    template_name = 'users/employee/validate.html'
    form_class = EmployeeValidationForm

    def get(self, request, id): # Changed employee_id to id as per your model
        """
        Display the employee validation form.
        Initializes username based on employee's last name and start year.
        """
        employee = get_object_or_404(User, id=id, is_activated=False)
        
        # Initial username suggestion logic
        username_initial = ""
        if employee.last_name and employee.start_date:
            year = employee.start_date.year
            department_slug = employee.department.lower().replace(' ', '').replace('&', '') if employee.department else ''
            username_initial = f"{employee.last_name.lower()}.ati{year}@{department_slug}"
        
        form = self.form_class(initial={
            'username': username_initial
        })
        return render(request, self.template_name, {
            'employee': employee,
            'form': form,
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        })
        
    def post(self, request, id): # Changed employee_id to id
        """
        Process the employee validation form.
        Activates the employee and sends credentials.
        """
        employee = get_object_or_404(User, id=id, is_activated=False)
        form = self.form_class(request.POST)
        
        if form.is_valid():
            new_username = form.cleaned_data['username']
            new_password = form.cleaned_data['password']

            # Check if chosen username is already taken by an activated user
            if User.objects.filter(username=new_username, is_activated=True).exclude(id=employee.id).exists():
                messages.error(request, "This username is already taken by another active user. Please choose a different one.")
                return render(request, self.template_name, {
                    'employee': employee,
                    'form': form,
                    'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
                })

            employee.username = new_username
            employee.set_password(new_password) # Hash the password
            employee.is_activated = True
            employee.save()
            
            send_credentials_email(employee, new_username, new_password)
            
            messages.success(request, f"Employee '{employee.get_full_name()}' validated successfully! Credentials sent to their personal email.")
            return redirect(reverse_lazy('users:validation_success'))
        else:
            messages.error(request, "Error validating employee. Please correct the highlighted errors.")
            return render(request, self.template_name, {
                'employee': employee,
                'form': form,
                'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
            })

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_ceo_user, login_url=reverse_lazy('users:login')), name='dispatch')
class EmployeeDeleteView(View):
    """
    View for CEO to delete an employee account.
    """
    template_name = 'users/ceo/delete_employee.html'
    
    def get(self, request, id): # Changed employee_id to id
        """
        Display confirmation page for employee deletion.
        """
        employee = get_object_or_404(User, id=id)
        return render(request, self.template_name, {
            'employee': employee,
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        })
    
    def post(self, request, id): # Changed employee_id to id
        """
        Process employee deletion.
        """
        employee = get_object_or_404(User, id=id)
        try:
            employee.delete()
            messages.success(request, f"Employee '{employee.get_full_name()}' has been deleted successfully.")
            return redirect(reverse_lazy('users:ceo_employees_list'))
        except Exception as e:
            messages.error(request, f"Error deleting employee '{employee.get_full_name()}': {e}")
            return redirect(reverse_lazy('users:ceo_employees_list'))


# --- HR Manager Views ---
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_hr_manager_user, login_url=reverse_lazy('users:login')), name='dispatch')
class HRDashboardView(TemplateView):
    """HR dashboard showing key HR metrics and recent employee registrations."""
    template_name = 'users/hr_manager/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        all_employees = User.objects.exclude(is_superuser=True) # Exclude only the CEO

        context.update({
            'total_employees': all_employees.count(),
            'pending_validations': all_employees.filter(is_activated=False, role__in=["MANAGER", "EMPLOYEE"]).count(),
            'new_this_month': all_employees.filter(
                date_joined__month=timezone.now().month, 
                date_joined__year=timezone.now().year,
                role__in=["MANAGER", "EMPLOYEE"]
            ).count(),
            'total_departments': len(DEPARTMENTS),
            'recent_employees': all_employees.filter(role__in=['MANAGER', 'EMPLOYEE']).order_by('-date_joined')[:5],
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        })
        return context

@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_hr_manager_user, login_url=reverse_lazy('users:login')), name='dispatch')
class EmployeeCreateView(CreateView):
    """
    View for HR Manager to register new employees.
    """
    form_class = UserCreationForm
    template_name = 'users/hr_manager/create_employee.html'
    success_url = reverse_lazy('users:employee_creation_success')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        return context
    
    def form_valid(self, form):
        """
        If the form is valid, save the employee (as non-activated) and notify.
        The form's save method handles password hashing and basic user creation.
        """
        try:
            employee = form.save(commit=False)
            employee.is_activated = False  # Employee requires CEO validation
            employee.save() # Save the user after setting is_activated
            
            messages.success(self.request, f"Employee '{employee.get_full_name()}' registered successfully! Waiting for CEO validation.")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred: {e}. Please try again.")
            print(f"Error in EmployeeCreateView form_valid: {e}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, display an error message and re-render the form.
        """
        messages.error(self.request, "Error creating employee. Please correct the highlighted errors.")
        return render(self.request, self.template_name, {'form': form, 'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_hr_manager_user, login_url=reverse_lazy('users:login')), name='dispatch')
class EmployeeUpdateView(UpdateView): # Changed from LoginRequiredMixin, UpdateView to just UpdateView as decorators handle login
    """
    View for HR Manager to edit an employee's personal details.
    """
    model = User
    form_class = EmployeeEditForm # Using EmployeeEditForm for personal details
    template_name = 'users/hr_manager/edit_employee.html'
    context_object_name = 'employee'
    success_url = reverse_lazy('users:hr_employees_list') # Redirect to HR's employee list

    def get_object(self, queryset=None):
        """Retrieve the employee based on id from URL kwargs."""
        user_id = self.kwargs.get('id') # Changed employee_id to id
        return get_object_or_404(User, id=user_id)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        return context

    def form_valid(self, form):
        """
        If the form is valid, save the changes and display a success message.
        """
        try:
            response = super().form_valid(form)
            messages.success(self.request, _(f"{self.object.get_full_name()}'s profile was updated successfully!"))
            return response
        except Exception as e:
            messages.error(self.request, f"An unexpected error occurred: {e}. Please try again.")
            print(f"Error in EmployeeUpdateView form_valid: {e}")
            return self.form_invalid(form)


    def form_invalid(self, form):
        """
        If the form is invalid, display an error message and re-render the form.
        """
        messages.error(self.request, _("Please correct the errors below when updating the employee profile."))
        return super().form_invalid(form)


# --- Manager Views ---
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_manager_user, login_url=reverse_lazy('users:login')), name='dispatch')
class ManagerDashboardView(TemplateView):
    """Department Manager dashboard showing team metrics."""
    template_name = 'users/manager/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        department_name = user.department if user.department else "Unknown Department"
        
        # Managers see employees in their department, excluding themselves
        team_members = User.objects.filter(
            department=user.department, 
            is_activated=True, 
            is_superuser=False, # Exclude CEO
        ).exclude(id=user.id).count() # Exclude self
        
        department_employees = User.objects.filter(
            department=user.department, 
            is_activated=True, 
            is_superuser=False,
        ).exclude(id=user.id).order_by('last_name', 'first_name')

        context.update({
            'team_members': team_members,
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform'),
            'department_name': department_name,
            'department_employees': department_employees
        })
        return context

# --- Employee Views ---
@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_employee_user, login_url=reverse_lazy('users:login')), name='dispatch')
class EmployeeDashboardView(TemplateView):
    """Individual Employee dashboard."""
    template_name = 'users/employee/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        employee_manager = None
        if user.department:
            # Try to find a manager in the same department
            manager_qs = User.objects.filter(
                department=user.department, 
                role='MANAGER', 
                is_activated=True
            )
            if manager_qs.exists():
                employee_manager = manager_qs.first() # Get the first manager if multiple exist

        context.update({
            'employee_manager': employee_manager,
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform'),
            'department_name': user.department if user.department else "Unknown Department"
        })
        return context

@method_decorator(login_required, name='dispatch')
class AboutMeView(TemplateView):
    """View for any user to see their own account details."""
    template_name = 'users/auth/about_me.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user_profile': self.request.user, # The logged-in user's profile
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        })
        return context

# --- Common Employee Listing/Detail View ---
@method_decorator(login_required, name='dispatch')
class EmployeeListView(ListView):
    """
    Common view for CEO, HR Manager, and Department Manager to list employees.
    Filters employees based on the logged-in user's role.
    """
    model = User
    template_name = 'users/employee/list.html'
    context_object_name = 'employees'
    paginate_by = 10
    
    def dispatch(self, *args, **kwargs):
        # Basic check to ensure only authorized roles can access this list
        user = self.request.user
        if not (user.is_superuser or user.role in ['HR_MANAGER', 'MANAGER']):
            messages.error(self.request, "You do not have permission to view employee lists.")
            return redirect(reverse_lazy('users:login')) # Or a more appropriate dashboard
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        """
        Returns the queryset of employees based on the logged-in user's role.
        """
        user = self.request.user
        # Start with all non-superusers (excluding the CEO itself)
        queryset = User.objects.order_by('date_joined').exclude(is_superuser=True)

        if user.is_superuser:
            # CEO sees all activated employees (excluding CEO itself)
            queryset = queryset # The CEO will see all the employees, activated or not
            messages.info(self.request, "Displaying all activated employees.")
        elif user.role == 'HR_MANAGER':
            # HR Manager sees all employees (activated and non-activated, excluding CEO)
            queryset = queryset.filter(is_superuser=False) # All non-superusers
            messages.info(self.request, "Displaying all registered employees (including those awaiting validation).")
        elif user.role == 'MANAGER':
            # Department Manager sees employees in their department who are activated
            queryset = queryset.filter(department=user.department, is_activated=True, is_superuser=False)
            messages.info(self.request, f"Displaying employees in your department: {user.department}.")
        else:
            messages.error(self.request, "You do not have the required role to view this list.")
            queryset = User.objects.none() # Return an empty queryset
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        context['connected_user'] = self.request.user
        return context

class EmployeeDetailView(View):
    """
    Common view for CEO, HR Manager, and Department Manager to view a single employee's details.
    """
    template_name = 'users/employee/detail.html'

    @method_decorator(login_required, name='dispatch')
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        employee_id_from_url = self.kwargs.get('id') # Changed employee_id to id
        employee = get_object_or_404(User, id=employee_id_from_url)

        # Ensure that only authorized roles can view employee details
        if user.is_superuser: # CEO can view anyone
            pass
        elif user.role == 'HR_MANAGER': # HR can view anyone
            pass
        elif user.role == 'MANAGER': # Manager can only view employees in their department
            if employee.department != user.department:
                messages.error(request, "You do not have permission to view details of employees outside your department.")
                return redirect(reverse_lazy('users:manager_dashboard'))
        else: # Regular employee or undefined role cannot view other employee details
            if user.id != employee_id_from_url: # Allow employee to view their own profile via about_me
                messages.error(request, "You do not have permission to view other employee details.")
                return redirect(reverse_lazy('users:employee_dashboard'))

        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        employee_id = self.kwargs.get('id')
        employee = get_object_or_404(User, id=employee_id)
        context = {'employee': employee}
        return render(request, self.template_name, context)


    def get(self, request, id): # Changed employee_id to id
        """
        Retrieves and displays a single employee's details.
        """
        employee = get_object_or_404(User, id=id)
        context = {
            'employee': employee,
            'connected_user': request.user,
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        }
        return render(request, self.template_name, context)


# --- Success Views (Generic and Specific) ---
class SuccessView(TemplateView):
    """Base success view with animations. To be inherited."""
    template_name = "users/success/generic.html"
    message = "Action completed successfully!"
    animation_class = "animate__fadeInUp" # Requires animate.css or similar CSS library
    redirect_url = reverse_lazy('users:login') # Default redirect

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'message': self.message,
            'animation_class': self.animation_class,
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform'),
            'redirect_url': self.redirect_url
        })
        return context

class EmployeeCreateSuccessView(SuccessView):
    """Success view for employee registration by HR Manager."""
    template_name = 'users/success/employee_created.html'
    message = "Employee registered successfully! Awaiting CEO validation."
    redirect_url = reverse_lazy('users:hr_dashboard') # Go back to HR dashboard

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['register_another_url'] = reverse_lazy('users:create_employee')
        context['go_to_dashboard_url'] = reverse_lazy('users:hr_dashboard')
        return context

class HRCreateSuccessView(SuccessView):
    """Success view for HR Manager creation by CEO."""
    template_name = 'users/success/hr_created.html'
    message = "HR Manager account created successfully!"
    redirect_url = reverse_lazy('users:ceo_dashboard') # Go back to CEO dashboard

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hr_manager'] = User.objects.filter(role='HR_MANAGER').first()
        context['go_to_dashboard_url'] = reverse_lazy('users:ceo_dashboard')
        return context

class ValidationSuccessView(SuccessView):
    """Success view for employee validation by CEO."""
    template_name = 'users/employee/validated.html'
    message = "Employee account validated successfully!"
    redirect_url = reverse_lazy('users:ceo_dashboard') # Go back to CEO dashboard

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['go_to_validation_list_url'] = reverse_lazy('users:ceo_dashboard') # Assuming CEO dashboard shows pending validations
        context['go_to_dashboard_url'] = reverse_lazy('users:ceo_dashboard')
        return context