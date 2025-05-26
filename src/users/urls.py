# Add these to your urls.py if missing
from users.views import *
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
    path('ceo/dashboard', CEODashboardView.as_view(), name='ceo_dashboard'),
    path('ceo/employees', EmployeeListView.as_view(), name='ceo_employees_list'),
    path('ceo/create-hr/', HRManagerCreateView.as_view(), name='create_hr'),
    path('ceo/validate/<int:id>/', EmployeeValidationView.as_view(), name='validate_employee'),
    path('ceo/view-employee/<int:id>/', EmployeeDetailView.as_view(), name='ceo_view_employee'),
    path('ceo/delete-employee/<int:id>/', EmployeeDeleteView.as_view(), name='delete_employee'),
    
    # HR Views
    path('hr/', HRDashboardView.as_view(), name='hr_dashboard'),
    path('hr/employees/', EmployeeListView.as_view(), name='hr_employees_list'),
    path('hr/create-employee/', EmployeeCreateView.as_view(), name='create_employee'),
    path('hr/view-employee/<int:id>/', EmployeeDetailView.as_view(), name='hr_view_employee'),
    path('hr/edit-employee/<int:id>/', EmployeeUpdateView.as_view(), name='edit_employee'),
    
    # Manager Views
    path('manager/dashboard/', ManagerDashboardView.as_view(), name='manager_dashboard'),
    
    # Success Views
    path('success/hr-created/<int:hr_id>', HRCreateSuccessView.as_view(), name='hr_creation_success'),
    path('success/employee-created/', EmployeeCreateSuccessView.as_view(), name='employee_creation_success'),
    path('success/validated/<int:id>', ValidationSuccessView.as_view(), name='validation_success'),
    
    # Employee View
    path('employee/dashboard/', EmployeeDashboardView.as_view(), name='employee_dashboard'),
    
    # The about me url
    path('about-me/', AboutMeView.as_view(), name='about_me'),
]