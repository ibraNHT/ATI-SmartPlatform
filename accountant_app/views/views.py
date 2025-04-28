from django.shortcuts import render

# Create your views here.

# Create thee views for the models in the accountant_app. These views will handle the logic for displaying and processing data related to income, expenses, and observations.
def income_list(request):
    # Logic to retrieve and display income records
    return render(request, 'accountant_app/income_list.html')