from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

app_name = 'users'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('', views.user_login, name='login'),  # Redirect root URL to login
    path('logout/', views.logout_user, name='logout'),
    path('hr-register/', views.HRManagerRegistrationView.as_view(), name='hr_register'),
    path('hr_list/', views.hr_list, name='hr_list'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('validate/', views.UserValidationListView.as_view(), name='validation_list'),
    path('validate/<int:pk>/', views.UserValidationView.as_view(), name='validate_user'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('ceo-dashboard/', views.ceo_dashboard, name='ceo_dashboard'),
    path('hr-dashboard/', views.hr_manager_dashboard, name='hr_manager_dashboard'),
    path('user-dashboard/', views.user_dashboard, name='user_dashboard'),
]