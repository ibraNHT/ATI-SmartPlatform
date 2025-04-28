# ATI-SmartPlatform
Hybrid and Web App for ATI Information and operations Systems.

# Project Specifications

# Project architecture 
ATI-SmartPlatform/ <!-- The repository name-->
├── .venv/ <!--  Containing my virtual environment data (Scripts, include, Lib) -->
├── Ati_SmartPlatform/ <!-- The project main directory to manage the entire project features and tools-->
│   ├── __pycache__/
│   ├── __init__.py
│   ├── urls.py
│   ├── settings.py
│   ├── wsgi.py
│   ├── asgi.py
├── accountant_app/ <!-- The first app of the project for the financial operations management by the accountant-->
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── models/
│   │   ├── models.py
│   ├── views/
│   │   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── tests/
│   │   └── test_models.py
│   └── __init__.py
├── static/
│   └── bootstrap-5.3/ <!-- To store the files from bootstrap downloading (css and js folders) -->
│   └── assets
│       └── images
│       └── icons
├── templates/ <!--  Where I will store the templates according to the welcoming interfaces and the links to ressources and operational apps -->
    ├── home/
    │   ├── index.html       # Welcome page
    │   ├── about.html       # About company page
    │   ├── contact.html     # Contact page
    │   └── login.html       # Login page (later)
├── .env <!-- Will contain the environment variables (DEBUG, DATABASE_URL, SECRET KEY, ...) -->
├── manage.py
├── README.md
├── requirements.txt
├── .gitignore
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