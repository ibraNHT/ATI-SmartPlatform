from django.shortcuts import render

def home(request):
    return render(request, 'external/index.html', context={
        'title': 'Home',
        'message': 'Welcome to the home page!'
    })

# def about(request):
#     return render(request, 'home/about.html', context={
#         'title': 'About Us',
#         'message': 'This is the about page where you can learn more about us.'
#     })

# def contacts(request):
#     return render(request, 'home/contact.html', context={
#         'title': 'Contact Us',
#         'message': 'Please fill out the form below to get in touch with us.'
#     })

# def login(request):
#     return render(request, 'home/login.html', context={
#         'title': 'Login',
#         'message': 'Please enter your credentials to log in.'
#     })
    
# def register(request):
#     return render(request, 'home/register.html', context={
#         'title': 'Register',
#         'message': 'Create a new account by filling out the form below.'
#     })

# def password_reset(request):
#     return render(request, 'home/password_reset.html', context={
#         'title': 'Password Reset',
#         'message': 'Enter your email address to reset your password.'
#     })
    
# def password_reset_done(request):
#     return render(request, 'home/password_reset_done.html', context={
#         'title': 'Password Reset Done',
#         'message': 'Check your email for a link to reset your password.'
#     })
    
# def internal(request):
#     return render(request, 'home/base_private.html', context={
#         'title': 'Internal Page',
#         'message': 'This is the internal page for logged-in users.'
#     })