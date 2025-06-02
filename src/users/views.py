# src/users/views.py
from datetime import timezone
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
from django.views.generic import ListView
from django.contrib.auth import get_user_model
from .models import User
from .forms import UserCreationForm, UserChangeForm, HRManagerCreationForm, EmployeeValidationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
import secrets
import string
# import the settings from your settings.py
from django.conf import settings

User = get_user_model()

# --- Utility Functions ---
def generate_random_password(length=10):
    """Generate a secure random password"""
    chars = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(chars) for _ in range(length))

def send_credentials_email(user, username, password):
    """Send login credentials to user's email"""
    subject = 'Your ATI Smart Platform Credentials'
    message = f'''
    Hello {user.first_name},
    
    Your account has been created successfully.
    
    Username: {username}
    Password: {password}
    
    Please log in at: {settings.BASE_URL}/login
    
    © {settings.COMPANY_NAME}
    '''
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.personal_email],
        fail_silently=False
    )

# --- Decorators ---
def ceo_required(view_func):
    """Decorator to ensure only CEO can access a view"""
    return user_passes_test(lambda u: u.is_superuser)(view_func)

def hr_required(view_func):
    """Decorator to ensure only HR can access a view"""
    return user_passes_test(lambda u: u.role == 'HR_MANAGER')(view_func)

# --- Authentication Views ---
class CustomLoginView(LoginView):
    """
    Custom login view with remember me functionality and role-based redirect
    """
    template_name = 'users/auth/login.html'
    extra_context = {'company_name': settings.COMPANY_NAME}
    
    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.POST.get('remember_me'):
            self.request.session.set_expiry(1209600)  # 2 weeks
            
        # Role-based redirect
        user = self.request.user
        if user.is_superuser:
            return redirect('users:ceo_dashboard')
        elif user.role == 'HR_MANAGER':
            return redirect('users:hr_dashboard')
        elif user.role == 'MANAGER':
            return redirect('users:manager_dashboard')
        return redirect('users:employee_dashboard')

class CustomLogoutView(LogoutView):
    """
    Enhanced logout view with confirmation message
    """
    template_name = 'users/auth/logout.html'
    next_page = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.info(request, "You have been successfully logged out.")
        return response

# --- CEO Views ---
class CEODashboardView(View):
    """CEO dashboard showing pending validations and quick actions"""
    template_name = 'users/ceo/dashboard.html'
    
    @method_decorator(login_required)
    @method_decorator(ceo_required)
    def get(self, request):
        context = {
            'total_employees': User.objects.exclude(is_superuser=True).count(),
            'total_managers': User.objects.filter(role__in=['MANAGER', 'HR_MANAGER']).count(),
            'total_hr_managers': User.objects.filter(role='HR_MANAGER').count(),
            'pending_validations': User.objects.filter(is_activated=False, role__in=['EMPLOYEE', 'MANAGER']).count(),
            'total_departments': len(settings.DEPARTMENTS),
            'pending_users': User.objects.filter(is_activated=False, role__in=['EMPLOYEE', 'MANAGER']),
            'company_name': settings.COMPANY_NAME
        }
        return render(request, 'users/ceo/dashboard.html', context)

