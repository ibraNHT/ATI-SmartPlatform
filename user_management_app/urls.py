from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('registration-success/', views.registration_success, name='registration_success'),
    path('pending-users/', views.pending_users, name='pending_users'),
    path('validate-user/<int:user_id>/', views.validate_user, name='validate_user'),
]
