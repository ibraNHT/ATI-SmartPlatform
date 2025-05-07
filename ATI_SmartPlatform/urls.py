"""
URL configuration for ATI_SmartPlatform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
#Import the files from the templates directory to render the HTML files.
from django.views.generic import TemplateView

from .views import home

from django.http import HttpResponse

def test_post_view(request):
    if request.method == 'POST':
        return HttpResponse("POST bien reçu !")
    return HttpResponse("GET seulement")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', home, name='home'),  # URL for the home view
    path('internal/', TemplateView.as_view(template_name='base_private.html'), name='internal'),
    path('', TemplateView.as_view(template_name='external/index.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='external/about.html'), name='about'),
    path('contacts/', TemplateView.as_view(template_name='external/contacts.html'), name='contacts'),
    path('login/', TemplateView.as_view(template_name='external/login.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='external/register.html'), name='register'),
    path('password_reset/', TemplateView.as_view(template_name='external/password_reset.html'), name='password_reset'),
    path('password_reset_done/', TemplateView.as_view(template_name='external/password_reset_done.html'), name='password_reset_done'),
    path('users/', include('user_management_app.urls')),
    path('test_post/', test_post_view, name='test_post'),  # URL for the test POST view
    path('accounts/', include('django.contrib.auth.urls')),  # For login/logout views
    
]
