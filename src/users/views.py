from datetime import datetime, timedelta
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.utils.decorators import method_decorator
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


from .models import User, DEPARTMENTS # Import DEPARTMENTS from models.py
from .forms import (
    UserCreationForm, EmployeeEditForm, EmployeeDeleteForm, # Corrected import for EmployeeEditForm
    HRManagerCreationForm, EmployeeValidationForm
)

# Get the custom User model
User = get_user_model()

# --- Utility Functions ---
def generate_random_password(length=10):
    """Generate a secure random password for initial account setup."""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(chars) for _ in range(length))

def send_credentials_email(user, username, password):
    """
    Send login credentials to user's personal email.
    Returns True if email was sent successfully, False otherwise.
    """
    subject = 'Your ATI Smart Platform Credentials'
    message = f'''
Hello {user.first_name},
    
Your account has been created/validated successfully.
    
Username: {username}
Password: {password}
    
Please log in at: {settings.BASE_URL}/login

Best regards,
{settings.COMPANY_NAME}
'''
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.personal_email],
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")  # For debugging
        return False

''' Users reqquirements methods
# --- Decorators ---
def ceo_required(view_func):
    """ Decorator to ensure only CEO (is_superuser) can access a view """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('users:login')
        return view_func(request, *args, **kwargs)
    return wrapper

# Create a method decorator version for class-based views
def ceo_required_method(view_method):
    # Decorator to ensure only CEO (is_superuser) can access a method.
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('users:login')
        return view_method(self, request, *args, **kwargs)
    return wrapper

def hr_required(view_func):
    # Decorator to ensure only HR Manager can access a view.
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.role == 'HR_MANAGER', login_url=reverse_lazy('users:login')))
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def manager_required(view_func):
    # Decorator to ensure only Department Manager can access a view.
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.role == 'MANAGER', login_url=reverse_lazy('users:login')))
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def employee_required(view_func):
    # Decorator to ensure only Employee can access a view.
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.role == 'EMPLOYEE', login_url=reverse_lazy('users:login')))
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view 
    
'''


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
        login(self.request, form.get_user(), backend='django.contrib.auth.backends.ModelBackend') # Specify backend for clarity

        if remember_me:
            self.request.session.set_expiry(1209600)  # 2 weeks
        else:
            self.request.session.set_expiry(0) # Session expires when browser is closed

        user = self.request.user
        if user.is_superuser:
            messages.success(self.request, f"Welcome CEO {user.first_name}!")
            return redirect('users:ceo_dashboard')
        elif user.role == 'HR_MANAGER':
            messages.success(self.request, f"Welcome HR Manager {user.first_name}!")
            return redirect('users:hr_dashboard')
        elif user.role == 'MANAGER':
            messages.success(self.request, f"Welcome Manager {user.first_name}!")
            return redirect('users:manager_dashboard')
        elif user.role == 'EMPLOYEE':
            messages.success(self.request, f"Welcome Employee {user.first_name}!")
            return redirect('users:employee_dashboard')
        else:
            messages.warning(self.request, "Your role is not defined. Redirecting to generic dashboard.")
            return redirect('users:about_me') # Fallback for undefined roles

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
class CEODashboardView(LoginRequiredMixin, TemplateView):
    """CEO dashboard showing key metrics and pending validations."""
    template_name = 'users/ceo/dashboard.html'

    # @method_decorator(ceo_required_method)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'total_employees': User.objects.exclude(is_activated=False).count(),
            'total_managers': User.objects.filter(role__in=['MANAGER', 'HR_MANAGER']).count(),
            'total_hr_managers': User.objects.filter(role='HR_MANAGER').count(),
            'pending_validations': User.objects.filter(is_activated=False, role__in=['EMPLOYEE', 'MANAGER']).count(),
            'total_departments': len(settings.DEPARTMENTS),
            'pending_users': User.objects.filter(is_activated=False, role__in=['EMPLOYEE', 'MANAGER']),
            'company_name': settings.COMPANY_NAME
        })
        return context

