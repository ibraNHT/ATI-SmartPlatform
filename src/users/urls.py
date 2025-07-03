# # Add these to your urls.py if missing
# from users.views import *
# from django.urls import path

# # At the top
# app_name = 'users'

# # Then use reverse('users:login') in views

from users.views import *
from django.urls import path

app_name = 'users'

urlpatterns = [
    # Authentication
    path('login/', CustomLoginView.as_view(), name='login'),
    path('', CustomLoginView.as_view(), name='login'), # Redirect root to login
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
    # CEO Views
    path('ceo/dashboard/', CEODashboardView.as_view(), name='ceo_dashboard'),
    path('ceo/employees/', EmployeeListView.as_view(), name='ceo_employees_list'), # CEO sees activated employees
    path('ceo/create-hr/', HRManagerCreateView.as_view(), name='create_hr'),
    path('ceo/validate/<int:id>/', EmployeeValidationView.as_view(), name='validate_employee'),
    path('ceo/view-employee/<int:id>/', EmployeeDetailView.as_view(), name='ceo_view_employee'),
    path('ceo/delete-employee/<int:id>/', EmployeeDeleteView.as_view(), name='ceo_delete_employee'),
    
    # HR Views
    path('hr/dashboard/', HRDashboardView.as_view(), name='hr_dashboard'),
    path('hr/employees/', EmployeeListView.as_view(), name='hr_employees_list'), # HR sees all employees
    path('hr/create-employee/', EmployeeCreateView.as_view(), name='create_employee'),
    path('hr/view-employee/<int:id>/', EmployeeDetailView.as_view(), name='hr_view_employee'),
    path('hr/edit-employee/<int:id>/', EmployeeUpdateView.as_view(), name='hr_edit_employee'),
    
    # Manager Views
    path('manager/dashboard/', ManagerDashboardView.as_view(), name='manager_dashboard'),
    path('manager/employees/', EmployeeListView.as_view(), name='manager_employees_list'), # Manager sees their department employees
    path('manager/view-employee/<int:id>/', EmployeeDetailView.as_view(), name='manager_view_employee'),
    
    # Success Views
    path('ceo/success/hr-created/', HRCreateSuccessView.as_view(), name='hr_creation_success'),
    path('hr/success/employee-created/', EmployeeCreateSuccessView.as_view(), name='employee_creation_success'),
    path('ceo/success/employee-validated/', ValidationSuccessView.as_view(), name='validation_success'),
    path('ceo/success/deleted/', EmployeeDeleteSuccessView.as_view(), name='employee_delete_success'),
    path('hr/success/employee-edited/', EmployeeEditSuccessView.as_view(), name='employee_edit_success'),
    
    # Employee View
    path('employee/dashboard/', EmployeeDashboardView.as_view(), name='employee_dashboard'),
    
    
    # The about me url
    path('about-me/', AboutMeView.as_view(), name='about_me'),
]