# ATI-SmartPlatform
Hybrid and Web App for ATI Information and operations Systems.

# Project Specifications

# Project architecture 
ATI-SmartPlatform/ <!-- The repository name-->
├── .venv/ <!--  Containing my virtual environment data (Scripts, include, Lib) -->
├── src/ <!--A subdirectory to contain the entire project code -->
│   ├── Ati_smart_platform/ <!-- The project name and main directory to manage the entire project features and tools-->
│   │   ├── __pycache__/
│   │   ├── __init__.py
│   │   ├── urls.py
│   │   ├── settings.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   ├── users/ <!-- The first app of the project that's supposed to manage users-->
│   │   ├── migrations/
│   │   ├── __pycache__/
│   │   ├── static/ <!-- There is where I tried to store some specific users app files-->
│   │   │    ├── users/
│   │   │    │   ├── css/
│   │   │    │   ├── images/
│   │   │    │   ├── js/
│   │   ├── templates/ <!-- This folder seems to be the refered one in the settings as TEMPLATE_FILES (surely for this specific app)-->
│   │   │    ├── users/
│   │   │    │   ├── ceo/
│   │   │    │   ├── hr_manager/
│   │   │    │   ├── auth/
│   │   │    │   ├── manager/
│   │   │    │   ├── employee/
│   │   │    │   ├── success/
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models,py
│   │   ├── views.py
│   │   ├── forms.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   └── __init__.py
│   ├── media/
│   │   ├── joined_files/ <!-- There is where the joined files are supposed to be stored -->
│   │   ├── profile_pics/  <!-- There is where the registered profile pictures are supposed to be stored -->
│   ├── db.sqlite3
│   ├── migrations/__init__.py
│   ├── templates/ base.html  <!-- The base template to build a common headder and import stuffs for the platform interfaces -->
├── static/images/ <!-- There is where other static files are supposed to be stored like the logo, and other static suffs -->
├── README.md
├── manage.py
├── requirements.txt
├── .gitignore
├── LICENCE
├── Procfile
├── runtime.txt
└── .github/
    └── workflows/
        └── django.yml


---

# 🖥️ 6. Visual Studio Code Full Setup

✅ **Extensions to Install**:
- Python
- Django
- Prettier (for HTML/CSS/JS)
- GitLens
- Docker (optional)

✅ **Settings to Activate**:
- Enable Format on Save
- Enable Linting (with Flake8 if you want)

✅ **Recommended Folder Setup**:
- Open the root folder `ati_finance_platform/` in VSCode
- Install Python interpreter pointing to your `venv`
- Activate Django environment
- Run server with:
   ```bash
   python manage.py runserver

# Run these commands in sequence
python manage.py check  # Verify project integrity
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Create CEO account