class HRManagerCreateView(CreateView):
    """
    View for CEO to create HR Manager accounts.
    """
    form_class = HRManagerCreationForm
    template_name = 'users/ceo/create_hr.html'
    success_url = reverse_lazy('users:hr_creation_success')
    
    # @method_decorator(ceo_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        return context
    
    def form_valid(self, form):
        """
        If the form is valid, save the HR Manager and send credentials.
        The form's save method handles role, department, activation, and password hashing.
        """
        user = form.save() # The form's save method sets password, role, is_activated, etc.
        
        # Send credentials only after successful save and activation
        email_sent = send_credentials_email(user, user.username, form.cleaned_data['password'])  # Password from form

        if email_sent:
            messages.success(self.request,
                            f"HR Manager '{user.get_full_name()}' created successfully! Credentials sent to their personal email.")
        else:
            messages.warning(self.request,
                            f"HR Manager '{user.get_full_name()}' created, but failed to send credentials email to {user.personal_email}.")

        return super().form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, display an error message and re-render the form.
        """
        messages.error(self.request, "Error creating HR Manager. Please correct the highlighted errors.")
        return render(self.request, self.template_name, {'form': form, 'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')})


class EmployeeValidationView(View):
    """
    View for CEO to validate employees.
    Allows CEO to set username and password for a non-activated employee.
    """
    template_name = 'users/employee/validate.html'
    
    # @method_decorator(ceo_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, id):
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
        
        form = EmployeeValidationForm(initial={
            'username': username_initial
        })
        return render(request, self.template_name, {
            'employee': employee,
            'form': form,
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        })
        
    def post(self, request, id):
        """
        Process the employee validation form.
        Activates the employee and sends credentials.
        """
        employee = get_object_or_404(User, id=id, is_activated=False)
        form = EmployeeValidationForm(request.POST)
        
        if form.is_valid():
            new_username = form.cleaned_data['username']
            new_password = form.cleaned_data['password']

            # Check if chosen username is already taken by an activated user
            if User.objects.filter(username=new_username, is_activated=True).exclude(id=id).exists():
                messages.error(request, "This username is already taken by another active user. Please choose a different one.")
                return render(request, self.template_name, {
                    'employee': employee,
                    'form': form,
                    'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
                })

            employee.username = new_username
            employee.set_password(new_password) # Hash the password
            employee.is_activated = True  # Activate the employee
            employee.save()
            
            # Send credentials after successful validation
            email_sent = send_credentials_email(employee, new_username, new_password)  # Send Email with plain password

            if email_sent:
                messages.success(request,
                                f"Employee '{employee.get_full_name()}' validated successfully! Credentials sent to their personal email.")
            else:
                messages.warning(request,
                                f"Employee '{employee.get_full_name()}' validated, but failed to send credentials email to {employee.personal_email}.")

            return redirect(reverse_lazy('users:validation_success'))  # Redirect to generic success page
        else:
            messages.error(request, "Error validating employee. Please correct the highlighted errors.")
            return render(request, self.template_name, {
                'employee': employee,
                'form': form,
                'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
            })


# Ensure it uses the confirmation template
class EmployeeDeleteView(View):
    """
    View for CEO to delete an employee account.
    """
    template_name = 'users/ceo/delete_employee.html'
    success_url = reverse_lazy('users:employee_delete_success')
    
    # @method_decorator(ceo_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, id):
        """
        Display confirmation page for employee deletion.
        """
        print('GET method called')
        employee = get_object_or_404(User, id=id)
        return render(request, self.template_name, {
            'employee': employee,
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        })
    
    def post(self, request, id):
        """
        Process employee deletion.
        """
        employee = get_object_or_404(User, id=id)
        try:
            employee.delete()
            print('POST called')
            messages.success(request, f"Employee '{employee.get_full_name()}' has been deleted successfully.")
            return redirect('users:ceo_employees_list')
        except Exception as e:
            messages.error(request, f"Error deleting employee '{employee.get_full_name()}': {e}")
            return redirect('users:ceo_employees_list') # Redirect back to list on error

# --- HR Manager Views ---
class HRDashboardView(TemplateView):
    """HR dashboard showing key HR metrics and recent employee registrations."""
    template_name = 'users/hr_manager/dashboard.html'
    
    # @method_decorator(hr_required)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get employees created by HR (excluding superusers)
        all_employees = User.objects.filter(is_superuser=False)

        context.update({
            'total_employees': all_employees.exclude(is_activated=False).count(),
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

class EmployeeCreateView(CreateView):
    """
    View for HR Manager to register new employees.
    """
    form_class = UserCreationForm
    template_name = 'users/hr_manager/create_employee.html'
    success_url = reverse_lazy('users:employee_creation_success') # Redirect to generic success page
    
    # @method_decorator(hr_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        return context
    
    def form_valid(self, form):
        """
        If the form is valid, save the employee (as non-activated) and notify.
        The form's save method handles password hashing and basic user creation.
        """
        employee = form.save(commit=False)
        employee.is_activated = False  # Employee requires CEO validation
        employee.save() # Save the user after setting is_activated
        
        messages.success(self.request, f"Employee '{employee.get_full_name()}' registered successfully! Waiting for CEO validation.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        If the form is invalid, display an error message and re-render the form.
        """
        messages.error(self.request, "Error creating employee. Please correct the highlighted errors.")
        return render(self.request, self.template_name, {'form': form, 'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')})



