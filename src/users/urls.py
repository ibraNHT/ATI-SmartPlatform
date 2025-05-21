# Add these to your urls.py if missing
from users.views import CustomLoginView, CustomLogoutView, CEODashboardView, HRManagerCreateView, EmployeeValidationView
from users.views import HRDashboardView, EmployeeListView, EmployeeCreateView, HRCreateSuccessView, EmployeeCreateSuccessView
from users.views import ValidationSuccessView, EmployeeDashboardView, EmployeeValidationListView, AboutMeView
from django.urls import path

# At the top
app_name = 'users'

# Then use reverse('users:login') in views

urlpatterns = [
    # Authentication
    path('login/', CustomLoginView.as_view(), name='login'),
    path('', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
    # CEO Views
    path('ceo/', CEODashboardView.as_view(), name='ceo_dashboard'),
    path('ceo/create-hr/', HRManagerCreateView.as_view(), name='create_hr'),
    path('ceo/validate/<int:id>/', EmployeeValidationView.as_view(), name='validate_employee'),
    path('ceo/validate-employees/', EmployeeValidationListView.as_view(), name='validate_employee_list'),
    
    # HR Views
    path('hr/', HRDashboardView.as_view(), name='hr_dashboard'),
    path('hr/employees/', EmployeeListView.as_view(), name='employee_list'),
    path('hr/create-employee/', EmployeeCreateView.as_view(), name='create_employee'),
    
    # Success Views
    path('success/hr-created/<int:id>/', HRCreateSuccessView.as_view(), name='hr_creation_success'),
    path('success/employee-created/<int:id>/', EmployeeCreateSuccessView.as_view(), name='employee_creation_success'),
    path('success/validated/<int:id>/', ValidationSuccessView.as_view(), name='validation_success'),
    
    # Employee View
    path('dashboard/', EmployeeDashboardView.as_view(), name='employee_dashboard'),
    
    # The about me url
    path('about-me/', AboutMeView.as_view(), name='about_me'),
]