# ATI-SmartPlatform
Hybrid and Web App for ATI Information and operations Systems.

## Requirements

This project uses different requirement files for different environments:

- `requirements-prod.txt`: Production dependencies (used in deployment)
- `requirements-dev.txt`: Development dependencies (includes production deps)
- `requirements-windows.txt`: Windows-specific dependencies (for local development on Windows)

## Local Development Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On macOS/Linux
   ```

2. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```
   
   For Windows development, also run:
   ```bash
   pip install -r requirements-windows.txt
   ```

3. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Update the values in `.env` as needed

## Deployment

This project is configured for deployment on [Render](https://render.com).

### Render Deployment

1. Push your code to your GitHub repository
2. Connect your repository to Render
3. Configure the following environment variables in Render:
   - `DJANGO_SETTINGS_MODULE`: `Ati_smart_platform.settings`
   - `ENVIRONMENT`: `production`
   - `SECRET_KEY`: Generate a secure key
   - `DATABASE_URL`: Your PostgreSQL connection string
   - Other required environment variables from `.env.prod`

4. The deployment will automatically use `requirements-prod.txt` for installing dependencies

## Project Specifications

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