class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for HR Manager to edit an employee's personal details.
    """
    model = User
    form_class = EmployeeEditForm # Using EmployeeEditForm for personal details
    template_name = 'users/hr_manager/edit_employee.html'
    context_object_name = 'employee'
    success_url = reverse_lazy('users:employee_edit_success') # Redirect to HR's employee list

    # @method_decorator(hr_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        """Retrieve the employee based on id from URL kwargs."""
        id = self.kwargs.get('id')
        return get_object_or_404(User, id=id)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        return context

    def form_valid(self, form):
        """
        If the form is valid, save the changes and display a success message.
        """
        response = super().form_valid(form)
        messages.success(self.request, _(f"{self.object.get_full_name()}'s profile was updated successfully!"))
        return response

    def form_invalid(self, form):
        """
        If the form is invalid, display an error message and re-render the form.
        """
        messages.error(self.request, _("Please correct the errors below when updating the employee profile."))
        return super().form_invalid(form)


# --- Manager Views ---
class ManagerDashboardView(TemplateView):
    """Department Manager dashboard showing team metrics."""
    template_name = 'users/manager/dashboard.html'
    
    # @method_decorator(manager_required)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        department_name = user.department if user.department else "Unknown Department"
        
        # Managers see employees in their department, excluding themselves
        team_members = User.objects.filter(
            department=user.department, 
            is_activated=True, 
            is_superuser=False # Exclude CEO
        ).exclude(id=user.id).count() # Exclude self
        
        department_employees = User.objects.filter(
            department=user.department, 
            is_activated=True, 
            is_superuser=False # Exclude CEO
        ).exclude(id=user.id).order_by('last_name', 'first_name')

        context.update({
            'team_members_count': team_members,
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform'),
            'department_name': department_name,
            'department_employees': department_employees
        })
        return context

# --- Employee Views ---
class EmployeeDashboardView(TemplateView):
    """Individual Employee dashboard."""
    template_name = 'users/employee/dashboard.html'

    # @method_decorator(employee_required)
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

class AboutMeView(TemplateView):
    """View for any user to see their own account details."""
    template_name = 'users/auth/about_me.html'
    
    # @method_decorator(login_required)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'user_profile': self.request.user, # The logged-in user's profile
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform')
        })
        return context

# --- Common Employee Listing/Detail View ---
class EmployeeListView(ListView):
    """
    Common view for CEO, HR Manager, and Department Manager to list employees.
    Filters employees based on the logged-in user's role.
    """
    model = User
    template_name = 'users/employee/list.html'
    context_object_name = 'employees'
    paginate_by = 10
    
    # @method_decorator(login_required)
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
        queryset = User.objects.exclude(is_superuser=True).order_by('last_name', 'first_name') # Start with all non-superusers

        if user.is_superuser:
            # CEO sees all employees
            # queryset = queryset.filter(is_activated=True)
            messages.info(self.request, "Displaying all registered employees.")
        elif user.role == 'HR_MANAGER':
            # HR Manager sees all employees (activated and non-activated)
            messages.info(self.request, "Displaying all registered employees (including those awaiting validation).")
        elif user.role == 'MANAGER':
            # Department Manager sees employees in their department
            queryset = queryset.filter(department=user.department, is_activated=True)
            messages.info(self.request, f"Displaying employees in your department: {user.department}.")
        else:
            # This case should ideally be caught by dispatch decorator, but as a fallback
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
    
    # @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        user = request.user
        employee_id = self.kwargs.get('id')
        employee = get_object_or_404(User, id=employee_id)

        # Ensure that only authorized roles can view employee details
        if user.is_superuser:  # CEO can view anyone
            pass
        elif user.role == 'HR_MANAGER':  # HR can view anyone
            pass
        elif user.role == 'MANAGER':  # Manager can only view employees in their department
            if employee.department != user.department:
                messages.error(request, "You do not have permission to view details of employees outside your department.")
                return redirect(reverse_lazy('users:manager_dashboard'))  # Or appropriate redirect
        else:  # Regular employee or undefined role cannot view other employee details
            # Allow employee to view their own profile via about_me
            if user.id != employee.id:
                messages.error(request, "You do not have permission to view other employee details.")
                return redirect(reverse_lazy('users:employee_dashboard'))  # Or appropriate redirect

        return super().dispatch(request, *args, **kwargs)


    def get(self, request, id):
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


# --- Success Views ---
class SuccessView(TemplateView):
    """Base success view with animations. To be inherited."""
    template_name = "users/success/generic.html"
    message = "Action completed successfully!"
    animation_class = "animate__fadeInUp" # Requires django-animate.css or similar CSS library
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
    template_name = 'users/success/employee_created.html' # Specific template if desired
    message = "Employee registered successfully! Awaiting CEO validation."
    redirect_url = reverse_lazy('users:hr_dashboard') # Go back to HR dashboard

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add buttons for HR: Register another or go to dashboard
        context['register_another_url'] = reverse_lazy('users:create_employee')
        context['go_to_dashboard_url'] = reverse_lazy('users:hr_dashboard')
        return context

class HRCreateSuccessView(SuccessView):
    """Success view for HR Manager creation by CEO."""
    template_name = 'users/success/hr_created.html' # Specific template if desired
    message = "HR Manager account created successfully!"
    redirect_url = reverse_lazy('users:ceo_dashboard') # Go back to CEO dashboard

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add buttons for CEO: Create another HR or go to dashboard
        context['create_another_hr_url'] = reverse_lazy('users:create_hr')
        context['go_to_dashboard_url'] = reverse_lazy('users:ceo_dashboard')
        context['created_hr_name'] = User.objects.filter(role='HR_MANAGER').first().first_name  # Get the name from the form data
        context['created_hr_email'] = User.objects.filter(role='HR_MANAGER').first().personal_email  # Get the email from the form data
        return context

class ValidationSuccessView(SuccessView):
    """Success view for employee validation by CEO."""
    template_name = 'users/employee/validated.html' # Reusing employee/validated.html
    message = "Employee account validated successfully!"
    redirect_url = reverse_lazy('users:ceo_dashboard') # Go back to CEO dashboard

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add buttons for CEO: Go back to validation list or go to dashboard
        context['go_to_validation_list_url'] = reverse_lazy('users:ceo_dashboard') # Or a dedicated validation list URL if implemented
        context['go_to_dashboard_url'] = reverse_lazy('users:ceo_dashboard')
        return context
    
class EmployeeDeleteSuccessView(TemplateView):
    """Success page after employee deletion"""
    template_name = 'users/success/employee_deleted.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform'),
            'redirect_url': reverse_lazy('users:ceo_dashboard')
        })
        return context
    
class EmployeeEditSuccessView(TemplateView):
    """Success page after editing an employee"""
    template_name = 'users/success/employee_edited.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'company_name': getattr(settings, 'COMPANY_NAME', 'ATI Smart Platform'),
            'redirect_url': reverse_lazy('users:hr_dashboard'),
            'view_employee_url': reverse_lazy('users:hr_employees_list')
        })
        return context