class HRManagerCreateView(CreateView):
    """
    View for CEO to create HR Manager accounts
    """
    form_class = HRManagerCreationForm
    template_name = 'users/ceo/create_hr.html'
    success_url = reverse_lazy('users:hr_creation_success')
    
    @method_decorator(login_required)
    @method_decorator(ceo_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = settings.COMPANY_NAME
        return context
    
    def form_valid(self, form):
        user = form.save()
        user.is_activated = True
        user.is_staff = True
        user.role = 'HR_MANAGER'
        user.username = form.cleaned_data['username']
        user.password = form.cleaned_data['password']
        user.set_password(user.password)
        user.department = 'HR and Accounting'
        user.role_description = 'HR Manager as the main user of the platform'
        user.joined_files = form.cleaned_data['joined_files']
        user.job_title = 'HR Manager'
        user.save()
        
        password = form.cleaned_data['password']
        try:
            send_credentials_email(user, user.username, password)
        except Exception as e:
            print(f"Email failed: {e}")  # Check console for errors
        
        messages.success(self.request, 'HR Manager created successfully!')
        return super().form_valid(form)
    
class EmployeeValidationView(View):
    template_name = 'users/employee/validate.html'
    success_url = reverse_lazy('users:validation_success')

    def get(self, request, id):
        employee = get_object_or_404(User, id=id, is_activated=False)
        # Extract year from start_date
        year = employee.start_date.year if employee.start_date else ''
        
        # Format department (convert to lowercase and remove spaces)
        department = employee.department.lower().replace(' ', '') if employee.department else ''
        
        form = EmployeeValidationForm(initial={
            'username': f"{employee.last_name.lower()}.ati{year}@{department}"
        })
        return render(request, self.template_name, {
            'employee': employee,
            'form': form,
            'company_name': settings.COMPANY_NAME
        })
        
    def post(self, request, id):
        employee = get_object_or_404(User, id=id, is_activated=False)
        form = EmployeeValidationForm(request.POST)
        
        if form.is_valid():
            employee.username = form.cleaned_data['username']
            employee.is_activated = True
            employee.set_password(form.cleaned_data['password'])
            employee.save()
            
            # Send email with credentials
            # send_credentials_email(employee, employee.username, form.cleaned_data['password'])
            
            messages.success(request, f'Employee {employee.first_name} has been validated successfully.')
            return redirect(self.success_url, id=employee.id)
        
        return render(request, self.template_name, {
            'employee': employee,
            'form': form,
            'company_name': settings.COMPANY_NAME
        })
        
        
# A class view for the ceo to look at the list of employees awaiting validation
# class EmployeeValidationListView(ListView):
#     model = User
#     template_name = 'users/ceo/validation_list.html'
#     context_object_name = 'pending_employees'
#     paginate_by = 10
#     ordering = ['-date_joined']
    
#     def get_queryset(self):
#         return User.objects.filter(is_activated=False).order_by('-date_joined')
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['company_name'] = settings.COMPANY_NAME
#         return context
    

# --- HR Manager Views ---
class HRDashboardView(View):
    """HR dashboard showing pending registrations"""
    template_name = 'users/hr_manager/dashboard.html'
    
    @method_decorator(login_required)
    @method_decorator(hr_required)
    def get(self, request):
        context = {
            'total_employees': User.objects.exclude(is_superuser = True).count(),
            'pending_validations': User.objects.filter(is_activated=False, role__in=["MANAGER", "EMPLOYEE"]).count(),
            'new_this_month': User.objects.filter(
                date_joined__month=timezone.now().month, role__in=["MANAGER", "EMPLOYEE"]
            ).count(),
            'total_departments': len(settings.DEPARTMENTS),
            'recent_employees': User.objects.filter(role__in=['MANAGER', 'EMPLOYEE']).order_by('-date_joined')[:5],
            'company_name': settings.COMPANY_NAME
        }
        return render(request, self.template_name, context)

# --- Success Views ---
class SuccessView(View):
    """Base success view with animations"""
    template_name = "users/success/generic.html"
    message = "Action completed successfully"
    animation_class = "animate__fadeInUp"
    
    def get(self, request):
        return render(request, self.template_name, {
            'message': self.message,
            'animation_class': self.animation_class,
            'company_name': settings.COMPANY_NAME
        })

# The employee list view returning the employees and the user connected
class EmployeeListView(ListView):
    model = User
    template_name = 'users/employee/list.html'
    context_object_name = 'employees'
    paginate_by = 10  # Number of employees per page
    
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        # Firstly a list of all the employees excluding the superuser
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('users:login')
        employees = User.objects.exclude(is_superuser=True).order_by('-date_joined')
        # Filter employees based on the connected user's role
        if request.user.is_superuser:
            employees = User.objects.exclude(is_superuser=True).order_by('-date_joined')
        elif request.user.role == 'HR_MANAGER':
            employees = User.objects.exclude(is_superuser = True).order_by('-date_joined')
        elif request.user.role == 'MANAGER':
            employees = User.objects.filter(department=request.user.department).order_by('-date_joined')
        else:
            employees = User.objects.filter(role='').order_by('-date_joined')
            
        print(f"Connected user: {request.user.is_superuser}, Role: {request.user.role}")
        
        return render(request, self.template_name, {
            'employees': employees,
            'company_name': settings.COMPANY_NAME,
            'connected_user': request.user
        })

class EmployeeCreateSuccessView(View):
    template_name = 'users/success/employee_created.html'
    
    def get(self, request):
        employee = get_object_or_404(User, is_activated=False, role__in=['EMPLOYEE', 'MANAGER'])
        # Ensure the employee is not activated yet
        if employee.is_activated:
            messages.error(request, "This employee is already activated.")
            return redirect('users:employee_list')
        return render(request, self.template_name, {
            'employee': employee,
            'company_name': settings.COMPANY_NAME
        })

class HRCreateSuccessView(View):
    template_name = 'users/success/hr_created.html'
    
    def get(self, request):
        hr_manager = get_object_or_404(User.objects.filter(role='HR_MANAGER', is_activated=True))
        return render(request, self.template_name, {
            'hr_manager': hr_manager,
            'company_name': settings.COMPANY_NAME
        })

class ValidationSuccessView(View):
    template_name = 'users/employee/validated.html'
    
    def get(self, request):
        # employee = get_object_or_404(User.objects.filter(username=request.username))
        # Ensure the employee is activated and has a role
        # if not employee.is_activated or employee.role not in ['EMPLOYEE', 'MANAGER', 'HR_MANAGER']:
        #     messages.error(request, "This employee is not activated or does not have a valid role.")
        #     return redirect('users:ceo_employee_list')
        return render(request, self.template_name, {
            # 'employee': employee,
            'company_name': settings.COMPANY_NAME
        })

# --- Manager Views ---
class ManagerDashboardView(View):
    template_name = 'users/manager/dashboard.html'
    
    @method_decorator(login_required)
    def get(self, request):
        # For managers, show team count - for regular employees, show department count and the department name
        department_name = request.user.department if request.user.department else "No Department"
        employees = User.objects.filter(department=request.user.department).exclude(id=request.user.id)
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('users:login')
        
        if request.user.role == 'MANAGER':
            team_members = User.objects.filter(
            department=request.user.department
            ).exclude(id=request.user.id).count()
        else:
            team_members = User.objects.filter(
            department=request.user.department
            ).count()
            
        return render(request, self.template_name, {
            'team_members': team_members,
            'company_name': settings.COMPANY_NAME,
            'department_name': department_name,
            'employees': employees
        })

# --- Employee Views ---
from django.views.generic import TemplateView
from django.utils import timezone
# from tasks.models import Task
# from communication.models import Message
# from events.models import Event
from datetime import timedelta

# class ManagerDashboardView(View):
#     template_name = 'users/manager/dashboard.html'
    
#     @method_decorator(login_required)
#     def get(self, request):
#         # For managers, show team count - for regular employees, show department count and the department name
#         department_name = request.user.department if request.user.department else "No Department"
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
#             'department_name': department_name
#         })

class EmployeeDashboardView(TemplateView):
    template_name = 'users/employee/dashboard.html'

    @method_decorator(login_required)
    def get(self, request):
        employee_manager = User.objects.filter(department=request.user.department, role='MANAGER')[0]
        
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to access this page")
            return redirect('users:login')
        

        return render(request, self.template_name, {
            'employee_manager': employee_manager,
            'company_name': settings.COMPANY_NAME,
            'department_name': request.user.department
        })
        
class EmployeeCreateView(CreateView):
    """View for HR to register new employees"""
    form_class = UserCreationForm
    template_name = 'users/hr_manager/create_employee.html'
    # Add the success_url variable with the user id
    success_url = reverse_lazy('users:employee_creation_success')
    # Add the company name as an extrat context
    extra_context = {'company_name': settings.COMPANY_NAME}
    
    @method_decorator(login_required)
    @method_decorator(hr_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        employee = form.save(commit=False)
        employee.is_activated = False  # Requires CEO validation
        employee.email= ''  # Set to empty string
        employee.username = employee.personal_email.split('@')[0] + employee.start_date.strftime('%Y%m%d')
        employee.save()
        messages.success(self.request, 'Employee registered! Waiting for CEO validation.')
        return super().form_valid(form)
    
    def get_success_url(self):
        # return reverse('users:employee_creation_success', args=[self.object.id])
        return reverse('users:employee_creation_success')
    
# A class view called AboutMeView for every users to look at their account details with just simple informations
class AboutMeView(View):
    template_name = 'users/auth/about_me.html'
    
#    @method_decorator(login_required)
    def get(self, request):
        return render(request, self.template_name, {
            'user': request.user,
            'company_name': settings.COMPANY_NAME
        })

# --- A view to view a unique employee for the CEO, the HR Manager and the other managers ---
class EmployeeDetailView(View):
    template_name = 'users/employee/detail.html'
    
    @method_decorator(login_required)
    def get(self, request, id):
        employee = get_object_or_404(User, id=id)
        connected_user = request.user
        return render(request, self.template_name, {
            'employee': employee,
            'connected_user': connected_user,
            # 'is_ceo': connected_user.is_superuser,
            # 'is_hr_manager': connected_user.role == 'HR_MANAGER',
            # 'is_manager': connected_user.role == 'MANAGER',
            # 'is_employee': connected_user.role == 'EMPLOYEE',
            'company_name': settings.COMPANY_NAME
        })

# --- A view to delete an employee for the CEO ---
class EmployeeDeleteView(View):
    template_name = 'users/ceo/delete_employee.html'
    
    @method_decorator(login_required)
    @method_decorator(ceo_required)
    def get(self, request, id):
        employee = get_object_or_404(User, id=id)
        return render(request, self.template_name, {
            'employee': employee,
            'company_name': settings.COMPANY_NAME
        })
    
    def post(self, request, id):
        employee = get_object_or_404(User, id=id)
        employee.delete()
        messages.success(request, f'Employee {employee.first_name} has been deleted successfully.')
        return redirect('users:ceo_employee_list')  # Redirect to the employee list after deletion
    
# class EmployeeEditView(UpdateView):
#     model = User
#     form_class = UserChangeForm
#     template_name = 'users/hr_manager/edit_employee.html'
#     success_url = reverse_lazy('users:employee_list')
    
#     @method_decorator(login_required)
#     @method_decorator(hr_required)
#     def dispatch(self, *args, **kwargs):
#         return super().dispatch(*args, **kwargs)
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['company_name'] = settings.COMPANY_NAME
#         return context
    
#     def form_valid(self, form):
#         messages.success(self.request, 'Employee details updated successfully!')
#         return super().form_valid(form)

# --- A view to edit an employee for the HR Manager ---
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext as _

class EmployeeUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserChangeForm
    template_name = 'users/hr_manager/edit_employee.html'  # match your template path
    context_object_name = 'employee'
    success_url = reverse_lazy('users:employee_list')  # adjust to your success URL

    @method_decorator(login_required)
    @method_decorator(hr_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    # Ensure the user is logged in and has HR permissions
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company_name'] = settings.COMPANY_NAME  # or get from settings
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _(f"{self.object.get_full_name()}'s profile was updated successfully!")
        )
        return response

    def form_invalid(self, form):
        messages.error(
            self.request,
            _("Please correct the errors below.")
        )
        return super().form_invalid(form)

    # Optional: Add permission mixin if needed
    # from django.contrib.auth.mixins import PermissionRequiredMixin
    # permission_required = 'users.change_employee'
    # raise_exception = True
