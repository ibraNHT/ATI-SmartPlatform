# Create a urls.py file in the accountant_app directory to define the URL patterns for the application. This file will map URLs to views, allowing users to access different parts of the application through their web browser.
# The urls.py file is essential for routing requests to the appropriate views and handling user interactions with the application.

from django.urls import path
from .views import home, about, contact, login